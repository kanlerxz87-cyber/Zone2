#!/usr/bin/env python3
"""Negative tests for the D8 page-metadata check in tools/seo_audit.py.

D8 exists because S-04 ("Give every page its own title and meta description") is the only P1
row on the 2026-11-17 brief that was still open when this check was added. Measured on the
combined tree of 19 November 2026, 39 of the pages in `pages/` shared one description, four
pairs shared a title, and the whole `revalidation/` namespace plus the 404 page carried no
description at all. Those are the defects these cases inject.

A gate that has only ever passed is a claim, not a control. Each case below builds a small
synthetic tree, injects exactly one defect, and asserts that `metadata_problems()` names it.
The real repository tree is never modified.

Usage:
    python3 tools/test_seo_meta.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seo_audit import metadata_problems  # noqa: E402

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="description" content="{description}">
</head>
<body><h1>{title}</h1></body>
</html>
"""

NO_DESC = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
</head>
<body><h1>{title}</h1></body>
</html>
"""

NO_TITLE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="description" content="{description}">
</head>
<body><p>No title element at all.</p></body>
</html>
"""


def build(root: Path, files: dict[str, str]) -> list[Path]:
    rels = []
    for name, text in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        rels.append(Path(name))
    return rels


def base_tree(root: Path) -> dict[str, str]:
    return {
        "index.html": PAGE.format(title="Home", description="The home page of the fixture tree."),
        "guide.html": PAGE.format(title="A guide", description="A guide about a question buyers ask."),
        "about.html": PAGE.format(title="About", description="How the fixture tree was made."),
    }


CASES: list[tuple[str, dict[str, str], str]] = [
    (
        "a page with no meta description is named",
        {"broken.html": NO_DESC.format(title="A page without a description")},
        "D8 metadata: broken.html has no meta description",
    ),
    (
        "a page with no <title> is named",
        {"untitled.html": NO_TITLE.format(description="A description with no title element beside it.")},
        "D8 metadata: untitled.html has no <title>",
    ),
    (
        "two pages sharing a title are named",
        {"one.html": PAGE.format(title="Same title", description="First page, its own description."),
         "two.html": PAGE.format(title="Same title", description="Second page, its own description.")},
        "D8 metadata: title shared by 2 pages",
    ),
    (
        "two pages sharing a meta description are named",
        {"one.html": PAGE.format(title="First title", description="The same description on both pages."),
         "two.html": PAGE.format(title="Second title", description="The same description on both pages.")},
        "D8 metadata: meta description shared by 2 pages",
    ),
    (
        "a whitespace-only description counts as missing",
        {"blank.html": PAGE.format(title="Blank description", description="   ")},
        "D8 metadata: blank.html has no meta description",
    ),
]


def main() -> int:
    failures: list[str] = []

    # The control: an unmutated tree must produce no problem at all.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rels = build(root, base_tree(root))
        clean = metadata_problems(rels, root)
        print(f"  {'FIRED ' if not clean else 'MISSED'}  control: a clean tree reports nothing"
              + (f" -> {clean[0][:90]}" if clean else ""))
        if clean:
            failures.append("control: a clean tree reported a problem")

    for label, injected, expect in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = base_tree(root)
            files.update(injected)
            rels = build(root, files)
            problems = metadata_problems(rels, root)
            hit = any(p.startswith(expect) for p in problems)
            print(f"  {'FIRED ' if hit else 'MISSED'}  {label}" + (f"  -> {problems[0][:100]}" if problems else ""))
            if not hit:
                failures.append(label)

    print()
    if failures:
        print(f"{len(failures)} check(s) did not fire on the defect they exist to catch:")
        for f in failures:
            print("  ", f)
        return 1
    print(f"{len(CASES) + 1}/{len(CASES) + 1} negative tests fired as intended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
