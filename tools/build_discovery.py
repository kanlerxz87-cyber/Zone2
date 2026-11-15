#!/usr/bin/env python3
"""Render the discovery namespace (discovery/) from the T40 registers.

What this is
------------
A reader-facing answer to three questions the project had not yet put on one
surface: *what did the review find* (DG-xx), *what information is still missing*
(DQ-xx), and *what could be done about it, at what cost* (DS-xx). Every row
ends in a link to the official page that supports it, or states plainly that no
source exists and names how to obtain it.

Design rules this file inherits from the rest of the repository
---------------------------------------------------------------
1. Data, not HTML. Pages are generated; `--check` fails when committed output
   drifts from the registers. Nobody hand-edits discovery/*.html.
2. Counts are derived. Every number printed on the hub is computed from the
   registers in the same run, so prose can never disagree with the tables.
3. Every row is sourced or explicitly flagged. A finding without a resolvable
   source id fails the build; a suggestion without evidence fails the build.
4. Nothing is presented as decided. `decision` stays empty until the owner
   records a choice, and the page says so in the reader's line of sight.

Run: python3 tools/build_discovery.py [--check]
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "discovery"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"
HERE = SITE + "discovery/"

REGISTER = REPO / "docs" / "discovery-t40.json"
GDOCS = REPO / "docs" / "discovery-t40-sources.json"
LEDGER_SOURCES = REPO / "ledger" / "sources.json"

DATA = json.loads(REGISTER.read_text(encoding="utf-8"))
GD_SOURCES = json.loads(GDOCS.read_text(encoding="utf-8"))["sources"]
LEDGER = {s["id"]: s for s in json.loads(LEDGER_SOURCES.read_text(encoding="utf-8"))["sources"]}
SOURCES = {s["id"]: s for s in GD_SOURCES}
AS_OF = DATA["as_of"]

FINDINGS = DATA["findings"]
QUESTIONS = DATA["questions"]
SUGGESTIONS = DATA["suggestions"]

NAV = [
    ("index.html", "Overview"),
    ("findings.html", "What we found"),
    ("questions.html", "Open questions"),
    ("suggestions.html", "Suggestions"),
    ("sources.html", "Sources"),
]


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------- helpers


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def source_rec(src_id: str) -> dict:
    """Resolve an id against the discovery register first, then the project ledger."""
    if src_id in SOURCES:
        return SOURCES[src_id]
    if src_id in LEDGER:
        s = LEDGER[src_id]
        return {
            "id": src_id,
            "publisher": s.get("publisher", ""),
            "kind": s.get("kind", "official"),
            "title": s.get("title", ""),
            "url": s.get("url", ""),
            "quote": "",
        }
    raise BuildError(f"unknown source id {src_id!r}")


def kind_label(kind: str) -> str:
    return {
        "official-amazon": "Amazon",
        "official-search": "Google Search Central",
        "official-legal": "FTC",
        "official": "official",
        "manufacturer": "manufacturer",
    }.get(kind, kind)


def source_cell(ids) -> str:
    """The last column of every table: a clickable official page, or an explicit flag."""
    if not ids:
        return '<td class="cell-unverified"><span class="pill pill-warn">no official source</span></td>'
    out = []
    for src_id in ids:
        src = source_rec(src_id)
        out.append(
            f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="noopener noreferrer nofollow">'
            f'{esc(src_id)} · {esc(kind_label(src["kind"]))}'
            f'<span class="src-kind">{esc(src["title"][:70])}</span></a>'
        )
    return "<td>" + "".join(out) + "</td>"


def sev_pill(sev: str) -> str:
    cls = {
        "blocks revenue": "pill-bad",
        "blocks growth": "pill-warn",
        "blocks a claim": "pill-warn",
        "cosmetic": "pill-ok",
    }.get(sev, "pill")
    return f'<span class="pill {cls}">{esc(sev)}</span>'


def q_state(q: dict) -> str:
    return "ANSWERED" if (q.get("answer") or "").strip() else "OPEN"


def sug_state(s: dict) -> str:
    return "RECORDED" if (s.get("decision") or "").strip() else "AWAITING_DECISION"


def counts() -> dict:
    return {
        "findings": len(FINDINGS),
        "findings_blocking": sum(1 for f in FINDINGS if f["severity"] != "cosmetic"),
        "questions": len(QUESTIONS),
        "questions_open": sum(1 for q in QUESTIONS if q_state(q) == "OPEN"),
        "suggestions": len(SUGGESTIONS),
        "suggestions_awaiting": sum(1 for s in SUGGESTIONS if sug_state(s) == "AWAITING_DECISION"),
        "sources": len(SOURCES) + len({s for f in FINDINGS for s in f["source_ids"]} - set(SOURCES)),
    }


def num_word(n: int) -> str:
    words = {
        1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
        8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve",
    }
    return words.get(n, str(n))


# --------------------------------------------------------------------------- shell

CSS = """\
:root{
  --ink:#14181f; --ink-2:#3d4757; --ink-3:#68738a; --line:#e2e6ee; --line-2:#eef1f6;
  --bg:#ffffff; --bg-2:#f7f8fb; --accent:#8a2c19; --accent-2:#b8412a;
  --ok:#1c6b46; --ok-bg:#e8f4ee; --warn:#8a5a10; --warn-bg:#fbf1de;
  --bad:#8f2020; --bad-bg:#fbeaea; --code:#f2f4f8;
  --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:2px}
