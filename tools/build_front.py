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
import front_t63 as t63  # noqa: E402  — T63 reader-first content (thermometers, FSIS rows, new guides)

ROOT = Path(__file__).resolve().parent.parent
FACTS = ROOT / "marketing" / "data" / "facts.json"
BOARD = ROOT / "docs" / "board-9251f262.json"
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"

CHECKED_ON = "2026-11-16"
UPDATED_ON = "2026-11-19"  # T63: date of this build's live source re-read (docs/verification-10727edd.md)
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
LINK_REL = "sponsored nofollow"
LINK_DISCLOSURE = "(paid link)"
ASIN_HELP_URL = "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC"

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
    "meat-thermometers": {
        "title": "Meat thermometers",
        "blurb": "An instant-read you carry to the food, and a leave-in wireless set that reports to your phone. Two of the five supplied links open these listings; both are compared here row by row.",
        "keys": ["P4", "P5"],
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
] + [(kicker, title, f"guides/{slug}.html", cat, dek)  # T63: the four question-shaped guides
     for slug, kicker, title, dek, cat in t63.NEW_GUIDES]


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
    # T63 (session 10727edd, 2026-11-19): the brief asked for the products to lead and for every
    # dashboard surface to sit behind "a single navigation group". The masthead therefore carries
    # five reader sections and ONE entry, "Behind the site", that opens a hub listing every
    # operator, decision and evidence surface. The three entries earlier sessions added here so
    # tools/audit_site.py would not report brief/, intake/ and board/ as orphans are kept
    # reachable from index.html through the footer and the hub instead — nothing was unlinked.
    nav = [
        ("index.html", "Front page"),
        ("marketing/buying-guide.html", "Air fryers"),
        ("guides/meat-thermometers.html", "Thermometers"),
        ("guides/index.html", "Guides"),
        ("marketing/comparison.html", "Compare"),
    ]
    depth = "../" if active.startswith("guides/") else ""
    items = []
    for href, label in nav:
        rel = depth + href
        cls = ' class="is-on"' if href == active else ""
        items.append(f'<a href="{e(rel)}"{cls}>{e(label)}</a>')
    behind_cls = " is-on" if active == "behind-the-site.html" else ""
    return f"""<header class="pb-mast">
  <div class="pb-wrap">
    <div class="pb-mast-top">
      <div>
        <div class="pb-word">Counter <em>Notes</em></div>
        <div class="pb-tag">Air fryers, meat thermometers and the questions to ask before you buy</div>
      </div>
      <div class="pb-mast-meta">Updated {e(UPDATED_ON)}</div>
    </div>
    <nav class="pb-nav" aria-label="Sections">{''.join(items)}<a class="pb-nav-behind{behind_cls}" href="{e(depth)}behind-the-site.html">Behind the site</a></nav>
  </div>
</header>
<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} If you buy through a product link marked &ldquo;(paid link)&rdquo;, we may earn a commission at no extra cost to you. Links to manufacturer pages, government sources and evidence are never affiliate links.</div></div>"""


def footer(depth: str = "") -> str:
    return f"""<footer class="pb-foot">
  <div class="pb-wrap">
    <div class="pb-foot-grid">
      <div><h4>Read</h4><ul>
        <li><a href="{e(depth)}index.html">Front page</a></li>
        <li><a href="{e(depth)}guides/index.html">All guides</a></li>
        <li><a href="{e(depth)}marketing/buying-guide.html">Which one to buy</a></li>
        <li><a href="{e(depth)}marketing/comparison.html">Head-to-head</a></li>
        <li><a href="{e(depth)}guides/meat-thermometers.html">Meat thermometers</a></li>
        <li><a href="{e(depth)}guides/thermometer-for-air-fryer.html">Thermometer + air fryer</a></li>
        <li><a href="{e(depth)}marketing/articles/index.html">The air-fryer write-ups</a></li>
      </ul></div>
      <div><h4>Decide</h4><ul>
        <li><a href="{e(depth)}suggestions.html">Suggestion board</a></li>
        <li><a href="{e(depth)}questions.html">Open questions</a></li>
        <li><a href="{e(depth)}intent.html">Link &amp; intent register</a></li>
        <li><a href="{e(depth)}paths.html">Launch paths</a></li>
        <li><a href="{e(depth)}brief/index.html">Design brief</a></li>
        <li><a href="{e(depth)}intake/index.html">Submitted-link register</a></li>
        <li><a href="{e(depth)}board/index.html">Decision board</a></li>
        <li><a href="{e(depth)}brief/index.html">Design brief</a></li>
        <li><a href="{e(depth)}intake/index.html">Submitted links</a></li>
        <li><a href="{e(depth)}flagged.html">Flagged for review</a></li>
      </ul></div>
      <div><h4>Evidence</h4><ul>
        <li><a href="{e(depth)}verification.html">Verification log</a></li>
        <li><a href="{e(depth)}sources.html">Source register</a></li>
        <li><a href="{e(depth)}marketing/verification.html">How we verify</a></li>
        <li><a href="{e(depth)}summary.html">Executive summary</a></li>
      </ul></div>
      <div><h4>Platform</h4><ul>
        <li><a href="{e(depth)}behind-the-site.html">Behind the site (all surfaces)</a></li>
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
      price display to content Amazon itself serves. Outbound product links are tagged Special Links
      marked <code>rel="sponsored nofollow"</code>; citation links to official pages are not affiliate
      links. Where no official source states a value, the cell is a dash with
      the reason printed beside it &mdash; never an estimate. Traffic, conversion and revenue figures
      appear nowhere on this site because none has been imported from a first-party report. The on-site
      click counter records aggregate page and link events only &mdash; no cookie, no visitor identifier,
      nothing per person &mdash; and its counts are not published until an endpoint keeps them and a
      first report makes the comparison meaningful.</p>
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
<script src="{e(depth)}assets/js/events.js" defer></script>
{f'<script src="{e(depth)}assets/js/data.js"></script><script src="{e(depth)}assets/js/app.js"></script>' if with_data else ''}
</body>
</html>
"""


def implemented_line(sg: dict) -> str:
    """T63: a row the owner decided says so; every other row keeps the original wording."""
    od = sg.get("owner_direction")
    if not od:
        return ('<span><b>Implemented</b> No &mdash; no suggestion on this board is applied until a '
                'choice is recorded.</span>')
    state = "Yes" if sg.get("implemented") else "Partly"
    return f'<span><b>Implemented</b> {state} &mdash; owner chose option {e(od["chosen_option"])} on {e(od["date"])}.</span>'


