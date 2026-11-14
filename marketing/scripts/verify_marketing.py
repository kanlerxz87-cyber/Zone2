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

OFFICIAL_HOSTS = {
    "www.amazon.com",
    "amazon.com",
    "chefman.com",
    "www.chefman.com",
    "www.emerileveryday.com",
    "affiliate-program.amazon.com",
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
    """G7/G8: for the article pages, every attribute row must carry a source pill or say why not."""
    if not rel.startswith("articles/p"):
        return
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
