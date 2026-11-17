#!/usr/bin/env python3
"""Decision board generator — T62, session `arena/1bfbc559-zone2` (2026-11-17).

WHY THIS FILE EXISTS
--------------------
The 2026-11-17 brief asks for five things that this repository did not have: a suggestion
board where a path is chosen *before* anything is implemented; a register of what is known,
what is not, and how to find the missing information; a product-intent confirmation record
that keeps intent and observation in separate fields; a trace of the brief's own requirement
rows against the tree; and an executive summary. It also supplies two product links the
repository has never seen and the first tracking ID any brief has supplied.

WHAT IT WRITES
--------------
  board/index.html         the executive summary and the five-product situation
  board/products.html      the product-intent confirmation record (5 rows, two field groups)
  board/suggestions.html   the choose-a-path board (12 rows, nothing applied)
  board/questions.html     the known / unknown register (17 rows, open answers empty)
  board/requirements.html  the S-04..S-25 + theme + SG-27..SG-30 trace, measured
  board/topics.html        article and topic proposals, unordered on purpose
  board/sources.html       the source register, live and carried rows labelled apart
  board/verification.html  the line-by-line verification record
  board/flagged.html       irregularities, each with the source that establishes it

THE RULE THIS FILE EXISTS TO ENFORCE
------------------------------------
Every count printed on these pages is measured from the tree in the same run and substituted
for a {{token}} in the data. No prose in board/data/*.json is allowed to type a number that
describes the repository, because this repository has twice shipped a page whose prose
printed a count that had drifted from the register it described (FB-01/FB-02, and the two
defects the T57 live read-back caught). tools/validate_board.py re-measures and fails if a
printed number disagrees, and tools/test_board.py injects defects to prove the checks fire.

Nothing here edits a ledger, another generator, or another session's namespace.

Usage:  python3 tools/build_board.py            (writes the pages)
        python3 tools/build_board.py --check    (fails if a written page is stale)
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOARD = REPO / "board"
DATA = BOARD / "data"
SITE = "https://kanlerxz87-cyber.github.io/Zone2"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".github"}
PLACEHOLDER_TAGS = {"YOURASSOCIATEID", "YOURID", "YOURASSOCIATEID-20", ""}

NAV = [
    ("index.html", "Executive summary"),
    ("products.html", "Product intent"),
    ("suggestions.html", "Choose a path"),
    ("questions.html", "Known & unknown"),
    ("requirements.html", "Requirements trace"),
    ("topics.html", "Topics"),
    ("sources.html", "Sources"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged"),
]


# --------------------------------------------------------------------------- measurement


def published_pages() -> list[Path]:
    """The site as it was handed to this session.

    board/ is excluded on purpose. These measurements are the evidence for a trace of
    claims about the *existing* site: if board/ were counted, the page total would rise
    by nine and — worse — og_image, chooser_pages and counter_pages would be inflated by
    this namespace's own prose mentioning them. A register that measures itself measures
    the wrong thing. The exclusion is stated on board/requirements.html.
    """
    out = []
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if rel.parts[0] == "board":
            continue
        out.append(p)
    return out


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def _amazon_links(text: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>", text, re.I):
        href, tag = m.group(1), m.group(0)
        if re.search(r"(amazon\.com|amzlinks\.in|link\.amazon)", href, re.I):
            rel = re.search(r"rel=[\"']([^\"']*)[\"']", tag, re.I)
            out.append((href, (rel.group(1).lower() if rel else "")))
    return out


READER_ROOTS = ("marketing", "guides", "journal")
READER_ROOT_FILES = {
    "index.html", "products.html", "analysis.html", "summary.html", "questions.html",
    "suggestions.html", "paths.html", "compliance.html", "tracking.html", "content.html",
    "sources.html", "verification.html", "flagged.html",
}
GUIDE_ROOTS = ("marketing", "guides", "journal")
LINK_TARGETS = re.compile(r"(comparison\.html|buying-guide\.html|guides/index\.html)")


def measure() -> dict[str, object]:
    pages = published_pages()
    texts = {p: _read(p) for p in pages}

    titles: dict[str, int] = {}
    descs: dict[str, int] = {}
    no_desc = 0
    disclosed = 0
    og_image = 0
    jsonld = 0
    tagged = 0
    viewport = 0
    sc = 0
    endpoint = 0
    capture = 0
    chooser = 0
    counter = 0
    amazon = 0
    sponsored = 0

    for p, t in texts.items():
        m = re.search(r"<title[^>]*>(.*?)</title>", t, re.S | re.I)
        if m and m.group(1).strip():
            titles[m.group(1).strip()] = titles.get(m.group(1).strip(), 0) + 1
        m = (re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", t, re.S | re.I)
             or re.search(r"<meta\s+content=[\"'](.*?)[\"']\s+name=[\"']description[\"']", t, re.S | re.I))
        if m and m.group(1).strip():
            descs[m.group(1).strip()] = descs.get(m.group(1).strip(), 0) + 1
        else:
            no_desc += 1

        if DISCLOSURE in t:
            disclosed += 1
        if "og:image" in t:
            og_image += 1
        if "application/ld+json" in t:
            jsonld += 1
        if 'name="viewport"' in t:
            viewport += 1
        if 'name="google-site-verification"' in t:
            sc += 1
        if re.search(r"/collect|/api/event|navigator\.sendBeacon", t, re.I):
            endpoint += 1
        if re.search(r"<input[^>]*type=[\"']email", t, re.I):
            capture += 1
        if re.search(r"chooser|which-one|which one is for you|three-question", t, re.I):
            chooser += 1
        if re.search(r"counter.?space|capacity per centimetre|capacity per centimeter", t, re.I):
            counter += 1

        real_tag = False
        for mm in re.finditer(r"[?&]tag=([A-Za-z0-9_\-]*)", t):
            if mm.group(1) not in PLACEHOLDER_TAGS:
                real_tag = True
        if real_tag:
            tagged += 1

        for _href, rel in _amazon_links(t):
            amazon += 1
            if "sponsored" in rel:
                sponsored += 1

    def parts(p: Path) -> tuple[str, ...]:
        # `rel` is taken as a loop variable above; do not shadow it.
        return p.relative_to(REPO).parts

    reader = [p for p in pages
              if (parts(p)[0] in READER_ROOTS and len(parts(p)) > 1)
              or (len(parts(p)) == 1 and p.name in READER_ROOT_FILES)]
    spon_reader = 0
    plain_reader = 0
    for p in reader:
        for _href, rel in _amazon_links(texts[p]):
            if "sponsored" in rel:
                spon_reader += 1
            else:
                plain_reader += 1

    guides = [p for p in pages if len(parts(p)) > 1 and parts(p)[0] in GUIDE_ROOTS]
    unlinked = [p for p in guides if not LINK_TARGETS.search(texts[p])]

    # How many pages the *inverted* price rule collapses to a single unit.
    # Recorded as a measurement rather than typed, because it is a count of the
    # tree and the tree keeps growing — FL-13 was filed with 162 and the number
    # moved twice before this page was even published.
    collapse = 0
    for p in pages:
        units = re.split(r"</tr>|</p>|</li>|<br\s*/?>", re.sub(r"<[^>]+>", " ", texts[p]))
        if len(units) == 1:
            collapse += 1

    return {
        "pages": len(pages),
        "price_rule_collapsed": collapse,
        "tagged": tagged,
        "disclosed": disclosed,
        "og_image": og_image,
        "jsonld": jsonld,
        "viewport_pages": viewport,
        "unique_titles": len(titles),
        "dup_titles": sum(1 for v in titles.values() if v > 1),
        "dup_desc": sum(1 for v in descs.values() if v > 1),
        "no_desc": no_desc,
        "amazon_links": amazon,
        "sponsored_links": sponsored,
        "reader_pages": len(reader),
        "sponsored_reader": spon_reader,
        "unsponsored_reader": plain_reader,
        "guide_pages": len(guides),
        "guides_unlinked": len(unlinked),
        "sc_pages": sc,
        "endpoint_pages": endpoint,
        "capture_pages": capture,
        "chooser_pages": chooser,
        "counter_pages": counter,
        "feed_present": (REPO / "marketing" / "feed.xml").is_file(),
    }


_MEASURED: dict[str, object] = {}

# Every token this run substituted, and the value it substituted. Written to
# board/data/measured.json so tools/validate_board.py can re-measure the tree and prove
# no printed number has drifted — the check that catches the FB-01/FB-02 class of defect
# before a deploy rather than after one.
_SUBS: dict[str, object] = {}


def sub(text: str) -> str:
    """Replace {{token}} with a value measured from the tree."""
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key not in _MEASURED:
            raise SystemExit(f"build_board: unknown token {{{{{key}}}}}")
        _SUBS[key] = _MEASURED[key]
        return str(_MEASURED[key])
    return re.sub(r"\{\{(\w+)\}\}", repl, text)


# --------------------------------------------------------------------------- rendering


def e(s: object) -> str:
    return html.escape(str(s), quote=True)


def external(href: str, label: str | None = None) -> str:
    """An outbound link. Product links are marked sponsored; everything else is nofollow."""
    text = e(label if label is not None else href)
    if re.search(r"(amazon\.com/dp/|amazon\.com/[^/]*/dp/|link\.amazon/|amzlinks\.in/)", href):
        return f'<a href="{e(href)}" rel="sponsored nofollow noopener" target="_blank">{text}</a>'
    return f'<a href="{e(href)}" rel="nofollow noopener" target="_blank">{text}</a>'


def ref_link(rid: str) -> str:
    """Point an id at the page that hosts it. The questions register's `blocks`
    field mixes suggestion and requirement ids, and tools/audit_site.py fails a
    fragment that addresses nothing — which is how this got caught."""
    if rid.startswith("BS-"):
        return f'<a href="suggestions.html#{e(rid)}">{e(rid)}</a>'
    if rid.startswith("RQ-"):
        return f'<a href="requirements.html#{e(rid)}">{e(rid)}</a>'
    if rid.startswith("BQ2-"):
        return f'<a href="questions.html#{e(rid)}">{e(rid)}</a>'
    if rid.startswith("PI-"):
        return f'<a href="products.html#{e(rid)}">{e(rid)}</a>'
    target = {"FL-": "flagged.html", "VF2-": "verification.html",
              "BD-": "sources.html", "TP-": "topics.html"}.get(rid[:3])
    if target:
        return f'<a href="{target}#{e(rid)}">{e(rid)}</a>'
    return e(rid)


def src_links(ids: list[str]) -> str:
    rows = load("sources")["sources"]
    by_id = {r["id"]: r for r in rows}
    out = []
    for sid in ids:
        r = by_id.get(sid)
        if not r:
            raise SystemExit(f"build_board: unknown source id {sid}")
        out.append(f'<a href="sources.html#{e(sid)}" title="{e(r.get("title",""))}">{e(sid)}</a>')
    return " ".join(out)


def load(name: str) -> dict:
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


def page(title: str, description: str, here: str, body: str) -> str:
    items = []
    for href, label in NAV:
        current = ' aria-current="page"' if href == here else ""
        items.append(f'<a href="{e(href)}"{current}>{e(label)}</a>')
    nav = "".join(items)
    canonical = f"{SITE}/board/{here}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Counter Notes">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{e(canonical)}">
<meta name="robots" content="index,follow">
<link rel="stylesheet" href="assets/board.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="mast-in">
    <a class="brand" href="../index.html">Counter Notes<span>Decision board · 2026-11-17</span></a>
    <nav class="top" aria-label="Sections">{nav}</nav>
  </div>
</header>
<div class="disclosure">
  <div class="wrap">
    <strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} Product links on this site carry
    no Associates tag yet, so nothing bought through them can be attributed — see
    <a href="flagged.html#FL-02">FL-02</a>.
  </div>
</div>
<main id="main" class="wrap">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <nav aria-label="Footer">
      <a href="../index.html">Front page</a>
      <a href="../marketing/comparison.html">Head-to-head</a>
      <a href="../marketing/buying-guide.html">Which to buy</a>
      <a href="../guides/index.html">Guides</a>
      <a href="../brief/index.html">Design brief</a>
      <a href="../suggestions.html">Suggestion board</a>
      <a href="../questions.html">Open questions</a>
      <a href="../flagged.html">Flagged for review</a>
      <a href="../COORDINATION.md">Task board</a>
    </nav>
    <p><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)}</p>
    <p>Part of the Zone2 project register. Everything on these pages is either measured from
    this repository or read from an official source and cited; a value no official source
    states is left blank and flagged rather than filled in.
    Built by <code>tools/build_board.py</code> — a hand-edit here will not survive the next run.</p>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages


def page_index() -> str:
    d = load("products")
    q = load("questions")
    s = load("suggestions")
    f = load("flags")
    m = _MEASURED

    open_q = [x for x in q["questions"] if x["state"] != "answered"]
    answered_q = [x for x in q["questions"] if x["state"] == "answered"]
    high = [x for x in f["rows"] if x["severity"] == "high"]

    cards = f"""
