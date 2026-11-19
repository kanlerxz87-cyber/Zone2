#!/usr/bin/env python3
"""Generate the Counter Notes thermometer desk: `marketing/thermometers/**`.

T64 (session `arena/32788da6-zone2`, 2026-11-19). Closes RQ-04: reader-facing, question-shaped guides
for the two thermometer destinations (ledger P-04 / P-05), written from one fact base,
`marketing/data/thermometers.json`, in which every value was read off an official page on the date the
file states.

WHAT THIS GENERATOR REFUSES TO PUBLISH (each one fails the build, not a warning)
    * a valued specification row with no source id, or with a source id that does not resolve;
    * a blank row without a stated reason, or a blank row that carries a value anyway;
    * a sentence (`prose` / `list` block) with no source id - opinions go in a labelled `take` box;
    * a price, a star rating, a review count or a sales rank anywhere on a page;
    * an Amazon link that is neither a tagged product Special Link (`tag=shopnow047c-20`, rel sponsored,
      link-level disclosure adjacent) nor an untagged citation (`class="src"`);
    * a link to a host outside ALLOWED_HOSTS, or an internal link that resolves to nothing;
    * a banned phrase from `marketing/data/editorial.json` `voice.banned_words`, or any wording that
      claims first-hand use ("we tested", "hands-on");
    * a page without the Associates disclosure sentence, or whose canonical URL is not its own path.

HOW IT FITS THE MARKETING BUILD
    `tools/build_marketing.py` imports `render()` from here and merges the pages into its own output, so
    `marketing/feed.xml`, `marketing/sitemap.xml`, the guides index and verify_marketing's G13/G14
    (orphans, sitemap coverage, feed targets, canonical) all see the desk. The pages are deliberately
    NOT in build_marketing's `PAGES` registry: verify_marketing's G10 host allow-list is outside this
    session's scope and does not list `www.fsis.usda.gov`, the source for every food-safety sentence
    here. This module enforces the equivalent gates itself (ALLOWED_HOSTS below) and CR-8 in
    COORDINATION.md asks the owner of verify_marketing.py to extend G10 instead.

Usage:
    python3 tools/build_thermometers.py            # write marketing/thermometers/
    python3 tools/build_thermometers.py --check    # exit 1 if committed output differs or a gate fails
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

import build_marketing as bm  # noqa: E402
from link_builder import (  # noqa: E402
    ASSOCIATES_TAG,
    REQUIRED_SITE_DISCLOSURE,
    LinkPolicyError,
    audit_html,
    build_product_link,
)

DATA = REPO / "marketing" / "data" / "thermometers.json"
OUT = REPO / "marketing"
SECTION = "thermometers"
LIVE = bm.LIVE

T = json.loads(DATA.read_text(encoding="utf-8"))
AS_OF = T["as_of"]
SOURCES = {s["id"]: s for s in T["sources"]}
PRODUCTS = {p["key"]: p for p in T["products"]}
GUIDES = T["guides"]
GUIDE_BY_SLUG = {g["slug"]: g for g in GUIDES}
TEMPS = T["temps"]

PRODUCT_SLUG = {"P4": "thermomaven-instant-read.html", "P5": "chef-iq-sense-wireless.html"}
CARD_ATTRS = {
    "P4": ["Reading time", "Accuracy", "Heat rating", "Probe reach"],
    "P5": ["Probes in this listing", "Heat rating", "Probe length", "Connectivity"],
}

#: The only external hosts a desk page may link to. A list, not a wildcard, on purpose:
#: the two Amazon hosts (product Special Links and untagged citations), USDA FSIS (every food-safety
#: statement), and Amazon's Associates help (the site-wide scope note emitted by the shared shell).
ALLOWED_HOSTS = {"www.amazon.com", "amazon.com", "www.fsis.usda.gov", "affiliate-program.amazon.com"}
MARKETPLACE_HOSTS = {"www.amazon.com", "amazon.com"}

VALUED = {"verified", "partial", "conflict"}
BLANK = {"unverified"}

MONEY = re.compile(r"[$€£]\s?\d")
RATINGS = re.compile(
    r"out of 5 stars|best sellers? rank|#\d+ in |\bcustomer reviews?\b|\bstar rating\b|\d[\d,]* ratings\b", re.I
)
FIRST_HAND = ("we tested", "our team tested", "hands-on", "we used it", "in our kitchen", "in our testing")
BANNED = [w.lower() for w in bm.VOICE["banned_words"]]


class BuildError(bm.BuildError):
    """A refusal from the desk. Subclasses build_marketing's, so its CLI reports it the same way."""


