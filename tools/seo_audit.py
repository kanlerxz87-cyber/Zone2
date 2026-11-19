#!/usr/bin/env python3
"""Discoverability audit: the checks that were missing when the root sitemap drifted to 16 of 115 pages.

`tools/audit_site.py` already proves that every published page is reachable *by a link*. Nothing proved
that a page is reachable *by a crawler*, and that is a different property. A page can be perfectly
linked from the footer and still be invisible to search: absent from the sitemap, excluded by a robots
meta tag, served from a path robots.txt disallows, or declaring a canonical URL that points somewhere
else. Every one of those failures is silent — the site looks fine to a human and earns nothing.

This gate fails on each of them. Nothing here is a judgement call about content quality; all of it is
mechanical and checkable.

CHECKS
  D1  sitemap coverage      every published page appears in root `sitemap.xml`
  D2  sitemap integrity     every `<loc>` is absolute, on this site's own origin, and resolves to a
                            file that exists; no URL appears twice; the XML parses
  D3  robots.txt            present, allows crawling of everything the sitemap advertises, and
                            advertises the root sitemap
  D4  robots meta           no published page carries a `noindex` directive while appearing in the
                            sitemap. `nofollow` is reported but not failed: it is sometimes deliberate.
  D5  marketing sitemap     `marketing/sitemap.xml` covers every `marketing/**` page (it is generated
                            from its own page registry, so this is the cross-check that the registry
                            and the tree agree)
  D6  favicon               every root-level page references an icon that exists — a browser asks for
                            `/favicon.ico` by default and Pages answers 404 when none is linked
  D7  canonical (report)    pages whose `<link rel="canonical">` points at a different path than the
                            page itself. Reported only, because the duplicate-content decision is an
                            owner decision recorded on the suggestions board (MQ-08 / DS-12), and the
                            marketing set is internally consistent.
  D8  page metadata        every published page carries its own `<title>` and its own
                            `<meta name="description">`, and no two published pages share either one.
                            S-04 is the brief's only P1 row that was still open: 39 of the pages in
                            `pages/` shared one description, four of them shared a title, and the
                            `revalidation/` namespace and the 404 page carried no description at all.
                            Google builds the search snippet from the description, so a shared one means
                            two pages competing for the same query instead of each earning its own.

Exit code 1 on any D1–D6 or D8 failure. D7 never fails.

Usage:
    python3 tools/seo_audit.py
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
# One source of truth for "what counts as a published page". If these ever diverge, this gate
# would pass a sitemap that the generator considers incomplete — the exact drift it exists to stop.
from build_sitemap import EXCLUDED_DIRS, EXCLUDED_FILES, indexable_pages  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/"
ORIGIN = "https://kanlerxz87-cyber.github.io"


def published_pages() -> list[Path]:
    pages: list[Path] = []
    for path in REPO.rglob("*.html"):
        rel = path.relative_to(REPO)
        if any(part.startswith(".") for part in rel.parts):
            continue
        if rel.parts[0] in EXCLUDED_DIRS:
            continue
        if rel.name in EXCLUDED_FILES:  # basename match, so nested error pages are excluded too
            continue
        pages.append(rel)
    return sorted(pages, key=lambda p: p.as_posix())


def live_url(rel: Path) -> str:
    s = rel.as_posix()
    return LIVE if s == "index.html" else LIVE + s


class Refs(HTMLParser):
    """Collect the head-level signals this gate cares about."""

    def __init__(self) -> None:
        super().__init__()
        self.robots: list[str] = []
        self.canonical: list[str] = []
        self.icons: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        if tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.robots.append((a.get("content") or "").lower())
        if tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "canonical" in rel and a.get("href"):
                self.canonical.append(a["href"])
            if ("icon" in rel or "shortcut" in rel) and a.get("href"):
                self.icons.append(a["href"])


TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)
DESCRIPTION_RE = re.compile(
    r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", re.S | re.I
)


def metadata_problems(pages: list[Path], root: Path) -> list[str]:
    """D8: every published page must have its own title and its own meta description.

    Kept as a separate function so tools/test_seo_meta.py can drive it over a synthetic tree
    and prove that each failure mode actually fires. A gate that has only ever passed is a
    claim, not a control.
    """
    problems: list[str] = []
    titles: dict[str, list[str]] = {}
    descriptions: dict[str, list[str]] = {}
    for rel in pages:
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        name = rel.as_posix()
        title_match = TITLE_RE.search(text)
        title = title_match.group(1).strip() if title_match else ""
        desc_match = DESCRIPTION_RE.search(text)
        description = desc_match.group(1).strip() if desc_match else ""
        if not title:
            problems.append(f"D8 metadata: {name} has no <title>")
        else:
            titles.setdefault(title, []).append(name)
        if not description:
            problems.append(f"D8 metadata: {name} has no meta description")
        else:
            descriptions.setdefault(description, []).append(name)
    for title, names in sorted(titles.items()):
        if len(names) > 1:
            problems.append(
                f"D8 metadata: title shared by {len(names)} pages: {title[:70]!r} — "
                + ", ".join(names)
            )
    for description, names in sorted(descriptions.items()):
        if len(names) > 1:
            problems.append(
                f"D8 metadata: meta description shared by {len(names)} pages: {description[:70]!r} — "
                + ", ".join(names[:8])
                + (f" (+{len(names) - 8} more)" if len(names) > 8 else "")
            )
    return problems


def parse_sitemap(path: Path) -> list[str]:
    """Return `<loc>` values; raises on malformed XML."""
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    return [el.text.strip() for el in root.iter(f"{ns}loc") if el.text and el.text.strip()]


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []

    pages = published_pages()
    page_urls = {live_url(p): p for p in pages}

    # ---- D1 / D2: root sitemap -------------------------------------------------------------
    sitemap = REPO / "sitemap.xml"
    if not sitemap.is_file():
        problems.append("D1 sitemap.xml: missing")
        locs: list[str] = []
    else:
        try:
            locs = parse_sitemap(sitemap)
        except ET.ParseError as exc:
            problems.append(f"D2 sitemap.xml: does not parse as XML ({exc})")
            locs = []

    seen: set[str] = set()
    for loc in locs:
        if not loc.startswith("http"):
            problems.append(f"D2 sitemap.xml: non-absolute <loc> {loc!r}")
            continue
        if not loc.startswith(LIVE.rstrip('/')):
            # A sitemap may only reference URLs on the host that serves it. Anything else is
            # either another property or a typo, and a search engine will reject it.
            if not loc.startswith(ORIGIN):
                problems.append(f"D2 sitemap.xml: off-origin <loc> {loc!r}")
                continue
        if loc in seen:
            problems.append(f"D2 sitemap.xml: duplicate <loc> {loc!r}")
        seen.add(loc)
        if loc.startswith(LIVE.rstrip('/')) and loc not in page_urls:
            problems.append(f"D2 sitemap.xml: <loc> {loc!r} has no corresponding file")

    wanted = {live_url(Path(rel)) for rel in indexable_pages()}
    extra = seen - wanted
    if extra:
        problems.append("D1 sitemap advertises non-reader/archive URLs: " + ", ".join(sorted(extra)))
    missing = sorted(wanted - seen)
    if missing:
        preview = ", ".join(m.replace(LIVE, "/") for m in missing[:6])
        more = f" (+{len(missing) - 6} more)" if len(missing) > 6 else ""
        problems.append(
            f"D1 sitemap coverage: {len(missing)} of {len(page_urls)} indexable reader pages absent — {preview}{more}"
        )

    # ---- D3: robots.txt --------------------------------------------------------------------
    robots = REPO / "robots.txt"
    if not robots.is_file():
        problems.append("D3 robots.txt: missing")
    else:
        text = robots.read_text(encoding="utf-8")
        disallow_all = re.search(r"^\s*Disallow:\s*/\s*$", text, re.M | re.I)
        if disallow_all:
            problems.append("D3 robots.txt: contains a blanket `Disallow: /`, which blocks the whole site")
        for ns_dir in ("marketing", "pages", "journal", "decisions"):
            if re.search(rf"^\s*Disallow:\s*/?{ns_dir}", text, re.M | re.I):
                problems.append(f"D3 robots.txt: disallows `{ns_dir}/`, which the sitemap advertises")
        if LIVE + "sitemap.xml" not in text:
            problems.append(f"D3 robots.txt: does not advertise {LIVE}sitemap.xml")

    # ---- D4 / D6 / D7: per-page head signals ----------------------------------------------
    noindex_in_sitemap: list[str] = []
    missing_icons: list[str] = []
    canonical_mismatch: list[str] = []

    for rel in pages:
        abs_path = REPO / rel
        parser = Refs()
        parser.feed(abs_path.read_text(encoding="utf-8", errors="replace"))

        if any("noindex" in r for r in parser.robots):
            if live_url(rel) in seen:
                noindex_in_sitemap.append(rel.as_posix())

        # D6 applies to the root-level pages: every other namespace resolves its icon relative to
        # itself and is checked by the generic link gate in CI. The root pages are the ones a
        # visitor lands on first, and a 404 there is the visible one.
        if len(rel.parts) == 1:
            if not parser.icons:
                missing_icons.append(rel.as_posix() + " (no icon link)")
            else:
                for href in parser.icons:
                    if href.startswith(("http", "//", "data:")):
                        continue
                    if not (abs_path.parent / href).resolve().is_file():
                        missing_icons.append(f"{rel.as_posix()} (icon target missing: {href})")

        for href in parser.canonical:
            expected = live_url(rel)
            if href.rstrip("/") != expected.rstrip("/"):
                canonical_mismatch.append(f"{rel.as_posix()} -> {href}")

    if noindex_in_sitemap:
        problems.append(
            "D4 robots meta: page is listed in sitemap.xml but declares noindex — "
            + ", ".join(noindex_in_sitemap)
        )
    if missing_icons:
        problems.append(
            f"D6 favicon: {len(missing_icons)} root page(s) without a resolvable icon — "
            + ", ".join(missing_icons)
        )
    for item in canonical_mismatch:
        notes.append(f"D7 canonical points elsewhere: {item}")

    # ---- D8: every published page has its own title and its own meta description -----------
    d8_problems = metadata_problems(pages, REPO)
    problems.extend(d8_problems)

    # ---- D5: marketing/sitemap.xml must cover marketing/** ---------------------------------
    m_sitemap = REPO / "marketing" / "sitemap.xml"
    m_pages = [p for p in pages if p.parts[0] == "marketing"]
    if m_sitemap.is_file():
        try:
            m_locs = set(parse_sitemap(m_sitemap))
        except ET.ParseError as exc:
            problems.append(f"D5 marketing/sitemap.xml: does not parse as XML ({exc})")
            m_locs = set()
        m_missing = sorted({live_url(p) for p in m_pages} - m_locs)
        if m_missing:
            problems.append(
                f"D5 marketing/sitemap.xml: {len(m_missing)} marketing page(s) absent — "
                + ", ".join(x.replace(LIVE, "/") for x in m_missing[:6])
            )
        m_extra = sorted({x for x in m_locs if x.startswith(LIVE + "marketing/")} - {live_url(p) for p in m_pages})
        if m_extra:
            problems.append(
                "D5 marketing/sitemap.xml: lists "
                + ", ".join(x.replace(LIVE, "/") for x in m_extra)
                + " which does not exist"
            )
    else:
        problems.append("D5 marketing/sitemap.xml: missing")

    # ---- report ---------------------------------------------------------------------------
    print(f"{len(pages)} published pages audited · {len(locs)} sitemap URLs")
    print(f"  D1 sitemap coverage    {'PASS' if not missing else 'FAIL'}")
    print(f"  D2 sitemap integrity   {'PASS' if not any(p.startswith('D2') for p in problems) else 'FAIL'}")
    print(f"  D3 robots.txt          {'PASS' if not any(p.startswith('D3') for p in problems) else 'FAIL'}")
    print(f"  D4 robots meta         {'PASS' if not noindex_in_sitemap else 'FAIL'}")
    print(f"  D5 marketing sitemap   {'PASS' if not any(p.startswith('D5') for p in problems) else 'FAIL'}")
    print(f"  D6 favicon             {'PASS' if not missing_icons else 'FAIL'}")
    print(f"  D7 canonical (report)  {len(canonical_mismatch)} page(s) point elsewhere")
    print(f"  D8 page metadata       {'PASS' if not d8_problems else 'FAIL'}")

    for note in notes:
        print(f"  note: {note}")

    if problems:
        print()
        for p in problems:
            print(f"FAIL {p}")
        return 1
    print("\nAll discoverability checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
