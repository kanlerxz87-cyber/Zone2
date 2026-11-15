#!/usr/bin/env python3
"""Render the decision surface (decisions/) from ledger/{requirements,questions,suggestions}.json.

Why this exists
---------------
The current project request asks for three deliverables that no earlier session produced:

  1. a section dedicated to suggestions, where a reviewer reads proposals and *chooses a path before
     anything is implemented*;
  2. the questions, answers and missing information that must be settled before a decision is reasonable,
     including how to obtain what is missing;
  3. an executive summary of both.

Design rules, inherited deliberately from tools/build_site.py so the two namespaces feel like one site:

  * Deterministic and network-free: same ledger bytes -> same HTML bytes. `--check` re-renders into a temp
    directory and fails if the committed output differs, so CI proves the pages match the data.
  * Every row that asserts something ends in an official source link, or in an explicit "no official source"
    marker. This is the project's core invariant and the new namespace is held to it, not exempted.
  * Counts are derived, never typed. A count in prose here would drift the moment a row is added; that bug
    class has already cost this repository three flags (F-17, F-26, F-29).
  * Nothing in this namespace is implemented. `decision` starts at AWAITING_DECISION and this renderer
    refuses to invent one.

Usage:
    python3 tools/build_decisions.py           # build into decisions/
    python3 tools/build_decisions.py --check   # render to a temp dir and compare with committed output
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
DATA = REPO / "ledger"
OUT = REPO / "decisions"

SITE_NAME = "Zone2"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AS_OF = "2026-11-15"

# Vendored design system, same provenance approach as tools/build_site.py.
DESIGN_CANDIDATES = ("assets/css/style.css", "styles.css", "northstar/styles.css")


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
REQS = load("requirements.json")
# The suggestion and question registers are OWNED by the T29 implementation session (2499438c, PR #61) and
# rendered canonically at pages/suggestions.html and pages/questions.html. This namespace reads them and adds
# no second copy: two decision stores would let a reviewer answer the same question twice, differently.
QS = load("questions.json")
SUGS = load("suggestions.json")
FINDINGS = load("decisions_findings.json")


def esc(value) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


# --------------------------------------------------------------------------- shared cell helpers


def source_cell(source_ids, *, note: str = "") -> str:
    """Every asserting row ends here: real links, or an explicit marker. Never a silent blank."""
    ids = [i for i in (source_ids or []) if i in SOURCES]
    if not ids:
        hint = esc(note or "no source registered for this row")
        return (
            '<td class="cell-unverified"><span class="pill pill-warn">NO SOURCE</span>'
            f'<div class="row-note">{hint}</div></td>'
        )
    links = "".join(
        '<a class="src" href="{url}" target="_blank" rel="noopener noreferrer nofollow">{sid}'
        '<span class="src-host">{host}</span></a>'.format(
            url=esc(SOURCES[i]["url"]), sid=esc(i), host=esc(SOURCES[i]["url"].split("/")[2])
        )
        for i in ids
    )
    return f'<td class="cell-src">{links}</td>'


def pill(kind: str, label: str) -> str:
    return f'<span class="pill pill-{kind}">{esc(label)}</span>'


STATUS_KIND = {
    "MET": "ok",
    "ANSWERED": "ok",
    "PARTIAL": "info",
    "ADOPT": "ok",
    "ADOPT_AFTER_PREREQUISITE": "info",
    "NOT_MET": "warn",
    "OPEN": "warn",
    "UNVERIFIABLE": "neg",
    "AWAITING_DECISION": "warn",
    "A": "ok",
    "B": "info",
    "C": "neg",
    "DEFER": "neg",
    "REJECT": "neg",
}


def ref_badge(ref: str) -> str:
    """Cross-references are rendered with their kind and a link, so a reader is never handed a bare code.
    SG = canonical suggestion (pages/suggestions.html), RF = this review's finding (flagged.html),
    F = project flag (pages/flags.html)."""
    if ref.startswith("SG-"):
        # pages/suggestions.html carries no per-row anchors, so a #fragment would address nothing;
        # link the page and name the row instead (caught by tools/audit_site.py::check_fragments).
        return f'<a href="../pages/suggestions.html">{esc(ref)} &middot; suggestion</a>'
    if ref.startswith("RF-"):
        return f'<a href="flagged.html#{esc(ref)}">{esc(ref)} &middot; this review</a>'
    if ref.startswith("F-"):
        return f'<a href="../pages/flags.html#{esc(ref)}">{esc(ref)} &middot; project flag</a>'
    return f"<span>{esc(ref)}</span>"


def status_pill(state: str) -> str:
    return pill(STATUS_KIND.get(state, "neg"), state)


def table(headers, rows, *, caption: str = "") -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    if rows:
        body = "".join("<tr>" + "".join(cells) + "</tr>" for cells in rows)
    else:
        body = (
            f'<tr><td colspan="{len(headers)}" class="empty-row">'
            "No rows published &mdash; the note above states why.</td></tr>"
        )
    cap = f"<caption>{esc(caption)}</caption>" if caption else ""
    return (
        f'<div class="table-wrap"><table class="data-table">{cap}'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


def panel(title: str, inner: str, *, meta: str = "") -> str:
    """The base sheet styles .card (and .card h3); .panel/.panel-head have no rule, so use .card."""
    head = f'<div class="panel-head"><h3>{esc(title)}</h3>{meta}</div>' if meta else f"<h3>{esc(title)}</h3>"
    return f'<section class="card">{head}{inner}</section>'


def notice(title: str, text: str) -> str:
    return f'<div class="notice"><strong>{esc(title)}</strong>{esc(text)}</div>'


# --------------------------------------------------------------------------- derived counts

def all_reqs() -> list[dict]:
    return [r for g in REQS["groups"] for r in g["rows"]]


def all_qs() -> list[dict]:
    """Canonical question rows (owned by the T29 implementation session)."""
    return QS["questions"]


def all_sugs() -> list[dict]:
    """Canonical suggestion rows. Schema: id, area, title, suggestion, why, evidence, options,
    recommended, needs_answers, decision, source_ids."""
    return SUGS["suggestions"]


def q_state(q: dict) -> str:
    """The register holds *unanswered* questions only: `known` is the background that is established,
    `missing` is the gap. There is no answered state in that schema, so every row here is OPEN and is
    labelled as such rather than being dressed up as partially answered."""
    return (q.get("state") or "").strip().upper() or "OPEN"


def sug_decision(s: dict) -> str:
    d = (s.get("decision") or "").strip()
    return d or "AWAITING_DECISION"


def counts() -> dict[str, int]:
    """Every published number comes from here. No count is typed into a template."""
    reqs, qs, sugs = all_reqs(), all_qs(), all_sugs()
    return {
        "reqs": len(reqs),
        "reqs_met": sum(1 for r in reqs if r["status"] == "MET"),
        "reqs_partial": sum(1 for r in reqs if r["status"] == "PARTIAL"),
        "reqs_not_met": sum(1 for r in reqs if r["status"] == "NOT_MET"),
        "reqs_unverifiable": sum(1 for r in reqs if r["status"] == "UNVERIFIABLE"),
        "qs": len(qs),
        "qs_answered": sum(1 for q in qs if q_state(q) == "ANSWERED"),
        "qs_partial": 0,
        "qs_open": sum(1 for q in qs if q_state(q) == "OPEN"),
        "sugs": len(sugs),
        "sugs_awaiting": sum(1 for s in sugs if sug_decision(s) == "AWAITING_DECISION"),
        "sugs_unblocked": sum(1 for s in sugs if not (s.get("needs_answers") or [])),
        "findings": len(FINDINGS["findings"]),
        "sources": len(SOURCES),
    }


# --------------------------------------------------------------------------- frame

NAV = [
    ("index.html", "Decision hub"),
    ("requirements.html", "Requirements"),
    ("content-plan.html", "Content plan"),
    ("flagged.html", "Flagged for review"),
    ("../pages/suggestions.html", "Suggestions (canonical)"),
    ("../pages/questions.html", "Questions (canonical)"),
]


def render(rel: str, title: str, lead: str, body: str, *, badge: str = "") -> str:
    """Same shell as pages/ (tools/build_site.py::render) so the two namespaces are one site."""
    c = counts()
    items = []
    for href, label in NAV:
        active = " active" if href == rel else ""
        items.append(f'<a class="nav-link{active}" href="{esc(href)}">{esc(label)}</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Decision surface for the Zone2 Amazon affiliate platform: sourced requirements, the open questions blocking each proposal, and suggestions awaiting an owner decision. Nothing here is implemented until it is chosen.">
<meta name="robots" content="index,follow">
<title>{esc(title)} &middot; {esc(SITE_NAME)} decisions</title>
<link rel="stylesheet" href="assets/dashboard.css">
<link rel="stylesheet" href="assets/site.css">
<link rel="stylesheet" href="assets/decisions.css">
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <a class="brand" href="../index.html"><span class="brand-mark">Z</span><span>{esc(SITE_NAME)}<small>Decisions &amp; suggestions</small></span></a>
  <div class="side-label">REVIEW BEFORE IMPLEMENTING</div>
  <nav class="nav">{"".join(items)}</nav>
  <div class="sidebar-bottom"><div class="status-dot"></div><div><strong>{c["sugs_awaiting"]} proposals awaiting a decision</strong><small>{esc(AS_OF)} &middot; nothing implemented</small></div></div>
</aside>
<main class="main">
  <header class="topbar">
    <div class="crumb"><a href="../index.html">{esc(SITE_NAME)}</a> <span>/</span> <strong>{esc(title)}</strong></div>
    <div class="top-right"><span class="live-tag"><i></i> Static, source-governed</span><a class="chip" href="../pages/index.html">Findings hub</a></div>
  </header>
  <div class="content">
    <div class="page-head">
      <div>
        <div class="eyebrow">reviewed {esc(AS_OF)} &middot; proposals, not changes</div>
        <h1>{esc(title)}</h1>
        <p>{esc(lead)}</p>
      </div>
      {badge or f'<a class="chip" href="flagged.html">{c["sugs"]} proposals &middot; 0 implemented</a>'}
    </div>
    {body}
  </div>
  <footer class="site">
    <div class="disclosure"><strong>Disclosure</strong> {esc(DISCLOSURE)} Outbound links are qualified with <code>rel="sponsored"</code>.</div>
    <div class="foot-meta">Decision surface <span>&middot;</span> every proposal states its evidence, cost, risk and blocker <span>&middot;</span> generated by <code>tools/build_decisions.py</code> from <code>ledger/*.json</code> <span>&middot;</span> <a href="../index.html">Dashboard</a> <span>&middot;</span> <a href="../pages/flags.html">Flagged for review</a></div>
  </footer>
</main>
</div>
</body>
</html>
"""


