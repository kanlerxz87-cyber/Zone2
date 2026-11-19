#!/usr/bin/env python3
"""Deploy gate for the marketing set.

Fails (non-zero exit) if any of these stop being true, so none of them depends on someone remembering:

  G1  every generated page exists and carries the Associates disclosure sentence
  G2  every page that shows an affiliate link also carries a link-level disclosure (R-02)
  G3  every generated page has fully resolved internal links and asset references
  G4  no page prints a money amount in a buying context (the project's no-price rule)
  G5  every outbound Amazon marketplace link carries rel="sponsored" (Google's outbound-link rule);
      since the owner supplied the Associates tag (2026-11-17): every product Special Link carries
      the owner's tag, no link carries a different tag, and citation links carry no tag at all
  G6  every generated page states the tagged-Special-Link state of its links (T58)
  G7  **every table row that shows a value also shows a source link** - the core project rule
  G8  every row marked UNVERIFIED/WITHHELD prints no value at all
  G9  committed HTML matches a fresh build (nothing hand-edited)
  G10 every official source URL used is on an allow-listed official host
  G11 every factual sentence on a guide or review page carries a source id that resolves  (T39)
  G12 the writing standard is enforced, not recommended: a banned phrase on a reader-facing page,
      an opinion outside a labelled take box, or an unlabelled "we tested" claim fails the build  (T39)
  G13 every generated page is reachable from another generated page  (T39)
  G14 sitemap.xml covers every HTML page, feed.xml items resolve, and each canonical URL matches
      the file it sits in  (T39)

CR-8 (T69, 2026-11-19): G1-G10 run over every rendered HTML page — the marketing registry and the
thermometer desk (marketing/thermometers/) alike — so there is one verifier for every reader page
(SG-15 option A). The desk keeps its own build-time gate in tools/build_thermometers.py; this
verifier no longer skips its pages.

The row-level checks (G7/G8) re-derive the expectation from marketing/data/facts.json and then read the
rendered HTML, so a renderer bug cannot quietly pass its own test.
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

from build_marketing import LIVE, PAGES, SOURCES, build  # noqa: E402
from link_builder import REQUIRED_SITE_DISCLOSURE  # noqa: E402

ROOT = REPO / "marketing"
FACTS = json.loads((ROOT / "data" / "facts.json").read_text(encoding="utf-8"))

# Our own published origin (scheme + repo path). Absolute links under this prefix are internal
# references, not external sources — see the same-origin branch in check_links (CR-8).
SITE_PREFIX = LIVE.rsplit("marketing/", 1)[0]

OFFICIAL_HOSTS = {
    "www.amazon.com",
    "amazon.com",
    "chefman.com",
    "www.chefman.com",
    "www.emerileveryday.com",
    "affiliate-program.amazon.com",
    # Added 2026-11-15 (T39): the improvement board's recommendations cite Google's own search
    # documentation instead of an SEO blog, so Google's domain is now an official source on these
    # pages. The allow-list is deliberately still a list, not a wildcard.
    "developers.google.com",
    # CR-8 (T69, 2026-11-19): SG-15 option A. The thermometer desk's food-safety sentences cite
    # USDA's Food Safety and Inspection Service — the federal agency that publishes the temperature
    # guidance the desk quotes (three FSIS factsheets, listed in marketing/data/thermometers.json).
    # The desk's own gate (build_thermometers.ALLOWED_HOSTS) has listed this host since the desk
    # shipped; this closes the gap so G1-G10 cover the desk's pages too. Still a list, not a wildcard.
    "www.fsis.usda.gov",
}
MARKETPLACE_HOSTS = {"www.amazon.com", "amazon.com"}

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(
    r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer|cost)\b", re.I
)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|tax|refund|withhold)s?\b", re.I
)

failures: list[str] = []


def fail(msg: str) -> None:
    failures.append(msg)


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, dict]] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.refs.append(("script", a))
        if tag == "link" and a.get("rel") == "stylesheet" and a.get("href"):
            self.refs.append(("stylesheet", a))
        if tag == "a" and a.get("href"):
            self.refs.append(("a", a))


def rel_path(ref: str) -> str:
    return ref.split("#")[0].split("?")[0]


def check_links(rel: str, doc: str) -> None:
    page_dir = (ROOT / rel).parent
    p = Refs()
    p.feed(doc)
    for kind, a in p.refs:
        ref = a.get("href") or a.get("src") or ""
        if kind != "a":
            target = (page_dir / ref).resolve()
            if not target.is_file():
                fail(f"G3 {rel}: missing asset {ref}")
            continue
        if ref.startswith(("http://", "https://")):
            # CR-8 (T69): the desk prints its published self-links as absolute URLs on our own
            # origin. Same-origin references are internal, not sources: resolve them inside the
            # repository and check they exist, instead of demanding they appear on the
            # official-host allow-list. A different origin still falls through to G10.
            if ref.startswith(SITE_PREFIX):
                own = ref[len(SITE_PREFIX):]
                if not (REPO / rel_path(own)).is_file():
                    fail(f"G3 {rel}: absolute self-link does not resolve in the repo: {ref[:90]}")
                continue
            host = re.sub(r"^https?://", "", ref).split("/")[0].lower()
            if host in MARKETPLACE_HOSTS:
                if "sponsored" not in (a.get("rel") or "").lower():
                    fail(f"G5 {rel}: Amazon link without rel=sponsored: {ref[:90]}")
                # T58 (2026-11-17): the owner supplied the Associates tag, so the rules hardened.
                #  - a product link (class="sponsored-link") MUST carry the owner's tag;
                #  - any tagged link must carry THE owner's tag, never another account's;
                #  - a citation link (class="src") MUST NOT carry a tag: evidence stays unmonetized.
                classes = (a.get("class") or "").split()
                if "sponsored-link" in classes and "tag=shopnow047c-20" not in ref:
                    fail(f"G5 {rel}: product Special Link without the owner's Associates tag: {ref[:90]}")
                if "src" in classes and "tag=" in ref:
                    fail(f"G5 {rel}: citation link carries an Associates tag; evidence must stay unmonetized: {ref[:90]}")
                if "tag=" in ref and "tag=shopnow047c-20" not in ref:
                    fail(f"G5 {rel}: Associates tag other than the owner's on {ref[:90]}")
                if "tag=" not in ref and "src" not in classes:
                    fail(f"G5 {rel}: untagged Amazon link that is not a citation: {ref[:90]}")
            if host not in OFFICIAL_HOSTS:
                fail(f"G10 {rel}: link to a non-allow-listed host {host!r}")
            continue
        if ref.startswith(("#", "mailto:")):
            continue
        target = (page_dir / rel_path(ref)).resolve()
        if not target.is_file():
            fail(f"G3 {rel}: broken internal link {ref}")


def check_prices(rel: str, doc: str) -> None:
    text = re.sub(r"<[^>]+>", " ", doc)
    for unit in re.split(r"</tr>|</p>|</li>|<br\s*/?>|\n", text):
        for m in MONEY.finditer(unit):
            if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                fail(f"G4 {rel}: money value {m.group(0)!r} in a buying context")


def check_rows(rel: str, doc: str) -> None:
    """G7/G8: for the article pages, every attribute row must carry a source pill or say why not."""
    if not rel.startswith("articles/p"):
        return
    rows = re.findall(r'<tr id="p\d-r\d+">(.*?)</tr>', doc, flags=re.S)
    if not rows:
        fail(f"G7 {rel}: no specification rows found - the page lost its table")
        return
    for i, row in enumerate(rows, start=1):
        has_value = bool(re.search(r"<strong>.*?</strong>", row, flags=re.S))
        has_src = 'class="src"' in row
        has_pill = 'class="pill' in row
        is_blank = 'class="cell-blank"' in row
        if has_value and not has_src:
            fail(f"G7 {rel}: row {i} prints a value with no official source link")
        if not has_value and not is_blank:
            fail(f"G8 {rel}: row {i} has neither a value nor an explicit blank marker")
        if is_blank and not has_pill:
            fail(f"G8 {rel}: row {i} is blank but carries no UNVERIFIED/WITHHELD pill and no reason")
    # cross-check the count against the data file
    key = re.search(r"articles/(p\d)\.html", rel).group(1).upper()
    expected = len(next(p for p in FACTS["products"] if p["key"] == key)["rows"])
    if len(rows) != expected:
        fail(f"G7 {rel}: {len(rows)} rows rendered but the data file defines {expected}")


BANNED_CACHE: dict[str, list[str]] = {}


def editorial_checks(rendered: dict[str, str]) -> None:
    """G11-G14, added by T39. These exist because the alternative - a style guide nobody enforces -
    is exactly how the previous revision drifted back to generic copy within one regeneration."""
    editorial = json.loads((ROOT / "data" / "editorial.json").read_text(encoding="utf-8"))
    banned = [w.lower() for w in editorial["voice"]["banned_words"]]
    known_srcs = set(SOURCES)

    # G11 covers the guide bodies. The product pages are governed by G7 (every valued spec row
    # carries its source), and a hub page makes no factual claim to source.
    reader_pages = {rel: doc for rel, doc in rendered.items()
                    if rel.startswith("topics/") and rel != "topics/index.html" and rel.endswith(".html")}

    for rel, doc in reader_pages.items():
        # G11: every claim element cites something, and the citation resolves.
        claims = re.findall(r'<p class="claim" id="([^"]+)" data-src="([^"]*)"', doc)
        if not claims:
            fail(f"G11 {rel}: no sourced claims - the page was rewritten around the data layer")
        for cid, srcs in claims:
            ids = [x for x in srcs.split(",") if x]
            if not ids:
                fail(f"G11 {rel}: claim {cid} states a fact with no source id")
            for sid in ids:
                if sid not in known_srcs:
                    fail(f"G11 {rel}: claim {cid} cites {sid!r}, which is not a registered official source")
        # G12a: the banned-phrase list. The improvements board is exempt on purpose: it *shows*
        # the phrases as negative examples, in a different namespace.
        flat = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", doc)).lower()
        for word in banned:
            if word in flat:
                fail(f"G12 {rel}: banned phrase {word!r} - generated filler, or a sentence worth rewriting")
        # G12b: an opinion must be labelled. Every .take box carries the label; nothing else may
        # claim first-hand experience.
        for take in re.findall(r'<aside class="take".*?</aside>', doc, flags=re.S):
            if "take-label" not in take:
                fail(f"G12 {rel}: a judgement box without its label - an opinion is passing as a spec")
        for phrase in ("we tested", "our team tested", "we tested these", "hands-on", "we used it"):
            if phrase in flat:
                fail(f"G12 {rel}: claims first-hand use ({phrase!r}); nobody here has cooked with these products")

    # G13: an orphan page is a page nobody finds. Count only links between generated pages.
    targets: set[str] = set()
    for rel, doc in rendered.items():
        if not rel.endswith(".html"):
            continue
        base = (ROOT / rel).parent
        for href in re.findall(r'<a[^>]+href="([^"]+)"', doc):
            if href.startswith(("http", "#", "mailto:")):
                continue
            clean = href.split("#")[0]
            if not clean:
                continue
            resolved = (base / clean).resolve()
            try:
                targets.add(str(resolved.relative_to(ROOT.resolve())))
            except ValueError:
                pass
    for rel in rendered:
        if rel.endswith(".html") and rel != "index.html" and rel not in targets:
            fail(f"G13 {rel}: generated but not linked from any other generated page - an orphan")

    # G14: the machine-readable set agrees with the page set.
    xml = rendered.get("sitemap.xml", "")
    for rel in rendered:
        if rel.endswith(".html"):
            if f"{LIVE}{rel}" not in xml:
                fail(f"G14 sitemap.xml: {rel} is published but not listed")
    for rel, doc in rendered.items():
        if rel.endswith(".html"):
            if f'rel="canonical" href="{LIVE}{rel}"' not in doc:
                fail(f"G14 {rel}: canonical URL does not match its own path")
    for item in re.findall(r"<item>.*?<link>([^<]+)</link>", rendered.get("feed.xml", ""), flags=re.S):
        # T63 (session 10727edd): the feed also carries the question-shaped guides under the
        # site's guides/ directory. An item outside marketing/ must resolve to a committed page
        # at the site root; an item inside marketing/ must still be a page this builder renders.
        site_root = LIVE.rsplit("marketing/", 1)[0]
        if not item.startswith(LIVE) and item.startswith(site_root):
            rel_site = item[len(site_root):]
            repo_root = Path(__file__).resolve().parents[2]
            if not rel_site.endswith(".html") or not (repo_root / rel_site).is_file():
                fail(f"G14 feed.xml: {item} does not resolve to a published page")
            continue
        target = item.replace(LIVE, "")
        if target not in rendered:
            fail(f"G14 feed.xml: {item} is not a generated page")


def main() -> int:
    if len(PAGES) < 9:
        fail(f"G1 expected at least 9 marketing pages, builder defines {len(PAGES)}")

    fresh = build(ROOT / ".fresh")  # build to a scratch dir, compare, then remove
    editorial_checks(fresh)  # G11-G14 (T39) run on the render, so a renderer bug cannot skip them
    import shutil

    shutil.rmtree(ROOT / ".fresh", ignore_errors=True)

    # CR-8 (T69): G1-G10 now run over every rendered HTML page — the marketing registry *and*
    # the thermometer desk — so one verifier owns every reader page (SG-15 option A). The set is
    # taken from the fresh build, never hand-listed, so a future desk page is covered on the day
    # it is added. sitemap.xml / robots.txt / feed.xml carry no prose and stay out, as before.
    html_pages = [rel for rel in fresh if rel.endswith(".html")]
    for rel in html_pages:
        path = ROOT / rel
        if not path.is_file():
            fail(f"G1 {rel}: not generated")
            continue
        doc = path.read_text(encoding="utf-8")
        if REQUIRED_SITE_DISCLOSURE not in doc:
            fail(f"G1 {rel}: missing the Associates disclosure sentence")
        if "sponsored-link" in doc and "disclosure--link" not in doc:
            fail(f"G2 {rel}: affiliate link without a link-level disclosure")
        if "sponsored-link" in doc and "Special Link" not in doc:
            fail(f"G6 {rel}: shows an affiliate link but does not state its tagged-Special-Link state")
        check_links(rel, doc)
        check_prices(rel, doc)
        check_rows(rel, doc)
        if fresh.get(rel) != doc:
            fail(f"G9 {rel}: committed file differs from a fresh build")

    # Every official source URL in the data must be on an allow-listed host.
    for product in FACTS["products"]:
        for src in product["official_sources"]:
            host = src["url"].split("/")[2]
            if host not in OFFICIAL_HOSTS:
                fail(f"G10 data: source {src['id']} host {host!r} is not allow-listed")
        for row in product["rows"]:
            if row["status"] not in ("unverified", "withheld_by_policy") and not row.get("src"):
                fail(f"G7 data: {product['key']} row {row['attr']!r} has a value but no source")

    pages = len(html_pages)  # CR-8: every rendered page, registry and desk, not just PAGES
    desk = sum(1 for rel in html_pages if rel.startswith("thermometers/"))
    rows = sum(len(p["rows"]) for p in FACTS["products"])
    if failures:
        print("\n".join(f"FAIL {f}" for f in failures))
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"OK  {pages} pages ({len(PAGES)} marketing registry + {desk} thermometer desk) · {rows} spec rows · 0 failures")
    print("    disclosure on every page · affiliate links disclosed and tagged as Special Links · no prices ·")
    print("    internal links resolve · every valued row carries an official source link")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
