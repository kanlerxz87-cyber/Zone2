#!/usr/bin/env python3
"""Render the marketing set from marketing/data/facts.json.

Design rules, each enforced here rather than trusted:

1.  **No inferred value ever reaches the page.**  A row whose ``status`` is ``unverified`` or
    ``withheld_by_policy`` renders an explicit ``UNVERIFIED`` / ``WITHHELD`` cell with its stated reason.
    A blank string is never emitted as if it were a fact.
2.  **Every printed value carries the official source it came from**, as a link.  A row with a value but no
    source is a hard build error - the build stops instead of publishing it.
3.  **A conflict is published as a conflict.**  Two official statements that disagree are both shown, with
    both sources, and the row is marked ``CONFLICT``.  The renderer does not pick a winner silently.
4.  **Every affiliate link goes through ``tools/link_builder.py``.**  Since the owner supplied the
    Associates tag (2026-11-17), that means ``build_product_link()`` with ``ASSOCIATES_TAG`` - a tagged
    Special Link whose format the builder validates.  The renderer refuses to hand-write ``amazon.com/dp/``
    URLs, and citation links (class="src") stay unmonetized by design.
5.  **No price is ever printed.**  Price rows are ``withheld_by_policy`` and the verifier re-checks the
    rendered HTML for money patterns in a buying context.

Usage:
    python3 tools/build_marketing.py            # write marketing/*.html
    python3 tools/build_marketing.py --check    # fail if committed output differs from a fresh build

Deterministic: no network, no clock, no randomness.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from link_builder import (  # noqa: E402
    ASSOCIATES_TAG,
    REQUIRED_SITE_DISCLOSURE,
    LinkPolicyError,
    audit_html,
    build_product_link,
)

DATA = REPO / "marketing" / "data" / "facts.json"
OUT = REPO / "marketing"
CSS = "assets/marketing.css"
SITE_NAME = "Zone2 Field Notes"
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/marketing/"
# The site-wide social preview card (T58, 2026-11-17). A brand card, deliberately not product
# photography — the product-imagery rights question is still open (Q-10).
OG_IMAGE = "https://kanlerxz87-cyber.github.io/Zone2/assets/img/og.jpg"

FACTS = json.loads(DATA.read_text(encoding="utf-8"))
PRODUCTS = {p["key"]: p for p in FACTS["products"]}
AS_OF = FACTS["verified_utc"]
# --------------------------------------------------------------------------- editorial layer
#
# Everything below is driven by marketing/data/editorial.json. No marketing page is hand-written:
# `tools/build_marketing.py --check` fails the build when committed HTML differs from a fresh render,
# so the copy, the improvement board and the question register are data, not files.

EDITORIAL_PATH = REPO / "marketing" / "data" / "editorial.json"
EDITORIAL = json.loads(EDITORIAL_PATH.read_text(encoding="utf-8"))
BRAND = EDITORIAL["brand"]
VOICE = EDITORIAL["voice"]
DESIGN = EDITORIAL["design"]
GUIDES = EDITORIAL["guides"]
GUIDE_BY_SLUG = {g["slug"]: g for g in GUIDES}
SUGGESTIONS = EDITORIAL["suggestions"]
QUESTIONS = EDITORIAL["questions"]
PROMPT_BRIEF = EDITORIAL["prompt_brief"]
BEFORE_AFTER = EDITORIAL["before_after"]
VERIFIED_TODAY = EDITORIAL["verified_today"]
PRODUCT_EDITORIAL = EDITORIAL.get("products", {})
ED_AS_OF = EDITORIAL["as_of"]



STATUS_LABEL = {
    "verified": ("OK", "pill-ok"),
    "partial": ("PARTIAL", "pill-warn"),
    "conflict": ("CONFLICT", "pill-flag"),
    "unverified": ("UNVERIFIED", "pill-warn"),
    "withheld_by_policy": ("WITHHELD", "pill-warn"),
}


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


class BuildError(RuntimeError):
    """Raised instead of publishing a value that has no official source."""


def source_registry() -> dict[str, dict]:
    reg = {}
    for product in FACTS["products"]:
        for src in product["official_sources"]:
            reg[src["id"]] = src
    return reg


SOURCES = source_registry()


def source_link(src_id: str | None) -> str:
    if not src_id:
        return ""
    src = SOURCES.get(src_id)
    if not src:
        raise BuildError(f"row cites unknown source id {src_id!r}; refusing to publish an unresolvable citation")
    host = src["url"].split("/")[2]
    kind = "manufacturer" if src["kind"] == "manufacturer" else "Amazon listing"
    # A citation pointing at an Amazon marketplace page is marked sponsored as well. It earns nothing
    # (there is no tag), but over-declaring a commercial relationship is the safe direction, and it keeps
    # the repository's existing "no amazon.com/dp/ link without rel=sponsored" rule literally true.
    rel = "sponsored nofollow noopener noreferrer" if host.endswith("amazon.com") else "noopener noreferrer nofollow"
    return (
        f'<a class="src" href="{esc(src["url"])}" target="_blank" rel="{rel}">'
        f'{esc(src_id)} · {esc(host)}<span class="src-kind">{esc(kind)}</span></a>'
    )


def product_link(product: dict) -> str:
    """Emit the product link through link_builder, never by hand.

    T58 (session `7264f3c2`, 2026-11-17): the owner supplied the Associates tag
    (``tools/link_builder.ASSOCIATES_TAG``), so this emits a tagged Special Link instead of the
    preview placeholder every page carried before. The builder validates the ASIN, the tag format
    and the absence of competing attribution parameters; the marketing verifier fails any sponsored
    product link that reaches Amazon without that tag, and forbids tags on citation links
    (class="src"), which stay unmonetized evidence by design.
    """
    link = build_product_link(
        product["asin"],
        ASSOCIATES_TAG,
        link_text=f'{product["manufacturer_product_name"]} (see this model\'s listing)',
    )
    href = esc(link.href)
    text = esc(link.text)
    return (
        f'<a class="sponsored-link" href="{href}" rel="sponsored nofollow" target="_blank" '
        f'referrerpolicy="no-referrer-when-downgrade" data-link-state="TAGGED" '
        f'data-product-key="{esc(product["key"])}">{text}</a>'
        f'<span class="link-note">Special Link \u2014 Associates tag {esc(ASSOCIATES_TAG)}</span>'
        # R-02: a clear, conspicuous statement adjacent to the affiliate link itself.
        f'<span class="disclosure disclosure--link" data-rule="R-02">{esc(FACTS["link_level_disclosure"])}</span>'
    )


def status_cell(row: dict) -> str:
    label, klass = STATUS_LABEL[row["status"]]
    if row["status"] in ("unverified", "withheld_by_policy"):
        reason = esc(row.get("blank_reason", "no official source states this value"))
        return f'<td class="cell-unverified"><span class="pill {klass}">{label}</span><div class="row-note">{reason}</div></td>'
    return f'<td><span class="pill {klass}">{label}</span></td>'


def value_cell(row: dict) -> str:
    if row["status"] in ("unverified", "withheld_by_policy"):
        # Never print a value for these states - that is the whole point of the state.
        return '<td class="cell-blank">—</td>'
    out = f'<strong>{esc(row["value"])}</strong>'
    if row.get("detail"):
        out += f'<div class="row-note">{esc(row["detail"])}</div>'
    return f"<td>{out}</td>"


def spec_table(product: dict, *, key_prefix: str) -> str:
    """A spec table where every row ends in its official source (or an explicit blank + why)."""
    rows = []
    for i, row in enumerate(product["rows"]):
        if row["status"] in ("unverified", "withheld_by_policy"):
            if not row.get("blank_reason"):
                raise BuildError(f'{product["key"]} row {row["attr"]!r} is blank with no stated reason')
        elif not row.get("src"):
            raise BuildError(
                f'{product["key"]} row {row["attr"]!r} prints {row["value"]!r} but cites no official source; '
                "refusing to publish it"
            )
        src_cells = source_link(row.get("src"))
        alt = row.get("src_alt")
        if alt:
            src_cells += source_link(alt)
        if not src_cells:
            if row["status"] == "withheld_by_policy":
                src_cells = '<span class="pill pill-warn">WITHHELD BY POLICY</span>'
            elif row["status"] == "unverified":
                src_cells = '<span class="pill pill-warn">NO SOURCE</span>'
            else:
                src_cells = ""
        rows.append(
            f'<tr id="{key_prefix}-r{i + 1}">'
            f'<th scope="row">{esc(row["attr"])}</th>'
            f'{value_cell(row)}'
            f'{status_cell(row)}'
            f'<td class="cell-src">{src_cells}</td>'
            f"</tr>"
        )
    return (
        '<table class="data">'
        "<caption>Manufacturer specification, read off the official pages on "
        f"{esc(AS_OF)}. Every row ends in the page it came from, or is marked blank with the reason.</caption>"
        "<thead><tr><th>Attribute</th><th>Value</th><th>Status</th><th>Official source</th></tr></thead>"
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def feature_list(product: dict) -> str:
    src = SOURCES.get(product["features_source"])
    if not src:
        raise BuildError(f'{product["key"]} feature list cites no resolvable source')
    items = "".join(f"<li>{esc(f)}</li>" for f in product["features_official"])
    return (
        f'<ul class="features">{items}</ul>'
        f'<p class="row-note">Features as stated on the <a class="src" href="{esc(src["url"])}" '
        f'target="_blank" rel="noopener noreferrer nofollow">{esc(src["name"])}</a>.</p>'
    )


# --------------------------------------------------------------------------- page shell

# Navigation is data: marketing/data/editorial.json -> "nav". Adding a page without a nav
# entry leaves it orphaned, which the marketing gate reports as a failure.
NAV = [(href, label) for href, label in EDITORIAL["nav"]]




def nav_html(root: str, here: str) -> str:
    parts = []
    for href, label in NAV:
        cls = ' class="active"' if href == here else ""
        parts.append(f'<a href="{root}{href}"{cls}>{esc(label)}</a>')
    return "".join(parts)


def cite(src_ids) -> str:
    """Citations that each resolve to one of the official pages recorded in facts.json."""
    if not src_ids:
        return ""
    return '<span class="cites">' + "".join(source_link(s) for s in src_ids) + "</span>"


def ext_link(label: str, url: str) -> str:
    host = url.split("/")[2]
    rel = "sponsored nofollow noopener noreferrer" if host.endswith("amazon.com") else "noopener noreferrer nofollow"
    return (
        f'<a class="src" href="{esc(url)}" target="_blank" rel="{rel}">'
        f"{esc(label)}</a>"
    )


def fact_value(product: dict, *candidates: str):
    """First row whose attribute matches a candidate. Never invents a value."""
    for cand in candidates:
        for row in product["rows"]:
            if row["attr"] == cand or row["attr"].startswith(cand):
                return row
    return None


def serving_claim(product: dict) -> dict:
    """The published household size, read out of the manufacturer's own feature list."""
    for feat in product.get("features_official", []):
        if "4" in feat and "6" in feat and "people" in feat:
            return {
                "attr": "Published household size",
                "value": feat[feat.index("sized") :] if "sized" in feat else feat,
                "status": "verified",
                "src": product.get("features_source"),
            }
    return {
        "attr": "Published household size",
        "value": "",
        "status": "unverified",
        "src": None,
        "blank_reason": "Neither official page states a servings figure for this model.",
    }