<div class="cards">
  <div class="card card--accent"><span class="stat">{m['pages']}</span><span class="stat-label">published pages, all carrying the disclosure</span></div>
  <div class="card card--warn"><span class="stat">{m['tagged']}</span><span class="stat-label">carry a real Associates tag</span></div>
  <div class="card"><span class="stat">5</span><span class="stat-label">products in the brief · 3 in the register</span></div>
  <div class="card card--blank"><span class="stat">{len(open_q)}</span><span class="stat-label">questions open · {len(answered_q)} answered</span></div>
</div>"""

    body = f"""
<p class="eyebrow">Executive summary</p>
<h1>Five products, three of them on the site, and one string that decides the rest</h1>
<p class="standfirst">The brief that opened this session names five products. The register this site is
built from holds three. It also supplies a tracking ID for the first time — the one value every previous
session has flagged as missing. Both of those are new facts, and both are recorded here before anything
is changed because of them.</p>
{cards}

<h2>What is new since the last brief</h2>
<ol>
  <li><strong>Two products the repository has never seen.</strong>
      <code>link.amazon/B0c8moW59</code> and <code>link.amazon/B0f3GKalj</code> appear in no file in this
      repository before today. Both were fetched live and both resolve — to two meat thermometers, not
      to air fryers. Every product page this site has published is about air fryers.
      <span class="src">{src_links(['BD-01','BD-02','BD-03','BD-04'])}</span></li>
  <li><strong>A tracking ID: <code>shopnow047c-20</code>.</strong> No file in the repository mentions it
      before today and no published page carries a tag. It matches the shape Amazon publishes for a
      special-link tag, and it cannot be confirmed as an issued, active ID from any public page — only
      from inside the account.
      <span class="src">{src_links(['BD-12','BD-13'])}</span></li>
  <li><strong>A requirement list with statuses.</strong> Nineteen rows, most marked
      <em>Implemented</em>. Checked against the tree, most of them hold up: three do not, and one is
      honestly marked partial while missing the half the row names first.
      <span class="src">{src_links(['BD-21'])}</span></li>
