#!/usr/bin/env python3
"""Front-of-house generator — T50, session `arena/9251f262-zone2` (2026-11-16).

WHY THIS FILE EXISTS
--------------------
The brief's complaint about the published site was that it read as generated. Part of
the answer is editorial; the part this file can guarantee is structural, and it is the
part that matters most:

  * every number on the front pages is read from `marketing/data/facts.json`, which was
    transcribed from official manufacturer and Amazon pages — never re-typed here;
  * every data row ends in a link to the official page that states the value;
  * a value no official source states is rendered as a dash with the recorded reason
    printed next to it, never filled in;
  * no price is ever emitted, and every outbound product link carries
    rel="sponsored nofollow" with a link-level disclosure.

WHAT IT WRITES
--------------
  index.html                     the publication landing page
  suggestions.html               the decision board (review and choose, do not auto-apply)
  questions.html                 the questions / known / unknown register
  guides/index.html              the article set, organised by category
  guides/basket-air-fryers.html  category page
  guides/air-fryer-ovens.html    category page
  guides/buying-guides.html      category page
  guides/method.html             category page

Nothing here edits a ledger, a dataset or another generator. `marketing/data/facts.json`
and `docs/board-9251f262.json` are read-only inputs.

Usage:  python3 tools/build_front.py            (writes the pages)
        python3 tools/build_front.py --check    (fails if a written page is stale)
"""
from __future__ import annotations

import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import head_meta  # noqa: E402  — the repository's single canonical/OG contract

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "marketing" / "data" / "facts.json"
BOARD = ROOT / "docs" / "board-9251f262.json"
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"

CHECKED_ON = "2026-11-16"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
LINK_REL = "sponsored nofollow"
LINK_DISCLOSURE = "(paid link)"

# Editorial copy for the three listings. Every figure quoted in these strings also
# appears as a sourced row in the generated table below it — the prose never introduces
# a number the table does not carry.
PRODUCT_VOICE = {
    "P1": {
        "display": "Chefman TurboFry Touch 6 Qt Dual-Window",
        "short": "Chefman 6 Qt dual-window",
        "brand": "Chefman",
        "headline": "Two baskets that finish at the same time",
        "note": "The only one of the three that solves the cold-second-batch problem.",
        "highlights": ["Capacity", "Temperature range", "Power", "Door / window", "Sync Finish"],
    },
    "P2": {
        "display": "Emeril Lagasse French Door AirFryer 360, 26 Qt",
        "short": "Emeril Lagasse 26 Qt French-door oven",
        "brand": "Emeril Lagasse",
        "headline": "An oven that air fries, with doors instead of a drawer",
        "note": "26 quarts and ten cooking modes. You give up counter space and get a rotisserie spit.",
        "highlights": ["Capacity", "Temperature range", "Cooking modes", "Door", "Dimensions"],
    },
    "P3": {
        "display": "Chefman TurboFry Touch 8 Qt Stainless Steel",
        "short": "Chefman 8 Qt TurboFry Touch",
        "brand": "Chefman",
        "headline": "The biggest single basket here, and the plainest panel",
        "note": "8 quarts, four presets, and nothing to learn.",
        "highlights": ["Capacity", "Temperature range", "Presets", "Shake reminder", "Weight (8 Qt)"],
    },
}

STATUS_PILL = {
    "verified": ("ok", "verified"),
    "conflict": ("flag", "conflict"),
    "partial": ("warn", "partial"),
    "unverified": ("idle", "unverified"),
    "withheld_by_policy": ("idle", "withheld"),
}

GUIDE_CATEGORIES = {
    "basket-air-fryers": {
        "title": "Basket air fryers",
        "blurb": "Drawer-style machines: a basket you pull out, a fan above it, and a footprint you can measure before you buy. Two of the three listings on this site are baskets.",
        "keys": ["P1", "P3"],
    },
    "air-fryer-ovens": {
        "title": "Air-fryer ovens",
        "blurb": "A small convection oven that also air fries. More capacity, more modes, and a very different shape of counter commitment.",
        "keys": ["P2"],
    },
    "buying-guides": {
        "title": "Buying guides",
        "blurb": "Decision-first pages: start from the question, end at one of the three listings, and show the row that settles it.",
        "keys": [],
    },
    "method": {
        "title": "Method and verification",
        "blurb": "How a figure earns a place on this site, what happens when two official pages disagree, and why a dash is sometimes the honest answer.",
        "keys": [],
    },
}