def value_html(row: dict) -> str:
    """Inner HTML of a comparison cell: the value with its source, or a dash with the reason."""
    if row["status"] in ("unverified", "withheld_by_policy"):
        reason = esc(row.get("blank_reason", "no official source states this value"))
        return f'<span class="dash">—</span><span class="cell-note">{reason}</span>'
    label, klass = STATUS_LABEL[row["status"]]
    out = f'<strong>{esc(row["value"])}</strong>'
    if row["status"] not in ("verified",):
        out += f'<span class="pill {klass}">{label}</span>'
    if row.get("detail"):
        out += f'<span class="cell-note">{esc(row["detail"])}</span>'
    out += cite([row["src"]] if row.get("src") else [])
    return out


def facts_table(products, spec, *, caption: str, key: str) -> str:
    """A comparison table sourced cell by cell, built only from facts.json rows.

    Values are never typed into the guide copy, so a guide cannot drift from the product page it
    summarises: the row either exists in the fact base (with its official source) or it prints a
    dash and the recorded reason for the blank.
    """
    head = "".join(f'<th>{esc(PRODUCTS[pk]["manufacturer_product_name"])}</th>' for pk in products)
    rows = []
    for i, (label, candidates) in enumerate(spec, start=1):
        cells = []
        for pk in products:
            p = PRODUCTS[pk]
            row = serving_claim(p) if candidates == ["@serving"] else fact_value(p, *candidates)
            if row is None:
                row = {
                    "attr": label, "value": "", "status": "unverified", "src": None,
                    "blank_reason": "Not stated on the official pages we read.",
                }
            cells.append(f"<td>{value_html(row)}</td>")
        rows.append(f'<tr id="{key}-{i}"><th scope="row">{esc(label)}</th>{"".join(cells)}</tr>')
    return (
        '<table class="data compare">'
        f"<caption>{esc(caption)}</caption>"
        f"<thead><tr><th>Attribute</th>{head}</tr></thead>"
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_table(block: dict) -> str:
    """A table specified in editorial.json. A row may end with a list of source ids."""
    rows = []
    has_src_col = False
    for i, raw in enumerate(block["rows"], start=1):
        srcs = next((c for c in raw if isinstance(c, list)), None)
        cells = [c for c in raw if not isinstance(c, list)]
        if srcs:
            has_src_col = True
        tds = "".join(f"<td>{esc(c)}</td>" for c in cells)
        src_cell = f'<td class="cell-src">{"".join(source_link(s) for s in srcs)}</td>' if srcs else "<td></td>"
        rows.append(f'<tr id="{esc(block.get("key", "t"))}-{i}">{tds}{src_cell}</tr>')
    src_head = "<th>Official page</th>" if has_src_col else ""
    return (
        '<table class="data">'
        f"<caption>{esc(block.get('caption', ''))}</caption>"
        f"<thead><tr>{''.join(f'<th>{esc(h)}</th>' for h in block['head'])}{src_head}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
    )


def render_blocks(blocks, *, key: str) -> str:
    out = []
    for i, b in enumerate(blocks):
        kind = b.get("kind")
        bid = f"{key}-b{i + 1}"
        if kind == "prose":
            srcs = ",".join(b.get("src", []))
            out.append(
                f'<p class="claim" id="{bid}" data-src="{esc(srcs)}">{b["html"]}{cite(b.get("src"))}</p>'
            )
        elif kind == "take":
            out.append(
                f'<aside class="take" id="{bid}" role="note"><p class="take-label">Our take — '
                'an editorial judgement, not a claim the manufacturer makes</p>'
                f'<p class="judgement">{b["html"]}</p></aside>'
            )
        elif kind == "list":
            srcs = ",".join(b.get("src", []))
            items = "".join(f'<li class="claim" data-src="{esc(srcs)}">{esc(it)}</li>' for it in b["items"])
            out.append(f'<ul class="points" id="{bid}">{items}{cite(b.get("src"))}</ul>')
        elif kind == "table":
            sub = dict(b)
            sub.setdefault("key", bid)
            out.append(f'<figure class="tbl" id="{bid}">{render_table(sub)}<figcaption>Transcribed from the '
                       f"pages linked in the last column; nothing in this table is averaged or rounded.</figcaption></figure>")
        elif kind == "capacity_table":
            out.append(
                f'<figure class="tbl" id="{bid}">'
                + facts_table(
                    ["P1", "P3", "P2"],
                    [
                        ("Capacity (as published)", ["Capacity"]),
                        ("Published household size", ["@serving"]),
                        ("Power", ["Power"]),
                        ("Temperature range", ["Temperature"]),
                    ],
                    caption="Capacity, power and range exactly as each official page publishes them. The capacity "
                    "figure is the brand's own measurement, which is why the household-size row matters more.",
                    key=bid,
                )
                + "</figure>"
            )
        elif kind == "duo_table":
            out.append(
                f'<figure class="tbl" id="{bid}">'
                + facts_table(
                    ["P1", "P3"],
                    [
                        ("Capacity (as published)", ["Capacity"]),
                        ("Power", ["Power"]),
                        ("Temperature range", ["Temperature"]),
                        ("Footprint", ["Dimensions"]),
                        ("Weight", ["Weight"]),
                        ("Presets and controls", ["Presets", "Control type"]),
                        ("What the design adds", ["Sync Finish", "Shake reminder"]),
                    ],
                    caption="Twin 3 Qt baskets against a single 8 Qt chamber, on the numbers both brands publish.",
                    key=bid,
                )
                + "</figure>"
            )
        elif kind == "footprint_table":
            out.append(
                f'<figure class="tbl" id="{bid}">'
                + facts_table(
                    ["P1", "P3", "P2"],
                    [
                        ("Product dimensions", ["Dimensions"]),
                        ("Weight", ["Weight"]),
                        ("Capacity (as published)", ["Capacity"]),
                        ("Door or drawer", ["Door / window", "Door", "Finish"]),
                        ("Basket care", ["Basket care"]),
                    ],
                    caption="The fit numbers. Where a brand publishes centimetres as well, both are transcribed; "
                    "where it publishes nothing, the cell is blank and says so.",
                    key=bid,
                )
                + "</figure>"
            )
        else:
            raise BuildError(f"unknown block kind {kind!r} in {key}")
    return "\n".join(out)


# --------------------------------------------------------------------------- page shell


def json_ld(title: str, description: str, url: str, crumbs, *, published: str | None = None,
            modified: str | None = None) -> str:
    """Article + BreadcrumbList only. Product / Review / AggregateRating markup is deliberately
    absent: nobody has used these products, and Google's review-snippet guidelines require a
    genuine, user-sourced rating behind that markup. See DS-07 and question Q-11."""
    graph = [
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "description": description,
            "datePublished": f"{published or ED_AS_OF}T00:00:00+00:00",
            "dateModified": f"{modified or AS_OF}T00:00:00+00:00",
            "inLanguage": "en",
            "isAccessibleForFree": True,
            "mainEntityOfPage": {"@type": "WebPage", "@id": url},
            "publisher": {"@type": "Organization", "name": BRAND["name"], "url": LIVE},
        }
    ]
    if len(crumbs) > 1:
        graph.append(
            {
                "@context": "https://schema.org",
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "name": name,
                        "item": LIVE if i == 1 else LIVE + href,
                    }
                    for i, (href, name) in enumerate(crumbs, start=1)
                ],
            }
        )
    payload = json.dumps(graph, ensure_ascii=False).replace("</", "<\\/")
    return f'<script type="application/ld+json">{payload}</script>'