def owner_direction_block(sg: dict) -> str:
    od = sg.get("owner_direction")
    note = sg.get("brief_note")
    if od:
        return (f'\n  <p class="pb-owner"><b>Owner direction ({e(od["date"])}).</b> The brief quotes option '
                f'{e(od["chosen_option"])} verbatim: &ldquo;{e(od["quote"])}&rdquo; '
                f'<b>Where it stands:</b> {e(od["implementation"])}</p>')
    if note:
        return f'\n  <p class="pb-owner">{e(note)}</p>'
    return ""


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
            rel = f"{LINK_REL} noopener noreferrer" if "amazon." in host else "noopener noreferrer"
            src = (f'<span><b>Source</b> <a href="{e(s["url"])}" target="_blank" '
                   f'rel="{rel}">{e(s["name"])} &middot; {e(host)}</a></span>')
    waits = ", ".join(
        f'<a href="questions.html#{e(q)}">{e(q)}</a>' for q in sg.get("waits_on", [])
    ) or "none &mdash; this can be decided now"
    return f"""<article class="pb-decision" id="{e(sg['id'])}">
  <div class="pb-decision-hd">
    <span class="pb-decision-id">{e(sg['id'])}</span>
    <h3>{e(sg['title'])}</h3>
    <span class="pb-pill pb-pill--{'ok' if sg.get('implemented') else 'warn'}">{e(sg['status'])}</span>
  </div>
  <p><b>Area:</b> {e(sg['area'])} &middot; {e(sg['summary'])}</p>
  <div class="pb-opts">{''.join(opts)}</div>
  <div class="pb-decision-ft">
    <span><b>Recommended</b> Option {e(sg['recommendation'])}</span>
    <span><b>Waits on</b> {waits}</span>
    {src}
    {implemented_line(sg)}
  </div>{owner_direction_block(sg)}
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
            rel = f"{LINK_REL} noopener noreferrer" if "amazon." in host else "noopener noreferrer"
            src = (f'<span><b>Source</b> <a href="{e(s["url"])}" target="_blank" '
                   f'rel="{rel}">{e(s["name"])} &middot; {e(host)}</a></span>')
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
# T63 helpers (session 10727edd, 2026-11-19)
# --------------------------------------------------------------------------- #
NUM_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
             "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
             "seventeen", "eighteen", "nineteen", "twenty"]


def num_word(n: int, cap: bool = False) -> str:
    """A count rendered from the register it describes — never typed (the 'Thirteen' drift, F-46)."""
    w = NUM_WORDS[n] if 0 <= n < len(NUM_WORDS) else str(n)
    return w[:1].upper() + w[1:] if cap else w


def all_products(facts: dict) -> dict:
    prods = {p["key"]: p for p in facts["products"]}
    prods.update(t63.load_thermometers())
    return prods


def voice(key: str) -> dict:
    return PRODUCT_VOICE.get(key) or t63.THERMO_VOICE[key]


def cta(product: dict, depth: str = "", label: str = "See the listing on Amazon") -> str:
    dp = product_link(product)
    return (f'<a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" '
            f'data-link-state="TAGGED" data-product-key="{e(product["key"])}">{e(label)} '
            f'{e(LINK_DISCLOSURE)} &rarr;</a>')


def thermo_card(product: dict, depth: str = "") -> str:
    v = t63.THERMO_VOICE[product["key"]]
    rows = spec_rows(product, v["highlights"])
    lis = "".join(f"<li><span>{e(r['attr'])}</span><span>{e((r.get('value') or '').strip() or '—')}</span></li>"
                  for r in rows)
    return f"""<article>
  <p class="pb-bench-brand">{e(v['brand'])} &middot; {e(v['kind'])}</p>
  <h3><a href="{e(depth)}guides/instant-read-or-wireless-thermometer.html">{e(v['headline'])}</a></h3>
  <p class="pb-bench-note">{e(v['display'])}</p>
  <p>{e(v['note'])}</p>
  <ul>{lis}</ul>
  {cta(product, depth)}
</article>"""


def sourced_table(caption: str, head: tuple[str, str, str], rows: list[tuple[str, str, str, str]]) -> str:
    """A cross-product table. Each row: (label, value, status, source_url). Empty url -> dash + reason."""
    trs = []
    for label, value, status, url in rows:
        kind, pill_label = STATUS_PILL.get(status, ("idle", "unverified"))
        pill = f'<span class="pb-pill pb-pill--{kind}">{e(pill_label)}</span>'
        val = f"{e(value)} {pill}" if value else f'<span class="pb-blank">&mdash;</span> {pill}'
        if url:
            src = (f'<a class="pb-src" href="{e(url)}" target="_blank" '
                   f'rel="{LINK_REL} noopener noreferrer">{e(t63.host_of(url))}</a>')
        else:
            src = '<span class="pb-blank">&mdash;<small>No official page states this value.</small></span>'
        trs.append(f'<tr><td class="k">{e(label)}</td><td>{val}</td><td>{src}</td></tr>')
    return (f'<div class="pb-table-scroll"><table class="pb-table"><caption>{caption}</caption>'
            f'<thead><tr><th>{e(head[0])}</th><th>{e(head[1])}</th><th>{e(head[2])}</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>')


def row_of(product: dict, attr: str) -> dict | None:
    return next((r for r in product["rows"] if r["attr"] == attr), None)


def cell(product: dict, attr: str, label: str | None = None) -> tuple[str, str, str, str]:
    """One cross-table row read straight from a product's sourced rows."""
    r = row_of(product, attr)
    name = label or f"{voice(product['key'])['short']} — {attr}"
    if not r:
        return (name, "", "unverified", "")
    url = src_map(product).get(r.get("src"), {}).get("url", "") if r.get("src") else ""
    return (name, r.get("value") or "", r.get("status", "unverified"), url)


