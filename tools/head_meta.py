#!/usr/bin/env python3
"""One implementation of the head-metadata contract: canonical URL + Open Graph identity.

T42 (session `5d6d2254`, 2026-11-15). Before this module, only `marketing/` carried a
`<link rel="canonical">` (18 of 78 published pages), and it built the tags inline in
`tools/build_marketing.py`. The other 60 pages — the root views, `journal/`, the 39 evidence subpages in
`pages/` and the 4 in `decisions/` — had none, so the same page was addressable both as `…/journal/` and
`…/journal/index.html`, and a link preview had no `og:url` or `og:type` to read.

This module exists so the four generators and the hand-written pages cannot disagree about what the
canonical form of a URL is: every caller passes the page's path **relative to the repository**, and the
`tools/build_sitemap.py --audit` gate fails the build if the emitted value drifts from the path.

What is deliberately *not* here: `og:image`, `twitter:card`, and `schema.org` markup beyond what
`marketing/` already emits. The site publishes no product imagery because the rights question is still
open (Q-10 on the questions register, DS-11 on the improvement board), and DS-07 records the decision not
to add Product/Review markup while there is no genuine review. An `og:image` tag pointing at nothing would
be the kind of placeholder this project refuses to ship.
"""
from __future__ import annotations

from html import escape

# The public address of this deployment (GitHub Pages, project page). Read from the live site and already
# hard-coded by tools/build_site.py, build_root_views.py and build_marketing.py; a custom domain is the
# owner's open decision (DS-04), and when it lands this constant plus those three are the whole change.
BASE = "https://kanlerxz87-cyber.github.io/Zone2/"


def url_for(rel_path: str) -> str:
    """The canonical URL of a published page, from its repository-relative path.

    One special case, shared with the sitemap generator: the repository's root `index.html` is canonical
    at the bare site URL (`…/Zone2/`), because that is the URL `tools/build_sitemap.py` advertises and the
    one GitHub Pages serves at the root. A canonical that disagrees with the indexed URL is the defect
    `tools/seo_audit.py` reports as D7. Nested `index.html` files keep their file form, exactly as the
    sitemap lists them.
    """
    rel = rel_path.strip("/")
    if rel in ("", "index.html"):
        return BASE
    return BASE + rel


def head_block(rel_path: str, *, title: str, description: str,
               site_name: str, page_type: str = "website") -> str:
    """The lines a page needs so a crawler and a link preview agree about which URL it is.

    `title` and `description` are passed in rather than invented: each caller already has the page's own
    display title and description, and copying them here is a transcription, not a claim.
    """
    url = url_for(rel_path)
    t, d = escape(title, quote=True), escape(description, quote=True)
    return (
        f'<link rel="canonical" href="{escape(url, quote=True)}">\n'
        f'<meta property="og:type" content="{escape(page_type, quote=True)}">\n'
        f'<meta property="og:site_name" content="{escape(site_name, quote=True)}">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta property="og:url" content="{escape(url, quote=True)}">'
    )