def shell(title: str, description: str, body: str, *, here: str, depth: int = 0,
          path: str | None = None, crumbs: list | None = None, kicker: str = "",
          lede: str = "", read_on: str | None = None, rail_note: str | None = None) -> str:
    # `read_on` / `rail_note` (T64, 2026-11-19, additive): a section built from a different fact base
    # (marketing/data/thermometers.json, via tools/build_thermometers.py) states its own read date and its
    # own source count instead of inheriting the air-fryer desk's. Defaults leave every existing page
    # byte-identical, which `--check` proves.
    read_on = read_on or ED_AS_OF
    rail_note = rail_note or ("Six official pages, read row by row. Two of them disagree with each other, so the\n"
                              "      tables show both numbers instead of picking one.")
    root = "../" * depth
    page_path = path or here
    url = LIVE + page_path
    crumb_html = ""
    if crumbs:
        parts = []
        last = len(crumbs) - 1
        for i, (href, name) in enumerate(crumbs):
            parts.append(f'<a href="{root}{href}">{esc(name)}</a>' if i < last else f"<span>{esc(name)}</span>")
        crumb_html = f'<nav class="crumbs" aria-label="Breadcrumb">{" › ".join(parts)}</nav>'
    head_kicker = f'<p class="eyebrow">{esc(kicker)}</p>' if kicker else ""
    head_lede = f'<p class="lede">{esc(lede)}</p>' if lede else ""
    ld = (json_ld(title, description, url, crumbs or [], published=read_on, modified=read_on)
          if read_on != ED_AS_OF else json_ld(title, description, url, crumbs or []))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · {esc(BRAND['name'])}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{esc(BRAND['name'])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:image" content="{esc(OG_IMAGE)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Counter Notes — every number links to its source">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="{esc(BRAND['name'])} — new guides" href="{root}feed.xml">
<link rel="stylesheet" href="{root}{CSS}">
{ld}
</head>
<body class="pub">
<a class="skip" href="#main">Skip to content</a>
<header class="masthead">
  <div class="mast-in">
    <a class="brand" href="{root}index.html"><span class="brand-name">{esc(BRAND['name'])}</span><span class="brand-sub">{esc(BRAND['sub'])}</span></a>
    <nav class="topnav" aria-label="Sections">{nav_html(root, here)}</nav>
  </div>
</header>
<div class="shell">
  <div class="col" id="main">
    <p class="disclosure" data-rule="R-01"><strong>Affiliate disclosure.</strong> {esc(REQUIRED_SITE_DISCLOSURE)}
    A commission may be earned when you buy through our links, at no extra cost to you. Product links are
    Special Links carrying the Associates tag <code>{esc(ASSOCIATES_TAG)}</code>.
    <a href="{root}verification.html">How we verify</a>.</p>
    <aside class="scope-note" role="note"><strong>Product identity is not confirmed.</strong> These pages describe the Amazon listings the supplied short links resolved to on {esc(read_on)}; they do not establish that those destinations are the products intended in the brief. The supplied codes are 9 characters and an ASIN is 10, so we write about the listings we can read rather than for products we cannot name.
    <a href="https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC" target="_blank"
    rel="noopener noreferrer nofollow">Amazon on ASINs and link formats</a> ·
    <a href="{root}../pages/flags.html#F-03">Flag F-03</a></aside>
{crumb_html}
{head_kicker}
{head_lede}
{body}
  </div>
  <aside class="rail">
    <div class="rail-card">
      <h2>What this site does</h2>
      <p>{esc(BRAND['standfirst'])}</p>
    </div>
    <div class="rail-card">
      <h2>Verified on</h2>
      <p class="rail-date">{esc(read_on)}</p>
      <p class="rail-note">{rail_note}</p>
      <p><a href="{root}verification.html">Read the method</a></p>
    </div>
    <div class="rail-card">
      <h2>Improve this site</h2>
      <p>The open board: what to change next, what each option costs, and the answer each decision is waiting for.</p>
      <p><a class="button button--ghost" href="{root}improvements.html">Open the board</a></p>
    </div>
    <div class="rail-card rail-card--dash">
      <p class="rail-note">A dash is not a gap in the research. It means no official page states the value, and
      we will not fill a blank with a guess.</p>
    </div>
  </aside>
</div>
<footer class="site">
  <p class="foot-brand">{esc(BRAND['name'])}</p>
  <p>{esc(BRAND['footer_note'])}</p>
  <p>{esc(REQUIRED_SITE_DISCLOSURE)}</p>
  <p>Product links are tagged Special Links carrying the Associates tag <strong>{esc(ASSOCIATES_TAG)}</strong>
  and <code>rel="sponsored nofollow"</code>; citation links to official pages are not affiliate links.
  On this site the click counter records aggregate page and link events only — no cookie, no visitor
  identifier, nothing per person. Facts verified {esc(AS_OF if read_on == ED_AS_OF else read_on)} against official
  {"manufacturer and Amazon product pages" if read_on == ED_AS_OF else "Amazon listings and USDA food-safety pages"}.
  <a href="{root}flagged.html">Open items</a> ·
  <a href="{root}improvements.html">Improvement board</a> ·
  <a href="{root}../index.html">Owner dashboard</a></p>
</footer>
<script src="{root}../assets/js/measurement-config.js" defer></script>
<script src="{root}../assets/js/events.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages

# --------------------------------------------------------------------------- pages

def page_index() -> str:
    hub = EDITORIAL["hub"]
    start = "".join(
        f'<li><a href="{esc(href)}"><strong>{esc(title)}</strong><span>{esc(blurb)}</span></a></li>'
        for href, title, blurb in hub["start"]
    )
    products = []
    for p in FACTS["products"]:
        slug = p["key"].lower()
        ed = PRODUCT_EDITORIAL.get(p["key"], {})
        cap = fact_value(p, "Capacity")
        rng = fact_value(p, "Temperature")
        verified = sum(1 for r in p["rows"] if r["status"] == "verified")
        products.append(
            f'<article class="pcard">'
            f'<p class="eyebrow">{esc(p["manufacturer"])} · {esc(p["category_path_amazon"].split(" › ")[-1])}</p>'
            f'<h3><a href="articles/{slug}.html">{esc(p["manufacturer_product_name"])}</a></h3>'
            f'<p class="bignum">{esc(cap["value"] if cap else "—")}</p>'
            f'<p class="pcard-note">{esc(rng["value"] if rng else "range not published")} · {verified} of {len(p["rows"])} rows sourced</p>'
            f'<p>{esc(ed.get("verdict", p["tagline_facts"]).split(". ")[0])}.</p>'
            f'<p class="pcard-links"><a href="articles/{slug}.html">The write-up</a>'
            f'<a href="comparison.html">Side by side</a></p>'
            f"</article>"
        )
    guides = "".join(
        f'<li><p class="eyebrow">{esc(g["kicker"])}</p>'
        f'<h3><a href="topics/{esc(g["slug"])}">{esc(g["title"])}</a></h3>'
        f'<p>{esc(g["hook"].split(". ")[0])}.</p></li>'
        for g in GUIDES
    )
    checked = "".join(
        f'<li><span class="pill {"pill-ok" if v["status"] == "verified" else "pill-flag"}">{esc(v["status"])}</span> '
        f"{esc(v['claim'])} <a class=\"src\" href=\"{esc(v['url'])}\" target=\"_blank\" "
        f'rel="{"sponsored nofollow noopener noreferrer" if v["url"].split("/")[2].endswith("amazon.com") else "noopener noreferrer nofollow"}">'
        f"{esc(v['url'].split('/')[2])}</a></li>"
        for v in VERIFIED_TODAY
    )
    rows = sum(len(p["rows"]) for p in FACTS["products"])
    conflicts = sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "conflict")
    blanks = sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] in ("unverified", "withheld_by_policy"))
    body = f"""    <div class="page-head">
      <p class="eyebrow">{esc(hub['kicker'])}</p>
      <h1>{esc(hub['title'])}</h1>
      <p class="standfirst">{esc(hub['standfirst'])}</p>
      <p class="receipts">{len(FACTS['products'])} products · {rows} specification rows, each one sourced or left
      blank · {conflicts} published disagreements between official pages · {blanks} blanks with a stated reason ·
      read on {esc(ED_AS_OF)}</p>
    </div>

    <section class="block">
      <h2>Start where the decision is</h2>
      <ol class="start">{start}</ol>
    </section>

    <section class="block">
      <h2>The three machines</h2>
      <div class="pgrid">{''.join(products)}</div>
    </section>

    <section class="block">
      <h2>Guides, by the question they answer</h2>
      <ul class="guide-list">{guides}</ul>
      <p class="more"><a href="topics/index.html">All guides</a> · <a href="buying-guide.html">Which one to buy</a> ·
      <a href="trending-topics.html">What is queued next, and the gate it has to pass</a></p>
    </section>

    <section class="block block--voice">
      <h2>How this site is written</h2>
      <p>Ten rules, and the build fails a page that breaks one of them. No scene-setting opener; no adjective
      where a number belongs; the opinion in a labelled box, away from the measurements; the limit stated once,
      in plain language, instead of a disclaimer nobody reads. It is the shortest route we know to a page that
      does not read like it was generated, because the sentences are only allowed to be as good as the sources.</p>
      <p><a class="button" href="improvements.html">Read the rules, and the board of what to change next</a></p>
    </section>

    <section class="block">
      <h2>What we checked on {esc(ED_AS_OF)}</h2>
      <ul class="check-list">{checked}</ul>
      <p class="more"><a href="verification.html">The full method</a> · <a href="flagged.html">What is still open</a></p>
    </section>
"""
    return shell(
        hub["title"],
        "Air fryer reviews and guides built from manufacturer and Amazon listings only: sourced spec rows, "
        "published disagreements, and the blanks labelled instead of filled in.",
        body,
        here="index.html",
        path="index.html",
        crumbs=[("index.html", "Home")],
    )


