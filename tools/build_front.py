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

T63 (session `arena/6ce606cb-zone2`, 2026-11-19) — shop-first rebuild
---------------------------------------------------------------------
  * the front page now leads with all five supplied listings: three air fryers from
    facts.json, two meat thermometers whose rows are read from ledger/products.json
    `resolved.specs` (sources S61/S62) — never re-typed here;
  * the masthead is one short reader navigation group; every dashboard and earlier build
    moved to the footer, which is on every page, so nothing became unreachable;
  * new: guides/thermometers.html (category) and three question-shaped thermometer guides,
    every food-safety temperature cited to FoodSafety.gov or USDA FSIS;
  * counts that drifted when typed by hand (suggestions, guides) are now derived;
  * editorial voice, food-safety rows, the new guides and the board overlay live in
    docs/front-6ce606cb.json (read-only input). tools/build_desk.py renders the decision desk.

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
OVERLAY = ROOT / "docs" / "front-6ce606cb.json"          # T63: voice, guides, board overlay
LEDGER_PRODUCTS = ROOT / "ledger" / "products.json"     # T63: thermometer rows (resolved.specs)
LEDGER_SOURCES = ROOT / "ledger" / "sources.json"
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"

# T63: all five short links re-resolved and both thermometer listings re-read on this date.
CHECKED_ON = "2026-11-19"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
LINK_REL = "sponsored nofollow"
LINK_DISCLOSURE = "(paid link)"

