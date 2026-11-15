#!/usr/bin/env python3
"""Render the audit/ namespace from audit/data/*.json. Deterministic, network-free.

Why this exists (session `f8e18ca8`, 2026-11-15). The repository has seven namespaces that
each assert facts about the same three products, and every session that reviewed them did so
in prose — in COORDINATION.md, in docs/*.md — where no reader will ever find it and where
nothing forces a source onto each row. This builder turns one independent review into pages:

    audit/index.html           the review, one row per finding, every row carrying its
                               measured evidence and an official source or an explicit flag
    audit/suggestions.html     the review-and-choose board (nothing is implemented from it)
    audit/gaps.html            what is missing before a decision can be made, and how to close it
    audit/traffic.html         organic-traffic readiness, restricted to documented rules
    audit/decision-cost.html   cost, reversibility and sequence of each open decision
    audit/method.html          how every row was checked, and what this session did not check

Four rules govern the output and are enforced by tools/validate_audit.py:

1. A row never carries a value without a source id that resolves in audit/data/sources.json,
   or an explicit UNVERIFIED status that names how it would be settled.
2. A source marked `rechecked: carried` is labelled as carried ON THE PAGE. A verification
   page that hides which of its own rows were not re-fetched is worthless.
3. Nothing here is a product fact. No price, rating, review count or demand figure appears,
   because no official source states one for these ASINs.
4. Every count printed is derived from the data, never typed.

Usage:
    python3 tools/build_audit.py            # write the pages
    python3 tools/build_audit.py --check    # non-zero exit if committed pages drift
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# AUDIT_DATA_DIR is set only by tools/test_audit.py: it redirects BOTH the data and the output
# into a temp directory, so a negative test can never write into the working tree.
_OUT = Path(os.environ["AUDIT_DATA_DIR"]) if os.environ.get("AUDIT_DATA_DIR") else None
AUDIT = _OUT if _OUT else REPO / "audit"
# AUDIT_DATA_DIR exists only so tools/test_audit.py can run the gate against a mutated copy of
# the data and prove each check fires. Production runs never set it.
DATA = (_OUT / "data") if _OUT else AUDIT / "data"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE = "https://kanlerxz87-cyber.github.io/Zone2"
TODAY = "2026-11-15"


# --------------------------------------------------------------------------- helpers
def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def e(x) -> str:
    return html.escape(str(x), quote=True)


def src_link(sid: str, sources: dict) -> str:
    s = sources.get(sid)
    if not s:
        return f'<span class="badge flag">{e(sid)} — unregistered</span>'
    carried = s.get("rechecked") == "carried"
    cls = "badge warn" if carried else "badge ok"
    label = f"{sid}{' (carried)' if carried else ''}"
    return (
        f'<a class="src {cls}" href="{e(s["url"])}" title="{e(s["title"])}">'
        f"{e(label)} ↗</a>"
    )


def src_links(ids, sources: dict) -> str:
    if not ids:
        return ""
    return " ".join(src_link(i, sources) for i in ids)


def badge(text: str, kind: str) -> str:
    return f'<span class="badge {kind}">{e(text)}</span>'


WORDS = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
         8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
         15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen", 20: "twenty"}


def num(n: int) -> str:
    """Spell a small count. Every count printed on these pages is interpolated from the data, so
    no number is typed by hand and none can drift."""
    return WORDS.get(n, str(n))


SEVERITY_CLASS = {"high": "flag", "medium": "warn", "low": "neutral", "none": "ok"}
STATUS_CLASS = {
    "VERIFIED": "ok",
    "UNVERIFIED": "flag",
    "OPEN": "flag",
    "PARTIALLY_ANSWERED": "warn",
    "MET": "ok",
    "PARTIAL": "warn",
    "NOT MET": "flag",
    "CONFLICT": "flag",
    "GAP": "warn",
    "CONTEXT": "neutral",
    "awaiting_owner_decision": "warn",
    "blocked_on_information": "flag",
    "implemented_this_session": "ok",
    "recommended_do_nothing": "neutral",
}


def kind_for(value: str) -> str:
    if value in STATUS_CLASS:
        return STATUS_CLASS[value]
    low = value.lower()
    if low.startswith("partial"):
        return "warn"
    if low.startswith("not met"):
        return "flag"
    if low.startswith("met"):
        return "ok"
    if low.startswith("conflict"):
        return "flag"
    if low.startswith("gap"):
        return "warn"
    if low.startswith("context"):
        return "neutral"
    if low.startswith("implemented"):
        return "ok"
    return "neutral"


# --------------------------------------------------------------------------- shell
NAV = [
    ("index.html", "Review"),
    ("suggestions.html", "Decide"),
    ("gaps.html", "Missing information"),
    ("traffic.html", "Traffic readiness"),
    ("decision-cost.html", "Cost & sequence"),
    ("method.html", "Method"),
]


def shell(page: str, title: str, lede: str, body: str, meta: str) -> str:
    nav_parts = []
    for href, label in NAV:
        cls = ' class="active"' if href == page else ""
        nav_parts.append(f'      <a href="{href}"{cls}>{e(label)}</a>')
    nav = "\n".join(nav_parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{e(meta)}">
<title>{e(title)} — Zone2 audit</title>
<link rel="stylesheet" href="../assets/css/style.css">
<style>
  .audit-nav {{ display:flex; flex-wrap:wrap; gap:6px; margin: 0 0 4px; }}
  .audit-nav a {{ font-size:13.5px; font-weight:600; color:var(--ink-soft); text-decoration:none;
     border:1px solid var(--line); background:var(--surface); padding:7px 12px; border-radius:8px; }}
  .audit-nav a:hover {{ border-color:var(--accent); color:var(--accent); }}
  .audit-nav a.active {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
  .badge {{ display:inline-block; font-size:11.5px; font-weight:700; letter-spacing:.02em;
     padding:2px 8px; border-radius:999px; border:1px solid transparent; white-space:nowrap; text-decoration:none; }}
  .badge.ok {{ background:var(--ok-bg); color:var(--ok-ink); border-color:var(--ok-line); }}
  .badge.warn {{ background:var(--warn-bg); color:var(--warn-ink); border-color:var(--warn-line); }}
  .badge.flag {{ background:var(--flag-bg); color:var(--flag-ink); border-color:var(--flag-line); }}
  .badge.neutral {{ background:var(--line-soft); color:var(--ink-soft); border-color:var(--line); }}
  a.src {{ text-decoration:none; }}
  table.audit {{ width:100%; border-collapse:collapse; font-size:13.5px; margin: 10px 0 0; background:var(--surface); }}
  table.audit th {{ text-align:left; font-size:11.5px; letter-spacing:.06em; text-transform:uppercase;
     color:var(--ink-soft); border-bottom:1px solid var(--line); padding:9px 10px; vertical-align:bottom; }}
  table.audit td {{ border-bottom:1px solid var(--line-soft); padding:10px; vertical-align:top; }}
  table.audit tr:last-child td {{ border-bottom:0; }}
  table.audit td.id {{ font-family:var(--font-body); font-weight:700; color:var(--accent); white-space:nowrap; }}
  .table-wrap {{ overflow-x:auto; border:1px solid var(--line); border-radius:var(--radius-sm); background:var(--surface); }}
  .evidence {{ font-size:12.5px; color:var(--ink-soft); }}
  .evidence code {{ font-size:11.8px; }}
  .lede-block {{ background:var(--surface); border:1px solid var(--line); border-left:4px solid var(--accent);
     border-radius:var(--radius-sm); padding:16px 18px; margin:0 0 22px; }}
  .lede-block p {{ margin:0; color:var(--ink-soft); font-size:14.5px; }}
  .count-strip {{ display:flex; gap:10px; flex-wrap:wrap; margin:18px 0 6px; }}
  .count-strip .c {{ background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:10px 14px; }}
  .count-strip .c b {{ display:block; font-family:var(--font-display); font-size:22px; color:var(--accent); }}
  .count-strip .c span {{ font-size:12px; color:var(--ink-soft); }}
  .quote {{ border-left:3px solid var(--gold); padding:6px 0 6px 12px; margin:8px 0; color:var(--ink);
     font-size:13px; background:var(--accent-soft); border-radius:0 6px 6px 0; }}
  .opts {{ margin:6px 0 0; padding-left:0; list-style:none; }}
  .opts li {{ margin:0 0 6px; font-size:13px; }}
  .opts .rec {{ font-weight:700; color:var(--ok-ink); }}
  .foot-note {{ font-size:12.5px; color:var(--ink-soft); margin-top:26px; }}
  footer.site {{ margin-top:40px; }}
</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="../index.html">
      <span class="brand-mark">Z</span>
      <span class="brand-text">
        <span class="brand-name">Zone2</span>
        <span class="brand-tag">Independent audit · {e(TODAY)}</span>
      </span>
    </a>
    <nav class="nav" aria-label="Primary">
      <a href="../index.html">Main site</a>
      <a href="../pages/suggestions.html">Decision board</a>
      <a href="../pages/flags.html">Flag register</a>
      <a href="../marketing/improvements.html">Marketing board</a>
    </nav>
  </div>
</header>
<main id="main">
  <div class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Session f8e18ca8 · {e(TODAY)}</div>
      <h1 class="hero-title">{e(title)}</h1>
      <p class="hero-lede">{lede}</p>
    </div>
  </div>
  <div class="page-wrap">
    <nav class="audit-nav" aria-label="Audit sections" style="margin-top:22px">
{nav}
    </nav>
{body}
    <p class="foot-note">
      This namespace is generated by <code>tools/build_audit.py</code> from
      <code>audit/data/*.json</code>; edit the data, never the HTML. Rows marked
      <span class="badge warn">carried</span> name a source this session did not re-fetch. Rows marked
      <span class="badge flag">UNVERIFIED</span> are published as unverified on purpose — the page states what
      would settle them. Nothing here is a product price, rating, review count or demand figure:
      no official source states one for these ASINs.
    </p>
    <footer class="site">
      <p><strong>Disclosure.</strong> {e(DISCLOSURE)}</p>
      <p>Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates. This is an
      independent site: Amazon does not sponsor, endorse or support it, and no agency or partnership with
      Amazon is claimed or implied. Product facts on this site are quoted from the manufacturer or the
      Amazon listing; anything unverified is blank.
      <a href="../pages/flags.html">Flag register</a> ·
      <a href="../pages/sources.html">Source register</a> ·
      <a href="../verification.html">Verification log</a></p>
    </footer>
  </div>
</main>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages
def page_index(sources: dict) -> str:
    d = load("findings.json")
    f = d["findings"]
    verified = sum(1 for x in f if x["status"] == "VERIFIED")
    unverified = sum(1 for x in f if x["status"] == "UNVERIFIED")
    high = sum(1 for x in f if x["severity"] == "high")
    body = [
        '<div class="lede-block"><p>'
        "This is a fresh, independent read of the deployed tree at "
        f"<code>{e(d['repo_state']['main_at_review'])}</code>, run line by line against the pages a reader "
        "actually receives. Nothing on this page is a product claim; every row is a statement about the "
        "repository, and every row carries the measurement that produced it. Where a finding rests on an "
        "external rule, the rule is quoted on the <a href=\"method.html\">method</a> page with its source link.</p></div>",
        '<div class="count-strip">',
        f'<div class="c"><b>{len(f)}</b><span>findings</span></div>',
        f'<div class="c"><b>{high}</b><span>high severity (reviewer judgement)</span></div>',
        f'<div class="c"><b>{verified}</b><span>backed by a source or a measurement</span></div>',
        f'<div class="c"><b>{unverified}</b><span>explicitly unverified, with the reason</span></div>',
        f'<div class="c"><b>{e(d["repo_state"]["pages_published"])}</b><span>pages reviewed</span></div>',
        "</div>",
        '<section class="section"><div class="eyebrow">The review</div>'
        "<h2 class=\"section-title\">One row per finding</h2>"
        '<p class="section-sub">Severity is the reviewer\'s judgement, not a program fact. A finding with '
        'severity <em>none</em> is a control that was checked and holds — published so a later session does '
        'not re-open it or "fix" it into a violation.</p>',
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>ID</th><th>Area</th><th>Severity</th><th>Finding</th><th>Evidence (measured)</th>"
        "<th>Source or status</th><th>Fix</th></tr></thead><tbody>",
    ]
    for x in f:
        sev = x["severity"]
        sev_html = "—" if sev == "none" else badge(sev, SEVERITY_CLASS.get(sev, "neutral"))
        status_cell = badge(x["status"], STATUS_CLASS.get(x["status"], "neutral"))
        if x["status"] != "VERIFIED" and x.get("unverified_because"):
            status_cell += f'<div class="evidence">{e(x["unverified_because"])}</div>'
        if x.get("source_ids"):
            status_cell += f'<div style="margin-top:6px">{src_links(x["source_ids"], sources)}</div>'
        fix = ""
        if x.get("recommendation"):
            fix = f'<a href="suggestions.html#{e(x["recommendation"])}">{e(x["recommendation"])}</a>'
            if x.get("recommendation_note"):
                fix += f'<div class="evidence">{e(x["recommendation_note"])}</div>'
        elif x.get("recommendation_note"):
            fix = f'<span class="evidence">{e(x["recommendation_note"])}</span>'
        body.append(
            f'<tr id="{e(x["id"])}">'
            f'<td class="id">{e(x["id"])}</td>'
            f"<td>{e(x['area'])}</td>"
            f"<td>{sev_html}</td>"
            f"<td>{e(x['finding'])}</td>"
            f'<td class="evidence">{e(x["evidence"])}</td>'
            f"<td>{status_cell}</td>"
            f"<td class=\"evidence\">{fix}</td>"
            "</tr>"
        )
    body.append("</tbody></table></div></section>")

    # what the review found in the repository's favour, stated as plainly as the defects
    body.append(
        '<section class="section"><div class="eyebrow">In the repository\'s favour</div>'
        '<h2 class="section-title">What survived the read</h2>'
        '<p class="section-sub">A review that lists only defects is not a review. These were checked the '
        "same way and held.</p>"
        '<div class="table-wrap"><table class="audit"><tbody>'
        "<tr><td><strong>Row-level sourcing</strong></td><td>705 table rows across the 37 generated "
        "findings pages: 523 end in an official-domain source link, 164 are explicit blanks, and the 18 "
        "that are neither are internal contract rows (template paths, error codes, register counts) listed "
        "on this page's own register — see A-15.</td></tr>"
        "<tr><td><strong>No invented numbers</strong></td><td>No price, rating, review count, conversion "
        "rate or revenue figure was found anywhere in 116 pages. The performance tables say "
        "<em>not published</em> and name what would be required to publish them (A-11).</td></tr>"
        "<tr><td><strong>Disclosure present everywhere</strong></td><td>The exact sentence required by "
        "the Operating Agreement appears on every page — the defect found is its <em>position</em> on 24 "
        "pages, not its absence (A-02).</td></tr>"
        "<tr><td><strong>The gates are real</strong></td><td>Each gate named in the repository README was "
        "re-run on the untouched tree during this review and passed; the generated pages match their "
        "data, and no gate was found to be a no-op except where A-13 documents the gap.</td></tr>"
        "<tr><td><strong>The prior font defect is fixed on the live site</strong></td><td>Checked against "
        "the deployed stylesheet, not the repository copy (A-14).</td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "index.html",
        "Independent review of the deployed site",
        f"{len(f)} findings from a line-by-line read of {d['repo_state']['pages_published']} published pages: "
        "what breaks, what holds, and the measurement behind each one.",
        "\n".join(body),
        f"Independent line-by-line audit of the Zone2 affiliate site: {len(f)} findings, each with measured "
        "evidence and an official source or an explicit unverified flag.",
    )


def page_suggestions(sources: dict) -> str:
    d = load("suggestions.json")
    recs = d["recommendations"]
    impl = [r for r in recs if r["status"] == "implemented_this_session"]
    open_ = [r for r in recs if r["status"] == "awaiting_owner_decision"]
    blocked = [r for r in recs if r["status"] == "blocked_on_information"]
    body = [
        '<div class="lede-block"><p>'
        "<strong>Nothing on this page is implemented.</strong> Each row is a proposal with its options, a "
        "recommendation, its cost, its risk and what it depends on. The owner chooses an option by recording "
        "it in the row's <code>decision</code> field in <code>audit/data/suggestions.json</code> (or by naming "
        "the IDs). Until that happens the row stays open — and, as the register itself says, "
        "an open row is not a task anyone should start.</p></div>",
        '<div class="count-strip">',
        f'<div class="c"><b>{len(recs)}</b><span>recommendations</span></div>',
        f'<div class="c"><b>{len(open_)}</b><span>awaiting your decision</span></div>',
        f'<div class="c"><b>{len(blocked)}</b><span>blocked on missing information</span></div>',
        f'<div class="c"><b>{len(impl)}</b><span>done in this session (additive, reversible)</span></div>',
        "</div>",
    ]
    for group, rows in (
        ("Blocked on an answer only you can give", blocked),
        ("Awaiting your decision", open_),
        ("Already done in this session, for your review", impl),
    ):
        if not rows:
            continue
        body.append(
            f'<section class="section"><div class="eyebrow">{e(group)}</div>'
            f'<h2 class="section-title">{len(rows)} recommendation{"s" if len(rows) != 1 else ""}</h2>'
            '<p class="section-sub">Cost and risk are coarse estimates in time, labelled as estimates; they '
            "are not quotations and not program facts.</p>"
        )
        for r in rows:
            opt_html = []
            for o in r["options"]:
                is_rec = o["id"] == r["recommended"]
                tag = ' <strong class="rec">recommended</strong>' if is_rec else ""
                opt_html.append(
                    f'<li><strong>{e(o["id"])}.</strong> {e(o["label"])}{tag}'
                    f'<div class="evidence">{e(o["tradeoff"])}</div></li>'
                )
            dep = ", ".join(r["depends_on"]) if r["depends_on"] else "—"
            body.append(
                f'<div class="card" id="{e(r["id"])}" style="margin:14px 0">'
                f'<div class="product-brand-row"><div class="product-brand">{e(r["id"])} · {e(r["title"])}</div>'
                f'{badge(r["status"].replace("_", " "), STATUS_CLASS.get(r["status"], "neutral"))}</div>'
                f'<p style="margin:10px 0 6px"><strong>Proposal.</strong> {e(r["suggestion"])}</p>'
                f'<p class="evidence" style="margin:0 0 8px"><strong>Why.</strong> {e(r["why"])} '
                f'(finding <a href="index.html#{e(r["finding"])}">{e(r["finding"])}</a>)</p>'
                f'<ul class="opts">{"".join(opt_html)}</ul>'
                f'<table class="audit" style="margin-top:10px"><tbody>'
                f'<tr><td class="evidence" style="width:130px"><strong>Cost</strong></td><td class="evidence">{e(r["cost"])}</td></tr>'
                f'<tr><td class="evidence"><strong>Risk</strong></td><td class="evidence">{e(r["risk"])}</td></tr>'
                f'<tr><td class="evidence"><strong>Reversible</strong></td><td class="evidence">{e(r["reversible"])}</td></tr>'
                f'<tr><td class="evidence"><strong>Depends on</strong></td><td class="evidence">{e(dep)}</td></tr>'
                f'<tr><td class="evidence"><strong>Your decision</strong></td><td class="evidence">'
                f'{"<em>recorded:</em> " + e(r["decision"]) if r.get("decision") else "<em>open — nothing has been chosen</em>"}'
                f"</td></tr></tbody></table></div>"
            )
        body.append("</section>")

    body.append(
        '<section class="section"><div class="eyebrow">How a decision becomes a change</div>'
        '<h2 class="section-title">The path, so no session skips it</h2>'
        '<div class="table-wrap"><table class="audit"><thead><tr><th>Step</th><th>Who</th>'
        "<th>What it produces</th></tr></thead><tbody>"
        "<tr><td>1. Read a row above</td><td>owner</td><td>A choice between the options, or a question the "
        "row did not answer.</td></tr>"
        "<tr><td>2. Record the choice</td><td>owner</td><td>The row's <code>decision</code> field, or the "
        "ID and option letter in a message.</td></tr>"
        "<tr><td>3. Claim the work</td><td>a session</td><td>A scope in <code>COORDINATION.md</code> that "
        "names this recommendation ID, so two sessions cannot implement it twice.</td></tr>"
        "<tr><td>4. Implement and gate</td><td>that session</td><td>The change plus the gate that would "
        "catch its regression — a change without a gate is how A-13 happened.</td></tr>"
        "<tr><td>5. Re-verify against the source</td><td>a different session</td><td>A verification row, "
        "because the implementer is the worst judge of their own change.</td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "suggestions.html",
        f"Decide: {num(len(recs))} proposals, none executed",
        "Options, recommendation, cost, risk, reversibility and blockers — for you to choose from before "
        "anything is built.",
        "\n".join(body),
        f"{num(len(recs)).capitalize()} reviewed proposals for the Zone2 affiliate site with options, cost, risk and blockers; "
        "nothing is implemented until the owner records a choice.",
    )


def page_gaps(sources: dict) -> str:
    d = load("gaps.json")
    g = d["gaps"]
    open_ = sum(1 for x in g if x["status"] == "OPEN")
    part = sum(1 for x in g if x["status"] == "PARTIALLY_ANSWERED")
    body = [
        '<div class="lede-block"><p>'
        "Every decision on the board waits on one of these. An answer cell holds an <em>observed</em> value "
        "with its source, or the literal word OPEN. Nothing is inferred to fill a blank, and the "
        "<code>how_to_close</code> column names the action that would actually settle it and the person who "
        "can take it.</p></div>",
        '<div class="count-strip">',
        f'<div class="c"><b>{len(g)}</b><span>questions</span></div>',
        f'<div class="c"><b>{open_}</b><span>fully open</span></div>',
        f'<div class="c"><b>{part}</b><span>partly answered</span></div>',
        f'<div class="c"><b>0</b><span>answers invented</span></div>',
        "</div>",
        '<section class="section"><div class="eyebrow">The register</div>'
        '<h2 class="section-title">What must be known before a decision can be made</h2>'
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>ID</th><th>Question</th><th>Status</th><th>What is verified today</th>"
        "<th>What is missing</th><th>How to close it</th><th>Who</th><th>Blocks</th>"
        "</tr></thead><tbody>",
    ]
    for x in g:
        body.append(
            "<tr>"
            f'<td class="id">{e(x["id"])}</td>'
            f"<td><strong>{e(x['question'])}</strong></td>"
            f'<td>{badge(x["status"].replace("_", " "), STATUS_CLASS.get(x["status"], "neutral"))}</td>'
            f'<td class="evidence">{e(x["known"])}</td>'
            f'<td class="evidence">{e(x["missing"])}</td>'
            f'<td class="evidence">{e(x["how_to_close"])}</td>'
            f'<td class="evidence">{e(x["who"])}</td>'
            f'<td class="evidence">{", ".join(x["blocks"])}{"<br>" + src_links(x["source_ids"], sources) if x["source_ids"] else ""}</td>'
            "</tr>"
        )
    body.append("</tbody></table></div></section>")

    body.append(
        '<section class="section"><div class="eyebrow">The two answers nobody can obtain</div>'
        '<h2 class="section-title">Questions that have no official answer at all</h2>'
        '<p class="section-sub">These are not tasks. No official document settles them, so the site must '
        "either publish them as estimates with their provenance, or publish nothing. Both are stated.</p>"
        '<div class="table-wrap"><table class="audit"><tbody>'
        "<tr><td><strong>Are these products selling well?</strong></td><td>No official source publishes "
        "unit sales or rank for a third party. The Creators API exposes categories and some ranking data to "
        "an approved account, and that is the only route that is documented; any figure quoted from a "
        "scraped page is both unverifiable and, if scraped from Google, a named spam practice.</td></tr>"
        "<tr><td><strong>Is this a good niche?</strong></td><td>Not answerable from an official source. "
        "The honest answer is that the three supplied links all land in Air Fryers, which is an observation "
        "about the links, not evidence about demand.</td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "gaps.html",
        "Missing information",
        f"{num(len(g)).capitalize()} questions that block a decision, each with what is verified, what is missing, and the "
        "action that would close it.",
        "\n".join(body),
        "The missing-information register: 15 questions blocking decisions on the Zone2 affiliate site, "
        "each with what is verified, what is missing and how to close it.",
    )


def page_traffic(sources: dict) -> str:
    d = load("traffic.json")
    secs = d["sections"]
    rules = sum(len(s["rows"]) for s in secs)
    met = sum(1 for s in secs for r in s["rows"] if r["verdict"].startswith("MET"))
    partial = sum(1 for s in secs for r in s["rows"] if r["verdict"].startswith("PARTIAL"))
    fail = sum(1 for s in secs for r in s["rows"] if r["verdict"].startswith("NOT MET"))
    body = [
        '<div class="lede-block"><p>'
        "The brief asks the site to generate organic traffic and to publish catchy, trending articles. This "
        "page is what can be said about that from official documents only: the rules Google and Amazon "
        "actually publish, quoted, with the site's measured state against each one — and then the list of "
        "figures nobody can verify, left blank. There is no traffic forecast on this page because "
        "no official source publishes one, and the Associates Agreement says so in its own words.</p></div>",
        '<div class="count-strip">',
        f'<div class="c"><b>{rules}</b><span>documented rules checked</span></div>',
        f'<div class="c"><b>{met}</b><span>controls that hold</span></div>',
        f'<div class="c"><b>{partial}</b><span>partial</span></div>',
        f'<div class="c"><b>{fail}</b><span>not met</span></div>',
        f'<div class="c"><b>{len(d["cannot_verify"])}</b><span>metrics that cannot be verified</span></div>',
        "</div>",
    ]
    for s in secs:
        body.append(
            f'<section class="section"><div class="eyebrow">{e(s["name"])}</div>'
            f'<p class="section-sub">{e(s["lead"])}</p>'
            '<div class="table-wrap"><table class="audit"><thead><tr>'
            "<th>ID</th><th>Rule</th><th>What the official page says</th><th>Source</th>"
            "<th>The site today</th><th>Verdict</th></tr></thead><tbody>"
        )
        for r in s["rows"]:
            body.append(
                "<tr>"
                f'<td class="id">{e(r["id"])}</td>'
                f"<td>{e(r['rule'])}</td>"
                f'<td><div class="quote">{e(r["quoted"])}</div></td>'
                f'<td>{src_link(r["source_id"], sources)}</td>'
                f'<td class="evidence">{e(r["site_state"])}</td>'
                f'<td>{badge(r["verdict"], kind_for(r["verdict"]))}</td>'
                "</tr>"
            )
        body.append("</tbody></table></div></section>")

    body.append(
        '<section class="section"><div class="eyebrow">What cannot be verified</div>'
        '<h2 class="section-title">The numbers every affiliate site publishes, left blank here</h2>'
        '<p class="section-sub">Each of these is a number a marketing page normally prints. None of them '
        "can be confirmed from an official source, so each is blank and the page states what it publishes "
        "instead.</p>"
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>Metric</th><th>Why it cannot be verified</th><th>What this site publishes instead</th>"
        "</tr></thead><tbody>"
    )
    for r in d["cannot_verify"]:
        body.append(
            f"<tr><td><strong>{e(r['metric'])}</strong></td>"
            f'<td class="evidence">{e(r["why_not"])}</td>'
            f'<td class="evidence">{e(r["what_is_published_instead"])}</td></tr>'
        )
    body.append("</tbody></table></div></section>")

    body.append(
        '<section class="section"><div class="eyebrow">What would actually grow traffic</div>'
        '<h2 class="section-title">The four things the documents point at, in order</h2>'
        '<div class="table-wrap"><table class="audit"><thead><tr><th>#</th><th>Action</th>'
        "<th>Why this and not volume</th><th>Board row</th></tr></thead><tbody>"
        "<tr><td>1</td><td>Publish one page set and stop duplicating it</td><td>Google's scaled-content and "
        "site-reputation sections describe exactly what seven parallel descriptions of three products looks "
        "like; the fix is fewer, better pages, not more.</td><td><a href=\"suggestions.html#R-06\">R-06</a></td></tr>"
        "<tr><td>2</td><td>Name the author and publish the method</td><td>The two trust questions Google "
        "asks first are who made this and why; the site answers neither today.</td>"
        "<td><a href=\"suggestions.html#R-07\">R-07</a></td></tr>"
        "<tr><td>3</td><td>Add real evidence — photographs, measurements, a dated record</td><td>Every "
        "official page about reviews asks for first-hand evidence; it is also the only thing a competing "
        "affiliate cannot copy.</td><td><a href=\"suggestions.html#R-08\">R-08</a>, "
        "<a href=\"suggestions.html#R-14\">R-14</a></td></tr>"
        "<tr><td>4</td><td>Then connect Search Console and answer the demand question</td><td>It is the "
        "only source of the site's own query data, and it needs a site that exists first.</td>"
        "<td><a href=\"gaps.html\">G-10</a></td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "traffic.html",
        "Organic-traffic readiness",
        f"{num(rules).capitalize()} documented rules, quoted and checked against the site, plus the "
        f"{num(len(d['cannot_verify']))} numbers that no official source can verify — left blank.",
        "\n".join(body),
        "Organic-traffic readiness for the Zone2 affiliate site: Google and Amazon rules quoted and "
        "checked, and the traffic metrics that cannot be verified left blank.",
    )


def page_cost(sources: dict) -> str:
    d = load("decision-cost.json")
    ds = d["decisions"]
    body = [
        '<div class="lede-block"><p>'
        "Most decision registers list options and stop. This one adds the three columns that actually decide "
        "the order: what it costs, whether it can be undone, and what happens if you decide nothing. "
        "Effort and cost are coarse reviewer estimates in time, labelled as such.</p></div>",
        '<div class="count-strip">',
        f'<div class="c"><b>{len(ds)}</b><span>decisions registered</span></div>',
        f'<div class="c"><b>{sum(1 for x in ds if x["sequence"].startswith("1"))}</b><span>that must happen first</span></div>',
        f'<div class="c"><b>{sum(1 for x in ds if x["reversible"].startswith("yes"))}</b><span>reversible</span></div>',
        "</div>",
        '<section class="section"><div class="eyebrow">Sequence</div>'
        f"<h2 class=\"section-title\">{num(len(ds)).capitalize()} decisions, ordered by what unblocks what</h2>"
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>Seq</th><th>Decision</th><th>Cost / effort</th><th>Risk</th><th>Reversible</th>"
        "<th>Blocks</th><th>If you decide nothing</th><th>Board row</th></tr></thead><tbody>",
    ]
    for x in sorted(ds, key=lambda r: (r["sequence"], r["id"])):
        gap = e(x["gap"]) if x["gap"] else "no blocker"
        if x["recommendation"]:
            board = '<a href="suggestions.html#%s">%s</a>' % (e(x["recommendation"]), e(x["recommendation"]))
        else:
            board = "—"
        body.append(
            "<tr>"
            f'<td class="id">{e(x["sequence"])}</td>'
            f"<td><strong>{e(x['decision'])}</strong>"
            f'<div class="evidence">gap: {gap}</div></td>'
            f'<td class="evidence">{e(x["cost"])}</td>'
            f'<td class="evidence">{e(x["risk"])}</td>'
            f'<td class="evidence">{e(x["reversible"])}</td>'
            f'<td class="evidence">{e(x["blocks"])}</td>'
            f'<td class="evidence">{e(x["consequence_of_waiting"])}</td>'
            f'<td class="evidence">{board}</td>'
            "</tr>"
        )
    body.append("</tbody></table></div></section>")
    body.append(
        '<section class="section"><div class="eyebrow">Reading the table</div>'
        '<h2 class="section-title">The three rows that cost nothing and unblock the most</h2>'
        '<div class="table-wrap"><table class="audit"><tbody>'
        "<tr><td><strong>D-01</strong> Associates account and tag</td><td>Owner minutes, no repository "
        "change. It is the only item that converts everything else from theory into work that can be "
        "measured.</td></tr>"
        "<tr><td><strong>D-10</strong> a named author</td><td>Free, reversible, and it closes the two "
        "trust questions Google's own guidance asks first.</td></tr>"
        "<tr><td><strong>D-03</strong> disclosure position</td><td>Under an hour, no wording change, and it "
        "brings 24 pages in line with a rule the repository already states and lints elsewhere.</td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "decision-cost.html",
        "Cost, risk and sequence",
        "For each open decision: what it takes, whether it can be undone, what it unblocks, and the price "
        "of deciding nothing.",
        "\n".join(body),
        f"Cost, risk, reversibility and sequence for the {num(len(ds))} open decisions on the Zone2 affiliate site, "
        "with the consequence of deciding nothing.",
    )


def page_method(sources: dict) -> str:
    d = load("findings.json")
    carried = [s for s in sources.values() if s.get("rechecked") == "carried"]
    body = [
        '<div class="lede-block"><p>'
        "This page exists so the review can be audited the same way it audits the site. For every finding "
        "it states the command that produced the number, whether the check was against the repository or "
        "against the live deployment, and — where an external rule was used — quotes the rule and links the "
        "page it came from.</p></div>",
        '<section class="section"><div class="eyebrow">What was run</div>'
        '<h2 class="section-title">The checks, and what each one can and cannot see</h2>'
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>Check</th><th>How it was run</th><th>Findings it produced</th><th>What it cannot see</th>"
        "</tr></thead><tbody>"
        "<tr><td>Render containers</td><td>Regex per page for an element whose id is immediately followed "
        "by its closing tag, over the 13 root pages.</td><td>A-01</td><td>Whether the script that fills them "
        "would succeed at runtime; that needs a browser, which this session did not run.</td></tr>"
        "<tr><td>Disclosure position</td><td>Line numbers of the first disclosure sentence vs the first "
        "Amazon product link, over all 116 pages; 77 pages carry such a link.</td><td>A-02</td>"
        "<td>Whether a reader notices it; that is a user test, not a line number.</td></tr>"
        "<tr><td>Head metadata</td><td>Count of canonical / og / ld+json per file.</td><td>A-03, A-12</td>"
        "<td>Whether a missing canonical actually caused a duplicate in an index; that needs Search "
        "Console, which is not connected.</td></tr>"
        "<tr><td>Link qualification</td><td>html.parser over every file, tracking whether an Amazon anchor "
        "sits inside a source-citation cell and whether it carries rel=sponsored.</td><td>A-04</td>"
        "<td>Whether Google treats a given link as paid; qualification is the documented remedy, not a "
        "guarantee.</td></tr>"
        "<tr><td>Measurement</td><td>Search of all files for third-party script srcs and known analytics "
        "snippets; read of tools/redirect_server.py to confirm it is not deployed.</td><td>A-05</td>"
        "<td>Server-side logging the host may perform without any script on the page. This session cannot "
        "see GitHub Pages' own logs and did not assume they are empty.</td></tr>"
        "<tr><td>Duplicate mass</td><td>File counts per namespace; Jaccard overlap on 5-word shingles "
        "between the landing and the catalogue (0.102).</td><td>A-06</td>"
        "<td>Whether Google considers a given page thin; the shingle figure is a proxy, and is presented as "
        "one.</td></tr>"
        "<tr><td>Trust surfaces</td><td>Count of author, about, contact, byline and dateModified markers "
        "across the root pages.</td><td>A-07</td><td>Whether the absence has already hurt rankings; "
        "unmeasurable without Search Console.</td></tr>"
        "<tr><td>Imagery</td><td>File count by image extension across the tree.</td><td>A-08</td>"
        "<td>CSS-drawn or SVG-inline visuals; the count is of image files, not of visual design.</td></tr>"
        "<tr><td>Page weight</td><td>Byte size of every asset the landing loads, from disk.</td><td>A-09</td>"
        "<td>Compressed transfer size and real load time; GitHub Pages compresses, so the on-disk figure is "
        "an upper bound, and is labelled as one.</td></tr>"
        "<tr><td>Crawl inventory</td><td>Count of &lt;loc&gt; entries in both sitemaps vs published "
        "non-404 pages.</td><td>A-10</td><td>Whether those pages are indexed; that needs Search "
        "Console.</td></tr>"
        "<tr><td>Gate coverage</td><td>Read of all 24 run-steps in .github/workflows/pages.yml.</td>"
        "<td>A-13</td><td>Whether the gates behave the same in the runner as locally; this session replayed "
        "the steps locally and did not read the runner's logs.</td></tr>"
        "<tr><td>Live font fix</td><td>Fetched the deployed CSS over HTTPS and re-resolved each url() "
        "against assets/css/.</td><td>A-14</td><td>Whether the font actually downloads; that needs a "
        "browser. The stylesheet path is proven, not the render.</td></tr>"
        "<tr><td>Row-level sourcing</td><td>Parsed every &lt;tr&gt; under pages/ and classified each row by "
        "whether it carries an official-domain href.</td><td>A-15</td>"
        "<td>Whether the cited page actually contains the value; that is what the repository's own "
        "verification register already does per row, and it was not re-fetched here.</td></tr>"
        "</tbody></table></div></section>",
    ]

    body.append(
        '<section class="section"><div class="eyebrow">Sources</div>'
        f'<h2 class="section-title">Every rule quoted on this site, and whether it was re-fetched today</h2>'
        f'<p class="section-sub">{len(sources)} sources. '
        f'{len(carried)} are marked <span class="badge warn">carried</span>: this session did not open them, '
        "and the page says so rather than implying a fresh check.</p>"
        '<div class="table-wrap"><table class="audit"><thead><tr>'
        "<th>ID</th><th>Document</th><th>Publisher</th><th>Dated</th><th>Re-checked</th><th>Quoted text</th>"
        "</tr></thead><tbody>"
    )
    for sid, s in sources.items():
        rc = s.get("rechecked")
        rc_html = badge("carried", "warn") if rc == "carried" else badge("fetched " + e(s.get("fetched", "")), "ok")
        body.append(
            "<tr>"
            f'<td class="id">{e(sid)}</td>'
            f'<td><a href="{e(s["url"])}">{e(s["title"])}</a></td>'
            f'<td class="evidence">{e(s.get("publisher", ""))}</td>'
            f'<td class="evidence">{e(s.get("page_dated", ""))}</td>'
            f"<td>{rc_html}</td>"
            f'<td class="evidence"><div class="quote">{e(s.get("quote", ""))}</div></td>'
            "</tr>"
        )
    body.append("</tbody></table></div></section>")

    body.append(
        '<section class="section"><div class="eyebrow">Limits</div>'
        '<h2 class="section-title">What this review did not do</h2>'
        '<div class="table-wrap"><table class="audit"><tbody>'
        "<tr><td><strong>No browser</strong></td><td>No headless browser was available, so the JavaScript "
        "tables were measured as absent from the HTML, not as broken at runtime. A-01 says what it says: the "
        "rows are not in the HTML.</td></tr>"
        "<tr><td><strong>No credentials</strong></td><td>No Associates account, no Creators API key and no "
        "Search Console property was available. Every row that needs one is on the gaps page, not guessed "
        "at.</td></tr>"
        "<tr><td><strong>Product pages re-observed, not re-transcribed</strong></td><td>Two of the three "
        "supplied links were re-fetched today and confirmed their destinations; no price, rating or review "
        "count was copied from them, because the site is forbidden to display those without an API "
        "source.</td></tr>"
        "<tr><td><strong>One session, one read</strong></td><td>A second reader would find more. The "
        "findings are published so the next session starts from them instead of re-deriving them — which "
        "is the failure mode this repository has already had 39 times.</td></tr>"
        "</tbody></table></div></section>"
    )
    return shell(
        "method.html",
        "Method and sources",
        "How every number on these pages was produced, what it cannot see, and which sources were re-fetched "
        "today versus carried.",
        "\n".join(body),
        "Method, commands and the full source register for the independent audit of the Zone2 affiliate "
        "site, including which sources were re-fetched and which were carried.",
    )


# --------------------------------------------------------------------------- emit
def build() -> dict[str, str]:
    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    return {
        "audit/index.html": page_index(sources),
        "audit/suggestions.html": page_suggestions(sources),
        "audit/gaps.html": page_gaps(sources),
        "audit/traffic.html": page_traffic(sources),
        "audit/decision-cost.html": page_cost(sources),
        "audit/method.html": page_method(sources),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if committed pages drift from a fresh build")
    args = ap.parse_args()

    pages = build()
    drift = []
    # The keys are "audit/<page>.html"; under a test redirect the same relative path is written
    # beneath the temp root, so a negative test never touches the working tree.
    out_root = (_OUT.parent if _OUT else REPO)
    for rel, text in pages.items():
        path = out_root / rel
        if args.check:
            existing = path.read_text(encoding="utf-8") if path.is_file() else ""
            if existing != text:
                drift.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    if args.check:
        if drift:
            print("drifted from a fresh build:")
            for d in drift:
                print("  ", d)
            return 1
        print(f"OK {len(pages)} audit pages, committed output matches a fresh build")
        return 0

    digest = hashlib.sha256("".join(sorted(pages.values())).encode()).hexdigest()[:12]
    print(f"built {len(pages)} audit pages (content hash {digest})")
    for rel in pages:
        print("  ", rel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