def fsis_table() -> str:
    rows = [(food, temp, "verified", t63.FSIS_URL) for food, temp in t63.FSIS_ROWS]
    return sourced_table(
        f'Minimum internal temperatures, transcribed from the '
        f'<a href="{e(t63.FSIS_URL)}" target="_blank" rel="noopener noreferrer">{e(t63.FSIS_NAME)}</a> '
        f'on {e(t63.TODAY)}.',
        ("Food", "Minimum internal temperature", "Official source"), rows)


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def build_index(facts: dict, board: dict) -> str:
    prods = all_products(facts)
    fryers = "".join(bench_card(prods[k]) for k in ("P1", "P3", "P2"))
    thermos = "".join(thermo_card(prods[k]) for k in ("P4", "P5"))

    picks = [
        ("You cook a main and a side at the same time", "P1",
         "Two baskets, and Sync Finish ends both together.", "marketing/articles/p1.html"),
        ("You want one big basket and no learning curve", "P3",
         "8 quarts, four presets.", "marketing/articles/p3.html"),
        ("You want an oven that also air fries", "P2",
         "26 quarts behind French doors, ten cooking modes.", "marketing/articles/p2.html"),
        ("You want a number in a second, anywhere", "P4",
         "Instant-read, one-second response per its listing.", "guides/instant-read-or-wireless-thermometer.html"),
        ("You want to leave the probe in and walk away", "P5",
         "Three wireless probes, WiFi to your phone.", "guides/instant-read-or-wireless-thermometer.html"),
    ]
    pick_lis = "".join(
        f'<li><span class="pb-pick-if">{e(cond)}</span>'
        f'<a href="{e(href)}">{e(voice(k)["short"])}</a><small>{e(why)}</small></li>'
        for cond, k, why, href in picks)

    guide_cards = [
        ("Thermometers", "Instant-read or leave-in wireless: which meat thermometer fits the way you cook?",
         "guides/instant-read-or-wireless-thermometer.html",
         "One you stab in and read; one that stays in and pings your phone."),
        ("Food safety", "Do you need a meat thermometer for an air fryer?",
         "guides/thermometer-for-air-fryer.html",
         "The dial sets the air temperature. The USDA chart is written in the food's."),
        ("Capacity", "How many quarts of air fryer do you actually need?",
         "marketing/topics/how-many-quarts-do-you-need.html",
         "Six quarts of what? How to translate the number every box leads with."),
        ("Design", "Two baskets or one big one? A trade you cannot undo later",
         "marketing/topics/dual-basket-or-one-big-basket.html",
         "The dual-basket pitch is about timing, not volume."),
        ("Checklist", "Seven questions to ask before buying a multi-function appliance",
         "guides/multi-function-appliance-questions.html",
         "Ten modes sounds like ten appliances. Count the ones you will use."),
        ("Fit & cleanup", "How to judge cleanup and counter space before you buy",
         "guides/cleanup-and-counter-space.html",
         "The machine you return is the one that did not fit or nobody washed."),
    ]
    stories = "".join(
        f'<a class="pb-story" href="{e(href)}"><span class="k">{e(k)}</span>'
        f'<h3>{e(t)}</h3><p>{e(b)}</p></a>' for k, t, href, b in guide_cards)
    n_guides = len(ARTICLES)

    poultry = t63.FSIS_ROWS[0][1].split(" (")[0]
    body = f"""
<section class="pb-lead pb-lead--hero"><div class="pb-wrap">
  <div class="pb-lead-grid">
    <div>
      <p class="pb-kicker">Roasting season &middot; kitchen buying guides</p>
      <h1 class="pb-h1">The air fryer that fits your counter, and the thermometer that tells you <em>dinner is done</em>.</h1>
      <p class="pb-stand">Five kitchen tools, compared on what you can check before you buy:
      footprint, capacity, controls, cleanup, and what each one is really for. Every figure links to
      the page it came from, so you never have to take our word for it.</p>
      <div class="pb-actions">
        <a class="pb-btn" href="marketing/buying-guide.html">Help me choose an air fryer</a>
        <a class="pb-btn pb-btn--ghost" href="guides/meat-thermometers.html">Pick a thermometer</a>
      </div>
    </div>
    <aside class="pb-takeaways pb-picks">
      <h2>Quick picks: start from how you cook</h2>
      <ol>{pick_lis}</ol>
      <p class="pb-picks-note">Matched on published specs, not on a test score. No price or star
      rating is shown on this site; the listing shows both.</p>
    </aside>
  </div>
  <figure class="pb-hero-art"><img src="assets/img/hero-counter.jpg" width="1600" height="900"
    alt="Illustration of an air fryer on a kitchen counter beside a roast chicken and a probe thermometer"
    loading="eager" decoding="async"><figcaption>Illustration, not product photography.</figcaption></figure>
</div></section>

<section class="pb-sec" id="air-fryers"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Air fryers</h2>
    <p class="pb-sub">A two-basket 6-quart, a one-basket 8-quart, and a 26-quart oven with doors.
    One line of opinion each, then the numbers off the spec sheet.</p></div>
    <a class="pb-sec-link" href="marketing/comparison.html">All three side by side &rarr;</a>
  </div>
  <div class="pb-bench">{fryers}</div>
</div></section>

<section class="pb-sec" id="thermometers"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Meat thermometers</h2>
    <p class="pb-sub">An instant-read you carry to the food, and a leave-in wireless set that reports
    to your phone. Different jobs, not better and worse.</p></div>
    <a class="pb-sec-link" href="guides/meat-thermometers.html">Full spec tables &rarr;</a>
  </div>
  <div class="pb-bench pb-bench--two">{thermos}</div>
</div></section>

<section class="pb-pair"><div class="pb-wrap">
  <div class="pb-pair-grid">
    <div>
      <p class="pb-kicker">Use them together</p>
      <h2 class="pb-h2">The {e(poultry)} rule: why an air fryer and a thermometer share a counter</h2>
      <p>An air fryer's dial sets the temperature of the <em>air</em>. The USDA's safe-cooking chart
      is written in the temperature <em>inside the food</em>: {e(poultry)} for all poultry,
      &ldquo;as measured with a food thermometer.&rdquo; No air fryer on this page claims to
      measure that for you.</p>
      <a class="pb-sec-link" href="guides/thermometer-for-air-fryer.html">Read the guide &rarr;</a>
    </div>
    <div>{fsis_table()}</div>
  </div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Questions buyers actually ask</h2>
    <p class="pb-sub">Each guide starts from a question, not a product, and ends at the row in a
    spec table that settles it. {num_word(n_guides, cap=True)} published so far.</p></div>
    <a class="pb-sec-link" href="guides/index.html">Every guide, by category &rarr;</a>
  </div>
  <div class="pb-stories">{stories}</div>
</div></section>

<section class="pb-trust"><div class="pb-wrap">
  <div class="pb-trust-grid">
    <div><h3>Sourced, row by row</h3><p>Specs come from the manufacturer's page or the Amazon
    listing, with a link on every row. When two official pages disagree, we print both.</p></div>
    <div><h3>Blanks stay blank</h3><p>If no official page states a value, you see a dash and the
    reason, never an estimate. No invented test scores, no fake &ldquo;tested by&rdquo; badges.</p></div>
    <div><h3>Paid links are labelled</h3><p>Product buttons are affiliate links marked
    &ldquo;(paid link)&rdquo;. Evidence links never are. <a href="guides/method.html">How we check</a>
    &middot; <a href="behind-the-site.html">Behind the site</a>.</p></div>
  </div>
  <p class="pb-trust-foot">Anything we could not confirm is published, with its source, on the
  <a href="flagged.html">Flagged for Review register</a>: <span id="flagCount">&mdash;</span> items right
  now, counted live from the register.<span class="pb-sr"> Register total: <span id="flagCountHeading">&mdash;</span>.</span></p>
</div></section>
"""
    return page("index.html", title="Air fryers and meat thermometers, compared on the specs that decide it · Counter Notes",
                description="Air fryer and meat thermometer buying guides: quick picks by how you cook, side-by-side spec tables linked to official pages, and the USDA temperatures that make a thermometer worth owning.",
                active="index.html", body=body, with_data=True,
                extra_head='<link rel="preload" as="image" href="assets/img/hero-counter.jpg">')