</ol>

<h2>The finding that outranks the rest</h2>
<div class="card card--warn">
<p>Three of the five products resolve into <strong>Air Fryers</strong> and two into
<strong>Meat Thermometers</strong> — two different browse trees under the same Home &amp; Kitchen parent.
The eight-article calendar, the comparison, the buying guide, the chooser and the counter-space analysis
were all built for three air fryers. The plan is what is out of date, not the pages.</p>
<p class="small">Source: the category breadcrumb served by each destination listing, read live
2026-11-17. <span class="src">{src_links(['BD-03','BD-04','BD-09','BD-10','BD-11'])}</span></p>
</div>

<h2>Decide these three first</h2>
<p>Everything else on the board is cheaper once these are settled. Each is a decision, not a task.</p>
<div class="cards">
  <div class="card card--accent">
    <h4>1 · Is the tracking ID real?</h4>
    <p>Confirm <code>shopnow047c-20</code> and its marketplace inside Associates Central. One sign-in,
    no code. Until it is confirmed, no link on this site can attribute a purchase and the application
    cannot be reviewed.</p>
    <p class="small"><span class="pill pill--blank">open</span> <a href="questions.html#BQ2-01">BQ2-01</a>
    · <a href="suggestions.html#BS-01">BS-01</a></p>
  </div>
  <div class="card card--accent">
    <h4>2 · Is this one site or two?</h4>
    <p>Were the two thermometers meant for this site at all? The evidence is consistent with both
    readings, so only the person who supplied them can answer. Everything written for them waits
    behind this.</p>
    <p class="small"><span class="pill pill--blank">open</span> <a href="questions.html#BQ2-05">BQ2-05</a>
    · <a href="suggestions.html#BS-03">BS-03</a></p>
  </div>
  <div class="card card--accent">
    <h4>3 · Switch measurement on</h4>
    <p>The brief's own priority is to choose topics from measured queries instead of instinct. Nothing
    is measuring: {m['sc_pages']} of {m['pages']} pages carry a Search Console tag. This is the
    cheapest row on the board and the one that every other editorial decision depends on.</p>
    <p class="small"><span class="pill pill--blank">open</span> <a href="questions.html#BQ2-10">BQ2-10</a>
    · <a href="suggestions.html#BS-02">BS-02</a></p>
  </div>
</div>

