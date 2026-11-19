#!/usr/bin/env python3
"""Build the shop section (T66, session arena/75efdf57-zone2, 2026-11-19).

    python3 tools/build_shop.py           # write shop/**.html
    python3 tools/build_shop.py --check   # exit 1 if any committed page differs from a fresh build

Inputs (all hand-verified, every value tied to an official source id):
    shop/data/catalog.json   five products, their sourced spec rows and link-intent records
    shop/data/guides.json    six question-shaped guides written with tokens (below)
    shop/data/briefing.json  owner briefing: summary, suggestions, open questions, design inputs

Outputs:
    shop/index.html, shop/air-fryers.html, shop/meat-thermometers.html, shop/compare.html,
    shop/<product-slug>.html (x5), shop/guides/index.html, shop/guides/<slug>.html (x6),
    shop/briefing.html

Guide tokens - resolved here, and the build FAILS on any token it cannot resolve:
    {{v:P-xx:Attr}}  the verified value of row `Attr` of product P-xx, followed by its source links.
                     A blank or conflicting row is refused: guides may only quote settled values.
    {{p:P-xx}}       a link to the product's page, labelled with its short name.
    {{s:ID}}         a citation link to source ID.
    {{buy:P-xx}}     the product's tagged price button.

Invariants (checked again, independently, by tools/validate_shop.py):
    * product buttons are built only by link_builder.build_product_link with the owner's tag and
      carry rel="sponsored nofollow", "(paid link)" and data-link-state/data-product-key, so
      assets/js/events.js counts them (EV-02);
    * citation links are never tagged; amazon.com citations still carry sponsored+nofollow
      (house rule G4);
    * no price, rating, review count or performance number is printed;
    * the disclosure strip precedes every table.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import head_meta  # noqa: E402
from link_builder import ASSOCIATES_TAG, build_product_link  # noqa: E402
from shop_layout import DISCLOSURE, e, footer, masthead  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "shop" / "data"
SITE = "Counter Notes"
PAID = "(paid link)"
BUY_TEXT = "Check today\u2019s price"

IMAGES = {
    "hero": "Overhead view of a kitchen counter with air-fried fries, sliced steak and roasted vegetables (illustrative food photograph, not a product photo)",
    "airfryer": "Crisp chicken wings and thick-cut fries on parchment paper (illustrative food photograph, not a product photo)",
    "thermometer": "A sliced medium-rare steak resting on a wooden board (illustrative food photograph, not a product photo)",
    "counter": "An empty oak kitchen counter with a tape measure laid across it (illustrative photograph)",
}

COMPARE = {
    "air-fryers": [
        ("Capacity", {"P-01": "Capacity", "P-03": "Capacity", "P-02": "Capacity"}),
        ("Temperature", {"P-01": "Temperature range", "P-03": "Maximum temperature"}),
        ("Dimensions", {"P-01": "Dimensions", "P-03": "Dimensions", "P-02": "Dimensions"}),
        ("Weight", {"P-01": "Weight", "P-03": "Weight"}),
        ("Power", {"P-01": "Power", "P-03": "Power", "P-02": "Wattage"}),
        ("Presets and functions", {"P-03": "Presets", "P-02": "Cooking functions"}),
        ("Cleanup", {"P-01": "Baskets", "P-03": "Basket"}),
        ("Warranty", {"P-01": "Certification and warranty", "P-03": "Certification and warranty", "P-02": "Warranty"}),
    ],
    "meat-thermometers": [
        ("How it reads", {"P-04": "Reading speed", "P-05": "Probes"}),
        ("Accuracy", {"P-04": "Accuracy", "P-05": "Accuracy"}),
        ("Connectivity", {"P-05": "Connectivity"}),
        ("Power", {"P-04": "In the box", "P-05": "Battery"}),
        ("Heat limit", {"P-04": "Maximum temperature", "P-05": "Heat safety"}),
        ("Cleaning", {"P-04": "Water resistance", "P-05": "Cleaning"}),
        ("Warranty", {"P-05": "Warranty"}),
    ],
}
NOT_TRANSCRIBED = "No comparable value was transcribed for this product from its official pages on {d}."


class BuildError(RuntimeError):
    pass


# --------------------------------------------------------------------------- #
# data
# --------------------------------------------------------------------------- #
def load() -> tuple[dict, dict, dict]:
    cat = json.loads((DATA / "catalog.json").read_text(encoding="utf-8"))
    gd = json.loads((DATA / "guides.json").read_text(encoding="utf-8"))
    br = json.loads((DATA / "briefing.json").read_text(encoding="utf-8"))
    return cat, gd, br


def products_by_id(cat: dict) -> dict[str, dict]:
    return {p["id"]: p for p in cat["products"]}


def row(p: dict, attr: str) -> dict:
    for r in p["rows"]:
        if r["attr"] == attr:
            return r
    raise BuildError(f"{p['id']}: no row named {attr!r}")


# --------------------------------------------------------------------------- #
# components
# --------------------------------------------------------------------------- #
def src_link(cat: dict, sid: str, *, short: bool = True) -> str:
    s = cat["sources"].get(sid)
    if not s:
        raise BuildError(f"unknown source id {sid}")
    url = s["url"]
    if "tag=" in url:
        raise BuildError(f"source {sid} carries an Associates tag - citations stay untagged")
    amazon = re.match(r"https?://(www\.)?amazon\.com", url) is not None
    rel = "sponsored nofollow noopener noreferrer" if amazon else "noopener noreferrer"
    text = s["host"] if short else s["label"]
    return (f'<a class="pb-src" href="{e(url)}" target="_blank" rel="{rel}" '
            f'title="{e(s["label"])}">{e(text)}</a>')


def src_links(cat: dict, ids: list[str]) -> str:
    return " ".join(src_link(cat, s) for s in ids)


def buy(p: dict, *, big: bool = False) -> str:
    link = build_product_link(p["asin"], ASSOCIATES_TAG, link_text=BUY_TEXT)
    if "tag=" + ASSOCIATES_TAG not in link.href or "sponsored" not in link.rel:
        raise BuildError(f"{p['id']}: link builder returned a non-compliant link")
    cls = "sh-buy pb-bench-cta" + (" sh-buy--big" if big else "")
    return (f'<a class="{cls}" href="{e(link.href)}" target="_blank" '
            f'rel="{e(link.rel)} noopener noreferrer" data-link-state="TAGGED" '
            f'data-product-key="{e(p["id"])}">{e(BUY_TEXT)} <span class="sh-paid">{PAID}</span></a>')


def picture(depth: str, name: str, *, cls: str = "", eager: bool = False, alt: str | None = None) -> str:
    base = f"{depth}assets/img/shop/{name}"
    loading = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture class="{e(cls)}"><img src="{e(base)}.jpg" '
            f'srcset="{e(base)}-800.jpg 800w, {e(base)}.jpg 1376w" sizes="(max-width: 860px) 100vw, 860px" '
            f'width="1376" height="768" alt="{e(alt or IMAGES[name])}" {loading} decoding="async"></picture>')


def value_cell(cat: dict, r: dict) -> tuple[str, str]:
    """(value html, source html) for one spec row."""
    if r["status"] == "blank":
        return ('<span class="pb-blank">&mdash; <small>' + e(r.get("blank_reason") or "Not stated") + "</small></span>", "")
    v = e(r["value"])
    if r["status"] == "conflict":
        v = '<span class="sh-conflict">Sources disagree</span> ' + e(re.sub(r"^CONFLICT - ", "", r["value"]))
    note = f'<small class="sh-note">{e(r["note"])}</small>' if r.get("note") else ""
    return (v + note, src_links(cat, r["src"]))


def spec_table(cat: dict, p: dict) -> str:
    trs = []
    for r in p["rows"]:
        v, s = value_cell(cat, r)
        s = s or '<span class="pb-blank"><small>No source states it</small></span>'
        trs.append(f'<tr><td class="k">{e(r["attr"])}</td><td>{v}</td><td class="sh-srccol">{s}</td></tr>')
    return (f'<div class="pb-table-scroll"><table class="pb-table sh-specs">'
            f'<caption>Specifications as published by the manufacturer or on the Amazon listing, re-read '
            f'{e(cat["checked_on"])}. Every row links to the page it came from.</caption>'
            f'<thead><tr><th scope="col">Specification</th><th scope="col">As published</th>'
            f'<th scope="col">Source</th></tr></thead><tbody>{"".join(trs)}</tbody></table></div>')


def compare_table(cat: dict, slug: str, depth: str) -> str:
    byid = products_by_id(cat)
    c = next(x for x in cat["categories"] if x["slug"] == slug)
    ps = [byid[i] for i in c["products"]]
    head = "".join(f'<th scope="col"><a href="{e(depth)}shop/{e(p["slug"])}.html">{e(p["short"])}</a></th>' for p in ps)
    trs = []
    for label, m in COMPARE[slug]:
        cells = []
        for p in ps:
            if p["id"] not in m:
                cells.append('<td><span class="pb-blank">&mdash; <small>'
                             + e(NOT_TRANSCRIBED.format(d=cat["checked_on"])) + "</small></span></td>")
                continue
            r = row(p, m[p["id"]])
            v, s = value_cell(cat, r)
            if r["status"] != "blank":
                v = re.sub(r'<small class="sh-note">.*?</small>', "", v)
            cells.append(f'<td>{v}{" " + s if s else ""}</td>')
        trs.append(f'<tr><td class="k">{e(label)}</td>{"".join(cells)}</tr>')
    return (f'<div class="pb-table-scroll"><table class="pb-table sh-compare">'
            f'<caption>{e(c["name"])} side by side. Each cell links to its official source; a dash means no '
            f'official value was recorded, with the reason.</caption>'
            f'<thead><tr><th scope="col">&nbsp;</th>{head}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>')


def card(cat: dict, p: dict, depth: str) -> str:
    facts = []
    for lab, val, attr in p["key_facts"]:
        r = row(p, attr)
        if r["status"] != "verified":
            raise BuildError(f"{p['id']}: key fact {lab!r} maps to a {r['status']} row")
        facts.append(f'<li><span>{e(lab)}</span><b>{e(val)}</b>{src_links(cat, r["src"][:1])}</li>')
    cat_name = next(c["name"] for c in cat["categories"] if c["slug"] == p["category"])
    return f"""<article class="sh-card" id="{e(p['id'])}">
  <p class="sh-badge">{e(p['badge'])}</p>
  <p class="sh-brand">{e(p['brand'])} &middot; {e(cat_name)}</p>
  <h3><a href="{e(depth)}shop/{e(p['slug'])}.html">{e(p['short'])}</a></h3>
  <p class="sh-head">{e(p['headline'])}</p>
  <ul class="sh-facts">{''.join(facts)}</ul>
  <div class="sh-card-ft">{buy(p)}<a class="sh-more-link" href="{e(depth)}shop/{e(p['slug'])}.html">Full specs and who it suits &rarr;</a></div>