def guide_shell(slug: str, body_html: str, related: list[str]) -> str:
    g = next(x for x in t63.NEW_GUIDES if x[0] == slug)
    _slug, kicker, title, dek, cat = g
    rel_path = f"guides/{slug}.html"
    rel_links = "".join(
        f'<li><a href="{e(h)}">{e(t)}</a></li>' for t, h in
        [(x[2], f"{x[0]}.html") for x in t63.NEW_GUIDES if x[0] in related])
    body = f"""
<article class="pb-article">
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">{e(kicker)} &middot; <a href="{e(cat)}.html" style="color:inherit">{e(GUIDE_CATEGORIES[cat]['title'])}</a></p>
  <h1 class="pb-h1 pb-measure">{e(title)}</h1>
  <p class="pb-stand pb-measure">{e(dek)}</p>
  <p class="pb-byline"><b>Counter Notes</b> &middot; published {e(t63.TODAY)} &middot; sources re-read {e(t63.TODAY)}
  &middot; <a href="method.html">how we check</a></p>
</div></section>
<section class="pb-sec"><div class="pb-wrap"><div class="pb-prose">
{body_html}
</div>
<aside class="pb-related"><h2>Keep reading</h2><ul>{rel_links}
<li><a href="index.html">Every guide, by category</a></li></ul></aside>
</div></section>
</article>
"""
    return page(rel_path, title=f"{title} · Counter Notes", description=dek, active=rel_path,
                body=body, depth="../", extra_head=t63.jsonld_article(rel_path, title, dek))


def g_cta(product: dict) -> str:
    return f'<p class="pb-inline-cta">{cta(product, label="Check " + voice(product["key"])["short"] + " on Amazon")}</p>'


def build_guide_thermo_compare(facts: dict, board: dict) -> str:
    p = all_products(facts)
    tm, cq = p["P4"], p["P5"]
    nm = t63.NEWER_MODEL_ASIN
    body = f"""
<h2>The short answer</h2>
<ul class="pb-checks">
  <li><b>You check food at the end and want a number now:</b> an instant-read. The ThermoMaven's
  listing states a 1-second response and &plusmn;0.5 &deg;F accuracy, and it runs on one AAA battery
  that comes in the box.</li>
  <li><b>You roast, smoke or cook for hours and want to walk away:</b> a leave-in wireless set. The
  CHEF iQ Sense listing states three probes, WiFi with unlimited range, and a hub that charges all
  three at once.</li>
</ul>

<h2>Two numbers that look alike and are not</h2>
<p>The ThermoMaven lists an <em>upper temperature range</em> of 572 &deg;F: the hottest thing it can
measure. The CHEF iQ lists <em>1000 &deg;F heat safe</em>: how much heat the probe is built to
survive while it sits in a grill. Neither number tells you the other. Read them as answers to
different questions.</p>

<h2>Questions to ask yourself</h2>
<ol class="pb-checks">
  <li><b>How many things are cooking at once?</b> One probe answers one question. The CHEF iQ set
  on this page has three; its listing also offers 1, 2, 3 or 4 probe sizes.</li>
  <li><b>Will you remember to charge it?</b> The ThermoMaven takes a AAA battery. The CHEF iQ is
  rechargeable, and its own listing gives two different battery lives, &ldquo;up to 50 hours&rdquo;
  in one section and &ldquo;70+ hours&rdquo; in another. We print both and pick neither.</li>
  <li><b>Is it going in the air fryer?</b> The CHEF iQ description says &ldquo;air-fryer and
  deep-fryer safe&rdquo;. The ThermoMaven listing does not say either way, so neither do we. An
  instant-read is used outside the machine anyway: pull the basket, read, push it back.</li>
  <li><b>How do you clean it?</b> ThermoMaven: wipe clean, and the listing calls it waterproof.
  CHEF iQ: waterproof, dishwasher-safe probes.</li>
</ol>

<h2>The ThermoMaven, row by row</h2>
{product_table(tm)}
{g_cta(tm)}

<h2>The CHEF iQ Sense, row by row</h2>
{product_table(cq)}
{g_cta(cq)}

<h2>What these listings cannot tell you</h2>
<p>Accuracy figures on both pages are the seller's own claims; we have no independent test, and we
will not invent one. One more thing we saw when we re-read the ThermoMaven page on {e(t63.TODAY)}:
Amazon now shows &ldquo;There is a newer model of this item&rdquo;, pointing at a different listing
(<a href="https://www.amazon.com/dp/{e(nm)}" target="_blank" rel="sponsored nofollow noopener noreferrer">{e(nm)}</a>).
We have not compared the two, so we say nothing about it.</p>
<p class="pb-fineprint">Both products are the listings the owner's supplied short links open. Whether
those are the exact products intended is a separate, open question
(<a href="../intent.html">link &amp; intent register</a>).</p>
"""
    return guide_shell("instant-read-or-wireless-thermometer", body,
                       ["thermometer-for-air-fryer", "cleanup-and-counter-space"])