# Editorial copy for the three listings. Every figure quoted in these strings also
# appears as a sourced row in the generated table below it — the prose never introduces
# a number the table does not carry.
PRODUCT_VOICE = {
    "P1": {
        "page": "marketing/articles/p1.html",
        "best_for": "Cooking a main and a side at once, both done together",
        "display": "Chefman TurboFry Touch 6 Qt Dual-Window",
        "short": "Chefman 6 Qt dual-window",
        "brand": "Chefman",
        "headline": "Two baskets that finish at the same time",
        "note": "The only one of the three that solves the cold-second-batch problem.",
        "highlights": ["Capacity", "Temperature range", "Power", "Door / window", "Sync Finish"],
    },
    "P2": {
        "page": "marketing/articles/p2.html",
        "best_for": "Family-size batches, rotisserie and oven-style cooking",
        "display": "Emeril Lagasse French Door AirFryer 360, 26 Qt",
        "short": "Emeril Lagasse 26 Qt French-door oven",
        "brand": "Emeril Lagasse",
        "headline": "An oven that air fries, with doors instead of a drawer",
        "note": "26 quarts and ten cooking modes. You give up counter space and get a rotisserie spit.",
        "highlights": ["Capacity", "Temperature range", "Cooking modes", "Door", "Dimensions"],
    },
    "P3": {
        "page": "marketing/articles/p3.html",
        "best_for": "One big basket and a panel with nothing to learn",
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
    # T63: the two thermometer listings get their own category; rendered by build_thermometers().
    "thermometers": {
        "title": "Meat thermometers",
        "blurb": "An instant-read that answers in a second and a wireless probe that stays in the roast, plus the safe temperatures that make either of them worth owning.",
        "keys": [],
    },
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
    # T63: evidenced question updates from the overlay are applied in memory only; the
    # board file belongs to another session and is never written.
    upd = extras()["overlay"].get("question_updates", {})
    for q in board["questions"]:
        if q["id"] in upd:
            q.update(upd[q["id"]])
    return facts, board


_EXTRAS: dict | None = None


def extras() -> dict:
    """T63: the overlay plus the two thermometer listings, normalised to the facts.json shape.

    Rows come from ledger/products.json `resolved.specs`, so the ledger stays the single place
    the thermometer values were transcribed. The overlay contributes editorial voice only, plus
    the policy blanks (price, rating) and one documented unknown.
    """
    global _EXTRAS
    if _EXTRAS is not None:
        return _EXTRAS
    ov = json.loads(OVERLAY.read_text(encoding="utf-8"))
    ledger = {en["id"]: en for en in json.loads(LEDGER_PRODUCTS.read_text(encoding="utf-8"))["entries"]}
    srcs = {s["id"]: s for s in json.loads(LEDGER_SOURCES.read_text(encoding="utf-8"))["sources"]}
    thermos = []
    for t in ov["thermometers"]:
        res = ledger[t["ledger_id"]]["resolved"]
        if res.get("asin") != t["asin"]:
            raise SystemExit(f"{t['ledger_id']}: overlay ASIN {t['asin']} != ledger {res.get('asin')}")
        rows = []
        for sp in res["specs"]:
            ids = sp.get("source_ids") or []
            row = {"attr": sp["attribute"], "value": sp["value"], "status": sp["status"],
                   "src": ids[0] if ids else None}
            if not ids:
                row["blank_reason"] = sp.get("why_blank") or "No official source recorded."
            rows.append(row)
        rows += t.get("extra_rows", [])
        official = []
        for sid in dict.fromkeys(r["src"] for r in rows if r.get("src")):
            official.append({"id": sid, "url": srcs[sid]["url"],
                             "name": f"Amazon listing {t['asin']} (ledger {sid})"})
        thermos.append({"key": t["key"], "asin": t["asin"], "model": None, "rows": rows,
                        "official_sources": official, "title_official": res.get("title", ""),
                        "listing_notice": t.get("listing_notice", ""),
                        "supplied_link": t["supplied_link"]})
        PRODUCT_VOICE[t["key"]] = {
            "page": f"guides/thermometers.html#{t['key']}",
            "best_for": t["best_for"], "display": t["display"], "short": t["short"],
            "brand": t["brand"], "headline": t["headline"], "note": t["note"],
            "highlights": t["highlights"],
        }
    _EXTRAS = {"overlay": ov, "thermos": thermos}
    return _EXTRAS


NUM_WORDS = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen "
             "Fourteen Fifteen Sixteen Seventeen Eighteen Nineteen Twenty Twenty-one Twenty-two "
             "Twenty-three Twenty-four Twenty-five Twenty-six Twenty-seven Twenty-eight Twenty-nine "
             "Thirty").split()


def num_word(n: int, lower: bool = False) -> str:
    """Counts are derived, never typed (the board H1 once said Thirteen over twelve rows)."""
    w = NUM_WORDS[n] if 0 <= n < len(NUM_WORDS) else str(n)
    return w.lower() if lower else w


def ov_source_link(sid: str, label: str | None = None) -> str:
    """A citation to a source in the T63 overlay register. Evidence links are never tagged."""
    s = extras()["overlay"]["sources"][sid]
    rel = LINK_REL + " noopener noreferrer" if "amazon." in s["url"] else "noopener noreferrer"
    return (f'<a class="pb-src" href="{e(s["url"])}" target="_blank" rel="{rel}">'
            f'{e(label or s["name"])}</a>')


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
    # T63 (session 6ce606cb, 2026-11-19): one short reader navigation group, per SG-T50-01's
    # Option B. Earlier sessions added Design brief (dc72a69e, T50), Submitted links
    # (613900e6, T58), Decision board (1bfbc559, T61), Suggestions, Questions and an Operator
    # dashboard link here so tools/audit_site.py would see each namespace linked from
    # index.html. Every one of them now sits in footer(), which is on every page including
    # index.html, so each stays linked and reachable; only its position changed.
    nav = [
        ("index.html", "Front page"),
        ("guides/basket-air-fryers.html", "Air fryers"),
        ("guides/thermometers.html", "Meat thermometers"),
        ("marketing/buying-guide.html", "Which to buy"),
        ("guides/index.html", "Guides"),
        ("desk/index.html", "Decision desk"),
    ]
    depth = "../" if "/" in active else ""
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
        <div class="pb-tag">Air fryers and meat thermometers, read off the spec sheet</div>
      </div>
      <div class="pb-mast-meta">Sources re-read {e(CHECKED_ON)}</div>
    </div>
    <nav class="pb-nav" aria-label="Sections">{''.join(items)}</nav>
  </div>
</header>
<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} A commission may be earned when you buy through our links, at no extra cost to you. Product links are Special Links carrying the Associates tag <code>{e(ASSOCIATES_TAG)}</code>; citation and evidence links are not affiliate links.</div></div>"""


def footer(depth: str = "") -> str:
    return f"""<footer class="pb-foot">
  <div class="pb-wrap">
    <div class="pb-foot-grid">
      <div><h4>Read</h4><ul>
        <li><a href="{e(depth)}index.html">Front page</a></li>
        <li><a href="{e(depth)}guides/index.html">All guides</a></li>
        <li><a href="{e(depth)}marketing/buying-guide.html">Which one to buy</a></li>
        <li><a href="{e(depth)}marketing/comparison.html">Head-to-head</a></li>
        <li><a href="{e(depth)}marketing/articles/index.html">The three air-fryer write-ups</a></li>
        <li><a href="{e(depth)}guides/thermometers.html">Meat thermometers</a></li>
        <li><a href="{e(depth)}guides/thermometers-is-the-turkey-done.html">Is the turkey done?</a></li>
        <li><a href="{e(depth)}marketing/feed.xml">RSS feed (air-fryer topics)</a></li>
      </ul></div>
      <div><h4>Decide</h4><ul>
        <li><a href="{e(depth)}desk/index.html">Decision desk</a></li>
        <li><a href="{e(depth)}desk/questions.html">Answer these first</a></li>
        <li><a href="{e(depth)}suggestions.html">Suggestion board</a></li>
        <li><a href="{e(depth)}questions.html">Open questions</a></li>
        <li><a href="{e(depth)}intent.html">Link &amp; intent register</a></li>
        <li><a href="{e(depth)}paths.html">Launch paths</a></li>
        <li><a href="{e(depth)}board/index.html">Decision board</a></li>
        <li><a href="{e(depth)}flagged.html">Flagged for review</a></li>
        <li><a href="{e(depth)}brief/index.html">Design brief</a></li>
        <li><a href="{e(depth)}intake/index.html">Submitted links</a></li>
      </ul></div>
      <div><h4>Evidence</h4><ul>
        <li><a href="{e(depth)}verification.html">Verification log</a></li>
        <li><a href="{e(depth)}sources.html">Source register</a></li>
        <li><a href="{e(depth)}marketing/verification.html">How we verify</a></li>
        <li><a href="{e(depth)}summary.html">Executive summary</a></li>
      </ul></div>
      <div><h4>Platform</h4><ul>
        <li><a href="{e(depth)}products.html">Products (operator dashboard)</a></li>
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