def page_article(key: str) -> str:
    p = PRODUCTS[key]
    slug = key.lower()
    ed = PRODUCT_EDITORIAL.get(key, {})
    faq = [
        ("What is the published capacity?", fact_value(p, "Capacity")),
        ("What power does the manufacturer state?", fact_value(p, "Power")),
        ("What temperature range is stated?", fact_value(p, "Temperature")),
        ("What model number should be on the box?", fact_value(p, "Model number")),
        ("Can the baskets go in a dishwasher?", fact_value(p, "Basket care")),
    ]
    faq_html = []
    for q, row in faq:
        if row and row["status"] in ("verified", "conflict", "partial"):
            src = cite([row["src"]] if row.get("src") else [])
            faq_html.append(f"<dt>{esc(q)}</dt><dd><strong>{esc(row['value'])}</strong>{src}</dd>")
        else:
            reason = esc((row or {}).get("blank_reason", "no official page states this"))
            faq_html.append(
                f'<dt>{esc(q)}</dt><dd><span class="pill pill-warn">NOT STATED</span> {reason}</dd>'
            )
    conflicts = [r for r in p["rows"] if r["status"] == "conflict"]
    conflict_block = ""
    if conflicts:
        items = "".join(f'<li><strong>{esc(r["attr"])}:</strong> {esc(r["detail"])}</li>' for r in conflicts)
        conflict_block = f"""
    <section class="block callout-flag">
      <h2>Where the official sources disagree</h2>
      <p>Printed as a disagreement, not averaged and not resolved in favour of the more flattering number.</p>
      <ul class="points">{items}</ul>
    </section>"""
    related = [g for g in GUIDES if key in g.get("products", [])]
    related_html = "".join(
        f'<li><a href="../topics/{esc(g["slug"])}">{esc(g["title"])}</a> <span>{esc(g["target_query"])}</span></li>'
        for g in related
    )
    if related_html:
        related_block = f"""
    <section class="block">
      <h2>Read this with</h2>
      <ul class="related">{related_html}</ul>
    </section>"""
    else:
        related_block = ""
    le = p.get("look_elsewhere") or []
    look_elsewhere = "".join(
        f'<li><a href="{esc(x["href"])}">{esc(x["label"])}</a>'
        + (f' <span>{esc(x["why"])}</span>' if x.get("why") else "") + "</li>"
        for x in le
    ) or '<li><a href="../topics/index.html">All guides</a></li>'
    buy_if = "".join(f"<li>{esc(x)}</li>" for x in ed.get("buy_if", []))
    skip_if = "".join(f"<li>{esc(x)}</li>" for x in ed.get("skip_if", []))
    not_tested = (
        f'<p class="not-tested">{esc(ed.get("gap", "Values no official page states are printed as blanks."))}</p>'
    )
    body = f"""    <article class="post">
    <div class="page-head">
      <p class="eyebrow">{esc(p['manufacturer'])} · {esc(p['category_path_amazon'].split(' › ')[-1])}</p>
      <h1>{esc(p['manufacturer_product_name'])}</h1>
      <p class="standfirst">{esc(ed.get('verdict', p['tagline_facts']))}</p>
      <p class="receipts">Model <code>{esc(p['model'])}</code> · ASIN <code>{esc(p['asin'])}</code> · read off
      {' / '.join(esc(s['url'].split('/')[2]) for s in p['official_sources'])} on {esc(AS_OF)}</p>
    </div>

    <div class="block block--verdict">
      <h2>Who it is for</h2>
      <div class="two-col">
        <div><h3>Buy it if</h3><ul class="points points--yes">{buy_if}</ul></div>
        <div><h3>Skip it if</h3><ul class="points points--no">{skip_if}</ul></div>
      </div>
      <p class="cta-row">{product_link(p)}</p>
      {not_tested}
    </div>

    <section class="block">
      <h2>The specification, row by row</h2>
      <p>Every value below is transcribed from the page named in its last column. Nobody on this site has cooked
      with this machine, so there is no performance paragraph — the numbers are the review.</p>
      {spec_table(p, key_prefix=slug)}
    </section>

    <section class="block">
      <h2>What the manufacturer says it does</h2>
      {feature_list(p)}
    </section>
{conflict_block}
    <section class="block">
      <h2>The listing title, as published</h2>
      <p class="quote">{esc(p['title_official'])}</p>
      <p class="row-note">Quoted in full because the title is itself a claim, and the tables above show where it
      agrees with the specification and where it does not.</p>
    </section>

    <section class="block">
      <h2>Questions worth asking before you order</h2>
      <dl class="faq">{''.join(faq_html)}</dl>
    </section>
{related_block}
    <section class="block">
      <h2>Elsewhere on this site</h2>
      <ul class="related">{look_elsewhere}</ul>
      <p class="row-note">Carried from the 2026-11-15 voice pass, which published these pointers in
      <code>marketing/data/facts.json</code>. Kept, because a reader leaving one product page should land on
      another of ours rather than on a search engine.</p>
    </section>

    <section class="block">
      <h2>Sources for this page</h2>
      <ul class="source-list">
        {''.join(f'<li>{source_link(s["id"])} — {esc(s["name"])}</li>' for s in p['official_sources'])}
      </ul>
      <p class="row-note">Read {esc(AS_OF)}. Specifications change; re-check the manufacturer page before buying.</p>
    </section>
    </article>
"""
    return shell(
        p["manufacturer_product_name"],
        ed.get("verdict", p["tagline_facts"])[:155],
        body,
        here="articles/index.html",
        depth=1,
        path=f"articles/{slug}.html",
        crumbs=[("index.html", "Home"), ("articles/index.html", "Reviews"), (f"articles/{slug}.html", p["manufacturer"])],
    )


def page_articles_index() -> str:
    rows = "".join(
        f'<tr><th scope="row"><a href="{p["key"].lower()}.html">{esc(p["manufacturer_product_name"])}</a></th>'
        f'<td><code>{esc(p["asin"])}</code></td>'
        f'<td>{esc(p["manufacturer"])}</td>'
        f'<td>{esc(p.get("hook_editorial") or p["tagline_facts"])}</td>'
        f'<td class="cell-src">{source_link(p["official_sources"][0]["id"])}{source_link(p["official_sources"][1]["id"])}</td></tr>'
        for p in FACTS["products"]
    )
    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <span>Product articles</span></nav>
    <div class="page-head">
      <h1>Product articles</h1>
      <p class="lede">One article per model. Each is generated from the product's verified rows, so the article
      and the specification table can never disagree.</p>
    </div>
    <section class="card">
      <table class="data">
        <caption>Each row links to the manufacturer's and Amazon's own pages for that model.</caption>
        <thead><tr><th>Product</th><th>ASIN</th><th>Brand</th><th>What the article covers</th><th>Official sources</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
    <p class="more">Looking for a decision rather than a model page? <a href="../topics/index.html">The guides answer one question each</a>, and <a href="../buying-guide.html">the buying guide routes you to one of these three</a>.
    </p>
"""
    return shell("Product articles", "One verified article per product, plus the guides that answer the questions around them.", body, here="articles/index.html", depth=1)


def page_comparison() -> str:
    """A comparison table whose every cell is a verified value or an explicit blank."""
    attrs: list[str] = []
    for p in FACTS["products"]:
        for r in p["rows"]:
            name = r["attr"].split(" (")[0]
            if name not in attrs:
                attrs.append(name)
    rows_html = []
    for i, attr in enumerate(attrs):
        cells = []
        for p in FACTS["products"]:
            match = next((r for r in p["rows"] if r["attr"].split(" (")[0] == attr), None)
            if match is None:
                cells.append('<td class="cell-blank">—<div class="row-note">not stated for this model</div></td>')
            elif match["status"] in ("unverified", "withheld_by_policy"):
                label, klass = STATUS_LABEL[match["status"]]
                cells.append(
                    f'<td class="cell-unverified"><span class="pill {klass}">{label}</span>'
                    f'<div class="row-note">{esc(match["blank_reason"])}</div></td>'
                )
            else:
                label, klass = STATUS_LABEL[match["status"]]
                note = f'<div class="row-note">{esc(match["detail"])}</div>' if match.get("detail") else ""
                srcs = source_link(match.get("src"))
                if match.get("src_alt"):
                    srcs += source_link(match["src_alt"])
                cells.append(
                    f'<td>{esc(match["value"])}<div class="pill {klass} pill-inline">{label}</div>{note}'
                    f'<div class="cell-src">{srcs}</div></td>'
                )
        rows_html.append(f'<tr id="c{i + 1}"><th scope="row">{esc(attr)}</th>{"".join(cells)}</tr>')

    heads = "".join(
        f'<th scope="col">{esc(p["manufacturer_product_name"])}<div class="row-note"><code>{esc(p["asin"])}</code></div></th>'
        for p in FACTS["products"]
    )
    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <span>Comparison</span></nav>
    <div class="page-head">
      <h1>Head-to-head comparison</h1>
      <p class="lede">The same attributes across all three models. Where a model does not state an attribute,
      the cell says so instead of borrowing another model's number.</p>
    </div>
    <section class="card">
      <div class="table-scroll">
        <table class="data compare">
          <caption>Read {esc(AS_OF)}. Each value carries the official page it came from directly beneath it; conflict rows carry both pages.</caption>
          <thead><tr><th scope="col">Attribute</th>{heads}</tr></thead>
          <tbody>{''.join(rows_html)}</tbody>
        </table>
      </div>
    </section>
    <section class="card">
      <h2>How to read this table</h2>
      <ul class="plain">
        <li><span class="pill pill-ok">OK</span> one official page states the value, and it is linked in the cell.</li>
        <li><span class="pill pill-flag">CONFLICT</span> two official statements disagree. Both are shown; neither is presented as the answer.</li>
        <li><span class="pill pill-warn">WITHHELD</span> the value exists on some page but publishing it would breach the price-display rule, so it is withheld by policy.</li>
        <li><span class="pill pill-warn">UNVERIFIED</span> no official page states it. Left blank on purpose.</li>
      </ul>
    </section>
"""
    return shell("Head-to-head comparison", "The three air fryers compared on verified specifications only.",
                 body, here="comparison.html")


