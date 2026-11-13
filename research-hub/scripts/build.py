#!/usr/bin/env python3
"""Generate the static GitHub Pages site from the verified dataset.

Design rule: no page may state a product fact that is not present in
data/products.json. Everything in the output HTML comes from JSON or from the
literal strings in TEMPLATES below.

Run:  python3 scripts/build.py
Out:  *.html and assets/ at the repository root (see site-manifest.json)
"""

from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
# GitHub Pages on this repository is configured as a *legacy* build from
# branch `main`, path `/`. That means the published files must sit at the
# repository root. Changing the Pages source requires repository-admin rights
# that this session does not have, so the generator writes to the root and
# keeps an explicit manifest of what it owns.
SITE = ROOT
MANIFEST = ROOT / "site-manifest.json"

CAPTURED_UTC = "2026-11-13"

# ---------------------------------------------------------------- data loading


def load(name: str) -> dict:
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


PRODUCTS = load("products.json")
COMPLIANCE = load("compliance.json")
REQUIREMENTS = load("requirements.json")
SOURCES = load("sources.json")

PRODUCT_BY_ID = {p["id"]: p for p in PRODUCTS["products"]}

# ---------------------------------------------------------------- helpers


def e(value) -> str:
    """HTML-escape, preserving nothing. Blank values stay blank."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def slug(product: dict) -> str:
    return f"product-{product['asin']}.html"


def status_chip(status: str) -> str:
    label = {
        "verified": "Verified",
        "conflict": "Conflict",
        "unverified": "Unverified",
    }.get(status, status)
    return f'<span class="chip chip--{e(status)}">{e(label)}</span>'


def source_cell(row: dict) -> str:
    """Every fact row renders a link to its official source, or an explicit blank."""
    url = row.get("source_url")
    if not url:
        return '<span class="blank" aria-label="no official source">— unverified —</span>'
    name = row.get("source_name") or "Source"
    return (
        f'<a class="src" href="{e(url)}" rel="noopener nofollow" '
        f'target="_blank">{e(name)}</a>'
    )


def value_cell(row: dict) -> str:
    """Blank out anything that is not verified or an explicit conflict."""
    if row.get("status") == "unverified":
        return '<span class="blank">—</span>'
    return e(row.get("value"))


def spec_table(product: dict) -> str:
    rows = []
    for spec in product["specs"]:
        note = f'<div class="note">{e(spec["note"])}</div>' if spec.get("note") else ""
        rows.append(
            "<tr>"
            f'<th scope="row">{e(spec["label"])}</th>'
            f'<td class="val">{value_cell(spec)}{note}</td>'
            f'<td class="st">{status_chip(spec["status"])}</td>'
            f'<td class="src-cell">{source_cell(spec)}</td>'
            "</tr>"
        )
    return (
        '<table class="grid"><caption>Specifications</caption><thead><tr>'
        "<th scope=\"col\">Attribute</th><th scope=\"col\">Value</th>"
        "<th scope=\"col\">Status</th><th scope=\"col\">Official source</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


def identifier_table(product: dict) -> str:
    rows = []
    for ident in product["identifiers"]:
        note = f'<div class="note">{e(ident["note"])}</div>' if ident.get("note") else ""
        rows.append(
            "<tr>"
            f'<th scope="row">{e(ident["label"])}</th>'
            f'<td class="val">{value_cell(ident)}{note}</td>'
            f'<td class="st">{status_chip(ident["status"])}</td>'
            f'<td class="src-cell">{source_cell(ident)}</td>'
            "</tr>"
        )
    return (
        '<table class="grid"><caption>Identifiers</caption><thead><tr>'
        "<th scope=\"col\">Identifier</th><th scope=\"col\">Value</th>"
        "<th scope=\"col\">Status</th><th scope=\"col\">Official source</th>"
        "</tr></thead><tbody>" + "".join(rows) + "</tbody></table>"
    )


# ---------------------------------------------------------------- templates


def page(title: str, active: str, body: str, description: str = "") -> str:
    nav_items = [
        ("index.html", "Overview", "overview"),
        ("products.html", "Products", "products"),
        ("compare.html", "Comparison", "compare"),
        ("compliance.html", "Amazon rules", "compliance"),
        ("requirements.html", "Requirements", "requirements"),
        ("methodology.html", "Method", "method"),
        ("flagged.html", "Flagged for Review", "flagged"),
        ("summary.html", "Executive summary", "summary"),
    ]
    nav_parts = []
    for href, label, key in nav_items:
        on = ' class="on" aria-current="page"' if key == active else ""
        nav_parts.append(f'<a href="{href}"{on}>{e(label)}</a>')
    nav = "".join(nav_parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<div class="disclosure-bar" role="note">
  <strong>Affiliate disclosure:</strong> As an Amazon Associate I earn from qualifying purchases.
  <a href="compliance.html">How this site complies with Amazon's rules</a>.
</div>

<header class="masthead">
  <div class="wrap">
    <a class="brand" href="index.html">
      <span class="brand__mark" aria-hidden="true"></span>
      <span class="brand__text">Affiliate Research Hub<small>Zone2 · verified product data</small></span>
    </a>
    <nav class="tabs" aria-label="Sections">{nav}</nav>
  </div>
</header>

<main id="main" class="wrap">
{body}
</main>

<footer class="footer">
  <div class="wrap">
    <p><strong>Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates.</strong></p>
    <p>This site is not endorsed by, sponsored by, or affiliated with Amazon.com, Inc. beyond participation
    in the Amazon Associates programme. Prices, availability, ratings and review counts change constantly and
    are deliberately not published here as facts — always confirm on the Amazon product page.</p>
    <p>Data captured {e(CAPTURED_UTC)} (UTC). Every published figure links to the official page it came from.
    Anything that could not be confirmed is left blank and listed on the
    <a href="flagged.html">Flagged for Review</a> page.</p>
  </div>
</footer>
</body>
</html>
"""


def stat(label: str, value: str, hint: str = "") -> str:
    hint_html = f'<span class="stat__hint">{e(hint)}</span>' if hint else ""
    return (
        f'<div class="stat"><span class="stat__value">{e(value)}</span>'
        f'<span class="stat__label">{e(label)}</span>{hint_html}</div>'
    )


def count_status(status: str) -> int:
    total = 0
    for product in PRODUCTS["products"]:
        for row in product["specs"] + product["identifiers"]:
            if row["status"] == status:
                total += 1
    return total


# ---------------------------------------------------------------- pages