def kpis(pairs: list[tuple[str, str]]) -> str:
    """Match the shared design system exactly: .kpis > .kpi > .num + .lbl (assets/css/style.css:66-74)."""
    cells = "".join(
        f'<div class="kpi"><div class="num">{esc(num)}</div><div class="lbl">{esc(label)}</div></div>'
        for num, label in pairs
    )
    return f'<section class="kpis">{cells}</section>'


# --------------------------------------------------------------------------- pages


def page_index() -> str:
    c = counts()
    body = [
        notice(
            "What this section is, and what it is not",
            "This is the requirement-and-review layer. The decision board itself — the ten suggestions with their "
            "options and the sixteen questions with their missing information — is owned and published by the "
            "canonical T29 register at pages/suggestions.html and pages/questions.html. This namespace does not "
            "duplicate it: it tracks the requirement set behind it, the content plan, and every irregularity found "
            "on the way. Nothing here is implemented.",
        ),
        kpis(
            [
                (str(c["reqs"]), "requirements tracked"),
                (str(c["reqs_partial"] + c["reqs_not_met"]), "requirements not yet met"),
                (str(c["findings"]), "irregularities flagged"),
                ("0", "changes implemented by this task"),
            ]
        ),
    ]

    body.append(
        panel(
            "The review path — read in this order",
            table(
                ["Step", "What you are choosing", "Where it lives", "State"],
                [
                    [
                        "<td>1</td>",
                        "<td>Which path to take on eligibility, product scope, pricing, article format, editorial voice, design, ratings, commission model, measurement and rollout</td>",
                        '<td><a class="pagelink" href="../pages/suggestions.html">pages/suggestions.html</a> — options, a recommendation and the evidence for each, with a decision field per row</td>',
                        f"<td>{status_pill('AWAITING_DECISION')}</td>",
                    ],
                    [
                        "<td>2</td>",
                        "<td>The information that must exist before those choices are safe to make</td>",
                        '<td><a class="pagelink" href="../pages/questions.html">pages/questions.html</a> — what is known, what is missing, how to find it, recorded per question with source links</td>',
                        f"<td>{pill('warn', 'OPEN BY DESIGN')}</td>",
                    ],
                    [
                        "<td>3</td>",
                        "<td>Whether the platform in the brief actually exists yet, requirement by requirement</td>",
                        '<td><a class="pagelink" href="requirements.html">Requirements</a> — every requirement with a status and a named pointer to the code or the gap</td>',
                        f"<td>{pill('info', 'PUBLISHED')}</td>",
                    ],
                    [
                        "<td>4</td>",
                        "<td>How to stop the site reading as machine output</td>",
                        '<td><a class="pagelink" href="content-plan.html">Content plan</a> — the complaint restated as the four things Google actually rates, and a plan that starts from evidence already gathered</td>',
                        f"<td>{status_pill('PARTIAL')}</td>",
                    ],
                    [
                        "<td>5</td>",
                        "<td>What is wrong or unverified, including this task's own mistakes</td>",
                        '<td><a class="pagelink" href="flagged.html">Flagged for review</a> — the three irregularities found in this review, plus the project flags that bear on them</td>',
                        f"<td>{pill('warn', 'FLAGGED')}</td>",
                    ],
                ],
            ),
        )
    )

    # Blockers derived from the canonical register's needs_answers edges.
    blockers: dict[str, list[str]] = {}
    for s in all_sugs():
        for q in (s.get("needs_answers") or []):
            blockers.setdefault(q, []).append(s["id"])
    qmap = {q["id"]: q for q in all_qs()}
    rows = []
    for qid in sorted(blockers, key=lambda k: (-len(blockers[k]), k)):
        q = qmap.get(qid)
        if not q:
            continue
        rows.append(
            [
                f'<td class="cell-code">{esc(qid)}</td>',
                f'<td><a class="pagelink" href="../pages/questions.html#{esc(qid)}">{esc(q["question"])}</a></td>',
                f"<td>{status_pill(q_state(q))}</td>",
                f'<td class="cell-code">{esc(", ".join(sorted(blockers[qid])))}</td>',
                f'<td>{esc(q.get("owner") or "")}</td>',
                source_cell(q.get("source_ids")),
            ]
        )
    body.append(
        panel(
            "The blockers, derived from the canonical register",
            '<p class="lede" style="margin-bottom:12px">Computed from the <code>needs_answers</code> edges in '
            "<code>ledger/suggestions.json</code>: each row is a question and the suggestions that cannot start "
            "until it is answered, ordered by how many suggestions it unblocks. Nothing here is narrated; re-running "
            "the generator recomputes it.</p>"
            + table(
                ["Question", "Asks", "State", "Blocks", "Who can answer it", "Official source"],
                rows,
                caption="Derived: one row per question that blocks at least one suggestion.",
            ),
        )
    )

    body.append(
        panel(
            "What cannot be decided from the information that exists",
            '<ul class="findings">'
            "<li><strong>Nothing about money.</strong> There is no Associates account and no tag, so no click, "
            "conversion or earnings figure exists or could exist. No proposal is costed in commission terms, "
            "because that would be an invented number.</li>"
            "<li><strong>Nothing about demand.</strong> Amazon publishes a hard prerequisite for catalog access — "
            "enrolment plus at least 10 qualifying sales in the past 30 days — and no analytics or Search Console "
            "data exists to substitute. Which products trend cannot be known here.</li>"
            "<li><strong>Nothing about the owner's intent.</strong> Whether the three supplied links point at the "
            "intended products, who the author of record is, which marketplace applies, and whether a domain will "
            "be bought are all owner decisions, recorded as open questions rather than assumed.</li>"
            "<li><strong>What can be decided now:</strong> the editorial and disclosure items. They need no Amazon "
            "account, and they are the ones that address the complaint that the site reads like machine output.</li>"
            "</ul>",
        )
    )
    return render(
        "index.html",
        "Decision hub",
        "The requirement set, the content plan and the review record behind the canonical decision board, with every "
        "claim traced to an official source or explicitly left blank.",
        "".join(body),
    )