</article>"""


def guide_teaser(g: dict, depth: str) -> str:
    return (f'<li><a href="{e(depth)}shop/guides/{e(g["slug"])}.html"><span class="sh-kick">{e(g["short"])}</span>'
            f'<b>{e(g["title"])}</b><span>{e(g["dek"])}</span></a></li>')


def page(rel: str, *, title: str, description: str, active: str, body: str,
         page_type: str = "article", jsonld: dict | None = None) -> str:
    depth = "../" * rel.count("/")
    head = head_meta.head_block(rel, title=title, description=description, site_name=SITE, page_type=page_type)
    ld = (f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>\n'
          if jsonld else "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
{head}
<link rel="stylesheet" href="{depth}assets/css/style.css">
<link rel="stylesheet" href="{depth}assets/css/publish.css">
<link rel="stylesheet" href="{depth}assets/css/shop.css">
<link rel="icon" href="{depth}assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Counter Notes" href="{depth}marketing/feed.xml">
{ld}</head>
<body class="sh">
<a class="skip-link" href="#main">Skip to content</a>
{masthead(depth, active, CHECKED_ON)}
<main id="main">
{body}
</main>
{footer(depth, CHECKED_ON)}
<script src="{depth}assets/js/events.js" defer></script>
</body>
</html>
"""