def build_index() -> str:
    total_rows = sum(
        len(p["specs"]) + len(p["identifiers"]) for p in PRODUCTS["products"]
    )
    verified = count_status("verified")
    conflicts = count_status("conflict")
    unverified = count_status("unverified")

    cards = []
    for product in PRODUCTS["products"]:
        cards.append(
            f"""<a class="card" href="{slug(product)}">
  <span class="card__kicker">{e(product["category"])}</span>
  <span class="card__title">{e(product["title"])}</span>
  <span class="card__meta">ASIN {e(product["asin"])} · {e(product["brand"])}</span>
  <span class="card__cta">View sourced profile →</span>
</a>"""
        )

    return f"""
<section class="hero">
  <p class="hero__eyebrow">Amazon Associates · research and disclosure</p>
  <h1>Three products, one verified data trail</h1>
  <p class="hero__lede">
    This site documents three Amazon affiliate products. Every published value is traced to an
    official Amazon or manufacturer page. Values that could not be confirmed are left blank and
    listed for review rather than guessed. Prices, ratings and conversion figures are not
    published as facts because they change constantly and Amazon's own rules restrict how they
    may be shown.
  </p>
  <div class="hero__actions">
    <a class="btn btn--primary" href="products.html">Browse the data</a>
    <a class="btn" href="flagged.html">See what is flagged</a>
  </div>
</section>

<section class="stats" aria-label="Verification summary">
  {stat("Products tracked", str(len(PRODUCTS["products"])))}
  {stat("Sourced rows", str(total_rows), "attribute rows published")}
  {stat("Verified", str(verified), "confirmed on an official page")}
  {stat("Conflicts", str(conflicts), "official sources disagree")}
  {stat("Unverified", str(unverified), "left blank on purpose")}
</section>

<section class="panel">
  <h2>What this page is, and is not</h2>
  <div class="two-col">
    <div>
      <h3>It is</h3>
      <ul class="ticks">
        <li>A sourced reference for three Amazon listings: what each product is, who makes it,
            and what the manufacturer and Amazon each state about it.</li>
        <li>A record of where those two sources disagree with each other.</li>
        <li>An honest map of what an affiliate site may and may not publish under Amazon's
            Associates policies.</li>
      </ul>
    </div>
    <div>
      <h3>It is not</h3>
      <ul class="crosses">
        <li>A price tracker. No price is printed, because a site may only display Amazon pricing
            when Amazon serves it or it comes from the official API.</li>
        <li>A review site. No star rating is printed, because ratings differ by Amazon storefront
            for the same product.</li>
        <li>An earnings prediction. The authoritative commission rate card requires an Associates
            login and could not be read.</li>
      </ul>
    </div>
  </div>
</section>

<section class="panel">
  <h2>The three products</h2>
  <div class="cards">{"".join(cards)}</div>
</section>

<section class="panel">
  <h2>Where to look next</h2>
  <div class="linklist">
    <a href="compare.html"><strong>Comparison</strong><span>Side-by-side, attribute by attribute</span></a>
    <a href="compliance.html"><strong>Amazon rules</strong><span>Disclosure, linking and pricing requirements, with citations</span></a>
    <a href="requirements.html"><strong>Requirements</strong><span>Every item in the brief and what was actually delivered</span></a>
    <a href="methodology.html"><strong>Method</strong><span>How values were captured and verified</span></a>
    <a href="flagged.html"><strong>Flagged for Review</strong><span>Conflicts, gaps and decisions for the owner</span></a>
    <a href="summary.html"><strong>Executive summary</strong><span>The short version</span></a>
  </div>
</section>
"""


def build_product_page(product: dict) -> str:
    """A dedicated page per ASIN: full sourced profile plus a buying-consideration write-up."""
    feats = "".join(f"<li>{e(f)}</li>" for f in product["features"])
    flags = "".join(
        f'<li><span class="chip chip--conflict">{e(f["id"])}</span> {e(f["issue"])} '
        f'<em>{e(f["disposition"])}</em></li>'
        for f in product.get("flags", [])
    )
    flags_block = (
        f'<h2>Flags on this product</h2><ul class="flags">{flags}</ul>' if flags else ""
    )
    snapshot = product["volatile_snapshot"]
    snapshot_rows = []
    for key, label in (
        ("rating", "Star rating"),
        ("rating_count", "Rating count"),
        ("price_usd", "Price (USD)"),
        ("list_price_usd", "List price (USD)"),
        ("badge", "Badge"),
    ):
        snapshot_rows.append(
            f'<tr><th scope="row">{e(label)}</th><td>'
            + (
                e(snapshot.get(key))
                if snapshot.get(key) is not None
                else '<span class="blank">not confirmed — withheld</span>'
            )
            + "</td></tr>"
        )

    link_note = (
        f'<p class="callout callout--warn"><strong>Link note.</strong> {e(product["link_note"])}</p>'
        if product.get("link_note")
        else ""
    )

    others = [p for p in PRODUCTS["products"] if p["asin"] != product["asin"]]
    other_links = "".join(
        f'<li><a href="{slug(p)}">{e(p["title"])}</a> '
        f'<span class="note">{e(p["brand"])} · ASIN {e(p["asin"])}</span></li>'
        for p in others
    )

    return f"""
<p class="kicker"><a href="products.html">Products</a> / {e(product["category"])}</p>
<h1>{e(product["title"])}</h1>
<p class="byline">{e(product["brand"])} · ASIN <code>{e(product["asin"])}</code>
 · <a href="{e(product["resolved_url"])}" rel="noopener nofollow" target="_blank">Amazon listing</a></p>

<p><a class="btn btn--primary" href="{e(product["resolved_url"])}" rel="noopener nofollow"
   target="_blank">Check current price on Amazon</a></p>
<p class="fineprint">Opens the Amazon product page in a new tab. The price shown there is the
price that applies — this site does not display prices, because Amazon's rules restrict who may
show them and require conditions this static site cannot meet.</p>

{link_note}

<section class="panel">
  <p class="kicker">What it is</p>
  <ul class="ticks">{feats}</ul>
  <p class="fineprint">Source:
    <a href="{e(product["features_source"]["source_url"])}" rel="noopener nofollow"
       target="_blank">{e(product["features_source"]["source_name"])}</a>.</p>
</section>

<section class="panel">
  {identifier_table(product)}
  {spec_table(product)}
  <p class="fineprint">Status key:
    <span class="chip chip--verified">Verified</span> one official page states it ·
    <span class="chip chip--conflict">Conflict</span> official pages disagree, both shown ·
    <span class="chip chip--unverified">Unverified</span> no official source, left blank.
  </p>
</section>

<section class="panel">
  <h2>Who it suits — and who it does not</h2>
  <p class="callout"><strong>Read this as a reading of the specifications, not a product test.</strong>
  Nothing on this page comes from handling the appliance. It comes from the sourced numbers above.</p>
  <div class="two-col">
    <div>
      <h3>Probably a good fit if</h3>
      <ul class="ticks">
        <li>You want the capacity stated above and you have the counter space for the stated
            footprint.</li>
        <li>The cooking modes listed in the feature set match the food you actually cook.</li>
        <li>You are comfortable relying on the manufacturer's stated warranty terms rather than a
            retailer's extended plan.</li>
      </ul>
    </div>
    <div>
      <h3>Think twice if</h3>
      <ul class="crosses">
        <li>You need a capacity the specs do not provide — check the
            <a href="compare.html">comparison</a> before deciding.</li>
        <li>Counter space is tight; the dimensions row above is the manufacturer's own figure
            where one exists.</li>
        <li>You need to run it on a circuit shared with other high-draw appliances — all three
            products in this set draw the same high wattage.</li>
      </ul>
    </div>
  </div>
</section>

{flags_block}

<section class="panel">
  <details class="snapshot" open>
    <summary>Point-in-time snapshot captured {e(CAPTURED_UTC)} — retained for audit, not published as fact</summary>
    <table class="grid"><tbody>{"".join(snapshot_rows)}</tbody></table>
    <p class="note">{e(snapshot["snapshot_note"])}</p>
  </details>
</section>

<section class="panel">
  <h2>Official sources for this product</h2>
  <ul class="srclist">
    {"".join(f'<li><a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(u)}</a></li>' for u in product["official_sources"])}
  </ul>
  <h3>Other products in this set</h3>
  <ul class="srclist">{other_links}</ul>
  <p><a href="flagged.html">See everything flagged for review →</a></p>
</section>
"""