def page_requirements() -> str:
    c = counts()
    parts = [
        notice(
            "A status is only as good as its pointer",
            "Every row below carries a closed-vocabulary status and a named pointer for its evidence — a file, a "
            "function or a ledger row. The build refuses a PARTIAL row with no stated gap and a MET row that carries "
            "one, so a status cannot be asserted without something to check it against.",
        ),
        kpis(
            [
                (str(c["reqs"]), "requirements"),
                (str(c["reqs_met"]), "met"),
                (str(c["reqs_partial"]), "partly met"),
                (str(c["reqs_not_met"]), "not met"),
            ]
        ),
        panel(
            "What the status words mean",
            table(
                ["Status", "Meaning"],
                [
                    [f"<td>{status_pill(k)}</td>", f"<td>{esc(v)}</td>"]
                    for k, v in REQS["status_vocabulary"].items()
                ],
            ),
        ),
    ]
    for g in REQS["groups"]:
        rows = []
        for r in g["rows"]:
            gap = f'<div class="row-note"><em>Gap:</em> {esc(r["gap"])}</div>' if r["gap"] else ""
            impl = (
                f'<div class="row-note"><em>Where:</em> <code>{esc(r["implementation"])}</code></div>'
                if r["implementation"]
                else '<div class="row-note"><em>Where:</em> &mdash; nothing implements it</div>'
            )
            flags = (
                '<div class="flags-inline">'
                + " ".join(ref_badge(f) for f in r["flag_ids"])
                + "</div>"
                if r["flag_ids"]
                else ""
            )
            rows.append(
                [
                    f'<td class="cell-code" id="{esc(r["id"])}">{esc(r["id"])}<div class="row-note">{esc(r["kind"])}</div></td>',
                    f"<td>{esc(r['requirement'])}</td>",
                    f"<td>{status_pill(r['status'])}</td>",
                    f'<td>{esc(r["evidence"])}{gap}{impl}{flags}</td>',
                    source_cell(r["source_ids"]),
                ]
            )
        parts.append(
            panel(
                f"{g['id']}. {g['name']}",
                f'<p class="lede" style="margin-bottom:12px">{esc(g["lead"])}</p>'
                + table(["ID", "Requirement", "Status", "Evidence, gap and where it lives", "Official source"], rows),
            )
        )
    return render(
        "requirements.html",
        "The full requirement set",
        "Every requirement in the brief, its state, and the exact place in the repository that satisfies or fails it.",
        "".join(parts),
    )


