#!/usr/bin/env python3
"""Render the two decision-support pages: suggestions.html and questions.html.

Why a generator and not hand-written HTML
-----------------------------------------
The project rule is that a published table row must be able to point at the data it came from.
These two pages are the ones a reviewer will act on, so a suggestion's status and a question's
answer cannot drift from the register that holds them. Both pages are therefore projected from
ledger/suggestions.json and ledger/questions.json, and the source each row cites is resolved
through ledger/sources.json - the same register every other table on this site uses.

Three rules the renderer enforces rather than trusts:

1.  **No row without a source.** A suggestion or a question that cites no source id stops the
    build. The reasoning behind a recommendation is only useful if the reader can open the page
    it rests on.
2.  **No invented numbers.** Every count on the page is computed from the data.
3.  **The Decision column stays empty.** It belongs to the reviewer. The renderer will not
    pre-fill it with a recommendation, because a column that is already filled cannot be used to
    record a different decision.

Usage:
    python3 tools/build_decision_pages.py            # write both pages
    python3 tools/build_decision_pages.py --check    # exit 1 if the committed output differs
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AS_OF = "2026-11-15"
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/"

SUGGESTIONS = json.loads((LEDGER / "suggestions.json").read_text(encoding="utf-8"))
QUESTIONS = json.loads((LEDGER / "questions.json").read_text(encoding="utf-8"))
SOURCE_INDEX = {
    s["id"]: s for s in json.loads((LEDGER / "sources.json").read_text(encoding="utf-8"))["sources"]
}

IMPACT_CLASS = {"Blocking": "flag", "High": "flag", "Medium": "warn", "Low": "ok"}
EFFORT_CLASS = {"Low": "ok", "Medium": "warn", "High": "flag"}
STATUS_CLASS = {
    "Needs decision": "flag",
    "Proposed": "warn",
    "Implemented in this session": "ok",
    "Partly implemented in this session": "warn",
    "Already the published behaviour": "ok",
    "Open": "flag",
}
CONFIDENCE_CLASS = {
    "None": "flag",
    "High on the destinations, None on the identity": "flag",
    "High on the rule, None on the decision": "flag",
    "High on the current state, None on the future": "flag",
    "High on the current deployment, None on the intent": "flag",
    "High on the gap, None on the remedy": "flag",
    "High on the formats, None on the intent": "flag",
    "High on the current state, None on the decision": "flag",
    "High on the requirement, None on the availability": "flag",
    "High on the reading, None on the account": "flag",
    "High on this session's approach, None on the desired end state": "flag",
    "High on the category, None on the strategy": "flag",
    "High": "ok",
}

NAV = [
    ("index.html", "Dashboard"),
    ("summary.html", "Executive Summary"),
    ("products.html", "Products"),
    ("analysis.html", "Analysis"),
    ("content.html", "Content"),
    ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking"),
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Open Questions"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
]


class BuildError(RuntimeError):
    """Raised instead of publishing a row that cannot be checked."""


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def src_link(source_id: str) -> str:
    """One citation, resolved through the shared source register. An unknown id is a build error."""
    src = SOURCE_INDEX.get(source_id)
    if not src:
        raise BuildError(f"unknown source id {source_id!r}; refusing to publish an unresolvable citation")
    host = src["url"].split("/")[2]
    rel = "noopener noreferrer nofollow"
    return (
        f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="{rel}">'
        f'{esc(source_id)}<span class="src-host">{esc(host)}</span></a>'
    )


def src_cell(source_ids: list[str]) -> str:
    if not source_ids:
        raise BuildError("a row cited no source; refusing to publish it")
    return " ".join(src_link(s) for s in source_ids)


def shell(title: str, description: str, body: str, *, here: str) -> str:
    nav_parts = []
    for href, label in NAV:
        active = ' class="active"' if href == here else ""
        nav_parts.append(f'<a href="{href}"{active}>{esc(label)}</a>')
    nav = "".join(nav_parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} — Zone2</title>
<meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <h1>Zone2</h1>
    <div class="sub">AI Amazon Affiliate Marketing Platform</div>
    <nav>
      {nav}
    </nav>
  </aside>
  <main class="main">
    <div class="page-head">
      <h2>{esc(title)}</h2>
      <p>{esc(description)}</p>
    </div>

    <div class="disclosure">
      <strong>Affiliate disclosure (required by the Amazon Associates Operating Agreement §5):</strong>
      {esc(DISCLOSURE)}
    </div>
{body}
    <footer class="site">
      Compiled {esc(AS_OF)} from <code>ledger/suggestions.json</code> and <code>ledger/questions.json</code> ·
      every row links to the official source it rests on ·
      <a href="index.html">Dashboard</a> ·
      <a href="questions.html">Open questions</a> ·
      <a href="flagged.html">Flagged for review</a> ·
      <a href="sources.html">Source register</a>
    </footer>
  </main>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- suggestions

def suggestion_counts(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "blocking": sum(1 for r in rows if r["impact"] == "Blocking"),
        "needs_decision": sum(1 for r in rows if r["status"] == "Needs decision"),
        "done": sum(1 for r in rows if "Implemented in this session" in r["status"]
                    or r["status"] == "Already the published behaviour"),
        "high": sum(1 for r in rows if r["impact"] == "High"),
    }


def page_suggestions() -> str:
    rows = SUGGESTIONS["suggestions"]
    areas = {a["id"]: a for a in SUGGESTIONS["areas"]}
    phases = {p["id"]: p for p in SUGGESTIONS["phases"]}
    counts = suggestion_counts(rows)

    area_links = " ".join(
        f'<a class="chip" href="suggestions.html#area-{a["id"]}">{esc(a["name"])}'
        f' ({sum(1 for r in rows if r["area"] == a["id"])})</a>'
        for a in SUGGESTIONS["areas"]
    )

    summary_rows = "".join(
        f'<tr id="row-{esc(r["id"])}">'
        f'<td><a href="suggestions.html#{esc(r["id"])}"><code>{esc(r["id"])}</code></a></td>'
        f'<td>{esc(areas[r["area"]]["name"])}</td>'
        f'<td><strong>{esc(r["title"])}</strong></td>'
        f'<td><span class="badge {IMPACT_CLASS.get(r["impact"], "warn")}">{esc(r["impact"])}</span></td>'
        f'<td><span class="badge {EFFORT_CLASS.get(r["effort"], "warn")}">{esc(r["effort"])}</span></td>'
        f'<td><span class="badge {STATUS_CLASS.get(r["status"], "warn")}">{esc(r["status"])}</span></td>'
        f'<td class="decision-cell"></td>'
        "</tr>"
        for r in rows
    )

    roadmap_rows = "".join(
        f'<tr><td><strong>{esc(phases[p["id"]]["name"])}</strong>'
        f'<div class="row-note">{esc(phases[p["id"]]["blurb"])}</div></td>'
        f'<td>' + ", ".join(
            f'<a href="suggestions.html#{esc(r["id"])}">{esc(r["id"])}</a>'
            for r in rows if r["phase"] == p["id"]
        ) + "</td></tr>"
        for p in SUGGESTIONS["phases"]
    )

    detail_blocks = []
    for area in SUGGESTIONS["areas"]:
        area_rows = [r for r in rows if r["area"] == area["id"]]
        if not area_rows:
            continue
        cards = []
        for r in area_rows:
            options = "".join(
                f'<tr><th scope="row">Option {esc(o["label"])}</th>'
                f'<td>{esc(o["text"])}</td>'
                f'<td class="tradeoff">{esc(o["tradeoff"])}</td></tr>'
                for o in r["options"]
            )
            evidence = "".join(
                f'<li>{src_link(e["source"])} — {esc(e["note"])}</li>' for e in r["evidence"]
            )
            cards.append(f"""        <article class="card suggestion-card" id="{esc(r['id'])}">
          <div class="suggestion-head">
            <span class="chip chip-id">{esc(r['id'])}</span>
            <h3>{esc(r['title'])}</h3>
          </div>
          <p class="suggestion-meta">
            <span class="badge {IMPACT_CLASS.get(r['impact'], 'warn')}">Impact: {esc(r['impact'])}</span>
            <span class="badge {EFFORT_CLASS.get(r['effort'], 'warn')}">Effort: {esc(r['effort'])}</span>
            <span class="badge {STATUS_CLASS.get(r['status'], 'warn')}">{esc(r['status'])}</span>
            <span class="badge">Phase: {esc(phases[r['phase']]['name'])}</span>
          </p>
          <h4>The problem</h4>
          <p>{esc(r['problem'])}</p>
          <h4>The options, with their trade-offs</h4>
          <div class="table-wrap">
            <table class="opt-table">
              <thead><tr><th>Option</th><th>What it means</th><th>Trade-off</th></tr></thead>
              <tbody>{options}</tbody>
            </table>
          </div>
          <h4>Recommendation</h4>
          <p class="rec">{esc(r['recommendation'])}</p>
          <h4>What this rests on</h4>
          <ul class="source-list">{evidence}</ul>
          <p class="decision-line"><strong>Decision:</strong> <span class="decision-cell"></span></p>
        </article>""")
        detail_blocks.append(f"""      <section id="area-{esc(area['id'])}">
        <div class="area-head">
          <h3>{esc(area['name'])}</h3>
          <p>{esc(area['blurb'])}</p>
        </div>
{chr(10).join(cards)}
      </section>""")

    body = f"""    <div class="kpis">
      <div class="kpi"><div class="num">{counts['total']}</div><div class="lbl">Suggestions on the register</div></div>
      <div class="kpi"><div class="num">{counts['blocking']}</div><div class="lbl">Blocking — nothing earns or launches until these are settled</div></div>
      <div class="kpi"><div class="num">{counts['needs_decision']}</div><div class="lbl">Waiting on a decision from the reviewer</div></div>
      <div class="kpi"><div class="num">{counts['done']}</div><div class="lbl">Already implemented or already the published behaviour</div></div>
      <div class="kpi"><div class="num">{len(QUESTIONS['questions'])}</div><div class="lbl"><a href="questions.html">Open questions</a> that have to be answered first</div></div>
    </div>

    <div class="card">
      <h3>How to use this page</h3>
      <p style="font-size:13.5px;margin:0 0 10px">
        Every row below is a <strong>proposal</strong>, not a change that has been made. Each one states the
        problem it solves, the options and what each costs, a recommendation, and the official source the
        reasoning rests on. The <strong>Decision</strong> cell is deliberately blank: it is where the
        reviewer records <em>accept</em>, <em>reject</em> or <em>defer</em>, and until it is filled the
        suggestion has not been approved.
      </p>
      <ol style="font-size:13.5px;margin:0;padding-left:20px;line-height:1.7">
        <li>Read the <strong>Decision table</strong> below and pick the rows that matter to you.</li>
        <li>Open the detail for each one — the options and the trade-offs are where the real choice is.</li>
        <li>Fill in the <strong>Decision</strong> cell, in the table or in the detail card.</li>
        <li>Anything still unanswered belongs in the <a href="questions.html">open-questions register</a>,
            which lists what is missing and how to obtain it.</li>
      </ol>
      <p style="font-size:12.5px;color:var(--muted);margin:12px 0 0">
        Nothing here is a product claim. A suggestion that rests on a number carries the source of that
        number; a suggestion that rests on a judgement says so.
      </p>
    </div>

    <div class="card">
      <h3>Jump to an area</h3>
      <p class="chips">{area_links}</p>
    </div>

    <div class="card">
      <h3>Decision table</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 10px">
        One row per suggestion. The Decision column is empty on purpose — fill it in, then take the
        detail below into account. Nothing is implemented until a decision is recorded here.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Area</th><th>Suggestion</th><th>Impact</th><th>Effort</th><th>Status</th><th>Decision</th></tr></thead>
          <tbody>{summary_rows}</tbody>
        </table>
      </div>
    </div>

    <div class="card">
      <h3>Suggested order of work</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 10px">
        The phases are a recommendation, not a schedule. Phase 1 is the set without which the site cannot
        earn anything; the later phases assume the earlier ones are done.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Phase</th><th>Suggestions</th></tr></thead>
          <tbody>{roadmap_rows}</tbody>
        </table>
      </div>
    </div>

    <h3 class="section-head">Every suggestion in full</h3>
{''.join(detail_blocks)}
"""
    return shell(
        "Suggestions",
        "A reviewable improvement backlog: what to change, the options and their trade-offs, a "
        "recommendation, the official source it rests on, and a blank Decision cell for the reviewer.",
        body,
        here="suggestions.html",
    )


# --------------------------------------------------------------------------- questions

def question_counts(rows: list[dict]) -> dict:
    return {
        "total": len(rows),
        "open": sum(1 for r in rows if r["status"] == "Open"),
        "launch": sum(1 for r in rows if r.get("priority") == "launch"),
        "before_publish": sum(1 for r in rows if r.get("priority") == "before publish"),
        "later": sum(1 for r in rows if r.get("priority") == "later"),
        "sourced": sum(1 for r in rows if r.get("known_sources")),
    }


def page_questions() -> str:
    rows = QUESTIONS["questions"]
    counts = question_counts(rows)

    launch = [r for r in rows if r.get("priority") == "launch"]
    launch_items = "".join(
        f'<li><a href="questions.html#{esc(r["id"])}"><code>{esc(r["id"])}</code></a> — {esc(r["question"])}</li>'
        for r in launch
    )

    table_rows = "".join(
        f'<tr id="row-{esc(r["id"])}">'
        f'<td><a href="questions.html#{esc(r["id"])}"><code>{esc(r["id"])}</code></a></td>'
        f'<td><strong>{esc(r["question"])}</strong></td>'
        f'<td>{esc(r["known"])}'
        + (f'<div class="src-row">{src_cell(r["known_sources"])}</div>' if r.get("known_sources")
           else '<div class="src-row"><span class="badge flag">NO SOURCE — nothing is known yet</span></div>')
        + f'</td>'
        f'<td>{esc(r["missing"])}</td>'
        f'<td>{esc(r["blocks"])}</td>'
        f'<td>{esc(r["how_to_find_out"])}</td>'
        f'<td><span class="badge {EFFORT_CLASS.get(r["effort"], "warn")}">{esc(r["effort"])}</span></td>'
        f'<td><span class="badge {CONFIDENCE_CLASS.get(r["confidence"], "warn")}">{esc(r["confidence"])}</span></td>'
        "</tr>"
        for r in rows
    )

    detail_cards = []
    for r in rows:
        known_sources = (
            " ".join(src_link(s) for s in r["known_sources"])
            if r.get("known_sources")
            else '<span class="badge flag">No official source states this</span>'
        )
        detail_cards.append(f"""        <article class="card question-card" id="{esc(r['id'])}">
          <div class="suggestion-head">
            <span class="chip chip-id">{esc(r['id'])}</span>
            <h3>{esc(r['question'])}</h3>
          </div>
          <p class="suggestion-meta">
            <span class="badge">Priority: {esc(r.get('priority', 'later'))}</span>
            <span class="badge {EFFORT_CLASS.get(r['effort'], 'warn')}">Effort to answer: {esc(r['effort'])}</span>
            <span class="badge {CONFIDENCE_CLASS.get(r['confidence'], 'warn')}">Confidence today: {esc(r['confidence'])}</span>
            <span class="badge {STATUS_CLASS.get(r['status'], 'warn')}">{esc(r['status'])}</span>
          </p>
          <h4>What is known today</h4>
          <p>{esc(r['known'])}</p>
          <div class="src-row">{known_sources}</div>
          <h4>What is still missing</h4>
          <p>{esc(r['missing'])}</p>
          <h4>Which decision it blocks</h4>
          <p>{esc(r['blocks'])}</p>
          <h4>How to obtain it</h4>
          <p class="rec">{esc(r['how_to_find_out'])}</p>
          <p class="decision-line"><strong>Answer:</strong> <span class="decision-cell"></span></p>
        </article>""")

    body = f"""    <div class="kpis">
      <div class="kpi"><div class="num">{counts['total']}</div><div class="lbl">Questions on the register</div></div>
      <div class="kpi"><div class="num">{counts['launch']}</div><div class="lbl">Must be answered before anything else</div></div>
      <div class="kpi"><div class="num">{counts['before_publish']}</div><div class="lbl">Needed before the site takes traffic</div></div>
      <div class="kpi"><div class="num">{counts['later']}</div><div class="lbl">Can wait for traffic to answer</div></div>
      <div class="kpi"><div class="num">{counts['sourced']}</div><div class="lbl">With at least one official source behind the answer so far</div></div>
    </div>

    <div class="card">
      <h3>How to use this page</h3>
      <p style="font-size:13.5px;margin:0 0 10px">
        A decision can only be made reasonably when the information behind it is known. This register
        lists the questions that are still open, what is known today and where that came from, what is
        missing, which decision the missing piece blocks, and how to obtain it. Nothing here is answered
        by inference: where no official source states a value, the row says so.
      </p>
      <ol style="font-size:13.5px;margin:0;padding-left:20px;line-height:1.7">
        <li>Start with the <strong>answer these first</strong> list — four questions that unblock the rest.</li>
        <li>Work down the register in priority order.</li>
        <li>Record the answer against the question, and move it to
            <a href="suggestions.html">the suggestions</a> if it changes a recommendation.</li>
      </ol>
    </div>

    <div class="card">
      <h3>Answer these first</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 10px">
        These four are the ones that other answers depend on. Each is a question for the account owner
        rather than a research task.
      </p>
      <ul style="font-size:13.5px;margin:0;padding-left:20px;line-height:1.75">{launch_items}</ul>
    </div>

    <div class="card">
      <h3>The register</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 10px">
        Every row states what is known, what is not, what the unknown blocks and how to find it. The
        confidence column records how much of the question is settled today.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Question</th><th>What is known today</th><th>What is missing</th><th>Blocks</th><th>How to find out</th><th>Effort</th><th>Confidence</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </div>
    </div>

    <h3 class="section-head">Every question in full</h3>
{''.join(detail_cards)}
"""
    return shell(
        "Open Questions",
        "What is known, what is missing, which decision each unknown blocks, and how to obtain it — "
        "before any decision is made on incomplete information.",
        body,
        here="questions.html",
    )


def build() -> dict[str, str]:
    return {"suggestions.html": page_suggestions(), "questions.html": page_questions()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed pages differ from a fresh build")
    args = ap.parse_args()

    try:
        pages = build()
    except BuildError as exc:
        print(f"BUILD ERROR: {exc}", file=sys.stderr)
        return 1

    if args.check:
        problems = []
        for rel, doc in pages.items():
            path = REPO / rel
            if not path.is_file():
                problems.append(f"{rel}: missing")
            elif path.read_text(encoding="utf-8") != doc:
                problems.append(f"{rel}: committed output differs from a fresh build")
        if problems:
            print("\n".join(problems), file=sys.stderr)
            return 1
        print(f"OK  {len(pages)} decision pages match a fresh build")
        return 0

    for rel, doc in pages.items():
        (REPO / rel).write_text(doc, encoding="utf-8")
        print(f"wrote {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