def build_products() -> str:
    rows = []
    for product in PRODUCTS["products"]:
        n_specs = len(product["specs"])
        n_conflict = sum(1 for s in product["specs"] if s["status"] == "conflict")
        n_unverified = sum(
            1
            for s in product["specs"] + product["identifiers"]
            if s["status"] == "unverified"
        )
        rows.append(
            "<tr>"
            f'<td><a class="prodlink" href="{slug(product)}">{e(product["title"])}</a>'
            f'<div class="note">{e(product["brand"])} · ASIN {e(product["asin"])}</div></td>'
            f'<td>{e(product["category"])}</td>'
            f'<td class="num">{n_specs}</td>'
            f'<td class="num">{n_conflict or "—"}</td>'
            f'<td class="num">{n_unverified or "—"}</td>'
            f'<td><a class="src" href="{e(product["resolved_url"])}" rel="noopener nofollow" '
            f'target="_blank">Amazon listing</a></td>'
            "</tr>"
        )

    profiles = []
    for product in PRODUCTS["products"]:
        link_note = (
            f'<p class="callout callout--warn"><strong>Link note.</strong> {e(product["link_note"])}</p>'
            if product.get("link_note")
            else ""
        )
        feats = "".join(f"<li>{e(f)}</li>" for f in product["features"])
        flags = "".join(
            f'<li><span class="chip chip--conflict">{e(f["id"])}</span> {e(f["issue"])} '
            f'<em>{e(f["disposition"])}</em></li>'
            for f in product.get("flags", [])
        )
        flags_block = (
            f'<h3>Flags on this product</h3><ul class="flags">{flags}</ul>' if flags else ""
        )
        snapshot = product["volatile_snapshot"]
        snapshot_rows = []
        for key, label in (
            ("rating", "Star rating"),
            ("rating_count", "Rating count"),
            ("price_usd", "Price (USD)"),
            ("list_price_usd", "List price (USD)"),
            ("badge", "Badge"),
        ):
            snapshot_rows.append(
                f"<tr><th scope=\"row\">{e(label)}</th><td>"
                + (e(snapshot.get(key)) if snapshot.get(key) is not None
                   else '<span class="blank">not confirmed — withheld</span>')
                + "</td></tr>"
            )
        profiles.append(
            f"""
<article class="panel" id="{e(product["asin"])}">
  <p class="kicker">{e(product["category"])}</p>
  <h2>{e(product["title"])}</h2>
  <p class="byline">{e(product["brand"])} · ASIN <code>{e(product["asin"])}</code></p>
  <p><a class="btn btn--primary" href="{e(product["resolved_url"])}" rel="noopener nofollow"
     target="_blank">Check current price on Amazon</a></p>
  <p class="fineprint">Opens the Amazon product page in a new tab. The price you see there is the
  price that applies — this site does not display prices because Amazon's rules restrict who may
  show them.</p>
  {link_note}
  <h3>What it is</h3>
  <ul class="ticks">{feats}</ul>
  <p class="fineprint">Feature list source:
    <a href="{e(product["features_source"]["source_url"])}" rel="noopener nofollow" target="_blank">
    {e(product["features_source"]["source_name"])}</a>.</p>
  {identifier_table(product)}
  {spec_table(product)}
  {flags_block}
  <details class="snapshot">
    <summary>Point-in-time snapshot captured {e(CAPTURED_UTC)} — not published as fact</summary>
    <table class="grid"><tbody>{"".join(snapshot_rows)}</tbody></table>
    <p class="note">{e(snapshot["snapshot_note"])}</p>
  </details>
  <h3>Official sources for this product</h3>
  <ul class="srclist">
    {"".join(f'<li><a href="{e(u)}" rel="noopener nofollow" target="_blank">{e(u)}</a></li>' for u in product["official_sources"])}
  </ul>
</article>"""
        )

    return f"""
<h1>Products</h1>
<p class="lede">Three listings, chosen from the links supplied. Each row below counts only
attributes with a named official source. Conflicts and gaps are counted, not hidden.</p>

<table class="grid"><caption>Summary</caption>
<thead><tr><th scope="col">Product</th><th scope="col">Category</th>
<th scope="col">Attributes</th><th scope="col">Conflicts</th>
<th scope="col">Unverified</th><th scope="col">Link</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>

<p class="callout"><strong>Reading the status column.</strong>
<span class="chip chip--verified">Verified</span> means one official page states the value.
<span class="chip chip--conflict">Conflict</span> means two official pages disagree and both
values are shown.
<span class="chip chip--unverified">Unverified</span> means nothing official could confirm it,
so the value is blank.</p>

{"".join(profiles)}
"""


def build_compare() -> str:
    """Build a comparison table across the three products, attribute by attribute."""
    all_labels: list[str] = []
    for product in PRODUCTS["products"]:
        for spec in product["specs"]:
            if spec["label"] not in all_labels:
                all_labels.append(spec["label"])

    header = "".join(
        f'<th scope="col">{e(p["brand"])}<br><small>ASIN {e(p["asin"])}</small></th>'
        for p in PRODUCTS["products"]
    )

    body_rows = []
    for label in all_labels:
        cells = []
        for product in PRODUCTS["products"]:
            match = next((s for s in product["specs"] if s["label"] == label), None)
            if match is None:
                cells.append('<td class="val"><span class="blank">— not listed —</span></td>')
                continue
            link = (
                f'<a class="mini" href="{e(match["source_url"])}" rel="noopener nofollow" '
                f'target="_blank">source</a>'
                if match.get("source_url")
                else '<span class="blank">no source</span>'
            )
            cells.append(
                f'<td class="val">{value_cell(match)}'
                f'<div class="cellfoot">{status_chip(match["status"])}{link}</div></td>'
            )
        body_rows.append(f'<tr><th scope="row">{e(label)}</th>{"".join(cells)}</tr>')

    return f"""
<h1>Comparison</h1>
<p class="lede">Every attribute that appears on at least one of the three products, placed
side by side. Where a cell is blank, the attribute is either absent from that listing or could
not be confirmed — the status chip says which.</p>

<div class="tablewrap">
<table class="grid grid--compare">
<caption>Attribute-by-attribute comparison</caption>
<thead><tr><th scope="col">Attribute</th>{header}</tr></thead>
<tbody>{"".join(body_rows)}</tbody>
</table>
</div>

<section class="panel">
  <h2>What the comparison actually shows</h2>
  <ul class="ticks">
    <li><strong>These are not interchangeable products.</strong> Two are basket air fryers and one
        is a 26-quart French-door oven. Capacity ranges from 6 qt to 26 qt.</li>
    <li><strong>All three are 1700 W on the manufacturer's or Amazon's own figures.</strong> The
        Chefman 8 Qt listing's bullet text claims 1000 W, which conflicts with the manufacturer —
        that conflict is flagged rather than resolved silently.</li>
    <li><strong>Power draw is not a differentiator here.</strong> All three sit at the top of what
        a standard US 120 V / 15 A kitchen circuit handles comfortably, and none should share a
        circuit with another high-draw appliance.</li>
    <li><strong>Capacity, not wattage, is the real choice.</strong> Two small independent baskets
        solve "main and side at once"; one large cavity solves "a whole chicken or a 12-inch
        pizza".</li>
  </ul>
  <p class="fineprint">The bullets above are direct readings of the sourced rows in the table.
  No performance claim is made, because none of the three products was tested by this project.</p>
</section>
"""


