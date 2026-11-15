#!/usr/bin/env python3
"""Shared chrome for the root (repository-root) pages.

One navigation model for every page in the root namespace, so a reader can reach any
surface from any surface. The design refresh (session bdbe382b, 2026-11-15) replaced the
old flat sidebar with a grouped one and added the decision-support entries.

Imported by tools/build_decisions.py and tools/build_root_views.py, and used by the
one-shot migration script tools/migrate_root_chrome_2026_11_15.py.
"""

from __future__ import annotations

import html

SITE_NAME = "Zone2"  # never an Amazon mark - Participation Requirements rule R-11

NAV = [
    ("index.html", "Dashboard"),
    ("summary.html", "Executive summary"),
    ("products.html", "Products"),
    ("analysis.html", "Analysis"),
    ("content.html", "Content"),
    ("marketing/index.html", "Published copy"),
    ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking"),
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Questions"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for review"),
]

NAV_GROUPS = [
    ("Site", ["index.html", "summary.html"]),
    ("Research", ["products.html", "analysis.html", "content.html", "marketing/index.html"]),
    ("Compliance", ["compliance.html", "tracking.html"]),
    ("Decide", ["suggestions.html", "questions.html"]),
    ("Evidence", ["verification.html", "sources.html", "flagged.html"]),
]

LABELS = dict(NAV)


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def nav_groups_html(active: str) -> str:
    """The grouped sidebar navigation (new chrome)."""
    groups = []
    for label, hrefs in NAV_GROUPS:
        items = []
        for href in hrefs:
            cls = " active" if href == active else ""
            items.append(f'<a class="nav-link{cls}" href="{esc(href)}">{esc(LABELS[href])}</a>')
        groups.append(
            f'<div class="nav-group"><span class="nav-label">{esc(label)}</span>{"".join(items)}</div>'
        )
    return "\n      ".join(groups)


def nav_flat_html(active: str) -> str:
    """The flat navigation used by the generated evidence views."""
    out = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        out.append(f'<a href="{esc(href)}"{cls}>{esc(label)}</a>')
    return "".join(out)


def sidebar_html(active: str) -> str:
    return f"""<aside class="sidebar">
    <a class="brand" href="index.html"><span class="brand-mark">Z</span><span>{esc(SITE_NAME)}<small>Affiliate intelligence</small></span></a>
    <nav class="nav" aria-label="Primary">
      {nav_groups_html(active)}
    </nav>
    <div class="sidebar-bottom">
      <div class="status-dot"></div>
      <div><strong>Verified data only</strong><small>every row links to its source</small></div>
    </div>
  </aside>"""


def topbar_html(title: str) -> str:
    return f"""<header class="topbar">
      <div class="crumb"><a href="index.html">{esc(SITE_NAME)}</a> <span>/</span> <strong>{esc(title)}</strong></div>
      <div class="top-right"><span class="live-tag"><i></i> Live on GitHub Pages</span><a class="chip" href="index.html">Dashboard</a></div>
    </header>"""
