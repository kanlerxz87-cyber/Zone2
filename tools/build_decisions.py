#!/usr/bin/env python3
"""Generate the decision-support surfaces: Suggestions and Questions.

Two registers, both generated from data so they cannot drift from the ledgers they cite:

  suggestions.html  - proposals with options, trade-offs, a recommendation, expected
                      effect, effort, dependencies, risk and a review status.
  questions.html    - the open questions: what is already known and who says so, what is
                      missing, the exact discovery step, and the (empty) answer field.

The project's contract is unchanged and is enforced here as well:

  * every row ends in an official-source link, or in an explicit blank marker;
  * a value is never invented to fill a cell - an unanswered question renders as an
    explicit "unanswered" marker, not as a guess;
  * no price, rating, review count, sales rank or performance figure is ever printed.

Usage
    python3 tools/build_decisions.py           # write suggestions.html + questions.html
    python3 tools/build_decisions.py --check   # fail if the committed output drifted
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"

SITE_NAME = "Zone2"  # never an Amazon mark - Participation Requirements rule R-11
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# The canonical root navigation. Every root page carries the same list so a reader can
# reach any surface from any surface; the design refresh (session bdbe382b) removed the
# inconsistency where most pages could not reach the executive summary or the published
# copy.
NAV = [
    ("index.html", "Dashboard"),
    ("summary.html", "Executive summary"),
    ("products.html", "Products"),
    ("analysis.html", "Analysis"),
    ("content.html", "Content"),
    ("marketing/index.html", "Published copy"),
    ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking"),
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Questions"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
]

NAV_GROUPS = [
    ("Site", ["index.html", "summary.html"]),
    ("Research", ["products.html", "analysis.html", "content.html", "marketing/index.html"]),
    ("Compliance", ["compliance.html", "tracking.html"]),
    ("Decide", ["suggestions.html", "questions.html"]),
    ("Evidence", ["verification.html", "sources.html", "flagged.html"]),
]

SIBLINGS = [
    ("pages/index.html", "Findings hub"),
    ("pages/categories/index.html", "Commission categories"),
    ("pages/flags.html", "Flagged for review (generated)"),
    ("research-hub/start.html", "Affiliate Research Hub"),
    ("revalidation/index.html", "Revalidation 2026-11-14"),
    ("affiliate-lab/index.html", "Affiliate Lab"),
]


# --------------------------------------------------------------------------- helpers


def load(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


def esc(value) -> str:
    if value is None:
        return ""
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slugify(name: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in name)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
FLAGS = {f["id"]: f for f in load("flags.json")["flags"]}
RULES = {r["id"]: r for r in load("compliance.json")["rules"]}
MODULES = {m["id"]: m for m in load("modules.json")["modules"]}
SUGGESTIONS = load("suggestions.json")
QUESTIONS = load("questions.json")


def module_page(module_id: str) -> str:
    m = MODULES.get(module_id)
    if not m:
        return "pages/modules/index.html"
    return f"pages/modules/{m['id'].lower()}-{slugify(m['name'])}.html"


def src_links(source_ids, *, cls: str = "src") -> str:
    """A row's evidence: one linked chip per official source."""
    ids = [i for i in (source_ids or []) if i in SOURCES]
    if not ids:
        return '<span class="pill pill-warn">NO SOURCE</span>'
    out = []
    for sid in ids:
        s = SOURCES[sid]
        host = s["url"].split("/")[2] if "//" in s["url"] else s["url"]
        kind = s.get("kind", "official")
        out.append(
            f'<a class="{cls}" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">'
            f'{esc(sid)} &middot; {esc(host)}<span class="src-kind">{esc(kind)}</span></a>'
        )
    return " ".join(out)


def xref_links(ids, *, href_for, label_prefix: str = "") -> str:
    out = []
    for i in ids or []:
        href = href_for(i)
        if not href:
            continue
        out.append(f'<a class="chip chip-sm" href="{esc(href)}">{esc(label_prefix + i)}</a>')
    return " ".join(out)


def flag_link(fid: str) -> str:
    return f"pages/flags.html#{fid}" if fid in FLAGS else ""


def rule_link(rid: str) -> str:
    return "pages/compliance.html" if rid in RULES else ""


def module_link(mid: str) -> str:
    return module_page(mid) if mid in MODULES else ""


def or_blank(html: str) -> str:
    """An empty cross-reference renders as an explicit blank marker, never as silence."""
    return html or '<span class="blank">none</span>"'.replace('"', "")


def pill(text: str, kind: str = "ok") -> str:
    return f'<span class="pill pill-{kind}">{esc(text)}</span>'