def page_buying_guide() -> str:
    def pick(attr_prefix: str, best=max):
        """Choose a model using ONLY verified numeric rows. Returns (product, value) or None."""
        cands = []
        for p in FAULTS_products():
            r = next((r for r in p["rows"] if r["attr"].startswith(attr_prefix)), None)
            if not r or r["status"] != "verified":
                continue
            num = first_number(r["value"])
            if num is not None:
                cands.append((num, p, r))
        if not cands:
            return None
        num, p, r = best(cands, key=lambda t: t[0])
        return p, r

    def first_number(text: str):
        import re

        m = re.search(r"(\d+(?:\.\d+)?)", text)
        return float(m.group(1)) if m else None

    biggest = pick("Capacity")
    smallest = pick("Capacity", best=min)
    widest = pick("Temperature")

    def sentence(hit, what: str) -> str:
        if hit is None:
            return (
                f"<li><strong>{esc(what)}:</strong> <span class=\"pill pill-warn\">UNVERIFIED</span> "
                "no comparable official figure exists for all three models, so no recommendation is made.</li>"
            )
        p, r = hit
        return (
            f"<li><strong>{esc(what)}:</strong> {esc(p['manufacturer_product_name'])} — {esc(r['value'])} "
            f'({source_link(r["src"])})</li>'
        )

    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <span>Buying guide</span></nav>
    <div class="page-head">
      <h1>Which air fryer, for which kitchen</h1>
      <p class="lede">A buying guide that only makes recommendations the specifications can support. Every pick
      below is decided by a number printed on a manufacturer page, and that page is linked beside it.</p>
    </div>

    <section class="card">
      <h2>The picks</h2>
      <ul class="plain picks">
        {sentence(biggest, 'Most capacity')}
        {sentence(smallest, 'Most compact basket')}
        {sentence(widest, 'Widest stated temperature range')}
      </ul>
      <p class="row-note">Capacity and temperature ranges are compared as the manufacturer states them. Air-fryer
      capacity claims are not directly interchangeable between a two-basket unit and a single-basket unit, so
      the guide explains what each figure actually measures rather than declaring one "bigger".</p>
    </section>

    <section class="card">
      <h2>Choose by how you cook</h2>
      <div class="card-grid">
        <article class="mini-card">
          <h3>Cooking two different things at once</h3>
          <p>The <strong>{esc(PRODUCTS['P1']['manufacturer_product_name'])}</strong> is the only one of the
          three whose manufacturer page describes <em>two independent baskets</em> with a Sync Finish feature
          so both finish together — {esc(_row(PRODUCTS['P1'], 'Capacity')['value'])} total.</p>
          <p>{source_link('M1')}</p>
        </article>
        <article class="mini-card">
          <h3>Cooking for a family, or a whole chicken</h3>
          <p>The <strong>{esc(PRODUCTS['P2']['manufacturer_product_name'])}</strong> states
          {esc(_row(PRODUCTS['P2'], 'Capacity')['value'])} and describes fitting a whole chicken, 12-inch
          pizzas or a full tray of cookies, on dual French doors.</p>
          <p>{source_link('M3')}</p>
        </article>
        <article class="mini-card">
          <h3>One big basket, simplest controls</h3>
          <p>The <strong>{esc(PRODUCTS['P3']['manufacturer_product_name'])}</strong> is a single-basket
          {esc(_row(PRODUCTS['P3'], 'Capacity')['value'])} unit with
          {esc(_row(PRODUCTS['P3'], 'Presets')['value'])} one-touch presets and a top-rack dishwasher-safe
          basket.</p>
          <p>{source_link('M5')}</p>
        </article>
      </div>
    </section>

    <section class="card">
      <h2>What this guide will not tell you</h2>
      <ul class="plain">
        <li><strong>What they cost.</strong> Prices change by the hour and the Associates operating rules restrict
        how they may be displayed. Nothing here quotes a price; check the listing.</li>
        <li><strong>How well they cook.</strong> No member of this project has tested these units. Claims about
        crispness or speed are the manufacturers', and are attributed to them.</li>
        <li><strong>How buyers rate them.</strong> Star ratings differ by Amazon storefront and move daily, so no
        rating is printed as a fact.</li>
        <li><strong>Which one to buy.</strong> The numbers decide between them for a stated use. Where the numbers
        do not separate them — notably where two official pages contradict each other — this guide says so
        instead of manufacturing a winner.</li>
      </ul>
      <p><a href="flagged.html">See every open question, with sources →</a></p>
    </section>

    <section class="card">
      <h2>Next</h2>
      <p><a href="comparison.html">Compare all three side by side</a> · <a href="articles/index.html">Read the individual product articles</a></p>
    </section>
"""
    return shell("Buying guide", "A source-governed buying guide for three Amazon air fryers.", body,
                 here="buying-guide.html")


def FAULTS_products():
    return FACTS["products"]


def _row(product: dict, prefix: str) -> dict:
    return next(r for r in product["rows"] if r["attr"].startswith(prefix))


def page_verification() -> str:
    method = [
        ("Read the official page", "Each product's manufacturer page and its Amazon listing were fetched live on "
         f"{esc(AS_OF)}. Values were copied from the page text, not from a search snippet or a third-party review."),
        ("Record the quoting text", "The specification block wording is preserved in the rows above so a reader "
         "can find the same sentence on the same page."),
        ("Refuse to interpolate", "If a page states a range, the range is printed. Unit conversions that the page "
         "itself does not give are not performed; where the manufacturer gives both units, both are shown."),
        ("Publish disagreements", "Two official statements that conflict produce a CONFLICT row carrying both "
         "sources. Nothing is averaged."),
        ("Withhold what policy forbids", "Prices and ratings are withheld by policy, not merely absent."),
    ]
    method_html = "".join(
        f'<div class="step"><span class="step-num">{i + 1}</span><div><h3>{esc(t)}</h3><p>{esc(d)}</p></div></div>'
        for i, (t, d) in enumerate(method)
    )
    counts = {
        "verified": sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "verified"),
        "conflict": sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "conflict"),
        "partial": sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "partial"),
        "unverified": sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "unverified"),
        "withheld_by_policy": sum(1 for p in FACTS["products"] for r in p["rows"] if r["status"] == "withheld_by_policy"),
    }
    count_rows = "".join(
        f'<tr><th scope="row">{esc(k)}</th><td>{v}</td></tr>' for k, v in counts.items()
    )
    src_rows = "".join(
        f'<tr><th scope="row">{esc(s["id"])}</th><td>{esc(s["name"])}</td>'
        f'<td>{esc("manufacturer" if s["kind"] == "manufacturer" else "Amazon listing")}</td>'
        f'<td><a class="src" href="{esc(s["url"])}" target="_blank" '
        f'rel="{"sponsored " if s["url"].split("/")[2].endswith("amazon.com") else ""}noopener noreferrer nofollow">'
        f'{esc(s["url"])}</a></td></tr>'
        for s in sorted(SOURCES.values(), key=lambda s: s["id"])
    )
    program_rows = "".join(
        f'<tr><th scope="row">{esc(f["fact"])}</th><td>{esc(f["value"])}</td>'
        f'<td class="cell-src"><a class="src" href="{esc(f["source"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(f["source"])}</a></td></tr>'
        for f in FACTS["program_facts"]
    )
    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <span>Verification</span></nav>
    <div class="page-head">
    <p class="receipts">Re-checked {esc(ED_AS_OF)}: the three supplied short links, all three Amazon
      listings and both manufacturer pages were fetched again; the results are on the
      <a href="improvements.html#checked">improvement board</a>. Row-level transcription keeps the date each
      value was copied ({esc(AS_OF)}), because a re-read of a link is not a re-read of a spec table.</p>
      <h1>How these pages were verified</h1>
      <p class="lede">The method, the exact pages used, and the counts. This page is generated from the same
      data file as the articles, so the numbers cannot drift away from them.</p>
    </div>

    <section class="card"><h2>Method</h2><div class="steps">{method_html}</div></section>

    <section class="card">
      <h2>Row counts</h2>
      <table class="data narrow">
        <caption>Every specification row across the three products, by status.</caption>
        <thead><tr><th>Status</th><th>Rows</th></tr></thead>
        <tbody>{count_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>Official sources used</h2>
      <table class="data">
        <caption>These are the only pages any value on this site was taken from.</caption>
        <thead><tr><th>ID</th><th>Page</th><th>Type</th><th>URL</th></tr></thead>
        <tbody>{src_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>Program facts</h2>
      <table class="data">
        <caption>Program-level statements relied on, each with Amazon's own page.</caption>
        <thead><tr><th>Fact</th><th>Statement</th><th>Official source</th></tr></thead>
        <tbody>{program_rows}</tbody>
      </table>
    </section>

    <section class="card">
      <h2>Links are monetized Special Links</h2>
      <p>Updated 2026-11-17: the owner supplied the Associates tracking ID, and every outbound product
      link here is now a tagged <strong>Special Link</strong> produced by the project's link builder,
      carrying the tag <code>{esc(ASSOCIATES_TAG)}</code>, marked <code>rel="sponsored nofollow"</code>
      and disclosed next to the link itself. The link builder validates the tag format, the ASIN and the
      absence of competing attribution parameters on every build, and the verifier fails any sponsored
      product link that reaches Amazon without the tag. Citation links to the official pages
      (class="src") deliberately stay untagged: they are evidence, not shopping links. Which product each
      supplied short link was <em>intended</em> to point at is still an open question — see the
      <a href="../intent.html">link &amp; intent register</a>.</p>
    </section>
"""
    return shell("Verification", "Method, sources and row counts for the verified marketing set.", body,
                 here="verification.html")