CHECKED_ON = "2026-11-19"


# --------------------------------------------------------------------------- #
# guides: token resolution
# --------------------------------------------------------------------------- #
TOKEN = re.compile(r"\{\{(v|p|s|buy):([^}]+)\}\}")


def resolve(cat: dict, text: str, where: str) -> str:
    byid = products_by_id(cat)

    def sub(m: re.Match) -> str:
        kind, arg = m.group(1), m.group(2)
        if kind == "s":
            return src_link(cat, arg)
        if kind in ("p", "buy"):
            if arg not in byid:
                raise BuildError(f"{where}: unknown product {arg}")
            p = byid[arg]
            return (f'<a href="../{e(p["slug"])}.html">{e(p["short"])}</a>' if kind == "p" else buy(p))
        pid, _, attr = arg.partition(":")
        if pid not in byid:
            raise BuildError(f"{where}: unknown product {pid}")
        r = row(byid[pid], attr)
        if r["status"] != "verified":
            raise BuildError(f"{where}: guide quotes {pid}:{attr}, which is {r['status']} - guides quote settled values only")
        return f'{e(r["value"])} <span class="sh-cite">{src_links(cat, r["src"])}</span>'

    out = TOKEN.sub(sub, text)
    if "{{" in out:
        raise BuildError(f"{where}: unresolved token near {out[out.index('{{'):][:40]!r}")
    return out