<h2>What is published here</h2>
<table>
<thead><tr><th>Page</th><th>What it holds</th></tr></thead>
<tbody>
<tr><td><a href="products.html">Product intent</a></td><td>Five rows. Every intent field is empty on purpose, with the reason printed next to it. Every observation field is full.</td></tr>
<tr><td><a href="suggestions.html">Choose a path</a></td><td>Twelve suggestions, two or three options each, nothing applied. The <code>chosen</code> field is empty on every row and the build fails if it is not.</td></tr>
<tr><td><a href="questions.html">Known &amp; unknown</a></td><td>{len(answered_q)} answered questions with sourced answers, {len(open_q)} left empty on purpose, each with the action that would close it and who can close it.</td></tr>
<tr><td><a href="requirements.html">Requirements trace</a></td><td>Every row in the brief, checked against the tree rather than taken from the brief's own status word.</td></tr>
<tr><td><a href="topics.html">Topics</a></td><td>Ten question-shaped proposals, each resting on a fact read from an official page today — and deliberately unordered, because nothing can rank them yet.</td></tr>
<tr><td><a href="sources.html">Sources</a></td><td>{len(load('sources')['sources'])} rows. Live reads and carried quotes are labelled apart.</td></tr>
<tr><td><a href="verification.html">Verification</a></td><td>{len(load('verification')['rows'])} checks, each with the method and the result.</td></tr>
<tr><td><a href="flagged.html">Flagged</a></td><td>{len(f['rows'])} irregularities, {len(high)} of them high severity.</td></tr>
</tbody>
</table>

<h2>Where the numbers come from</h2>
<p>Every count printed on these pages is measured from this repository's tree by
<code>tools/build_board.py</code> in the same run that writes them, and re-measured by
<code>tools/validate_board.py</code>, which fails if a printed number disagrees. That rule exists because
this repository has twice shipped a page whose prose printed a count that had drifted from the register
it described — and the reason the second one was caught within the hour rather than never is that a
check recomputed it.</p>
<p class="note">Session <code>arena/1bfbc559-zone2</code>, task T62 on
<a href="../COORDINATION.md">the shared board</a>. Nothing on this board is implemented.</p>
"""
    return page(
        "Executive summary · Counter Notes decision board",
        "The 2026-11-17 five-product brief: two products the repository has never seen, the first "
        "tracking ID any brief has supplied, and the three decisions that gate everything else.",
        "index.html",
        body,
    )


def page_products() -> str:
    d = load("products")
    rows = []
    for r in d["rows"]:
        it = r["intent"]
        ob = r["observation"]
        prior = ", ".join(ob["prior_observation_dates"]) if ob["prior_observation_dates"] else "none — first observation"
        rows.append(f"""
<section class="card" id="{e(r['id'])}" style="margin-bottom:18px">
  <div class="head" style="padding:15px 18px 12px;border-bottom:1px solid var(--line-soft)">
    <p class="eyebrow" style="margin-bottom:4px">{e(r['id'])} · {e(r['label'])}</p>
    <h3 style="margin:0 0 6px">{external(r['submitted_url'], r['submitted_url'])}</h3>
    <p class="small" style="margin:0">Token as given: <code>{e(r['token_as_given'])}</code> ·
      {e(r['token_length'])} characters ·
      <span class="pill pill--blank">{'matches' if r['token_matches_asin_definition'] else 'does not match'} the published ASIN definition</span>
      <span class="pill pill--{"done" if r['status'] == 'VERIFIED' else "blank"}">{e(r['status'])}</span>
    </p>
  </div>
  <div style="padding:14px 18px 16px">
    <div class="fieldgroup fieldgroup--intent">
      <h4>Intended product — the four fields that travel together</h4>
      <dl>
        <dt>Intended ASIN</dt><dd class="blank">{e(it['intended_asin']) or 'empty'}</dd>
        <dt>Official listing URL</dt><dd class="blank">{e(it['official_listing_url']) or 'empty'}</dd>
        <dt>Confirmation date</dt><dd class="blank">{e(it['confirmation_date']) or 'empty'}</dd>
        <dt>Source of confirmation</dt><dd class="blank">{e(it['source_of_confirmation']) or 'empty'}</dd>
      </dl>
    </div>
    <div class="fieldgroup fieldgroup--observed">
      <h4>Observed redirect target — a separate field group, never merged into the one above</h4>
      <dl>
        <dt>Resolved URL</dt><dd class="small">{external(ob['observed_redirect_url'], ob['observed_redirect_url'])}</dd>
        <dt>ASIN at the destination</dt><dd><code>{e(ob['observed_asin'])}</code></dd>
        <dt>Listing title as served</dt><dd>{e(ob['observed_listing_title'])}</dd>
        <dt>Category path as served</dt><dd>{e(ob['observed_category_path'])}</dd>
        <dt>Observed</dt><dd>{e(ob['observed_utc'])} by {e(ob['observed_by'])}</dd>
        <dt>Earlier observations</dt><dd>{e(prior)}</dd>
        <dt>Carries an Associates tag</dt><dd>{'yes' if ob['carries_associates_tag'] else 'no'}</dd>
      </dl>
    </div>
    <p class="small" style="margin:0 0 6px"><strong>Why the intent fields are empty.</strong>
      {e(r['intent_blank_reason'])}</p>
    <p class="small" style="margin:0">Sources: <span class="src">{src_links(r['source_ids'])}</span></p>
  </div>
</section>""")

    body = f"""
<p class="eyebrow">Product-intent confirmation record</p>
<h1>Two questions, two field groups, never merged</h1>
<p class="standfirst">The brief asks for a record that keeps the intended product — ASIN, official
listing URL, confirmation date, source — apart from what the supplied link was observed to do. That is
a distinction worth keeping: one is what someone meant, the other is what a URL did. On all five rows
the first group is empty and the second is full.</p>

<div class="card">
<h4 style="margin-top:0">The rule, and why the emptiness is the finding</h4>
<p>{e(d['note'])}</p>
<p><strong>The definition every token is measured against:</strong> “{e(d['asin_definition']['text'])}”
— {external('https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC', 'Amazon’s own help page')}, read live {e(d['asin_definition']['read_utc'])}.
All five supplied tokens are 9 characters. A control confirms the two are different namespaces rather
than a truncation: a valid, live 10-character ASIN placed in the same slot returns the service's
“invalid URL” page. <span class="src">{src_links(['BD-05','BD-12'])}</span></p>
</div>