esc = bm.esc


# --------------------------------------------------------------------------- data gate


def validate_data() -> None:
    """Refuse the fact base before rendering anything from it."""
    for sid, s in SOURCES.items():
        host = s["url"].split("/")[2]
        if host not in ALLOWED_HOSTS:
            raise BuildError(f"source {sid}: host {host!r} is not on the desk allow-list")
    for key, p in PRODUCTS.items():
        if key not in PRODUCT_SLUG:
            raise BuildError(f"product {key}: no page slug registered")
        seen = set()
        for row in p["rows"]:
            attr = row["attr"]
            if attr in seen:
                raise BuildError(f"{key}: duplicate row {attr!r}")
            seen.add(attr)
            st = row.get("status")
            if st in VALUED:
                if not row.get("value"):
                    raise BuildError(f"{key} row {attr!r}: status {st} but no value")
                if row.get("src") not in SOURCES:
                    raise BuildError(f"{key} row {attr!r}: a value with no resolvable source - refusing to publish it")
            elif st in BLANK:
                if row.get("value"):
                    raise BuildError(f"{key} row {attr!r}: marked {st} but carries a value - never fill a blank")
                if not row.get("blank_reason"):
                    raise BuildError(f"{key} row {attr!r}: a blank without a stated reason")
            else:
                raise BuildError(f"{key} row {attr!r}: unknown status {st!r}")
        for item in p.get("before_you_buy", []):
            _require_srcs(item.get("src"), f"{key} before_you_buy")
    for g in GUIDES:
        for si, sec in enumerate(g["sections"], start=1):
            for bi, b in enumerate(sec["blocks"], start=1):
                where = f"{g['slug']} s{si}b{bi}"
                if b["kind"] in ("prose", "list"):
                    _require_srcs(b.get("src"), where)
                elif b["kind"] == "compare":
                    for spec in b["rows"]:
                        names = spec.split("|")
                        if not any(_row(p, names) for p in PRODUCTS.values()):
                            raise BuildError(f"{where}: compare row {spec!r} matches no product row")
                elif b["kind"] == "temps":
                    for t in b["rows"]:
                        if t not in TEMPS or TEMPS[t]["src"] not in SOURCES:
                            raise BuildError(f"{where}: temperature row {t!r} is missing or unsourced")
                elif b["kind"] != "take":
                    raise BuildError(f"{where}: unknown block kind {b['kind']!r}")
        for r in g.get("related", []):
            if r not in GUIDE_BY_SLUG:
                raise BuildError(f"{g['slug']}: related guide {r!r} does not exist")


def _require_srcs(ids, where: str) -> None:
    if not ids:
        raise BuildError(f"{where}: a statement with no source id - put opinion in a labelled take box instead")
    for sid in ids:
        if sid not in SOURCES:
            raise BuildError(f"{where}: cites {sid!r}, which is not a registered source")


def _row(product: dict, names) -> dict | None:
    for n in names:
        for r in product["rows"]:
            if r["attr"] == n:
                return r
    return None


# --------------------------------------------------------------------------- fragments


def src_link(sid: str) -> str:
    s = SOURCES[sid]
    host = s["url"].split("/")[2]
    rel = "sponsored nofollow noopener noreferrer" if host in MARKETPLACE_HOSTS else "noopener noreferrer nofollow"
    return (
        f'<a class="src" href="{esc(s["url"])}" target="_blank" rel="{rel}">'
        f'{esc(sid)} · {esc(host)}<span class="src-kind">{esc(s["label"])}</span></a>'
    )


def cite(ids) -> str:
    if not ids:
        return ""
    return '<span class="cites">' + "".join(src_link(s) for s in ids) + "</span>"