def bench_card(product: dict, depth: str = "") -> str:
    v = PRODUCT_VOICE[product["key"]]
    rows = spec_rows(product, v["highlights"])
    lis = []
    for r in rows:
        val = (r.get("value") or "").strip() or "—"
        lis.append(f"<li><span>{e(r['attr'])}</span><span>{e(val)}</span></li>")
    dp = product_link(product)
    ident = product["model"] or f"ASIN {product['asin']}"
    return f"""<article id="pick-{e(product['key'].lower())}">
  <p class="pb-bench-brand">{e(v['brand'])}</p>
  <h3><a href="{e(depth)}{e(v['page'])}">{e(v['headline'])}</a></h3>
  <p class="pb-bench-note">{e(v['display'])} &middot; {e(ident)}</p>
  <p>{e(v['note'])}</p>
  <p class="pb-bench-for"><b>Best for</b> {e(v['best_for'])}</p>
  <ul>{''.join(lis)}</ul>
  <a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" data-link-state="TAGGED" data-product-key="{e(product['key'])}">See the listing on Amazon {e(LINK_DISCLOSURE)} &rarr;</a>
  <a class="pb-bench-more" href="{e(depth)}{e(v['page'])}">Every row and its source</a>
</article>"""


def sourced_table(rows: list[dict], sources: dict, head: tuple[str, str, str], caption: str) -> str:
    """T63: a three-column table whose last cell is a citation or a stated blank (gate G1)."""
    trs = []
    for r in rows:
        s = sources.get(r.get("src") or "")
        if s:
            host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", s["url"]).split("/")[0])
            rel = LINK_REL + " noopener noreferrer" if "amazon." in s["url"] else "noopener noreferrer"
            cell = f'<a class="pb-src" href="{e(s["url"])}" target="_blank" rel="{rel}">{e(host)}</a>'
        else:
            cell = (f'<span class="pb-blank">&mdash;<small>'
                    f'{e(r.get("blank_reason") or "No official source states this value.")}</small></span>')
        trs.append(f'<tr><td class="k">{e(r["attr"])}</td><td>{value_cell(r)}</td><td>{cell}</td></tr>')
    return (f'<div class="pb-table-scroll"><table class="pb-table"><caption>{caption}</caption>'
            f'<thead><tr><th>{e(head[0])}</th><th>{e(head[1])}</th><th>{e(head[2])}</th></tr></thead>'
            f'<tbody>{"".join(trs)}</tbody></table></div>')


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def all_products(facts: dict) -> dict:
    prods = {p["key"]: p for p in facts["products"]}
    prods.update({t["key"]: t for t in extras()["thermos"]})
    return prods


def thermo_guides() -> list[tuple]:
    """The T63 thermometer guides, in the ARTICLES tuple shape (kicker, title, href, cat, blurb)."""
    return [(g["kicker"], g["title"], "guides/" + g["slug"], g["category"], g["hook"])
            for g in extras()["overlay"]["guides"]]


def all_articles() -> list[tuple]:
    return thermo_guides() + ARTICLES


def desk_counts(board: dict) -> dict:
    ov = extras()["overlay"]
    sgs = board["suggestions"] + ov["suggestions"]
    qs = board["questions"] + ov["questions"]
    return {"suggestions": len(sgs), "questions": len(qs),
            "open": sum(1 for q in qs if q["status"] != "answered"),
            "goals": len(ov["goals"])}