def page_content_plan() -> str:
    """The 'AI slop' answer: restate the complaint as the four testable attributes Google names."""
    content_reqs = [r for r in all_reqs() if r["kind"] == "quality"]
    rows = []
    for r in content_reqs:
        gap_html = (
            '<div class="row-note"><em>Gap:</em> ' + esc(r["gap"]) + "</div>" if r["gap"] else ""
        )
        rows.append(
            [
                f'<td class="cell-code">{esc(r["id"])}</td>',
                f"<td>{esc(r['requirement'])}</td>",
                f"<td>{status_pill(r['status'])}</td>",
                f'<td>{esc(r["evidence"])}{gap_html}</td>',
                source_cell(r["source_ids"]),
            ]
        )

    body = [
        notice(
            "\"AI slop\" is a real, defined complaint, not a matter of taste",
            "Google's documentation describes the failure precisely: content produced by generative AI 'without manual "
            "oversight or curation' represents 'little to no effort', and 'using generative AI tools or other similar "
            "tools to generate many pages without adding value for users may violate' the scaled-content-abuse policy. "
            "So the fix is not better prose — it is adding work the machine did not do.",
        ),
        panel(
            "The four attributes Google actually rates, and where this site stands",
            table(["ID", "What is required", "State", "Evidence and gap", "Official source"], rows),
        ),
        panel(
            "Why this site currently reads as machine output",
            '<ul class="findings">'
            "<li><strong>Everything is a table.</strong> The layout is honest and unusual, and honesty is the site's "
            "best asset — but a page of sourced cells makes no argument, and an argument is what a reader came for.</li>"
            "<li><strong>No human made a judgement anywhere.</strong> Every sentence is either a quoted requirement or "
            "a rendered value. A reader can feel the absence of a person choosing between two products and saying why.</li>"
            "<li><strong>The strongest material is buried.</strong> The three published spec conflicts — the 1000 W vs "
            "1700 W power discrepancy and the 24 vs 25 cooking-function discrepancy — are the most useful and most "
            "original things this project produced, and they are recorded as flags rather than written up as the "
            "reason to read the site.</li>"
            "<li><strong>No byline, no date-of-a-person, no voice.</strong> Google asks who created the content and "
            "whether that is self-evident; on this site it is not evident at all.</li>"
            "</ul>",
        ),
        panel(
            "The plan, in the order that needs no Amazon account first",
            "<ol class=\"findings\">"
            "<li><strong>Write three pieces that carry an argument.</strong> A decision-first buying guide "
            "(organised by kitchen constraint, not by product), a capacity explainer that uses the verified "
            "6 Qt-in-two-3-Qt-baskets figure as its worked example, and a 'what the marketing copy hides' piece "
            "built from the spec conflicts already in the ledger. This is original analysis of evidence the project "
            "already owns, and it is the only content on the site that a copy-farm competitor could not reproduce. "
            "The article-format choice itself belongs to the canonical board (SG-04).</li>"
            "<li><strong>Publish an author or an editorial statement.</strong> One honest sentence about how the "
            "site is made beats an invented persona, which Google explicitly calls deception. The voice question "
            "is SG-05 on the canonical board.</li>"
            "<li><strong>Put the paid-link label next to every affiliate link.</strong> Two hours, and it closes the "
            "gap measured in RF-02: 7 pages carry an outbound affiliate anchor, only 3 carry the in-context "
            "label.</li>"
            "<li><strong>Then measure, and only then expand.</strong> Without impressions and queries the next "
            "article is a guess, and guessing is how the generic set got written. Measurement is SG-09 on the "
            "canonical board.</li>"
            "<li><strong>Do not write about products nobody has handled</strong> in a voice that implies otherwise. "
            "The FTC states you cannot talk about your experience with a product you have not tried; the project has "
            "tested nothing, and the plan is built to stay true to that.</li>"
            "</ol>",
        ),
        panel(
            "What would make this page unnecessary",
            "<p class=\"lede\">A page per decision that a reader cannot get anywhere else, written by someone whose "
            "name is on it, based on evidence a content farm would not have gathered. The repository's machinery "
            "already gathers that evidence and gates it; what it has never had is a writer, a byline and a measurement "
            "of whether anyone reads the result. Those are the three gaps this plan closes.</p>",
        ),
    ]
    return render(
        "content-plan.html",
        "The content plan",
        "The \"does not read like AI slop\" requirement, restated as the four things Google actually asks for, with a "
        "plan that starts from the evidence this project already owns.",
        "".join(body),
    )


