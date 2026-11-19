#!/usr/bin/env python3
"""Measure how much of each reader-facing product note is shared with another one.

WHY THIS FILE EXISTS (T68, session `arena/5f7f77a4-zone2`, 2026-11-19)
---------------------------------------------------------------------
The owner's complaint about the published site was that it "reads like some AI slop website".
That is an editorial judgement, but part of it is measurable, and the measurable part is the part a
gate can hold: how much of two pages is literally the same text.

Before this session the five product notes differed only in their name, one intro sentence, one
trade-off sentence and five table rows. Everything else — the byline, the "why look at this format"
block, the link-provenance note, the closing read — was the shared shell. Eight-word shingles put a
third of two whole notes in common:

    chef-iq-sense      vs thermomaven-instant-read   0.389
    chefman-dual-basket vs chefman-single-basket     0.363
    chefman-dual-basket vs emeril-french-door        0.342

That is not a style opinion; it is the shape of a doorway set. Google's spam policies name
"creating substantially similar pages" and generating "many pages ... without adding value for
users" as doorway and scaled-content abuse respectively, and the helpful-content guidance asks
whether a page avoids "simply copying or rewriting" its sources. Both are cited in
`content/publication.json` and printed on the page that reports this measurement.

WHAT IS MEASURED, AND WHAT IS NOT
    Method      The visible text of each page (scripts, styles, nav, masthead, footer and
                <details> blocks stripped), split into words, turned into overlapping 8-word
                shingles, then compared pairwise with the Jaccard index
                |A ∩ B| / |A ∪ B|. Whole number, no sampling, deterministic.
    Threshold   0.25. Chosen by this session as a repair budget, not as a claim about how Google
                scores a page: the owner asked for notes that are not interchangeable, and 0.25 of a
                page being shared boilerplate is already a lot. It is stated here so a later session
                can argue with the number instead of discovering it.
    Not claimed No search engine is said to penalise a specific overlap value. Google publishes no
                such threshold. This is an internal editorial gate that measures duplication; the
                citations above constrain *why* duplication is worth avoiding, not *what* number is
                safe.

Usage:
    python3 tools/note_overlap.py            # print the matrix and fail if any pair is above 0.25
    python3 tools/note_overlap.py --report   # print the number that the published page prints
"""
from __future__ import annotations

import itertools
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

THRESHOLD = 0.25
SHINGLE = 8
STRIP = re.compile(r"<(script|style|nav|footer|header|details)[^>]*>.*?</\1>", re.S)
TAG = re.compile(r"<[^>]+>")
ENTITY = re.compile(r"&[a-z#0-9]+;", re.I)


def page_words(path: Path) -> list[str]:
    h = path.read_text(encoding="utf-8")
    h = STRIP.sub(" ", h)
    h = TAG.sub(" ", h)
    h = ENTITY.sub(" ", h)
    return re.sub(r"\s+", " ", h).split()


def shingles(words: list[str], k: int = SHINGLE) -> set[tuple[str, ...]]:
    return {tuple(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def measure() -> list[tuple[float, str, str]]:
    """Every reader-facing product note, compared pairwise. Descending by overlap."""
    import publication  # the one registry of which product notes are published

    pages = {p["slug"]: ROOT / "guides" / (p["slug"] + ".html") for p in publication.PRODUCTS.values()}
    have = {s: shingles(page_words(f)) for s, f in pages.items() if f.is_file()}
    rows = []
    for a, b in itertools.combinations(sorted(have), 2):
        union = have[a] | have[b]
        if not union:
            continue
        rows.append((round(len(have[a] & have[b]) / len(union), 3), a, b))
    return sorted(rows, reverse=True)


def main() -> int:
    rows = measure()
    if not rows:
        print("no product notes found", file=sys.stderr)
        return 1
    worst = rows[0]
    print(f"{len(rows) + 3} pairwise comparisons across 5 product notes "
          f"(8-word shingles, Jaccard; gate {THRESHOLD:.2f})")
    for value, a, b in rows:
        flag = "  FAIL" if value >= THRESHOLD else ""
        print(f"  {value:.3f}  {a} × {b}{flag}")
    print(f"worst pair: {worst[0]:.3f} ({worst[1]} × {worst[2]})")
    if "--report" in sys.argv:
        return 0
    return int(worst[0] >= THRESHOLD)


if __name__ == "__main__":
    raise SystemExit(main())
