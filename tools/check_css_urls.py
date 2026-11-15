#!/usr/bin/env python3
"""Fail the build when a stylesheet points at a file that is not there.

Why this exists. On 2026-11-15 the deployed site silently served system fonts for weeks because
`assets/css/style.css` wrote its @font-face URLs as `url("assets/fonts/…")`. A CSS url() resolves
against the stylesheet's own location, so the browser requested `assets/css/assets/fonts/…`, which
never existed. Every gate in the repo passed: the link checker parses HTML only, and a missing font
degrades silently rather than erroring. Session 1b839f87 repaired the paths (PR #89) and logged the
missing check as `1B-2`; this is that check.

What it does. For every tracked *.css file, resolve every relative url() against that stylesheet's
directory and fail if the target is not a file. Absolute URLs (http://, https://, //, data:) are
skipped: they are not this repository's to guarantee, and the project deliberately ships no
third-party stylesheet.

Negative-tested: appending `url("nope/font.woff2")` to any stylesheet makes this exit 1.

Usage:
    python3 tools/check_css_urls.py
    python3 tools/check_css_urls.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".local", ".cache"}
URL = re.compile(r"""url\(\s*(?P<q>['"]?)(?P<u>[^'")]+)(?P=q)\s*\)""", re.I)


COMMENT = re.compile(r"/\*.*?\*/", re.S)


def strip_comments(text: str) -> str:
    """Blank out CSS comments, keeping newlines so reported line numbers stay correct.

    A comment that documents a path (e.g. `url("../../assets/fonts/…")`) is not a reference and must
    not be checked; without this the gate failed on main for a comment, not a broken link (R86-09).
    """
    return COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def stylesheets() -> list[Path]:
    out = []
    for p in sorted(REPO.rglob("*.css")):
        if SKIP_DIRS.intersection(p.relative_to(REPO).parts):
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    broken = []
    checked = 0
    for css in stylesheets():
        text = strip_comments(css.read_text(encoding="utf-8", errors="ignore"))
        for m in URL.finditer(text):
            u = m.group("u").strip()
            if u.startswith(("http://", "https://", "//", "data:", "#")):
                continue
            checked += 1
            target = (css.parent / u.split("?")[0].split("#")[0]).resolve()
            if not target.is_file():
                line = text[: m.start()].count("\n") + 1
                broken.append({
                    "file": str(css.relative_to(REPO)),
                    "line": line,
                    "url": u,
                    "resolved_to": str(target),
                })

    if args.json:
        print(json.dumps({"ok": not broken, "references_checked": checked,
                          "stylesheets": len(stylesheets()), "broken": broken}, indent=2))
    else:
        for b in broken:
            print(f"BROKEN {b['file']}:{b['line']}  url({b['url']!r}) -> {b['resolved_to']} does not exist")
        print(f"{len(stylesheets())} stylesheets · {checked} local url() references · {len(broken)} broken")
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