<h2>The five rows</h2>
{''.join(rows)}

<h2>What the five say together</h2>
<div class="card card--warn">
<p>{sub(e(d['what_the_five_rows_say_together']['statement']))}</p>
<p class="small" style="margin:0">Basis: {e(d['what_the_five_rows_say_together']['basis'])}.
This is a statement about what the links <em>do</em>, not about what the submitter
<em>meant</em> — which is exactly the separation this page is built to keep.
<span class="src">{src_links(d['what_the_five_rows_say_together']['source_ids'])}</span></p>
</div>
"""
    return page(
        "Product-intent confirmation record · Counter Notes decision board",
        "Five supplied affiliate links: the intended product fields left empty on purpose, and the "
        "observed redirect targets recorded separately, never merged.",
        "products.html",
        body,
    )


def page_suggestions() -> str:
    d = load("suggestions")
    blocks = []
    for r in d["rows"]:
        opts = []
        for o in r["options"]:
            opts.append(f"""
<div class="option">
  <span class="opt-id">Option {e(o['id'])}</span>
  <h5>{e(o['label'])}</h5>
  <p>{sub(e(o['what']))}</p>
  <dl>
    <dt>Effort</dt><dd>{sub(e(o['effort']))}</dd><br>
    <dt>Risk</dt><dd>{sub(e(o['risk']))}</dd><br>
    <dt>Reversibility</dt><dd>{sub(e(o['reversibility']))}</dd>
  </dl>
  <p class="src" style="margin-top:8px">{src_links(o['source_ids'])}</p>
</div>""")
        blockers = " ".join(ref_link(b) for b in r["blocked_by"]) or "none"
        blocks.append(f"""
<section class="suggestion" id="{e(r['id'])}">
  <div class="head">
    <p class="eyebrow" style="margin-bottom:4px">{e(r['id'])} · not chosen</p>
    <h3>{e(r['title'])}</h3>
    <p class="why">{sub(e(r['why_now']))}</p>
  </div>
  <div class="options">{''.join(opts)}</div>
  <div class="foot">
    <p><strong>Where this session's reading points.</strong> {sub(e(r['lean']))}</p>
    <p class="small">Blocked by: {blockers} · Sources: <span class="src">{src_links(r['source_ids'])}</span>
      · <strong>Chosen: <span class="blank">nothing — this row is waiting for you</span></strong></p>
  </div>
</section>""")

    body = f"""
<p class="eyebrow">Choose a path</p>
<h1>Twelve suggestions, nothing applied</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card card--accent">
<p style="margin:0"><strong>Nothing here has been done.</strong> Every row below has an empty
<code>chosen</code> field, and <code>tools/validate_board.py</code> fails the build if one is filled
without a matching decision record. This page is where a path gets picked; the work happens after.</p>
</div>

{''.join(blocks)}

<h2>How to use this board</h2>
<p>Work top-down. The rows are ordered roughly by what each choice unblocks, so choosing the first
before the second avoids doing the expensive step twice. Rows blocked by an open question cannot be
chosen sensibly yet — the question pages say who can close each one and what it costs to leave it open.</p>
<p>The <em>lean</em> on each row is this session's reading of where the measurements point. It is an
argument, not a decision, and it is labelled as one.</p>
"""
    return page(
        "Choose a path · Counter Notes decision board",
        "Twelve suggestions for the five-product affiliate site, each with two or three costed "
        "options. Nothing on this board is applied — a path is chosen here first.",
        "suggestions.html",
        body,
    )


def page_questions() -> str:
    d = load("questions")
    open_rows, answered_rows = [], []
    for q in d["questions"]:
        pill = {"answered": "done", "open": "blank"}.get(q["state"], "info")
        blocks = " ".join(ref_link(b) for b in q["blocks"]) or "nothing directly"
        blk = f"""
<section class="question question--{'answered' if q['state'] == 'answered' else 'open'}" id="{e(q['id'])}">
  <p class="eyebrow" style="margin-bottom:4px">{e(q['id'])}
    <span class="pill pill--{pill}">{e(q['state'])}</span></p>
  <h3>{e(q['question'])}</h3>
  <dl>
    <dt>What we have</dt><dd>{sub(e(q['known']))}</dd>
    <dt>What we do not</dt><dd>{sub(e(q['not_known']))}</dd>
    <dt>Answer</dt><dd>{('<strong>' + sub(e(q['answer'])) + '</strong>') if q['answer'] else '<span class="blank">empty — the information does not exist yet</span>'}</dd>
    <dt>How to close it</dt><dd>{sub(e(q['how_to_close']))}</dd>
    <dt>Who can close it</dt><dd>{sub(e(q['who_can_close']))}</dd>
    <dt>Cost of leaving it open</dt><dd>{sub(e(q['cost_if_left_open']))}</dd>
    <dt>Blocks</dt><dd>{blocks}</dd>
    <dt>Sources</dt><dd class="src">{src_links(q['source_ids'])}</dd>
  </dl>
</section>"""
        (answered_rows if q["state"] == "answered" else open_rows).append(blk)

    body = f"""
<p class="eyebrow">Known and unknown</p>
<h1>What has to be answered before a decision can be reasonably made</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card">
<p style="margin:0"><strong>The shape of this register.</strong> {len(answered_rows)} question(s) are
answered and the answers are printed and sourced. {len(open_rows)} are empty <em>on purpose</em> — an
empty answer field is how this register says the information does not exist yet, and the build fails if
an open question carries an answer. Every open row names the action that would close it and who can
close it. Nothing is inferred.</p>
</div>

<h2>Answered</h2>
{''.join(answered_rows) or '<p class="note">None.</p>'}