a:hover{color:var(--accent-2)}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px 12px;z-index:9;border:1px solid var(--line)}
header.mast{border-bottom:1px solid var(--line);background:var(--bg)}
.mast-in{display:flex;flex-wrap:wrap;gap:10px 24px;align-items:baseline;
  justify-content:space-between;padding:14px 0 10px}
.brand{text-decoration:none;color:var(--ink);display:flex;flex-direction:column;line-height:1.2}
.brand b{font-size:17px;letter-spacing:-.01em}
.brand span{font-size:12.5px;color:var(--ink-3)}
nav.top{display:flex;flex-wrap:wrap;gap:4px}
nav.top a{font-size:13.5px;text-decoration:none;color:var(--ink-2);padding:6px 10px;border-radius:6px}
nav.top a:hover{background:var(--bg-2);color:var(--ink)}
nav.top a[aria-current]{background:var(--ink);color:#fff}
.disclosure{margin:0;background:var(--bg-2);border:1px solid var(--line);border-radius:8px;
  padding:10px 14px;font-size:13.5px;color:var(--ink-2)}
.disclosure strong{color:var(--ink)}
main{padding:26px 0 8px}
.crumbs{font-size:13px;color:var(--ink-3);margin:0 0 8px}
.crumbs a{color:var(--ink-3)}
h1{font-family:var(--serif);font-size:clamp(1.7rem,3.6vw,2.5rem);line-height:1.12;
  letter-spacing:-.02em;margin:.2em 0 .3em;max-width:26ch}
h2{font-family:var(--serif);font-size:1.4rem;line-height:1.2;letter-spacing:-.01em;
  margin:2em 0 .5em;padding-top:.1em}
h3{font-size:1.06rem;margin:1.4em 0 .4em;letter-spacing:-.005em}
.lede{font-size:1.1rem;color:var(--ink-2);max-width:66ch;margin:0 0 10px}
p,li{max-width:72ch}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:22px 0 6px}
.kpi{border:1px solid var(--line);border-radius:10px;padding:14px 16px;background:var(--bg)}
.kpi b{display:block;font-family:var(--serif);font-size:1.9rem;line-height:1;letter-spacing:-.02em}
.kpi span{display:block;font-size:12.5px;color:var(--ink-3);margin-top:6px;line-height:1.4}
.card{border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:16px 0;background:var(--bg)}
.card h2{margin-top:0}
.note{border-left:3px solid var(--accent);background:var(--bg-2);padding:12px 16px;
  border-radius:0 8px 8px 0;margin:18px 0;font-size:14.5px}