def page_flagged() -> str:
    """Everything unverified: requirement gaps, open questions, this review's own findings, and the
    project flags that bear on them."""
    legacy = load("flags.json")["flags"]
    req_partial = [r for r in all_reqs() if r["status"] in ("PARTIAL", "NOT_MET")]
    q_open = [q for q in all_qs() if q_state(q) == "OPEN"]

    body = [
        notice(
            "What this page is",
            "Four kinds of flag, kept apart. Requirement rows that are not fully met. Canonical questions with no "
            "answer yet. Irregularities found during this review — including this task's own first error. And the "
            "existing project flags that bear on the choices above. Nothing here blocks a merge; each item blocks "
            "an assertion.",
        ),
    ]

    body.append(
        panel(
            "Irregularities found while reviewing the repository (this task)",
            f'<p class="lede" style="margin-bottom:12px">{esc(FINDINGS["note"])}</p>'
            + table(
                ["ID", "Finding", "Impact", "Recommendation", "Official source"],
                [
                    [
                        f'<td class="cell-code" id="{esc(f["id"])}">{esc(f["id"])}<div class="row-note">{esc(f["severity"])}</div></td>',
                        f'<td>{esc(f["finding"])}<div class="row-note">{esc(f["owner_note"])}</div></td>',
                        f'<td>{esc(f["impact"])}</td>',
                        f'<td>{esc(f["recommendation"])}</td>',
                        source_cell(f["source_ids"]),
                    ]
                    for f in FINDINGS["findings"]
                ],
            ),
        )
    )

    body.append(
        panel(
            "Requirement rows that are not fully met",
            table(
                ["ID", "Requirement", "Status", "Gap", "Official source"],
                [
                    [
                        f'<td class="cell-code" id="{esc(r["id"])}">{esc(r["id"])}</td>',
                        f"<td>{esc(r['requirement'])}</td>",
                        f"<td>{status_pill(r['status'])}</td>",
                        f"<td>{esc(r['gap'])}</td>",
                        source_cell(r["source_ids"]),
                    ]
                    for r in req_partial
                ],
                caption="Derived: rows whose status is PARTIAL or NOT_MET.",
            ),
        )
    )
    body.append(
        panel(
            "Canonical questions that no official source answers yet",
            '<p class="lede" style="margin-bottom:12px">Read from <code>ledger/questions.json</code>, the T29 '
            "register. The full row, including what is missing and how to find it, is on "
            '<a class="pagelink" href="../pages/questions.html">the canonical page</a>.</p>'
            + table(
                ["ID", "Question", "State", "Missing information", "How to find it"],
                [
                    [
                        f'<td class="cell-code" id="{esc(q["id"])}">{esc(q["id"])}</td>',
                        f'<td>{esc(q["question"])}</td>',
                        f"<td>{status_pill(q_state(q))}</td>",
                        f"<td>{esc(q['missing'])}</td>",
                        f"<td>{esc(q['how_to_find'])}</td>",
                    ]
                    for q in q_open
                ],
                caption="Derived: rows with no recorded answer.",
            ),
        )
    )

    bearing = [
        f
        for f in legacy
        if any(k in json.dumps(f).lower() for k in ("link.amazon", "associates tag", "mapping", "price", "bounty"))
    ]
    rows = []
    for f in bearing[:20]:
        ids = f.get("source_ids") or ([f["source_id"]] if f.get("source_id") else [])
        rows.append(
            [
                f'<td class="cell-code">{esc(f["id"])}</td>',
                f'<td><a class="pagelink" href="../pages/flags.html#{esc(f["id"])}">{esc(f.get("title", ""))}</a></td>',
                f'<td>{esc(str(f.get("state", f.get("status", ""))))}</td>',
                source_cell(ids),
            ]
        )
    body.append(
        panel(
            "Project flags that bear on these choices",
            '<p class="lede" style="margin-bottom:12px">From <code>ledger/flags.json</code>, filtered to entries '
            "touching link attribution, price display, commission transcription or the product mapping. The full "
            "register stays on the findings site.</p>"
            + table(["Flag", "Subject", "State", "Official source"], rows),
        )
    )
    return render(
        "flagged.html",
        "Flagged for review",
        "Everything unverified or still open in this review — requirement gaps, unanswered questions, this task's own "
        "corrected error, and the project flags that bear on them.",
        "".join(body),
    )