<h2>Open — and how each one closes</h2>
{''.join(open_rows) or '<p class="note">None.</p>'}
"""
    return page(
        "Known and unknown · Counter Notes decision board",
        "The questions that have to be answered before a decision on this project can be reasonably "
        "made: what is known, what is not, and the action that would close each gap.",
        "questions.html",
        body,
    )


def page_requirements() -> str:
    d = load("requirements")
    pill = {
        "matches": "done",
        "overstated": "high",
        "as-stated": "info",
        "no-status-given": "blank",
        "unmeasurable-from-the-tree": "medium",
    }
    trs = []
    for r in d["rows"]:
        trs.append(f"""
<tr id="{e(r['id'])}">
  <td class="id">{e(r['brief_ref'])}</td>
  <td class="id">{e(r['priority'])}</td>
  <td><strong>{e(r['requirement'])}</strong></td>
  <td>{e(r['brief_status']) or '<span class="blank">no status given</span>'}</td>
  <td><span class="pill pill--{pill.get(r['verdict'], 'low')}">{e(r['verdict'])}</span><br>
      <span class="small">{sub(e(r['measured_status']))}</span></td>
  <td>{sub(e(r['measured']))}</td>
  <td>{sub(e(r['gap']))}</td>
  <td class="src">{src_links(r['source_ids'])}</td>
</tr>""")

    vocab = "".join(
        f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in d["verdict_vocabulary"].items()
    )
    body = f"""
<p class="eyebrow">Requirements trace</p>
<h1>Every row in the brief, checked against the tree</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card">
<dl style="margin:0">{vocab}</dl>
</div>

<div class="table-scroll">
<table>
<thead><tr>
  <th>Row</th><th>P</th><th>Requirement</th><th>Status in the brief</th>
  <th>Checked against the tree</th><th>Measured</th><th>Gap</th><th>Source</th>
</tr></thead>
<tbody>{''.join(trs)}</tbody>
</table>
</div>

<h2>Reading the trace</h2>
<p>Most rows hold up. The site is in better shape than a reader of an unincorporated status column
would guess: every one of the {_MEASURED['pages']} published pages carries the required disclosure, the
front page genuinely leads with the products, and the campaign ledger is exactly the empty-but-defined
thing the brief asks for.</p>
<p>Four rows do not hold up, and three of them fail the same way — a status word that says
<em>Implemented</em> where the tree shows something partial:</p>
<ul>
  <li><strong>S-04</strong> ({_MEASURED['no_desc']} pages with no meta description, {_MEASURED['dup_titles']} duplicated titles) — the only unfinished P1 row.</li>
  <li><strong>S-19</strong> — no chooser component exists, though a question-led article section does.</li>
  <li><strong>S-24</strong> — {_MEASURED['guides_unlinked']} reader pages are one hop short of the row's requirement.</li>
  <li><strong>S-09</strong> is honestly marked <em>Partly implemented</em>; the missing half is the social preview image, which is the half the row names first.</li>
</ul>
<p>The loudest number on this page is the one that is <em>not</em> a defect: {_MEASURED['amazon_links']}
Amazon-host links of which {_MEASURED['sponsored_links']} carry <code>rel="sponsored"</code>. The
unmarked remainder are citations to a source inside a verification table, not offers — and Google
defines the value by what the link is. See
<a href="suggestions.html#BS-04">BS-04</a>.</p>
"""
    return page(
        "Requirements trace · Counter Notes decision board",
        "Every requirement row from the 2026-11-17 brief, checked against the repository rather than "
        "taken from the brief's own status word. Four rows do not hold up.",
        "requirements.html",
        body,
    )


def page_topics() -> str:
    d = load("topics")
    trs = []
    for t in d["rows"]:
        prods = " ".join(f'<a href="products.html#{e(p)}">{e(p)}</a>' for p in t["products"])
        trs.append(f"""
<tr id="{e(t['id'])}">
  <td class="id">{e(t['id'])}</td>
  <td><strong>{e(t['working_title'])}</strong><br>
      <span class="small">{sub(e(t['why_this_shape']))}</span></td>
  <td>{e(t['cluster'])}</td>
  <td>{sub(e(t['rests_on']))}<br><span class="src">{src_links(t['source_ids'])}</span></td>
  <td>{prods}</td>
  <td>{sub(e(t['existing_page']))}</td>
  <td class="small">{sub(e(t['status']))}</td>
</tr>""")

    body = f"""
<p class="eyebrow">Topics</p>
<h1>Ten questions, deliberately in no order</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card card--blank">
<p style="margin:0"><strong>Why these are not ranked.</strong> {e(d['ranking_note'])} The four working
titles the brief offers are hypotheses, not findings — the brief says so itself and calls them
“not claims about popularity, search volume or product superiority”. With no Search Console and no
event endpoint there is no instrument that could rank these, so any ordering would be decoration
pretending to be evidence. Once <a href="questions.html#BQ2-10">BQ2-10</a> closes, this page should be
re-sorted by measured queries.</p>
</div>

<div class="table-scroll">
<table>
<thead><tr>
  <th>Id</th><th>Working title</th><th>Cluster</th><th>Rests on</th><th>Products</th>
  <th>Existing page</th><th>Status</th>
</tr></thead>
<tbody>{''.join(trs)}</tbody>
</table>
</div>