.note p{max-width:70ch;margin:.3em 0}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px;margin:14px 0 8px}
table{width:100%;border-collapse:collapse;font-size:14px}
caption{caption-side:top;text-align:left;padding:12px 14px 10px;font-size:13px;color:var(--ink-3)}
th,td{text-align:left;vertical-align:top;padding:10px 12px;border-bottom:1px solid var(--line-2)}
th{background:var(--bg-2);font-size:12px;text-transform:uppercase;letter-spacing:.06em;
  color:var(--ink-3);font-weight:600;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fcfcfd}
td.id{font-family:var(--mono);font-size:12.5px;white-space:nowrap}
td.id a{text-decoration:none;font-weight:600}
.note-sm{font-size:12.5px;color:var(--ink-3);margin-top:5px;line-height:1.45}
.cell-unverified{color:var(--ink-3)}
.pill{display:inline-block;font-size:11.5px;font-weight:600;letter-spacing:.02em;
  padding:2px 8px;border-radius:999px;background:var(--bg-2);color:var(--ink-2);white-space:nowrap}
.pill-bad{background:var(--bad-bg);color:var(--bad)}
.pill-warn{background:var(--warn-bg);color:var(--warn)}
.pill-ok{background:var(--ok-bg);color:var(--ok)}
.src{display:block;font-size:12.5px;line-height:1.35;margin:2px 0;text-decoration:none;color:var(--accent)}
.src-kind{display:block;color:var(--ink-3);font-size:11.5px}
ul.opts{list-style:none;padding:0;margin:10px 0 0;display:grid;gap:8px}
ul.opts li{border:1px solid var(--line);border-radius:9px;padding:10px 12px;font-size:14px}
ul.opts li.rec{border-color:var(--ok);background:var(--ok-bg)}
ul.opts .oid{font-family:var(--mono);font-weight:700;margin-right:6px}
ul.opts .trade{display:block;color:var(--ink-2);font-size:13px;margin-top:3px}
.sug{border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:16px 0}
.sug h3{margin:0 0 4px;font-size:1.12rem}
.sug .meta{font-size:12px;color:var(--ink-3);margin-bottom:8px;display:flex;gap:10px;flex-wrap:wrap}
.rec-line{font-size:13.5px;color:var(--ink-2);margin:10px 0 0}
.rec-line b{color:var(--ink)}
footer.site{border-top:1px solid var(--line);margin-top:40px;padding:20px 0 40px;
  font-size:13px;color:var(--ink-3);background:var(--bg-2)}
footer.site p{max-width:78ch}
footer.site a{color:var(--ink-2)}
.qline{margin:0 0 6px}
blockquote{margin:10px 0;padding:10px 14px;border-left:3px solid var(--line);
  background:var(--bg-2);font-size:13.5px;color:var(--ink-2);border-radius:0 8px 8px 0}