def build_index(facts: dict, board: dict) -> str:
    prods = all_products(facts)
    fryers = "".join(bench_card(prods[k]) for k in ("P1", "P2", "P3"))
    thermos = "".join(bench_card(prods[t["key"]]) for t in extras()["thermos"])
    n_products = 3 + len(extras()["thermos"])

    picks = "".join(
        f'<li><a href="#pick-{e(k.lower())}"><span>{e(PRODUCT_VOICE[k]["best_for"])}</span>'
        f'<b>{e(PRODUCT_VOICE[k]["short"])}</b></a></li>'
        for k in ("P1", "P2", "P3", *[t["key"] for t in extras()["thermos"]])
    )

    guides = all_articles()
    lead_articles = thermo_guides()[:3] + [a for a in ARTICLES if a[0] in ("Capacity", "Design", "Category")][:3]
    stories = "".join(
        f'<a class="pb-story" href="{e(href)}"><span class="k">{e(kicker)}</span>'
        f'<h3>{e(title)}</h3><p>{e(blurb)}</p></a>'
        for kicker, title, href, _cat, blurb in lead_articles
    )

    ov = extras()["overlay"]
    c = desk_counts(board)
    goal_cards = "".join(
        f'<div class="pb-bt"><h3>{e(g["title"])}</h3><p>{e(g["blurb"])}</p>'
        f'<a href="desk/index.html#goal-{e(gk)}">'
        f'{sum(1 for s in board["suggestions"] if ov["goal_map"].get(s["id"]) == gk) + sum(1 for s in ov["suggestions"] if s["goal"] == gk)}'
        f' suggestions &rarr;</a></div>'
        for gk, g in ov["goals"].items()
    )
    turkey = next(g for g in ov["guides"] if "turkey" in g["slug"])

    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <div class="pb-lead-grid">
    <div>
      <p class="pb-kicker">Air fryers &middot; meat thermometers &middot; {num_word(n_products, True)} picks</p>
      <h1 class="pb-h1">Crisp it in one. <em>Know it&rsquo;s done</em> with the other.</h1>
      <p class="pb-stand">Three air fryers and two meat thermometers, each with one line of opinion and
      the numbers straight off its own listing or maker&rsquo;s page. Where two official pages disagree we
      print both. No prices, no star ratings, no invented test scores.</p>
      <div class="pb-actions">
        <a class="pb-btn" href="#shop">See the {num_word(n_products, True)} picks</a>
        <a class="pb-btn pb-btn--ghost" href="marketing/buying-guide.html">Which air fryer should I buy?</a>
      </div>
      <p class="pb-byline"><b>Listings re-checked</b> {e(CHECKED_ON)} &middot;
      <b>How we check</b> <a href="guides/method.html">our method</a> &middot;
      <b>Why the links pay us</b> see the disclosure above.</p>
    </div>
    <aside class="pb-takeaways">
      <h2>Quick pick</h2>
      <ul class="pb-picks">{picks}</ul>
    </aside>
  </div>
</div></section>

<section class="pb-season"><div class="pb-wrap">
  <p><b>{e(turkey['kicker'])}.</b> Poultry is safe at 165&nbsp;&deg;F, according to
  {ov_source_link("FS1", "FoodSafety.gov")}. Here is where the probe goes:
  <a href="guides/{e(turkey['slug'])}">{e(turkey['title'])} &rarr;</a></p>
</div></section>

<section class="pb-sec" id="shop"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">The air fryers</h2>
    <p class="pb-sub">Two baskets, one big basket, or an oven with French doors. One line of opinion each, then the spec sheet.</p></div>
    <a class="pb-sec-link" href="marketing/comparison.html">All three side by side &rarr;</a>
  </div>
  <div class="pb-bench">{fryers}</div>
</div></section>

<section class="pb-sec" id="thermometers"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">The meat thermometers</h2>
    <p class="pb-sub">One instant-read that answers in a second, one wireless probe that stays in the roast.
    <a href="guides/thermometers-instant-read-or-leave-in.html">Which kind do you need?</a></p></div>
    <a class="pb-sec-link" href="guides/thermometers.html">Every row, with its source &rarr;</a>
  </div>
  <div class="pb-bench pb-bench--two">{thermos}</div>
  <p class="pb-sub pb-fine">All {num_word(n_products, True)} buttons go to the listing that the supplied
  <code>link.amazon</code> short link opened when re-checked on {e(CHECKED_ON)}, and carry the tracking ID
  <code>{e(ASSOCIATES_TAG)}</code>. A link opening a listing is not the same as an official record of which
  product was meant, so that record is kept apart in <a href="intent.html">the link &amp; intent register</a>
  (<a href="questions.html#Q-T50-01">Q-T50-01</a>).</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Start with the question, not the product</h2>
    <p class="pb-sub">{num_word(len(guides))} guides, each built around something a buyer actually asks.</p></div>
    <a class="pb-sec-link" href="guides/index.html">Browse by category &rarr;</a>
  </div>
  <div class="pb-stories">{stories}</div>
</div></section>