def page_flagged() -> str:
    flags = []
    for p in FACTS["products"]:
        for r in p["rows"]:
            if r["status"] in ("conflict", "partial", "unverified", "withheld_by_policy"):
                flags.append((p, r))
    rows = []
    for i, (p, r) in enumerate(flags, start=1):
        label, klass = STATUS_LABEL[r["status"]]
        why = r.get("detail") or r.get("blank_reason") or ""
        srcs = source_link(r.get("src"))
        if r.get("src_alt"):
            srcs += source_link(r["src_alt"])
        if not srcs:
            if r["status"] == "withheld_by_policy":
                srcs = '<span class="pill pill-warn">withheld by policy — not printed on purpose</span>'
            else:
                srcs = '<span class="pill pill-warn">no official source states this value</span>'
        rows.append(
            f'<tr><th scope="row">MK-{i:02d}</th><td>{esc(p["manufacturer_product_name"])}</td>'
            f"<td>{esc(r['attr'])}</td><td><span class=\"pill {klass}\">{label}</span></td>"
            f"<td>{esc(why)}</td><td class=\"cell-src\">{srcs}</td></tr>"
        )
    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <span>Flagged for review</span></nav>
    <div class="page-head">
      <h1>Flagged for review</h1>
      <p class="lede">Everything in this marketing set that is not a plain confirmed fact, in one table, with
      the source links needed to adjudicate each one. These items do not block publication — they are published
      <em>as</em> open questions rather than closed with a guess.</p>
    </div>
    <section class="card">
      <table class="data">
        <caption>{len(flags)} items. A CONFLICT row means two official pages disagree; WITHHELD means policy
        forbids printing it; UNVERIFIED means no official page states it; PARTIAL means the page names only some
        of a set.</caption>
        <thead><tr><th>ID</th><th>Product</th><th>Attribute</th><th>State</th><th>What the sources say</th><th>Source(s)</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </section>
    <section class="card">
      <h2>Owner actions</h2>
      <ol class="plain">
        <li><strong>Validate one Special Link per product in the enrolled Associates workflow.</strong>
        Done 2026-11-17: the owner supplied the Associates tag and every product link on this site is a
        tagged Special Link. Still open: signing in to Associates Central to confirm each link's
        destination and that the tracking report attributes it — that check needs the owner's enrolled
        session and cannot be run from this repository. Until it is recorded, scale to no further
        products or placements.</li>
        <li><strong>Resolve the Emeril preset count.</strong> The manufacturer's own page says both "25 Cooking
        Pre-sets" and "24 one-touch cooking presets"; Amazon's title says 24. Ask the brand which is current.</li>
        <li><strong>Resolve the Chefman 8 Qt maximum temperature.</strong> The Amazon title advertises a 450 °F
        Hi-Fry option; the manufacturer's 8 Qt specification states a 200–400 °F range.</li>
        <li><strong>Resolve the Emeril model number.</strong> Manufacturer store: 4-00675-02A-VN. Amazon
        product-information block: 4-00675-02X-VN.</li>
      </ol>
    </section>