# --------------------------------------------------------------------------- #
# pages
# --------------------------------------------------------------------------- #
def how_we_pick(depth: str) -> str:
    return f"""<section class="sh-band sh-how">
  <div class="sh-wrap">
    <h2>How we pick and what we promise</h2>
    <ol class="sh-how-list">
      <li><b>Sourced, not tasted.</b> We have not cooked with these products. Every figure links to the manufacturer&rsquo;s page or the Amazon listing it came from, re-read {CHECKED_ON}.</li>
      <li><b>Disagreements stay visible.</b> When two official pages print different numbers we show both. When no page states a value, the cell stays empty and says why.</li>
      <li><b>No prices, no stars.</b> They change daily and live on the listing. Our buttons take you there, and we may earn a commission when you buy.</li>
    </ol>
    <p><a href="{depth}shop/briefing.html">Read the owner briefing</a> &middot; <a href="{depth}flagged.html">See everything flagged for review</a></p>
  </div>
</section>"""


def build_shop_index(cat: dict, gd: dict) -> str:
    rel, d = "shop/index.html", "../"
    byid = products_by_id(cat)
    order = [i for c in cat["categories"] for i in c["products"]]
    cats = "".join(
        f'<a class="sh-tile" href="{c["slug"]}.html">{picture(d, c["image"], alt=c["image_alt"])}'
        f'<span class="sh-kick">{e(c["kicker"])}</span><b>{e(c["name"])}</b><span>{e(c["dek"])}</span></a>'
        for c in cat["categories"])
    body = f"""<section class="sh-hero">
  <div class="sh-wrap sh-hero-grid">
    <div>
      <p class="sh-kick">The shop</p>
      <h1>Five pieces of kitchen gear, explained before you buy</h1>
      <p class="sh-dek">Three air fryers and two meat thermometers. For each one: who it suits, who should skip it, and every specification linked to the page that published it.</p>
      <p><a class="sh-btn" href="compare.html">Compare them side by side</a></p>
    </div>
    {picture(d, "hero", cls="sh-hero-img", eager=True)}
  </div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">All five products</h2>
  <div class="sh-grid">{''.join(card(cat, byid[i], d) for i in order)}</div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Shop by category</h2>
  <div class="sh-tiles">{cats}</div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Buying guides</h2>
  <ul class="sh-guides">{''.join(guide_teaser(g, d) for g in gd['guides'])}</ul>
</section>
{how_we_pick(d)}"""
    return page(rel, title="Shop: air fryers and meat thermometers | Counter Notes",
                description="Three air fryers and two meat thermometers, each with who it suits and every specification linked to its official source.",
                active="shop/index.html", body=body, page_type="website")


