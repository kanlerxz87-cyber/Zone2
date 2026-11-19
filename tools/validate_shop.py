#!/usr/bin/env python3
"""Gate for the shop section (T66, session arena/75efdf57-zone2, 2026-11-19).

Reads the published HTML under shop/ (and the shop data) and fails on any of:

  S1  sourcing      every <tr><td class="k"> row - and every value cell of a spec/compare table -
                    carries a source link (class pb-src) or a blank with a written reason (<small>)
  S2  prices        no price-like string, no numeric price assignment
  S3  disclosure    the Operating Agreement sentence is on the page, in the strip under the masthead
                    (before <main>) and again in the footer, and before the first table
  S4  links         every amazon.com link carries sponsored+nofollow; every product button carries
                    tag=shopnow047c-20, data-link-state, data-product-key and "(paid link)";
                    citation links (pb-src) are untagged; no other account's tag
  S5  internal      every relative href/src resolves to a file
  S6  canonical     <link rel="canonical"> is the live URL of the page
  S7  metrics       no asserted traffic/click/conversion figure
  S8  tokens        no unresolved {{...}} guide token
  S9  images        every <img> has non-empty alt and width/height
  S10 data          catalog: verified rows cite known sources; blank rows have a reason and no
                    value; conflict rows cite at least two sources; intent fields stay separate
                    (an observed target is never copied into an intended field)
  S12 feed        shop/feed.xml parses and every item resolves to a published guide
  S11 briefing      every suggestion is 'Proposed', its recommendation is one of its options, its
                    waits_on ids exist; every open question has known/missing/how filled in

Exit 0 on pass, 1 on failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/"
TAG = "shopnow047c-20"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
PRICE_RE = re.compile(r"(?:US)?\$\s?\d[\d,]*\.?\d{0,2}\b|\b\d[\d,]*\.\d{2}\s?(?:USD|usd|EUR|eur)\b|€\s?\d")
METRIC_WORD = (r"(?:visitors|visits|page\s?views|sessions|clicks|conversions|impressions|"
               r"orders|sales|revenue|earnings|conversion rate|CTR)")
VANITY_RE = re.compile(rf"\b\d[\d,]*(?:\.\d+)?\s*%?\s+{METRIC_WORD}\b"
                       rf"|\b{METRIC_WORD}\s*(?:of|:|=|was|were|is|at)?\s+\d[\d,]*(?:\.\d+)?\s*%?", re.I)


def pages() -> list[Path]:
    return sorted((ROOT / "shop").rglob("*.html"))


def check_page(p: Path, errors: list[str]) -> None:
    rel = p.relative_to(ROOT).as_posix()
    h = p.read_text(encoding="utf-8")

    def fail(msg: str) -> None:
        errors.append(f"{rel}: {msg}")

    # S1 sourcing
    for r in re.findall(r'<tr><td class="k">(.*?)</tr>', h, re.S):
        if 'class="pb-src"' not in r and 'class="pb-blank"' not in r:
            fail(f"S1 row without a source or a reasoned blank: {r[:90]}")
        if 'class="pb-blank"' in r and "<small>" not in r:
            fail(f"S1 blank without a written reason: {r[:90]}")
    # compare tables hold one product per cell, so each cell must carry its own source or reason
    for tbl in re.findall(r'<table class="pb-table sh-compare">(.*?)</table>', h, re.S):
        for tr in re.findall(r'<tr><td class="k">.*?</td>(.*?)</tr>', tbl, re.S):
            for cell in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S):
                if 'class="pb-src"' not in cell and not ('class="pb-blank"' in cell and "<small>" in cell):
                    fail(f"S1 compare cell without a source or reasoned blank: {cell[:80]}")

    # S2 prices
    for m in PRICE_RE.finditer(h):
        fail(f"S2 price-like string {m.group(0)!r}")
    if re.search(r"\b(?:price|list price|MSRP)\b\s*[:=]\s*\d", h, re.I):
        fail("S2 numeric price assignment")

    # S3 disclosure
    main_at = h.find("<main")
    first = h.find(DISCLOSURE)
    if first == -1:
        fail("S3 disclosure sentence missing")
    else:
        if main_at == -1 or first > main_at:
            fail("S3 disclosure is not in the strip above <main>")
        if 'class="pb-disc' not in h[:main_at]:
            fail("S3 disclosure strip (.pb-disc) missing above <main>")
        foot = h.find('<footer')
        if foot == -1 or DISCLOSURE not in h[foot:]:
            fail("S3 disclosure not repeated in the footer")
        t = h.find("<table")
        if t != -1 and first > t:
            fail("S3 disclosure appears after a table")

    # S4 links
    for m in re.finditer(r'<a[^>]+href="(https?://(?:www\.)?amazon\.com[^"]*)"[^>]*>(.*?)</a>', h, re.S):
        tag, href, text = m.group(0), m.group(1), m.group(2)
        cls = (re.search(r'class="([^"]*)"', tag) or [None, ""])[1].split()
        if "sponsored" not in tag or "nofollow" not in tag:
            fail(f"S4 amazon.com link without sponsored+nofollow: {href[:90]}")
        if "tag=" in href and f"tag={TAG}" not in href:
            fail(f"S4 foreign Associates tag: {href[:90]}")
        if "pb-src" in cls and "tag=" in href:
            fail(f"S4 citation carries a tag: {href[:90]}")
        if "sh-buy" in cls:
            if f"tag={TAG}" not in href:
                fail(f"S4 product button without the owner's tag: {href[:90]}")
            if 'data-link-state="' not in tag or 'data-product-key="' not in tag:
                fail(f"S4 product button not counted by events.js: {href[:90]}")
            if "(paid link)" not in text:
                fail(f"S4 product button without '(paid link)': {href[:90]}")
            if re.search(r"amazon|associates", re.sub(r"<[^>]+>", "", text), re.I):
                fail("S4 button text names Amazon (link_builder rule R-11)")
        elif "pb-src" not in cls:
            fail(f"S4 amazon.com link that is neither a product button nor a citation: {tag[:90]}")

    # S5 internal links
    for m in re.finditer(r'(?:href|src)="([^"#?]+?)(?:[#?][^"]*)?"', h):
        ref = m.group(1)
        if ref.startswith(("http", "mailto:", "data:")):
            continue
        if not (p.parent / ref).resolve().is_file():
            fail(f"S5 broken reference {ref}")
    for m in re.finditer(r'srcset="([^"]+)"', h):
        for part in m.group(1).split(","):
            ref = part.strip().split(" ")[0]
            if not (p.parent / ref).resolve().is_file():
                fail(f"S5 broken srcset reference {ref}")

    # S6 canonical
    want = LIVE + rel
    if f'<link rel="canonical" href="{want}">' not in h:
        fail(f"S6 canonical is not {want}")

    # S7 metrics
    body = re.sub(r"<[^>]+>", " ", h)
    for m in VANITY_RE.finditer(body):
        window = body[max(0, m.start() - 90): m.end() + 90]
        if re.search(r"\b(zero|no .{0,24}figure|none has been measured|nothing|not measured|unmeasured)\b", window, re.I):
            continue
        fail(f"S7 performance figure asserted: {m.group(0)!r}")

    # S8 tokens
    if "{{" in h or "}}" in h:
        fail("S8 unresolved guide token")

    # S9 images
    for m in re.finditer(r"<img\b[^>]*>", h):
        tag = m.group(0)
        if not re.search(r'alt="[^"]+"', tag):
            fail(f"S9 image without alt text: {tag[:80]}")
        if "width=" not in tag or "height=" not in tag:
            fail(f"S9 image without dimensions: {tag[:80]}")


def check_data(errors: list[str]) -> None:
    cat = json.loads((ROOT / "shop/data/catalog.json").read_text(encoding="utf-8"))
    br = json.loads((ROOT / "shop/data/briefing.json").read_text(encoding="utf-8"))
    srcs = cat["sources"]
    for sid, s in srcs.items():
        if not s.get("url", "").startswith("https://"):
            errors.append(f"S10 source {sid}: not an https URL")
        if "tag=" in s.get("url", ""):
            errors.append(f"S10 source {sid}: citation URL carries a tag")
    for p in cat["products"]:
        for r in p["rows"]:
            where = f"S10 {p['id']} {r['attr']}"
            if r["status"] == "verified":
                if not r["value"] or not r["src"]:
                    errors.append(f"{where}: verified without a value and a source")
            elif r["status"] == "blank":
                if r["value"] or not r.get("blank_reason"):
                    errors.append(f"{where}: blank must have no value and a reason")
            elif r["status"] == "conflict":
                # two pages disagreeing need two sources; one page disagreeing with itself is
                # marked same_page and must quote both readings in its value
                if len(r["src"]) < 2 and not (r.get("same_page") and len(r["src"]) == 1
                                               and r["value"].count("'") >= 4):
                    errors.append(f"{where}: conflict needs two sources, or same_page with both readings quoted")
            else:
                errors.append(f"{where}: unknown status {r['status']}")
            for s in r["src"]:
                if s not in srcs:
                    errors.append(f"{where}: unknown source {s}")
            if r["attr"].lower() in ("price", "customer rating", "rating", "reviews") and r["status"] != "blank":
                errors.append(f"{where}: prices and ratings are never printed")
        it = p["intent"]
        observed = it["observed_redirect_target"]
        for k in ("intended_asin", "intended_listing_url", "confirmation_date", "intent_source"):
            if it.get(k) and (it[k] == observed or (k == "intended_asin" and not it.get("intent_source"))):
                errors.append(f"S10 {p['id']} intent.{k}: filled from the observation or without a source")
    qids = {q["id"] for q in br["questions"]}
    for s in br["suggestions"]:
        if "Proposed" not in s["status"]:
            errors.append(f"S11 {s['id']}: status is not Proposed")
        if s["recommendation"] not in {o["label"] for o in s["options"]}:
            errors.append(f"S11 {s['id']}: recommendation not among options")
        for w in s["waits_on"]:
            if w not in qids:
                errors.append(f"S11 {s['id']}: waits on unknown {w}")
        for sid in s.get("src", []):
            if sid not in srcs:
                errors.append(f"S11 {s['id']}: unknown source {sid}")
    for q in br["questions"]:
        for k in ("known", "missing", "how"):
            if not q.get(k, "").strip():
                errors.append(f"S11 {q['id']}: empty {k}")
        for sid in q.get("known_src", []):
            if sid not in srcs:
                errors.append(f"S11 {q['id']}: unknown source {sid}")


def check_feed(errors: list[str]) -> None:
    """S12 feed: shop/feed.xml parses as RSS 2.0 and every item resolves to a published guide."""
    import xml.etree.ElementTree as ET
    f = ROOT / "shop" / "feed.xml"
    if not f.is_file():
        errors.append("S12 shop/feed.xml missing")
        return
    try:
        root = ET.fromstring(f.read_bytes())
    except ET.ParseError as exc:
        errors.append(f"S12 shop/feed.xml does not parse ({exc})")
        return
    items = root.findall("./channel/item")
    if not items:
        errors.append("S12 shop/feed.xml has no items")
    for it in items:
        link = (it.findtext("link") or "").strip()
        if not link.startswith(LIVE) or not (ROOT / link[len(LIVE):]).is_file():
            errors.append(f"S12 feed item link does not resolve to a published page: {link}")
        if not (it.findtext("pubDate") or "").strip():
            errors.append(f"S12 feed item without pubDate: {link}")


def main() -> int:
    errors: list[str] = []
    ps = pages()
    if len(ps) < 17:
        errors.append(f"expected at least 17 shop pages, found {len(ps)}")
    for p in ps:
        check_page(p, errors)
    check_data(errors)
    check_feed(errors)
    if errors:
        print(f"SHOP GATE FAILED - {len(errors)} problem(s):")
        for x in errors:
            print("  " + x)
        return 1
    print(f"shop gate PASS: {len(ps)} pages + feed, S1-S12 clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