def build_guide_thermo_airfryer(facts: dict, board: dict) -> str:
    p = all_products(facts)
    rows = [cell(p["P1"], "Temperature range", "Chefman 6 Qt dual-window: air temperature range"),
            cell(p["P3"], "Temperature range", "Chefman 8 Qt: air temperature range"),
            cell(p["P2"], "Temperature range", "Emeril 26 Qt oven: air temperature range"),
            cell(p["P4"], "Response time", "ThermoMaven: time to a reading"),
            cell(p["P5"], "Air-fryer / deep-fryer safe", "CHEF iQ Sense: air-fryer safe")]
    body = f"""
<h2>The short answer</h2>
<p>If you cook chicken, pork or anything ground in an air fryer: yes, or at least it is the only
way to know. The USDA Food Safety and Inspection Service puts it plainly:
&ldquo;{e(t63.FSIS_QUOTE)}&rdquo;</p>

<h2>The dial is not the doneness</h2>
<p>Every air fryer on this site publishes a temperature range, and every one of them is the
temperature of the <em>air</em> the fan pushes around the basket. None of the three official pages
claims to measure the food. That is the gap a thermometer fills.</p>
{sourced_table("Air temperature is what the appliance sets. Internal temperature is what the chart asks for.",
               ("What", "As published", "Official source"), rows)}

<h2>The temperatures that matter</h2>
{fsis_table()}
<p>For whole cuts of beef, pork, veal and lamb, the chart adds a rest: at least three minutes before
carving.</p>

<h2>Which kind of thermometer suits an air fryer?</h2>
<ul class="pb-checks">
  <li><b>Instant-read:</b> pull the basket, take a reading, slide it back. Nothing has to survive the
  cooking chamber. <a href="instant-read-or-wireless-thermometer.html">Compare the two types</a>.</li>
  <li><b>Leave-in wireless:</b> the CHEF iQ description says &ldquo;air-fryer and deep-fryer safe&rdquo;.
  Whether a probe fits under the drawer of a particular basket model is not stated on any page we
  read, so measure your basket before you count on it.</li>
</ul>
{g_cta(p["P4"])}
{g_cta(p["P5"])}
"""
    return guide_shell("thermometer-for-air-fryer", body,
                       ["instant-read-or-wireless-thermometer", "multi-function-appliance-questions"])


def build_guide_multifunction(facts: dict, board: dict) -> str:
    p = all_products(facts)
    em, c8 = p["P2"], p["P3"]
    body = f"""
<p>A multi-function appliance is a bet that one box will replace several. Sometimes it does.
Sometimes it replaces one appliance well and the rest only on paper. These seven questions use the 26-quart Emeril
Lagasse French-door oven as the worked example, because it is the multi-function machine on this
site, and the 8-quart Chefman as the single-purpose contrast.</p>

<ol class="pb-checks">
  <li><b>Which modes will you use every week?</b> The Emeril lists ten: air fry, bake, broil,
  defrost, dehydrate, grill, proof, reheat, roast and warm. Circle the ones you would actually use.
  If it is two, a simpler machine may serve you better.</li>
  <li><b>Where will it live?</b> Its manufacturer page gives 16.9&Prime; deep, 15.8&Prime; wide and
  14.8&Prime; high. Measure the depth of your counter and the height under your wall cabinets.</li>
  <li><b>Does the door need room to swing?</b> Dual French doors open outward, so the space in front
  of the machine matters as much as the footprint.</li>
  <li><b>Which count do you trust when the pages disagree?</b> The Emeril's preset count and its
  accessory count differ between the manufacturer page and the Amazon title. When counts disagree,
  read the list, not the number on the front.</li>
  <li><b>Is your outlet up to it?</b> 1700 W at 120 V on the official pages. Check that against
  the circuit you plan to use.</li>
  <li><b>What does the warranty cover?</b> One year, per the manufacturer page.</li>
  <li><b>Would a single-purpose machine do the job?</b> The 8-quart Chefman has four presets and
  one basket. It does less, and that is the point.</li>
</ol>

<h2>The Emeril oven, row by row</h2>
{product_table(em)}
{g_cta(em)}

<h2>The single-purpose contrast</h2>
{product_table(c8, ["Capacity", "Presets", "Dimensions (8 Qt)", "Power", "Temperature range"])}
{g_cta(c8)}
"""
    return guide_shell("multi-function-appliance-questions", body,
                       ["cleanup-and-counter-space", "thermometer-for-air-fryer"])


def build_guide_cleanup(facts: dict, board: dict) -> str:
    p = all_products(facts)
    fit = [cell(p["P1"], "Dimensions", "Chefman 6 Qt dual-window"),
           cell(p["P3"], "Dimensions (8 Qt)", "Chefman 8 Qt"),
           cell(p["P2"], "Dimensions", "Emeril 26 Qt French-door oven"),
           ("Drawer pull-out clearance (any model)", "", "unverified", "")]
    clean = [cell(p["P1"], "Basket care", "Chefman 6 Qt dual-window"),
             cell(p["P3"], "Basket care", "Chefman 8 Qt"),
             ("Emeril 26 Qt French-door oven", "", "unverified", ""),
             cell(p["P4"], "Care instructions", "ThermoMaven instant-read"),
             cell(p["P5"], "Probe care", "CHEF iQ Sense probes")]
    body = f"""
<p>Most kitchen-appliance regret is not about cooking. It is about the gap
between the top of the machine and the bottom of the cabinet, or the basket nobody wants to scrub.
Check these two things before anything else.</p>

<h2>1. Will it fit?</h2>
<p>Take a tape measure to three places: counter depth, height under the wall cabinet, and the space
in front for a drawer or door to open. The official dimensions are below. None of the pages states
how far a drawer pulls out, so that row is a dash: measure the one in the shop or ask the seller.</p>
{sourced_table("Footprint as published on each official page.", ("Model", "Dimensions as published", "Official source"), fit)}
<p>Leave a little air around the machine as well; the manufacturer manual for your model is the
place to check how much.</p>

<h2>2. Will you actually clean it?</h2>
{sourced_table("Cleanup as each official page describes it. A dash means the page we read does not say.",
               ("Item", "Care as published", "Official source"), clean)}
<p>Rule of thumb: a part that goes in the dishwasher gets cleaned; a part that needs hand-scrubbing
gets put off. If the page does not say, assume hand-wash until the manual tells you otherwise.</p>

<h2>3. Think in footprints, not quarts</h2>
<p>Quarts are measured by each brand its own way. Dimensions are not. If two machines fit your
space, then compare capacity; <a href="../marketing/topics/how-many-quarts-do-you-need.html">here is
how to read the quarts number</a>.</p>
{g_cta(p["P1"])}
{g_cta(p["P3"])}
"""
    return guide_shell("cleanup-and-counter-space", body,
                       ["multi-function-appliance-questions", "instant-read-or-wireless-thermometer"])