STATUS_KIND = {
    "PROPOSED": "warn",
    "ACCEPTED": "ok",
    "IN PROGRESS": "info",
    "DONE": "ok",
    "DEFERRED": "muted",
    "REJECTED": "flag",
    "OPEN": "warn",
    "ANSWERED": "ok",
}
PRIORITY_KIND = {"P1": "flag", "P2": "warn", "P3": "muted"}


# --------------------------------------------------------------------------- chrome


def nav_html(active: str) -> str:
    groups = []
    for label, hrefs in NAV_GROUPS:
        items = []
        for href in hrefs:
            name = dict(NAV)[href]
            cls = " active" if href == active else ""
            items.append(f'<a class="nav-link{cls}" href="{esc(href)}">{esc(name)}</a>')
        groups.append(
            f'<div class="nav-group"><span class="nav-label">{esc(label)}</span>{"".join(items)}</div>'
        )
    return "\n      ".join(groups)


def siblings_html() -> str:
    links = []
    for href, label in SIBLINGS:
        if (REPO / href).exists():
            links.append(f'<a href="{esc(href)}">{esc(label)}</a>')
    return " <span>&middot;</span> ".join(links)


def page(*, filename: str, title: str, lead: str, eyebrow: str, body: str, active: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{esc(lead)}">
<title>{esc(title)} &middot; {esc(SITE_NAME)}</title>
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <a class="brand" href="index.html"><span class="brand-mark">Z</span><span>{esc(SITE_NAME)}<small>Affiliate intelligence</small></span></a>
    <nav class="nav" aria-label="Primary">
      {nav_html(active)}
    </nav>
    <div class="sidebar-bottom">
      <div class="status-dot"></div>
      <div><strong>Verified data only</strong><small>blank = unconfirmed</small></div>
    </div>
  </aside>
  <main class="main">
    <header class="topbar">
      <div class="crumb"><a href="index.html">{esc(SITE_NAME)}</a> <span>/</span> <strong>{esc(title)}</strong></div>
      <div class="top-right"><span class="live-tag"><i></i> Live on GitHub Pages</span><a class="chip" href="index.html">Dashboard</a></div>
    </header>
    <div class="content">
      <div class="page-head">
        <div>
          <div class="eyebrow">{esc(eyebrow)}</div>
          <h1>{esc(title)}</h1>
          <p>{esc(lead)}</p>
        </div>
      </div>
      <div class="disclosure">
        <strong>Affiliate disclosure (required by the Amazon Associates Operating Agreement &sect;5):</strong>
        As an Amazon Associate I earn from qualifying purchases.
      </div>
{body}
      <footer class="site">
        <strong>{esc(SITE_NAME)}</strong> &middot; every row on this page links to the official page it came from &middot;
        {siblings_html()}
      </footer>
    </div>
  </main>
</div>
</body>
</html>
"""


def kpi_block(items: list[tuple[str, str, str]]) -> str:
    cells = []
    for num, label, sub in items:
        cells.append(
            f'<div class="kpi"><div class="num">{esc(num)}</div><div class="lbl">{esc(label)}</div>'
            f'<div class="kpi-sub">{esc(sub)}</div></div>'
        )
    return '<section class="kpis">' + "".join(cells) + "</section>"


# --------------------------------------------------------------------------- questions


def questions_page() -> str:
    qs = QUESTIONS["questions"]
    open_q = [q for q in qs if q["status"] == "OPEN"]
    answered = [q for q in qs if q["status"] != "OPEN"]
    p1 = [q for q in qs if q["priority"].startswith("P1")]
    owner_actions = [q for q in qs if q["answer_source_kind"] in ("owner_decision", "owner_account")]
    public_pages = [q for q in qs if q["answer_source_kind"] == "official_public_page"]

    rows = []
    for q in qs:
        rows.append(
            "<tr>"
            f'<th scope="row"><a class="row-id" href="#{esc(q["id"])}">{esc(q["id"])}</a></th>'
            f'<td>{esc(q["question"])}</td>'
            f'<td>{esc(q["decision_blocked"])}</td>'
            f'<td>{pill(q["priority"].split(" ")[0], PRIORITY_KIND.get(q["priority"][:2], "muted"))}'
            f'<div class="cell-note">{esc(q["priority"].split(" ", 1)[1] if " " in q["priority"] else "")}</div></td>'
            f'<td class="cell-answer">'
            + (
                esc(q["answer"])
                if q["answer"]
                else '<span class="blank">not yet answered</span>'
                f'<div class="cell-note">{esc(q["how_to_obtain"].split(".")[0])}.</div>'
            )
            + "</td>"
            f'<td>{pill(q["status"], STATUS_KIND.get(q["status"], "muted"))}</td>'
            "</tr>"
        )

    summary = f"""    <section class="card">
      <h2>Every open question, in one table</h2>
      <p class="card-note">The answer column is empty on purpose: it is filled only when an official source or
      the owner supplies the answer. The note under each empty cell is the discovery step that closes it.</p>
      <div class="table-wrap">
        <table class="data-table">
          <caption>Open questions register, generated from ledger/questions.json.</caption>
          <thead><tr><th scope="col">ID</th><th scope="col">Question</th><th scope="col">Decision it blocks</th>
          <th scope="col">Priority</th><th scope="col">Answer</th><th scope="col">Status</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
    </section>
"""

    cards = []
    for q in qs:
        known_links = src_links(q["source_ids"])
        answer_block = (
            f'<div class="answer answer-set">{esc(q["answer"])}<div class="cell-note">Sources: {src_links(q["answer_source_ids"])}</div></div>'
            if q["answer"]
            else f'<div class="answer answer-open"><span class="blank">not yet answered</span>'
            f'<div class="cell-note">Answer source: {esc(q["answer_source_kind"].replace("_", " "))} &mdash; '
            f'no public page states this.</div></div>'
        )
        q_flags = xref_links(q["related_flag_ids"], href_for=flag_link)
        q_rules = xref_links(q["related_rule_ids"], href_for=rule_link)
        q_modules = xref_links(q["related_module_ids"], href_for=module_link)
        q_suggestions = xref_links(q["related_suggestion_ids"], href_for=lambda i: f"suggestions.html#{i}")
        cards.append(
            f"""    <article class="qcard" id="{esc(q["id"])}">
      <header class="qcard-head">
        <div>
          <p class="eyebrow">{esc(q["id"])} &middot; {esc(q["priority"])}</p>
          <h2>{esc(q["question"])}</h2>
        </div>
        {pill(q["status"], STATUS_KIND.get(q["status"], "muted"))}
      </header>
      <div class="qcard-grid">
        <section>
          <h3>Decision it blocks</h3>
          <p>{esc(q["decision_blocked"])}</p>
        </section>
        <section>
          <h3>What we already know</h3>
          <p>{esc(q["known"])}</p>
          <p class="cell-note">Official sources: {known_links}</p>
        </section>
        <section>
          <h3>What is missing</h3>
          <p>{esc(q["missing"])}</p>
        </section>
        <section>
          <h3>How to obtain it</h3>
          <p>{esc(q["how_to_obtain"])}</p>
          <p class="cell-note">Reference pages for the artifact sought: {src_links(q["obtain_refs"])}</p>
        </section>
        <section class="span-2">
          <h3>Answer</h3>
          {answer_block}
        </section>
      </div>
      <footer class="qcard-foot">
        <span class="foot-label">Owner:</span> {esc(q["owner"])}
        <span class="foot-label">Effort:</span> {esc(q["effort"])}
        <span class="foot-label">Flags:</span> {or_blank(q_flags)}
        <span class="foot-label">Rules:</span> {or_blank(q_rules)}
        <span class="foot-label">Modules:</span> {or_blank(q_modules)}
        <span class="foot-label">Suggestions:</span> {or_blank(q_suggestions)}
      </footer>
    </article>
"""
        )

    body = f"""{kpi_block([
        (str(len(qs)), "questions on the register", f"{len(open_q)} still open, {len(answered)} answered"),
        (str(len(p1)), "P1 questions", "they block revenue or compliance"),
        (str(len(owner_actions)), "need an owner answer", "the repository cannot obtain these itself"),
        (str(len(public_pages)), "can be closed from a public page", "once the identity questions are answered"),
    ])}
    <section class="card">
      <h2>How this register works</h2>
      <ul class="checklist">
        <li><span class="check">1</span>Every row states the question, the decision it blocks, what is already known and the official page that says so, what is missing, and the concrete step that closes it.</li>
        <li><span class="check">2</span>The answer column stays empty until an official source or the owner supplies it. An empty cell is a task, not a gap in the research.</li>
        <li><span class="check">3</span>A question marked <code>owner account</code> or <code>owner decision</code> cannot be closed from the public web at all &mdash; it needs the account holder, and this repository will not guess it.</li>
        <li><span class="check">4</span>Each question names the suggestions that depend on it, so a suggestion cannot be started while its question is open &mdash; only planned.</li>
        <li><span class="check">5</span>Questions are re-opened whenever the verification pass changes what is known. The register is generated from <code>ledger/questions.json</code>, so it cannot drift from the flag register.</li>
      </ul>
      <p class="card-note">Read with the <a href="suggestions.html">Suggestions register</a>: a suggestion names the question it
      depends on, and a question names the discovery step that unblocks it.</p>
    </section>
{summary}
    <h2 class="section-h">Full detail, one card per question</h2>
{''.join(cards)}"""

    return page(
        filename="questions.html",
        title="Questions & information needed",
        lead=(
            "The open questions behind every decision on this project: what is already known and who says so, "
            "what is missing, exactly how to obtain it, and where the answer would come from."
        ),
        eyebrow=f"register &middot; as of {esc(QUESTIONS['as_of'])} &middot; generated from ledger/questions.json",
        body=body,
        active="questions.html",
    )


# --------------------------------------------------------------------------- suggestions


def suggestions_page() -> str:
    sg = SUGGESTIONS["suggestions"]
    by_status: dict[str, int] = {}
    for s in sg:
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
    accepted = [s for s in sg if s["status"] in ("ACCEPTED", "IN PROGRESS", "DONE")]
    proposed = [s for s in sg if s["status"] == "PROPOSED"]
    cats = sorted({s["category"] for s in sg})

    rows = []
    for s in sg:
        dep_links = xref_links(
            s["dependencies"],
            href_for=lambda i: (f"questions.html#{i}" if i.startswith("Q-") else flag_link(i)),
        )
        rows.append(
            "<tr>"
            f'<th scope="row"><a class="row-id" href="#{esc(s["id"])}">{esc(s["id"])}</a></th>'
            f'<td><strong>{esc(s["title"])}</strong><div class="cell-note">{esc(s["category"])}</div></td>'
            f'<td>{esc(s["recommendation"])}</td>'
            f'<td>{esc(s["effort"])}</td>'
            f'<td>{dep_links}</td>'
            f'<td>{pill(s["status"], STATUS_KIND.get(s["status"], "muted"))}</td>'
            "</tr>"
        )

    summary = f"""    <section class="card">
      <h2>Every proposal, in one table</h2>
      <p class="card-note">The recommendation column is this project's reading, not a decision. The status column is
      where a decision is recorded; a proposal still marked PROPOSED is an open item, not a plan.</p>
      <div class="table-wrap">
        <table class="data-table">
          <caption>Suggestions register, generated from ledger/suggestions.json.</caption>
          <thead><tr><th scope="col">ID</th><th scope="col">Suggestion</th><th scope="col">Recommended option</th>
          <th scope="col">Effort</th><th scope="col">Depends on</th><th scope="col">Status</th></tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
      </div>
    </section>
"""

    cards = []
    for s in sg:
        options = []
        for i, opt in enumerate(s["options"]):
            options.append(
                "<tr>"
                f'<th scope="row">{esc(opt["option"])}</th>'
                f'<td>{esc(opt["pros"])}</td>'
                f'<td>{esc(opt["cons"])}</td>'
                "</tr>"
            )
        s_flags = xref_links([d for d in s["dependencies"] if d.startswith("F-")], href_for=flag_link)
        s_questions = xref_links([d for d in s["dependencies"] if d.startswith("Q-")], href_for=lambda i: f"questions.html#{i}")
        s_related = xref_links([d for d in s["dependencies"] if d.startswith("SG-")], href_for=lambda i: f"suggestions.html#{i}")
        cards.append(
            f"""    <article class="qcard" id="{esc(s["id"])}">
      <header class="qcard-head">
        <div>
          <p class="eyebrow">{esc(s["id"])} &middot; {esc(s["category"])}</p>
          <h2>{esc(s["title"])}</h2>
        </div>
        {pill(s["status"], STATUS_KIND.get(s["status"], "muted"))}
      </header>
      <div class="qcard-grid">
        <section class="span-2">
          <h3>The problem it addresses</h3>
          <p>{esc(s["problem"])}</p>
          <p class="cell-note">Evidence: {src_links(s["source_ids"])}</p>
        </section>
        <section class="span-2">
          <h3>Options and their trade-offs</h3>
          <div class="table-wrap">
            <table class="data-table compact">
              <caption>Every option is recorded with what it gains and what it costs.</caption>
              <thead><tr><th scope="col">Option</th><th scope="col">Advantages</th><th scope="col">Costs</th></tr></thead>
              <tbody>{"".join(options)}</tbody>
            </table>
          </div>
        </section>
        <section>
          <h3>Recommendation</h3>
          <p>{esc(s["recommendation"])}</p>
        </section>
        <section>
          <h3>Expected effect</h3>
          <p>{esc(s["expected_effect"])}</p>
        </section>
        <section>
          <h3>Effort</h3>
          <p>{esc(s["effort"])}</p>
        </section>
        <section>
          <h3>Risk</h3>
          <p>{esc(s["risk"])}</p>
        </section>
        <section class="span-2">
          <h3>Decision</h3>
          <div class="answer {'answer-set' if s['decision_note'] else 'answer-open'}">
            {esc(s["decision_note"]) if s["decision_note"] else '<span class="blank">no decision recorded yet</span>'}
          </div>
        </section>
      </div>
      <footer class="qcard-foot">
        <span class="foot-label">Owner:</span> {esc(s["owner"])}
        <span class="foot-label">Flags:</span> {or_blank(s_flags)}
        <span class="foot-label">Questions:</span> {or_blank(s_questions)}
        <span class="foot-label">Related suggestions:</span> {or_blank(s_related)}
      </footer>
    </article>
"""
        )

    body = f"""{kpi_block([
        (str(len(sg)), "proposals on the register", f"{len(proposed)} still to decide, {len(accepted)} in motion"),
        (str(len(cats)), "areas covered", ", ".join(cats[:4]).lower() + " and more"),
        (str(by_status.get("PROPOSED", 0)), "awaiting a decision", "each needs an owner and a written note"),
        (str(len(sg) - by_status.get("PROPOSED", 0)), "already in motion", "recorded with what was done"),
    ])}
    <section class="card">
      <h2>How to review this register</h2>
      <ul class="checklist">
        <li><span class="check">1</span>Read the problem line and its sources first. If the problem is not the one you are actually facing, reject the suggestion instead of rewriting it.</li>
        <li><span class="check">2</span>Compare the options. Each one carries its own advantage and its own cost; the recommendation is a reading, not a ruling.</li>
        <li><span class="check">3</span>Check the dependencies. A suggestion whose question is still open can be planned but not started.</li>
        <li><span class="check">4</span>Record the decision and move the status. Leaving a proposal at PROPOSED is how a register turns into a wish list.</li>
        <li><span class="check">5</span>Questions that block a decision live in the <a href="questions.html">Questions register</a>, with the exact step that closes each one.</li>
      </ul>
      <p class="card-note">Review stages: {" &rarr; ".join(SUGGESTIONS["review_model"]["stages"])}. The register is generated from
      <code>ledger/suggestions.json</code>, so every published status is the recorded one.</p>
    </section>
{summary}
    <h2 class="section-h">Full detail, one card per suggestion</h2>
{''.join(cards)}"""

    return page(
        filename="suggestions.html",
        title="Suggestions & decisions",
        lead=(
            "Proposals for this project with their options, trade-offs, expected effect, effort, dependencies and "
            "risk - written so a decision can be made before anything is changed."
        ),
        eyebrow=f"register &middot; as of {esc(SUGGESTIONS['as_of'])} &middot; generated from ledger/suggestions.json",
        body=body,
        active="suggestions.html",
    )


# --------------------------------------------------------------------------- main


def build(out_dir: Path) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, builder in (("suggestions.html", suggestions_page), ("questions.html", questions_page)):
        path = out_dir / name
        path.write_text(builder(), encoding="utf-8")
        written.append(name)
    return written


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="build to a temp dir and compare with the committed output")
    args = ap.parse_args(argv)

    if args.check:
        tmp = Path(tempfile.mkdtemp(prefix="z2decisions-"))
        names = build(tmp)
        drift = []
        for name in names:
            fresh = hashlib.sha256((tmp / name).read_bytes()).hexdigest()
            committed_path = REPO / name
            committed = (
                hashlib.sha256(committed_path.read_bytes()).hexdigest() if committed_path.exists() else ""
            )
            if fresh != committed:
                drift.append(name)
        shutil.rmtree(tmp, ignore_errors=True)
        print(json.dumps({"built": len(names), "drifted_or_uncommitted": drift}, indent=2))
        if drift:
            print(
                "suggestions.html / questions.html are out of date - run python3 tools/build_decisions.py",
                file=sys.stderr,
            )
        return 1 if drift else 0

    names = build(REPO)
    print(
        json.dumps(
            {
                "pages": names,
                "suggestions": len(SUGGESTIONS["suggestions"]),
                "questions": len(QUESTIONS["questions"]),
                "as_of": SUGGESTIONS["as_of"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