def build_category(cat: dict, gd: dict, c: dict) -> str:
    rel, d = f"shop/{c['slug']}.html", "../"
    byid = products_by_id(cat)
    guides = [g for g in gd["guides"] if g["category"] == c["slug"]]
    body = f"""<section class="sh-hero sh-hero--cat">
  <div class="sh-wrap sh-hero-grid">
    <div>
      <p class="sh-crumb"><a href="index.html">Shop</a> / {e(c['name'])}</p>
      <p class="sh-kick">{e(c['kicker'])}</p>
      <h1>{e(c['name'])}</h1>
      <p class="sh-dek">{e(c['dek'])}</p>
    </div>
    {picture(d, c['image'], cls="sh-hero-img", eager=True, alt=c['image_alt'])}
  </div>
</section>
<section class="sh-wrap">
  <div class="sh-grid">{''.join(card(cat, byid[i], d) for i in c['products'])}</div>
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Side by side</h2>
  {compare_table(cat, c['slug'], d)}
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Guides for this category</h2>
  <ul class="sh-guides">{''.join(guide_teaser(g, d) for g in guides)}</ul>
</section>
{how_we_pick(d)}"""
    return page(rel, title=f"{c['name']}: compared before you buy | Counter Notes",
                description=c["dek"][:155], active=rel, body=body)


def build_compare(cat: dict) -> str:
    rel, d = "shop/compare.html", "../"
    blocks = "".join(
        f'<section class="sh-wrap"><h2 class="sh-h2"><a href="{c["slug"]}.html">{e(c["name"])}</a></h2>'
        f'{compare_table(cat, c["slug"], d)}</section>' for c in cat["categories"])
    body = f"""<section class="sh-wrap sh-intro">
  <p class="sh-crumb"><a href="index.html">Shop</a> / Compare</p>
  <h1>Compare side by side</h1>
  <p class="sh-dek">The figures that decide a purchase, in one place. Every cell links to its source. A dash means no official value was recorded for that product, and the cell says why.</p>
</section>
{blocks}"""
    return page(rel, title="Compare air fryers and meat thermometers side by side | Counter Notes",
                description="Capacity, size, power, accuracy and warranty for five kitchen products, each figure linked to its official source.",
                active=rel, body=body)


def intent_block(cat: dict, p: dict) -> str:
    it = p["intent"]
    sl = cat["sources"][it["submitted_link"]]
    rows = [
        ("Link you supplied", f'<code>{e(sl["url"])}</code>', src_link(cat, it["submitted_link"])),
        ("Where it led on " + e(it["observed_on"]), f'<code>{e(it["observed_redirect_target"])}</code>',
         src_link(cat, p["listing_title_source"])),
    ]
    for lab, key in (("Intended ASIN", "intended_asin"), ("Intended official listing", "intended_listing_url"),
                     ("Confirmed on", "confirmation_date"), ("Confirmed by", "intent_source")):
        val = it.get(key) or ""
        rows.append((lab, e(val) if val else f'<span class="pb-blank">&mdash; <small>{e(it["why_blank"])}</small></span>' if key == "intended_asin" else '<span class="pb-blank">&mdash; <small>Awaiting owner confirmation.</small></span>', ""))
    trs = "".join(f'<tr><td class="k">{l}</td><td>{v}</td><td class="sh-srccol">{s}</td></tr>' for l, v, s in rows)
    return (f'<details class="sh-intent"><summary>Link record: what you supplied, where it led, what is confirmed</summary>'
            f'<p>The observed destination and the intended product are kept apart and never merged. '
            f'This page describes the observed destination.</p>'
            f'<div class="pb-table-scroll"><table class="pb-table"><thead><tr><th scope="col">Field</th>'
            f'<th scope="col">Value</th><th scope="col">Source</th></tr></thead><tbody>{trs}</tbody></table></div></details>')