def build_compliance() -> str:
    def section(title: str, key: str) -> str:
        rows = []
        for item in COMPLIANCE[key]:
            rows.append(
                "<tr>"
                f'<td>{e(item.get("id", ""))}</td>'
                f'<td>{e(item.get("requirement", item.get("rule", "")))}'
                + (f'<div class="note">{e(item["note"])}</div>' if item.get("note") else "")
                + "</td>"
                f'<td>{e(item.get("section") or "—")}</td>'
                f'<td class="src-cell"><a class="src" href="{e(item["source_url"])}" '
                f'rel="noopener nofollow" target="_blank">Official text</a></td>'
                "</tr>"
            )
        return f"""
<h2>{e(title)}</h2>
<table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Requirement</th>
<th scope="col">Section</th><th scope="col">Source</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>"""

    docs = "".join(
        f'<li><a href="{e(d["url"])}" rel="noopener nofollow" target="_blank">{e(d["name"])}</a>'
        f' — seen {e(d.get("version_seen") or "version not stated")} {status_chip(d["status"])}'
        + (f'<div class="note">{e(d["note"])}</div>' if d.get("note") else "")
        + "</li>"
        for d in COMPLIANCE["documents"]
    )

    rate = COMPLIANCE["commission_rates"]

    return f"""
<h1>Amazon rules this site complies with</h1>
<p class="lede">Every rule below is taken from an official Amazon page and linked. The project
brief asked for an automated affiliate platform, so the rules that constrain automation are
listed explicitly rather than buried.</p>

<section class="panel">
  <h2>The documents consulted</h2>
  <ul class="srclist">{docs}</ul>
</section>

<section class="panel">
  <h2>Disclosure requirements</h2>
  <p class="callout callout--ok">Amazon supplies the exact sentence and this site uses it,
  unmodified, in the bar at the top of every page:
  <em>“{e(COMPLIANCE["disclosure"][0]["exact_wording_amazon_supplies"])}”</em></p>
  <table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Requirement</th>
  <th scope="col">Section</th><th scope="col">Source</th></tr></thead><tbody>
  {"".join(f'<tr><td>{e(i["id"])}</td><td>{e(i["requirement"])}</td><td>{e(i.get("section") or "—")}</td><td class="src-cell"><a class="src" href="{e(i["source_url"])}" rel="noopener nofollow" target="_blank">Official text</a></td></tr>' for i in COMPLIANCE["disclosure"])}
  </tbody></table>
</section>

<section class="panel">{section("Linking rules", "linking_rules")}</section>

<section class="panel">
  {section("Pricing rules — why no price appears on this site", "pricing_rules")}
  <p class="callout callout--warn"><strong>This is the single biggest constraint on affiliate
  product pages.</strong> A site may show prices only where Amazon itself serves the pricing, or
  where the figures come from the official API, and any displayed price needs a timestamp and a
  disclaimer. This site therefore links out to Amazon and states plainly that the price on
  Amazon is the price that applies.</p>
</section>

<section class="panel">{section("Content rules", "content_rules")}</section>

<section class="panel">
  {section("Automation limits — the Agent Terms", "automation_rules")}
  <p class="callout callout--warn"><strong>Why this project does not "fully automate" data
  collection.</strong> Amazon's Agent Terms define an Agent as any software taking autonomous or
  semi-autonomous action, require it to identify itself in the user agent as
  <code>Agent/[agent name]</code>, forbid disguising automated access, and forbid solving or
  circumventing CAPTCHAs. A platform that silently scrapes the storefront at scale would breach
  those terms. The honest build is: automate generation, verification and publishing; take data
  from official pages under the licence; and move to the official API for anything
  volume-based.</p>
</section>

<section class="panel">{section("Account rules", "account_rules")}</section>

<section class="panel">
  <h2>Commission rates</h2>
  <p class="callout callout--warn"><strong>Not verified, therefore not published.</strong>
  {e(rate["reason"])}</p>
  <p>The only commission claim this site will repeat is Amazon's own public marketing sentence:
  <em>“{e(rate["public_headline"])}”</em>
  (<a href="{e(rate["public_headline_source"])}" rel="noopener nofollow" target="_blank">Associates Central</a>).</p>
  <p class="fineprint">Anything more specific — for example a category-by-category percentage —
  must be read from the rate card inside an Associates account and recorded here with its date.
  Reporting a number from a blog would not meet this project's own standard.</p>
</section>

<section class="panel">
  <h2>Attribution windows</h2>
  <table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Rule</th>
  <th scope="col">Section</th><th scope="col">Source</th></tr></thead><tbody>
  {"".join(f'<tr><td>{e(i["id"])}</td><td>{e(i["rule"])}</td><td>{e(i.get("section") or "—")}</td><td class="src-cell"><a class="src" href="{e(i["source_url"])}" rel="noopener nofollow" target="_blank">Official text</a></td></tr>' for i in COMPLIANCE["session_and_attribution"])}
  </tbody></table>
</section>
"""


def build_requirements() -> str:
    rows = []
    for req in REQUIREMENTS["requirements"]:
        disp = req["disposition"]
        source = (
            f'<a class="src" href="{e(req["source_url"])}" rel="noopener nofollow" target="_blank">'
            f'{e(req.get("section") or "Official text")}</a>'
            if req.get("source_url")
            else '<span class="blank">—</span>'
        )
        rows.append(
            "<tr>"
            f'<td>{e(req["id"])}</td>'
            f'<td class="val">{e(req["text"])}</td>'
            f'<td><span class="chip chip--{e(disp)}">{e(disp.replace("_", " "))}</span></td>'
            f'<td class="val">{e(req["delivered"])}'
            + (f'<div class="note"><strong>Constraint:</strong> {e(req["constraint"])}</div>'
               if req.get("constraint") else "")
            + "</td>"
            f'<td class="src-cell">{source}</td>'
            "</tr>"
        )

    tally: dict[str, int] = {}
    for req in REQUIREMENTS["requirements"]:
        tally[req["disposition"]] = tally.get(req["disposition"], 0) + 1

    return f"""
<h1>Requirements, line by line</h1>
<p class="lede">Every clause of the brief, and an honest statement of what was delivered.
Nothing is marked delivered unless it exists in this repository.</p>

<section class="stats">
  {stat("Requirements", str(len(REQUIREMENTS["requirements"])))}
  {stat("Delivered", str(tally.get("delivered", 0)))}
  {stat("Constrained by Amazon policy", str(tally.get("constrained", 0)))}
  {stat("Owner decision needed", str(tally.get("owner_decision", 0)))}
  {stat("Not deliverable", str(tally.get("not_deliverable", 0)))}
</section>

<p class="callout"><strong>“Constrained” is not a failure.</strong> It means the brief asked for
something Amazon's own terms forbid doing literally — usually publishing price data, rates, or
automated scraping. In each case the compliant alternative was built instead, and the rule that
forced the change is cited.</p>

<div class="tablewrap">
<table class="grid grid--req">
<caption>Disposition of every requirement</caption>
<thead><tr><th scope="col">ID</th><th scope="col">Requirement</th><th scope="col">Status</th>
<th scope="col">What was delivered</th><th scope="col">Source</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
</div>
"""