"""
    return shell("Flagged for review", "Open questions in the marketing set, with sources.", body,
                 here="flagged.html")


def planned_topics_block() -> str:
    """The article list left by the 2026-11-15 voice pass (session 8c4236ad, PR #75), published in
    facts.json as `planned_topics`. Nothing is deleted and nothing is silently dropped: each entry is
    shown with the page that now covers it, or with the reason it is still unwritten. The crosswalk is a
    statement about this site, not a programme fact, and every published_as target is link-checked."""
    pt = FACTS.get("planned_topics") or {}
    items = pt.get("topics") or []
    if not items:
        return ""
    cross = {x["planned"]: x for x in EDITORIAL.get("planned_topics_crosswalk", [])}
    rows = []
    for i, t in enumerate(items, start=1):
        c = cross.get(t["title"], {})
        href = c.get("published_as")
        if href:
            # this block renders inside marketing/topics/, so rebaseline each target
            here = href[len("topics/"):] if href.startswith("topics/") else "../" + href
            status = f'<a href="{esc(here)}">published as {esc(href)}</a>'
        else:
            status = '<span class="pill pill-warn">not published</span>'
        rows.append(
            f'<tr id="pt-{i}"><th scope="row">{esc(t["title"])}</th><td>{esc(t["angle"])}</td>'
            f'<td>{status}</td><td>{esc(c.get("note", ""))}</td></tr>'
        )
    board = pt.get("board_href") or "../../pages/suggestions.html"
    note = esc(FACTS.get("editorial_note", ""))
    return (
        '<section class="block"><h2>Planned by the 2026-11-15 voice pass</h2>'
        f'<p class="row-note">{esc(pt.get("status", ""))} <a href="{board}">the programme board</a>.</p>'
        '<table class="data"><caption>Four topics were queued before this pass. Each is shown with what '
        'covers it now, or with the reason it is still open.</caption>'
        "<thead><tr><th>Planned topic</th><th>Angle as written</th><th>Status</th><th>Note</th></tr></thead>"
        f'<tbody>{"".join(rows)}</tbody></table>'
        f'<p class="row-note">Data-file note carried from that pass: {note}</p>'
        "</section>"
    )


def _thermometers():
    """The thermometer desk (T64). Imported lazily: build_thermometers imports this module for the shared
    shell, so a top-level import would be circular."""
    import build_thermometers

    return build_thermometers


def thermometer_guides_block() -> str:
    rows = "".join(
        f'<li class="topic-row"><div><p class="eyebrow">{esc(g["kicker"])} · {esc(g["intent"])}</p>'
        f'<h3><a href="../{esc(g["rel"])}">{esc(g["title"])}</a></h3>'
        f'<p>{esc(g["hook"])}</p></div>'
        f'<p class="topic-meta">Answers: <em>{esc(g["target_query"])}</em><br>'
        f"Read on {esc(g['date'])} · every line sourced</p></li>"
        for g in _thermometers().guide_entries()
    )
    return (
        '<section class="block" id="thermometers"><h2>From the thermometer desk</h2>'
        '<p class="row-note">Built from two Amazon listings and three USDA food-safety pages. '
        '<a href="../thermometers/index.html">The desk, with both thermometers row by row</a>.</p>'
        f'<ul class="topics">{rows}</ul></section>'
    )


def page_topics_index() -> str:
    items = []
    for g in GUIDES:
        items.append(
            f'<li class="topic-row"><div><p class="eyebrow">{esc(g["kicker"])} · {esc(g["intent"])}</p>'
            f'<h3><a href="{esc(g["slug"])}">{esc(g["title"])}</a></h3>'
            f'<p>{esc(g["hook"])}</p></div>'
            f'<p class="topic-meta">Answers: <em>{esc(g["target_query"])}</em><br>'
            f"{len(g['sections'])} sections · every row sourced</p></li>"
        )
    body = f"""    <div class="page-head">
      <p class="eyebrow">Guides</p>
      <h1>The questions worth arriving on</h1>
      <p class="standfirst">{num_words(len(GUIDES))} guides, each answering one phrasing somebody actually types. They are written
      from the same fact base as the product pages, so a guide and its specification table cannot disagree - and
      each one names the number the brands never published.</p>
    </div>
    <ul class="topics">{"".join(items)}</ul>
{thermometer_guides_block()}
{planned_topics_block()}
    <section class="block">
      <h2>Not sure which question is yours?</h2>
      <p class="more"><a href="../buying-guide.html">Answer three questions and get a model</a> ·
      <a href="../comparison.html">See every number side by side</a> ·
      <a href="../improvements.html#DS-14">The {num_words(len(next(s["roadmap"] for s in SUGGESTIONS if s["id"] == "DS-14"))).lower()} guides we have not written yet, and what blocks each one</a></p>
    </section>
"""
    return shell("Guides", "Capacity, design, fit and specification-drift guides for the three air fryers, "
                 "written from the official pages.", body,
                 here="topics/index.html", depth=1, path="topics/index.html",
                 crumbs=[("index.html", "Home"), ("topics/index.html", "Guides")])


def page_topic(slug: str) -> str:
    g = GUIDE_BY_SLUG[slug]
    key = slug.replace(".html", "").replace("-", "")
    parts = []
    for si, s in enumerate(g["sections"], start=1):
        inner = render_blocks(s["blocks"], key=f"{key}s{si}")
        parts.append(f'<section class="block"><h2>{esc(s["h2"])}</h2>{inner}</section>')
    product_links = ""
    if g.get("products"):
        rows = []
        for pk in g["products"]:
            p = PRODUCTS[pk]
            rows.append(
                f'<li><a href="../articles/{esc(p["key"].lower())}.html">{esc(p["manufacturer_product_name"])}</a> '
                f'<span>{esc(PRODUCT_EDITORIAL.get(pk, {}).get("verdict", "").split(". ")[0])}.</span></li>'
            )
        product_links = (
            '<section class="block block--cta"><h2>The models this guide is about</h2>'
            f'<ul class="related">{"".join(rows)}</ul>'
            '<p class="row-note">Links go to our own write-ups, which carry the tagged product page '
            "link and its disclosure.</p></section>"
        )
    related = "".join(
        f'<li><a href="{esc(r)}">{esc(GUIDE_BY_SLUG[r]["title"])}</a> <span>{esc(GUIDE_BY_SLUG[r]["kicker"])}</span></li>'
        for r in g.get("related", []) if r in GUIDE_BY_SLUG
    )
    src_ids = sorted({s for b in [blk for sec in g["sections"] for blk in sec["blocks"]] for s in b.get("src", [])})
    src_list = "".join(f"<li>{source_link(s)}</li>" for s in src_ids)
    body = f"""    <article class="post">
    <div class="page-head">
      <p class="eyebrow">{esc(g['kicker'])} · {esc(g['intent'])} search</p>
      <h1>{esc(g['title'])}</h1>
      <p class="standfirst">{esc(g['hook'])}</p>
      <p class="receipts">Why this exists: {esc(g['angle'])}</p>
    </div>
{"".join(parts)}
{product_links}
    <section class="block">
      <h2>What we did not do</h2>
      <p class="not-tested">Nobody on this site has cooked with these machines. Every number here was copied from a
      manufacturer page or an Amazon listing on {esc(AS_OF)}, and where the two disagree we say so. Prices and
      star ratings are not printed anywhere on this site: the first is restricted by the programme's content rules,
      the second changes too often to be a fact.</p>
    </section>
    <section class="block">
      <h2>Read next</h2>
      <ul class="related">{related}</ul>
    </section>
    <section class="block">
      <h2>Sources for this guide</h2>
      <ul class="source-list">{src_list}</ul>
    </section>
    </article>
"""
    return shell(g["title"], g["meta_description"], body,
                 here="topics/index.html", depth=1, path=f"topics/{slug}",
                 crumbs=[("index.html", "Home"), ("topics/index.html", "Guides"), (f"topics/{slug}", g["kicker"])])


def status_pill(status: str) -> str:
    if status == "implemented-as-recommended":
        return '<span class="pill pill-ok">implemented as recommended</span>'
    if status == "awaiting-owner-decision":
        return '<span class="pill pill-warn">awaiting your decision</span>'
    return f'<span class="pill pill-warn">{esc(status)}</span>'


NUM_WORDS = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven",
             8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve"}


def num_words(n: int) -> str:
    """Counts in prose, spelled out up to twelve: a caption that starts "6 proposals" reads like a
    report, and a typed "Six proposals" is a number that can go stale."""
    return NUM_WORDS.get(n, str(n))


def page_trending() -> str:
    """The queue of article shapes this set could grow into. Carried over from the 2026-11-15 marketing
    pass, which committed this page by hand under the old shell; regenerated here so it inherits the
    masthead, the disclosure, canonical URLs, the sitemap and the orphan check, and so its assertions are
    labelled as what they are. No value in it is new: every basis string is a row already published."""
    t = EDITORIAL["trending"]
    how = "".join(f"<li>{esc(x)}</li>" for x in t["how"])
    rows = []
    for i, q in enumerate(t["queue"], start=1):
        rows.append(
            f'<tr id="idea-{i}"><th scope="row">{esc(q["title"])}</th>'
            f'<td>{esc(q["angle"])}</td>'
            f'<td><a href="{esc(q["href"])}">{esc(q["relates"])}</a></td>'
            f'<td>{esc(q["format"])}</td>'
            f'<td>{esc(q["basis"])}</td></tr>'
        )
    gate = "".join(f"<li>{esc(x)}</li>" for x in t["gate"])
    body = f"""    <article class="post">
    <div class="page-head">
      <p class="eyebrow">{esc(t['kicker'])}</p>
      <h1>{esc(t['title'])}</h1>
      <p class="lede">{esc(t['lede'])}</p>
    </div>

    <section class="block">
      <h2>How a page like this earns a reader</h2>
      <div class="take">
        <p class="take-label">{esc(t['how_label'])}</p>
        <ol class="points">{how}</ol>
      </div>
    </section>

    <section class="block">
      <h2>The queue</h2>
      <p>{esc(t['queue_intro'])}</p>
      <table class="data">
        <caption>{num_words(len(t["queue"]))} {esc(t["queue_caption"])}</caption>
        <thead><tr><th>Working title</th><th>Angle, and where a reader would push back</th>
        <th>Relates to</th><th>Shape</th><th>Basis in the verified set</th></tr></thead>
        <tbody>{"".join(rows)}</tbody>
      </table>
    </section>

    <section class="block">
      <h2>Before any of these is published</h2>
      <p>{esc(t['gate_intro'])}</p>
      <ol class="points">{gate}</ol>
    </section>

    <section class="block">
      <h2>How this page got here</h2>
      <p class="not-tested">{esc(t['provenance'])}</p>
    </section>

    <nav class="crumbs" aria-label="Related"><a href="index.html">Overview</a> ·
      <a href="topics/index.html">Guides</a> · <a href="improvements.html">Improvement board</a> ·
      <a href="../pages/suggestions.html">Programme suggestions</a></nav>
    </article>
"""
    return shell("Trending topics", f"{num_words(len(t['queue']))} article shapes this set could grow into, each tied to a row already "
                 "published, with the gate each one has to pass before it is written.", body,
                 here="trending-topics.html", depth=0,
                 crumbs=[("index.html", "Overview"), ("trending-topics.html", "Trending topics")])


def page_improvements() -> str:
    """The review board: every open suggestion with its options, cost and blocking question, plus the
    question register, the design brief for the next revision, and the before/after standard."""
    board = []
    counts = {"implemented-as-recommended": 0, "awaiting-owner-decision": 0}
    for s in SUGGESTIONS:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
        options = "".join(
            f'<li class="opt{" opt--rec" if o["id"] == s["recommended"] else ""}">'
            f'<span class="opt-id">{esc(o["id"])}</span><strong>{esc(o["label"])}</strong>'
            f'<span class="opt-cost">{esc(o["tradeoff"])}</span>'
            + ('<span class="pill pill-ok">recommended</span>' if o["id"] == s["recommended"] else "")
            + "</li>"
            for o in s["options"]
        )
        evidence = "".join(f"<li>{ext_link(e['label'], e['url'])}</li>" for e in s.get("evidence", []))
        needs = s.get("needs_answers", [])
        needs_html = " ".join(
            (f'<a href="#{esc(n)}">{esc(n)}</a>' if n.startswith("MQ-")
             else f'<a href="../pages/questions.html#{esc(n)}">{esc(n)}</a>')
            for n in needs
        ) or '<span class="ok">nothing blocking</span>'
        roadmap = ""
        if s.get("roadmap"):
            rows = "".join(
                f'<tr><th scope="row">{esc(t)}</th><td>{esc(note)}</td></tr>' for t, note in s["roadmap"]
            )
            roadmap = (
                f'<table class="data"><caption>The next {num_words(len(s["roadmap"])).lower()} articles, and the gap that blocks each one.</caption>'
                f"<thead><tr><th>Candidate</th><th>What it needs</th></tr></thead><tbody>{rows}</tbody></table>"
            )
        board.append(
            f'<section class="sug" id="{esc(s["id"])}">'
            f'<p class="eyebrow">{esc(s["area"])} · impact {esc(s["impact"])} · effort {esc(s["effort"])}</p>'
            f'<h3>{esc(s["id"])} — {esc(s["title"])}</h3>'
            f'<p class="sug-status">{status_pill(s["status"])}</p>'
            f'<p class="sug-do">{esc(s["suggestion"])}</p>'
            f'<p class="sug-why"><strong>Why:</strong> {esc(s["why"])}</p>'
            f'<h4>Options</h4><ul class="opts">{options}</ul>'
            f'<div class="sug-foot"><p><strong>Needs answered first:</strong> {needs_html}</p>'
            f'<h4>Evidence</h4><ul class="source-list">{evidence}</ul></div>'
            f"{roadmap}</section>"
        )
    index_rows = "".join(
        f'<tr id="{esc(s["id"])}-row"><th scope="row"><a href="#{esc(s["id"])}">{esc(s["id"])}</a></th>'
        f'<td>{esc(s["area"])}</td><td><a href="#{esc(s["id"])}">{esc(s["title"])}</a></td>'
        f'<td>{esc(s["impact"])}</td><td>{esc(s["effort"])}</td>'
        f'<td><span class="opt-id">{esc(s["recommended"])}</span></td>'
        f"<td>{status_pill(s['status'])}</td></tr>"
        for s in SUGGESTIONS
    )
    qs = []
    for q in QUESTIONS:
        ev = "".join(f"<li>{ext_link(e['label'], e['url'])}</li>" for e in q.get("evidence", []))
        blocks = " ".join(
            (f'<a href="#{esc(b)}">{esc(b)}</a>' if b.startswith("DS-")
             else f'<a href="../pages/questions.html#{esc(b)}">{esc(b)}</a>')
            for b in q.get("blocks", [])
        )
        qs.append(
            f'<section class="q" id="{esc(q["id"])}">'
            f'<h3>{esc(q["id"])} — {esc(q["question"])}</h3>'
            f'<p class="q-why"><strong>Why it has to be answered:</strong> {esc(q["why_it_matters"])}</p>'
            f'<dl class="qa"><div><dt>What we already know</dt><dd>{esc(q["known"])}</dd></div>'
            f'<div><dt>What is missing</dt><dd class="missing">{esc(q["missing"])}</dd></div>'
            f'<div><dt>How to find out</dt><dd>{esc(q["how_to_find"])}</dd></div>'
            f'<div><dt>Decisions waiting on it</dt><dd>{blocks}</dd></div></dl>'
            f'<h4>Sources</h4><ul class="source-list">{ev}</ul>'
            "</section>"
        )
    rules = "".join(
        f'<tr id="{esc(r["id"])}"><th scope="row">{esc(r["id"])}</th><td>{esc(r["rule"])}</td>'
        f'<td class="good">{esc(r["do"])}</td><td class="bad">{esc(r["dont"])}</td>'
        f"<td>{esc(r['why'])}</td></tr>"
        for r in VOICE["rules"]
    )
    before_after = "".join(
        f'<section class="pair"><h3>{esc(x["problem"])}</h3>'
        f'<div class="pair-cols"><p class="before"><span class="pair-tag">As generated</span>{esc(x["before"])}</p>'
        f'<p class="after"><span class="pair-tag">As published</span>{esc(x["after"])}</p></div>'
        f'<p class="fix"><strong>Rule that fixes it:</strong> {esc(x["fix"])} · '
        f'{ext_link("the page the replacement is drawn from", x["src"])}</p></section>'
        for x in BEFORE_AFTER
    )
    tokens = "".join(f"<tr><th scope=\"row\">{esc(a)}</th><td>{esc(b)}</td></tr>" for a, b in DESIGN["tokens"])
    anti = "".join(f"<li>{esc(x)}</li>" for x in DESIGN["anti_patterns"])
    banned = "".join(f"<code>{esc(w)}</code> " for w in VOICE["banned_words"])
    brief = "".join(
        f'<div class="brief-row"><h4>{esc(h)}</h4><p>{esc(t)}</p></div>' for h, t in PROMPT_BRIEF["blocks"]
    )
    checked = "".join(
        f'<tr><th scope="row">{esc(v["id"])}</th><td>{esc(v["claim"])}</td>'
        f'<td>{esc(v["observed"])}</td>'
        f'<td><span class="pill {"pill-ok" if v["status"] == "verified" else "pill-flag"}">{esc(v["status"])}</span></td>'
        f'<td class="cell-src">{ext_link(v["url"].split("/")[2], v["url"])}</td></tr>'
        for v in VERIFIED_TODAY
    )
    body = f"""    <div class="page-head">
      <p class="eyebrow">Review before anything else changes</p>
      <h1>The improvement board</h1>
      <p class="standfirst">Every open suggestion for this site, with the options, what each one costs, and the
      answer it is waiting for. {counts['implemented-as-recommended']} of {len(SUGGESTIONS)} are already built the
      recommended way and can be reversed here; the rest are not implemented, on purpose - a suggestion that ships
      before the owner reads it is not a suggestion.</p>
      <p class="receipts">Nothing on this page is a program fact. Recommendations are judgements built on the
      official sources cited in each entry; the facts they rest on are on the
      <a href="verification.html">verification page</a>.</p>
    </div>

    <section class="block" id="how-to-use">
      <h2>How to decide</h2>
      <ol class="points">
        <li>Read the index below. Choose the ones worth a decision today - the rest stay open and cost nothing.</li>
        <li>For each, either record a choice in the <code>decision</code> field of
        <code>marketing/data/editorial.json</code>, or reply with the IDs and letters. Both are enough.</li>
        <li>An entry whose question is unanswered stays blocked. The blocking IDs are named on the card, and
        answering the question is usually cheaper than the decision it gates.</li>
        <li>Programme-level decisions (account, marketplace, niche, monetisation) live on the owner dashboard's
        <a href="../pages/suggestions.html">decision board</a> and <a href="../pages/questions.html">question
        register</a>. This board is the site: design, copy, traffic and measurement. They cross-reference and do
        not overlap.</li>
      </ol>
    </section>

    <section class="block">
      <h2>Index</h2>
      <table class="data">
        <caption>{len(SUGGESTIONS)} open suggestions. Impact and effort are this project's own estimates, not
        measurements; the recommended column is the letter already implemented or the one we would pick.</caption>
        <thead><tr><th>ID</th><th>Area</th><th>Suggestion</th><th>Impact</th><th>Effort</th><th>Rec.</th><th>Status</th></tr></thead>
        <tbody>{index_rows}</tbody>
      </table>
    </section>

    <div class="sug-list">{"".join(board)}</div>

    <section class="block" id="questions">
      <h2>What has to be known before a decision is reasonable</h2>
      <p>Ten questions in the site's own domain, each with what is verified, what is missing, and the cheapest way
      to close the gap. The register on the dashboard
      (<a href="../pages/questions.html">Q-01 … Q-16</a>) covers the programme side; where a question here is the
      same one, it names the ID rather than restating it.</p>
      {"".join(qs)}
    </section>

    <section class="block" id="voice">
      <h2>The writing standard, enforced by the build</h2>
      <p class="row-note">{esc(VOICE['brief'])}</p>
      <table class="data">
        <caption>Ten rules. The marketing gate checks the banned-phrase list and requires every factual sentence
        to carry a source, so a regeneration cannot quietly restore the house style.</caption>
        <thead><tr><th>ID</th><th>Rule</th><th>What that looks like</th><th>What it replaces</th><th>Why</th></tr></thead>
        <tbody>{rules}</tbody>
      </table>
      <p class="banned"><strong>Banned as evidence of generated copy:</strong> {banned}</p>
    </section>

    <section class="block" id="before-after">
      <h2>The same sentences, before and after</h2>
      {before_after}
    </section>

    <section class="block" id="design">
      <h2>Design direction as it is currently built</h2>
      <p class="row-note">{esc(DESIGN['summary'])}</p>
      <table class="data"><thead><tr><th>Token</th><th>Rule</th></tr></thead><tbody>{tokens}</tbody></table>
      <h3>Refused on sight</h3>
      <ul class="points points--no">{anti}</ul>
    </section>

    <section class="block" id="brief">
      <h2>{esc(PROMPT_BRIEF['title'])}</h2>
      <p class="row-note">{esc(PROMPT_BRIEF['note'])}</p>
      <div class="brief">{brief}</div>
      <p><a class="button" href="../pages/suggestions.html">The programme board, which this brief must not
      contradict</a></p>
    </section>

    <section class="block" id="checked">
      <h2>Re-verified on {esc(ED_AS_OF)}</h2>
      <table class="data">
        <caption>Everything a page on this board asserts about the outside world, checked today against an
        official page. A row marked conflict stays a conflict.</caption>
        <thead><tr><th>ID</th><th>Claim</th><th>What was observed</th><th>Verdict</th><th>Source</th></tr></thead>
        <tbody>{checked}</tbody>
      </table>
    </section>
"""
    return shell("The improvement board", "Every open suggestion for this site with its options, cost, evidence "
                 "and the answer it is waiting for - plus the writing standard and the question register.", body,
                 here="improvements.html", path="improvements.html",
                 crumbs=[("index.html", "Home"), ("improvements.html", "Improvement board")])


# --------------------------------------------------------------------------- text outputs


def page_sitemap() -> str:
    # Derived from the page registry, never typed: a hand-maintained list is how
    # F-26-style drift starts. One registry, one sitemap, one truth.
    urls = list(PAGES) + _thermometers().page_rels()  # T64: the thermometer desk, from its own registry
    entries = "".join(
        f"<url><loc>{LIVE}{u}</loc><lastmod>{ED_AS_OF}</lastmod></url>" for u in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{entries}</urlset>\n'


def page_robots() -> str:
    return f"User-agent: *\nAllow: /\nSitemap: {LIVE}sitemap.xml\n"


def page_feed() -> str:
    items = []
    # T64 (2026-11-19): the thermometer desk's guides, newest first. Titles, links and dates come from
    # tools/build_thermometers.py, which publishes the same values on the pages themselves.
    for g in _thermometers().guide_entries():
        items.append(
            "<item>"
            f"<title>{esc(g['title'])}</title>"
            f"<link>{LIVE}{esc(g['rel'])}</link>"
            f"<guid isPermaLink=\"true\">{LIVE}{esc(g['rel'])}</guid>"
            f"<pubDate>{g['date']}T00:00:00Z</pubDate>"
            f"<description>{esc(g['hook'])}</description>"
            "</item>"
        )
    for g in GUIDES:
        items.append(
            "<item>"
            f"<title>{esc(g['title'])}</title>"
            f"<link>{LIVE}topics/{esc(g['slug'])}</link>"
            f"<guid isPermaLink=\"true\">{LIVE}topics/{esc(g['slug'])}</guid>"
            f"<pubDate>{ED_AS_OF}T00:00:00Z</pubDate>"
            f"<description>{esc(g['hook'])}</description>"
            "</item>"
        )
    # T63 (session 10727edd, 2026-11-19): the brief asks that each new guide be added to the
    # existing feed. The four question-shaped guides live under guides/ and are declared once, in
    # tools/front_t63.py; they are appended here, newest first, so the feed has one source of truth.
    import front_t63  # noqa: E402  (tools/ is on sys.path when this script runs)
    site = "https://kanlerxz87-cyber.github.io/Zone2/"
    for slug, _kicker, title, dek, _cat in front_t63.NEW_GUIDES:
        url = f"{site}guides/{slug}.html"
        items.insert(0,
            "<item>"
            f"<title>{esc(title)}</title>"
            f"<link>{url}</link>"
            f"<guid isPermaLink=\"true\">{url}</guid>"
            f"<pubDate>{front_t63.TODAY}T00:00:00Z</pubDate>"
            f"<description>{esc(dek)}</description>"
            "</item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
        f"<title>{esc(BRAND['name'])}</title><link>{LIVE}</link>"
        f"<description>{esc(BRAND['standfirst'])}</description>"
        f"<language>en</language>{''.join(items)}</channel></rss>\n"
    )


# --------------------------------------------------------------------------- build

PAGES = {
    "index.html": page_index,
    "buying-guide.html": page_buying_guide,
    "comparison.html": page_comparison,
    "verification.html": page_verification,
    "flagged.html": page_flagged,
    "improvements.html": page_improvements,
    "trending-topics.html": page_trending,
    "articles/index.html": page_articles_index,
    "articles/p1.html": lambda: page_article("P1"),
    "articles/p2.html": lambda: page_article("P2"),
    "articles/p3.html": lambda: page_article("P3"),
    "topics/index.html": page_topics_index,
    **{f"topics/{g['slug']}": (lambda s=g["slug"]: page_topic(s)) for g in GUIDES},
}

# Machine-readable outputs. Not HTML, so they skip the markup audit and the disclosure rule; they
# carry no product data at all, only titles, URLs and dates already published on the pages.
TEXT_PAGES = {
    "sitemap.xml": page_sitemap,
    "robots.txt": page_robots,
    "feed.xml": page_feed,
}


def build(out_dir: Path) -> dict[str, str]:
    rendered = {}
    for rel, fn in PAGES.items():
        doc = fn()
        problems = audit_html(doc)
        if problems:
            raise BuildError(f"{rel}: non-compliant affiliate markup: {problems}")
        if REQUIRED_SITE_DISCLOSURE not in doc:
            raise BuildError(f"{rel}: missing the required Associates disclosure")
        rendered[rel] = doc
    # T64: the thermometer desk renders through its own module, which runs its own publish gate (host
    # allow-list including www.fsis.usda.gov, sourced claims, no prices or ratings) before returning.
    for rel, doc in _thermometers().render().items():
        if rel in rendered:
            raise BuildError(f"{rel}: generated by both the marketing registry and the thermometer desk")
        rendered[rel] = doc
    for rel, fn in TEXT_PAGES.items():
        rendered[rel] = fn()
    for rel, doc in rendered.items():
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(doc, encoding="utf-8")
    return rendered


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true", help="fail if committed output differs from a fresh build")
    args = ap.parse_args(argv)

    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            rendered = build(Path(tmp))
        drift = []
        for rel, doc in rendered.items():
            committed = OUT / rel
            if not committed.is_file():
                drift.append(f"{rel}: missing")
            elif committed.read_text(encoding="utf-8") != doc:
                drift.append(f"{rel}: differs from a fresh build")
        if drift:
            print("\n".join(drift))
            return 1
        n_desk = len(rendered) - len(PAGES) - len(TEXT_PAGES)
        print(f"{len(rendered)} marketing outputs ({len(PAGES)} pages + {n_desk} thermometer-desk pages + "
              f"{len(TEXT_PAGES)} machine-readable): committed output is current")
        return 0

    rendered = build(OUT)
    print(f"built {len(rendered)} marketing outputs into {OUT.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, LinkPolicyError) as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        # T64: a refused build now exits non-zero. Before, it printed the refusal and exited 0, so a
        # wrapper that only read the exit code would have treated a refused build as a success.
        raise SystemExit(1)