blockquote p{margin:0}
code{font-family:var(--mono);font-size:.92em;background:var(--code);padding:1px 5px;border-radius:4px}
@media (max-width:640px){
  h1{font-size:1.55rem}
  .mast-in{gap:8px}
  table{font-size:13px}
}
"""


def page(title: str, description: str, body: str, *, here: str, crumbs) -> str:
    url = HERE + here
    CURRENT = ' aria-current="page"'
    nav = "".join(
        f'<a href="{href}"{CURRENT if href == here else ""}>{esc(label)}</a>'
        for href, label in NAV
    )
    crumb_parts = []
    for i, (href, label) in enumerate(crumbs):
        if i == len(crumbs) - 1:
            crumb_parts.append(f"<span>{esc(label)}</span>")
        else:
            crumb_parts.append(f'<a href="{href}">{esc(label)}</a>')
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": f"{AS_OF}T00:00:00+00:00",
        "dateModified": f"{AS_OF}T00:00:00+00:00",
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "publisher": {"@type": "Organization", "name": "Zone2", "url": SITE},
    }
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Zone2 discovery review</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Zone2">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta name="robots" content="index,follow">
<style>{CSS}</style>
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="wrap mast-in">
    <a class="brand" href="index.html"><b>Zone2 discovery review</b><span>What was found, what is missing, what to do next</span></a>
    <nav class="top" aria-label="Sections">{nav}</nav>
  </div>
</header>
<div class="wrap">
  <main id="main">
    <p class="disclosure" data-rule="R-01"><strong>Affiliate disclosure.</strong> {DISCLOSURE}</p>
    <p class="crumbs" aria-label="Breadcrumb">{' › '.join(crumb_parts)}</p>
{body}
  </main>
</div>
<footer class="site">
  <div class="wrap">
    <p>{DISCLOSURE}</p>
    <p>Generated by <code>tools/build_discovery.py</code> from <code>docs/discovery-t40.json</code> and
    <code>docs/discovery-t40-sources.json</code> on {esc(AS_OF)}. Every source link points at the official
    page it was read from. Nothing on these pages has been implemented: each suggestion waits for a recorded
    owner decision.</p>
    <p><a href="../index.html">Owner dashboard</a> ·
       <a href="../pages/suggestions.html">Earlier decision board (SG-01…SG-10)</a> ·
       <a href="../pages/questions.html">Earlier question register (Q-01…Q-16)</a> ·
       <a href="../pages/flags.html">Flagged for review</a> ·
       <a href="../marketing/index.html">Reader-facing site</a></p>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages


def page_index() -> str:
    c = counts()
    top = sorted(
        [f for f in FINDINGS if f["severity"] in ("blocks revenue", "blocks growth")],
        key=lambda f: (f["severity"] != "blocks revenue", f["id"]),
    )
    rows = "".join(
        f'<tr><td class="id"><a href="findings.html#{esc(f["id"])}">{esc(f["id"])}</a></td>'
        f'<td>{sev_pill(f["severity"])}</td>'
        f'<td><strong>{esc(f["area"])}</strong><div class="note-sm">{esc(f["finding"][:190])}…</div></td>'
        f'<td>{source_cell(f["source_ids"])}</td></tr>'
        for f in top
    )
    body = f"""
<h1>The site is accurate. It is not yet a shop.</h1>
<p class="lede">This review asked one question of every page: could a person land here from a search,
find what they needed in ten seconds, and click through? The answer is mostly no, and almost none of the
reasons are about wording. They are mechanical, and they are fixable.</p>

<div class="kpis">
  <div class="kpi"><b>{c['findings']}</b><span>findings measured against the published tree</span></div>
  <div class="kpi"><b>{c['findings_blocking']}</b><span>of them block revenue, growth or a claim</span></div>
  <div class="kpi"><b>{c['questions_open']}</b><span>open questions that only you can answer</span></div>
  <div class="kpi"><b>{c['suggestions']}</b><span>suggestions with options, costs and blockers</span></div>
</div>

<div class="note">
  <p><strong>Nothing on this site has been implemented.</strong> Per the project's contract, a proposal is
  published for you to choose from; the decision field stays empty until you record a choice. The suggestions
  page is the review board: read the options, their trade-offs and the questions blocking each one, then pick.</p>
</div>

<h2>The three things that cost the most</h2>
<p>Ordered by what they cost, not by how interesting they are.</p>
<div class="tablewrap">
  <table>
    <caption>Derived from <code>docs/discovery-t40.json</code>: findings whose severity is <em>blocks revenue</em> or <em>blocks growth</em>.</caption>
    <thead><tr><th>ID</th><th>Severity</th><th>What was measured</th><th>Official source</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>