BEHIND_GROUPS = [
    ("Decide", "Where the open choices live. Nothing on these pages applies itself.", [
        ("suggestions.html", "Suggestion board", "Every proposed change, with options, cost and trade-offs."),
        ("questions.html", "Open questions", "What is known, what is missing, and how to find out."),
        ("board/index.html", "Decision board", "The five-product brief: choose-a-path and the requirements trace."),
        ("review-decide.html", "Review board", "Findings to review before anything is implemented."),
        ("paths.html", "Launch paths", "The named launch paths and what each one does not authorise."),
        ("decisions/index.html", "Decision hub", "Decisions recorded so far, with blockers."),
        ("console/index.html", "Owner's Console", "The owner's decision sheet."),
    ]),
    ("Evidence", "How every number on the reader pages was checked.", [
        ("flagged.html", "Flagged for review", "Every irregularity, with its official-source link."),
        ("verification.html", "Verification log", "Each check performed, with its result."),
        ("sources.html", "Source register", "Every official source the site relies on."),
        ("intent.html", "Link & intent register", "Supplied links: intended product vs observed destination, kept apart."),
        ("intake/index.html", "Submitted links", "The five supplied short links, as observed."),
        ("summary.html", "Executive summary", "The state of the project on one page."),
        ("audit/index.html", "Independent audit", "A second session's audit of the tree."),
    ]),
    ("Platform", "The operator dashboards behind the affiliate workflow.", [
        ("products.html", "Products", "The product catalog as the platform sees it."),
        ("analysis.html", "Analysis", "Scoring modules (data-gated: they say 'insufficient data' rather than guess)."),
        ("content.html", "Content engine", "Planned and published content."),
        ("compliance.html", "Compliance", "Disclosure and link-policy checks."),
        ("tracking.html", "Tracking", "The click-measurement plan and its status."),
        ("release/index.html", "Release readiness", "What is met and what is still open."),
        ("pages/index.html", "Findings hub", "The ledger rendered as browsable pages."),
        ("brief/index.html", "Design brief", "The design brief and its measured state."),
        ("discovery/index.html", "Discovery review", "The discovery-phase register."),
    ]),
    ("Archive", "Earlier builds, preserved rather than deleted.", [
        ("marketing/index.html", "Counter Notes archive", "The first editorial build."),
        ("journal/index.html", "Journal", "Long-form notes."),
        ("research-hub/start.html", "Affiliate Research Hub", "An earlier research dashboard."),
        ("zone2/index.html", "Zone2 platform build", "An earlier multi-page dashboard."),
        ("affiliate-lab/index.html", "Affiliate Lab", "An earlier lab build."),
        ("revalidation/index.html", "Revalidation", "An earlier revalidation pass."),
        ("northstar/index.html", "Northstar prototype", "The first prototype."),
    ]),
]


def build_behind(facts: dict, board: dict) -> str:
    groups = []
    for title, blurb, items in BEHIND_GROUPS:
        lis = "".join(f'<li><a href="{e(h)}">{e(t)}</a><p>{e(d)}</p></li>' for h, t, d in items)
        groups.append(f'<section><h2>{e(title)}</h2><p class="pb-rail-blurb">{e(blurb)}</p><ul>{lis}</ul></section>')
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Behind the site</p>
  <h1 class="pb-h1">How this site is checked, and <em>what is still undecided</em>.</h1>
  <p class="pb-stand pb-measure">The reader pages lead with the products. Everything that supports them
  (the verification log, the flagged register, the suggestion board, the open questions and the operator
  dashboards) lives here, one click from every page.</p>
  <p class="pb-byline"><b>{num_word(len(board['suggestions']), cap=True)} suggestions</b> awaiting a
  decision &middot; <b>{num_word(sum(1 for q in board['questions'] if q['status'] != 'answered'))} open questions</b>
  &middot; updated {e(UPDATED_ON)}</p>
