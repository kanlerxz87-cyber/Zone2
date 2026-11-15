#!/usr/bin/env python3
"""One-shot migration: give every hand-authored root page the new chrome.

Run once (2026-11-15, session bdbe382b). It rewrites the sidebar, inserts the sticky
topbar and the skip link, wraps the body in .content, promotes the page heading to an
<h1> and adds a meta description where one was missing.

Idempotent: a page that already carries the new chrome is left alone.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))

from root_chrome import esc, sidebar_html, topbar_html  # noqa: E402

# filename -> (page title for the topbar, meta description)
PAGES = {
    "products.html": (
        "Products",
        "The three supplied affiliate links and the three Amazon destinations each one resolves to, "
        "with every specification row linked to the official page it was read from.",
    ),
    "analysis.html": (
        "Analysis",
        "Niche, pricing, competition and commission-potential analysis for the three resolved "
        "destinations, with each figure traced to an official source or left blank and flagged.",
    ),
    "content.html": (
        "Content",
        "The SEO content plan: which articles, comparisons and buying guides exist, which are "
        "published, and what is blocked until product identity is confirmed.",
    ),
    "compliance.html": (
        "Compliance",
        "The Amazon Associates Operating Agreement and Program Policies rules this platform is "
        "built to satisfy, each with its official source link.",
    ),
    "tracking.html": (
        "Tracking",
        "How Special Links, campaign keys, disclosure placement and first-party click counting "
        "work together, with the official rule behind each control.",
    ),
    "flagged.html": (
        "Flagged for review",
        "Every irregularity and every value that no official source confirms, with the source "
        "links needed to review each one.",
    ),
    "404.html": (
        "Page not found",
        "The page you requested does not exist on this site.",
    ),
}

SIDEBAR_RE = re.compile(r'<aside class="sidebar">.*?</aside>', re.S)


def migrate(name: str, title: str, description: str) -> bool:
    path = REPO / name
    text = path.read_text(encoding="utf-8")
    original = text

    if 'class="brand"' not in text:  # not migrated yet
        text = SIDEBAR_RE.sub(lambda _m: sidebar_html(name), text, count=1)

    if '<div class="content">' not in text:
        # wrap the body of <main> in .content, then put the sticky topbar above it so the
        # bar spans the full width of the page rather than the padded content column.
        text = text.replace('<main class="main">', '<main class="main">\n  <div class="content">', 1)
        text = text.replace("  </main>", "  </div>\n  </main>", 1)

    if "<header class=\"topbar\">" not in text:
        text = re.sub(
            r'<main class="main"([^>]*)>',
            lambda m: f'<main class="main"{m.group(1)}>\n    ' + topbar_html(title),
            text,
            count=1,
        )

    if '<a class="skip"' not in text:
        text = text.replace("<body>", '<body>\n<a class="skip" href="#main">Skip to content</a>', 1)
    if 'id="main"' not in text:
        text = text.replace('<main class="main">', '<main class="main" id="main">', 1)

    # promote the page heading to an <h1>
    text = re.sub(r'<div class="page-head">\s*<h2>', '<div class="page-head">\n      <h1>', text)
    text = re.sub(r'<h2>([^<]*?)</h2>\s*<p>', r'<h1>\1</h1>\n      <p>', text, count=1)

    if 'name="description"' not in text:
        text = text.replace(
            '<meta name="viewport"',
            f'<meta name="description" content="{esc(description)}">\n<meta name="viewport"',
            1,
        )

    if text != original:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> int:
    changed = [name for name, (title, desc) in PAGES.items() if migrate(name, title, desc)]
    print({"migrated": changed})
    return 0


if __name__ == "__main__":
    sys.exit(main())