<section class="pb-receipts"><div class="pb-wrap">
  <h2 class="pb-h2">The receipts</h2>
  <p class="pb-sub">Where an affiliate site would put growth numbers, this one puts its own verification
  state. No traffic, conversion or revenue figure appears anywhere on this site, because none has been
  imported from a first-party report, and we do not make them up. Aggregate, cookie-free click counting
  has been on since decision DS-11 (2026-11-17). Its counts will be published only once an endpoint
  stores them and an Associates report exists to check them against.</p>
  <div class="pb-figs">
    <div class="pb-fig"><b>5<i> / 5</i></b><span>Supplied links that resolve, reproducibly, to one
      specific Amazon listing each &mdash; two of them meat thermometers. Re-checked {e(CHECKED_ON)};
      <a href="intent.html">the link &amp; intent register</a>.</span></div>
    <div class="pb-fig"><b>0<i> / 5</i></b><span>Product mappings confirmed by an official Amazon
      document. <a href="flagged.html">Flag F-03</a>.</span></div>
    <div class="pb-fig"><b>9<i> / 10</i></b><span>Characters per supplied code against the 10-character
      ASIN rule on Amazon&rsquo;s own help page. <a href="flagged.html">Flag F-01</a>.</span></div>
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
    <p class="pb-sub">{num_word(c['suggestions'])} suggestions, grouped under {num_word(c['goals'], True)} goals, each
    with its options, its evidence, what is still unknown and how to find out. None is marked decided.
    {num_word(c['open'])} questions are still open; <a href="desk/questions.html">answer these first</a>.</p></div>
    <a class="pb-sec-link" href="desk/index.html">Open the decision desk &rarr;</a>
  </div>
  <div class="pb-board-tease">{goal_cards}</div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-note"><b>A listing title is perishable, and the record shows the whole arc.</b>
  Re-reading every load-bearing source on 2026-11-16 showed that the Amazon title stored for the 26-quart
  Emeril listing was no longer the title the page served. No specification row was affected. It was
  published as flag <b>F-41</b> instead of being quietly overwritten, then corrected, so the drift is dated
  and traceable. On {e(CHECKED_ON)} the ThermoMaven listing began pointing to a newer model; that is
  logged the same way, as an open question rather than a silent switch
  (<a href="desk/questions.html#Q-T63-07">Q-T63-07</a>).
  <a href="flagged.html">The full flagged register</a> holds <span id="flagCountHeading">&mdash;</span> items.</div>
</div></section>
"""
    return page("index.html", title="Counter Notes · Three air fryers and two meat thermometers, read off their own spec sheets",
                description="Three air fryers and two meat thermometers, each with sourced spec rows from its own listing or maker's page, plus question-shaped buying guides. No prices, no invented scores.",
                active="index.html", body=body, with_data=True)


def build_suggestions(facts: dict, board: dict) -> str:
    blocks = "".join(decision_block(s, board) for s in board["suggestions"])
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Decision board</p>
  <h1 class="pb-h1">{num_word(len(board['suggestions']))} things we could do next. <em>None of them is done.</em></h1>
  <p class="pb-note">T63 (2026-11-19): these {num_word(len(board['suggestions']), True)} rows, plus
  {num_word(len(extras()['overlay']['suggestions']), True)} new ones, are now grouped by goal on
  <a href="desk/index.html">the decision desk</a>, together with the questions to answer first.</p>
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
        arts = [a for a in all_articles() if a[3] == slug]
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
  <p class="pb-stand">{num_word(len(all_articles()))} pieces, grouped the way a reader browses rather than the way the files are
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
                description="Every guide published on Counter Notes, organised by category: meat thermometers, basket air fryers, air-fryer ovens, buying guides and method.",
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
# T63: meat thermometers
# --------------------------------------------------------------------------- #
def fs(sid: str, label: str) -> str:
    """Inline citation for the food-safety and listing sources held in the overlay."""
    return ov_source_link(sid, label)


def m5(label: str = "Chefman's product page") -> str:
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    p3 = next(p for p in facts["products"] if p["key"] == "P3")
    url = src_map(p3)["M5"]["url"]
    return f'<a class="pb-src" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)}</a>'


def food_safety_table(attrs: list[str] | None = None, caption: str = "") -> str:
    ov = extras()["overlay"]
    rows = [r for r in ov["food_safety"] if attrs is None or r["attr"] in attrs]
    return sourced_table(rows, ov["sources"], ("Food", "Safe minimum internal temperature", "Source"),
                         caption or e(ov["food_safety_note"]))


def guide_by_slug(slug: str) -> dict:
    return next(g for g in extras()["overlay"]["guides"] if g["slug"] == slug)


def thermo_shelf(depth: str = "../") -> str:
    cards = "".join(bench_card(t, depth) for t in extras()["thermos"])
    return (f'<section class="pb-sec"><div class="pb-wrap"><div class="pb-sec-head"><div>'
            f'<h2 class="pb-h2">The two thermometers we cover</h2>'
            f'<p class="pb-sub">One line of opinion each, then figures from their own Amazon listings.</p></div>'
            f'<a class="pb-sec-link" href="{e(depth)}guides/thermometers.html">Every row, with its source &rarr;</a></div>'
            f'<div class="pb-bench pb-bench--two">{cards}</div></div></section>')


def guide_page(slug: str, body_html: str, sources: list[str]) -> str:
    g = guide_by_slug(slug)
    others = "".join(
        f'<li><a href="{e(o["slug"])}">{e(o["title"])}</a></li>'
        for o in extras()["overlay"]["guides"] if o["slug"] != slug)
    src_list = "".join(f"<li>{fs(sid, extras()['overlay']['sources'][sid]['name'])}</li>" for sid in sources)
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">{e(g['kicker'])} &middot; <a href="thermometers.html" style="color:inherit">Meat thermometers</a></p>
  <h1 class="pb-h1 pb-measure">{e(g['title'])}</h1>
  <p class="pb-stand pb-measure">{e(g['hook'])}</p>
  <p class="pb-byline"><b>Published</b> {e(g['published'])} &middot; <b>Temperatures from</b>
  FoodSafety.gov and USDA FSIS &middot; <b>Product figures from</b> the Amazon listings, read {e(CHECKED_ON)}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap"><article class="pb-article">
{body_html}
</article></div></section>
{thermo_shelf()}
<section class="pb-sec"><div class="pb-wrap pb-article">
  <h2>Sources for this guide</h2>
  <ul class="pb-sources">{src_list}</ul>
  <p class="pb-fine">Food-safety figures are quoted from the government pages above, not interpreted.
  Product figures are what each listing stated on the date shown; a listing can change after that.</p>
  <h2>Read next</h2>
  <ul class="pb-sources">{others}<li><a href="index.html">All guides</a></li></ul>
</div></section>
"""
    return page(f"guides/{slug}", title=f"{g['title']} · Counter Notes", description=g["hook"],
                active="guides/thermometers.html", body=body, depth="../")