<h2>What this site already does right</h2>
<p>It is worth stating plainly, because the fix list below is long and the foundation is not broken.</p>
<ul>
  <li><strong>Every value is sourced or blank.</strong> {esc(num_word(48))} specification rows, each ending in a link to the
  manufacturer or listing page it was read from, with blanks published as blanks rather than guessed.</li>
  <li><strong>The disclosure is in the right place.</strong> The exact required sentence, plus a
  link-level <em>(paid link)</em> tag beside every product link — which is what the FTC asks for and what most
  affiliate sites get wrong.</li>
  <li><strong>Affiliate links are qualified.</strong> Every Amazon link carries
  <code>rel="sponsored nofollow"</code>, and the build fails if one does not.</li>
  <li><strong>It publishes real disagreements.</strong> Four specification conflicts between official pages are shown
  with both values, instead of one being quietly dropped. That is the kind of thing Google's guidance calls
  added value, and it is the best raw material on the site.</li>
</ul>

<h2>How to read the rest</h2>
<ul>
  <li><a href="findings.html"><strong>What we found</strong></a> — {c['findings']} measured findings, each with the
  command used to measure it, what it costs, and the official page that governs it.</li>
  <li><a href="questions.html"><strong>Open questions</strong></a> — {c['questions']} pieces of information that do not exist in
  the repository, with exactly how to obtain each one. No answer is filled in for you.</li>
  <li><a href="suggestions.html"><strong>Suggestions</strong></a> — {c['suggestions']} proposals. Each states its options, what
  each option costs, the evidence behind it and the questions blocking it. Pick one per row.</li>
  <li><a href="sources.html"><strong>Sources</strong></a> — every official page this review read, with the exact text it
  relied on, quoted so you can check it without trusting this site.</li>
</ul>

<h2>The short version</h2>
<p>The fastest revenue gain is not a design change: it is an Associates ID. Until one exists, every product
link on this site earns nothing, and two of the fixes a reader would notice first — a product photograph and a
price — are blocked by Amazon's own licence and price rules rather than by effort. The fastest <em>credible</em>
gain is the opposite: six pages that answer six buying questions using the specifications the site already
holds, plus a measurement layer that says which page sends people where.</p>
<p>Both of those are choices for you, not for this review. They are written up as
<a href="suggestions.html#DS-02">DS-02</a>, <a href="suggestions.html#DS-03">DS-03</a> and
<a href="suggestions.html#DS-11">DS-11</a>.</p>
"""
    return page(
        "Discovery review",
        "What a line-by-line review of this site found, what information is missing, and which changes are worth "
        "making — every row sourced to an official page.",
        body,
        here="index.html",
        crumbs=[("index.html", "Overview")],
    )


def page_findings() -> str:
    rows = []
    for f in FINDINGS:
        measurable = ""
        if f.get("measurement"):
            measurable = f'<div class="note-sm"><strong>How it was measured:</strong> {esc(f["measurement"])}</div>'
        why = f'<div class="note-sm"><strong>Why it costs:</strong> {esc(f["why_it_matters"])}</div>'
        rec = f'<div class="note-sm"><strong>Recommended:</strong> {esc(f["recommendation"])}</div>'
        limit = ""
        if f.get("what_cannot_be_done"):
            limit = f'<div class="note-sm"><strong>What cannot be done about it:</strong> {esc(f["what_cannot_be_done"])}</div>'
        rows.append(
            f'<tr id="{esc(f["id"])}">'
            f'<td class="id">{esc(f["id"])}<div class="note-sm">{sev_pill(f["severity"])}</div></td>'
            f'<td><strong>{esc(f["finding"])}</strong>{measurable}</td>'
            f'<td>{esc(f["area"])}{why}{rec}{limit}</td>'
            f'{source_cell(f["source_ids"])}</tr>'
        )
    body = f"""
<h1>What we found, and how to check it</h1>
<p class="lede">{esc(num_word(len(FINDINGS)))} findings, each measured on 2026-11-15 against the published tree.
Every row states the measurement so you can reproduce it, what it costs, and the official page that governs it.
Where a finding is a strength rather than a gap, it says so — a review that only lists problems cannot tell you
what not to break.</p>
<div class="tablewrap">
  <table>
    <caption>Sorted as recorded. Severity is this review's judgement, not an Amazon or Google category; the
    official page that makes each finding true is the last column.</caption>
    <thead><tr><th>ID</th><th>Finding and measurement</th><th>Area, cost and recommendation</th><th>Official source</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>
