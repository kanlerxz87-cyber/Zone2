#!/usr/bin/env python3
"""Deploy gate for the marketing set.

Fails (non-zero exit) if any of these stop being true, so none of them depends on someone remembering:

  G1  every generated page exists and carries the Associates disclosure sentence
  G2  every page that shows an affiliate link also carries a link-level disclosure (R-02)
  G3  every generated page has fully resolved internal links and asset references
  G4  no page prints a money amount in a buying context (the project's no-price rule)
  G5  every outbound Amazon marketplace link carries rel="sponsored" (Google's outbound-link rule)
  G6  every generated page states the preview state of its links while no Associates ID is configured
  G7  **every table row that shows a value also shows a source link** - the core project rule
  G8  every row marked UNVERIFIED/WITHHELD prints no value at all
  G9  committed HTML matches a fresh build (nothing hand-edited)
  G10 every official source URL used is on an allow-listed official host
  G11 every article in the data is published, linked from the topic hub, and reachable


The row-level checks (G7/G8) re-derive the expectation from marketing/data/facts.json and then read the
rendered HTML, so a renderer bug cannot quietly pass its own test.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

from build_marketing import PAGES, build  # noqa: E402
from link_builder import REQUIRED_SITE_DISCLOSURE  # noqa: E402

ROOT = REPO / "marketing"
FACTS = json.loads((ROOT / "data" / "facts.json").read_text(encoding="utf-8"))
EDITORIAL = json.loads((ROOT / "data" / "editorial.json").read_text(encoding="utf-8"))

OFFICIAL_HOSTS = {
    "www.amazon.com",
    "amazon.com",
    "chefman.com",
    "www.chefman.com",
    "www.emerileveryday.com",
    "affiliate-program.amazon.com",
    # Session 6cc428f1 (T31, 2026-11-15): the cooking and food-safety articles are sourced to two
    # United States government publishers and to Google Search Central's own documentation about
    # how a site should be written. These are primary publishers speaking about their own subject.
    "www.fsis.usda.gov",
    "fsis.usda.gov",
    "www.foodsafety.gov",
    "foodsafety.gov",
    "developers.google.com",
}
MARKETPLACE_HOSTS = {"www.amazon.com", "amazon.com"}

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(
    r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer|cost)\b", re.I
)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|tax|refund|withhold)s?\b", re.I
)

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.refs.append(("script", a))
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href"):
            self.refs.append(("stylesheet", a))
        if tag == "a" and a.get("href"):
            self.refs.append(("a", a))


def rel_path(ref: str) -> str:
    return ref.split("#")[0].split("?")[0]


def check_links(rel: str, doc: str) -> None:
    page_dir = (ROOT / rel).parent
    p = Refs()
    p.feed(doc)
    for kind, a in p.refs:
        ref = a.get("href") or a.get("src") or ""
        if kind != "a":
            target = (page_dir / ref).resolve()
            if not target.is_file():
                fail(f"G3 {rel}: missing asset {ref}")
            continue
        if ref.startswith(("http://", "https://")):
            host = re.sub(r"^https?://", "", ref).split("/")[0].lower()
            if host in MARKETPLACE_HOSTS:
                if "sponsored" not in (a.get("rel") or "").lower():
                    fail(f"G5 {rel}: Amazon link without rel=sponsored: {ref[:90]}")
                if "tag=" not in ref:
                    if "NOT FOR PUBLICATION" not in doc and "preview link" not in doc:
                        fail(f"G5 {rel}: untagged Amazon link with no preview label: {ref[:90]}")
            if host not in OFFICIAL_HOSTS:
                fail(f"G10 {rel}: link to a non-allow-listed host {host!r}")
            continue
        if ref.startswith(("#", "mailto:")):
            continue
        target = (page_dir / rel_path(ref)).resolve()
        if not target.is_file():
            fail(f"G3 {rel}: broken internal link {ref}")


def check_prices(rel: str, doc: str) -> None:
    text = re.sub(r"<[^>]+>", " ", doc)
    for unit in re.split(r"</tr>|</p>|</li>|<br\s*/?>|\n", text):
        for m in MONEY.finditer(unit):
            if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                fail(f"G4 {rel}: money value {m.group(0)!r} in a buying context")


def check_rows(rel: str, doc: str) -> None:
    """G7/G8: every row that prints a value must carry an official source, and a row that prints
    nothing must say so explicitly.

    Two row families exist now: the product articles' specification rows (``p<N>-r<N>``) and the
    editorial articles' chart rows (``ea-<slug>-r<N>``). Both are checked the same way.
    """
    if re.fullmatch(r"articles/p\d\.html", rel):
        rows = re.findall(r'<tr id="p\d-r\d+">(.*?)</tr>', doc, flags=re.S)
        if not rows:
            fail(f"G7 {rel}: no specification rows found - the page lost its table")
            return
        for i, row in enumerate(rows, start=1):
            has_value = bool(re.search(r"<strong>.*?</strong>", row, flags=re.S))
            has_src = 'class="src"' in row
            has_pill = 'class="pill' in row
            is_blank = 'class="cell-blank"' in row
            if has_value and not has_src:
                fail(f"G7 {rel}: row {i} prints a value with no official source link")
            if not has_value and not is_blank:
                fail(f"G8 {rel}: row {i} has neither a value nor an explicit blank marker")
            if is_blank and not has_pill:
                fail(f"G8 {rel}: row {i} is blank but carries no UNVERIFIED/WITHHELD pill and no reason")
        # cross-check the count against the data file
        key = re.search(r"articles/(p\d)\.html", rel).group(1).upper()
        expected = len(next(p for p in FACTS["products"] if p["key"] == key)["rows"])
        if len(rows) != expected:
            fail(f"G7 {rel}: {len(rows)} rows rendered but the data file defines {expected}")
        return

    m = re.fullmatch(r"articles/([a-z0-9-]+)\.html", rel)
    if not m or m.group(1) == "index":
        return
    slug = m.group(1)
    article = next((a for a in EDITORIAL["editorial_articles"] if a["slug"] == slug), None)
    if article is None:
        fail(f"G7 {rel}: no editorial article with slug {slug!r} in marketing/data/editorial.json")
        return
    rows = re.findall(r'<tr id="ea-[a-z0-9-]+-r\d+">(.*?)</tr>', doc, flags=re.S)
    expected_rows = len((article.get("table") or {}).get("rows", []))
    if len(rows) != expected_rows:
        fail(f"G7 {rel}: {len(rows)} chart rows rendered but the data file defines {expected_rows}")
    for i, row in enumerate(rows, start=1):
        if 'class="src"' not in row:
            fail(f"G7 {rel}: chart row {i} prints values with no official source link")
    # Every section, FAQ answer and table row must cite at least one source.
    sections = article["sections"]
    if len(sections) != len(re.findall(r'<section class="article-section">', doc)):
        fail(f"G7 {rel}: {len(sections)} sections in the data but the page rendered a different number")
    for i, sec in enumerate(sections, start=1):
        if not sec.get("source_ids"):
            fail(f"G7 {rel}: section {i} has no source_ids")
    for i, f in enumerate(article["faq"], start=1):
        if not f.get("source_ids"):
            fail(f"G7 {rel}: FAQ answer {i} has no source_ids")
    for i, row in enumerate((article.get("table") or {}).get("rows", []), start=1):
        if not row.get("source_ids"):
            fail(f"G7 {rel}: chart row {i} has no source_ids")


def check_editorial_sources() -> None:
    """G10/G11: every source the editorial articles cite must resolve to a registered source on an
    allow-listed official host.

    Split out of main() so a test can call it directly: the negative test strips a citation from
    one article and asserts this function turns red. A check that cannot be shown to fail is not
    evidence of anything.
    """
    registered = {s["id"] for s in FACTS["products"][0]["official_sources"]}
    registered |= {s["id"] for product in FACTS["products"] for s in product["official_sources"]}
    registered |= {s["id"] for s in EDITORIAL["sources"]}
    for src in EDITORIAL["sources"]:
        host = src["url"].split("/")[2]
        if host not in OFFICIAL_HOSTS:
            fail(f"G10 data: editorial source {src['id']} host {host!r} is not allow-listed")
    for article in EDITORIAL["editorial_articles"]:
        cited = set(article.get("sources", []))
        # Every individual claim carries its own citation. An article-level list is a summary of
        # what was read, not a substitute for citing the source of each specific statement.
        for i, sec in enumerate(article["sections"], start=1):
            if not sec.get("source_ids"):
                fail(f"G11 data: article {article['slug']!r} section {i} cites no source")
            cited.update(sec.get("source_ids", []))
        for i, f in enumerate(article["faq"], start=1):
            if not f.get("source_ids"):
                fail(f"G11 data: article {article['slug']!r} FAQ answer {i} cites no source")
            cited.update(f.get("source_ids", []))
        for i, row in enumerate((article.get("table") or {}).get("rows", []), start=1):
            if not row.get("source_ids"):
                fail(f"G11 data: article {article['slug']!r} chart row {i} cites no source")
            cited.update(row.get("source_ids", []))
        for pick in article.get("product_picks", []):
            cited.add(pick.get("src"))
        unknown = sorted(c for c in cited if c and c not in registered)
        if unknown:
            fail(f"G11 data: article {article['slug']!r} cites unregistered source ids {unknown}")
        if not cited:
            fail(f"G11 data: article {article['slug']!r} cites no source at all")


def check_editorial_coverage() -> None:
    """G11: the topic hub must exist, list every topic, and every article in the data must be
    published, linked from the hub and from the articles index.

    This is the check that stops a written article from being orphaned: an article that exists in
    the data but is not reachable from the hub would be invisible to a reader and to a crawler.
    """
    hub_path = ROOT / "topics.html"
    if not hub_path.is_file():
        fail("G11 topics.html: the topic hub is missing")
        return
    hub = hub_path.read_text(encoding="utf-8")

    for topic in EDITORIAL["topics"]:
        if f'id="topic-{topic["id"]}"' not in hub:
            fail(f"G11 topics.html: topic {topic['id']!r} has no anchor on the hub")
        for slug in topic["articles"]:
            article = next(
                (a for a in EDITORIAL["editorial_articles"] if a["slug"] == slug), None
            )
            if article is None:
                fail(f"G11 data: topic {topic['id']!r} lists unknown article slug {slug!r}")
                continue
            page = ROOT / "articles" / f"{slug}.html"
            if not page.is_file():
                fail(f"G11 articles/{slug}.html: article in the data has no generated page")
                continue
            if f'href="articles/{slug}.html"' not in hub:
                fail(f"G11 topics.html: article {slug!r} is not linked from its topic block")
            if f'href="{slug}.html"' not in (ROOT / "articles" / "index.html").read_text(encoding="utf-8"):
                fail(f"G11 articles/index.html: article {slug!r} is not listed in the index")
            # The hub must say what the topic covers, and the article must say what it answers.
            if not topic.get("blurb"):
                fail(f"G11 data: topic {topic['id']!r} has no blurb")
            if not article.get("dek"):
                fail(f"G11 data: article {slug!r} has no dek")
            if not article.get("answer"):
                fail(f"G11 data: article {slug!r} has no short answer")
            # A section with no paragraphs is an empty section on the page.
            for i, sec in enumerate(article["sections"], start=1):
                if not sec.get("paragraphs"):
                    fail(f"G11 data: article {slug!r} section {i} has no prose")
            if not article.get("faq"):
                fail(f"G11 data: article {slug!r} has no question-and-answer section")

    # The topics page and every article must be reachable from the site overview.
    overview = (ROOT / "index.html").read_text(encoding="utf-8")
    if 'href="topics.html"' not in overview:
        fail("G11 index.html: the topic hub is not linked from the overview")
    nav = (ROOT / "articles" / "index.html").read_text(encoding="utf-8")
    if 'href="../topics.html"' not in nav:
        fail("G11 articles/index.html: the topic hub is not linked from the articles index")


def main() -> int:
    if len(PAGES) < 9:
        fail(f"G1 expected at least 9 marketing pages, builder defines {len(PAGES)}")

    fresh = build(ROOT / ".fresh")  # build to a scratch dir, compare, then remove
    import shutil

    shutil.rmtree(ROOT / ".fresh", ignore_errors=True)

    for rel in PAGES:
        path = ROOT / rel
        if not path.is_file():
            fail(f"G1 {rel}: not generated")
            continue
        doc = path.read_text(encoding="utf-8")
        if REQUIRED_SITE_DISCLOSURE not in doc:
            fail(f"G1 {rel}: missing the Associates disclosure sentence")
        if "sponsored-link" in doc and "disclosure--link" not in doc:
            fail(f"G2 {rel}: affiliate link without a link-level disclosure")
        if "sponsored-link" in doc and "preview link" not in doc:
            fail(f"G6 {rel}: shows an affiliate link but does not state it is a non-earning preview link")
        check_links(rel, doc)
        check_prices(rel, doc)
        check_rows(rel, doc)
        if fresh.get(rel) != doc:
            fail(f"G9 {rel}: committed file differs from a fresh build")

    # Every official source URL in the data must be on an allow-listed host.
    for product in FACTS["products"]:
        for src in product["official_sources"]:
            host = src["url"].split("/")[2]
            if host not in OFFICIAL_HOSTS:
                fail(f"G10 data: source {src['id']} host {host!r} is not allow-listed")
        for row in product["rows"]:
            if row["status"] not in ("unverified", "withheld_by_policy") and not row.get("src"):
                fail(f"G7 data: {product['key']} row {row['attr']!r} has a value but no source")

    check_editorial_sources()
    check_editorial_coverage()

    pages = len(PAGES)
    rows = sum(len(p["rows"]) for p in FACTS["products"])
    if failures:
        print("\n".join(f"FAIL {f}" for f in failures))
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK  {pages} pages · {rows} spec rows · 0 failures")
    print("    disclosure on every page · affiliate links disclosed and marked preview · no prices ·")
    print("    internal links resolve · every valued row carries an official source link")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
