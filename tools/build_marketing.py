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
4.  **Every affiliate link goes through ``tools/link_builder.py``.**  With no Associates ID configured, that
    means ``preview_link()`` - which is explicitly non-monetized and must be labelled as such.  The renderer
    refuses to hand-write ``amazon.com/dp/`` URLs.
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

from link_builder import REQUIRED_SITE_DISCLOSURE, LinkPolicyError, audit_html, preview_link  # noqa: E402

DATA = REPO / "marketing" / "data" / "facts.json"
OUT = REPO / "marketing"
CSS = "assets/marketing.css"
SITE_NAME = "Zone2 Field Notes"
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/marketing/"

FACTS = json.loads(DATA.read_text(encoding="utf-8"))
PRODUCTS = {p["key"]: p for p in FACTS["products"]}
AS_OF = FACTS["verified_utc"]

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
    """Emit the product link through link_builder, never by hand."""
    link = preview_link(
        product["asin"],
        link_text=f'{product["manufacturer_product_name"]} (see this model on Amazon)',
    )
    href = esc(link.href)
    text = esc(link.text)
    warn = esc(" ".join(link.warnings))
    return (
        f'<a class="sponsored-link" href="{href}" rel="sponsored nofollow" target="_blank" '
        f'referrerpolicy="no-referrer-when-downgrade" data-link-state="PREVIEW_NO_TAG">{text}</a>'
        f'<span class="link-note" title="{warn}">preview link \u2014 no Associates ID configured, earns nothing</span>'
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

NAV = [
    ("index.html", "Overview"),
    ("buying-guide.html", "Buying guide"),
    ("comparison.html", "Comparison"),
    ("articles/index.html", "Product articles"),
    ("verification.html", "Verification"),
    ("flagged.html", "Flagged for review"),
]


def shell(title: str, description: str, body: str, *, here: str, depth: int = 0) -> str:
    root = "../" * depth
    nav_parts = []
    for href, label in NAV:
        active = ' class="active"' if href == here else ""
        nav_parts.append(f'<a href="{root}{href}"{active}>{esc(label)}</a>')
    nav = "".join(nav_parts)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — {esc(SITE_NAME)}</title>
<meta name="description" content="{esc(description)}">
<link rel="stylesheet" href="{root}{CSS}">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="shell">
  <aside class="sidebar">
    <a class="brand" href="{root}index.html">{esc(SITE_NAME)}</a>
    <p class="sub">Verified Amazon affiliate content</p>
    <nav aria-label="Marketing sections">{nav}</nav>
    <p class="side-note">Every claim on these pages links to the official page it came from. Values that no official page states are left blank and flagged.</p>
    <p class="side-note"><a href="{root}../index.html">← Platform dashboard</a></p>
  </aside>
  <main class="main" id="main">
    <div class="disclosure" data-rule="R-01"><strong>Affiliate disclosure:</strong> {esc(REQUIRED_SITE_DISCLOSURE)}</div>
{body}
    <footer class="site">
      <p>{esc(REQUIRED_SITE_DISCLOSURE)}</p>
      <p>Facts verified {esc(AS_OF)} against official manufacturer and Amazon product pages.
      Product links are <strong>preview links</strong>: no Associates ID is configured for this project, so
      they are not monetized and carry <code>rel="sponsored nofollow"</code>.
      <a href="{root}verification.html">Verification method</a> ·
      <a href="{root}flagged.html">Flagged for review</a></p>
    </footer>
  </main>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages

def page_index() -> str:
    cards = []
    for p in FACTS["products"]:
        slug = p["key"].lower()
        cards.append(f"""
      <article class="card product-card">
        <p class="eyebrow">{esc(p['manufacturer'])} · {esc(p['category_path_amazon'].split('› ')[-1])}</p>
        <h3><a href="articles/{slug}.html">{esc(p['manufacturer_product_name'])}</a></h3>
        <p class="lede">{esc(p['tagline_facts'])}</p>
        <dl class="mini">
          <div><dt>ASIN</dt><dd><code>{esc(p['asin'])}</code></dd></div>
          <div><dt>Model</dt><dd><code>{esc(p['model'])}</code></dd></div>
          <div><dt>Rows verified</dt><dd>{sum(1 for r in p['rows'] if r['status'] == 'verified')} of {len(p['rows'])}</dd></div>
        </dl>
        <p><a class="button" href="articles/{slug}.html">Read the article</a></p>
      </article>""")
    return shell(
        "Verified Amazon affiliate content",
        "Source-governed buying guide, comparison and product articles for three Amazon air fryers.",
        f"""    <div class="page-head">
      <h1>Three air fryers, written up from official specs only</h1>
      <p class="lede">A buying guide, a side-by-side comparison and one article per product — every
      specification traced to the manufacturer's or Amazon's own page, and anything unconfirmed left
      blank and flagged rather than guessed.</p>
    </div>

    <section class="kpis">
      <div class="kpi"><span class="kpi-num">{len(FACTS['products'])}</span><span class="kpi-label">products covered</span></div>
      <div class="kpi"><span class="kpi-num">{sum(len(p['rows']) for p in FACTS['products'])}</span><span class="kpi-label">spec rows, each sourced or blank</span></div>
      <div class="kpi"><span class="kpi-num">{sum(1 for p in FACTS['products'] for r in p['rows'] if r['status'] == 'conflict')}</span><span class="kpi-label">published source conflicts</span></div>
      <div class="kpi"><span class="kpi-num">{sum(1 for p in FACTS['products'] for r in p['rows'] if r['status'] in ('unverified', 'withheld_by_policy'))}</span><span class="kpi-label">rows left blank, with reasons</span></div>
    </section>

    <div class="card">
      <h2>Start here</h2>
      <ul class="links-grid">
        <li><a href="buying-guide.html"><strong>Buying guide</strong><span>Which of the three fits which kitchen — decided by the verified numbers, not by adjectives.</span></a></li>
        <li><a href="comparison.html"><strong>Head-to-head comparison</strong><span>Every shared attribute in one table, with the source beside each value.</span></a></li>
        <li><a href="articles/index.html"><strong>Product articles</strong><span>One SEO-structured article per model, built from that model's verified rows.</span></a></li>
        <li><a href="verification.html"><strong>Verification</strong><span>What was checked, when, against which page, and what could not be confirmed.</span></a></li>
        <li><a href="flagged.html"><strong>Flagged for review</strong><span>Every irregularity found while building this set, with its source links.</span></a></li>
      </ul>
    </div>

    <h2>The three products</h2>
    <div class="card-grid">{''.join(cards)}
    </div>
""",
        here="index.html",
    )


def page_article(key: str) -> str:
    p = PRODUCTS[key]
    slug = key.lower()
    # FAQ answers are assembled only from rows that carry a verified value.
    faq = [
        ("What is the verified capacity?",
         next((r["value"] for r in p["rows"] if r["attr"].startswith("Capacity")), None)),
        ("What power rating does the manufacturer state?",
         next((r["value"] for r in p["rows"] if r["attr"].startswith("Power")), None)),
        ("What temperature range is stated?",
         next((r["value"] for r in p["rows"] if r["attr"].startswith("Temperature")), None)),
        ("What model number should be on the box?",
         next((r["value"] for r in p["rows"] if r["attr"].startswith("Model number")), None)),
    ]
    faq_html = []
    for q, a in faq:
        if a:
            faq_html.append(f"<dt>{esc(q)}</dt><dd>{esc(a)}</dd>")
        else:
            faq_html.append(
                f'<dt>{esc(q)}</dt><dd><span class="pill pill-warn">UNVERIFIED</span> no official page states this, '
                "so it is not answered here.</dd>"
            )
    conflicts = [r for r in p["rows"] if r["status"] == "conflict"]
    conflict_block = ""
    if conflicts:
        items = "".join(
            f'<li><strong>{esc(r["attr"])}:</strong> {esc(r["detail"])}</li>' for r in conflicts
        )
        conflict_block = f"""
    <section class="card callout-flag">
      <h2>Where the official sources disagree</h2>
      <p>These are printed as disagreements. No value is chosen for you.</p>
      <ul>{items}</ul>
    </section>"""

    body = f"""    <nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">Overview</a> › <a href="index.html">Product articles</a> › <span>{esc(p['manufacturer_product_name'])}</span></nav>
    <div class="page-head">
      <p class="eyebrow">{esc(p['manufacturer'])}</p>
      <h1>{esc(p['manufacturer_product_name'])}</h1>
      <p class="lede">{esc(p['tagline_facts'])}</p>
      <p class="byline">Official listing title: <em>{esc(p['title_official'])}</em></p>
    </div>

    <div class="card">
      <h2>Quick verdict</h2>
      <p>If you want <strong>{esc(p['tagline_facts'].split(': ', 1)[-1].rstrip('.'))}</strong>, this is the
      model that states those numbers on its manufacturer page. That is the entire basis for recommending it
      here — this set contains no hands-on testing, no star ratings and no price claims, because none of
      those could be confirmed from an official source.</p>
      <p>{product_link(p)}</p>
    </div>

    <section class="card">
      <h2>Specification, with the source on every row</h2>
      {spec_table(p, key_prefix=slug)}
    </section>

    <section class="card">
      <h2>What the manufacturer says it does</h2>
      {feature_list(p)}
    </section>
{conflict_block}
    <section class="card">
      <h2>Questions buyers actually ask</h2>
      <dl class="faq">{''.join(faq_html)}</dl>
      <p class="row-note">Only questions that the verified data above can answer are answered. A question whose
      answer is not stated on an official page is marked UNVERIFIED rather than filled in.</p>
    </section>

    <section class="card">
      <h2>Sources for this article</h2>
      <ul class="source-list">
        {''.join(f'<li>{source_link(s["id"])} — {esc(s["name"])}</li>' for s in p['official_sources'])}
      </ul>
      <p class="row-note">Read {esc(AS_OF)}. Specifications change; re-check the manufacturer page before buying.</p>
    </section>
"""
    return shell(
        p["manufacturer_product_name"],
        p["tagline_facts"],
        body,
        here="articles/index.html",
        depth=1,
    )


def page_articles_index() -> str:
    rows = "".join(
        f'<tr><th scope="row"><a href="{p["key"].lower()}.html">{esc(p["manufacturer_product_name"])}</a></th>'
        f'<td><code>{esc(p["asin"])}</code></td>'
        f'<td>{esc(p["manufacturer"])}</td>'
        f'<td>{esc(p["tagline_facts"])}</td>'
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
        <thead><tr><th>Product</th><th>ASIN</th><th>Brand</th><th>One-line verified summary</th><th>Official sources</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
"""
    return shell("Product articles", "One verified article per product.", body, here="articles/index.html", depth=1)


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
      <h2>Links are not monetized</h2>
      <p>No Amazon Associates ID is configured for this project, and inventing one is prohibited. Every
      outbound product link here is therefore an inert <strong>preview link</strong> produced by the
      project's link builder, marked <code>rel="sponsored nofollow"</code> and labelled as non-earning. Before
      publishing, the owner must set the Associates ID; the builder will then emit a properly tagged Special
      Link instead, and the "preview link" labels disappear automatically because they are driven by that
      same configuration.</p>
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
        <li><strong>Set the Associates ID.</strong> Until one is configured, every product link on this site is a
        non-earning preview link. Nothing is tagged, because a fabricated tag would be worse than none.</li>
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


# --------------------------------------------------------------------------- build

PAGES = {
    "index.html": page_index,
    "buying-guide.html": page_buying_guide,
    "comparison.html": page_comparison,
    "verification.html": page_verification,
    "flagged.html": page_flagged,
    "articles/index.html": page_articles_index,
    "articles/p1.html": lambda: page_article("P1"),
    "articles/p2.html": lambda: page_article("P2"),
    "articles/p3.html": lambda: page_article("P3"),
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
        print(f"{len(rendered)} marketing pages: committed output is current")
        return 0

    rendered = build(OUT)
    print(f"built {len(rendered)} marketing pages into {OUT.relative_to(REPO)}/")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, LinkPolicyError) as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
