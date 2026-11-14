#!/usr/bin/env python3
"""Generate the data-driven blocks of assets/js/data.js from ledger/*.json.

Why this exists (T23 final integration): the root dashboard and the generated `pages/` namespace
were two hand-maintained copies of the same dataset, which is how the repository came to publish two
mutually contradictory readings of the same evidence. From now on the ledger is the single source of
truth for the product rows, the specification rows, the resolution evidence and the flags register,
and this script projects them into the root site's dataset.

Usage:
    python3 tools/build_root_data.py           # rewrite assets/js/data.js
    python3 tools/build_root_data.py --check   # fail if the committed file is out of date
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
DATA_JS = REPO / "assets" / "js" / "data.js"

PRODUCTS = json.loads((LEDGER / "products.json").read_text(encoding="utf-8"))
FLAGS = json.loads((LEDGER / "flags.json").read_text(encoding="utf-8"))
SOURCES = {s["id"]: s for s in json.loads((LEDGER / "sources.json").read_text(encoding="utf-8"))["sources"]}


def js(value) -> str:
    """Emit a JavaScript string literal, or null/"" for an empty value."""
    if value is None:
        return "null"
    if value == "":
        return '""'
    return json.dumps(value, ensure_ascii=False)


def block(name: str, body: str) -> str:
    return f"/* BEGIN GENERATED: {name} */\n{body}\n/* END GENERATED: {name} */"


# ------------------------------------------------------------------------------- products block
def gen_products() -> str:
    out = ["const PRODUCTS = ["]
    for e in PRODUCTS["entries"]:
        r = e["resolved"]
        out.append("  {")
        out.append(f"    id: {js(e['id'].lower().replace('-', ''))},")
        out.append(f"    shortLink: {js(e['submitted_url'])},")
        out.append(f"    shortCode: {js(e['token_as_given'])},")
        out.append(f"    codeLength: {e['asin_length_observed']},")
        out.append(f"    asinFormatValid: {str(e['asin_format_valid']).lower()},")
        out.append(f"    canonicalDpUrl: {js(e['canonical_dp_url'])},")
        out.append(f"    canonicalDpResult: {js(e['canonical_dp_result'])},")
        out.append(f"    resolvesToAsin: {js(r['asin'])},")
        out.append(f"    resolvesToUrl: {js(r['resolves_to'])},")
        out.append(f"    brand: {js(r['brand'])},")
        out.append(f"    title: {js(r['title'])},")
        out.append(f"    category: {js(r['category'])},")
        out.append(f"    categoryPath: {js(r['category_path'])},")
        out.append("    price: null,")
        out.append("    rating: null,")
        out.append("    reviewCount: null,")
        out.append("    availability: null,")
        out.append("    identityStatus: \"OBSERVED\",")
        out.append(f"    source: {js(r['source_ids'][0] and SOURCES[r['source_ids'][0]]['url'])},")
        out.append(
            f"    sourceLabel: {js('Amazon.com product page for the destination this link resolves to (' + r['asin'] + ')')},"
        )
        out.append(f"    flags: {json.dumps(e['flag_ids'])},")
        out.append("  },")
    out.append("];")
    return "\n".join(out)


# ----------------------------------------------------------------------------------- specs block
def gen_specs() -> str:
    out = ["const SPECS = ["]
    for e in PRODUCTS["entries"]:
        r = e["resolved"]
        pid = e["id"].lower().replace("-", "")
        out.append(f"  // {pid} — {r['brand']} {r['asin']} (resolved from {e['token_as_given']})")
        for sp in r["specs"]:
            out.append("  {")
            out.append(f"    pid: {js(pid)},")
            out.append(f"    attribute: {js(sp['attribute'])},")
            out.append(f"    value: {js(sp['value'])},")
            out.append(f"    status: {js(sp['status'])},")
            out.append(f"    source: {js(SOURCES[sp['source_ids'][0]]['url'] if sp.get('source_ids') else '')},")
            out.append(f"    sourceLabel: {js(sp.get('source_label') or sp.get('why_blank') or '')},")
            out.append(f"    sourceIds: {json.dumps(sp.get('source_ids', []))},")
            out.append("  },")
    out.append("];")
    return "\n".join(out)


# ------------------------------------------------------------------ resolution evidence block
def gen_resolution_evidence() -> str:
    out = ["const RESOLUTION_EVIDENCE = ["]
    for o in PRODUCTS["evidence_observations"]:
        out.append("  {")
        out.append(f"    id: {js(o['id'])},")
        out.append(f"    observation: {js(o['observation'])},")
        out.append(f"    interpretation: {js(o['interpretation'])},")
        out.append(f"    status: {js(o['status'])},")
        out.append(f"    source: {js(SOURCES[o['source_ids'][0]]['url'] if o.get('source_ids') else '')},")
        out.append(f"    sourceIds: {json.dumps(o.get('source_ids', []))},")
        out.append("  },")
    out.append("];")
    return "\n".join(out)


# --------------------------------------------------------------------------------- flags block
def gen_flags() -> str:
    out = ["const FLAGGED_ROWS = ["]
    for f in FLAGS["flags"]:
        ids = [i for i in f.get("source_ids", []) if i in SOURCES]
        out.append("  {")
        out.append(f"    item: {js(f['id'] + ' — ' + f['title'])},")
        out.append(f"    detail: {js(f['detail'])},")
        out.append(f"    severity: {js(f['severity'])},")
        out.append(f"    impact: {js(f['impact'])},")
        out.append(f"    actionRequired: {js(f['action_required'])},")
        out.append(f"    ledgerFlag: {js(f['id'])},")
        out.append(f"    ledgerUrl: {js('pages/flags.html#' + f['id'])},")
        out.append(f"    source: {js(SOURCES[ids[0]]['url'] if ids else '')},")
        out.append(f"    sourceIds: {json.dumps(ids)},")
        out.append("  },")
    out.append("];")
    return "\n".join(out)


def replace_block(text: str, name: str, body: str) -> str:
    begin = f"/* BEGIN GENERATED: {name} */"
    end = f"/* END GENERATED: {name} */"
    if begin not in text or end not in text:
        raise SystemExit(f"marker {name} missing from {DATA_JS}")
    i = text.index(begin)
    j = text.index(end) + len(end)
    return text[:i] + block(name, body) + text[j:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    text = DATA_JS.read_text(encoding="utf-8")
    new = text
    new = replace_block(new, "products", gen_products())
    new = replace_block(new, "specs", gen_specs())
    new = replace_block(new, "resolution-evidence", gen_resolution_evidence())
    new = replace_block(new, "flags", gen_flags())

    # Keep the dashboard's canonical flag count derived from the ledger (F-22/F-26 gate:
    # tools/validate_data.py::check_flag_count fails the build on any disagreement).
    count = len(FLAGS["flags"])
    new, n_sub = re.subn(
        r"const CANONICAL_FLAG_COUNT = \d+;",
        f"const CANONICAL_FLAG_COUNT = {count};",
        new,
        count=1,
    )
    if n_sub != 1:
        raise SystemExit(f"CANONICAL_FLAG_COUNT declaration missing from {DATA_JS}")

    if args.check:
        if new != text:
            print(f"{DATA_JS.relative_to(REPO)} is out of date — run: python3 tools/build_root_data.py")
            return 1
        print(f"{DATA_JS.relative_to(REPO)} is up to date")
        return 0

    DATA_JS.write_text(new, encoding="utf-8")
    print(f"wrote {DATA_JS.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