def product_cta(p: dict) -> str:
    """The tagged Special Link, emitted through link_builder exactly like the air-fryer desk."""
    link = build_product_link(p["asin"], ASSOCIATES_TAG, link_text=f'{p["name"]} (see this listing)')
    return (
        f'<a class="sponsored-link" href="{esc(link.href)}" rel="sponsored nofollow" target="_blank" '
        f'referrerpolicy="no-referrer-when-downgrade" data-link-state="TAGGED" '
        f'data-product-key="{esc(p["ledger_id"])}">{esc(link.text)}</a>'
        f'<span class="link-note">Special Link \u2014 Associates tag {esc(ASSOCIATES_TAG)}</span>'
        f'<span class="disclosure disclosure--link" data-rule="R-02">{esc(bm.FACTS["link_level_disclosure"])}</span>'
    )


def intent_note(p: dict, root: str) -> str:
    return (
        f'<p class="row-note">The link opens the listing the supplied short link <code>{esc(p["submitted_link"])}</code> '
        f"resolved to when we re-opened it on {esc(AS_OF)}. That shows where the link goes, not which product the "
        f'brief intended; intent is unconfirmed until the owner says so (<a href="{root}../pages/flags.html#F-03">flag F-03</a>).</p>'
    )


def status_pill(row: dict) -> str:
    label, cls = bm.STATUS_LABEL[row["status"]]
    return f'<span class="pill {cls}">{label}</span>'


def cell(row: dict | None) -> str:
    if row is None:
        return '<span class="dash">—</span> <span class="row-note">not stated in the listing</span>'
    if row["status"] in BLANK:
        return f'<span class="dash">—</span> <span class="row-note">{esc(row["blank_reason"])}</span>'
    return f'<strong>{esc(row["value"])}</strong>{cite([row["src"]])}'


def spec_table(p: dict) -> str:
    slug = PRODUCT_SLUG[p["key"]].replace(".html", "")
    rows = []
    for i, r in enumerate(p["rows"], start=1):
        if r["status"] in BLANK:
            value = f'<span class="dash">—</span><p class="row-note">{esc(r["blank_reason"])}</p>'
            src = esc(r.get("src_note", "—"))
        else:
            value = f'<strong>{esc(r["value"])}</strong>'
            if r.get("detail"):
                value += f'<p class="row-note">{esc(r["detail"])}</p>'
            src = src_link(r["src"])
        rows.append(
            f'<tr id="{slug}-r{i}"><th scope="row">{esc(r["attr"])}</th><td>{value}</td>'
            f"<td>{status_pill(r)}</td><td>{src}</td></tr>"
        )
    return (
        '<table class="data"><caption>Each value transcribed from the page in the last column on '
        f"{esc(AS_OF)}. A dash is a value the listing does not state; the reason sits under it.</caption>"
        "<thead><tr><th>What</th><th>As published</th><th>Status</th><th>Source</th></tr></thead>"
        f'<tbody>{"".join(rows)}</tbody></table>'
    )


def render_blocks(blocks, *, key: str, root: str) -> str:
    out = []
    for i, b in enumerate(blocks, start=1):
        bid = f"{key}-b{i}"
        kind = b["kind"]
        if kind == "prose":
            out.append(
                f'<p class="claim" id="{bid}" data-src="{esc(",".join(b["src"]))}">{esc(b["html"])}{cite(b["src"])}</p>'
            )
        elif kind == "list":
            srcs = esc(",".join(b["src"]))
            items = "".join(f'<li class="claim" data-src="{srcs}">{esc(x)}</li>' for x in b["items"])
            out.append(f'<ul class="points" id="{bid}">{items}</ul>{cite(b["src"])}')
        elif kind == "take":
            out.append(
                f'<aside class="take" id="{bid}" role="note"><p class="take-label">Our take — '
                "an editorial judgement, not a claim the manufacturer or USDA makes</p>"
                f'<p class="judgement">{esc(b["html"])}</p></aside>'
            )
        elif kind == "compare":
            heads = "".join(
                f'<th scope="col"><a href="{esc(PRODUCT_SLUG[k])}">{esc(p["short"])}</a></th>'
                for k, p in PRODUCTS.items()
            )
            trs = []
            for spec in b["rows"]:
                names = spec.split("|")
                tds = "".join(f"<td>{cell(_row(p, names))}</td>" for p in PRODUCTS.values())
                trs.append(f'<tr><th scope="row">{esc(names[0])}</th>{tds}</tr>')
            out.append(
                f'<figure class="tbl" id="{bid}"><table class="data"><thead><tr><th>Row</th>{heads}</tr></thead>'
                f'<tbody>{"".join(trs)}</tbody></table><figcaption>{esc(b["caption"])}</figcaption></figure>'
            )
        elif kind == "temps":
            trs = "".join(
                f'<tr><th scope="row">{esc(TEMPS[t]["label"])}</th><td><strong>{esc(TEMPS[t]["value"])}</strong></td>'
                f'<td>{src_link(TEMPS[t]["src"])}</td></tr>'
                for t in b["rows"]
            )
            out.append(
                f'<figure class="tbl" id="{bid}"><table class="data"><thead><tr><th>Food</th>'
                f"<th>Safe minimum internal temperature</th><th>Source</th></tr></thead><tbody>{trs}</tbody></table>"
                f'<figcaption>{esc(b["caption"])}</figcaption></figure>'
            )
    return "\n".join(out)