</div></section>
<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-rail">{''.join(groups)}</div>
</div></section>
"""
    return page("behind-the-site.html", title="Behind the site · Counter Notes",
                description="Every verification, decision and operator surface behind Counter Notes, in one place: flagged items, sources, the suggestion board, open questions and dashboards.",
                active="behind-the-site.html", body=body)


def build_current_summary(facts: dict, board: dict) -> str:
    """Reader-facing, current executive summary from the five-link intent register.

    This replaces the stale three-link `summary.html` narrative. It reads the newer
    product-intent ledger and never fills an intended value from an observed redirect target.
    """
    submissions = json.loads((ROOT / "intake" / "data" / "submissions.json").read_text(encoding="utf-8"))
    entries = submissions["entries"]
    product_rows = []
    for item in entries:
        asin = item.get("observed_redirect_asin") or ""
        submitted = item.get("submitted_token") or ""
        target_link = (f'<span>Observed ASIN <code>{e(asin)}</code>'
                       if asin else '<span class="pb-blank">&mdash;<small>No observed destination recorded.</small></span>')
        intended = item.get("intended_asin") or ""
        intent_cell = (f'<code>{e(intended)}</code>' if intended else
                       '<span class="pb-blank">Not confirmed<small>Intended ASIN and official listing URL remain blank.</small></span>')
        product_rows.append(
            f'<tr id="{e(item["id"])}"><td><code>{e(submitted)}</code>'
            f'<small>{e(item.get("token_char_count", ""))} characters as supplied</small></td>'
            f'<td>{intent_cell}</td><td>{target_link}'
            f'<small>Observed {e(item.get("observed_utc", ""))}; not evidence of intended identity.</small></td>'
            f'<td><a class="pb-src" href="intake/submissions.html#{e(item["id"])}">Intent/observation record</a>'
            f' <a class="pb-src" href="{ASIN_HELP_URL}" target="_blank" rel="noopener noreferrer">Amazon ASIN rule</a></td></tr>'
        )

    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Current executive summary · 2026-11-19</p>
  <h1 class="pb-h1">The evidence, the gaps, and the next sensible decisions.</h1>
  <p class="pb-stand">Counter Notes is now a reader-facing publication with sourced buyer guides,
  a comparison, an RSS feed and a generated sitemap. This is the current project summary, not a
  product-performance claim: the product-link observations below are dated 2026-11-17, and this
  integration pass did not repeat the Amazon redirects.</p>
  <p class="pb-byline"><b>Working rule.</b> Intended product identity, observed redirect destination,
  and campaign performance are separate records. Unknowns stay blank; proposals stay proposals.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Five submitted links — intent is still unconfirmed</h2>
  <p class="pb-sub">The five recorded observations resolve to three air-fryer listings and two meat-thermometer
  listings. That describes observed destinations only; it does not establish what the owner intended.</p></div>
  <a class="pb-sec-link" href="intake/submissions.html">Open the full confirmation register &rarr;</a></div>
  <div class="pb-table-scroll"><table class="pb-table"><thead><tr>
    <th>Code supplied</th><th>Intended ASIN</th><th>Observed target</th><th>Review sources</th>
  </tr></thead><tbody>{''.join(product_rows)}</tbody></table></div>
  <p class="pb-note"><b>Do not read the short-code shape as a compliance verdict.</b> The exact compliance
  status of the supplied short links remains unresolved in <a href="https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003" target="_blank" rel="noopener noreferrer">FLG-003</a>.
  The code supplied is not itself a 10-digit ASIN, but that fact alone does not establish whether the
  short link is compliant. The official record of intended ASIN, official listing URL, confirmation date
  and confirmation source is kept apart from the observed redirect target.
  <a href="https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC" target="_blank" rel="noopener noreferrer">Amazon’s ASIN and link-format help</a>.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">What is working — and what is not</h2>
  <p class="pb-sub">The site automates deterministic checks; account actions, first-party reports and product-intent confirmation still require evidence the repository does not hold.</p></div></div>
  <div class="pb-table-scroll"><table class="pb-table"><thead><tr><th>Area</th><th>Evidence-backed status</th><th>What remains open</th><th>Official review</th></tr></thead><tbody>
    <tr><td class="k">Special Links</td><td>The owner supplied <code>{e(ASSOCIATES_TAG)}</code>. The tag appears in this publication’s disclosure copy, but repository HTML inspection shows that product-destination links do not consistently carry it.</td><td>Account ownership, active status, marketplace and each product’s enrolled-Associates destination/report test are not confirmed. The five supplied short links themselves were observed without an Associates tag; that is not a finding that the short links are invalid. Apply and test the supplied tag on every intended Special Link only after product intent is confirmed.</td><td><a class="pb-src" href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener noreferrer">Amazon Operating Agreement</a> <a class="pb-src" href="{ASIN_HELP_URL}" target="_blank" rel="noopener noreferrer">Amazon link format</a></td></tr>
    <tr><td class="k">Disclosure and paid-link marking</td><td>The build gates check the required Associates statement and sponsored qualification on product offers; source citations are kept distinct from offers.</td><td>Keep disclosure placement and endorsement context in every new publishing review.</td><td><a class="pb-src" href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener noreferrer">Amazon Agreement</a> <a class="pb-src" href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" target="_blank" rel="noopener noreferrer">FTC disclosure guidance</a> <a class="pb-src" href="https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links" target="_blank" rel="noopener noreferrer">Google sponsored links</a></td></tr>
    <tr><td class="k">Click and conversion measurement</td><td><code>assets/js/events.js</code> queues three aggregate event types locally in the browser; it sends nothing and publishes no counts without an endpoint.</td><td>GitHub Pages is static hosting. No self-hosted event sink, retention decision, server-side bot filter, Associates report import or Search Console query import is present. The event registers disagree on implementation status, and the page-view code sends its hostname field as <code>r</code> while the measurement schema calls it <code>referrer_host</code>. Reconcile these contracts before implementing an endpoint.</td><td><a class="pb-src" href="https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages" target="_blank" rel="noopener noreferrer">GitHub Pages: static hosting</a> <a class="pb-src" href="discovery/measurement.html#EV-01">Event register</a> <a class="pb-src" href="intake/tracking.html">Submitted brief’s tracking record</a></td></tr>
    <tr><td class="k">Campaign ledger</td><td><code>ledger/campaigns.json</code> is empty by design. No click, order or revenue score is invented.</td><td>Only add rows from authorized first-party reports, with dated provenance. Product intent must be confirmed before campaigns are associated with a submitted product.</td><td><a class="pb-src" href="https://affiliate-program.amazon.com/help/operating/policies" target="_blank" rel="noopener noreferrer">Amazon Program Policies</a> <a class="pb-src" href="ledger/campaigns.json">Empty ledger and schema</a></td></tr>
    <tr><td class="k">Search and editorial</td><td>The publication has question-shaped guides, a feed and sitemap. Titles are editorial hypotheses, not claims about trends, query popularity or search volume.</td><td>No Search Console property or query report is recorded. Verify ownership, submit the sitemap, then plan topics from measured query/page data. Set an accountable editor, cadence and image-rights policy before scaling.</td><td><a class="pb-src" href="https://support.google.com/webmasters/answer/9008080?hl=en" target="_blank" rel="noopener noreferrer">Google: verify ownership</a> <a class="pb-src" href="https://support.google.com/webmasters/answer/7451001?hl=en" target="_blank" rel="noopener noreferrer">Google: sitemaps</a> <a class="pb-src" href="https://support.google.com/webmasters/answer/7576553?hl=en" target="_blank" rel="noopener noreferrer">Google: performance/query report</a></td></tr>
    <tr><td class="k">Product research and commission</td><td>Verified manufacturer/listing specifications can be shown with their sources. Price, rating, review count, competition and product-specific conversion/commission potential remain blank where not confirmed.</td><td>Do not rank products or forecast revenue without authorized catalog data and first-party reports; confirm product category and account eligibility first.</td><td><a class="pb-src" href="https://affiliate-program.amazon.com/help/operating/policies" target="_blank" rel="noopener noreferrer">Amazon Program Policies</a> <a class="pb-src" href="sources.html">Source register</a></td></tr>
  </tbody></table></div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Questions to answer before scaling</h2>
  <p class="pb-sub">Each question is a gate, not a placeholder to guess around. The linked register includes what is known, what is missing, who can obtain it, and the next evidence to collect.</p></div>
  <a class="pb-sec-link" href="questions.html">Open all questions &rarr;</a></div>
  <ol class="pb-prose">
    <li>For each of the five submissions, what exact product was intended? Record the ASIN, official listing URL, date and confirmation source; keep the redirect observation in its separate field.</li>
    <li>Which Associates account and marketplace owns the supplied tag, and does one test link per confirmed product reach the intended destination and appear in the authorized report?</li>
    <li>Where will the first-party event endpoint run, what is the retention/bot-filter rule, and which of the two conflicting five-event definitions is canonical?</li>
    <li>Who is the named editor, what publishing cadence is sustainable, and will visuals be original, properly licensed or permitted Program Content?</li>
    <li>Is this publication strictly about air fryers, or should the two observed thermometer destinations become a separate category only after their intended identity is confirmed?</li>
  </ol>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Suggested order of work</h2>
  <p class="pb-sub">Recommendations are review items, not approvals. Nothing is auto-applied from this list.</p></div>
  <a class="pb-sec-link" href="suggestions.html">Review options and trade-offs &rarr;</a></div>
  <ol class="pb-prose">
    <li><b>Resolve intent first.</b> Confirm all five product mappings and decide whether the publication remains air-fryer-only or adds a thermometer category.</li>
    <li><b>Validate one tagged Special Link per confirmed product.</b> Check destination and Associates reporting inside the enrolled account before scaling.</li>
    <li><b>Connect measurement honestly.</b> Reconcile the event definitions, choose a first-party endpoint and retention policy, verify Search Console ownership, then report only data actually received.</li>
    <li><b>Publish a short editorial pilot.</b> Use buyer questions such as basket-versus-oven trade-offs, capacity, cleanup/counter space and multi-function appliance checklists as hypotheses. Add an accountable byline and original/authorized visuals; do not call topics “trending” without evidence or imply hands-on use that did not occur.</li>
  </ol>
  <p class="pb-note"><b>Editorial guardrail.</b> The FTC says an endorser cannot describe experience with a product they have not tried. A sourced specification comparison is not a hands-on test, and the copy should keep that distinction clear. <a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers" target="_blank" rel="noopener noreferrer">FTC guidance</a>.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <h2 class="pb-h2">Review the registers</h2>
  <div class="pb-rail">
    <section><h2>Decide</h2><ul><li><a href="suggestions.html">Suggestions board</a><p>Options, costs and trade-offs; nothing chosen.</p></li><li><a href="questions.html">Known and unknown</a><p>What can be decided now, and the evidence still missing.</p></li><li><a href="board/index.html">Five-link decision board</a><p>Requirement trace, intent fields and flagged irregularities.</p></li></ul></section>
    <section><h2>Verify</h2><ul><li><a href="intent.html">Product-intent record</a><p>Intent and observed redirect targets kept separate.</p></li><li><a href="flagged.html">Flagged for review</a><p>Open irregularities and their sources.</p></li><li><a href="sources.html">Official source register</a><p>Source pages and verification records.</p></li></ul></section>
  </div>
</div></section>
"""
    return page("summary.html", title="Executive summary · Counter Notes",
                description="Current evidence, open questions and reviewable recommendations for Counter Notes. Product intent, redirect observations and performance data are kept separate.",
                active="summary.html", body=body)