def build_product(cat: dict, gd: dict, p: dict) -> str:
    rel, d = f"shop/{p['slug']}.html", "../"
    c = next(x for x in cat["categories"] if x["slug"] == p["category"])
    guides = [g for g in gd["guides"] if p["id"] in g["products"]]
    siblings = [x for x in cat["products"] if x["category"] == p["category"] and x["id"] != p["id"]]
    facts = "".join(
        f'<li><span>{e(lab)}</span><b>{e(val)}</b>{src_links(cat, row(p, attr)["src"][:1])}</li>'
        for lab, val, attr in p["key_facts"])
    ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Shop", "item": head_meta.url_for("shop/index.html")},
        {"@type": "ListItem", "position": 2, "name": c["name"], "item": head_meta.url_for(f"shop/{c['slug']}.html")},
        {"@type": "ListItem", "position": 3, "name": p["short"], "item": head_meta.url_for(rel)}]}
    body = f"""<article class="sh-product">
<section class="sh-wrap sh-product-hd">
  <p class="sh-crumb"><a href="index.html">Shop</a> / <a href="{e(c['slug'])}.html">{e(c['name'])}</a> / {e(p['short'])}</p>
  <div class="sh-product-grid">
    <div>
      <p class="sh-badge">{e(p['badge'])}</p>
      <h1>{e(p['name'])}</h1>
      <p class="sh-head sh-head--big">{e(p['headline'])}</p>
      <p class="sh-dek">{e(p['dek'])}</p>
      <div class="sh-cta-row">{buy(p, big=True)}</div>
      <p class="sh-small">Opens the Amazon listing this product&rsquo;s supplied link leads to (ASIN <code>{e(p['asin'])}</code>). Price and availability are shown there, not here.</p>
    </div>
    <aside class="sh-keybox"><h2>At a glance</h2><ul class="sh-facts">{facts}</ul></aside>
  </div>
</section>
<section class="sh-wrap sh-fit">
  <div><h2>A good fit if&hellip;</h2><ul class="sh-ticks">{''.join(f'<li>{e(x)}</li>' for x in p['good_fit'])}</ul></div>
  <div><h2>Think twice if&hellip;</h2><ul class="sh-crosses">{''.join(f'<li>{e(x)}</li>' for x in p['think_twice'])}</ul></div>
</section>
<section class="sh-wrap">
  <p class="sh-caveat"><b>Where these specs come from.</b> {e(p['caveat'])}</p>
  <h2 class="sh-h2">Full specifications</h2>
  {spec_table(cat, p)}
</section>
<section class="sh-wrap">
  <h2 class="sh-h2">Read before you decide</h2>
  <ul class="sh-guides">{''.join(guide_teaser(g, d) for g in guides)}</ul>
  <h2 class="sh-h2">Also in {e(c['name'].lower())}</h2>
  <ul class="sh-also">{''.join(f'<li><a href="{e(x["slug"])}.html"><b>{e(x["short"])}</b> &mdash; {e(x["badge"])}</a></li>' for x in siblings)}</ul>
</section>
<section class="sh-wrap">
  {intent_block(cat, p)}
</section>
</article>"""
    return page(rel, title=f"{p['short']}: specs, who it suits | Counter Notes",
                description=p["dek"][:155], active=f"shop/{c['slug']}.html", body=body, jsonld=ld)


def build_guides_index(gd: dict) -> str:
    rel, d = "shop/guides/index.html", "../../"
    body = f"""<section class="sh-wrap sh-intro">
  <p class="sh-crumb"><a href="../index.html">Shop</a> / Guides</p>
  <h1>Buying guides</h1>
  <p class="sh-dek">One buyer question per guide, answered with figures you can check. The titles are the questions we expect buyers to ask; they are working titles, not measured search demand.</p>
</section>
<section class="sh-wrap"><ul class="sh-guides sh-guides--wide">{''.join(guide_teaser(g, d) for g in gd['guides'])}</ul></section>
<section class="sh-wrap"><p class="sh-small">Earlier pieces live in the <a href="{d}guides/index.html">guide archive</a>.</p></section>"""
    return page(rel, title="Buying guides: air fryers and meat thermometers | Counter Notes",
                description="Question-shaped buying guides for air fryers and meat thermometers. Every figure links to its official source.",
                active=rel, body=body)


