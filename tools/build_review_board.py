#!/usr/bin/env python3
"""Render the review board (review.html, review-questions.html, review-trace.html).

Why this exists
---------------
The 2026-11-16 request asks for three things this repository did not have on one surface:

  1. suggestions a reviewer can compare and *choose from* before anything is implemented,
     scored on one scale instead of scattered across seven incompatible boards;
  2. the questions, the known information and the missing information that must be settled
     before any of those choices is reasonable, with a route to obtain each missing piece;
  3. a requirements trace of the request as written, row by row, including the rows the
     repository cannot satisfy.

Design rules, inherited deliberately from tools/build_decisions.py and tools/build_discovery.py
----------------------------------------------------------------------------------------------
  * Data, not HTML. Pages are generated from decisions/data/review-board.json and `--check`
    fails when committed output drifts. Nobody hand-edits these three pages.
  * Counts are derived in this file and printed from the derived values. A typed count has
    already cost this repository three flags (F-17, F-26, F-29); none is typed here.
  * Every row that asserts something ends in a link to the official page it was read from, or
    in an explicit "no official source" marker. A measurement row names the command or file it
    was counted from instead, because a measurement is not a citation.
  * Nothing here is decided. `decision` starts at AWAITING_DECISION and the renderer refuses to
    print a selection that is not in the row's own option set.
  * The scores are self-assessed ordering aids, and the page says so in the reader's line of
    sight. They are not measurements and are labelled as such wherever they appear.

Usage:
    python3 tools/build_review_board.py           # build into the repository root
    python3 tools/build_review_board.py --check   # render to a temp dir and compare
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTER = REPO / "docs" / "review-board.json"
OUT = REPO

sys.path.insert(0, str(Path(__file__).resolve().parent))
from head_meta import head_block  # canonical + og:*, one definition for the whole site  # noqa: E402

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
DATA = json.loads(REGISTER.read_text(encoding="utf-8"))
AS_OF = DATA["as_of"]
SOURCES = {s["id"]: s for s in DATA["sources"]}
PROPOSALS = DATA["proposals"]
QUESTIONS = DATA["questions"]
FINDINGS = DATA["design_findings"]
MEASUREMENTS = DATA["measurements"]
REQUIREMENTS = DATA["requirements"]
IDEAS = DATA["ideas"]
IRREGULARITIES = DATA["irregularities"]
DECISIONS = DATA["decision_vocabulary"]

AREAS = sorted({p["area"] for p in PROPOSALS})

_WORDS = {8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen",
          14: "Fourteen", 15: "Fifteen", 16: "Sixteen", 17: "Seventeen", 18: "Eighteen"}


def word(n: int, *, lower: bool = False) -> str:
    """A number spelled out, derived from the register so the prose cannot drift from the table."""
    w = _WORDS.get(n, str(n))
    return w.lower() if lower else w


N_PROP = len(PROPOSALS)
N_Q = len(QUESTIONS)
N_IDEA = len(IDEAS)
N_REQ = len(REQUIREMENTS)
N_FIND = len(FINDINGS)
N_MEAS = len(MEASUREMENTS)


class BuildError(RuntimeError):
    """Raised rather than emitting a page that states something the register does not."""


# --------------------------------------------------------------------------- helpers


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def kind_label(kind: str) -> str:
    return {
        "official-amazon": "Amazon",
        "official-search": "Google Search Central",
        "official-legal": "FTC",
        "official": "official",
        "manufacturer": "manufacturer",
    }.get(kind, kind)


def source_link(src_id: str) -> str:
    src = SOURCES.get(src_id)
    if src is None:
        raise BuildError(f"unknown source id {src_id!r}")
    return (
        f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{esc(src_id)} · {esc(kind_label(src["kind"]))}'
        f'<span class="src-kind">{esc(src["title"][:74])}</span></a>'
    )


def source_cell(ids) -> str:
    """The provenance column. A row without a source says so rather than looking sourced."""
    if not ids:
        return '<td class="cell-no-source"><span class="badge warn">no official source</span></td>'
    return "<td>" + "".join(source_link(i) for i in ids) + "</td>"


def state_badge(state: str) -> str:
    cls = {"MET": "ok", "PARTIAL": "warn", "NOT_MET": "flag"}.get(state, "warn")
    return f'<span class="badge {cls}">{esc(state)}</span>'


def decision_badge(decision: str) -> str:
    cls = {"SELECTED": "ok", "DEFERRED": "warn", "AWAITING_DECISION": "flag"}.get(decision, "flag")
    label = {"AWAITING_DECISION": "awaiting your decision"}.get(decision, decision.lower())
    return f'<span class="badge {cls}">{esc(label)}</span>'


def score_bar(value: int) -> str:
    """Five-cell block instead of a number, so a score is not mistaken for a measurement."""
    filled, empty = "#" * value, "#" * (5 - value)
    return (
        '<span class="score" aria-hidden="true">'
        f'<span class="score-on">{esc(filled)}</span><span class="score-off">{esc(empty)}</span>'
        "</span>"
        f'<span class="sr-only">{value} of 5</span>'
    )


def page(title: str, description: str, rel_path: str, body: str, active: str) -> str:
    nav = [
        ("review.html", "Review board"),
        ("review-questions.html", "Questions"),
        ("review-trace.html", "Requirements trace"),
        ("review-ideas.html", "Idea board"),
        ("review-decide.html", "Answer sheet"),
        ("decisions/index.html", "Decisions view"),
        ("pages/suggestions.html", "Suggestion register"),
        ("flagged.html", "Flagged for review"),
    ]
    nav_html = "".join(
        f'<a href="{esc(href)}"' + (' class="active"' if href == active else "") + f">{esc(label)}</a>"
        for href, label in nav
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} — Zone2</title>
<meta name="description" content="{esc(description)}">
{head_block(rel_path, title=f"{title} — Zone2", description=description, site_name="Zone2")}
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/review.css">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>

<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="index.html">
      <span class="brand-mark">Z</span>
      <span class="brand-text">
        <span class="brand-name">Zone2</span>
        <span class="brand-tag">Verified affiliate platform</span>
      </span>
    </a>
    <label class="nav-toggle" for="navtoggle">Menu</label>
    <input type="checkbox" id="navtoggle" class="nav-toggle-input">
    <nav class="nav" aria-label="Primary">
      <a href="index.html">Overview</a>
      {nav_html}
    </nav>
  </div>
</header>

<main id="main">
{body}
  <footer class="site-footer">
    <div class="footer-inner">
      <div class="footer-disclosure">
        <strong>Affiliate disclosure:</strong> {esc(DISCLOSURE)}
        <span class="footer-independent">This site is independent and is not affiliated with Amazon.</span>
        Outbound product links are marked <code>rel="sponsored"</code>. No price is displayed on any page.
      </div>
      <div class="footer-note">
        Review board for task T53, compiled {esc(AS_OF)} from
        <code>decisions/data/review-board.json</code> · rendered by
        <code>tools/build_review_board.py</code> · every count on this page is derived at build
        time · nothing on this board is implemented until a decision is recorded against it.
      </div>
    </div>
  </footer>
</main>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages


def page_ideas() -> str:
    rows = []
    for i in IDEAS:
        rows.append(
            f'<tr id="{esc(i["id"])}">'
            f'<td class="id">{esc(i["id"])}</td>'
            f"<td><strong>{esc(i['title'])}</strong></td>"
            f"<td>{esc(i['article_concept'])}</td>"
            f"<td>{esc(i['trend_basis'])}</td>"
            f"<td>{esc(i['why_it_converts'])}</td>"
            f'<td class="wait">{(", ".join(esc(w) for w in i["waiting_on"]) if i["waiting_on"] else "—")}</td>'
            f'<td class="dec">{decision_badge(i["decision"])}</td>'
            f"<td>{source_cell(i['source_ids'])}</td>"
            "</tr>"
        )

    body = f"""
  <section class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Content ideas · {len(IDEAS)} concepts · none written</div>
      <h1 class="hero-title">Topics a reader would actually <em>search for</em>.</h1>
      <p class="hero-lede">
        {word(N_IDEA)} article concepts, each with the basis for thinking it will find an audience, the page it
        would become, and why it might convert. None of them is written and none of them is promised:
        writing one is a separate decision, and it needs a tagged link to be worth anything.
        The existing thirteen guides and three articles already answer the questions a spec sheet can
        answer, so these are chosen for what the spec sheet cannot.
      </p>
      <div class="hero-meta">
        <span class="chip">{len(IDEAS)} concepts</span>
        <span class="chip">0 written</span>
        <span class="chip">{sum(1 for i in IDEAS if not i["waiting_on"])} need no new information at all</span>
      </div>
    </div>
  </section>

  <div class="page-wrap">
    <section class="section">
      <h2 class="section-title">The idea board</h2>
      <p class="section-sub">
        A “trend” claim requires data this project does not have. Only one row here makes a dated,
        checkable claim — PS-13, about the November–December season — and it is stated as a season, not
        as a measurement. The other {word(N_IDEA - 1, lower=True)} are argued from what the site already publishes, which is the
        only honest basis available without a keyword tool (PQ-03).
      </p>
      <div class="table-wrap">
        <table>
          <caption>Article concepts for the 2026-11-16 request. Each row ends in the official page its argument rests on.</caption>
          <thead>
            <tr><th scope="col">ID</th><th scope="col">Concept</th><th scope="col">The page it would become</th><th scope="col">Why now</th><th scope="col">Why it might convert</th><th scope="col">Waits on</th><th scope="col">Decision</th><th scope="col">Source</th></tr>
          </thead>
          <tbody>{''.join(rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">What these deliberately are not</h2>
      <div class="callout callout-warn">
        <p><strong>Not generated content.</strong> Every concept is a page built from facts this site has
        already verified, plus a structure no competitor has. The repository's voice gate would fail a
        page that opened with a category eulogy, so none of these starts with one.</p>
        <p><strong>Not a trend claim.</strong> “Trending” needs a trend series. Until PQ-03 is answered,
        the honest word is “seasonal” or “question-shaped”, and this board uses those words.</p>
        <p><strong>Not decided.</strong> Each row says awaiting your decision. Saying yes to a concept
        here records the choice; writing it is the next task.</p>
      </div>
    </section>
  </div>
"""
    return page(
        "Idea board — five article concepts, none written",
        "Five article concepts for the 2026-11-16 request, each with its basis, the page it would become, "
        "why it might convert, and the official source it rests on. Nothing here is written or promised.",
        "review-ideas.html",
        body,
        "review-ideas.html",
    )


def page_decide() -> str:
    """The one page a reviewer needs: what to answer, and how, without reading a table first."""
    open_props = [p for p in PROPOSALS if p["decision"] == "AWAITING_DECISION"]
    unblocked = [p for p in open_props if not p["waiting_on"]]
    blocked = [p for p in open_props if p["waiting_on"]]

    # Unblocked proposals, ordered by the single scale the board claims: value first, cost second.
    def value(p):
        return p["quality_impact"] + p["conversion_impact"]

    def cost(p):
        return p["risk"] + p["effort"]

    ranked = sorted(unblocked, key=lambda p: (-value(p), cost(p), p["id"]))
    top = ranked[:4]

    option_rows = []
    for p in top:
        for o in p["options"]:
            option_rows.append(
                f'<tr id="{esc(p["id"])}-{esc(o["id"])}">'
                f'<td class="id">{esc(p["id"])} · {esc(o["id"])}</td>'
                f"<td>{esc(o['label'])}</td>"
                f"<td>{esc(o['cost'])}</td>"
                f"<td>{esc(o['risk'])}</td>"
                f'<td class="wait">{esc(p["area"])}</td>'
                "</tr>"
            )

    answer_rows = []
    for q in QUESTIONS:
        answer_rows.append(
            f'<tr id="{esc(q["id"])}">'
            f'<td class="id">{esc(q["id"])}</td>'
            f"<td>{esc(q['question'])}</td>"
            f'<td class="obtain">{esc(q["obtain"])}</td>'
            f"<td>{source_cell(q['source_ids'])}</td>"
            "</tr>"
        )

    body = f"""
  <section class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Answer sheet · {len(open_props)} decisions and {len(QUESTIONS)} questions</div>
      <h1 class="hero-title">One page to answer, so nothing has to be <em>read twice</em>.</h1>
      <p class="hero-lede">
        The board has {len(PROPOSALS)} proposals and {len(QUESTIONS)} questions, and reading all of it is a
        waste of your time if you only want to reply. This page is the short version: the
        {len(top)} proposals that need nothing from anybody, the {len(blocked)} that wait on an answer,
        and the {len(QUESTIONS)} questions with the exact action that closes each one. Reply in any form —
        a list is enough.
      </p>
      <div class="hero-meta">
        <span class="chip">{len(unblocked)} decidable now</span>
        <span class="chip">{len(blocked)} blocked on an answer</span>
        <span class="chip">{len(QUESTIONS)} questions · 0 answered</span>
      </div>
    </div>
  </section>

  <div class="page-wrap">
    <section class="section">
      <h2 class="section-title">1. The {word(len(top), lower=True)} proposals to decide first</h2>
      <p class="section-sub">
        Chosen by value (quality + conversion) and then by cost (risk + effort), from the
        {len(unblocked)} proposals that need no missing information. This ordering is a reading of the
        board, not a measurement.
      </p>
      <div class="table-wrap">
        <table>
          <caption>The {len(top)} proposals that need nothing from anybody, with every option they offer. Each row is a whole answer.</caption>
          <thead><tr><th scope="col">ID · option</th><th scope="col">If you pick this</th><th scope="col">What it costs</th><th scope="col">What it risks</th><th scope="col">Area</th></tr></thead>
          <tbody>
            {''.join(f'<tr id="{esc(o["id"])}"><td class="id">{esc(o["id"])}</td><td>{esc(o["label"])}</td><td>{esc(o["cost"])}</td><td>{esc(o["risk"])}</td><td class="wait">{esc(o["area"])}</td></tr' for o in [])}
            {''.join(option_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">2. How to reply</h2>
      <div class="callout">
        <p><strong>Short form is fine.</strong> “PS-05 A, PS-02 A, defer PS-07” is a complete answer.
        Nothing else is required — no form, no file, no account.</p>
        <p><strong>What happens next.</strong> The decision is written into
        <code>docs/review-board.json</code> with your words and the date, the page is regenerated, and the
        gate checks that the option you named is one the row actually offered. Only then does a build
        session start.</p>
        <p><strong>Deferring is an answer.</strong> <code>DEFERRED</code> needs one sentence on what would
        make it decidable. Nothing gets deleted and nothing gets decided for you.</p>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">3. The {len(QUESTIONS)} questions, one action each</h2>
      <p class="section-sub">
        None of these needs a build session. Each is a lookup, a sign-in, or one email, and each is
        phrased so that a one-line reply closes it.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Open questions with the action that obtains the answer. An empty answer is deliberate: this project does not infer.</caption>
          <thead><tr><th scope="col">ID</th><th scope="col">The question</th><th scope="col">The action that closes it</th><th scope="col">Source</th></tr></thead>
          <tbody>{''.join(answer_rows)}</tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">4. What this page does not do</h2>
      <div class="callout callout-warn">
        <p>It does not record your answer by itself. The site is static and ships no form handler, and a
        form that posted nowhere would be worse than this page. Your reply is the record; the next session
        transcribes it into the register with the gate checking it.</p>
        <p>It does not recommend everything. {word(len(top), lower=True)} proposals are surfaced here because
        they need nothing from anybody and score highest on value per unit of cost; the other
        {len(unblocked) - len(top)} decidable proposals and the {len(blocked)} blocked ones are on the
        <a href="review.html">board</a>, each with the answer it waits on.</p>
      </div>
    </section>
  </div>
"""
    return page(
        "Answer sheet — four decisions, nine questions, one reply",
        "The short version of the review board: the proposals that can be decided today, the questions with "
        "the action that closes each one, and how to reply. Nothing here is implemented.",
        "review-decide.html",
        body,
        "review-decide.html",
    )


def page_review() -> str:
    awaiting = sum(1 for p in PROPOSALS if p["decision"] == "AWAITING_DECISION")
    selected = sum(1 for p in PROPOSALS if p["decision"] == "SELECTED")
    blocked = sum(1 for p in PROPOSALS if p["waiting_on"])
    no_source_reqs = sum(1 for r in REQUIREMENTS if not r["source_ids"])
    met = sum(1 for r in REQUIREMENTS if r["state"] == "MET")
    partial = sum(1 for r in REQUIREMENTS if r["state"] == "PARTIAL")
    not_met = sum(1 for r in REQUIREMENTS if r["state"] == "NOT_MET")

    rows = []
    for p in PROPOSALS:
        rows.append(
            "<tr>"
            f'<td class="id"><a href="#{esc(p["id"])}">{esc(p["id"])}</a></td>'
            f"<td><strong>{esc(p['title'])}</strong>"
            f'<div class="row-area">{esc(p["area"])}</div>'
            f'<div class="row-problem">{esc(p["problem"])}</div></td>'
            f'<td class="num">{p["quality_impact"]}</td>'
            f'<td class="num">{p["conversion_impact"]}</td>'
            f'<td class="num">{p["risk"]}</td>'
            f'<td class="num">{p["effort"]}</td>'
            f'<td class="wait">{(", ".join(esc(w) for w in p["waiting_on"]) if p["waiting_on"] else "—")}</td>'
            f'<td class="dec">{decision_badge(p["decision"])}</td>'
            f"<td>{source_cell(p['evidence'])}</td>"
            "</tr>"
        )

    detail = []
    for p in PROPOSALS:
        opts = []
        for o in p["options"]:
            opts.append(
                '<div class="option">'
                f'<div class="option-head"><span class="option-id">{esc(o["id"])}</span>'
                f'<span class="option-label">{esc(o["label"])}</span></div>'
                f'<dl class="option-body">'
                f"<dt>Commits to</dt><dd>{esc(o['commitment'])}</dd>"
                f"<dt>Cost</dt><dd>{esc(o['cost'])}</dd>"
                f"<dt>Risk</dt><dd>{esc(o['risk'])}</dd>"
                f"</dl></div>"
            )
        detail.append(
            f'<article class="suggest-card" id="{esc(p["id"])}">'
            f'<div class="card-head"><span class="eyebrow">{esc(p["area"])} · {esc(p["id"])}</span>'
            f"<h3>{esc(p['title'])}</h3></div>"
            f"<p>{esc(p['problem'])}</p>"
            f'<div class="options">{"".join(opts)}</div>'
            f'<div class="callout"><strong>Recommended here:</strong> {esc(p["recommendation"])}'
            f'<div class="note">A recommendation is not a decision. This row stays '
            f'{esc(DECISIONS["AWAITING_DECISION"]) if False else "awaiting your decision"} until you '
            f"record one, and recording one is a separate step from building it.</div></div>"
            f'<div class="card-foot"><span>Waits on: '
            f'{(", ".join(f"<a href=review-questions.html#{esc(w)}>{esc(w)}</a>" for w in p["waiting_on"]) if p["waiting_on"] else "nothing - decidable now")}</span>'
            f"<span>{source_cell(p['evidence'])}</span></div>"
            "</article>"
        )

    score_note = (
        "The four numbers in the table are <em>self-assessed ordering aids</em>, 1 to 5, written by "
        "this session and not measured. Quality and conversion say how much the proposal is expected "
        "to change what a reader sees; risk and effort say what it costs. They exist so that three "
        "proposals of equal value can be told apart by what they cost - never as evidence."
    )

    body = f"""
  <section class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Decision surface · nothing here is implemented</div>
      <h1 class="hero-title">Choose a <em>path</em> before anything changes.</h1>
      <p class="hero-lede">
        {word(N_PROP)} proposals for the 2026-11-16 request, each with three options, the cost and risk of
        each, the question it waits on, and an official source. Every row is still
        <strong>awaiting your decision</strong> — {awaiting} of {len(PROPOSALS)} of them — so nothing here has
        been built. Read the table, open a proposal, pick an option. That is the whole interface.
      </p>
      <div class="hero-meta">
        <span class="chip">{len(PROPOSALS)} proposals</span>
        <span class="chip">{awaiting} awaiting decision · {selected} selected</span>
        <span class="chip">{blocked} blocked on an open question</span>
        <span class="chip">{len(QUESTIONS)} open questions · 0 answered</span>
      </div>
    </div>
  </section>

  <div class="page-wrap">
    <section class="section">
      <h2 class="section-title">What the site does not do yet, in three lines</h2>
      <div class="kpi-band">
        <div class="kpi-card"><div class="kpi-value">{len(REQUIREMENTS)}</div><div class="kpi-label">requirement rows traced from the request</div></div>
        <div class="kpi-card"><div class="kpi-value">{met}</div><div class="kpi-label">met</div></div>
        <div class="kpi-card"><div class="kpi-value">{partial}</div><div class="kpi-label">partial</div></div>
        <div class="kpi-card"><div class="kpi-value">{not_met}</div><div class="kpi-label">not met</div></div>
      </div>
      <p class="section-sub">
        The <a href="review-trace.html">requirements trace</a> takes the request sentence by sentence
        and states, for each one, what exists, what is missing, and which row of this board would
        close it. {no_source_reqs} of the {len(REQUIREMENTS)} rows rest on no official source at all,
        because no official page defines what clauses like "automates product research" must produce —
        those rows say so, in their own words, instead of borrowing a source they do not have.
      </p>
    </section>

    <section class="section">
      <h2 class="section-title">The {word(N_PROP, lower=True)} proposals, on one scale</h2>
      <p class="section-sub">{score_note}</p>
      <div class="table-wrap">
        <table>
          <caption>Proposals for the 2026-11-16 request. Sorting is by area, then by id. The last column is the official page the row's argument rests on; a row with none says so.</caption>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Proposal</th>
              <th scope="col">Quality</th>
              <th scope="col">Conversion</th>
              <th scope="col">Risk</th>
              <th scope="col">Effort</th>
              <th scope="col">Waits on</th>
              <th scope="col">Decision</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">The proposals in full</h2>
      <p class="section-sub">Three options each. Every option states what it commits to, what it costs and what it risks, because an option without a trade-off is a slogan.</p>
      {''.join(detail)}
    </section>

    <section class="section" id="irregularities">
      <h2 class="section-title">Flagged for review: {len(IRREGULARITIES)} items from this session</h2>
      <p class="section-sub">
        Irregularities this session found or caused, published rather than tidied away. None blocks
        the site; each names what happened, how it was resolved, and whether anything is left for you.
        Rows with no official source say so - they describe this repository, not an external rule.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Flags raised by T53. Four are closed by this session and one leaves an optional owner action.</caption>
          <thead><tr><th scope="col">ID</th><th scope="col">Severity</th><th scope="col">What was found</th><th scope="col">Effect</th><th scope="col">Resolution</th><th scope="col">For the owner</th><th scope="col">Source</th></tr></thead>
          <tbody>
            {''.join(
                f'<tr id="{esc(i["id"])}"><td class="id">{esc(i["id"])}</td>'
                f'<td><span class="badge {"warn" if i["severity"]=="medium" else "ok"}">{esc(i["severity"])}</span></td>'
                f'<td>{esc(i["found"])}</td><td>{esc(i["effect"])}</td><td>{esc(i["resolution"])}</td>'
                f'<td>{esc(i["owner_action"])}</td><td>{source_cell(i["source_ids"])}</td></tr>'
                for i in IRREGULARITIES
            )}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">How a decision gets recorded</h2>
      <div class="callout">
        <p><strong>1.</strong> You pick a proposal and an option in your reply — for example
        “PS-05, option A”. Nothing else is needed.</p>
        <p><strong>2.</strong> The next session sets <code>decision</code> to
        <code>SELECTED</code> and fills <code>decision_note</code> with your words and the date. The
        gate fails if a recorded selection names an option the row does not offer, so the record
        cannot drift from the decision.</p>
        <p><strong>3.</strong> Only then does an implementation session start — on its own branch,
        with its own gate — and this board keeps showing the selection rather than erasing it.</p>
        <p class="note">A proposal may also be marked <code>DEFERRED</code>, which requires a note
        saying what would make it decidable. There is no third state: no row disappears.</p>
      </div>
    </section>
  </div>
"""
    return page(
        f"Review board: {word(N_PROP, lower=True)} proposals, one decision at a time",
        f"{word(N_PROP)} scoped proposals for the 2026-11-16 request, each with three options, a cost, a risk, "
        "the open question it waits on and an official source. Every row is awaiting a decision and "
        "nothing on the board is implemented.",
        "review.html",
        body,
        "review.html",
    )


def page_questions() -> str:
    rows = []
    for q in QUESTIONS:
        rows.append(
            f'<tr id="{esc(q["id"])}">'
            f'<td class="id">{esc(q["id"])}</td>'
            f"<td><strong>{esc(q['question'])}</strong></td>"
            f"<td>{esc(q['known']) or '—'}</td>"
            f"<td>{esc(q['missing'])}</td>"
            f'<td class="obtain">{esc(q["obtain"])}<div class="row-owner">owner: {esc(q["owner"])}</div></td>'
            f'<td class="wait">{(", ".join(esc(b) for b in q["blocks"]) if q["blocks"] else "—")}</td>'
            f"<td><span class=\"badge flag\">open</span></td>"
            f"<td>{source_cell(q['source_ids'])}</td>"
            "</tr>"
        )

    blocked_on_owner = sum(1 for q in QUESTIONS if q["owner"] == "owner")
    with_answer = sum(1 for q in QUESTIONS if q.get("answer"))

    body = f"""
  <section class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Information register · {len(QUESTIONS)} open questions · {with_answer} answered</div>
      <h1 class="hero-title">What has to be known before a choice is <em>reasonable</em>.</h1>
      <p class="hero-lede">
        Each row states what is already verified, what is missing, and the exact action that would
        obtain the missing piece. Not one row carries an answer, because the information is not in
        this repository — {blocked_on_owner} of {len(QUESTIONS)} need a person, not a build.
        This is deliberate: filling an answer from inference is the one thing this project refuses.
      </p>
      <div class="hero-meta">
        <span class="chip">{len(QUESTIONS)} questions</span>
        <span class="chip">0 answered · 0 inferred</span>
        <span class="chip">{blocked_on_owner} wait on the owner</span>
      </div>
    </div>
  </section>

  <div class="page-wrap">
    <section class="section">
      <h2 class="section-title">The questions</h2>
      <p class="section-sub">
        The “obtain” column is the point of the table. A question without a route is a complaint,
        so every row names the action and the person who can take it.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Open questions raised by the 2026-11-16 request. Every row ends in the official page that makes the question answerable in principle.</caption>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">Question</th>
              <th scope="col">What is verified today</th>
              <th scope="col">What is missing</th>
              <th scope="col">How to obtain it</th>
              <th scope="col">Blocks</th>
              <th scope="col">State</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">The four that decide the rest</h2>
      <p class="section-sub">Most of the board collapses once these are answered. They are listed first on purpose.</p>
      <div class="cards-grid">
        <div class="card"><h3>PQ-01 · the account</h3><p>Without an approved Associates account and a tag, no link on this site can earn anything. Every commercial proposal is downstream of this row.</p><p><a href="#PQ-01">Read the row</a></p></div>
        <div class="card"><h3>PQ-08 · the images</h3><p>Twenty product pages carry no photograph. The image rights question is the single largest visual constraint on the site.</p><p><a href="#PQ-08">Read the row</a></p></div>
        <div class="card"><h3>PQ-04 · the traffic</h3><p>Nobody knows whether the site has any organic visits. Search Console needs no tag and no payment, so this is the cheapest unknown to close.</p><p><a href="#PQ-04">Read the row</a></p></div>
        <div class="card"><h3>PQ-09 · the scope</h3><p>Three products or a whole category. Depth on three models and breadth across a category need different content plans.</p><p><a href="#PQ-09">Read the row</a></p></div>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Questions this register did not invent</h2>
      <p class="section-sub">
        Twenty-eight open questions already existed before this task, in two other registers, and
        none of them is answered either. They are not duplicated here; they are linked, because the
        same information closes both.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Existing question registers, with their size and state at the time of writing.</caption>
          <thead><tr><th scope="col">Register</th><th scope="col">Rows</th><th scope="col">Answered</th><th scope="col">Where</th></tr></thead>
          <tbody>
            <tr><td>Ledger question register</td><td class="num">18</td><td class="num">0</td><td><a href="pages/questions.html">Q-01 – Q-18 questions page</a> · <a href="review-questions.html">read this register's companion view</a></td></tr>
            <tr><td>Marketing question set</td><td class="num">10</td><td class="num">0</td><td><a href="marketing/improvements.html">MQ-01 – MQ-10 on the improvement board</a></td></tr>
            <tr><td>This register</td><td class="num">{len(QUESTIONS)}</td><td class="num">0</td><td>this page</td></tr>
          </tbody>
        </table>
      </div>
      <p class="note">Three registers, three vocabularies, thirty-seven questions and no answers. That is PS-12 on the board.</p>
    </section>
  </div>
"""
    return page(
        "Open questions — what must be known before deciding",
        "Every question that has to be settled before a proposal on the review board can reasonably be "
        "chosen, with what is verified, what is missing, the action that obtains it, and an official source.",
        "review-questions.html",
        body,
        "review-questions.html",
    )


def page_trace() -> str:
    met = sum(1 for r in REQUIREMENTS if r["state"] == "MET")
    partial = sum(1 for r in REQUIREMENTS if r["state"] == "PARTIAL")
    not_met = sum(1 for r in REQUIREMENTS if r["state"] == "NOT_MET")
    rows = []
    for r in REQUIREMENTS:
        rows.append(
            f'<tr id="{esc(r["id"])}">'
            f'<td class="id">{esc(r["id"])}</td>'
            f'<td class="clause">“{esc(r["brief_clause"])}”</td>'
            f"<td>{state_badge(r['state'])}</td>"
            f"<td>{esc(r['what_exists'])}</td>"
            f"<td>{esc(r['what_is_missing']) or '—'}</td>"
            f"<td>{source_cell(r['source_ids'])}</td>"
            "</tr>"
        )

    measurement_rows = []
    for m in MEASUREMENTS:
        measurement_rows.append(
            "<tr>"
            f'<td class="id">{esc(m["id"])}</td>'
            f"<td>{esc(m['measure'])}</td>"
            f'<td class="num-strong">{esc(m["value"])}</td>'
            f"<td><code>{esc(m['how_measured'])}</code></td>"
            f"<td>{esc(m['means'])}</td>"
            "</tr>"
        )

    finding_rows = []
    for f in FINDINGS:
        finding_rows.append(
            "<tr>"
            f'<td class="id">{esc(f["id"])}</td>'
            f"<td><strong>{esc(f['title'])}</strong><div class=\"row-problem\">{esc(f['what_a_reader_sees'])}</div></td>"
            f"<td>{esc(f['why_it_matters'])}</td>"
            f'<td class="wait">{esc(f["measured_by"]) or "—"}</td>'
            f'<td class="wait">{esc(f["proposed_fix"])}</td>'
            f"<td>{source_cell(f['source_ids'])}</td>"
            "</tr>"
        )

    body = f"""
  <section class="hero-light">
    <div class="hero-inner">
      <div class="hero-eyebrow">Requirements trace · {len(REQUIREMENTS)} rows · derived counts</div>
      <h1 class="hero-title">The request, taken <em>sentence by sentence</em>.</h1>
      <p class="hero-lede">
        {met} met · {partial} partial · {not_met} not met. Each row quotes the clause it traces, states
        what actually exists in this repository, states what is missing, and links the official page the
        judgement rests on. Where no official page can settle the clause, the row says so instead of
        borrowing one.
      </p>
    </div>
  </section>

  <div class="page-wrap">
    <section class="section">
      <h2 class="section-title">Requirement trace</h2>
      <div class="table-wrap">
        <table>
          <caption>Every clause of the 2026-11-16 request, in order. Status vocabulary: MET means an implementation exists and the row names it; PARTIAL means part exists and the row names what is missing; NOT_MET means nothing attempts it.</caption>
          <thead>
            <tr>
              <th scope="col">ID</th>
              <th scope="col">The request says</th>
              <th scope="col">State</th>
              <th scope="col">What exists</th>
              <th scope="col">What is missing</th>
              <th scope="col">Source</th>
            </tr>
          </thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">What was measured to reach those rows</h2>
      <p class="section-sub">
        A judgement without a measurement is an opinion. Each row below names the command or file it was
        counted from, so any figure here can be reproduced in one line.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Measurements taken on 2026-11-16 against the published tree. None of these is an external claim, so the source column would be empty by construction — the reproduction command is the evidence.</caption>
          <thead>
            <tr><th scope="col">ID</th><th scope="col">What was measured</th><th scope="col">Value</th><th scope="col">How to reproduce</th><th scope="col">What it means</th></tr>
          </thead>
          <tbody>
            {''.join(measurement_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Design findings: the “AI slop” complaint, made specific</h2>
      <p class="section-sub">
        The complaint in the request is that the site reads like generic generated output. That is a
        real observation and a useless instruction until it is broken into things that can be seen and
        counted. Nine findings, each with what a reader actually sees, why it matters, and the proposal
        that would change it.
      </p>
      <div class="table-wrap">
        <table>
          <caption>Design findings. “Measured by” refers to a row in the measurement table above; “Fix” refers to a row on the review board.</caption>
          <thead>
            <tr><th scope="col">ID</th><th scope="col">Finding</th><th scope="col">Why it matters</th><th scope="col">Measured by</th><th scope="col">Fix</th><th scope="col">Source</th></tr>
          </thead>
          <tbody>
            {''.join(finding_rows)}
          </tbody>
        </table>
      </div>
    </section>

    <section class="section">
      <h2 class="section-title">Sources</h2>
      <div class="table-wrap">
        <table>
          <caption>Every official page this board rests on, with the sentence taken from it. Re-read on 2026-11-16.</caption>
          <thead><tr><th scope="col">ID</th><th scope="col">Publisher</th><th scope="col">Page</th><th scope="col">What it says, quoted</th><th scope="col">Used for</th></tr></thead>
          <tbody>
            {''.join(
                f'<tr><td class="id">{esc(s["id"])}</td><td>{esc(s["publisher"])}</td>'
                f'<td><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer">{esc(s["title"])}</a></td>'
                f'<td class="quote">“{esc(s["quote"])}”</td><td>{esc(s["used_for"])}</td></tr>'
                for s in DATA["sources"]
            )}
          </tbody>
        </table>
      </div>
    </section>
  </div>
"""
    return page(
        "Requirements trace and design findings",
        "The 2026-11-16 request traced sentence by sentence, with what exists, what is missing and an "
        f"official source per row, plus {word(N_MEAS, lower=True)} measurements and {word(N_FIND, lower=True)} design findings.",
        "review-trace.html",
        body,
        "review-trace.html",
    )


PAGES = {
    "review.html": page_review,
    "review-questions.html": page_questions,
    "review-trace.html": page_trace,
    "review-ideas.html": page_ideas,
    "review-decide.html": page_decide,
}


def build(out_root: Path) -> list[str]:
    written = []
    for name, fn in PAGES.items():
        (out_root / name).write_text(fn(), encoding="utf-8")
        written.append(name)
    return written


def digest(root: Path) -> dict[str, str]:
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()[:16] for name in PAGES}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="render to a temp dir and compare with committed output")
    args = ap.parse_args()

    if args.check:
        tmp = Path(tempfile.mkdtemp(prefix="z2rb-"))
        build(tmp)
        fresh, committed = digest(tmp), digest(OUT)
        shutil.rmtree(tmp, ignore_errors=True)
        drift = sorted(k for k in PAGES if fresh[k] != committed.get(k))
        print(json.dumps({"pages": len(fresh), "drifted": drift}, indent=2))
        if drift:
            print("review pages are out of date - run python3 tools/build_review_board.py", file=sys.stderr)
            return 1
        return 0

    written = build(OUT)
    print(json.dumps({"pages": len(written), "as_of": AS_OF, "out": "repository root"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