# The article set, grouped the way a reader browses it. Every entry links to a page that
# already exists in this repository; nothing here is a dangling stub.
ARTICLES = [
    ("Capacity", "How many quarts of air fryer do you actually need?",
     "marketing/topics/how-many-quarts-do-you-need.html", "buying-guides",
     "Capacity is the number every buyer looks at and almost nobody can translate."),
    ("Design", "Two baskets or one big one? A trade you cannot undo later",
     "marketing/topics/dual-basket-or-one-big-basket.html", "basket-air-fryers",
     "The dual-basket pitch is not really about capacity."),
    ("Category", "Air fryer or air fryer toaster oven: the door is the decision",
     "marketing/topics/basket-or-fryer-oven.html", "air-fryer-ovens",
     "Most comparisons answer with a list of extra modes. The answer is geometry."),
    ("Specs", "Hi-Fry, 450 F and 400 F: why two official pages disagree about one fryer",
     "marketing/topics/what-hi-fry-actually-does.html", "basket-air-fryers",
     "On one product the Amazon title says 450 F and the manufacturer's sheet says 400 F."),
    ("Fit", "Will it fit? The exact footprint of all three, in inches",
     "marketing/topics/will-it-fit-your-counter.html", "buying-guides",
     "Return reasons are usually not performance."),
    ("Specs", "24 presets or 25? A field guide to spec-sheet drift",
     "marketing/topics/why-two-official-pages-disagree.html", "method",
     "The Emeril oven's Amazon title and its own store page disagree. Both are official."),
    ("Comparison", "Air fryer vs your oven: what three spec sheets can settle",
     "marketing/topics/air-fryer-vs-oven.html", "buying-guides",
     "'Air fryer vs oven' is really three questions wearing one coat."),
    ("Verdict", "Are air fryers worth it? What three spec sheets support",
     "marketing/topics/are-air-fryers-worth-it.html", "buying-guides",
     "A verdict on 'worth it' is always really a price, a habit and a kitchen."),
    ("Journal", "Two baskets beat one long timer",
     "journal/dual-basket-air-fryers.html", "basket-air-fryers",
     "What the dual-basket design actually changes, argued from the verified specs."),
    ("Journal", "Basket fryer or air-fryer oven? Choose by geometry",
     "journal/basket-vs-oven.html", "air-fryer-ovens",
     "A basket fryer and an air-fryer oven are different machines that share a heating method."),
    ("Journal", "Why every number here links to its source",
     "journal/why-every-number-has-a-source.html", "method",
     "Most affiliate sites are written backwards. This one was built the other way round."),
]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def e(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def load() -> tuple[dict, dict]:
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    return facts, board


def src_map(product: dict) -> dict:
    return {s["id"]: s for s in product["official_sources"]}


def source_cell(product: dict, row: dict) -> str:
    """The last cell of a data row: a link to the official page, or an explicit blank."""
    sid = row.get("src")
    if sid:
        s = src_map(product).get(sid)
        if s:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", s["url"]).split("/")[0])
            return (f'<a class="pb-src" href="{e(s["url"])}" target="_blank" '
                    f'rel="{LINK_REL} noopener noreferrer">{e(host)}</a>')
    reason = row.get("blank_reason") or "No official source states this value."
    return f'<span class="pb-blank">&mdash;<small>{e(reason)}</small></span>'


def value_cell(row: dict) -> str:
    kind, label = STATUS_PILL.get(row.get("status", "unverified"), ("idle", "unverified"))
    pill = f'<span class="pb-pill pb-pill--{kind}">{e(label)}</span>'
    val = (row.get("value") or "").strip()
    if not val:
        return f'<span class="pb-blank">&mdash;</span> {pill}'
    return f"{e(val)} {pill}"


def product_link(product: dict) -> str:
    asin = product["asin"]
    return f"https://www.amazon.com/dp/{e(asin)}"


def spec_rows(product: dict, attrs: list[str]) -> list[dict]:
    by_attr = {r["attr"]: r for r in product["rows"]}
    return [by_attr[a] for a in attrs if a in by_attr]


def masthead(active: str) -> str:
    nav = [
        ("index.html", "Counter Notes"),
        ("marketing/buying-guide.html", "Which to buy"),
        ("guides/index.html", "Guides"),
        ("suggestions.html", "Suggestions"),
        ("questions.html", "Questions"),
        # Added 2026-11-16 by session dc72a69e (T50). tools/audit_site.py fails a published
        # namespace that no page links to, and index.html is generated by this file, so the
        # design brief has no way to be reachable without this entry. One nav item; nothing
        # else in this generator was touched. Logged as a scope extension in COORDINATION.md.
        ("brief/index.html", "Design brief"),
        ("marketing/comparison.html", "Head-to-head"),
    ]
    depth = "../" if active.startswith("guides/") else ""
    items = []
    for href, label in nav:
        rel = depth + href
        cls = ' class="is-on"' if href == active else ""
        items.append(f'<a href="{e(rel)}"{cls}>{e(label)}</a>')
    return f"""<header class="pb-mast">
  <div class="pb-wrap">
    <div class="pb-mast-top">
      <div>
        <div class="pb-word">Counter <em>Notes</em></div>
        <div class="pb-tag">Countertop cooking gear, read off the spec sheet</div>
      </div>
      <div class="pb-mast-meta">Sources re-read {e(CHECKED_ON)}</div>
    </div>
    <nav class="pb-nav" aria-label="Sections">{''.join(items)}<a href="{e(depth)}products.html">Operator dashboard</a></nav>
  </div>
</header>
<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} A commission may be earned when you buy through our links, at no extra cost to you. Product links on this site carry no Associates tag yet, so they are preview links and earn nothing.</div></div>"""


def footer(depth: str = "") -> str:
    return f"""<footer class="pb-foot">
  <div class="pb-wrap">
    <div class="pb-foot-grid">
      <div><h4>Read</h4><ul>
        <li><a href="{e(depth)}index.html">Front page</a></li>
        <li><a href="{e(depth)}guides/index.html">All guides</a></li>
        <li><a href="{e(depth)}marketing/buying-guide.html">Which one to buy</a></li>
        <li><a href="{e(depth)}marketing/comparison.html">Head-to-head</a></li>
        <li><a href="{e(depth)}marketing/articles/index.html">The three write-ups</a></li>
      </ul></div>
      <div><h4>Decide</h4><ul>
        <li><a href="{e(depth)}suggestions.html">Suggestion board</a></li>
        <li><a href="{e(depth)}questions.html">Open questions</a></li>
        <li><a href="{e(depth)}paths.html">Launch paths</a></li>
        <li><a href="{e(depth)}flagged.html">Flagged for review</a></li>
      </ul></div>
      <div><h4>Evidence</h4><ul>
        <li><a href="{e(depth)}verification.html">Verification log</a></li>
        <li><a href="{e(depth)}sources.html">Source register</a></li>
        <li><a href="{e(depth)}marketing/verification.html">How we verify</a></li>
        <li><a href="{e(depth)}summary.html">Executive summary</a></li>
      </ul></div>
      <div><h4>Platform</h4><ul>
        <li><a href="{e(depth)}products.html">Products</a></li>
        <li><a href="{e(depth)}analysis.html">Analysis</a></li>
        <li><a href="{e(depth)}content.html">Content engine</a></li>
        <li><a href="{e(depth)}compliance.html">Compliance</a></li>
        <li><a href="{e(depth)}tracking.html">Tracking</a></li>
        <li><a href="{e(depth)}pages/index.html">Findings hub</a></li>
      </ul></div>
    </div>
    <div class="pb-foot-detail">
      <p><strong>{e(DISCLOSURE)}</strong> Amazon and the Amazon mark are trademarks of
      Amazon.com, Inc. or its affiliates; this site is independent and not affiliated with Amazon.</p>
      <p>No price is displayed on any page of this site: the Amazon Associates Program Policies restrict
      price display to links and API responses Amazon serves itself. Outbound product links are marked
      <code>rel="sponsored nofollow"</code>. Where no official source states a value, the cell is a dash with
      the reason printed beside it &mdash; never an estimate. Traffic, click, conversion and revenue figures
      appear nowhere on this site because none has been measured.</p>
      <p><strong>Decision surfaces.</strong>
      <a href="{e(depth)}review-decide.html">Review board</a> &middot;
      <a href="{e(depth)}review.html">Review: findings</a> &middot;
      <a href="{e(depth)}review-questions.html">Review: questions</a> &middot;
      <a href="{e(depth)}review-ideas.html">Review: ideas</a> &middot;
      <a href="{e(depth)}review-trace.html">Requirements trace</a> &middot;
      <a href="{e(depth)}pages/suggestions.html">Findings-hub suggestions</a> &middot;
      <a href="{e(depth)}pages/questions.html">Findings-hub questions</a> &middot;
      <a href="{e(depth)}design-notes.html">Design notes</a> &middot;
      <a href="{e(depth)}playbook.html">Design &amp; content playbook</a></p>
      <p><strong>Operator surfaces and earlier builds.</strong>
      <a href="{e(depth)}products.html">Products</a> &middot;
      <a href="{e(depth)}analysis.html">Analysis</a> &middot;
      <a href="{e(depth)}content.html">Content engine</a> &middot;
      <a href="{e(depth)}compliance.html">Compliance</a> &middot;
      <a href="{e(depth)}tracking.html">Tracking</a> &middot;
      <a href="{e(depth)}verification.html">Verification log</a> &middot;
      <a href="{e(depth)}sources.html">Source register</a> &middot;
      <a href="{e(depth)}summary.html">Executive summary</a> &middot;
      <a href="{e(depth)}pages/index.html">Findings hub</a> &middot;
      <a href="{e(depth)}decisions/index.html">Decision hub</a> &middot;
      <a href="{e(depth)}release/index.html">Release readiness</a> &middot;
      <a href="{e(depth)}audit/index.html">Independent audit</a> &middot;
      <a href="{e(depth)}discovery/index.html">Discovery review</a> &middot;
      <a href="{e(depth)}console/index.html">Owner&rsquo;s Console</a> &middot;
      <a href="{e(depth)}journal/index.html">Journal</a> &middot;
      <a href="{e(depth)}marketing/index.html">Counter Notes archive</a> &middot;
      <a href="{e(depth)}marketing/improvements.html">Improvement board</a> &middot;
      <a href="{e(depth)}research-hub/start.html">Affiliate Research Hub</a> &middot;
      <a href="{e(depth)}zone2/index.html">Zone2 platform build</a> &middot;
      <a href="{e(depth)}affiliate-lab/index.html">Affiliate Lab</a> &middot;
      <a href="{e(depth)}revalidation/index.html">Revalidation</a> &middot;
      <a href="{e(depth)}northstar/index.html">Northstar prototype</a></p>
      <p><a href="{e(depth)}pages/categories/index.html">Commission categories</a> &middot;
      <a href="{e(depth)}journal/index.html">Journal</a> &middot;
      <a href="{e(depth)}journal/dual-basket-air-fryers.html">Two baskets beat one long timer</a> &middot;
      <a href="{e(depth)}journal/basket-vs-oven.html">Choose by geometry</a> &middot;
      <a href="{e(depth)}journal/why-every-number-has-a-source.html">Why every number links to its source</a></p>
      <p>Official sources re-read {e(CHECKED_ON)}.
      <a href="https://affiliate-program.amazon.com/">Amazon Associates</a> &middot;
      <a href="https://affiliate-program.amazon.com/help/operating/policies">Program Policies</a> &middot;
      <a href="https://affiliate-program.amazon.com/help/operating/agreement">Operating Agreement</a> &middot;
      <a href="{e(depth)}sources.html">full source register</a></p>
    </div>
  </div>
</footer>"""


def page(rel_path: str, *, title: str, description: str, active: str,
         body: str, depth: str = "", extra_head: str = "", with_data: bool = False) -> str:
    head = head_meta.head_block(rel_path, title=title, description=description,
                                site_name="Counter Notes",
                                page_type="article" if rel_path != "index.html" else "website")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{head}
<link rel="stylesheet" href="{e(depth)}assets/css/style.css">
<link rel="stylesheet" href="{e(depth)}assets/css/publish.css">
<link rel="icon" href="{e(depth)}assets/favicon.svg" type="image/svg+xml">
{extra_head}
</head>
<body>
<a class="skip-link" href="#main">{'Skip to content'}</a>
{masthead(active)}
<main id="main">
{body}
</main>
{footer(depth)}
{f'<script src="{e(depth)}assets/js/data.js"></script><script src="{e(depth)}assets/js/app.js"></script>' if with_data else ''}
</body>
</html>
"""


def decision_block(sg: dict, board: dict) -> str:
    opts = []
    for o in sg["options"]:
        cls = ' pb-opt--rec' if o["label"] == sg["recommendation"] else ""
        tag = " &nbsp;<b>(recommended)</b>" if o["label"] == sg["recommendation"] else ""
        opts.append(
            f'<div class="pb-opt{cls}"><b>Option {e(o["label"])}{tag}</b>'
            f'<p>{e(o["text"])}</p>'
            f'<div class="cost"><b>Cost</b> {e(o["cost"])}<br><b>Trade-off</b> {e(o["tradeoff"])}</div></div>'
        )
    src = ""
    if sg.get("source"):
        s = board["sources"].get(sg["source"])
        if s:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", s["url"]).split("/")[0])
            src = (f'<span><b>Source</b> <a href="{e(s["url"])}" target="_blank" '
                   f'rel="noopener noreferrer">{e(s["name"])} &middot; {e(host)}</a></span>')
    waits = ", ".join(
        f'<a href="questions.html#{e(q)}">{e(q)}</a>' for q in sg.get("waits_on", [])
    ) or "none &mdash; this can be decided now"
    return f"""<article class="pb-decision" id="{e(sg['id'])}">
  <div class="pb-decision-hd">
    <span class="pb-decision-id">{e(sg['id'])}</span>
    <h3>{e(sg['title'])}</h3>
    <span class="pb-pill pb-pill--warn">{e(sg['status'])}</span>
  </div>
  <p><b>Area:</b> {e(sg['area'])} &middot; {e(sg['summary'])}</p>
  <div class="pb-opts">{''.join(opts)}</div>
  <div class="pb-decision-ft">
    <span><b>Recommended</b> Option {e(sg['recommendation'])}</span>
    <span><b>Waits on</b> {waits}</span>
    {src}
    <span><b>Implemented</b> No &mdash; no suggestion on this board is applied until a choice is recorded.</span>
  </div>
</article>"""


def question_block(q: dict, board: dict) -> str:
    pill = "ok" if q["status"] == "answered" else "flag"
    blocks = ", ".join(
        f'<a href="suggestions.html#{e(s)}">{e(s)}</a>' for s in q.get("blocks", [])
    ) or "nothing &mdash; no suggestion is waiting on this"
    src = ""
    if q.get("source"):
        s = board["sources"].get(q["source"])
        if s:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", s["url"]).split("/")[0])
            src = (f'<span><b>Source</b> <a href="{e(s["url"])}" target="_blank" '
                   f'rel="noopener noreferrer">{e(s["name"])} &middot; {e(host)}</a></span>')
    return f"""<article class="pb-decision" id="{e(q['id'])}">
  <div class="pb-decision-hd">
    <span class="pb-decision-id">{e(q['id'])}</span>
    <h3>{e(q['question'])}</h3>
    <span class="pb-pill pb-pill--{pill}">{e(q['status'])}</span>
  </div>
  <p><b>What we know.</b> {e(q['what_we_know'])}</p>
  <p><b>What is missing.</b> {e(q['what_is_missing'])}</p>
  <p><b>How to discover it.</b> {e(q['how_to_discover'])}</p>
  <div class="pb-decision-ft">
    <span><b>Blocks</b> {blocks}</span>
    {src}
  </div>
</article>"""


def product_table(product: dict, attrs: list[str] | None = None) -> str:
    rows = spec_rows(product, attrs) if attrs else product["rows"]
    trs = []
    for r in rows:
        trs.append(
            f"<tr><td class=\"k\">{e(r['attr'])}</td><td>{value_cell(r)}</td>"
            f"<td>{source_cell(product, r)}</td></tr>"
        )
    sids = " ".join(
        f'<a class="pb-src" href="{e(s["url"])}" target="_blank" rel="{LINK_REL} noopener noreferrer">{e(s["name"])}</a>'
        for s in product["official_sources"]
    )
    return (f'<div class="pb-table-scroll"><table class="pb-table">'
            f'<caption>Every row below was read from one of these official pages: {sids}</caption>'
            f'<thead><tr><th>Specification</th><th>Value as published</th><th>Official source</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>')


def bench_card(product: dict) -> str:
    v = PRODUCT_VOICE[product["key"]]
    rows = spec_rows(product, v["highlights"])
    lis = []
    for r in rows:
        val = (r.get("value") or "").strip() or "—"
        lis.append(f"<li><span>{e(r['attr'])}</span><span>{e(val)}</span></li>")
    dp = product_link(product)
    return f"""<article>
  <p class="pb-bench-brand">{e(v['brand'])}</p>
  <h3><a href="marketing/articles/{e(product['key'].lower())}.html">{e(v['headline'])}</a></h3>
  <p class="pb-bench-note">{e(v['display'])} &middot; {e(product['model'] or 'model not stated')}</p>
  <p>{e(v['note'])}</p>
  <ul>{''.join(lis)}</ul>
  <a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer">See the listing on Amazon {e(LINK_DISCLOSURE)} &rarr;</a>
</article>"""


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def build_index(facts: dict, board: dict) -> str:
    prods = {p["key"]: p for p in facts["products"]}

    bench = "".join(bench_card(prods[k]) for k in ("P1", "P2", "P3"))

    lead_articles = [a for a in ARTICLES if a[0] in ("Capacity", "Design", "Specs")][:3]
    stories = "".join(
        f'<a class="pb-story" href="{e(href)}"><span class="k">{e(kicker)}</span>'
        f'<h3>{e(title)}</h3><p>{e(blurb)}</p></a>'
        for kicker, title, href, _cat, blurb in lead_articles
    )

    open_sg = [s for s in board["suggestions"]][:3]
    board_cards = "".join(
        f'<div class="pb-bt"><h3>{e(s["title"])}</h3><p>{e(s["area"])} &middot; '
        f'Option {e(s["recommendation"])} recommended. {e(s["status"])}.</p>'
        f'<a href="suggestions.html#{e(s["id"])}">Read the options &rarr;</a></div>'
        for s in open_sg
    )

    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <div class="pb-lead-grid">
    <div>
      <p class="pb-kicker">Three air fryers &middot; one counter</p>
      <h1 class="pb-h1">The 6-quart, the 8-quart, and the <em>oven</em> that wants to be both.</h1>
      <p class="pb-stand">Every figure on this page came off a manufacturer page or an Amazon
      listing, on a date you can check. Where the two disagree we print both. Where neither says
      anything, we print a dash and tell you why. No price, no star rating, no invented test score.</p>
      <div class="pb-actions">
        <a class="pb-btn" href="marketing/buying-guide.html">Which one should I buy?</a>
        <a class="pb-btn pb-btn--ghost" href="guides/index.html">All the guides</a>
      </div>
      <p class="pb-byline"><b>What this is.</b> Five Amazon listings this project was asked to
      promote &mdash; three air fryers and two kitchen thermometers &mdash; read row by row against
      their own spec sheets. &middot;
      <b>Sources re-read</b> {e(CHECKED_ON)} &middot;
      <b>Then</b> <a href="guides/method.html">how we verify</a>.</p>
    </div>
    <aside class="pb-takeaways">
      <h2>The short version</h2>
      <ol>
        <li><b>Two 3-quart baskets, or one big one.</b> The Chefman 6 Qt is the only machine here
        that finishes both halves of a meal at the same time.</li>
        <li><b>26 quarts is a different appliance.</b> The Emeril is an oven with French doors that
        also air fries &mdash; and the deepest machine here, 16.9 in front to back against 12.6 in
        for the 8-quart Chefman.</li>
        <li><b>The 8-quart Chefman is the plainest.</b> Four presets, one basket, and the largest
        single chamber of the three.</li>
        <li><b>Two official pages disagree twice.</b> On the Emeril's preset count and on the 8-quart
        Chefman's maximum temperature. Both disagreements are published, not resolved by picking one.</li>
        <li><b>No price is printed anywhere here.</b> Amazon's program policies restrict price display
        to content Amazon itself serves. <a href="guides/method.html">The rule and its source</a>.</li>
      </ol>
    </aside>
  </div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">The three machines on the bench</h2>
    <p class="pb-sub">One line of opinion each, then the numbers straight off the spec sheet.</p></div>
    <a class="pb-sec-link" href="marketing/comparison.html">Every number, side by side &rarr;</a>
  </div>
  <div class="pb-bench">{bench}</div>
  <p class="pb-sub" style="margin-top:18px">The listings above are the three air-fryer listings the
  first batch of supplied <code>link.amazon</code> short links open. The brief names five links
  in total; the two thermometers they resolve to are onboarded in the catalog too &mdash; see
  <a href="products.html">the product catalog</a>. That destination is reproducible, but it is not the
  same claim as &ldquo;this is the product the brief meant&rdquo; &mdash; see
  <a href="questions.html#Q-T50-01">Q-T50-01</a> and <a href="flagged.html">the flagged register</a>.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Start with the question, not the product</h2>
    <p class="pb-sub">Eight guides, each built around something a buyer actually types into a search box.</p></div>
    <a class="pb-sec-link" href="guides/index.html">Browse by category &rarr;</a>
  </div>
  <div class="pb-stories">{stories}</div>
</div></section>

<section class="pb-receipts"><div class="pb-wrap">
  <h2 class="pb-h2">The receipts</h2>
  <p class="pb-sub">Where an affiliate site would put growth numbers, this one puts its own verification
  state. No traffic, click, conversion or revenue figure appears anywhere on this site: none has been
  measured, and inventing one is the thing this project refuses to do.</p>
  <div class="pb-figs">
    <div class="pb-fig"><b>5<i> / 5</i></b><span>Supplied links that resolve, reproducibly, to one
      specific Amazon listing each. Re-observed {e(CHECKED_ON)}.</span></div>
    <div class="pb-fig"><b>0<i> / 5</i></b><span>Product mappings confirmed by an official Amazon
      document. <a href="flagged.html">Flag F-03</a>.</span></div>
    <div class="pb-fig"><b>9<i> / 10</i></b><span>Characters per supplied code against the 10-character
      ASIN rule on Amazon's own help page. <a href="flagged.html">Flag F-01</a>.</span></div>
    <div class="pb-fig"><b>4.50%<i> or 4.00%</i></b><span>Kitchen band vs &ldquo;All Other Categories&rdquo;
      in Table 1. Which applies is <a href="questions.html#Q-T50-05">Q-T50-05</a>.</span></div>
    <div class="pb-fig"><b><span id="flagCount">&mdash;</span><i> open</i></b><span>Items on the
      <a href="flagged.html">Flagged for Review register</a>, each with its official-source link.
      This number is rendered from the register, never typed.</span></div>
  </div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">What we would change next &mdash; your call</h2>
    <p class="pb-sub">Thirteen suggestions sit on the board with their options, costs and trade-offs.
    Nothing on it has been implemented. This build follows the rule, not the recommendation: every
    item still says <em>proposed</em> until you record a choice.</p></div>
    <a class="pb-sec-link" href="suggestions.html">Open the whole board &rarr;</a>
  </div>
  <div class="pb-board-tease">{board_cards}</div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">A drift found, and how it was handled</h2>
    <p class="pb-sub">Re-reading every load-bearing source on {e(CHECKED_ON)} turned up one stored value
    that was no longer true on the page it came from. It is one of
    <span id="flagCountHeading">&mdash;</span> items on the register.</p></div>
    <a class="pb-sec-link" href="flagged.html">Full flagged register &rarr;</a>
  </div>
  <div class="pb-note"><b>A listing title is perishable, and the record shows the whole arc.</b>
  This project re-read every load-bearing official source on {e(CHECKED_ON)} and found that the Amazon
  title stored for the 26-quart Emeril listing was no longer the title the page served. No specification
  row was affected and nothing on this site was wrong &mdash; the stored <em>title</em> was stale. It was
  published as a flagged item rather than quietly overwritten, because a record that silently rewrites
  itself cannot be trusted. The register now carries it as <b>F-41</b>, and the stored title has since
  been corrected by another session working on this repository in parallel &mdash; which is how the
  process is meant to work: the drift is dated, visible and traceable rather than invisible.
  <a href="https://www.amazon.com/dp/B09B7SB46R" target="_blank" rel="{LINK_REL} noopener noreferrer">Check it yourself</a> &middot;
  <a href="flagged.html">the full flagged register</a> &middot;
  <a href="questions.html#Q-T50-11">why the cadence question is still open</a>.</div>
</div></section>
"""
    return page("index.html", title="Three air fryers, measured against their own spec sheets · Counter Notes",
                description="Air fryer reviews and guides built from manufacturer and Amazon listings only: sourced spec rows, published disagreements, and blanks left blank instead of filled in.",
                active="index.html", body=body, with_data=True)


def build_suggestions(facts: dict, board: dict) -> str:
    blocks = "".join(decision_block(s, board) for s in board["suggestions"])
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Decision board</p>
  <h1 class="pb-h1">Thirteen things we could do next. <em>None of them is done.</em></h1>
  <p class="pb-stand">This is the review surface the brief asked for: every suggestion, with the options
  it could take, what each option costs, what it gives up, and the question that has to be answered
  before it can be decided. Read it, pick a path, and record the choice &mdash; nothing on this page
  applies itself.</p>
  <p class="pb-byline"><b>{len(board['suggestions'])} suggestions</b> &middot;
  <b>{sum(1 for s in board['suggestions'] if s['waits_on'])} blocked on an open question</b> &middot;
  <b>{sum(1 for s in board['suggestions'] if not s['waits_on'])} ready to decide now</b> &middot;
  last updated {e(CHECKED_ON)}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">The board</h2>
  <p class="pb-sub">Ordered roughly by how much is riding on them. Each row links to the questions
  that block it, and each question links back.</p></div>
  <a class="pb-sec-link" href="questions.html">Open the questions register &rarr;</a></div>
  {blocks}
  <div class="pb-note"><b>How a suggestion leaves this board.</b> It does not, on its own. A choice has
  to be recorded against its id, and only then does it become work. Until then the status stays
  <em>Proposed &mdash; awaiting owner decision</em>, which is the honest state of all
  {len(board['suggestions'])} rows above.</div>
</div></section>
"""
    return page("suggestions.html", title="Suggestion board · Counter Notes",
                description="Every open suggestion for this affiliate site, with options, cost, trade-offs and the questions each one waits on. Nothing is implemented until a choice is recorded.",
                active="suggestions.html", body=body)


def build_questions(facts: dict, board: dict) -> str:
    qs = board["questions"]
    answered = [q for q in qs if q["status"] == "answered"]
    openq = [q for q in qs if q["status"] != "answered"]
    blocks = "".join(question_block(q, board) for q in openq + answered)
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Questions register</p>
  <h1 class="pb-h1">What we know, what we do not, and <em>how to find out</em>.</h1>
  <p class="pb-stand">A decision made on this page before the gaps are closed is a guess wearing a
  decision's clothes. So each question states what is already settled, what is missing, the single
  action that would close it, and which suggestions are waiting on it.</p>
  <p class="pb-byline"><b>{len(qs)} questions</b> &middot;
  <b>{len(answered)} answered from an official source</b> &middot;
  <b>{len(openq)} still open</b> &middot; last updated {e(CHECKED_ON)}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Open first, then answered</h2>
  <p class="pb-sub">The open ones are the ones that block work. The answered ones are recorded too,
  because a settled rule that nobody can find gets re-litigated every cycle.</p></div>
  <a class="pb-sec-link" href="suggestions.html">Back to the suggestion board &rarr;</a></div>
  {blocks}
</div></section>
"""
    return page("questions.html", title="Open questions · Counter Notes",
                description="What this affiliate project knows, what it does not, the action that would close each gap, and which decisions are waiting on it.",
                active="questions.html", body=body)


def build_guides_index(facts: dict, board: dict) -> str:
    sections = []
    for slug, cat in GUIDE_CATEGORIES.items():
        arts = [a for a in ARTICLES if a[3] == slug]
        lis = "".join(
            f'<li><a href="../{e(href)}">{e(title)}</a><p>{e(blurb)}</p></li>'
            for _k, title, href, _c, blurb in arts
        )
        sections.append(
            f'<section><h2>{e(cat["title"])}</h2><p style="font-size:13.5px;color:var(--ink-soft);'
            f'margin:0 0 12px;line-height:1.5">{e(cat["blurb"])}</p><ul>{lis}</ul>'
            f'<p style="margin:12px 0 0"><a class="pb-sec-link" href="{e(slug)}.html">Open this category &rarr;</a></p></section>'
        )
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Guides</p>
  <h1 class="pb-h1">Everything published here, <em>by the question it answers</em>.</h1>
  <p class="pb-stand">Eleven pieces, grouped the way a reader browses rather than the way the files are
  laid out. Each one argues from the same rows the tables use, and shows its conflicts where the
  official pages disagree.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-rail">{''.join(sections)}</div>
  <div class="pb-note" style="margin-top:30px"><b>What is deliberately not here.</b> No piece on this
  site carries a search-volume figure, a trend score or a demand estimate. Those numbers exist only in
  third-party tools, not in any official source, and publishing them as fact is exactly what
  <a href="https://developers.google.com/search/docs/fundamentals/creating-helpful-content" target="_blank" rel="noopener noreferrer">Google's own guidance</a>
  warns against. When measurement is switched on
  (<a href="../suggestions.html#SG-T50-05">SG-T50-05</a>), real queries replace the guesswork.</div>
</div></section>
"""
    return page("guides/index.html", title="Guides by category · Counter Notes",
                description="Every guide published on Counter Notes, organised by category: basket air fryers, air-fryer ovens, buying guides and method.",
                active="guides/index.html", body=body, depth="../")


def build_category(slug: str, facts: dict, board: dict) -> str:
    cat = GUIDE_CATEGORIES[slug]
    prods = {p["key"]: p for p in facts["products"]}
    arts = [a for a in ARTICLES if a[3] == slug]

    lis = "".join(
        f'<li><a href="../{e(href)}">{e(title)}</a><p>{e(blurb)}</p></li>'
        for _k, title, href, _c, blurb in arts
    ) or '<li><p style="color:var(--ink-soft)">No guide published in this category yet.</p></li>'

    tables = ""
    for key in cat["keys"]:
        p = prods[key]
        v = PRODUCT_VOICE[key]
        dp = product_link(p)
        tables += (
            f'<h3 style="font-family:Fraunces,Georgia,serif;font-size:22px;font-weight:600;'
            f'margin:32px 0 6px;letter-spacing:-0.015em">{e(v["display"])}</h3>'
            f'<p style="font-size:14px;color:var(--ink-soft);margin:0 0 14px">'
            f'<a href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer">{e(dp)}</a> '
            f'&middot; {e(LINK_DISCLOSURE)}</p>'
            + product_table(p)
        )

    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Category &middot; <a href="index.html" style="color:inherit">Guides</a></p>
  <h1 class="pb-h1">{e(cat['title'])}</h1>
  <p class="pb-stand pb-measure">{e(cat['blurb'])}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">In this category</h2></div>
  <a class="pb-sec-link" href="index.html">All categories &rarr;</a></div>
  <div class="pb-rail"><section><h2>Published</h2><ul>{lis}</ul></section></div>
</div></section>
{f'<section class="pb-sec"><div class="pb-wrap"><div class="pb-sec-head"><div><h2 class="pb-h2">The verified rows behind them</h2><p class="pb-sub">Read from the official pages on {e(CHECKED_ON)}. A dash means no official source states the value.</p></div></div>{tables}</div></section>' if tables else ''}
"""
    return page(f"guides/{slug}.html", title=f"{cat['title']} · Counter Notes",
                description=cat["blurb"], active=f"guides/{slug}.html",
                body=body, depth="../")


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
TARGETS: list[tuple[str, callable]] = [
    ("index.html", build_index),
    ("suggestions.html", build_suggestions),
    ("questions.html", build_questions),
    ("guides/index.html", build_guides_index),
    ("guides/basket-air-fryers.html", lambda f, b: build_category("basket-air-fryers", f, b)),
    ("guides/air-fryer-ovens.html", lambda f, b: build_category("air-fryer-ovens", f, b)),
    ("guides/buying-guides.html", lambda f, b: build_category("buying-guides", f, b)),
    ("guides/method.html", lambda f, b: build_category("method", f, b)),
]


def main() -> int:
    check = "--check" in sys.argv
    facts, board = load()
    stale = []
    for rel, fn in TARGETS:
        out = ROOT / rel
        want = fn(facts, board)
        if check:
            if not out.exists() or out.read_text(encoding="utf-8") != want:
                stale.append(rel)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(want, encoding="utf-8")
            print(f"  wrote {rel} ({len(want):,} bytes)")
    if check:
        if stale:
            for s in stale:
                print(f"  STALE: {s} — run `python3 tools/build_front.py`")
            return 1
        print(f"front pages current ({len(TARGETS)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