NOT_DONE = (
    "Nobody on this site has used either thermometer. Every specification was copied from the Amazon listing "
    "linked beside it, and every food-safety statement from a USDA Food Safety and Inspection Service page, all "
    "read on {as_of}. Where this page gives a temperature, the number and its wording are USDA's. Prices, star "
    "ratings, review counts and sales ranks appear on the listings and are deliberately not repeated here: the "
    "first is restricted by the programme's content rules, the rest change too often to be facts."
)

RAIL_NOTE = (
    "Five official pages - two Amazon listings and three USDA food-safety pages - read row by row. Where one "
    "listing contradicts itself, both statements are printed."
)


def page(title, description, body, *, rel, crumb_label) -> str:
    crumbs = [("index.html", "Home"), (f"{SECTION}/index.html", "Thermometers")]
    if rel != f"{SECTION}/index.html":
        crumbs.append((rel, crumb_label))
    return bm.shell(
        title, description, body, here=f"{SECTION}/index.html", depth=1, path=rel, crumbs=crumbs,
        read_on=AS_OF, rail_note=RAIL_NOTE,
    )


# --------------------------------------------------------------------------- pages


def page_hub() -> str:
    rows = sum(len(p["rows"]) for p in PRODUCTS.values())
    conflicts = sum(1 for p in PRODUCTS.values() for r in p["rows"] if r["status"] == "conflict")
    blanks = sum(1 for p in PRODUCTS.values() for r in p["rows"] if r["status"] in BLANK)
    cards = []
    for key, p in PRODUCTS.items():
        facts = "".join(
            f'<li><span>{esc(a)}</span> {cell(_row(p, [a]))}</li>' for a in CARD_ATTRS[key]
        )
        cards.append(
            f'<article class="pcard"><p class="eyebrow">{esc(p["brand"])} · {esc(p["kind_label"])}</p>'
            f'<h3><a href="{esc(PRODUCT_SLUG[key])}">{esc(p["headline"])}</a></h3>'
            f'<p>{esc(p["note"])}</p><ul class="points">{facts}</ul>'
            f'<p class="cta-row">{product_cta(p)}</p>{intent_note(p, "../")}'
            f'<p class="pcard-links"><a href="{esc(PRODUCT_SLUG[key])}">Every row, with its source</a></p></article>'
        )
    guides = "".join(
        f'<li><p class="eyebrow">{esc(g["kicker"])}</p><h3><a href="{esc(g["slug"])}">{esc(g["title"])}</a></h3>'
        f'<p>{esc(g["hook"].split(". ")[0].rstrip("."))}.</p></li>'
        for g in GUIDES
    )
    sources = "".join(f"<li>{src_link(s)} — {esc(SOURCES[s]['name'])}</li>" for s in SOURCES)
    body = f"""    <div class="page-head">
      <p class="eyebrow">Thermometers</p>
      <h1>Meat thermometers, read off the listing</h1>
      <p class="standfirst">An air fryer cooks by time; USDA says to finish by temperature. Two thermometers, one
      that reads in a second and one that stays in the food, with every number linked to the page it came from and
      every food-safety line linked to USDA.</p>
      <p class="receipts">{len(PRODUCTS)} thermometers · {rows} specification rows, each sourced or left blank ·
      {conflicts} published disagreement inside one listing · {blanks} blanks with a stated reason · read on {esc(AS_OF)}</p>
    </div>

    <section class="block">
      <h2>The two thermometers</h2>
      <div class="pgrid">{"".join(cards)}</div>
    </section>

    <section class="block">
      <h2>Guides, by the question they answer</h2>
      <ul class="guide-list">{guides}</ul>
      <p class="more"><a href="../topics/index.html">All guides, air fryers included</a></p>
    </section>

    <section class="block">
      <h2>What this desk is built from</h2>
      <p>Five pages and nothing else. A dash in a table is a value none of them states.</p>
      <ul class="source-list">{sources}</ul>
      <p class="not-tested">{esc(NOT_DONE.format(as_of=AS_OF))}</p>
    </section>
"""
    return page(
        "Meat thermometers",
        "Instant-read or leave-in? Two meat thermometers compared row by row from their listings, with USDA's "
        "safe temperatures and placement rules linked beside every line.",
        body, rel=f"{SECTION}/index.html", crumb_label="Thermometers",
    )