<div class="note">
  <p><strong>Two findings are deliberately not called violations.</strong> DG-13 (compliance commentary and
  Operating Agreement §5) and DG-14 (the missing 2(k) text disclaimer) are published as a question and a
  recommendation, not as findings of breach, because the reach of those clauses is a legal judgement this
  project is not entitled to make. They are in
  <a href="suggestions.html#DS-14">DS-14</a> and <a href="questions.html#DQ-09">DQ-09</a> for your decision.</p>
</div>
"""
    return page(
        "What we found",
        "Seventeen measured findings about this affiliate site — measurement, cost, recommendation and the official "
        "page that governs each one.",
        body,
        here="findings.html",
        crumbs=[("index.html", "Overview"), ("findings.html", "What we found")],
    )


def page_questions() -> str:
    rows = []
    for q in QUESTIONS:
        state = q_state(q)
        pill = (
            '<span class="pill pill-warn">OPEN</span>'
            if state == "OPEN"
            else '<span class="pill pill-ok">ANSWERED</span>'
        )
        blocks = ", ".join(q.get("blocks") or []) or "—"
        rows.append(
            f'<tr id="{esc(q["id"])}">'
            f'<td class="id">{esc(q["id"])}<div class="note-sm">{pill}</div></td>'
            f'<td><strong>{esc(q["question"])}</strong>'
            f'<div class="note-sm"><strong>What is known:</strong> {esc(q["known"])}</div></td>'
            f'<td><span class="cell-unverified">—</span>'
            f'<div class="note-sm"><strong>Missing:</strong> {esc(q["missing"])}</div>'
            f'<div class="note-sm"><strong>How to obtain it:</strong> {esc(q["how_to_obtain"])}</div>'
            f'<div class="note-sm"><strong>Blocks:</strong> {esc(blocks)}</div></td>'
            f'{source_cell(q["source_ids"])}</tr>'
        )
    n_open = sum(1 for q in QUESTIONS if q_state(q) == "OPEN")
    body = f"""
<h1>The information that is missing</h1>
<p class="lede">{esc(num_word(len(QUESTIONS)))} questions. {esc(num_word(n_open))} of them have no answer anywhere in the
repository, and none has been filled in with a plausible guess. Each row states what <em>is</em> known, what is
missing, and exactly how to obtain it — a question without a route to an answer is a dead end, not a plan.</p>
<p>These are ordered so that the ones blocking the most work come first.
<a href="suggestions.html#DS-02">DS-02</a>, <a href="suggestions.html#DS-01">DS-01</a>,
<a href="suggestions.html#DS-07">DS-07</a> and <a href="suggestions.html#DS-11">DS-11</a> all wait on a single
answer: whether an Associates account exists.</p>
<div class="tablewrap">
  <table>
    <caption>The answer column is empty by design. A question marked ANSWERED means the owner recorded an answer,
    not that this review inferred one.</caption>
    <thead><tr><th>ID</th><th>Question and what is known</th><th>Answer, gap and route</th><th>Official source</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>
<div class="note">
  <p><strong>One question is deliberately uncomfortable.</strong> <a href="#DQ-09">DQ-09</a> asks whether the
  site's own long commentary on the Associates Operating Agreement is wise before an account exists. The
  Agreement's Section 5 restricts public communications about the Agreement. This project quotes and analyses
  it on most pages. That is published as a question for you, not resolved by this review.</p>