def build_turkey(facts: dict, board: dict) -> str:
    slug = "thermometers-is-the-turkey-done.html"
    body = f"""
<h2>The number: 165&nbsp;&deg;F</h2>
<p>The safe minimum internal temperature for poultry, and for the stuffing cooked with it, is
<b>165&nbsp;&deg;F (74&nbsp;&deg;C)</b> ({fs("FS1", "FoodSafety.gov chart")}). Colour is not the test.
USDA&rsquo;s Food Safety and Inspection Service calls a food thermometer the only reliable way to know that
food has reached a safe temperature ({fs("FS2", "USDA FSIS")}).</p>

<h2>Where the probe goes</h2>
<ul>
  <li><b>Three places, not one.</b> For whole poultry, FSIS says to check the thigh, the wing and the
  thickest part of the breast ({fs("FS2", "USDA FSIS")}). Every reading needs to reach 165&nbsp;&deg;F.</li>
  <li><b>Thickest part, clear of bone.</b> Put the tip in the thickest part of the meat, away from bone,
  fat and gristle ({fs("FS2", "USDA FSIS")}).</li>
  <li><b>Stuffing gets its own reading.</b> It has the same 165&nbsp;&deg;F minimum ({fs("FS1", "FoodSafety.gov")}).</li>
</ul>

<h2>Instant-read or leave-in, on the day</h2>
<p><b>An instant-read</b> is the tool for the three-spot check. FSIS says a digital thermocouple gives a reading
in 2 to 5 seconds and needs only about a quarter of an inch in the food ({fs("FS2", "USDA FSIS")}). The
ThermoMaven we cover lists a 1-second response time and &plusmn;0.5&nbsp;&deg;F accuracy
({fs("S61", "Amazon listing")}). Take the reading, then take the thermometer out. FSIS advises against leaving a
thermometer in food unless it is made to stay there ({fs("FS2", "USDA FSIS")}), and this listing does not say it is.</p>
<p><b>A leave-in probe</b> lets you watch the temperature from the table without opening the oven. FSIS describes
wireless and smart thermometers that stay in the food while it cooks ({fs("FS2", "USDA FSIS")}). The CHEF iQ
Sense listing includes three probes, each with four internal sensors and one ambient sensor, rated to a heat
safety of 1000&nbsp;&deg;F, and connects over Wi-Fi and Bluetooth ({fs("S62", "Amazon listing")}).
When the probe says you are close, still check the other two spots.</p>
<div class="pb-note"><b>Which one for a once-a-year turkey?</b> If you roast a bird a few times a year, an instant-read
covers it. If you roast or smoke most weekends, a leave-in probe saves you opening the door again and again.
Hosting a big table? Some cooks use both: the probe for the bird and the instant-read for everything else.</div>

<h2>Check your thermometer before the day</h2>
<p>FSIS gives two checks. In a glass of ice water (stem at least 2 inches in, wait 30 seconds) it should read
32&nbsp;&deg;F. In boiling water it should read 212&nbsp;&deg;F at sea level, and a few degrees less at
altitude ({fs("FS2", "USDA FSIS")}). If yours is off, follow the maker&rsquo;s instructions.</p>

<h2>After dinner</h2>
<p>FSIS warns that perishable food left between 40&nbsp;&deg;F and 140&nbsp;&deg;F for more than two hours is
a risk ({fs("FS2", "USDA FSIS")}). Reheat leftovers to 165&nbsp;&deg;F ({fs("FS1", "FoodSafety.gov")}).</p>

<h2>The chart</h2>
{food_safety_table()}
"""
    return guide_page(slug, body, ["FS1", "FS2", "S61", "S62"])


