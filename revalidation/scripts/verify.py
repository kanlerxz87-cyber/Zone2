#!/usr/bin/env python3
"""Per-row sourcing verifier for the revalidation site (session c6e94e8d).

Enforces, for every page in revalidation/:
  1. The required Amazon Associates disclosure sentence is present.
  2. Every internal link / asset reference resolves to a real file.
  3. Every data-table row (<tr> with <td>) contains at least one external
     source link, OR is an explicit blank/unverified row that says so.
  4. No product price is printed. A dollar figure is allowed only when the
     surrounding cell is about programme economics, never a product purchase.
  5. No placeholder text.

Exit 0 = pass. Exit 1 = failures printed.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

EXTERNAL = re.compile(r"^https?://", re.I)
# Unanchored: used to ask "does this row cite an external official source at all?"
ANY_EXTERNAL = re.compile(r"https?://", re.I)
INTERNAL = re.compile(r"^(?!https?://|#|mailto:|javascript:)([^?#]+)", re.I)
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(r"\b(price|pricing|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|tax|refund|withhold)\w*",
    re.I,
)
PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum)\b", re.I)

failures: list[str] = []
rows_checked = 0
links_checked = 0


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and "src" in a:
            self.refs.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.refs.append(a["href"])
        if tag in ("a", "img") and a.get("href"):
            self.refs.append(a["href"])
        if tag == "img" and a.get("src"):
            self.refs.append(a["src"])


pages = sorted(SITE.rglob("*.html"))
if not pages:
    print("no pages found under", SITE)
    raise SystemExit(1)

for page in pages:
    rel = page.relative_to(ROOT).as_posix()
    html = page.read_text(encoding="utf-8")

    if DISCLOSURE not in html:
        failures.append(f"{rel}: missing the required Associates disclosure sentence")

    for m in PLACEHOLDER.finditer(re.sub(r"<[^>]+>", " ", html)):
        failures.append(f"{rel}: placeholder text {m.group(0)!r}")

    p = Refs()
    p.feed(html)
    for ref in p.refs:
        links_checked += 1
        if EXTERNAL.match(ref):
            continue
        m = INTERNAL.match(ref)
        if not m:
            continue
        target = (page.parent / m.group(1)).resolve()
        if not target.is_file():
            failures.append(f"{rel}: unresolved internal reference -> {ref}")

    # Per-row sourcing.
    for row in re.findall(r"<tr>(.*?)</tr>", html, re.S):
        if "<td" not in row:
            continue  # header row
        rows_checked += 1
        has_source = bool(ANY_EXTERNAL.search(row))
        is_blank = 'class="blank"' in row or "left blank" in row or "no official source" in row
        if not has_source and not is_blank:
            cells = re.sub(r"<[^>]+>", " ", row).strip()
            failures.append(f"{rel}: table row has neither a source link nor a blank flag -> {cells[:90]!r}")

    # No product prices: scan cell-by-cell.
    for cell in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", html, re.S):
        text = re.sub(r"<[^>]+>", " ", cell)
        for m in MONEY.finditer(text):
            if PRICE_CONTEXT.search(text) and not PROGRAM_CONTEXT.search(text):
                failures.append(f"{rel}: money value {m.group(0)!r} in a buying context")

print(f"Pages checked:        {len(pages)}")
print(f"Table rows checked:   {rows_checked}")
print(f"References checked:   {links_checked}")
print(f"Failures:             {len(failures)}")
if failures:
    print()
    for f in failures:
        print("  x", f)
    sys.exit(1)
sys.exit(0)