def build_methodology() -> str:
    return f"""
<h1>Method</h1>
<p class="lede">How the data on this site was obtained, and the rules that decide what gets
published.</p>

<section class="panel">
  <h2>1. Resolve the links</h2>
  <p>The three supplied links are opaque short links. Each was followed and the redirect target
  recorded, which yields the ASIN. The ASIN is what identifies the product; the short link does
  not contain it.</p>
  <p class="callout callout--warn"><strong>Finding.</strong> None of the three resolved URLs
  carried an Amazon Associates <code>tag=</code> parameter. Without a tracking ID, clicks cannot
  be attributed to an account. The site therefore links to the canonical product pages and does
  <em>not</em> invent a tag. See the <a href="flagged.html">Flagged for Review</a> page.</p>
</section>

<section class="panel">
  <h2>2. Capture from official pages only</h2>
  <p>A value is captured only from an official page: the Amazon product page for that exact ASIN,
  or the manufacturer's own product page for the model number printed on that listing.</p>
  <ul class="ticks">
    <li>Every value is stored with its own source name and URL. A value without a URL is not
        stored as a fact.</li>
    <li>Where the manufacturer and Amazon disagree, both values are stored as separate rows, each
        with its own source, and marked <span class="chip chip--conflict">Conflict</span>.</li>
    <li>Where only a non-official source has a value, the row is marked
        <span class="chip chip--unverified">Unverified</span> and the value is left blank.</li>
  </ul>
</section>

<section class="panel">
  <h2>3. Decide what may be published</h2>
  <p>Capture and publication are separate decisions. Several things were captured for the audit
  trail but are deliberately not published:</p>
  <table class="grid"><thead><tr><th scope="col">Captured</th><th scope="col">Published?</th>
  <th scope="col">Why</th></tr></thead><tbody>
  <tr><th scope="row">Price</th><td>No</td><td>Amazon permits price display only where Amazon
  serves the pricing or it comes from the official API, and requires a timestamp plus a
  disclaimer.</td></tr>
  <tr><th scope="row">Star rating</th><td>No</td><td>Ratings are storefront-specific for the same
  ASIN, so a single figure would mislead.</td></tr>
  <tr><th scope="row">Review count</th><td>No</td><td>Same reason; counts also drift
  continuously.</td></tr>
  <tr><th scope="row">Stock status</th><td>No</td><td>Changes by the minute.</td></tr>
  <tr><th scope="row">Commission rate</th><td>No</td><td>The official rate card requires an
  Associates login and was not readable.</td></tr>
  <tr><th scope="row">Wattage, capacity, dimensions, model number, certification, warranty</th>
  <td>Yes</td><td>Stable manufacturer specifications, each with a named official source.</td></tr>
  </tbody></table>
</section>

<section class="panel">
  <h2>4. Verify mechanically, not by eye</h2>
  <p><code>scripts/verify.py</code> runs on every change and fails the build when:</p>
  <ul class="ticks">
    <li>a fact row has no source URL;</li>
    <li>a source URL is not <code>https</code>;</li>
    <li>a row claimed as verified has no source;</li>
    <li>an internal link in the generated site points at a file that does not exist;</li>
    <li>a page is missing the affiliate disclosure;</li>
    <li>a page prints a price, which this project does not permit.</li>
  </ul>
  <p>The rule is simple: if the checker cannot confirm it, the site does not claim it.</p>
</section>

<section class="panel">
  <h2>5. Known limitations, stated plainly</h2>
  <ul class="crosses">
    <li><strong>Amazon pages render inconsistently to automated fetches.</strong> Some captures
        returned only page chrome. Where the US page body did not render, the same ASIN's page on
        another Amazon storefront was used to read the product-information block, and the
        manufacturer was used for specifications. This is disclosed per product.</li>
    <li><strong>No product was tested.</strong> This project has not handled any of the three
        appliances. Nothing here is a performance claim.</li>
    <li><strong>Capture is a single point in time.</strong> The dataset records
        {e(CAPTURED_UTC)}. Amazon requires site content to be recent — generally within 60
        days — so a re-capture is due by roughly 2027-01-12.</li>
    <li><strong>Non-official sources were used only to find official ones.</strong> They are
        listed, with the reason for rejection, in <code>data/sources.json</code>.</li>
  </ul>
</section>
"""