def build_guide(cat: dict, gd: dict, g: dict) -> str:
    rel, d = f"shop/guides/{g['slug']}.html", "../../"
    where = f"guide {g['slug']}"
    byid = products_by_id(cat)
    secs = "".join(f'<section><h2>{e(s["h"])}</h2>{resolve(cat, s["html"], where)}</section>' for s in g["sections"])
    faq = "".join(f'<details class="sh-faq"><summary>{e(q)}</summary><p>{resolve(cat, a, where)}</p></details>' for q, a in g["faq"])
    picks = "".join(card(cat, byid[i], d) for i in g["products"])
    others = [x for x in gd["guides"] if x["slug"] != g["slug"]][:3]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"],
          "datePublished": gd["published"], "dateModified": gd["published"],
          "author": {"@type": "Organization", "name": gd["author"]},
          "publisher": {"@type": "Organization", "name": SITE},
          "image": head_meta.url_for(f"assets/img/shop/{g['image']}.jpg"),
          "mainEntityOfPage": head_meta.url_for(rel)}
    body = f"""<article class="sh-guide">
<header class="sh-wrap sh-guide-hd">
  <p class="sh-crumb"><a href="../index.html">Shop</a> / <a href="index.html">Guides</a></p>
  <p class="sh-kick">{e(g['short'])}</p>
  <h1>{e(g['title'])}</h1>
  <p class="sh-dek">{e(g['dek'])}</p>
  <p class="sh-byline">By {e(gd['author'])} &middot; <time datetime="{e(gd['published'])}">{e(gd['published'])}</time> &middot; Figures re-read from official pages that day. We have not tested these products hands-on.</p>
  {picture(d, g['image'], cls="sh-guide-img", eager=True)}
</header>
<div class="sh-wrap sh-prose">{secs}</div>
<section class="sh-wrap"><h2 class="sh-h2">Questions buyers ask</h2>{faq}</section>
<section class="sh-wrap"><h2 class="sh-h2">The products in this guide</h2><div class="sh-grid">{picks}</div></section>
<section class="sh-wrap"><h2 class="sh-h2">Keep reading</h2><ul class="sh-guides">{''.join(guide_teaser(x, d) for x in others)}</ul></section>
</article>"""
    return page(rel, title=f"{g['title']} | Counter Notes", description=g["dek"][:155],
                active="shop/guides/index.html", body=body, jsonld=ld)