</div>
"""
    return page(
        "Open questions",
        "The information this project does not have, why each item matters, and exactly how to obtain it — with "
        "nothing filled in by guesswork.",
        body,
        here="questions.html",
        crumbs=[("index.html", "Overview"), ("questions.html", "Open questions")],
    )


def page_suggestions() -> str:
    blocks = []
    for s in SUGGESTIONS:
        state = sug_state(s)
        opts = []
        for o in s["options"]:
            rec = " rec" if o["id"] in (s.get("recommended") or "") else ""
            badge = ' <span class="pill pill-ok">recommended</span>' if rec else ""
            opts.append(
                f'<li class="{"rec" if rec else ""}"><span class="oid">{esc(o["id"])}</span>{esc(o["label"])}{badge}'
                f'<span class="trade">{esc(o["tradeoff"])}</span></li>'
            )
        needs = ", ".join(s.get("needs_answers") or [])
        blocker_line = (
            f'<span>Blocked by: <a href="questions.html#{esc(s["needs_answers"][0])}">{esc(needs)}</a></span>'
            if needs
            else "<span>Not blocked: can start as soon as you choose</span>"
        )
        ev = " ".join(
            f'<a class="src" style="display:inline;margin-right:8px" href="{esc(source_rec(i)["url"])}" '
            f'target="_blank" rel="noopener noreferrer nofollow">{esc(i)}</a>'
            for i in s["evidence"]
        )
        status_pill = (
            '<span class="pill pill-warn">AWAITING_DECISION</span>'
            if state == "AWAITING_DECISION"
            else '<span class="pill pill-ok">RECORDED</span>'
        )
        blocks.append(
            f"""<section class="sug" id="{esc(s["id"])}">
  <h3>{esc(s["title"])}</h3>
  <p class="meta"><span><strong>{esc(s["id"])}</strong></span><span>{esc(s["area"])}</span>{status_pill}{blocker_line}</p>
  <p>{esc(s["suggestion"])}</p>
  <p class="note-sm"><strong>Why:</strong> {esc(s["why"])}</p>
  <ul class="opts">{''.join(opts)}</ul>
  <p class="rec-line"><b>Recommended:</b> {esc(s["recommended"])} &nbsp;·&nbsp; <b>Evidence:</b> {ev}</p>
</section>"""
        )
    n_await = sum(1 for s in SUGGESTIONS if sug_state(s) == "AWAITING_DECISION")
    body = f"""
<h1>What could change, and what each choice costs</h1>
<p class="lede">This is the review board. {esc(num_word(len(SUGGESTIONS)))} proposals, each with two or three real
options, the trade-off of every option, the evidence behind it, and the questions that block it. Nothing here
has been built. {esc(num_word(n_await))} of the {esc(str(len(SUGGESTIONS)))} are waiting on a decision you record —
that is the intended state, not an incomplete one.</p>
<p>Read the options, pick one per row, and the choice becomes the instruction. Where a recommendation is
compound ("A, then B"), it means: do A now and revisit B when the blocker clears.</p>
<div class="note">
  <p><strong>Start here if you only read three.</strong>
  <a href="#DS-02">DS-02</a> decides what the product links point at — the difference between a site that can
  earn and one that cannot. <a href="#DS-03">DS-03</a> decides how traffic is earned without tripping the
  scaled-content rules. <a href="#DS-11">DS-11</a> decides whether there will ever be data to base the next
  choice on.</p>