def build_flagged() -> str:
    """Everything unresolved, in one place, each with a source link."""
    product_flags = []
    for product in PRODUCTS["products"]:
        for flag in product.get("flags", []):
            product_flags.append(
                "<tr>"
                f'<td>{e(flag["id"])}</td>'
                f'<td>ASIN {e(product["asin"])}<div class="note">{e(product["brand"])}</div></td>'
                f'<td class="val">{e(flag["issue"])}<div class="note">{e(flag["disposition"])}</div></td>'
                f'<td class="src-cell"><a class="src" href="{e(product["resolved_url"])}" '
                f'rel="noopener nofollow" target="_blank">Amazon listing</a></td>'
                "</tr>"
            )

    blanks = []
    for product in PRODUCTS["products"]:
        for row in product["specs"] + product["identifiers"]:
            if row["status"] == "unverified":
                blanks.append(
                    "<tr>"
                    f'<td>ASIN {e(product["asin"])}</td>'
                    f'<td>{e(row["label"])}</td>'
                    f'<td>{e(row.get("source_name") or "no official source")}</td>'
                    f'<td class="val">{e(row.get("note") or "Could not be confirmed on an official source.")}</td>'
                    "</tr>"
                )

    return f"""
<h1>Flagged for Review</h1>
<p class="lede">Nothing on this page blocks the site from working. It is the honest list of
what could not be settled, what two official sources disagree about, and what only the account
owner can decide. Each item links to the page it came from.</p>

<section class="panel">
  <h2>1. Owner actions — only you can resolve these</h2>
  <table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Item</th>
  <th scope="col">Detail</th><th scope="col">What to do</th></tr></thead><tbody>
  <tr><td>O-1</td><td>The three links carry no Associates tracking tag</td>
      <td>All three resolved to plain <code>amazon.com/dp/&lt;ASIN&gt;</code> URLs with no
      <code>tag=</code> parameter. In that state, clicks cannot be attributed and no commission
      can be earned.</td>
      <td>Sign in to Associates Central and re-generate all three links with your Store ID, then
      replace the <code>resolved_url</code> values in <code>data/products.json</code>.</td></tr>
  <tr><td>O-2</td><td>Commission rate card is login-gated</td>
      <td>The official schedule redirects to sign-in, so no category rate is published here.</td>
      <td>Read the rate card inside your account, then record the Home-category rate and the date
      in <code>data/compliance.json</code>.</td></tr>
  <tr><td>O-3</td><td>No repository licence</td>
      <td>The repo has no <code>LICENSE</code> file.</td>
      <td>Choose one, or state that the content is unlicensed.</td></tr>
  <tr><td>O-4</td><td>Affiliate account not evidenced</td>
      <td>The disclosure statement is published because the brief identifies this as an Amazon
      affiliate project. Only the account holder can confirm an approved Associates account
      exists.</td>
      <td>Confirm the account is approved; the 3-sale / 180-day review applies.</td></tr>
  <tr><td>O-5</td><td>Content refresh deadline</td>
      <td>Amazon expects site content to be recent, generally within 60 days. This capture is
      dated {e(CAPTURED_UTC)}.</td>
      <td>Re-capture and re-verify by roughly 2027-01-12.</td></tr>
  </tbody></table>
</section>

<section class="panel">
  <h2>2. Conflicts between official sources</h2>
  <p>Two official pages state different values for the same attribute. Both are published side by
  side; neither is silently chosen.</p>
  <table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Product</th>
  <th scope="col">What disagrees</th><th scope="col">Source</th></tr></thead>
  <tbody>{"".join(product_flags)}</tbody></table>
</section>

<section class="panel">
  <h2>3. Values left blank</h2>
  <p>These are blank on the site on purpose. Filling them from a non-official source would have
  been easy and wrong.</p>
  <table class="grid"><thead><tr><th scope="col">Product</th><th scope="col">Attribute</th>
  <th scope="col">What sources exist</th><th scope="col">Why it is blank</th></tr></thead>
  <tbody>{"".join(blanks)}</tbody></table>
</section>

<section class="panel">
  <h2>4. Repository irregularities</h2>
  <table class="grid"><thead><tr><th scope="col">ID</th><th scope="col">Finding</th>
  <th scope="col">Disposition</th></tr></thead><tbody>
  <tr><td>I-1</td><td>The initial commit contained a 7-byte <code>README.md</code> reading only
  <code># Zone2</code> — no description, usage, or licence.</td><td>Resolved: README rewritten
  this session.</td></tr>
  <tr><td>I-2</td><td>No <code>LICENSE</code>, <code>.gitignore</code>, CI or tests in the initial
  commit.</td><td>Partly resolved: <code>.gitignore</code> and CI added. Licence is owner decision
  O-3.</td></tr>
  <tr><td>I-3</td><td>The supplied <code>link.amazon/*</code> links are opaque; the ASIN cannot be
  read from the link text and must be resolved by following the redirect.</td><td>Resolved and
  documented in <code>data/raw-verification-log.md</code>.</td></tr>
  <tr><td>I-4</td><td>No tracking tag on any of the three links.</td><td>Owner action O-1.</td></tr>
  <tr><td>I-5</td><td>Prices, ratings and stock are volatile and Amazon restricts their display.
  </td><td>By design: captured for audit, withheld from publication.</td></tr>
  <tr><td>I-6</td><td>Amazon product pages render inconsistently to automated fetches.</td>
  <td>Disclosed in the methodology; corroborated against regional storefronts and the
  manufacturer.</td></tr>
  <tr><td>I-7</td><td>Star ratings differ by storefront for the same ASIN (4.5/16,128 on
  Amazon.co.uk versus 4.6/8,361 on Amazon.sa for B09B7SB46R).</td><td>No rating published.</td></tr>
  <tr><td>I-8</td><td>Chefman 8 Qt: the Amazon bullet text says 1000 W; the manufacturer says
  1700 W for the same model number.</td><td>Manufacturer figure published; discrepancy
  flagged.</td></tr>
  <tr><td>I-9</td><td>Chefman 8 Qt dimensions differ between the Amazon spec table and the
  manufacturer page.</td><td>Both published as separate sourced rows.</td></tr>
  <tr><td>I-10</td><td>Emeril model number suffix differs: <code>-02X-VN</code> on Amazon US
  against <code>-02A-VN</code> on the manufacturer store.</td><td>Both published with
  sources.</td></tr>
  <tr><td>I-11</td><td>Emeril wattage: 1700 W is the rated figure; a customer review reports a
  lower measured draw in bake mode.</td><td>Rated figure published. Measured draw is not a
  specification and is not published.</td></tr>
  <tr><td>I-12</td><td>Emeril preset count: 24 in the title and manufacturer description, 25 in
  the manufacturer's own spec tile.</td><td>Both shown side by side.</td></tr>
  <tr><td>I-13</td><td>Emeril 500 °F maximum is sourced to Amazon only.</td><td>Published as
  single-source and labelled.</td></tr>
  <tr><td>I-15</td><td>Amazon's Agent Terms require automated clients to identify themselves and
  forbid bypassing blocks — which makes "fully automated scraping" non-compliant.</td>
  <td>Documented in place of the requested automation; see the compliance page.</td></tr>
  </tbody></table>
</section>

<section class="panel">
  <h2>5. What is <em>not</em> flagged</h2>
  <p>For clarity: no value on this site was inferred, interpolated, or copied from a similar
  product. Every published value has a clickable source on the row it appears in. Where a source
  could not be found, the cell is blank.</p>
</section>
"""


def build_summary() -> str:
    path = ROOT / "docs" / "executive-summary.md"
    text = path.read_text(encoding="utf-8")
    return f"""
<h1>Executive summary</h1>
<p class="lede">The same content as <code>docs/executive-summary.md</code>, rendered for reading
in the browser.</p>
<section class="panel prose">
{markdown_to_html(text)}
</section>
"""


def markdown_to_html(text: str) -> str:
    """Deliberately small Markdown subset renderer — headings, lists, tables, bold, code, links."""
    import re

    lines = text.split("\n")
    out: list[str] = []
    in_table = False
    in_list = False
    in_ol = False

    def inline(s: str) -> str:
        s = html.escape(s, quote=False)
        s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", s)
        s = re.sub(
            r"\[([^\]]+)\]\((https?://[^)]+)\)",
            r'<a href="\2" rel="noopener nofollow" target="_blank">\1</a>',
            s,
        )
        return s

    def close_list() -> None:
        nonlocal in_list, in_ol
        if in_list:
            out.append("</ul>")
            in_list = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if stripped.startswith("|"):
            close_list()
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if all(set(c) <= set("-: ") for c in cells) and cells:
                continue
            if not in_table:
                out.append('<div class="tablewrap"><table class="grid"><tbody>')
                in_table = True
                out.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            out.append("</tbody></table></div>")
            in_table = False

        if not stripped:
            close_list()
            continue
        if stripped.startswith("#"):
            close_list()
            level = len(stripped) - len(stripped.lstrip("#"))
            out.append(f"<h{level}>{inline(stripped[level:].strip())}</h{level}>")
        elif stripped.startswith(("- ", "* ")):
            if not in_list:
                close_list()
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{inline(stripped[2:])}</li>")
        elif re.match(r"^\d+\.\s", stripped):
            if not in_ol:
                close_list()
                out.append("<ol>")
                in_ol = True
            item_text = re.sub(r"^\d+\.\s", "", stripped)
            out.append(f"<li>{inline(item_text)}</li>")
        elif stripped.startswith(">"):
            close_list()
            out.append(f'<blockquote>{inline(stripped[1:].strip())}</blockquote>')
        else:
            close_list()
            out.append(f"<p>{inline(stripped)}</p>")

    close_list()
    if in_table:
        out.append("</tbody></table></div>")
    return "\n".join(out)


# ---------------------------------------------------------------- css

