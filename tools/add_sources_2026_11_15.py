#!/usr/bin/env python3
"""Append the source records verified on 2026-11-15 to ledger/sources.json.

Why this script exists
----------------------
The Suggestions register (T29) and the Open-questions register (T30) cite the same
official documents the rest of the site cites, so they cite the SAME ids rather than
carrying a private copy of the URLs. That keeps one source register for the whole
site and lets `tools/build_root_views.py` publish every new source on sources.html.

Every record below was read on 2026-11-15 by opening the page; the `used_for` text
states what the page actually says that this repository relies on. Nothing is
inferred from memory.

Idempotent: re-running it changes nothing, so it is safe to run after a merge that
also touched the register.

Usage:
    python3 tools/add_sources_2026_11_15.py           # add any missing records
    python3 tools/add_sources_2026_11_15.py --check   # fail if a record is missing
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger" / "sources.json"

NEW = [
    {
        "id": "S38",
        "publisher": "Google (Search Central documentation)",
        "kind": "official",
        "title": "Spam policies for Google web search",
        "url": "https://developers.google.com/search/docs/essentials/spam-policies",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "scaled content abuse - 'creating large amounts of unoriginal content that provides little to no value to users, no matter how it's created'",
            "thin affiliation - affiliate pages whose product descriptions and reviews are copied from the merchant with no original content; the page lists 'product comparisons' and 'rigorous testing and ratings' as examples of added value",
            "site reputation policy - 'Using affiliate links throughout a page, with links treated appropriately' is listed as NOT inconsistent, while an 'unauthored affiliate article not integrated in publication' is likely to be actioned",
        ],
    },
    {
        "id": "S39",
        "publisher": "Google (Search Central documentation)",
        "kind": "official",
        "title": "Creating helpful, reliable, people-first content",
        "url": "https://developers.google.com/search/docs/fundamentals/creating-helpful-content",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "the self-assessment questions this project uses to keep the marketing pages from reading as thin affiliate copy",
            "'Does the main heading or page title provide a descriptive, helpful summary of the content?'",
            "'Avoid creating search engine-first content' - the basis for the editorial standard in the Suggestions register",
        ],
    },
    {
        "id": "S40",
        "publisher": "Google (Search Central documentation)",
        "kind": "official",
        "title": "Build and submit a sitemap",
        "url": "https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "the XML sitemap format and the sitemap best practices this project would publish a sitemap.xml against",
            "the documented route to submitting a sitemap in Search Console and in robots.txt",
        ],
    },
    {
        "id": "S41",
        "publisher": "USDA Food Safety and Inspection Service (United States Department of Agriculture)",
        "kind": "official",
        "title": "Air Fryers and Food Safety",
        "url": "https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/air-fryers-and-food-safety",
        "page_stated_update": "2024-06-24",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "air fryers are 'essentially countertop convection ovens' that 'cook food faster and consume less energy'",
            "'Foods generally require 5 to 25 minutes of cooking at a temperature range of 350 degrees F to 400 degrees F'",
            "do not overcrowd the basket; cook in batches rather than all at once",
            "safe minimum internal temperatures: fish 145 F, whole cuts of beef/pork/veal/lamb 145 F with a 3-minute rest, ground meat 160 F, poultry 165 F",
            "do NOT air fry raw, stuffed, breaded chicken breast products",
            "refrigerate leftovers within 2 hours; the Danger Zone is 40 F to 140 F",
        ],
    },
    {
        "id": "S42",
        "publisher": "FoodSafety.gov (U.S. Department of Health and Human Services)",
        "kind": "official",
        "title": "Cook to a Safe Minimum Internal Temperature",
        "url": "https://www.foodsafety.gov/food-safety-charts/safe-minimum-internal-temperatures",
        "page_stated_update": "2024-11-21",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "the safe minimum internal temperature chart used by the cooking-safety article: beef/pork/veal/goat/lamb steaks, roasts and chops 145 F (63 C) with a 3-minute rest; ground meat and sausage 160 F (71 C); poultry 165 F (74 C); casseroles 165 F (74 C); raw ham 145 F (63 C) with a 3-minute rest; precooked ham to reheat 165 F (74 C); leftovers 165 F (74 C); seafood 145 F (63 C)",
            "'Always use a food thermometer to check whether meat has reached a safe minimum internal temperature'",
        ],
    },
    {
        "id": "S43",
        "publisher": "Google (Search Central documentation)",
        "kind": "official",
        "title": "Article (Article, NewsArticle, BlogPosting) structured data",
        "url": "https://developers.google.com/search/docs/appearance/structured-data/article",
        "accessed_utc": "2026-11-15",
        "used_for": [
            "the JSON-LD Article type this project would add to editorial pages so the headline, author and date are machine-readable",
            "the author-markup requirement that ties an article to a named, identifiable author",
        ],
    },
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    doc = json.loads(LEDGER.read_text(encoding="utf-8"))
    sources = doc["sources"]
    by_id = {s["id"]: s for s in sources}

    missing = [rec for rec in NEW if rec["id"] not in by_id]
    if args.check:
        if missing:
            print("MISSING: " + ", ".join(r["id"] for r in missing))
            return 1
        print(f"all {len(NEW)} records present")
        return 0

    if missing:
        sources.extend(missing)
        doc["note"] = doc["note"].rstrip() + (
            " S38-S43 were added on 2026-11-15 by session 6cc428f1: three Google Search Central documents "
            "on how a site should be written and indexed, and two United States government food-safety "
            "documents (USDA FSIS and FoodSafety.gov) used to source the cooking-safety content. Each record "
            "states what the page actually says that this repository relies on."
        )
        LEDGER.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"added {len(missing)} source records: " + ", ".join(r["id"] for r in missing))
    else:
        print("nothing to add - all records already present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
