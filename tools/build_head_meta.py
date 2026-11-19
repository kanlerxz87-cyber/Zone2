#!/usr/bin/env python3
"""The head-metadata contract: every page this site asks a crawler to index declares its own URL.

T42 (session `5d6d2254`, 2026-11-15), reconciled with T41 (session `156aae86`).

Both sessions found the same hole on the same day and from the same measurement: `<link
rel="canonical">` and the Open Graph identity tags existed on the 18 `marketing/` pages and on no other of
the 78 published pages, so the same page was addressable twice (`…/journal/` and `…/journal/index.html`)
and a link preview had no `og:url` to read. `156aae86` shipped the crawler half — `tools/build_sitemap.py`
(now the repository's sitemap generator, deriving all 121 published pages) and `tools/seo_audit.py`, whose
D7 check *reports* a canonical that points somewhere else. This module ships the other half, which is why
D7 currently has nothing to report on the reader and evidence surfaces:

    * the block itself — `<link rel="canonical">`, `og:type`, `og:site_name`, `og:title`, `og:description`,
      `og:url` — emitted by the generator that owns each page, through `tools/head_meta.py` so the URL form
      is computed in exactly one place;
    * `--audit`, which fails the build when an indexed page breaks that contract;
    * `--fix-heads`, which writes the block into the hand-written pages (the root views that no generator
      owns and `journal/`), deriving title and description from the page's own `<head>` — a transcription,
      never a new claim.

The two tools are deliberately not merged: `tools/seo_audit.py` checks what a crawler is *told* (sitemap
coverage, robots, noindex, favicon, canonical agreement) and is written to be neutral about which tags a
page carries; this tool checks what a page *declares about itself*, including the `og:` properties a
crawler never reads and a preview renderer only does. `156aae86`'s D7 stays report-only on purpose — the
duplicate-content decision for the companion namespaces is the owner's (MQ-08 / DS-12) — and so this
audit's scope stops at the same line: the four superseded prototype namespaces are **reported, not failed**.

Usage:
    python3 tools/build_head_meta.py --audit       # gate: 0 problems or exit 1
    python3 tools/build_head_meta.py --fix-heads   # write the block into the hand-written pages
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import head_meta
from head_meta import head_block, url_for

REPO = Path(__file__).resolve().parents[1]

# The surfaces this contract holds to a passing standard: the reader publication, the hand-written
# editorial layer, the generated evidence registers, the decision surface, the discovery review, and
# the root pages. "discovery" was added by session 224cc10c (T49): PR #104 shipped the namespace with
# a second, parallel head layer that put two canonical links and two conflicting og:url values on
# every page. It was discarded on merge, and the pages now carry this contract's canonical form.
CONTRACT_DIRS = ["pages", "journal", "decisions", "marketing", "discovery", "guides"]

# Root pages a generator owns. Their head block comes from that generator, so `--fix-heads` must not
# write into them (the next `--check` would revert it) — and their generators are patched instead.
GENERATED_ROOT = {
    "summary.html": "tools/build_summary.py",
    "verification.html": "tools/build_root_views.py",
    "sources.html": "tools/build_root_views.py",
}

# Published, but excluded from the pass/fail contract: the prototypes and companion builds whose files are
# the working records of finished sessions. Listed here so the exclusion is visible in the output rather
# than silent — and so `--audit` prints how far the contract still has to go if the owner (MQ-08 / DS-12)
# decides to fold them in.
REPORT_ONLY_DIRS = ["northstar", "zone2", "research-hub", "affiliate-lab", "revalidation", "release",
                    "audit"]


class Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self.description = ""
        self.canonical = ""
        self.og: dict[str, str] = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            prop = (a.get("property") or "").lower()
            if name == "description":
                self.description = a.get("content", "")
            elif prop.startswith("og:"):
                self.og[prop[3:]] = a.get("content", "")
        elif tag == "link" and (a.get("rel") or "").lower() == "canonical":
            self.canonical = a.get("href", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def rel_of(path: Path) -> str:
    """Repository-relative posix path — the only form `head_meta.url_for` accepts."""
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix().lstrip("/")


def unescape(text: str) -> str:
    return (text.replace("&amp;", "&").replace("&quot;", '"').replace("&#39;", "'").replace("&apos;", "'")
            .replace("&middot;", "·").replace("&nbsp;", " ").replace("&ndash;", "–").replace("&mdash;", "—")
            .replace("&gt;", ">").replace("&lt;", "<"))


def read_head(path: Path) -> Head:
    h = Head()
    h.feed(path.read_text(encoding="utf-8"))
    return h


def contract_pages() -> list[Path]:
    """Every page the contract covers, in a stable order: root first, then each namespace."""
    out: list[Path] = []
    root_pages = sorted(p for p in (REPO / ".").glob("*.html") if p.name != "404.html")
    out.extend(sorted(root_pages, key=lambda p: (p.name != "index.html", p.name)))
    for d in CONTRACT_DIRS:
        out.extend(sorted((REPO / d).rglob("*.html")))
    return out


def report_only_pages() -> list[Path]:
    out: list[Path] = []
    for d in REPORT_ONLY_DIRS:
        out.extend(sorted(p for p in (REPO / d).rglob("*.html") if p.name != "404.html"))
    return out


def audit(pages: list[Path]) -> tuple[list[str], int]:
    problems: list[str] = []
    for p in pages:
        if not p.is_file():
            problems.append(f"{p.relative_to(REPO)}: page in the contract but not on disk")
            continue
        rel = p.relative_to(REPO).as_posix()
        h = read_head(p)
        mine = url_for(rel_of(p))
        if not h.title.strip():
            problems.append(f"{rel}: no <title>")
        if not h.description.strip():
            problems.append(f'{rel}: no <meta name="description">')
        if h.canonical != mine:
            problems.append(f"{rel}: canonical is {h.canonical!r}, expected {mine!r}")
        for prop in ("type", "site_name", "title", "url"):
            if not h.og.get(prop):
                problems.append(f"{rel}: no og:{prop}")
        if h.og.get("url") and h.og["url"] != mine:
            problems.append(f"{rel}: og:url is {h.og['url']!r}, expected {mine!r}")
        # A canonical that agrees with the file's own path is the only canonical claim this gate can make
        # without deciding the duplicate-content question for the owner (see D7 in tools/seo_audit.py).
    return problems, len(pages)


def fix_heads() -> tuple[int, list[str]]:
    """Add the block to hand-written pages that lack it. Idempotent; never rewrites a correct block."""
    changed, skipped = 0, []
    targets = [p for p in (REPO / ".").glob("*.html")
               if p.name not in GENERATED_ROOT and p.name != "404.html"]
    targets += sorted((REPO / "journal").rglob("*.html"))
    for p in sorted(targets):
        rel = p.relative_to(REPO).as_posix()
        text = p.read_text(encoding="utf-8")
        h = read_head(p)
        if h.canonical == url_for(rel_of(p)) and all(k in h.og for k in ("type", "site_name", "title", "url")):
            continue
        title = unescape(re.sub(r"\s+", " ", h.title)).strip()
        desc = unescape(h.description).strip()
        if not title or not desc:
            skipped.append(f"{rel}: no title or description to transcribe — left alone, not invented")
            continue
        is_journal = rel.startswith("journal/")
        block = head_block(
            rel_of(p), title=title, description=desc,
            site_name="Zone2 Journal" if is_journal else "Zone2",
            page_type="article" if is_journal and not rel.endswith("index.html") else "website")
        # Insert immediately before </head>, on its own line. An earlier revision anchored on the
        # first of several candidate tags, which let a `<link rel="icon">` line end up split in half —
        # visible in the rendered page, and the kind of defect this repository now gates against.
        anchor = re.search(r'</head>', text)
        if anchor is None:
            skipped.append(f"{rel}: no </head> to insert before — left alone rather than guessed")
            continue
        # Replace a stray half-block (a canonical with no og:* set) instead of stacking a second one.
        text = re.sub(r'(?:<link rel="canonical"[^>]*>\n(?:<meta property="og:[^>]*>\n?){0,5})+',
                      '', text, count=1) if h.canonical and h.canonical != url_for(rel_of(p)) else text
        insert = block + "\n"
        # keep the closing tag on its own line
        head_close = anchor.start()
        pre = text[:head_close].rstrip(" \t")
        p.write_text(pre + "\n" + insert + text[head_close:], encoding="utf-8")
        changed += 1
    return changed, skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--audit", action="store_true", help="fail if a page in the contract breaks the head-metadata rules")
    ap.add_argument("--fix-heads", action="store_true", help="write the block into the hand-written pages that lack it")
    args = ap.parse_args()

    if args.fix_heads:
        changed, skipped = fix_heads()
        for s in skipped:
            print(f"skip  {s}")
        print(f"{changed} hand-written page(s) updated, {len(skipped)} skipped")
        return 0

    problems, n = audit(contract_pages())
    extras = [p for p in report_only_pages() if read_head(p).canonical != url_for(rel_of(p))]
    if problems:
        print("\n".join(problems))
    print(f"{n} pages under the contract: {len(problems)} problem(s)")
    if extras:
        print(f"  report only (companion namespaces, owner decision MQ-08 / DS-12): {len(extras)} page(s) "
              f"without a self-referencing canonical")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