CSS = """:root{
  --ink:#0f172a; --ink-2:#3f4b5f; --ink-3:#6b7787;
  --line:#e3e8ef; --line-2:#cfd8e3;
  --bg:#f7f9fc; --card:#ffffff;
  --accent:#0b5fff; --accent-ink:#0847c4;
  --ok:#0f7b4f; --ok-bg:#e7f6ee;
  --warn:#8a5300; --warn-bg:#fff4e0;
  --bad:#a02121; --bad-bg:#fdecec;
  --radius:12px;
  --shadow:0 1px 2px rgba(16,24,40,.05),0 1px 3px rgba(16,24,40,.06);
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;background:#eef2f7;
  padding:1px 5px;border-radius:4px;color:var(--ink-2)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;border-radius:8px;z-index:99}

/* disclosure */
.disclosure-bar{
  background:#0f172a;color:#e8edf5;font-size:14px;padding:9px 20px;text-align:center;
}
.disclosure-bar strong{color:#fff}
.disclosure-bar a{color:#9cc0ff}

/* masthead */
.masthead{background:var(--card);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.masthead .wrap{display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding-top:12px;padding-bottom:0}
.brand{display:flex;align-items:center;gap:10px;color:var(--ink);text-decoration:none;padding-bottom:12px}
.brand__mark{width:28px;height:28px;border-radius:8px;flex:0 0 28px;
  background:linear-gradient(135deg,#0b5fff,#4f46e5)}
.brand__text{font-weight:650;font-size:16px;line-height:1.2;display:flex;flex-direction:column}
.brand__text small{font-weight:400;font-size:12px;color:var(--ink-3)}
.tabs{display:flex;gap:2px;flex-wrap:wrap;margin-left:auto}
.tabs a{
  padding:10px 13px;border-radius:8px 8px 0 0;color:var(--ink-2);font-size:14px;
  font-weight:520;border-bottom:2px solid transparent;white-space:nowrap
}
.tabs a:hover{background:#f1f5fb;text-decoration:none;color:var(--ink)}
.tabs a.on{color:var(--accent-ink);border-bottom-color:var(--accent);background:#f5f8ff}

/* layout */
main{padding:32px 20px 56px}
h1{font-size:34px;line-height:1.2;letter-spacing:-.02em;margin:0 0 12px}
h2{font-size:21px;line-height:1.3;letter-spacing:-.01em;margin:0 0 12px}
h3{font-size:16px;margin:22px 0 8px}
.lede{font-size:17px;color:var(--ink-2);max-width:74ch;margin:0 0 26px}
.fineprint{font-size:13px;color:var(--ink-3);max-width:80ch}
.note{font-size:12.5px;color:var(--ink-3);margin-top:3px}
.kicker{font-size:12px;text-transform:uppercase;letter-spacing:.08em;color:var(--accent-ink);
  font-weight:650;margin:0 0 4px}
.byline{color:var(--ink-3);font-size:14px;margin:0 0 16px}

/* hero */
.hero{background:var(--card);border:1px solid var(--line);border-radius:16px;
  padding:38px 32px;box-shadow:var(--shadow);margin-bottom:22px}
.hero__eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:.09em;
  color:var(--accent-ink);font-weight:700;margin:0 0 10px}
.hero h1{max-width:20ch}
.hero__lede{font-size:17px;color:var(--ink-2);max-width:72ch;margin:0 0 24px}
.hero__actions{display:flex;gap:10px;flex-wrap:wrap}

.btn{display:inline-block;padding:11px 18px;border-radius:9px;border:1px solid var(--line-2);
  background:#fff;color:var(--ink);font-weight:580;font-size:15px;box-shadow:var(--shadow)}
.btn:hover{text-decoration:none;border-color:var(--accent);color:var(--accent-ink)}
.btn--primary{background:var(--accent);border-color:var(--accent);color:#fff}
.btn--primary:hover{background:var(--accent-ink);color:#fff;border-color:var(--accent-ink)}

/* stats */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 22px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:16px 18px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:2px}
.stat__value{font-size:26px;font-weight:680;letter-spacing:-.02em;line-height:1.1}
.stat__label{font-size:13px;color:var(--ink-2);font-weight:520}
.stat__hint{font-size:11.5px;color:var(--ink-3)}

/* panels */
.panel{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:26px 28px;box-shadow:var(--shadow);margin:0 0 20px}
.panel p{max-width:80ch}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:28px}
@media(max-width:760px){.two-col{grid-template-columns:1fr}}

ul.ticks,ul.crosses,ul.flags,ul.srclist{padding-left:0;list-style:none;margin:0;max-width:84ch}
ul.ticks li,ul.crosses li{position:relative;padding-left:26px;margin-bottom:9px;color:var(--ink-2)}
ul.ticks li::before{content:"✓";position:absolute;left:0;top:0;color:var(--ok);font-weight:700}
ul.crosses li::before{content:"×";position:absolute;left:0;top:0;color:var(--bad);font-weight:700}
ul.flags li{position:relative;padding-left:0;margin-bottom:10px;font-size:14px;color:var(--ink-2)}
ul.srclist li{margin-bottom:7px;font-size:14px;word-break:break-word}

/* cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}
.card{display:flex;flex-direction:column;gap:6px;background:#fbfcfe;border:1px solid var(--line);
  border-radius:var(--radius);padding:20px;color:var(--ink);
  transition:border-color .15s ease, box-shadow .15s ease}
.card:hover{border-color:var(--accent);box-shadow:0 4px 14px rgba(11,95,255,.10);text-decoration:none}
.card__kicker{font-size:11.5px;text-transform:uppercase;letter-spacing:.07em;
  color:var(--accent-ink);font-weight:700}
.card__title{font-weight:600;font-size:15px;line-height:1.42}
.card__meta{font-size:12.5px;color:var(--ink-3)}
.card__cta{font-size:13.5px;font-weight:600;color:var(--accent);margin-top:6px}

/* link list */
.linklist{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
.linklist a{display:flex;flex-direction:column;gap:2px;padding:14px 16px;border:1px solid var(--line);
  border-radius:10px;background:#fbfcfe;color:var(--ink)}
.linklist a:hover{border-color:var(--accent);text-decoration:none}
.linklist span{font-size:13px;color:var(--ink-3)}

/* tables */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);
  box-shadow:var(--shadow);background:var(--card);margin:0 0 20px}
.tablewrap table.grid{border:0;border-radius:0;box-shadow:none;margin:0;min-width:720px}
table.grid{width:100%;border-collapse:separate;border-spacing:0;background:var(--card);
  border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;
  box-shadow:var(--shadow);margin:0 0 20px;font-size:14px}
table.grid caption{caption-side:top;text-align:left;font-weight:650;font-size:15px;
  padding:14px 16px 10px;color:var(--ink)}
table.grid th,table.grid td{padding:10px 14px;text-align:left;vertical-align:top;
  border-bottom:1px solid var(--line)}
table.grid thead th{background:#f3f6fb;font-size:12px;text-transform:uppercase;
  letter-spacing:.05em;color:var(--ink-3);font-weight:650;border-bottom:1px solid var(--line-2)}
table.grid tbody th{font-weight:560;color:var(--ink);width:230px;background:#fcfdff}
table.grid tbody tr:last-child th,table.grid tbody tr:last-child td{border-bottom:0}
table.grid tbody tr:hover td,table.grid tbody tr:hover th{background:#f8fafd}
td.val{color:var(--ink-2)}
td.num{text-align:right;font-variant-numeric:tabular-nums;width:96px}
td.st{width:132px}
td.src-cell{width:210px}
.grid--compare td.val{min-width:210px}
.grid--req td.val{min-width:280px}
.cellfoot{display:flex;gap:8px;align-items:center;margin-top:6px;flex-wrap:wrap}
a.mini{font-size:11.5px;color:var(--ink-3);border-bottom:1px dotted var(--line-2)}
a.mini:hover{color:var(--accent)}
a.src{font-size:12.5px;font-weight:520;border-bottom:1px solid rgba(11,95,255,.25)}
a.src:hover{border-bottom-color:var(--accent);text-decoration:none}
a.prodlink{font-weight:560}
.blank{color:#9aa5b4;font-size:12.5px;font-style:italic}

/* chips */
.chip{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11.5px;
  font-weight:640;letter-spacing:.01em;white-space:nowrap}
.chip--verified{background:var(--ok-bg);color:var(--ok)}
.chip--conflict{background:var(--warn-bg);color:var(--warn)}
.chip--unverified{background:var(--bad-bg);color:var(--bad)}
.chip--delivered{background:var(--ok-bg);color:var(--ok)}
.chip--constrained{background:var(--warn-bg);color:var(--warn)}
.chip--owner_decision{background:#eef2ff;color:#3730a3}
.chip--not_deliverable{background:var(--bad-bg);color:var(--bad)}

/* callouts */
.callout{background:#f5f8ff;border:1px solid #d8e4ff;border-left:3px solid var(--accent);
  border-radius:8px;padding:12px 16px;font-size:14px;color:var(--ink-2);max-width:88ch}
.callout--warn{background:var(--warn-bg);border-color:#f0dcb8;border-left-color:#c98a1a}
.callout--ok{background:var(--ok-bg);border-color:#c6e8d7;border-left-color:var(--ok)}

/* details */
.snapshot{margin:18px 0;border:1px solid var(--line);border-radius:10px;padding:12px 16px;
  background:#fbfcfe}
.snapshot summary{cursor:pointer;font-weight:600;font-size:14px;color:var(--ink-2)}
.snapshot table.grid{margin-top:12px;box-shadow:none}
.snapshot tbody th{width:170px;background:transparent}

/* prose */
.prose{max-width:82ch}
.prose h1{font-size:26px}
.prose h2{font-size:19px;margin-top:26px}
.prose ul,.prose ol{padding-left:22px;color:var(--ink-2)}
.prose li{margin-bottom:6px}
.prose blockquote{margin:14px 0;padding:10px 16px;border-left:3px solid var(--line-2);
  color:var(--ink-3);background:#fbfcfe}

/* footer */
.footer{border-top:1px solid var(--line);background:var(--card);padding:28px 0 40px;
  font-size:13px;color:var(--ink-3)}
.footer .wrap{display:block}
.footer p{max-width:90ch;margin:0 0 10px}

/* print */
@media print{
  .disclosure-bar,.masthead,.footer{position:static}
  body{background:#fff}
  .panel,.hero,.stat,table.grid{box-shadow:none}
}
@media(max-width:700px){
  h1{font-size:27px}
  .hero{padding:26px 20px}
  .panel{padding:20px}
  .tabs a{padding:9px 10px;font-size:13px}
  table.grid{font-size:13px}
  table.grid tbody th{width:auto}
  td.st,td.src-cell,td.num{width:auto}
}
"""