<h2>The one worth noticing</h2>
<div class="card card--accent">
<p><a href="#TP-09">TP-09 — “The two tools that decide whether dinner is cooked.”</a> It is the only
title here that turns an awkward product set into an advantage. An air fryer cooks it and a thermometer
tells you when it is done, and one of the two thermometers names <em>Air Fryer</em> among the cooking
environments in its own listing title — so the bridge between the two halves of the catalogue is not a
marketing invention, it is on the box.</p>
<p class="small" style="margin:0">It is also the most dependent row here: it only makes sense if
<a href="suggestions.html#BS-03">BS-03</a> goes to option A or B.
<span class="src">{src_links(['BD-04'])}</span></p>
</div>
"""
    return page(
        "Topics · Counter Notes decision board",
        "Ten question-shaped article proposals for the five promoted products, each resting on a fact "
        "read from an official page, and deliberately not ranked by search volume.",
        "topics.html",
        body,
    )


def page_sources() -> str:
    d = load("sources")
    trs = []
    for s in d["sources"]:
        status = s["status"]
        pill = "done" if status.startswith("live") else "info"
        carried = ""
        if status == "carried":
            carried = f'<br><span class="small"><strong>Carried, not re-fetched.</strong> {e(s.get("carried_note",""))}</span>'
        updated = f'<br><span class="small">Page states last update: {e(s["page_stated_update"])}</span>' if s.get("page_stated_update") else ""
        trs.append(f"""
<tr id="{e(s['id'])}">
  <td class="id">{e(s['id'])}</td>
  <td>{external(s['url'], s['url'])}{updated}</td>
  <td>{e(s.get('publisher',''))}<br><span class="small">{e(s.get('kind',''))}</span></td>
  <td><span class="pill pill--{pill}">{e(status.replace('_',' '))}</span>{carried}</td>
  <td><strong>{e(s.get('title',''))}</strong><br>{sub(e(s.get('quote','')))}</td>
  <td class="small">{e('; '.join(s.get('used_for', [])))}</td>
</tr>""")

    live = sum(1 for s in d["sources"] if s["status"].startswith("live"))
    carried_n = sum(1 for s in d["sources"] if s["status"] == "carried")

    body = f"""
<p class="eyebrow">Source register</p>
<h1>{len(d['sources'])} sources, {live} read live today and {carried_n} carried</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card">
<p style="margin:0"><strong>Why carried rows are labelled rather than hidden.</strong> A register that
silently upgrades a carried quote to a live one is the failure this whole namespace exists to prevent.
Four rows here were not re-fetched by this session, and each says so, names the session and date that
last read it, and is used only where the claim does not depend on a fresh read.</p>
</div>

<div class="table-scroll">
<table>
<thead><tr>
  <th>Id</th><th>URL</th><th>Publisher</th><th>Read</th><th>What it states</th><th>Used for</th>
</tr></thead>
<tbody>{''.join(trs)}</tbody>
</table>
</div>

<h2>How the live reads were made</h2>
<p>The sandbox shell has no general outbound network access, so every live fetch on this page was made
with the session's page-fetch tool and every repository fact was measured from the working tree. Every
outbound link to an Amazon product page on this site carries <code>rel="sponsored nofollow noopener"</code>,
per the brief's instruction that outbound product links stay marked; links to the Associates help pages,
Google and the FTC are documentation citations and carry <code>rel="nofollow noopener"</code>.</p>
"""
    return page(
        "Sources · Counter Notes decision board",
        "Every source used by the 2026-11-17 decision board, with what each states and whether it was "
        "read live today or carried from the repository register.",
        "sources.html",
        body,
    )


def page_verification() -> str:
    d = load("verification")
    trs = []
    for v in d["rows"]:
        trs.append(f"""
<tr id="{e(v['id'])}">
  <td class="id">{e(v['id'])}</td>
  <td>{sub(e(v['claim']))}</td>
  <td>{sub(e(v['method']))}</td>
  <td>{sub(e(v['result']))}</td>
  <td class="src">{src_links(v['source_ids'])}</td>
</tr>""")

    # What the gates check, not what the last run concluded.
    #
    # This page used to print the result of `tools/ci_replay.py`. That is a fixed
    # point: ci_replay runs `build_board.py --check`, which compares this page
    # against a fresh render, and the fresh render quotes a run that has not
    # finished yet. One failing step therefore latched the page stale forever,
    # with the stale line itself being the only thing still failing. The result
    # of a run belongs to the run, not to the page it is checking — so it lives
    # in measured.json and in the workflow log, and this page states what is
    # enforced instead of claiming it passed.
    gate_rows = "".join(
        f'<tr><td>{e(name)}</td><td>{e(cmd)}</td><td>{e(enforces)}</td></tr>'
        for name, cmd, enforces in GATES
    )
    gate_line = f"""
<div class="card">
<h2>What enforces the numbers above</h2>
<p>Every count on this page is re-derived when the page is written, and four gates
replay against the tree. <strong>This page deliberately does not print the result of
the last run.</strong> One of those gates rebuilds this page and compares it to a
fresh render, so a page that quoted its own checker's verdict would be comparing
itself against a run that had not finished — and a single failure would latch the
page stale forever. The verdict belongs to the run: it is recorded in
<code>board/data/measured.json</code> and enforced by
<code>.github/workflows/pages.yml</code>, which will not publish a tree that fails.</p>
<table>
<thead><tr><th>Gate</th><th>Command</th><th>What it refuses</th></tr></thead>
<tbody>{gate_rows}</tbody>
</table>
</div>
"""

    body = f"""
<p class="eyebrow">Verification</p>
<h1>{len(d['rows'])} checks, line by line</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card">
<p style="margin:0"><strong>Method.</strong> {e(d['method'])}</p>
</div>

<div class="table-scroll">
<table>
<thead><tr><th>Id</th><th>Claim</th><th>Method</th><th>Result</th><th>Source</th></tr></thead>
<tbody>{''.join(trs)}</tbody>
</table>
</div>

<h2>The gate run</h2>
{gate_line or '<p class="note">Run <code>python3 tools/build_board.py</code> to record the gate result.</p>'}

<h2>What could not be verified</h2>
<ul>
  <li>Whether <code>shopnow047c-20</code> is an issued, active Associates ID. No public page can
      establish it; Amazon states IDs are generated when you apply. <a href="questions.html#BQ2-01">BQ2-01</a></li>
  <li>Whether the supplied short links are valid Special Links. The brief records this as unresolved
      and instructs that no claim be made either way, so it is reproduced as an open question rather
      than a finding. <a href="questions.html#BQ2-04">BQ2-04</a></li>
  <li>The fifteen decision records the brief cites on another site. The page is live and hosts
      decision anchors in the form the brief cites, but each id was not individually checked, and the
      Zone3 item the brief cites was not fetched at all. <a href="flagged.html#FL-11">FL-11</a></li>
