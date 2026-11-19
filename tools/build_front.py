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
import head_meta
import shop_layout  # noqa: E402  (T63 shared chrome)
import build_shop  # noqa: E402  (T63 shop components)  # noqa: E402  — the repository's single canonical/OG contract
from link_builder import ASSOCIATES_TAG, build_product_link  # noqa: E402  — the policy-guarded Special Link emitter

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
    """The outbound product link, composed by the policy-guarded link builder — never by hand.

    T58 (session `7264f3c2`, 2026-11-17): the owner supplied the Associates tracking ID
    (`ASSOCIATES_TAG` in tools/link_builder.py), so this is now a tagged Special Link rather than
    the inert preview link every page published before. build_product_link() refuses an invalid
    identifier, a malformed tag, competing attribution parameters and user-derived sub-tags, so a
    policy violation fails the build instead of publishing. Citation links (class="pb-src") never
    route through here: evidence links stay unmonetized by design.
    """
    link = build_product_link(product["asin"], ASSOCIATES_TAG,
                              link_text="See this model's listing")
    return link.href


def spec_rows(product: dict, attrs: list[str]) -> list[dict]:
    by_attr = {r["attr"]: r for r in product["rows"]}
    return [by_attr[a] for a in attrs if a in by_attr]


def masthead(active: str) -> str:
    """Reader nav + one "Behind the scenes" group + disclosure strip.

    T63 (session 75efdf57, 2026-11-19): delegated to tools/shop_layout.py so the front pages and
    the shop section share one masthead. Every entry the earlier nav carried (design brief,
    submitted links, decision board, operator dashboard ...) is still linked: from the
    "Behind the scenes" menu and from the footer, which tools/audit_site.py relies on.
    """
    depth = "../" if active.startswith("guides/") else ""
    return shop_layout.masthead(depth, active)


def footer(depth: str = "") -> str:
    """Shared footer (T63): every dashboard and register, plus the disclosure repeated."""
    return shop_layout.footer(depth, CHECKED_ON)


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
<link rel="stylesheet" href="{e(depth)}assets/css/shop.css">
<link rel="alternate" type="application/rss+xml" title="Counter Notes" href="{e(depth)}marketing/feed.xml">
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
<script src="{e(depth)}assets/js/events.js" defer></script>
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
  <a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" data-link-state="TAGGED" data-product-key="{e(product['key'])}">See the listing on Amazon {e(LINK_DISCLOSURE)} &rarr;</a>
</article>"""


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def build_index(facts: dict, board: dict) -> str:
    """The front page: a shop-first publication front (T63, session 75efdf57, 2026-11-19).

    Order follows the owner's brief - lead with products, then categories, guides, method - and
    keeps the audit trail one click away (the "Behind the scenes" strip and the footer) instead
    of on the front. Product cards, buttons and citations come from tools/build_shop.py, so the
    front page and the shop cannot disagree. The derived flag-count markers (flagCount,
    flagCountHeading) stay: tools/validate_data.py requires them and app.js fills them.
    """
    cat, gd, _br = build_shop.load()
    byid = build_shop.products_by_id(cat)
    order = [i for c in cat["categories"] for i in c["products"]]
    cards = "".join(build_shop.card(cat, byid[i], "") for i in order)
    tiles = "".join(
        f'<a class="sh-tile" href="shop/{e(c["slug"])}.html">{build_shop.picture("", c["image"], alt=c["image_alt"])}'
        f'<span class="sh-kick">{e(c["kicker"])}</span><b>{e(c["name"])}</b><span>{e(c["dek"])}</span></a>'
        for c in cat["categories"])
    guides = "".join(build_shop.guide_teaser(g, "") for g in gd["guides"])
    archive = "".join(
        f'<li><a href="{e(href)}"><span class="sh-kick">{e(kicker)}</span><b>{e(title)}</b><span>{e(blurb)}</span></a></li>'
        for kicker, title, href, _cat, blurb in ARTICLES[:3])
    temps = next(g for g in gd["guides"] if g["slug"] == "air-fryer-meat-thermometer-temperatures")
    body = f"""<section class="sh-hero">
  <div class="sh-wrap sh-hero-grid">
    <div>
      <p class="sh-kick">Kitchen gear, explained before you buy</p>
      <h1>Two baskets, one big basket, or an oven &mdash; and the thermometer that tells you when it&rsquo;s done.</h1>
      <p class="sh-dek">Three air fryers and two meat thermometers, each with who it suits, who should skip it, and every specification linked to the page that published it. No prices, no star ratings, no invented test scores.</p>
      <p><a class="sh-btn" href="shop/index.html">Shop all five</a> &nbsp; <a class="sh-more-link" href="shop/compare.html">Compare side by side &rarr;</a></p>
    </div>
    {build_shop.picture("", "hero", cls="sh-hero-img", eager=True)}
  </div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">The five products</h2>
  <div class="sh-grid">{cards}</div>
</section>
<section class="sh-wrap">
  <div class="sh-season">
    <p class="sh-kick">In season &middot; Thanksgiving is Thursday, 26 November</p>
    <h2>Turkey is done at 165 &deg;F &mdash; measured in the thickest part, not guessed from the clock.</h2>
    <p>That is the U.S. government&rsquo;s safe minimum for all poultry {build_shop.src_link(cat, "SH-01")}. Our temperature guide has the full chart and how each thermometer here fits the job.</p>
    <p><a class="sh-btn" href="shop/guides/{e(temps["slug"])}.html">{e(temps["title"])}</a></p>
  </div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Shop by category</h2>
  <div class="sh-tiles">{tiles}</div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Buying guides</h2>
  <ul class="sh-guides">{guides}</ul>
  <h2 class="sh-h2" style="margin-top:36px">From the archive</h2>
  <ul class="sh-guides">{archive}</ul>
  <p class="sh-small"><a href="guides/index.html">Earlier guides by category</a> &middot; <a href="marketing/buying-guide.html">Which air fryer to buy</a> &middot; <a href="journal/index.html">Journal</a></p>
</section>
{build_shop.how_we_pick("")}
<section class="sh-wrap">
  <div class="sh-behind">
    <div>
      <p class="sh-kick">Behind the scenes</p>
      <h2>How this site is checked</h2>
      <p>Every figure is re-read from its official page; disagreements and gaps are published rather than smoothed over. <span id="flagCountHeading">&mdash;</span> irregularities are on the register right now, each with its source. Decisions the owner still has to make live on the briefing, with options and the questions they wait on.</p>
    </div>
    <ul>
      <li><a href="shop/briefing.html"><b>Owner briefing</b><span>Summary, suggestions to choose from, open questions</span></a></li>
      <li><a href="flagged.html"><b>Flagged for review</b><span><span id="flagCount">&mdash;</span> items, each with its official source</span></a></li>
      <li><a href="intent.html"><b>Link and intent register</b><span>What each supplied link opens, kept apart from what was intended</span></a></li>
      <li><a href="pages/index.html"><b>Findings hub</b><span>The line-by-line verification record</span></a></li>
    </ul>
  </div>
</section>
"""
    return page("index.html", title="Counter Notes: air fryers and meat thermometers, explained before you buy",
                description="Three air fryers and two meat thermometers: who each one suits, who should skip it, and every specification linked to its official source.",
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
            f'<a href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" '
            f'data-link-state="TAGGED" data-product-key="{e(p["key"])}">{e(dp)}</a> '
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