def build_suggestions(facts: dict, board: dict) -> str:
    blocks = "".join(decision_block(s, board) for s in board["suggestions"])
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Decision board</p>
  <h1 class="pb-h1">{num_word(len(board['suggestions']), cap=True)} things we could do next. <em>{num_word(sum(1 for s in board['suggestions'] if s.get('owner_direction')), cap=True)} decided by the owner, the rest waiting on you.</em></h1>
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
  <em>Proposed &mdash; awaiting owner decision</em>, which is the honest state of
  {sum(1 for s in board['suggestions'] if not s.get('owner_direction'))} of the
  {len(board['suggestions'])} rows above. A row reads <em>Decided</em> only where the owner's own brief
  quotes one of its options word for word; the quote is printed on the row.</div>
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
  <p class="pb-stand">{num_word(len(ARTICLES), cap=True)} pieces, grouped the way a reader browses rather than the way the files are
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
    prods = all_products(facts)
    arts = [a for a in ARTICLES if a[3] == slug]

    lis = "".join(
        f'<li><a href="../{e(href)}">{e(title)}</a><p>{e(blurb)}</p></li>'
        for _k, title, href, _c, blurb in arts
    ) or '<li><p style="color:var(--ink-soft)">No guide published in this category yet.</p></li>'

    tables = ""
    for key in cat["keys"]:
        p = prods[key]
        v = voice(key)
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
    ("summary.html", build_current_summary),
    ("suggestions.html", build_suggestions),
    ("questions.html", build_questions),
    ("guides/index.html", build_guides_index),
    ("guides/basket-air-fryers.html", lambda f, b: build_category("basket-air-fryers", f, b)),
    ("guides/air-fryer-ovens.html", lambda f, b: build_category("air-fryer-ovens", f, b)),
    ("guides/buying-guides.html", lambda f, b: build_category("buying-guides", f, b)),
    ("guides/method.html", lambda f, b: build_category("method", f, b)),
    # T63 (session 10727edd): reader-first additions
    ("guides/meat-thermometers.html", lambda f, b: build_category("meat-thermometers", f, b)),
    ("guides/instant-read-or-wireless-thermometer.html", build_guide_thermo_compare),
    ("guides/thermometer-for-air-fryer.html", build_guide_thermo_airfryer),
    ("guides/multi-function-appliance-questions.html", build_guide_multifunction),
    ("guides/cleanup-and-counter-space.html", build_guide_cleanup),
    ("behind-the-site.html", build_behind),
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