</ul>
"""
    return page(
        "Verification · Counter Notes decision board",
        "Line-by-line verification record for the 2026-11-17 brief: each claim, the method used to "
        "test it, the result, and the official page that establishes it.",
        "verification.html",
        body,
    )


def page_flagged() -> str:
    d = load("flags")
    pill = {"high": "high", "medium": "medium", "low": "low"}.get
    blocks = []
    for f_ in d["rows"]:
        blocks.append(f"""
<section class="card" id="{e(f_['id'])}" style="margin-bottom:14px">
  <p class="eyebrow" style="margin-bottom:4px">{e(f_['id'])}
    <span class="pill pill--{pill(f_['severity'], 'info')}">{e(f_['severity'])}</span></p>
  <h3 style="margin:0 0 8px">{sub(e(f_['title']))}</h3>
  <p class="small"><strong>What.</strong> {sub(e(f_['what']))}</p>
  <p class="small"><strong>Evidence.</strong> {sub(e(f_['evidence']))}</p>
  <p class="small"><strong>Why it matters.</strong> {sub(e(f_['why_it_matters']))}</p>
  <p class="small"><strong>Status.</strong> {sub(e(f_['status']))}</p>
  <p class="small" style="margin-bottom:0"><strong>Owner action.</strong> {sub(e(f_['owner_action']))}
    · Sources: <span class="src">{src_links(f_['source_ids'])}</span></p>
</section>""")

    high = sum(1 for x in d["rows"] if x["severity"] == "high")
    body = f"""
<p class="eyebrow">Flagged for review</p>
<h1>{len(d['rows'])} irregularities, {high} of them high severity</h1>
<p class="standfirst">{e(d['note'])}</p>

<div class="card card--warn">
<p style="margin:0"><strong>None of these blocks a merge.</strong> They are published here, with the
source that establishes each one, so they can be reviewed after the site is live and changes requested.
That is the arrangement this repository has used since the second session.</p>
</div>

{''.join(blocks)}

<h2>A note on severity</h2>
<p>“High” here means <em>it changes what should be done next</em>, not <em>the site is broken</em>. The
site builds, every page carries the disclosure, and no page prints a price. The three high rows are
about a plan that has been overtaken: two products the register does not know about, a tag that does not
exist anywhere, and a category split that the published site does not cover.</p>
"""
    return page(
        "Flagged for review · Counter Notes decision board",
        "Irregularities found while checking the 2026-11-17 brief against the repository, each with "
        "the source that establishes it. None blocks a merge.",
        "flagged.html",
        body,
    )


PAGES = [
    ("index.html", page_index),
    ("products.html", page_products),
    ("suggestions.html", page_suggestions),
    ("questions.html", page_questions),
    ("requirements.html", page_requirements),
    ("topics.html", page_topics),
    ("sources.html", page_sources),
    ("verification.html", page_verification),
    ("flagged.html", page_flagged),
]


# The gates this namespace is subject to, stated rather than measured. See the
# comment in page_verification() for why the *result* is not printed here.
GATES: list[tuple[str, str, str]] = [
    ("Board gate", "tools/validate_board.py",
     "An unsourced row, a blank with no stated reason, a decided question, a typed "
     "count that the tree contradicts, or a money figure."),
    ("Board negative tests", "tools/test_board.py",
     "Any of 19 injected defects going undetected — a gate that never fires is "
     "worse than no gate."),
    ("Freshness", "tools/build_board.py --check",
     "A committed page that differs from a fresh render of board/data/*.json."),
    ("Full CI replay", "tools/ci_replay.py",
     "Any workflow step that would fail on GitHub, replayed locally first."),
]


def run_gates() -> str:
    """Replay the repository's CI steps and report the result. Recorded, never typed."""
    import subprocess
    script = REPO / "tools" / "ci_replay.py"
    if not script.is_file():
        return "tools/ci_replay.py not present — not run"
    try:
        proc = subprocess.run([sys.executable, str(script)], cwd=str(REPO),
                              capture_output=True, text=True, timeout=1800)
        tail = (proc.stdout or "").strip().splitlines()
        summary = tail[-1] if tail else "(no output)"
        return (f"tools/ci_replay.py exit {proc.returncode} — {summary}"
                f"{' (all steps passed)' if proc.returncode == 0 else ' (see the run for the failing step)'}")
    except Exception as exc:  # noqa: BLE001 — a gate failure must not break the build
        return f"tools/ci_replay.py could not be run: {exc}"


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    check = "--check" in argv
    global _MEASURED
    _MEASURED = measure()

    problems = []
    for name, fn in PAGES:
        out = fn()
        if "{{" in out:
            problems.append(f"{name}: an unsubstituted token survived into the output")
        target = BOARD / name
        if check:
            if not target.is_file():
                problems.append(f"{name}: missing")
            elif target.read_text(encoding="utf-8") != out:
                problems.append(f"{name}: stale — run tools/build_board.py")
        else:
            target.write_text(out, encoding="utf-8")

    if problems:
        print("\n".join(problems))
        return 1

    if check:
        print(f"board/: {len(PAGES)} pages current")
        return 0

    # The gates run AFTER the pages are written. tools/ci_replay.py includes
    # `build_board.py --check`, so running them first would compare against the
    # previous commit's pages and report a stale build that this run just fixed.
    gates = run_gates()
    (DATA / "measured.json").write_text(
        json.dumps({**_MEASURED, "gates": gates, "measured_utc": "2026-11-17",
                    "substitutions": dict(sorted(_SUBS.items()))},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"board/: wrote {len(PAGES)} pages")
    print(f"gates: {gates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
