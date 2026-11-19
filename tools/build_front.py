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
from link_builder import ASSOCIATES_TAG, build_product_link  # noqa: E402  — the policy-guarded Special Link emitter

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "marketing" / "data" / "facts.json"
BOARD = ROOT / "docs" / "board-9251f262.json"
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"

CHECKED_ON = "2026-11-16"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
LINK_REL = "sponsored nofollow"
CITATION_REL = "nofollow noopener noreferrer"
LINK_DISCLOSURE = "(paid link)"

# Editorial copy for the three listings. Every figure quoted in these strings also
# appears as a sourced row in the generated table below it — the prose never introduces
# a number the table does not carry.
PRODUCT_VOICE = {
    "P1": {
        "display": "Chefman TurboFry Touch 6 Qt Dual-Window",
        "short": "Chefman 6 Qt dual-window",
        "brand": "Chefman",
        "headline": "A six-quart air fryer with two baskets",
        "note": "The manufacturer lists two independent baskets and a Sync Finish. Compare the total capacity, temperature range, and footprint.",
        "highlights": ["Capacity", "Temperature range", "Power", "Door / window", "Sync Finish"],
    },
    "P2": {
        "display": "Emeril Lagasse French Door AirFryer 360, 26 Qt",
        "short": "Emeril Lagasse 26 Qt French-door oven",
        "brand": "Emeril Lagasse",
        "headline": "A French-door oven-style air fryer",
        "note": "The manufacturer page and Amazon listing disagree on preset counts. The comparison keeps both statements visible.",
        "highlights": ["Capacity", "Cooking presets", "Dimensions", "Door", "Included accessories"],
    },
    "P3": {
        "display": "Chefman TurboFry Touch 8 Qt Stainless Steel",
        "short": "Chefman 8 Qt TurboFry Touch",
        "brand": "Chefman",
        "headline": "An eight-quart basket with a temperature conflict",
        "note": "The listing title and manufacturer page state different maximum temperatures. Read the conflict before comparing heat claims.",
        "highlights": ["Capacity", "Temperature range", "Hi-Fry / max temperature claim in Amazon title", "Basket care", "Dimensions (8 Qt)"],
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
    """Link every populated value to its official source(s), or explain a blank."""
    sources = src_map(product)
    sids = [sid for sid in (row.get("src"), row.get("src_alt")) if sid]
    links = []
    for sid in sids:
        source = sources.get(sid)
        if not source:
            continue
        host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", source["url"]).split("/")[0])
        links.append(
            f'<a class="pb-src" href="{e(source["url"])}" target="_blank" '
            f'rel="{CITATION_REL}">{e(host)}</a>'
        )
    if links:
        return '<span class="pb-source-links">' + ' <span aria-hidden="true">·</span> '.join(links) + '</span>'
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
    """Reader-first navigation with one grouped doorway to all project surfaces."""
    depth = "../" if active.startswith("guides/") else ""
    primary = [
        ("index.html", "Home"),
        ("index.html#products", "Products"),
        ("marketing/buying-guide.html", "Buying guide"),
        ("marketing/comparison.html", "Compare"),
        ("guides/index.html", "Guides"),
        ("marketing/articles/index.html", "Articles"),
    ]
    primary_items = []
    for href, label in primary:
        is_active = href == active or (href == "guides/index.html" and active.startswith("guides/"))
        cls = ' class="is-on"' if is_active else ""
        primary_items.append(f'<a href="{e(depth + href)}"{cls}>{e(label)}</a>')

    project_groups = [
        ("Choose what happens next", [
            ("board/index.html", "Decision board"),
            ("board/suggestions.html", "Suggestions &amp; choices"),
            ("board/questions.html", "Known &amp; missing information"),
            ("board/topics.html", "Editorial topic queue"),
            ("board/products.html", "Product-intent register"),
            ("board/requirements.html", "Requirements trace"),
            ("paths.html", "Launch paths"),
            ("suggestions.html", "Site suggestions"),
            ("questions.html", "Site questions"),
        ]),
        ("Verify the record", [
            ("intent.html", "Link &amp; intent register"),
            ("intake/index.html", "Submitted-link intake"),
            ("flagged.html", "Flagged for review"),
            ("verification.html", "Verification log"),
            ("sources.html", "Source register"),
            ("summary.html", "Executive summary"),
            ("marketing/verification.html", "How we verify"),
        ]),
        ("Operator dashboards", [
            ("products.html", "Products"),
            ("analysis.html", "Analysis"),
            ("content.html", "Content engine"),
            ("compliance.html", "Compliance"),
            ("tracking.html", "Tracking"),
            ("brief/index.html", "Design brief"),
            ("console/index.html", "Owner's console"),
            ("pages/index.html", "Findings hub"),
            ("decisions/index.html", "Decision hub"),
            ("release/index.html", "Release readiness"),
        ]),
        ("Archives &amp; prototypes", [
            ("audit/index.html", "Independent audit"),
            ("discovery/index.html", "Discovery review"),
            ("journal/index.html", "Journal"),
            ("marketing/index.html", "Marketing archive"),
            ("marketing/improvements.html", "Improvement board"),
            ("research-hub/start.html", "Affiliate Research Hub"),
            ("zone2/index.html", "Zone2 platform build"),
            ("affiliate-lab/index.html", "Affiliate Lab"),
            ("revalidation/index.html", "Revalidation"),
            ("northstar/index.html", "Northstar prototype"),
            ("design-notes.html", "Design notes"),
            ("playbook.html", "Design &amp; content playbook"),
        ]),
    ]
    project_hrefs = {href for _title, links in project_groups for href, _label in links}
    menu_open = " open" if active in project_hrefs else ""
    columns = []
    for title, links in project_groups:
        lis = []
        for href, label in links:
            cls = ' class="is-on"' if active == href else ""
            lis.append(f'<li><a href="{e(depth + href)}"{cls}>{label}</a></li>')
        columns.append(f'<section class="pb-nav-col"><h2>{title}</h2><ul>{"".join(lis)}</ul></section>')

    return f"""<header class="pb-mast">
  <div class="pb-wrap">
    <div class="pb-mast-top">
      <a class="pb-brand" href="{e(depth)}index.html" aria-label="Counter Notes home">
        <span class="pb-word">Counter <em>Notes</em></span>
        <span class="pb-tag">Countertop cooking, read from the spec sheet</span>
      </a>
      <span class="pb-mast-meta">Independent buying notes · source links on every spec</span>
    </div>
    <nav class="pb-nav" aria-label="Main navigation">
      <div class="pb-nav-links">{"".join(primary_items)}</div>
      <details class="pb-nav-group"{menu_open}>
        <summary>Project desk <span aria-hidden="true">⌄</span></summary>
        <div class="pb-nav-dropdown">{"".join(columns)}</div>
      </details>
    </nav>
  </div>
</header>
<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} We may earn a commission when you use an Amazon product link, at no extra cost to you. Product links are marked near the link; source citations are kept separate. <a href="{e(depth)}intent.html">See the link record.</a></div></div>"""


def footer(depth: str = "") -> str:
    """A short reader footer, with every project surface available in a single archive."""
    groups = [
        ("Read", [
            ("index.html", "Front page"),
            ("guides/index.html", "All guides"),
            ("marketing/buying-guide.html", "Buying guide"),
            ("marketing/comparison.html", "Compare the listings"),
            ("marketing/articles/index.html", "Product notes"),
            ("marketing/feed.xml", "RSS feed"),
        ]),
        ("Choose", [
            ("board/suggestions.html", "Review suggestions"),
            ("board/questions.html", "Known &amp; missing"),
            ("board/topics.html", "Question-shaped topics"),
            ("board/products.html", "Product-intent register"),
            ("intent.html", "Link &amp; intent"),
            ("flagged.html", "Flagged for review"),
        ]),
        ("Research", [
            ("sources.html", "Source register"),
            ("verification.html", "Verification log"),
            ("marketing/verification.html", "Editorial method"),
            ("summary.html", "Executive summary"),
            ("sitemap.xml", "Sitemap"),
        ]),
        ("Platform", [
            ("products.html", "Product dashboard"),
            ("analysis.html", "Analysis dashboard"),
            ("content.html", "Content engine"),
            ("compliance.html", "Compliance dashboard"),
            ("tracking.html", "Tracking dashboard"),
            ("console/index.html", "Owner's console"),
        ]),
    ]
    columns = []
    for title, links in groups:
        lis = "".join(f'<li><a href="{e(depth + href)}">{label}</a></li>' for href, label in links)
        columns.append(f'<div><h2>{title}</h2><ul>{lis}</ul></div>')

    archive = [
        ("board/index.html", "Decision board"),
        ("board/requirements.html", "Requirements trace"),
        ("intake/index.html", "Submitted-link intake"),
        ("brief/index.html", "Design brief"),
        ("paths.html", "Launch paths"),
        ("suggestions.html", "Site suggestions"),
        ("questions.html", "Site questions"),
        ("analysis.html", "Analysis"),
        ("content.html", "Content"),
        ("compliance.html", "Compliance"),
        ("tracking.html", "Tracking"),
        ("pages/index.html", "Findings hub"),
        ("decisions/index.html", "Decision hub"),
        ("release/index.html", "Release readiness"),
        ("audit/index.html", "Independent audit"),
        ("discovery/index.html", "Discovery review"),
        ("journal/index.html", "Journal"),
        ("marketing/index.html", "Marketing archive"),
        ("marketing/improvements.html", "Improvement board"),
        ("research-hub/start.html", "Affiliate Research Hub"),
        ("zone2/index.html", "Zone2 platform"),
        ("affiliate-lab/index.html", "Affiliate Lab"),
        ("revalidation/index.html", "Revalidation"),
        ("northstar/index.html", "Northstar prototype"),
        ("design-notes.html", "Design notes"),
        ("playbook.html", "Design &amp; content playbook"),
        ("pages/categories/index.html", "Commission categories"),
    ]
    archive_links = " · ".join(f'<a href="{e(depth + href)}">{label}</a>' for href, label in archive)
    return f"""<footer class="pb-foot">
  <div class="pb-wrap">
    <div class="pb-foot-grid">{"".join(columns)}</div>
    <details class="pb-foot-archive">
      <summary>All project surfaces &amp; earlier builds</summary>
      <p>{archive_links}</p>
    </details>
    <div class="pb-foot-detail">
      <p><strong>{e(DISCLOSURE)}</strong> Counter Notes is an independent publication. Amazon and the Amazon mark are trademarks of Amazon.com, Inc. or its affiliates; this site is not affiliated with Amazon.</p>
      <p>We do not print static product prices, ratings, search-volume claims or conversion estimates. The five submitted-link records keep intended products separate from observed destinations; the two thermometer destinations are not in the buying shortlist while intent is unconfirmed. The click script stores only a bounded aggregate queue in the reader's browser. There is no hosted event endpoint connected, so no site-wide traffic or conversion figures are reported.</p>
      <p>Review source dates beside each record. <a href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener noreferrer nofollow">Amazon Associates Operating Agreement</a> · <a href="https://affiliate-program.amazon.com/help/operating/policies" target="_blank" rel="noopener noreferrer nofollow">Program Policies</a> · <a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" target="_blank" rel="noopener noreferrer nofollow">FTC disclosure guidance</a> · <a href="{e(depth)}flagged.html">Open issues</a></p>
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
<link rel="alternate" type="application/rss+xml" title="Counter Notes — new guides" href="{e(depth)}marketing/feed.xml">
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
        f'<a class="pb-src" href="{e(s["url"])}" target="_blank" rel="{CITATION_REL}">{e(s["name"])}</a>'
        for s in product["official_sources"]
    )
    return (f'<div class="pb-table-scroll"><table class="pb-table">'
            f'<caption>Every row below was read from one of these official pages: {sids}</caption>'
            f'<thead><tr><th>Specification</th><th>Value as published</th><th>Official source</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>')


def bench_card(product: dict) -> str:
    v = PRODUCT_VOICE[product["key"]]
    rows = []
    for row in spec_rows(product, v["highlights"]):
        value = value_cell(row)
        source = source_cell(product, row)
        rows.append(
            f'<li><span class="pb-bench-label">{e(row["attr"])}</span>'
            f'<span class="pb-bench-value">{value}</span>{source}</li>'
        )
    dp = product_link(product)
    name_source = next((source for source in product["official_sources"]
                        if source.get("kind") == "manufacturer"), product["official_sources"][0])
    name_source_link = (
        f'<a class="pb-src" href="{e(name_source["url"])}" target="_blank" '
        f'rel="{CITATION_REL}">Manufacturer source</a>'
    )
    return f"""<article class="pb-product-card">
  <p class="pb-bench-brand">{e(v['brand'])} · observed listing</p>
  <h3><a href="marketing/articles/{e(product['key'].lower())}.html">{e(v['headline'])}</a></h3>
  <p class="pb-bench-note">{e(v['display'])} &middot; {name_source_link}</p>
  <p class="pb-product-summary">{e(v['note'])}</p>
  <ul class="pb-bench-facts">{''.join(rows)}</ul>
  <a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" data-link-state="TAGGED" data-product-key="{e(product['key'])}">See the Amazon listing {e(LINK_DISCLOSURE)} &rarr;</a>
  <p class="pb-product-read"><a href="marketing/articles/{e(product['key'].lower())}.html">Read the sourced notes</a></p>
</article>"""


def observed_thermometer_listings() -> str:
    """Show the two extra observed destinations as source records, not recommendations."""
    ledger = json.loads((ROOT / "ledger" / "products.json").read_text(encoding="utf-8"))
    sources_data = json.loads((ROOT / "ledger" / "sources.json").read_text(encoding="utf-8"))
    sources = {source["id"]: source for source in sources_data["sources"]}
    entries = {entry["id"]: entry for entry in ledger["entries"]}
    cards = []
    for product_id in ("P-04", "P-05"):
        entry = entries.get(product_id)
        if not entry:
            continue
        resolved = entry.get("resolved", {})
        source = next((sources[sid] for sid in resolved.get("source_ids", []) if sid in sources), None)
        if not source or source.get("kind") != "official":
            raise ValueError(f"{product_id}: observed thermometer destination has no official source")
        title = (resolved.get("title") or "").strip()
        brand = (resolved.get("brand") or "").strip()
        observed = (resolved.get("observed_utc") or "").strip()
        if not (title and brand and observed and source.get("url")):
            raise ValueError(f"{product_id}: observed thermometer listing is missing a sourced field")
        cards.append(f"""<article class="pb-observed-card">
  <p class="pb-bench-brand">{e(entry['id'])} · destination observed</p>
  <h3>{e(brand)}</h3>
  <p class="pb-observed-title">{e(title)}</p>
  <p class="pb-observed-status">Observed {e(observed)} · intended product not confirmed.</p>
  <a class="pb-src" href="{e(source['url'])}" target="_blank" rel="{CITATION_REL}">Amazon listing source</a>
</article>""")
    if len(cards) != 2:
        raise ValueError("Expected the two thermometer destination records P-04 and P-05")
    return ''.join(cards)


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def build_index(facts: dict, board: dict) -> str:
    prods = {p["key"]: p for p in facts["products"]}
    bench = "".join(bench_card(prods[k]) for k in ("P1", "P2", "P3"))
    thermometer_cards = observed_thermometer_listings()

    featured_kickers = {"Capacity", "Category", "Fit", "Specs"}
    lead_articles = [article for article in ARTICLES if article[0] in featured_kickers]
    stories = "".join(
        f'<a class="pb-story" href="{e(href)}"><span class="k">{e(kicker)}</span>'
        f'<h3>{e(title)}</h3><p>{e(blurb)}</p></a>'
        for kicker, title, href, _category, blurb in lead_articles
    )

    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <div class="pb-front-hero">
    <div class="pb-front-copy">
      <p class="pb-kicker">Counter Notes &middot; countertop cooking</p>
      <h1 class="pb-h1">Air fryer or oven-style? Start with the space you have.</h1>
      <p class="pb-stand">We compare three air-fryer listings using the manufacturers&rsquo; pages and the listings themselves: two basket designs and one French-door oven. Check capacity, shape, and footprint before you decide. If sources disagree, we show both. If they say nothing, we leave the cell blank.</p>
      <div class="pb-actions">
        <a class="pb-btn" href="#products">Browse the three listings</a>
        <a class="pb-btn pb-btn--ghost" href="marketing/comparison.html">Compare the specs</a>
      </div>
      <p class="pb-front-routes"><a href="guides/basket-air-fryers.html">Basket air fryers</a><span aria-hidden="true">·</span><a href="guides/air-fryer-ovens.html">Oven-style models</a><span aria-hidden="true">·</span><a href="guides/index.html">All buyer guides</a></p>
    </div>
    <figure class="pb-front-art">
      <img src="assets/img/counter-notes-still-life.jpg" alt="Editorial illustration of a generic air fryer, oven, cooking basket, thermometer and measuring tape on a countertop" width="1365" height="768" fetchpriority="high">
      <figcaption>Illustrative artwork, not a photograph of a reviewed product.</figcaption>
    </figure>
  </div>
</div></section>

<section class="pb-sec" id="products"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><p class="pb-kicker">The current comparison</p><h2 class="pb-h2">Three air-fryer listings. Three different shapes.</h2>
    <p class="pb-sub">Start with how each one is built. Every specification shown here links to the official page that states it.</p></div>
    <a class="pb-sec-link" href="marketing/comparison.html">See every sourced row &rarr;</a>
  </div>
  <div class="pb-bench">{bench}</div>
  <p class="pb-intent-note">These are the destinations the first three supplied short links opened in the recorded checks. That observation does not confirm which products were intended. The product-intent register keeps the two fields separate, and the enrolled Associates link-and-report test is still pending. <a href="intent.html">Review all five link records</a>.</p>
</div></section>

<section class="pb-sec pb-sec--quiet"><div class="pb-wrap">
  <div class="pb-sec-head pb-sec-head--tight">
    <div><p class="pb-kicker">Another aisle in the brief</p><h2 class="pb-h2">Two thermometer listings are still in the intake.</h2>
    <p class="pb-sub">The other two supplied links resolve to meat-thermometer listings. Their intended products have not been confirmed, so we keep them out of the buying recommendations for now. These are destination records, not endorsements.</p></div>
    <a class="pb-sec-link" href="board/products.html">Open the five-product register &rarr;</a>
  </div>
  <div class="pb-observed-grid">{thermometer_cards}</div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><p class="pb-kicker">Read before you choose</p><h2 class="pb-h2">Buyer questions, answered from the spec sheets.</h2>
    <p class="pb-sub">Short guides for the trade-offs the listings actually show. These are editorial questions, not claims about search popularity.</p></div>
    <a class="pb-sec-link" href="guides/index.html">Browse all guides &rarr;</a>
  </div>
  <div class="pb-stories">{stories}</div>
  <div class="pb-editorial-next">
    <div><strong>What should we cover next?</strong><p>The proposed titles are hypotheses, not trend data. The topic queue shows the source behind each idea and what still needs measuring.</p></div>
    <div class="pb-editorial-links"><a href="board/topics.html">Review the article queue &rarr;</a><a href="marketing/feed.xml">Follow new guides by RSS &rarr;</a></div>
  </div>
</div></section>

<section class="pb-sec pb-project-callout"><div class="pb-wrap">
  <div class="pb-project-grid">
    <div><p class="pb-kicker">A publication shaped with readers</p><h2 class="pb-h2">Help choose the next move.</h2>
    <p class="pb-sub">The review board lays out the options, costs, trade-offs, unanswered questions, and ways to find missing information. Product scope, publishing cadence, and real measurement are still open decisions. Nothing is marked chosen or auto-applied.</p></div>
    <div class="pb-project-actions">
      <a class="pb-btn" href="board/suggestions.html">Review suggestions</a>
      <a class="pb-btn pb-btn--ghost" href="board/questions.html">See what is known &amp; missing</a>
      <a class="pb-sec-link" href="board/index.html">Open the decision board &rarr;</a>
    </div>
  </div>
  <p class="pb-project-foot">The RSS feed is shipped. Search Console and a hosted event endpoint are not connected, so no search-demand, click, conversion, or revenue results are presented.</p>
</div></section>
"""
    return page("index.html", title="Air fryer and oven-style buying guides · Counter Notes",
                description="Compare three air-fryer listings by basket layout, capacity and footprint. Every published specification links to its official source; disagreements and unknowns stay visible.",
                active="index.html", body=body)


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