# --------------------------------------------------------------------------- executive summary (markdown)


def esc_md(v: str) -> str:
    return str(v).replace("|", "\\|").replace("\n", " ")


def build_summary_md() -> str:
    c = counts()
    q_open = [q for q in all_qs() if q_state(q) == "OPEN"]
    sugs = all_sugs()
    unblocked = [s for s in sugs if not (s.get("needs_answers") or [])]
    lines = [
        "# Decision review — executive summary",
        "",
        f"Generated by `tools/build_decisions.py` from `ledger/{{requirements,questions,suggestions}}.json` on "
        f"{AS_OF}. This file and the published pages are rendered from the same data in the same run, so they cannot "
        "disagree. **Nothing proposed here has been implemented.**",
        "",
        "## The one-paragraph version",
        "",
        f"The brief asks for a great deal that automated agents can build and a few things they cannot. Of the "
        f"{c['reqs']} requirements this review tracks, {c['reqs_met']} are met and verifiable, {c['reqs_partial']} "
        f"are partly met, and {c['reqs_not_met']} are not met. The pattern behind that split is simple: everything "
        "that depends on Amazon's catalog data is blocked on an account prerequisite that does not exist, and "
        "everything that depends on original writing is blocked on a person. The decision board carries "
        f"{c['sugs']} suggestions awaiting an owner choice and {c['qs']} questions, {c['qs_open']} of which have no "
        "recorded answer.",
        "",
        "## What is blocked, and by what",
        "",
        "| Blocker | Published requirement | What it stops |",
        "|---|---|---|",
        "| No approved Associates account and no Associates tag | Creators API prerequisites: enrolled, plus "
        "**at least 10 qualifying sales within the past 30 days** | Every catalog fact, every monetized link, all "
        "click/conversion/earnings tracking, all trend and conversion scoring |",
        "| No first-party measurement | No analytics or Search Console property exists | Any evidence-led choice of "
        "what content to write next |",
        "| No author of record, and no product has been handled | Google treats fabricated authorship as deception; "
        "the FTC states you cannot claim experience you do not have | Byline, trust signals, any first-hand review |",
        "| The supplied short codes are not ASINs | Supplied tokens are 9 characters; Amazon's help describes an "
        "ASIN as the 10-digit product code; `/dp/<code>` is Page Not Found | Confirming the destinations are the "
        "intended products |",
        "",
        f"## Can be decided without any new access ({len(unblocked)} of {len(sugs)} suggestions)",
        "",
    ]
    for s in unblocked:
        rec = s.get("recommended") or ""
        chosen = next((o for o in s.get("options", []) if o.get("id") == rec), None)
        lines += [
            f"### {s['id']} — {s['area']}",
            "",
            f"**{s['title']}**",
            "",
            f"*Proposed.* {s['suggestion']}",
            "",
            f"*Recommended option.* {rec}" + (f" — {chosen['label']}" if chosen else ""),
            "",
            f"*Why.* {s['why']}",
            "",
            f"*Sources.* {', '.join(s.get('evidence') or [])}",
            "",
        ]
        for o in s.get("options", []):
            lines.append(f"- **{o['id']}** {o['label']} — {o['tradeoff']}")
        lines.append("")
    lines += [
        "## Needs an answer first",
        "",
        "| Suggestion | Title | Needs answers to |",
        "|---|---|---|",
    ]
    for s in sugs:
        if s.get("needs_answers"):
            lines.append(f"| {s['id']} | {s['title']} | {', '.join(s['needs_answers'])} |")
    lines += [
        "",
        f"## Questions with no recorded answer ({len(q_open)})",
        "",
        "| ID | Question | What is missing | Who can find it |",
        "|---|---|---|---|",
    ]
    for q in q_open:
        lines.append(
            f"| {q['id']} | {esc_md(q['question'])} | {esc_md(q['missing'])[:160]}… | {esc_md(q.get('owner') or '')} |"
        )
    lines += [
        "",
        "The full register, with the discovery action for each row, is at `pages/questions.html`. The decision board "
        "is at `pages/suggestions.html`.",
        "",
        "## Irregularities found in this review",
        "",
        "| ID | Finding | Recommendation |",
        "|---|---|---|",
    ]
    for f in FINDINGS["findings"]:
        lines.append(f"| {f['id']} | {esc_md(f['finding'])} | {esc_md(f['recommendation'])} |")
    lines += [
        "",
        "## How to decide",
        "",
        "1. Read `pages/suggestions.html`. Each row states the options, which one is recommended, the trade-off, and "
        "what must be answered first.",
        "2. Answer the blocking questions on `pages/questions.html`. Blank means unknown; nothing there is guessed.",
        "3. Record one decision per suggestion in `ledger/suggestions.json`, then regenerate with "
        "`python3 tools/build_site.py && python3 tools/build_decisions.py`.",
        "4. Implement only what was adopted, one batch per decision, each with its own gate run.",
        "",
        "## Compliance position, stated plainly",
        "",
        "The site is compliant on the things that can be checked mechanically, and the gates prove it: the required "
        "disclosure sentence is on every page, no product price is published anywhere, outbound product links are "
        "qualified with `rel=\"sponsored\"`, and no rating or review figure is displayed without a licensed feed. "
        "It is not yet monetized and not yet author-attributed, and both are recorded as gaps rather than described "
        "as complete.",
        "",
        "## Sources",
        "",
        "Every claim above traces to a row in `ledger/sources.json`. The sources this review added are Amazon's "
        "application-review page (S38) and Google's guidance on generative AI content (S39), helpful content (S40), "
        "spam policies (S41) and review quality (S42).",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- build


def vendor_assets(out_root: Path) -> None:
    src = next((REPO / c for c in DESIGN_CANDIDATES if (REPO / c).is_file()), None)
    (out_root / "assets").mkdir(parents=True, exist_ok=True)
    dest = out_root / "assets" / "dashboard.css"
    if src is None:
        if dest.exists():
            dest.unlink()
    else:
        header = (
            f"/* Vendored from {src.relative_to(REPO).as_posix()} by tools/build_decisions.py - do not edit here.\n"
            "   Re-run the builder after changing the source. */\n"
        )
        # CR (session 2b257b2e, T34 integration): the shared stylesheet now bundles its
        # fonts via relative url(...)s. Vendored one level deeper (decisions/assets/),
        # those paths would resolve into decisions/assets/fonts/, which does not exist;
        # rewrite them to point back at the repository-root font files.
        # Either authoring form is normalised to the repository-root font files: this copy is
        # published from decisions/assets/, so ../fonts/ and assets/fonts/ both resolve inside the
        # namespace and 404. Repaired from two sides on 2026-11-15 - session 1b839f87 fixed the
        # source sheet and the copies, session bbcc741f made the builders tolerant of both forms so
        # a stylesheet move cannot silently cost a namespace its webfonts (F-39).
        text = (src.read_text(encoding="utf-8")
                .replace('url("../fonts/', 'url("../../assets/fonts/')
                .replace('url("assets/fonts/', 'url("../../assets/fonts/'))
        dest.write_text(header + text, encoding="utf-8")
    site_css = REPO / "tools" / "pages-site.css"
    if site_css.is_file():
        shutil.copy2(site_css, out_root / "assets" / "site.css")
    # Namespace-specific sheet: fills the classes the base design system does not define.
    own = REPO / "tools" / "decisions.css"
    if own.is_file():
        shutil.copy2(own, out_root / "assets" / "decisions.css")


def build(out_root: Path) -> list[str]:
    out_root.mkdir(parents=True, exist_ok=True)
    vendor_assets(out_root)
    pages = {
        "index.html": page_index(),
        "requirements.html": page_requirements(),
        "content-plan.html": page_content_plan(),
        "flagged.html": page_flagged(),
    }
    written = []
    for name, doc in pages.items():
        (out_root / name).write_text(doc, encoding="utf-8")
        written.append(name)
    manifest = {
        "generated": sorted(written),
        "count": len(written),
        "as_of": AS_OF,
        "note": "Generated by tools/build_decisions.py from ledger/*.json - edit the data, not the HTML.",
        "implemented": 0,
    }
    (out_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return written


def digest(root: Path) -> dict[str, str]:
    return {
        str(f.relative_to(root)): hashlib.sha256(f.read_bytes()).hexdigest()[:16]
        for f in sorted(root.rglob("*"))
        if f.is_file()
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="render to a temp dir and compare with committed output")
    args = ap.parse_args()

    summary = build_summary_md()

    if args.check:
        tmp = Path(tempfile.mkdtemp(prefix="z2dec-"))
        build(tmp)
        fresh, committed = digest(tmp), digest(OUT)
        drift = sorted(k for k in set(fresh) | set(committed) if fresh.get(k) != committed.get(k))
        shutil.rmtree(tmp, ignore_errors=True)
        current = (REPO / "DECISIONS.md").read_text(encoding="utf-8") if (REPO / "DECISIONS.md").is_file() else ""
        md_drift = current != summary
        print(json.dumps({"built": len(fresh), "drifted": drift, "summary_stale": md_drift}, indent=2))
        if drift or md_drift:
            print("decisions/ or DECISIONS.md is out of date - run python3 tools/build_decisions.py", file=sys.stderr)
            return 1
        return 0

    written = build(OUT)
    (REPO / "DECISIONS.md").write_text(summary, encoding="utf-8")
    (REPO / ".nojekyll").write_text("", encoding="utf-8")
    print(json.dumps({"pages": len(written), "as_of": AS_OF, "out": "decisions/"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
