#!/usr/bin/env python3
"""Zone2 site verifier.

Checks, for every page in the site root:
  1. Internal links (href to local files) resolve to real files.
  2. Every <tr> in a data table contains at least one external source link
     (http/https) OR is explicitly exempted (header rows are <th>, not <tr>).
  3. No obviously unfilled placeholders like TODO/TBD/FIXME/lorem.
  4. The Amazon Associates disclosure sentence appears on every page.

Exit code 0 = all checks pass; 1 = failures (printed).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pages to check (site root HTML).
PAGES = sorted(p for p in ROOT.glob("*.html"))

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# Rows allowed to lack an external source link (pure navigation/status rows
# are still required to have one; this list stays empty on purpose — every
# data row must cite a source).
ROW_EXEMPT_IDS: set[str] = set()

EXTERNAL_HREF = re.compile(r'^https?://', re.I)
INTERNAL_HREF = re.compile(r'^(?!https?://|#|mailto:)(.+?)(?:#.*)?$', re.I)
TODO_RE = re.compile(r'\b(TODO|TBD|FIXME|lorem ipsum)\b', re.I)

failures: list[str] = []
checked_rows = 0
checked_links = 0


def fail(msg: str) -> None:
    failures.append(msg)


def strip_tags(html: str) -> str:
    return re.sub(r'<[^>]+>', ' ', html)


for page in PAGES:
    rel = page.name
    html = page.read_text(encoding="utf-8")

    # --- check 4: disclosure present ---
    if DISCLOSURE not in html:
        fail(f"{rel}: missing required disclosure sentence")

    # --- check 3: placeholder junk ---
    # Ignore code-ish tokens inside <code> is overkill; simple scan is fine.
    body_text = strip_tags(html)
    for m in TODO_RE.finditer(body_text):
        fail(f"{rel}: placeholder text found: {m.group(0)!r}")

    # --- collect rows ---
    for row_match in re.finditer(r'<tr\b[^>]*>(.*?)</tr>', html, re.S | re.I):
        row = row_match.group(0)
        # Skip header rows (contain <th> and no <td>).
        if re.search(r'<th\b', row, re.I) and not re.search(r'<td\b', row, re.I):
            continue
        checked_rows += 1
        # Any http(s) occurrence anywhere in the row counts as a source link
        # (href="https://…", including multi-attribute anchors).
        has_external = bool(re.search(r'https?://', row, re.I))
        # Extract id attr if present for exemption matching.
        id_m = re.search(r'\bid="([^"]+)"', row, re.I)
        row_id_val = id_m.group(1) if id_m else ""
        if not has_external and row_id_val not in ROW_EXEMPT_IDS:
            # Give context: first 80 visible chars of the row.
            visible = strip_tags(row)
            visible = re.sub(r'\s+', ' ', visible).strip()[:80]
            fail(f"{rel}: table row without external source link: {visible!r}")

    # --- check 1: internal links resolve ---
    for href_m in re.finditer(r'href="([^"]+)"', html, re.I):
        href = href_m.group(1)
        if EXTERNAL_HREF.match(href) or href.startswith("#") or href.startswith("mailto:"):
            checked_links += 1
            continue
        target = href.split("#", 1)[0]
        if not target:
            continue
        checked_links += 1
        target_path = (ROOT / target).resolve()
        try:
            target_path.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"{rel}: link escapes site root: {href}")
            continue
        if not target_path.exists():
            fail(f"{rel}: broken internal link: {href}")

# --- data file checks ---
import json

for data_file in ["data/products.json", "data/compliance.json"]:
    p = ROOT / data_file
    if not p.exists():
        fail(f"missing data file: {data_file}")
        continue
    try:
        json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"{data_file}: invalid JSON: {e}")

# products.json rule: every product with status unverified must have nulls
# for its attribute fields and non-empty flag_ids + checks with sources.
pp = ROOT / "data/products.json"
if pp.exists():
    pdata = json.loads(pp.read_text(encoding="utf-8"))
    for prod in pdata.get("products", []):
        for field in ["name", "price", "rating", "review_count", "category",
                      "commission_rate", "availability", "best_seller_rank"]:
            if prod.get("status") == "unverified" and prod.get(field) is not None:
                fail(f"products.json: {prod['id']} has non-null {field} despite unverified status")
        if not prod.get("flag_ids"):
            fail(f"products.json: {prod.get('id')} missing flag_ids")
        for chk in prod.get("checks", []):
            if not chk.get("url", "").startswith("http"):
                fail(f"products.json: {prod.get('id')} check without http url: {chk}")

# compliance.json rule: every requirement must have an http(s) source.
cp = ROOT / "data/compliance.json"
if cp.exists():
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    for req in cdata.get("requirements", []):
        if not req.get("source", "").startswith("http"):
            fail(f"compliance.json: {req.get('id')} missing http source")

print(f"Pages checked:        {len(PAGES)}")
print(f"Table rows checked:   {checked_rows}")
print(f"Links checked:        {checked_links}")
print(f"Failures:             {len(failures)}")
for f in failures:
    print(f"  ✗ {f}")

sys.exit(1 if failures else 0)