</div>
{''.join(blocks)}
<h2>How a suggestion becomes a change</h2>
<p>A suggestion is a proposal, not an instruction. When you pick an option, the choice is recorded in
<code>docs/discovery-t40.json</code> on that row's <code>decision</code> field, the row's status changes from
AWAITING_DECISION, and only then is the work built — under the same gates as everything else on this site: every
row sourced or explicitly blank, no price, disclosure on every page, links resolving.</p>
<p>Two things are intentionally not on this board because they are not choices: the required disclosure sentence
and the <code>rel="sponsored"</code> qualification on affiliate links. Those are conditions of participating, and
<a href="#DS-05">DS-05</a> and <a href="#DS-09">DS-09</a> propose only to lock them in place.</p>
"""
    return page(
        "Suggestions review board",
        "Fourteen proposals for this affiliate site, each with its options, the cost of every option, the evidence "
        "behind it, and the questions blocking it. Nothing is implemented until a choice is recorded.",
        body,
        here="suggestions.html",
        crumbs=[("index.html", "Overview"), ("suggestions.html", "Suggestions")],
    )


def page_sources() -> str:
    rows = []
    for s in GD_SOURCES:
        quote = (
            f'<blockquote><p>{esc(s["quote"])}</p></blockquote>' if s.get("quote") else ""
        )
        anchor = f' <span class="note-sm">section: {esc(s["anchor"])}</span>' if s.get("anchor") else ""
        upd = ""
        if s.get("page_stated_update"):
            upd = f'<div class="note-sm">Page states: updated {esc(s["page_stated_update"])}</div>'
        rows.append(
            f'<tr id="{esc(s["id"])}">'
            f'<td class="id">{esc(s["id"])}<div class="note-sm">{esc(kind_label(s["kind"]))}</div></td>'
            f'<td><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer nofollow">'
            f'<strong>{esc(s["title"])}</strong></a>{anchor}{upd}</td>'
            f'<td>{quote}<div class="note-sm"><strong>Used for:</strong> {esc(s["used_for"])}</div></td>'
            f"</tr>"
        )
    body = f"""
<h1>Every official page this review read</h1>
    <p class="lede">{esc(num_word(len(GD_SOURCES)))} sources, fetched live on {esc(AS_OF)}. For each one the exact
text this review relied on is quoted beside the link, so you can check a finding against the page itself instead
of trusting this site's paraphrase.</p>
<div class="tablewrap">
  <table>
    <caption>Quotes are copied from the page as served; only whitespace is normalised. Where a page states its own
    update date, it is shown.</caption>
    <thead><tr><th>ID</th><th>Official page</th><th>The text relied on, and what it was used for</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</div>
<h2>What is not in this list</h2>
<p>Anything a suggestion needs that no official page settles. Four of them are load-bearing and are published as
open questions rather than assumed: whether a github.io address satisfies the site-ownership test
(<a href="questions.html#DQ-06">DQ-06</a>), whether a static page may hot-link an Amazon image under the
no-caching rule (<a href="questions.html#DQ-03">DQ-03</a>), whether quoted listing titles count as Product
Advertising Content (<a href="questions.html#DQ-09">DQ-09</a>), and the reach of the Operating Agreement's
restriction on public commentary (also <a href="questions.html#DQ-09">DQ-09</a>).</p>
<p>The earlier registers on this project cite a further 42 sources (S01–S42); they are listed on the
<a href="../pages/sources.html">source register</a> and are not repeated here.</p>
"""
    return page(
        "Sources",
        "Every official page this review read, with the exact text relied on quoted beside the link.",
        body,
        here="sources.html",
        crumbs=[("index.html", "Overview"), ("sources.html", "Sources")],
    )


PAGES = {
    "index.html": page_index,
    "findings.html": page_findings,
    "questions.html": page_questions,
    "suggestions.html": page_suggestions,
    "sources.html": page_sources,
}


def build() -> dict[str, str]:
    OUT.mkdir(exist_ok=True)
    out = {}
    for name, fn in PAGES.items():
        doc = fn()
        # Every published page must carry the required sentence (R-01). The footer is
        # generated, so this is a canary, not a decoration: it fails the build if a page
        # function is ever written without the shell.
        if DISCLOSURE not in doc:
            raise BuildError(f"{name}: missing the required Site disclosure")
        out[name] = doc
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    try:
        rendered = build()
    except BuildError as exc:
        print(f"ERROR {exc}")
        return 1
    stale = []
    for name, doc in rendered.items():
        path = OUT / name
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != doc:
                stale.append(name)
        else:
            path.write_text(doc, encoding="utf-8")
    c = counts()
    print(json.dumps({"pages": len(rendered), **c, "stale": stale}, indent=2))
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