def build_briefing(cat: dict, br: dict) -> str:
    rel, d = "shop/briefing.html", "../"
    qids = {q["id"] for q in br["questions"]}
    sids = {s["id"] for s in br["suggestions"]}

    def cites(ids: list[str] | None) -> str:
        return (' <span class="sh-cite">' + src_links(cat, ids) + "</span>") if ids else ""

    summ = "".join(f'<li><b>{e(x["h"])}.</b> {e(x["t"])}{cites(x.get("src"))}</li>' for x in br["summary"])
    sug = []
    for s in br["suggestions"]:
        for w in s["waits_on"]:
            if w not in qids:
                raise BuildError(f"{s['id']} waits on unknown question {w}")
        if s["recommendation"] not in {o["label"] for o in s["options"]}:
            raise BuildError(f"{s['id']}: recommendation is not one of its options")
        opts = "".join(
            f'<div class="pb-opt{" pb-opt--rec" if o["label"] == s["recommendation"] else ""}"><b>Option {e(o["label"])}'
            f'{" &nbsp;(recommended)" if o["label"] == s["recommendation"] else ""}</b><p>{e(o["text"])}</p>'
            f'<div class="cost"><b>Cost</b> {e(o["cost"])}<br><b>Trade-off</b> {e(o["tradeoff"])}</div></div>'
            for o in s["options"])
        waits = ", ".join(f'<a href="#{e(w)}">{e(w)}</a>' for w in s["waits_on"]) or "nothing &mdash; can be decided now"
        sug.append(f"""<article class="pb-decision" id="{e(s['id'])}">
  <div class="pb-decision-hd"><span class="pb-decision-id">{e(s['id'])}</span><h3>{e(s['title'])}</h3><span class="pb-pill pb-pill--warn">{e(s['status'])}</span></div>
  <p><b>{e(s['area'])}.</b> {e(s['why'])}{cites(s.get('src'))}</p>
  <div class="pb-opts">{opts}</div>
  <div class="pb-decision-ft"><span><b>Recommended</b> Option {e(s['recommendation'])}</span><span><b>Effort</b> {e(s['effort'])}</span><span><b>Waits on</b> {waits}</span><span><b>Implemented</b> No</span></div>
</article>""")
    qs = []
    for q in br["questions"]:
        for b in q["blocks"]:
            if b not in sids:
                raise BuildError(f"{q['id']} blocks unknown suggestion {b}")
        blocks = ", ".join(f'<a href="#{e(b)}">{e(b)}</a>' for b in q["blocks"]) or "no suggestion"
        qs.append(f"""<article class="pb-decision" id="{e(q['id'])}">
  <div class="pb-decision-hd"><span class="pb-decision-id">{e(q['id'])}</span><h3>{e(q['q'])}</h3><span class="pb-pill pb-pill--flag">Open</span></div>
  <p><b>Why it matters.</b> {e(q['why'])}</p>
  <p><b>What we know.</b> {e(q['known'])}{cites(q.get('known_src'))}</p>
  <p><b>What is missing.</b> {e(q['missing'])}</p>
  <p><b>How to find out.</b> {e(q['how'])}</p>
  <div class="pb-decision-ft"><span><b>Who</b> {e(q['who'])}</span><span><b>Blocks</b> {blocks}</span></div>
</article>""")
    dp = "".join(f'<tr><td class="k">{e(k)}</td><td>{e(v)}</td><td class="sh-srccol"><span class="pb-blank"><small>Editorial input, not a factual claim</small></span></td></tr>' for k, v in br["design_prompt"]["items"])
    toc = ('<nav class="sh-toc" aria-label="On this page"><a href="#summary">Executive summary</a>'
           '<a href="#suggestions">Suggestions to choose from</a><a href="#questions">Open questions</a>'
           '<a href="#design">Inputs for the next design prompt</a></nav>')
    body = f"""<section class="sh-wrap sh-intro">
  <p class="sh-crumb"><a href="index.html">Shop</a> / Owner briefing</p>
  <p class="sh-kick">Behind the scenes &middot; {e(br['as_of'])}</p>
  <h1>Owner briefing</h1>
  <p class="sh-dek">What changed, what to decide next, and what nobody knows yet. Nothing below has been applied: each suggestion waits for your choice, and each open question says how the answer can be found.</p>
  {toc}
</section>
<section class="sh-wrap" id="summary"><h2 class="sh-h2">Executive summary</h2><ul class="sh-summary">{summ}</ul></section>
<section class="sh-wrap" id="suggestions"><h2 class="sh-h2">Suggestions to choose from</h2><p class="sh-small">Each has options with cost and trade-off, a recommendation, and the questions it waits on. Earlier sessions' boards remain at <a href="{d}suggestions.html">the suggestion board</a> and <a href="{d}questions.html">open questions</a>.</p>{''.join(sug)}</section>
<section class="sh-wrap" id="questions"><h2 class="sh-h2">Open questions, and how to answer them</h2>{''.join(qs)}</section>
<section class="sh-wrap" id="design"><h2 class="sh-h2">Inputs for the next design prompt</h2><p>{e(br['design_prompt']['intro'])}</p>
<div class="pb-table-scroll"><table class="pb-table"><thead><tr><th scope="col">Topic</th><th scope="col">Input</th><th scope="col">Status</th></tr></thead><tbody>{dp}</tbody></table></div></section>"""
    return page(rel, title="Owner briefing: summary, suggestions, open questions | Counter Notes",
                description="Executive summary, suggestions with options to choose from, and open questions with how to answer each one.",
                active="", body=body)


def build_all() -> dict[str, str]:
    cat, gd, br = load()
    out: dict[str, str] = {"shop/index.html": build_shop_index(cat, gd),
                           "shop/compare.html": build_compare(cat),
                           "shop/guides/index.html": build_guides_index(gd),
                           "shop/briefing.html": build_briefing(cat, br)}
    for c in cat["categories"]:
        out[f"shop/{c['slug']}.html"] = build_category(cat, gd, c)
    for p in cat["products"]:
        out[f"shop/{p['slug']}.html"] = build_product(cat, gd, p)
    for g in gd["guides"]:
        out[f"shop/guides/{g['slug']}.html"] = build_guide(cat, gd, g)
    for rel, h in out.items():
        if DISCLOSURE not in h:
            raise BuildError(f"{rel}: disclosure missing")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    try:
        out = build_all()
    except BuildError as exc:
        print(f"SHOP BUILD FAILED: {exc}")
        return 1
    if a.check:
        stale = [r for r, h in out.items() if not (ROOT / r).is_file() or (ROOT / r).read_text(encoding="utf-8") != h]
        if stale:
            print("SHOP BUILD STALE - committed pages differ from a fresh build: " + ", ".join(stale))
            return 1
        print(f"shop build current: {len(out)} pages")
        return 0
    for rel, h in out.items():
        f = ROOT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(h, encoding="utf-8")
    print(f"shop build wrote {len(out)} pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