def page_product(key: str) -> str:
    p = PRODUCTS[key]
    rel = f"{SECTION}/{PRODUCT_SLUG[key]}"
    before = "".join(f'<li class="claim" data-src="{esc(",".join(x["src"]))}">{esc(x["text"])}{cite(x["src"])}</li>'
                     for x in p.get("before_you_buy", []))
    conflicts = [r for r in p["rows"] if r["status"] == "conflict"]
    conflict_block = ""
    if conflicts:
        items = "".join(f'<li><strong>{esc(r["attr"])}:</strong> {esc(r["detail"])}</li>' for r in conflicts)
        conflict_block = (
            '<section class="block callout-flag"><h2>Where the listing disagrees with itself</h2>'
            "<p>Printed as a disagreement, not resolved in favour of the more flattering statement.</p>"
            f'<ul class="points">{items}</ul></section>'
        )
    related_html = "".join(
        f'<li><a href="{esc(g["slug"])}">{esc(g["title"])}</a> <span>{esc(g["kicker"])}</span></li>' for g in GUIDES
    )
    body = f"""    <article class="post">
    <div class="page-head">
      <p class="eyebrow">{esc(p["brand"])} · {esc(p["kind_label"])}</p>
      <h1>{esc(p["name"])}</h1>
      <p class="standfirst">{esc(p["headline"])}. {esc(p["note"])}</p>
      <p class="receipts">Model <code>{esc(_row(p, ["Model"])["value"])}</code> · ASIN <code>{esc(p["asin"])}</code> ·
      ledger entry {esc(p["ledger_id"])} · read off www.amazon.com on {esc(AS_OF)}</p>
    </div>

    <div class="block block--verdict">
      <h2>See the listing</h2>
      <p class="cta-row">{product_cta(p)}</p>
      {intent_note(p, "../")}
    </div>

    <section class="block">
      <h2>The specification, row by row</h2>
      <p>Nobody on this site has used this thermometer, so there is no performance paragraph. The rows are the
      review, and each one says where it came from.</p>
      {spec_table(p)}
    </section>
{conflict_block}
    <section class="block">
      <h2>Before you order</h2>
      <ul class="points">{before}</ul>
    </section>

    <section class="block">
      <h2>The listing title, as published</h2>
      <p class="quote">{esc(p["title_official"])}</p>
      <p class="row-note">Category on the listing: {esc(p["category_path"])}.</p>
    </section>

    <section class="block">
      <h2>Read this with</h2>
      <ul class="related">{related_html}</ul>
    </section>

    <section class="block">
      <h2>What we did not do</h2>
      <p class="not-tested">{esc(NOT_DONE.format(as_of=AS_OF))}</p>
    </section>
    </article>
"""
    return page(p["name"], f'{p["headline"]}. {p["note"]}'[:158], body, rel=rel, crumb_label=p["short"])