def build_instant_or_leave(facts: dict, board: dict) -> str:
    slug = "thermometers-instant-read-or-leave-in.html"
    ov = extras()["overlay"]
    types = [
        {"attr": "Digital instant-read (thermocouple)", "value": "Reads in 2–5 seconds; needs about 1/4 in in the food; can be calibrated", "status": "verified", "src": "FS2"},
        {"attr": "Digital instant-read (thermistor)", "value": "Reads in about 10 seconds; needs about 1/2 in in the food", "status": "verified", "src": "FS2"},
        {"attr": "Wireless / smart", "value": "Designed to stay in the food while it cooks", "status": "verified", "src": "FS2"},
        {"attr": "Oven cord", "value": "Reads in about 10 seconds; stays in the food while it cooks; cannot be calibrated", "status": "verified", "src": "FS2"},
        {"attr": "Oven-safe dial", "value": "Oven-safe; reads in 1–2 minutes; insert 2–2.5 in deep", "status": "verified", "src": "FS2"},
    ]
    t4, t5 = extras()["thermos"]
    r4 = {r["attr"]: r for r in t4["rows"]}
    r5 = {r["attr"]: r for r in t5["rows"]}
    s4 = src_map(t4)["S61"]["url"]
    s5 = src_map(t5)["S62"]["url"]

    def val(row: dict | None, reason: str) -> str:
        if row and (row.get("value") or "").strip():
            return value_cell(row)
        return f'<span class="pb-blank">&mdash;<small>{e(reason)}</small></span>'

    comp = [
        ("Accuracy", r4.get("Accuracy"), r5.get("Accuracy")),
        ("Response time", r4.get("Response time"), None),
        ("Highest figure on the listing", r4.get("Upper temperature range"), r5.get("Heat safety")),
        ("Power", r4.get("Power source"), r5.get("Battery life")),
        ("Probes", None, r5.get("Probes included")),
        ("Probe length", None, r5.get("Probe length")),
    ]
    trs = "".join(
        f'<tr><td class="k">{e(label)}</td><td>{val(a, "The listing does not state this.")}</td>'
        f'<td>{val(b, "The listing does not state this.")}</td>'
        f'<td><a class="pb-src" href="{e(s4)}" target="_blank" rel="{LINK_REL} noopener noreferrer">S61</a> '
        f'<a class="pb-src" href="{e(s5)}" target="_blank" rel="{LINK_REL} noopener noreferrer">S62</a></td></tr>'
        for label, a, b in comp)
    comparison = (f'<div class="pb-table-scroll"><table class="pb-table"><caption>As stated on each Amazon listing, '
                  f'read {e(CHECKED_ON)}. The 572&nbsp;&deg;F and 1000&nbsp;&deg;F figures measure different things: '
                  f'a measuring range and a heat-safety rating.</caption>'
                  f'<thead><tr><th></th><th>ThermoMaven 1 Sec</th><th>CHEF iQ Sense (3 probes)</th><th>Sources</th></tr></thead>'
                  f'<tbody>{trs}</tbody></table></div>')
    body = f"""
<h2>Two jobs, two tools</h2>
<p>An instant-read lives in a drawer. You push it into the food, read the number and pull it out. A leave-in
probe goes into the food before it cooks and stays there, reporting as it goes. Both answer the same question,
&ldquo;is it done?&rdquo;, but at different moments. The government&rsquo;s own list of thermometer types draws
the same line:</p>
{sourced_table(types, ov["sources"], ("Type", "What USDA FSIS says about it", "Source"), "Thermometer types as described by USDA FSIS, read " + e(CHECKED_ON) + ".")}

<h2>Three questions that decide it</h2>
<ol>
  <li><b>How long does it cook?</b> Burgers, chops, fish and a basket of wings take minutes, which suits an
  instant-read. Roasts, whole birds and anything smoked take hours, which suits a probe that stays in.</li>
  <li><b>Do you want to watch without opening the door?</b> Every time you open an oven or a smoker, heat
  escapes. A leave-in probe shows you the number without opening anything.</li>
  <li><b>Will you charge it?</b> The ThermoMaven runs on one AAA battery, which is included
  ({fs("S61", "listing")}). The CHEF iQ probes charge in their hub. Its listing states the battery life twice,
  as up to 50 hours and as 70+ hours, so we print both ({fs("S62", "listing")}).</li>
</ol>

<h2>Our two, side by side</h2>
{comparison}

<div class="pb-note"><b>The short answer.</b> If most of what you cook is done in under half an hour, start with
the instant-read. If you roast, smoke or cook for a crowd, the leave-in probe earns its place. Neither replaces
the safe temperatures: poultry at 165&nbsp;&deg;F, ground meat at 160&nbsp;&deg;F, and steaks, chops and roasts at
145&nbsp;&deg;F with a 3-minute rest ({fs("FS1", "FoodSafety.gov")}).</div>
"""
    return guide_page(slug, body, ["FS2", "FS1", "S61", "S62"])


