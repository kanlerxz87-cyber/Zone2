#!/usr/bin/env python3
"""T42 (session 2b07e526, 2026-11-15) - release-readiness board.

Why this file exists
--------------------
The repository already answers "did we verify what we published?" (pages/verification.html),
"what are we proposing to change?" (pages/suggestions.html), and "why is the account not earning?"
(COORDINATION.md). None of them answers the question a person has before spending an evening on an
Associates application:

    Amazon publishes the list of things it checks when it reviews a Site. Which of those does this
    repository meet today, which does it not, and what exactly is missing?

That list is on S23 (Application Review Process). This generator renders one row per named
requirement on that page, with the count or path in this repository that settles each row, and
refuses to publish when it cannot settle one.

The gate is the point
---------------------
A readiness board is worthless if it can drift from the tree. `--check` rebuilds the page in memory
and fails when the committed HTML differs. validate() fails the build on:

  * a row with no official source id, or an id that does not resolve in ledger/sources.json
  * a row quoting S23 whose quote is not a substring of the S23 text captured in this register
  * a BLOCKED row that does not name the open question blocking it, or has no owner action
  * a GAP / OPEN / UNVERIFIED row with no owner action (a gap with no next step is not a finding)
  * a `measure` key this generator cannot compute (an unmeasurable row)
  * a count the register states that disagrees with the tree it is describing
  * a `{measure}` token in a `site_state` that names no measure this generator can compute
  * a published page without the disclosure sentence, a product price, or a broken local link

Counts are derived, not typed
-----------------------------
A `site_state` may contain a `{measure}` token — for example `{pages_with_disclosure}`. The token is
replaced with the measured value when the page is rendered, and the rendered number is the one the gate
checks. A hand-typed number is still accepted, and is still checked against the tree, so a typed count
that drifts still fails the build. The difference is that a token cannot drift: every page any session
adds to this repository moves the number, and a token follows it. This defect class had already bitten
this register twice (T48 recorded the 124-vs-126 instance; the 126-vs-134 instance was measured on
2026-11-16), each time because the sentence in the register was typed and the tree moved.

Usage
-----
    python3 tools/build_readiness.py           # write release/index.html
    python3 tools/build_readiness.py --check   # fail if the committed output is stale
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "ledger"
OUT = REPO / "release" / "index.html"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE_NAME = "Zone2"
AS_OF = "2026-11-15"

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(
    r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I
)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|stream|tax|"
    r"refund|withhold)\w*",
    re.I,
)

# Closed vocabulary. The validator rejects anything else, so no row can be asserted with a status
# word the reader has to interpret.
STATES = {
    "MET": "A requirement Amazon names is satisfied today, and the cell says how it is checkable.",
    "GAP": "A requirement Amazon names is not satisfied. Nothing blocks it but work.",
    "BLOCKED": "A requirement cannot be satisfied until an owner decision or account state changes.",
    "OPEN": "The requirement's application here rests on a reading, not on Amazon's words.",
    "UNVERIFIED": "The repository cannot settle this row, and does not guess at it.",
    "NOT_APPLICABLE": "Amazon states the requirement for a surface this repository is not.",
}

NAV = [
    ("../index.html", "Overview"),
    ("../products.html", "Products"),
    ("../pages/suggestions.html", "Suggestions &amp; Decisions"),
    ("../pages/questions.html", "Open Questions"),
    ("../verification.html", "Verification"),
    ("../decisions/index.html", "Requirements &amp; Review"),
    ("../marketing/index.html", "Counter Notes"),
    ("index.html", "Release readiness"),
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_json(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- measurements

def published_pages() -> list[Path]:
    """Published pages, excluding this board's own output.

    The board cannot count itself: its KPI band states the count, so counting it would make every
    rebuild shift the number it reports. Excluded by path, not by directory, so the rest of release/
    would still be counted if it ever holds another page.
    """
    skip = {".git", "__pycache__", "node_modules", ".github"}
    out = []
    for p in sorted(REPO.rglob("*.html")):
        if any(part in skip for part in p.relative_to(REPO).parts):
            continue
        if p.resolve() == OUT.resolve():
            continue
        out.append(p)
    return out


def count_editorial_posts(reg: dict) -> int:
    """A candidate post counts only if it still exists and is an article, not a directory index."""
    n = 0
    for rel in reg["candidate_editorial_posts"]:
        p = REPO / rel
        if p.is_file() and p.name != "index.html":
            n += 1
    return n


def count_pages_with_disclosure() -> int:
    return sum(1 for p in published_pages() if DISCLOSURE in p.read_text(encoding="utf-8"))


def count_pages_with_tagged_link() -> int:
    """A tagged link is an Amazon URL carrying an Associates tag in Amazon's published format (NAME-NN).

    `tag=YOURASSOCIATEID` is the placeholder Amazon prints in its own example, not a tag, and does
    not count. Measured 2026-11-15: zero pages carry one.
    """
    pat = re.compile(r"tag=[A-Za-z0-9]+-[0-9]{2}\b")
    return sum(1 for p in published_pages() if pat.search(p.read_text(encoding="utf-8")))


def published_namespaces() -> list[str]:
    """Directories that publish at least one HTML page, plus the repository root."""
    skip = {".git", ".github", "__pycache__", "node_modules", "tools", "tests", "docs", "ledger",
            "content", "assets"}
    out = ["."]
    for d in sorted(p for p in REPO.iterdir() if p.is_dir()):
        if d.name in skip:
            continue
        if any(d.rglob("*.html")):
            out.append(d.name)
    return out


def oldest_page_date() -> tuple[str, int]:
    """Oldest date this repository prints for its own content.

    Read from the dates the pages actually show, not from file mtimes: a checkout timestamp is not
    a content date. Returns (date, age in days relative to AS_OF).
    """
    pattern = re.compile(
        r"(?:read|verified|observed|re-observed|reviewed|checked)\s+(?:on\s+)?(20\d\d-\d\d-\d\d)", re.I
    )
    dates: set[str] = set()
    for p in published_pages():
        dates.update(pattern.findall(p.read_text(encoding="utf-8")))
    if not dates:
        return AS_OF, 0
    oldest = min(dates)
    y, m, d = (int(x) for x in oldest.split("-"))
    ref = date(*[int(x) for x in AS_OF.split("-")])
    return oldest, (ref - date(y, m, d)).days


MEASURES = {
    "editorial_posts": lambda reg: count_editorial_posts(reg),
    "pages_with_disclosure": lambda reg: count_pages_with_disclosure(),
    "pages_with_tagged_link": lambda reg: count_pages_with_tagged_link(),
    "published_namespaces": lambda reg: len(published_namespaces()),
    "oldest_page_days": lambda reg: oldest_page_date()[1],
}


def measured_facts(reg: dict) -> dict[str, object]:
    return {k: fn(reg) for k, fn in MEASURES.items()}


# A `{measure}` token inside a `site_state`. The token names a key of MEASURES; the builder replaces it
# with the measured value at render time, so the number in the sentence is derived from the tree rather
# than typed into the register and left behind when the tree moves.
TOKEN_RE = re.compile(r"\{([a-z_][a-z0-9_]*)\}")


def tokens_in(text: str) -> list[str]:
    """The measure names a `site_state` asks to have substituted into it."""
    return TOKEN_RE.findall(text or "")


def resolve_tokens(text: str, facts: dict[str, object]) -> str:
    """Replace every `{measure}` token with its measured value.

    An unknown token is left in place on purpose: the gate reports it, and a literal `{foo}` reaching
    the published page is a visible defect rather than a silent zero.
    """
    if not text:
        return text
    return TOKEN_RE.sub(
        lambda m: str(facts[m.group(1)]) if m.group(1) in facts else m.group(0), text
    )


# --------------------------------------------------------------------------- validation

def validate(reg: dict) -> list[str]:
    problems: list[str] = []
    sources = {s["id"]: s for s in load_json("sources.json")["sources"]}
    questions = {q["id"] for q in load_json("questions.json")["questions"]}
    quotes = "\n".join(reg.get("primary_source_quotes", []))

    primary = reg.get("primary_source_id")
    if primary not in sources:
        problems.append("primary_source_id does not resolve in ledger/sources.json")
    elif sources[primary].get("url") != reg.get("primary_source_url"):
        problems.append("primary_source_url disagrees with ledger/sources.json")

    seen: set[str] = set()
    for r in reg["rows"]:
        rid = r.get("id", "?")
        if rid in seen:
            problems.append(f"{rid}: duplicate id")
        seen.add(rid)

        if r.get("state") not in STATES:
            problems.append(f"{rid}: state {r.get('state')!r} is not in the closed vocabulary")

        src = r.get("source_ids") or []
        if not src:
            problems.append(f"{rid}: no official source id - a row must cite where its requirement is stated")
        for sid in src:
            if sid not in sources:
                problems.append(f"{rid}: source id {sid!r} does not resolve in ledger/sources.json")
            elif sources[sid].get("kind") != "official":
                problems.append(f"{rid}: source {sid} is not an official source")

        if r.get("quote") and r["quote"] not in quotes:
            problems.append(
                f"{rid}: quote is not present in the S23 text captured in primary_source_quotes"
            )

        if r["state"] == "BLOCKED":
            blocked_by = r.get("blocked_by") or []
            if not blocked_by:
                problems.append(f"{rid}: BLOCKED with no blocked_by - a blocker must name who can clear it")
            for q in blocked_by:
                if q not in questions:
                    problems.append(f"{rid}: blocked_by {q!r} does not resolve in ledger/questions.json")
            if not r.get("owner_action"):
                problems.append(f"{rid}: BLOCKED with no owner_action")

        if r["state"] in {"GAP", "OPEN", "UNVERIFIED"} and not r.get("owner_action"):
            problems.append(
                f"{rid}: {r['state']} with no owner_action - a gap with no next step is not a finding"
            )

        if r.get("measure"):
            if r["measure"] not in MEASURES:
                problems.append(f"{rid}: unknown measure {r['measure']!r} - the row would be unmeasurable")
            elif not str(r.get("site_state", "")).strip():
                problems.append(f"{rid}: declares measure {r['measure']!r} but states no site_state")

        # A `{measure}` token in a site_state is how a count stays derived instead of typed.
        site_state = str(r.get("site_state", ""))
        names = tokens_in(site_state)
        for name in names:
            if name not in MEASURES:
                problems.append(
                    f"{rid}: site_state asks for {{{{{name}}}}} but this generator cannot compute that "
                    f"measure - the token would reach the published page unrendered"
                )
            elif r.get("measure") and name != r["measure"]:
                problems.append(
                    f"{rid}: site_state asks for {{{{{name}}}}} but the row's measure is "
                    f"{r['measure']!r} - the row would state a number it is not checked against"
                )
        if names and not r.get("measure"):
            problems.append(
                f"{rid}: site_state carries a measure token but the row declares no 'measure', so "
                f"nothing would check the number it states"
            )

    return problems


def check_claims(reg: dict) -> list[str]:
    """Cross-check the numbers the register states against the tree it describes.

    A measured row carries its count inside `site_state`, so the number lives in exactly one place.
    Two forms are accepted:

      * a `{measure}` token — the count is substituted at render time from the same measurement the
        gate uses, so it cannot drift. `rendered_claims()` then proves the rendered page states it.
      * a hand-typed number — still accepted, still checked, and still fails when the tree moves.

    The second form is why this function exists at all; the first is why a typed number is no longer
    needed on any row whose count changes whenever a page is added.
    """
    problems: list[str] = []
    facts = measured_facts(reg)
    for r in reg["rows"]:
        if not r.get("measure") or r["measure"] not in facts:
            continue  # validate() already reported the unknown key
        want = facts[r["measure"]]
        site_state = str(r.get("site_state", ""))
        if r["measure"] in tokens_in(site_state):
            continue  # derived; checked on the rendered page instead
        if str(want) not in site_state:
            problems.append(
                f"{r['id']}: site_state does not state the measured value {want} "
                f"(measure {r['measure']}); the tree and the register disagree"
            )
    return problems


def rendered_claims(reg: dict, page: str) -> list[str]:
    """Prove that every derived count reaches the published page as the measured number.

    This is the check that replaces the typed-number check for token rows: the substitution happens
    here, and this asserts the result is in the page that will be deployed.
    """
    problems: list[str] = []
    facts = measured_facts(reg)
    for r in reg["rows"]:
        names = tokens_in(str(r.get("site_state", "")))
        if not names:
            continue
        resolved = resolve_tokens(str(r.get("site_state", "")), facts)
        for name in names:
            if name not in facts:
                continue  # validate() already reported the unknown measure
            want = str(facts[name])
            if want not in resolved:
                problems.append(
                    f"{r['id']}: the rendered site_state does not state the measured value {want} "
                    f"(measure {name})"
                )
        if esc(resolved) not in page:
            problems.append(
                f"{r['id']}: the rendered site_state does not appear on the published page"
            )
    if TOKEN_RE.search(page):
        problems.append("an unresolved measure token reached the published page")
    return problems


# --------------------------------------------------------------------------- rendering

def pill(state: str) -> str:
    cls = {
        "MET": "rr-ok",
        "GAP": "rr-gap",
        "BLOCKED": "rr-blocked",
        "OPEN": "rr-open",
        "UNVERIFIED": "rr-unver",
        "NOT_APPLICABLE": "rr-na",
    }[state]
    return f'<span class="rr-pill {cls}">{esc(state)}</span>'


def src_links(ids: list[str]) -> str:
    sources = {s["id"]: s for s in load_json("sources.json")["sources"]}
    out = []
    for sid in ids:
        s = sources[sid]
        host = re.sub(r"^https?://(www\.)?", "", s["url"]).split("/")[0]
        out.append(
            f'<a class="src" href="{esc(s["url"])}" target="_blank" '
            f'rel="noopener noreferrer nofollow">{esc(sid)}'
            f'<span class="src-host">{esc(host)}</span></a>'
        )
    return "".join(out)


def render_rows(reg: dict) -> str:
    facts = measured_facts(reg)
    body = []
    for r in reg["rows"]:
        extra = ""
        if r.get("quote"):
            extra += f'<blockquote class="rr-quote">{esc(r["quote"])}</blockquote>'
        if r.get("site_state"):
            extra += f'<div class="row-note"><em>Site state:</em> {esc(resolve_tokens(r["site_state"], facts))}</div>'
        if r.get("measure"):
            extra += (f'<div class="row-note">measured in this tree: <code>{esc(r["measure"])}</code>'
                      f' = {esc(facts[r["measure"]])}</div>')
        if r.get("blocked_by"):
            links = " ".join(
                f'<a class="pagelink" href="../pages/questions.html#{esc(q)}">{esc(q)}</a>'
                for q in r["blocked_by"]
            )
            extra += f'<div class="row-note">blocked by {links}</div>'
        if r.get("owner_action"):
            extra += f'<div class="row-action"><strong>Open item.</strong> {esc(r["owner_action"])}</div>'
        body.append(
            "<tr>"
            f'<td class="cell-code">{esc(r["id"])}</td>'
            f"<td>{esc(r['requirement'])}{extra}</td>"
            f"<td>{pill(r['state'])}</td>"
            f'<td class="cell-src">{src_links(r["source_ids"])}</td>'
            "</tr>"
        )
    return "".join(body)


def render_open_items(reg: dict) -> str:
    rows = [r for r in reg["rows"] if r["state"] in {"GAP", "BLOCKED", "OPEN", "UNVERIFIED"}]
    body = []
    for i, r in enumerate(rows, 1):
        who = ", ".join(r.get("blocked_by") or []) or "no answer needed"
        body.append(
            "<tr>"
            f"<td>{i}</td>"
            f'<td class="cell-code">{esc(r["id"])}</td>'
            f"<td>{esc(r['requirement'])}</td>"
            f"<td>{pill(r['state'])}</td>"
            f'<td>{esc(r.get("owner_action") or "")}<div class="row-note">{esc(who)}</div></td>'
            f'<td class="cell-src">{src_links(r["source_ids"])}</td>'
            "</tr>"
        )
    return "".join(body)


CSS = """
.rr-wrap{max-width:1120px;margin:0 auto;padding:0 20px 64px}
.rr-top{display:flex;gap:12px;flex-wrap:wrap;align-items:baseline;justify-content:space-between;
border-bottom:1px solid var(--line,#e3e6ec);padding:14px 0;margin-bottom:26px}
.rr-brand{font-weight:650;letter-spacing:-.01em}
.rr-brand small{display:block;font-weight:400;color:#5b6270;font-size:12px;letter-spacing:.04em;
text-transform:uppercase}
.rr-topnav{display:flex;gap:14px;flex-wrap:wrap;font-size:13px}
.rr-topnav a{color:#5b6270;text-decoration:none;padding-bottom:2px;border-bottom:1px solid transparent}
.rr-topnav a:hover,.rr-topnav a.active{color:#16181d;border-bottom-color:#1f5f4f}
.rr-head h1{font-size:clamp(28px,4vw,40px);line-height:1.12;letter-spacing:-.02em;margin:18px 0 10px;
max-width:22ch}
.rr-lede{font-size:17px;color:#333;max-width:74ch;line-height:1.62}
.rr-disclosure{border-left:3px solid #1f5f4f;background:#f4f7f5;padding:10px 14px;font-size:13px;
color:#2a3a34;margin:0 0 22px;border-radius:0 6px 6px 0}
.rr-kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:24px 0 0}
.rr-kpi{border:1px solid #e3e6ec;border-radius:10px;padding:14px;background:#fff}
.rr-kpi .n{font-size:26px;font-weight:650;letter-spacing:-.02em}
.rr-kpi .l{font-size:12px;color:#5b6270;line-height:1.45;margin-top:4px}
.rr-card{border:1px solid #e3e6ec;border-radius:12px;background:#fff;padding:20px;margin:22px 0}
.rr-card h2{font-size:20px;margin:0 0 8px;letter-spacing:-.01em}
.rr-card p{color:#333;line-height:1.62;margin:0 0 12px}
.rr-table-wrap{overflow-x:auto;border:1px solid #e3e6ec;border-radius:10px;background:#fff}
table.rr-table{width:100%;border-collapse:collapse;font-size:13.5px}
table.rr-table th{text-align:left;font-size:11.5px;letter-spacing:.06em;text-transform:uppercase;
color:#5b6270;border-bottom:1px solid #e3e6ec;padding:10px 12px;background:#f7f8f9}
table.rr-table td{border-bottom:1px solid #e3e6ec;padding:12px;vertical-align:top;line-height:1.52}
table.rr-table tr:last-child td{border-bottom:0}
.cell-code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12px;white-space:nowrap}
.cell-src{font-size:11.5px;min-width:132px}
a.src{display:inline-block;margin:0 6px 4px 0;color:#1f5f4f;text-decoration:none;
border-bottom:1px dotted currentColor}
a.src .src-host{display:block;color:#5b6270;font-size:10.5px;border:0}
.pagelink{color:#1f5f4f;text-decoration:none;border-bottom:1px dotted currentColor}
.row-note{color:#5b6270;font-size:12px;margin-top:6px;line-height:1.5}
.row-action{margin-top:8px;font-size:12.5px;background:#fdf6e9;border-left:3px solid #c99a2e;
padding:8px 10px;border-radius:0 6px 6px 0;color:#4a3a12;line-height:1.52}
.rr-quote{margin:8px 0 0;padding:6px 10px;border-left:2px solid #e3e6ec;color:#555;font-size:12.5px;
font-style:italic}
.rr-pill{display:inline-block;font-size:10.5px;font-weight:650;letter-spacing:.05em;padding:3px 8px;
border-radius:999px;white-space:nowrap}
.rr-ok{background:#e7f3ec;color:#1f6f43}
.rr-gap{background:#fdf3dd;color:#8a5a00}
.rr-blocked{background:#fbeaec;color:#8c2f39}
.rr-open{background:#e9eefa;color:#3b5c8a}
.rr-unver{background:#eef0f3;color:#5b6270}
.rr-na{background:#f1f1f1;color:#666}
.rr-quotes{margin:0;padding-left:18px;color:#3a3f48;font-size:13px;line-height:1.66}
.rr-quotes li{margin-bottom:8px}
.rr-foot{border-top:1px solid #e3e6ec;margin-top:34px;padding-top:16px;font-size:12.5px;color:#5b6270;
line-height:1.62}
@media(max-width:640px){.rr-topnav{display:none}.rr-head h1{max-width:none}}
"""


def render(reg: dict) -> str:
    facts = measured_facts(reg)
    rows = reg["rows"]
    met = sum(1 for r in rows if r["state"] == "MET")
    open_items = [r for r in rows if r["state"] in {"GAP", "BLOCKED", "OPEN", "UNVERIFIED"}]
    oldest, age = oldest_page_date()
    active_cls = ' class="active"'
    nav = "".join(
        f'<a href="{h}"{active_cls if h == "index.html" else ""}>{lbl}</a>' for h, lbl in NAV
    )
    quotes = "".join(f"<li>&ldquo;{esc(q)}&rdquo;</li>" for q in reg["primary_source_quotes"])
    src = reg["primary_source_id"]
    url = reg["primary_source_url"]
    read = reg["primary_source_accessed_utc"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Release readiness: Amazon's own Application Review Process requirements, one row each, against what this repository can show today. {met} of {len(rows)} met; {len(open_items)} open items, each with an owner action and an official source.">
<title>Release readiness - what Amazon checks, and where this site stands - {SITE_NAME}</title>
<link rel="stylesheet" href="../assets/css/style.css">
<style>{CSS}</style>
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="rr-wrap">
<div class="rr-top">
  <div class="rr-brand">{SITE_NAME}<small>Release readiness</small></div>
  <nav class="rr-topnav" aria-label="Primary">{nav}</nav>
</div>

<main id="main">
<p class="rr-disclosure"><strong>Affiliate disclosure.</strong> {esc(DISCLOSURE)}
Nothing on this page is a product recommendation, and no product price is published here.</p>

<header class="rr-head">
  <p class="eyebrow">Reviewed {esc(AS_OF)} &middot; Amazon's own review criteria, row by row</p>
  <h1>What Amazon checks before it approves a Site, and where this one stands</h1>
  <p class="rr-lede">
    Amazon publishes the criteria its Associates team uses when it reviews an application
    (<a href="{esc(url)}" target="_blank" rel="noopener noreferrer nofollow">{esc(src)}, Application Review Process</a>,
    read {esc(read)}). This page takes each named requirement on that page, states it in Amazon's own words, and
    puts beside it the count or the path in this repository that settles it. {met} of {len(rows)} rows are met
    today. The other {len(open_items)} are listed under <a href="#open">Open items</a>, each with the official
    source of the requirement and the single action that would clear it. Where this repository cannot settle a
    row, the row says so and stays blank rather than guessing at an answer.
  </p>
  <div class="rr-kpis">
    <div class="rr-kpi"><div class="n">{met} / {len(rows)}</div><div class="l">Amazon review criteria met today</div></div>
    <div class="rr-kpi"><div class="n">{len(open_items)}</div><div class="l">Open items, each with an owner action</div></div>
    <div class="rr-kpi"><div class="n">{facts["editorial_posts"]}</div><div class="l">Editorial posts counted in the tree</div></div>
    <div class="rr-kpi"><div class="n">{age} d</div><div class="l">Age of the oldest content date any page prints ({esc(oldest)})</div></div>
    <div class="rr-kpi"><div class="n">{facts["pages_with_tagged_link"]}</div><div class="l">Pages carrying a real Associates tag</div></div>
  </div>
</header>

<section class="rr-card">
  <h2>The {len(reg["primary_source_quotes"])} things Amazon actually says</h2>
  <p>Quoted verbatim from {esc(src)} on {esc(read)}, so every row below traces to a sentence rather than to a summary:</p>
  <ul class="rr-quotes">{quotes}</ul>
  <p class="row-note">Source: <a class="src" href="{esc(url)}" target="_blank"
  rel="noopener noreferrer nofollow">{esc(src)}<span class="src-host">affiliate-program.amazon.com</span></a></p>
</section>

<section class="rr-card" id="board">
  <h2>The board, one row per named requirement</h2>
  <p>Every row carries the official page the requirement was read from. A measured row states the count this
  tree produces; the generator recomputes it and fails the build when the two disagree.</p>
  <div class="rr-table-wrap">
  <table class="rr-table">
    <thead><tr><th>ID</th><th>Requirement, as Amazon states it, and this site's state</th><th>State</th><th>Official source</th></tr></thead>
    <tbody>{render_rows(reg)}</tbody>
  </table>
  </div>
</section>

<section class="rr-card" id="open">
  <h2>Open items &mdash; what to do next, in order</h2>
  <p>The {len(open_items)} rows that are not met, each with the official source of the requirement and the single
  action that would clear it. Nothing on this list is a change to the site; each is a decision or a piece of work.</p>
  <div class="rr-table-wrap">
  <table class="rr-table">
    <thead><tr><th>#</th><th>ID</th><th>Requirement</th><th>State</th><th>Action</th><th>Official source</th></tr></thead>
    <tbody>{render_open_items(reg)}</tbody>
  </table>
  </div>
</section>

<section class="rr-card">
  <h2>What this board does not claim</h2>
  <ul class="rr-quotes">
    <li>It does not predict whether Amazon will approve an application. {esc(src)} states criteria and a
    reviewer's judgement; a row marked MET is a fact about this repository, not an approval.</li>
    <li>It does not state a product price, a traffic figure, a conversion rate or a commission estimate. None of
    those exists in this repository, and the build fails if a price is printed.</li>
    <li>It does not decide which of the published surfaces is the declared Site (RR-11). That is an owner
    decision, recorded as open.</li>
    <li>RR-02 and RR-12 are UNVERIFIED and OPEN because {esc(src)} states the ownership requirement without
    defining how it applies to a github.io address. This board does not fill that gap with an assumption.</li>
  </ul>
</section>

<footer class="rr-foot">
  <strong>Disclosure.</strong> {esc(DISCLOSURE)}<br>
  Generated by <code>tools/build_readiness.py</code> from <code>ledger/readiness.json</code> and
  <code>ledger/sources.json</code>; edit the data, never this page. Requirement text and quotes are from
  <a href="{esc(url)}" target="_blank" rel="noopener noreferrer nofollow">{esc(src)}</a>, read {esc(read)}.
  The register is re-checked against the tree on every build and every CI run.
  &middot; <a href="../index.html">Dashboard</a>
  &middot; <a href="../pages/suggestions.html">Suggestions board</a>
  &middot; <a href="../pages/questions.html">Open questions</a>
  &middot; <a href="../flagged.html">Flagged for review</a>
</footer>
</main>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- gates + CLI

def no_price_problems(page: str) -> list[str]:
    """The same context-aware rule as tools/validate_data.py and the CI price step."""
    out = []
    text = re.sub(r"<[^>]+>", " ", page)
    for unit in re.split(r"</tr>|</p>|</li>|<br\s*/?>", text):
        for m in MONEY.finditer(unit):
            if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                out.append(f"money value {m.group(0)!r} in a buying context")
    return out


def link_problems(page: str) -> list[str]:
    out = []
    for href in re.findall(r'href="([^"]+)"', page):
        if href.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = (OUT.parent / href.split("#")[0]).resolve()
        if target == OUT:
            continue
        if href.split("#")[0] == "":
            continue
        if not target.is_file():
            out.append(f"internal link does not resolve: {href}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed page is stale")
    args = ap.parse_args()

    reg = load_json("readiness.json")
    # Validate before rendering: an unresolvable source id makes the renderer raise, and a traceback
    # reads like a bug in the tool rather than a verdict on the data.
    problems = validate(reg) + check_claims(reg)
    if problems:
        print("release readiness: FAIL")
        for p in problems:
            print("  -", p)
        return 1
    page = render(reg)
    problems += no_price_problems(page)
    problems += link_problems(page)
    problems += rendered_claims(reg, page)
    if DISCLOSURE not in page:
        problems.append("the rendered page is missing the disclosure sentence")

    if problems:
        print("release readiness: FAIL")
        for p in problems:
            print("  -", p)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if current != page:
            print("release/index.html is stale - run python3 tools/build_readiness.py")
            return 1
        print(f"release/index.html is current - {len(reg['rows'])} rows, every one sourced")
        return 0

    OUT.write_text(page, encoding="utf-8")
    met = sum(1 for r in reg["rows"] if r["state"] == "MET")
    print(f"wrote {OUT.relative_to(REPO)} - {len(reg['rows'])} rows, {met} met, {len(reg['rows']) - met} open")
    return 0


if __name__ == "__main__":
    sys.exit(main())
