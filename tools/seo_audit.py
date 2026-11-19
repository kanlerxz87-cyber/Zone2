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
  D8  per-page identity     S-04 / RQ-01, which the decision board measures as the brief's only
                            unfinished P1 row. Three mechanical properties over every published page:
                            (a) it carries a non-empty `<meta name="description">`; (b) no two pages
                            share a `<title>`; (c) no two pages share a description. Before T72 the
                            tree failed all three — 7 pages had no description at all and one string
                            served 39 URLs — and nothing failed the build, which is why the row
                            stayed open while the brief called it "Implemented".

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
        self.description: list[str] = []
        self.title: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag == "meta" and (a.get("name") or "").lower() == "robots":
            self.robots.append((a.get("content") or "").lower())
        if tag == "meta" and (a.get("name") or "").lower() == "description":
            self.description.append((a.get("content") or "").strip())
        if tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "canonical" in rel and a.get("href"):
                self.canonical.append(a["href"])
            if ("icon" in rel or "shortcut" in rel) and a.get("href"):
                self.icons.append(a["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            text = " ".join(data.split())
            if text:
                self.title.append(text)


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

    # ---- D8: per-page identity (S-04 / RQ-01) --------------------------------------------
    # Deliberately measured over *every published page*, including the noindex archives: a
    # duplicate title is a defect whether or not the page is advertised in the sitemap, and the
    # brief's row says "every page" rather than "every indexed page".
    missing_desc: list[str] = []
    title_owner: dict[str, list[str]] = {}
    desc_owner: dict[str, list[str]] = {}
    for rel in pages:
        parser = Refs()
        parser.feed((REPO / rel).read_text(encoding="utf-8", errors="replace"))
        desc = next((d for d in parser.description if d), "")
        title = " ".join(parser.title).strip()
        if not desc:
            missing_desc.append(rel.as_posix())
        else:
            desc_owner.setdefault(desc, []).append(rel.as_posix())
        if title:
            title_owner.setdefault(title, []).append(rel.as_posix())
    dup_titles = {k: v for k, v in title_owner.items() if len(v) > 1}
    dup_descs = {k: v for k, v in desc_owner.items() if len(v) > 1}
    if missing_desc:
        problems.append(
            f"D8 per-page identity: {len(missing_desc)} published page(s) carry no meta description — "
            + ", ".join(missing_desc[:12]) + (" …" if len(missing_desc) > 12 else "")
        )
    if dup_titles:
        problems.append(
            f"D8 per-page identity: {len(dup_titles)} title(s) shared by more than one page — "
            + "; ".join(f"{k!r} on {len(v)} pages" for k, v in sorted(dup_titles.items())[:6])
        )
    if dup_descs:
        problems.append(
            f"D8 per-page identity: {len(dup_descs)} description(s) shared by more than one page — "
            + "; ".join(f"{k[:60]!r}… on {len(v)} pages" for k, v in sorted(dup_descs.items())[:6])
        )

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
    d8_ok = not (missing_desc or dup_titles or dup_descs)
    print(f"  D8 per-page identity   {'PASS' if d8_ok else 'FAIL'}"
          f"  ({len(pages) - len(missing_desc)}/{len(pages)} described, "
          f"{len(title_owner)} distinct titles, {len(desc_owner)} distinct descriptions)")

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