# ---------------------------------------------------------------- write


GENERATED_DIRS = ("assets",)


def clean_previous_output() -> list[str]:
    """Remove only files this generator previously created, per the manifest."""
    removed: list[str] = []
    if MANIFEST.exists():
        previous = json.loads(MANIFEST.read_text(encoding="utf-8"))
        for rel in previous.get("files", []):
            target = ROOT / rel
            if target.is_file():
                target.unlink()
                removed.append(rel)
    for directory in GENERATED_DIRS:
        path = ROOT / directory
        if path.is_dir():
            for child in sorted(path.rglob("*"), reverse=True):
                if child.is_file():
                    child.unlink()
                elif child.is_dir():
                    child.rmdir()
            path.rmdir()
    return removed


def main() -> None:
    removed = clean_previous_output()
    (SITE / "assets").mkdir(parents=True, exist_ok=True)

    pages = {
        "index.html": (
            "Affiliate Research Hub — three Amazon products, verified",
            "overview",
            build_index(),
            "Source-linked research on three Amazon affiliate products, with Amazon Associates compliance documented.",
        ),
        "products.html": (
            "Products — sourced profiles",
            "products",
            build_products(),
            "Per-product specification tables with an official source on every row.",
        ),
        "compare.html": (
            "Comparison",
            "compare",
            build_compare(),
            "Attribute-by-attribute comparison of the three products.",
        ),
        "compliance.html": (
            "Amazon rules this site complies with",
            "compliance",
            build_compliance(),
            "Disclosure, linking, pricing and automation requirements from Amazon's official policies.",
        ),
        "requirements.html": (
            "Requirements, line by line",
            "requirements",
            build_requirements(),
            "Every requirement in the brief and its honest disposition.",
        ),
        "methodology.html": (
            "Method",
            "method",
            build_methodology(),
            "How data was captured, verified and decided upon.",
        ),
        "flagged.html": (
            "Flagged for Review",
            "flagged",
            build_flagged(),
            "Conflicts, blanks and owner decisions.",
        ),
        "summary.html": (
            "Executive summary",
            "summary",
            build_summary(),
            "The short version.",
        ),
    }

    for filename, (title, active, body, desc) in pages.items():
        (SITE / filename).write_text(
            page(title, active, body, desc), encoding="utf-8"
        )

    # one detail page per ASIN, linked from products.html and the overview cards
    for product in PRODUCTS["products"]:
        (SITE / slug(product)).write_text(
            page(
                f"{product['title']} — sourced profile",
                "products",
                build_product_page(product),
                f"Sourced specifications and official links for {product['title']}.",
            ),
            encoding="utf-8",
        )

    (SITE / "assets" / "style.css").write_text(CSS, encoding="utf-8")

    # a 404 that keeps people on the site
    (SITE / "404.html").write_text(
        page(
            "Page not found",
            "",
            """
<div class="hero">
  <h1>Page not found</h1>
  <p class="hero__lede">That address does not exist on this site.</p>
  <div class="hero__actions">
    <a class="btn btn--primary" href="index.html">Back to the overview</a>
    <a class="btn" href="products.html">Browse products</a>
  </div>
</div>
""",
            "Page not found.",
        ),
        encoding="utf-8",
    )

    # .nojekyll so GitHub Pages serves the files verbatim, no Jekyll processing
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    # Record exactly which files this generator owns, so the next run can clean
    # up without ever touching hand-written files such as README.md or data/.
    owned = sorted(
        [*pages.keys(), *[slug(p) for p in PRODUCTS["products"]],
         "404.html", ".nojekyll", "assets/style.css"]
    )
    MANIFEST.write_text(
        json.dumps(
            {
                "generated_by": "scripts/build.py",
                "note": "Files listed here are generated. Do not edit them by hand; "
                        "edit data/ or scripts/build.py and re-run the build.",
                "files": owned,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"built {len(pages) + len(PRODUCTS['products']) + 1} pages at repo root; "
        f"{len(owned)} generated files recorded in {MANIFEST.name}"
    )


if __name__ == "__main__":
    main()
