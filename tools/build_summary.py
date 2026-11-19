#!/usr/bin/env python3
"""Compatibility entry point for the current generated `summary.html`.

`tools/build_front.py` owns the publication summary and its source-derived content. This
wrapper remains because the Pages workflow already has a summary freshness step; delegating
to the canonical builder prevents the old three-link ledger page from competing with the
current five-submission summary.

Usage:
    python3 tools/build_summary.py           # write summary.html
    python3 tools/build_summary.py --check   # fail if the committed page is stale
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_front  # noqa: E402

OUT = ROOT / "summary.html"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    facts, board = build_front.load()
    expected = build_front.build_current_summary(facts, board)
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != expected:
            print("summary.html: stale — run `python3 tools/build_front.py`")
            return 1
        print("summary.html: current executive summary")
        return 0
    OUT.write_text(expected, encoding="utf-8")
    print("wrote summary.html (current executive summary)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