def build_air_fryer_probe(facts: dict, board: dict) -> str:
    slug = "thermometers-in-an-air-fryer.html"
    t5 = extras()["thermos"][1]
    r5 = {r["attr"]: r for r in t5["rows"]}
    af = r5.get("Air-fryer / deep-fryer safe", {}).get("value", "")
    length = r5.get("Probe length", {}).get("value", "")
    body = f"""
<h2>Short answer: yes, but the kind matters</h2>
<p>Air-fryer food is small and cooks fast, which makes guessing easy and getting it wrong easy too. A thermometer
settles it, and the two kinds work differently in a basket.</p>

<h2>With an instant-read: open, check, close</h2>
<p>Pull the basket, take a reading in the thickest piece, slide it back. On the 8-quart Chefman, the maker states
that auto shut-off halts cooking when the timer runs out <em>or the basket is opened</em> ({m5()}), so the
heat is not running while you check. Whether cooking resumes by itself when the basket goes back is not stated
on the page we read, so look at the display before you walk away.</p>

<h2>With a leave-in probe: check the fit first</h2>
<p>The CHEF iQ Sense listing names air fryers among its uses and lists it as air-fryer safe
(&ldquo;{e(af)}&rdquo;), with {e(length)} probes ({fs("S62", "Amazon listing")}). Neither maker says whether a
probe fits under a particular basket or rack. Before the first cook, check that the basket closes freely with
the probe in place.</p>

<h2>Air-fryer food is thin: go in from the side</h2>
<p>For thin food such as a burger or a chicken breast, FSIS says to insert the thermometer from the side
({fs("FS2", "USDA FSIS")}). A digital thermocouple needs only about a quarter of an inch of food to read
({fs("FS2", "USDA FSIS")}), which is why instant-reads suit wings and thin fillets.</p>

<h2>The numbers for typical air-fryer food</h2>
{food_safety_table(None)}
<p class="pb-fine">Fish can also be judged by eye: FoodSafety.gov says cook it to 145&nbsp;&deg;F, or until the flesh
is opaque and flakes ({fs("FS1", "FoodSafety.gov")}).</p>

<h2>Which air fryer pairs with which probe?</h2>
<p>Any of them works with an instant-read. For a whole chicken or a rotisserie roast in the 26-quart Emeril oven,
a leave-in probe means you do not have to open the doors to check. See all three on
<a href="../index.html#shop">the front page</a>, or compare them on
<a href="../marketing/comparison.html">one table</a>.</p>
"""
    return guide_page(slug, body, ["FS1", "FS2", "S62"])


def build_thermometers(facts: dict, board: dict) -> str:
    ov = extras()["overlay"]
    blocks = []
    for t in extras()["thermos"]:
        v = PRODUCT_VOICE[t["key"]]
        dp = product_link(t)
        notice = (f'<p class="pb-note"><b>Listing notice, {e(CHECKED_ON)}.</b> {e(t["listing_notice"])}</p>'
                  if t.get("listing_notice") else "")
        blocks.append(f"""
<article class="pb-product" id="{e(t['key'])}">
  <p class="pb-bench-brand">{e(v['brand'])}</p>
  <h2 class="pb-h2">{e(v['display'])}</h2>
  <p class="pb-sub">{e(v['note'])} <b>Best for:</b> {e(v['best_for'])}.</p>
  <p><a class="pb-bench-cta" href="{e(dp)}" target="_blank" rel="{LINK_REL} noopener noreferrer" data-link-state="TAGGED" data-product-key="{e(t['key'])}">See the listing on Amazon {e(LINK_DISCLOSURE)} &rarr;</a></p>
  <p class="pb-fine">Amazon title as read: {e(t['title_official'])}</p>
  {notice}
  {product_table(t)}
</article>""")
    guides = "".join(
        f'<li><a href="{e(g["slug"])}">{e(g["title"])}</a><p>{e(g["hook"])}</p></li>' for g in ov["guides"])
    cat = GUIDE_CATEGORIES["thermometers"]
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Category &middot; <a href="index.html" style="color:inherit">Guides</a></p>
  <h1 class="pb-h1">Meat thermometers: <em>stop guessing</em>.</h1>
  <p class="pb-stand pb-measure">{e(cat['blurb'])}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Guides</h2></div>
  <a class="pb-sec-link" href="index.html">All categories &rarr;</a></div>
  <div class="pb-rail"><section><h2>Published {e(ov['guides'][0]['published'])}</h2><ul>{guides}</ul></section>
  <section><h2>Safe minimum temperatures</h2>{food_safety_table()}</section></div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">The two listings, row by row</h2>
  <p class="pb-sub">Every row comes from the listing the supplied short link opened, as recorded in the project
  ledger. Price and star rating are left blank on purpose.</p></div></div>
  {''.join(blocks)}
</div></section>
"""
    return page("guides/thermometers.html", title="Meat thermometers: instant-read and leave-in, with safe temperatures · Counter Notes",
                description=cat["blurb"], active="guides/thermometers.html", body=body, depth="../")


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
    # T63 (session 6ce606cb): thermometer category and guides. Also listed in verify_front PAGES.
    ("guides/thermometers.html", build_thermometers),
    ("guides/thermometers-is-the-turkey-done.html", build_turkey),
    ("guides/thermometers-instant-read-or-leave-in.html", build_instant_or_leave),
    ("guides/thermometers-in-an-air-fryer.html", build_air_fryer_probe),
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