def page_guide(slug: str) -> str:
    g = GUIDE_BY_SLUG[slug]
    rel = f"{SECTION}/{slug}"
    key = "t" + slug.replace(".html", "").replace("-", "")
    parts = []
    for si, sec in enumerate(g["sections"], start=1):
        parts.append(
            f'<section class="block"><h2>{esc(sec["h2"])}</h2>'
            f'{render_blocks(sec["blocks"], key=f"{key}s{si}", root="../")}</section>'
        )
    products = "".join(
        f'<li><a href="{esc(PRODUCT_SLUG[k])}">{esc(p["name"])}</a> <span>{esc(p["headline"])}.</span></li>'
        for k, p in PRODUCTS.items()
    )
    cross = ""
    if g.get("cross_links"):
        items = "".join(
            f'<li><a href="{esc(h)}">{esc(t)}</a> <span>{esc(n)}</span></li>' for h, t, n in g["cross_links"]
        )
        cross = f'<section class="block"><h2>The air fryers on this site</h2><ul class="related">{items}</ul></section>'
    related = "".join(
        f'<li><a href="{esc(r)}">{esc(GUIDE_BY_SLUG[r]["title"])}</a> <span>{esc(GUIDE_BY_SLUG[r]["kicker"])}</span></li>'
        for r in g.get("related", [])
    )
    used = []
    for sec in g["sections"]:
        for b in sec["blocks"]:
            ids = list(b.get("src", []))
            if b["kind"] == "temps":
                ids += [TEMPS[t]["src"] for t in b["rows"]]
            if b["kind"] == "compare":
                ids += [r["src"] for p in PRODUCTS.values() for spec in b["rows"]
                        for r in [_row(p, spec.split("|"))] if r and r.get("src") and r["status"] in VALUED]
            used += [i for i in ids if i not in used]
    src_list = "".join(f"<li>{src_link(s)} — {esc(SOURCES[s]['name'])}</li>" for s in sorted(used))
    body = f"""    <article class="post">
    <div class="page-head">
      <p class="eyebrow">{esc(g["kicker"])} · {esc(g["intent"])} search</p>
      <h1>{esc(g["title"])}</h1>
      <p class="standfirst">{esc(g["hook"])}</p>
      <p class="receipts">Answers: <em>{esc(g["target_query"])}</em> · read on {esc(AS_OF)} · every line sourced</p>
    </div>
{"".join(parts)}
    <section class="block block--cta">
      <h2>The thermometers this guide is about</h2>
      <ul class="related">{products}</ul>
      <p class="row-note">Links go to our own pages, which carry the tagged listing link and its disclosure.</p>
    </section>
{cross}
    <section class="block">
      <h2>What we did not do</h2>
      <p class="not-tested">{esc(NOT_DONE.format(as_of=AS_OF))}</p>
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
    return page(g["title"], g["meta_description"], body, rel=rel, crumb_label=g["kicker"])


def page_rels() -> list[str]:
    """Every page this module publishes, as a path relative to marketing/. No rendering needed."""
    return (
        [f"{SECTION}/index.html"]
        + [f"{SECTION}/{PRODUCT_SLUG[k]}" for k in PRODUCTS]
        + [f"{SECTION}/{g['slug']}" for g in GUIDES]
    )


def guide_entries() -> list[dict]:
    """Feed/index metadata for build_marketing (titles, links and dates already published on the pages)."""
    return [
        {"rel": f"{SECTION}/{g['slug']}", "slug": g["slug"], "title": g["title"], "kicker": g["kicker"],
         "intent": g["intent"], "hook": g["hook"], "target_query": g["target_query"], "date": AS_OF}
        for g in GUIDES
    ]


# --------------------------------------------------------------------------- page gate


class Links(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            a = dict(attrs)
            if a.get("href"):
                self.links.append(a)


def gate(rel: str, doc: str, known: set[str]) -> list[str]:
    problems = [f"{rel}: {p}" for p in audit_html(doc)]
    if REQUIRED_SITE_DISCLOSURE not in doc:
        problems.append(f"{rel}: missing the Associates disclosure sentence")
    if f'rel="canonical" href="{LIVE}{rel}"' not in doc:
        problems.append(f"{rel}: canonical URL is not its own path")
    if "sponsored-link" in doc and ("disclosure--link" not in doc or "Special Link" not in doc):
        problems.append(f"{rel}: product link without its link-level disclosure or Special Link note")
    p = Links()
    p.feed(doc)
    for a in p.links:
        href = a["href"]
        classes = (a.get("class") or "").split()
        if href.startswith(("http://", "https://")):
            host = href.split("/")[2].lower()
            if host not in ALLOWED_HOSTS:
                problems.append(f"{rel}: link to non-allow-listed host {host!r}")
            if host in MARKETPLACE_HOSTS:
                if "sponsored" not in (a.get("rel") or ""):
                    problems.append(f"{rel}: Amazon link without rel=sponsored: {href[:80]}")
                if "sponsored-link" in classes and f"tag={ASSOCIATES_TAG}" not in href:
                    problems.append(f"{rel}: product link without the owner's tag: {href[:80]}")
                if "src" in classes and "tag=" in href:
                    problems.append(f"{rel}: citation link carries a tag: {href[:80]}")
                if "tag=" not in href and "src" not in classes:
                    problems.append(f"{rel}: untagged Amazon link that is not a citation: {href[:80]}")
            continue
        if href.startswith(("#", "mailto:")):
            continue
        target = (OUT / rel).parent / href.split("#")[0]
        resolved = target.resolve()
        try:
            inside = str(resolved.relative_to(OUT.resolve()))
        except ValueError:
            inside = None
        if not (resolved.is_file() or (inside and inside in known)):
            problems.append(f"{rel}: broken internal link {href}")
    for cid, srcs in re.findall(r'class="claim"(?: id="([^"]*)")? data-src="([^"]*)"', doc):
        ids = [x for x in srcs.split(",") if x]
        if not ids or any(i not in SOURCES for i in ids):
            problems.append(f"{rel}: claim {cid or '(list item)'} has a missing or unresolvable source ({srcs!r})")
    for take in re.findall(r'<aside class="take".*?</aside>', doc, flags=re.S):
        if "take-label" not in take:
            problems.append(f"{rel}: an opinion box without its label")
    body = doc.split("<body", 1)[1]
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
    flat = text.lower()
    if MONEY.search(text):
        problems.append(f"{rel}: a money amount is printed - prices are never published")
    if RATINGS.search(text):
        problems.append(f"{rel}: a rating, review count or sales rank is printed")
    for w in BANNED:
        if w in flat:
            problems.append(f"{rel}: banned phrase {w!r}")
    for w in FIRST_HAND:
        if w in flat:
            problems.append(f"{rel}: claims first-hand use ({w!r})")
    return problems


def render() -> dict[str, str]:
    """Validate the data, render every desk page, gate each one. Keys are paths relative to marketing/."""
    validate_data()
    pages = {f"{SECTION}/index.html": page_hub()}
    for k in PRODUCTS:
        pages[f"{SECTION}/{PRODUCT_SLUG[k]}"] = page_product(k)
    for g in GUIDES:
        pages[f"{SECTION}/{g['slug']}"] = page_guide(g["slug"])
    assert list(pages) == page_rels()
    known = set(pages)
    problems = [p for rel, doc in pages.items() for p in gate(rel, doc, known)]
    if problems:
        raise BuildError("refusing to publish:\n  " + "\n  ".join(problems))
    return pages


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail if committed output differs or a gate fails")
    args = ap.parse_args(argv)
    pages = render()
    if args.check:
        drift = []
        for rel, doc in pages.items():
            f = OUT / rel
            if not f.is_file():
                drift.append(f"{rel}: missing")
            elif f.read_text(encoding="utf-8") != doc:
                drift.append(f"{rel}: differs from a fresh build")
        for f in sorted((OUT / SECTION).rglob("*")) if (OUT / SECTION).is_dir() else []:
            rel = str(f.relative_to(OUT))
            if f.is_file() and rel not in pages:
                drift.append(f"{rel}: in the tree but not generated - remove it or add it to the data")
        if drift:
            print("\n".join(drift))
            return 1
        rows = sum(len(p["rows"]) for p in PRODUCTS.values())
        print(f"OK  {len(pages)} thermometer pages · {rows} spec rows · {len(SOURCES)} sources · gates passed · committed output is current")
        return 0
    for rel, doc in pages.items():
        dest = OUT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(doc, encoding="utf-8")
    print(f"built {len(pages)} thermometer pages into marketing/{SECTION}/")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (BuildError, LinkPolicyError) as exc:
        print(f"BUILD REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(1)
