#!/usr/bin/env python3
"""Generate the root `sitemap.xml` from the pages actually published in this repository.

Why a generator instead of the hand-typed list this replaces: the hand-typed file had drifted to
16 of 115 published pages (86% of the site absent), including every page a search engine would
need first — `marketing/index.html`, `playbook.html` and all 38 `pages/*.html` findings pages.
Nothing rebuilt it, so nothing could notice. A sitemap that nobody regenerates is a claim about
the site that stops being true silently, which is the exact failure mode this repository's other
gates exist to prevent. Here the file is derived from the tree, and `--check` fails the build if
the committed copy disagrees with a fresh derivation.

WHAT COUNTS AS PUBLISHED
    Every `*.html` file in the repository, minus the exclusions below. GitHub Pages serves this
    repository's working tree verbatim (`.github/workflows/pages.yml` uploads `path: .`), so
    "present in the tree" is literally "reachable at a URL" — the only definition a sitemap can
    be held to.

EXCLUSIONS (each one deliberate, none silent)
    `404.html`, and any file with that basename  Error documents. They are not destinations; listing
                          one invites a crawler to index a failure. The match is on the basename, so
                          `research-hub/404.html` is excluded too — an exact-path rule missed it on the
                          first run. `custom_404` is enabled on the Pages site (verified via the
                          Pages API).
    `tools/`, `tests/`, `content/`   build scripts, fixtures and content templates. No `.html`
                          currently lives there; the exclusion keeps a future stray file from
                          being advertised.

NOT EMITTED, ON PURPOSE
    `<lastmod>`  The sitemap protocol makes it optional. This repository has no reliable per-file
                 change date: `actions/checkout` fetches a single commit, so `git log` cannot see a
                 file's real history in CI, and a date typed by hand is exactly the class of
                 unverified value every other gate in this repo refuses to publish. Omitting the
                 field is correct; inventing it would be a false claim. When a real timestamp
                 source exists, add it here rather than to the XML by hand.
    `<changefreq>` and `<priority>`  Google documents both as ignored. Publishing them would be
                 decoration. See `docs/verification-156aae86.md` for the cited pages.

Usage:
    python3 tools/build_sitemap.py            # write sitemap.xml
    python3 tools/build_sitemap.py --check    # exit 1 if the committed file differs
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITEMAP = REPO / "sitemap.xml"
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/"

#: Directories whose HTML is never a published destination. See the module docstring.
EXCLUDED_DIRS = ("tools", "tests", "content")

#: Files that exist in the tree but are not destinations, matched on the **basename** so that a
#: nested error page is caught as well as the root one. `research-hub/404.html` is a "Page not found"
#: document; an exact-path set missed it, and the first generated sitemap advertised it — listing an
#: error page invites a crawler to index a failure.
EXCLUDED_FILES = {"404.html"}

#: `sitemap.xml` element order, per https://www.sitemaps.org/protocol.html — `<loc>` is required and
#: every other element is optional. Emitting only `<loc>` keeps the file inside the protocol.
HEADER = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
)
FOOTER = "</urlset>\n"


def published_pages() -> list[str]:
    """Every published HTML page, as a repository-relative POSIX path, deterministically ordered."""
    pages: list[str] = []
    for path in REPO.rglob("*.html"):
        rel = path.relative_to(REPO)
        if any(part.startswith(".") for part in rel.parts):
            continue  # .git and any dot-directory
        if rel.parts[0] in EXCLUDED_DIRS:
            continue
        if rel.name in EXCLUDED_FILES:
            continue
        pages.append(rel.as_posix())
    # Directory-style ordering keeps each namespace together and the root pages first, which makes
    # the diff readable when a page is added.
    return sorted(pages, key=lambda p: (p.count("/"), p))


def url_for(rel: str) -> str:
    """Map a repository-relative path onto its live URL."""
    if rel == "index.html":
        return LIVE
    return LIVE + rel


def render() -> str:
    pages = published_pages()
    if not pages:
        raise SystemExit("no published pages found — refusing to write an empty sitemap")
    body = "".join(f"  <url><loc>{url_for(p)}</loc></url>\n" for p in pages)
    return HEADER + body + FOOTER


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare against the committed file")
    args = ap.parse_args()

    doc = render()

    if args.check:
        current = SITEMAP.read_text(encoding="utf-8") if SITEMAP.is_file() else ""
        if current == doc:
            print(f"sitemap.xml is current ({len(published_pages())} URLs)")
            return 0
        committed = current.count("<url>")
        expected = doc.count("<url>")
        print(
            f"sitemap.xml drifted from the published tree: committed {committed} URLs, "
            f"a fresh derivation has {expected}.",
            file=sys.stderr,
        )
        if committed != expected:
            print(
                "  Re-run: python3 tools/build_sitemap.py",
                file=sys.stderr,
            )
        else:
            print(
                "  Same URL count but different content or ordering — re-run the generator.",
                file=sys.stderr,
            )
        tmp = Path(tempfile.mkdtemp(prefix="z2sitemap-")) / "sitemap.xml"
        tmp.write_text(doc, encoding="utf-8")
        print(f"  Fresh copy written to {tmp} for diffing.", file=sys.stderr)
        return 1

    SITEMAP.write_text(doc, encoding="utf-8")
    print(f"wrote sitemap.xml — {len(published_pages())} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
