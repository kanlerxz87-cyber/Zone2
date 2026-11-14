#!/usr/bin/env python3
"""Structural audit of the published site — the checks the drift gates cannot make.

Why this exists (T26, session `808a6840`). `build_site.py --check` and
`build_root_views.py --check` prove that the committed HTML matches the ledger, and
`validate_data.py` proves that each ledger row carries a source. None of them can see
four classes of defect that only a read of the *deployed* pages exposes:

1. **Dead fragment.** `href="products.html#"` or `href="#section"` where no element
   carries that `id`: the reader is silently dropped at the top of the page and the
   cited evidence is lost. The CI link check strips fragments, so it cannot see this.
2. **A specification sourced to a page that does not exist.** A row can be internally
   consistent (value + source id both present) while the cited URL is Amazon's
   Page Not Found response for a 9-character code. This checks the data, so it holds
   regardless of which page renders it.
3. **Prose counts drifting from the registers they describe.** The deploy gates compare
   HTML against data; nothing compares the *number written in a sentence* against the
   register. That is how "22 sources" survived while the register held 35.
4. **An orphaned published namespace.** A whole set of pages can ship with no inbound
   link from the landing page, which is invisible to a link checker that only tests
   links that exist.

Every check fails the build with file and line. No network access, so CI and a local run
agree byte for byte.

Usage:
    python3 tools/audit_site.py            # report, non-zero exit on failure
    python3 tools/audit_site.py --json     # machine-readable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".github"}

# Namespaces that must be reachable from the landing page (`index.html`).
REQUIRED_NAMESPACES = [
    "pages/index.html",
    "research-hub/start.html",
    "northstar/index.html",
    "zone2/index.html",
    "affiliate-lab/index.html",
    "revalidation/index.html",
    "marketing/index.html",
]

# URLs Amazon answers with an error page. Evidence: ledger/verification.json V-02..V-04 and
# flag F-02. Any of them may be *cited as evidence of the failure* — but no specification
# value may be sourced to one.
KNOWN_NOT_FOUND = {
    "https://www.amazon.com/dp/B04G1MEwY",
    "https://www.amazon.com/dp/B02NbDxp3",
    "https://www.amazon.com/dp/B00hJ57DV",
}

# Surfaces whose prose is a claim about this repository's own registers. Companion
# namespaces (affiliate-lab/, research-hub/, pages/) describe their own session-local
# counts and are deliberately excluded — they would otherwise be compared against the
# wrong register.
COUNT_SURFACES = ["README.md", "EXECUTIVE_SUMMARY.md"]


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.js_routes: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        # A hash-router (northstar/) declares its routes as data-page attributes rather
        # than element ids. Those `#route` links are navigation, not fragment citations.
        if "data-page" in a:
            self.js_routes.add(str(a["data-page"]))
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], self.getpos()[0]))


def load_json(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


def published_pages() -> list[Path]:
    out = []
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        out.append(p)
    return out


def resolve(page: Path, href: str) -> Path | None:
    if not href or href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
        return None
    target = href.split("#", 1)[0].split("?", 1)[0]
    if not target:
        return page
    return (page.parent / target).resolve()


def check_fragments(pages, parsed) -> list[str]:
    problems = []
    for p in pages:
        for href, line in parsed[p].links:
            if "#" not in href or href.startswith(("http://", "https://", "mailto:")):
                continue
            target, frag = href.split("#", 1)
            tgt = resolve(p, href)
            if tgt is None or not tgt.is_file():
                continue
            tgt_page = parsed.get(tgt)
            if tgt_page is None:
                tgt_page = Page()
                tgt_page.feed(tgt.read_text(encoding="utf-8"))
            if frag == "":
                # Tolerated only when the target page hosts a hash-router.
                if tgt_page.js_routes or tgt_page.ids:
                    continue
            if frag == "" or (frag.lower() not in {i.lower() for i in tgt_page.ids}
                              and frag not in tgt_page.js_routes):
                problems.append(
                    f"{p.relative_to(REPO)}:{line}: {href!r} — fragment #{frag or '(empty)'} "
                    f"addresses nothing in {tgt.relative_to(REPO)}"
                )
    return problems


def check_spec_sources() -> list[str]:
    """No specification value may be sourced to a URL that does not resolve."""
    problems = []
    sources = {s["id"]: s["url"] for s in load_json("sources.json")["sources"]}

    def audit(rows, where):
        for row in rows:
            ids = row.get("source_ids") or []
            if not ids:
                problems.append(f"{where}: {row.get('attribute')!r} has no source id")
                continue
            urls = [sources.get(i, "") for i in ids]
            live = [u for u in urls if u and u not in KNOWN_NOT_FOUND]
            if not live:
                problems.append(
                    f"{where}: {row.get('attribute')!r} = {str(row.get('value'))[:40]!r} is "
                    f"sourced only to a Page-Not-Found URL ({urls})"
                )
            for i, u in zip(ids, urls):
                if not u:
                    problems.append(f"{where}: unknown source id {i!r}")

    specs = json.loads((REPO / "tools" / "verified_specs_2026-11-14.json").read_text(encoding="utf-8"))
    for product in specs["products"]:
        audit(product.get("specs", []), f"specs:{product.get('resolved_asin')}")
    return problems


def check_counts() -> list[str]:
    """Numbers written in prose on the root surfaces must match the registers."""
    actual = {
        "flags": len(load_json("flags.json")["flags"]),
        "checks": len(load_json("verification.json")["rows"]),
        "sources": len(load_json("sources.json")["sources"]),
        "products": len(load_json("products.json")["entries"]),
    }
    patterns = [
        (re.compile(r"(\d+)\s+(?:logged\s+|independent\s+)?checks\b", re.I), "checks"),
        (re.compile(r"(\d+)\s+sources\b", re.I), "sources"),
        (re.compile(r"(\d+)\s+flags\b", re.I), "flags"),
        (re.compile(r"(\d+)\s+items?\s+flagged\b", re.I), "flags"),
    ]
    problems = []
    for name in COUNT_SURFACES:
        path = REPO / name
        if not path.is_file():
            problems.append(f"{name}: declared in COUNT_SURFACES but missing")
            continue
        text = path.read_text(encoding="utf-8")
        prose = re.sub(r"<[^>]+>", " ", text)
        for pattern, key in patterns:
            for m in pattern.finditer(prose):
                found = int(m.group(1))
                if found != actual[key]:
                    ctx = re.sub(r"\s+", " ", prose[max(0, m.start() - 70):m.end() + 25]).strip()
                    problems.append(
                        f"{name}: says {found} {key} but the register holds {actual[key]} "
                        f"— near {ctx!r}"
                    )
    return problems


def check_namespaces() -> list[str]:
    landing = (REPO / "index.html").read_text(encoding="utf-8")
    problems = []
    for ns in REQUIRED_NAMESPACES:
        if not (REPO / ns).is_file():
            problems.append(f"{ns}: declared in REQUIRED_NAMESPACES but not published")
        elif ns not in landing:
            problems.append(f"{ns}: published but not linked from index.html — orphaned")
    return problems


def check_disclosure(pages) -> list[str]:
    return [f"{p.relative_to(REPO)}: disclosure sentence absent"
            for p in pages if DISCLOSURE not in p.read_text(encoding="utf-8")]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    pages = published_pages()
    parsed = {}
    for p in pages:
        page = Page()
        page.feed(p.read_text(encoding="utf-8"))
        parsed[p] = page

    results = {
        "pages": len(pages),
        "fragments": check_fragments(pages, parsed),
        "spec_sources": check_spec_sources(),
        "prose_counts": check_counts(),
        "namespaces": check_namespaces(),
        "disclosure": check_disclosure(pages),
    }
    failures = sum(len(v) for v in results.values() if isinstance(v, list))
    results["failures"] = failures
    results["ok"] = failures == 0

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"{results['pages']} published pages audited")
        for key in ("fragments", "spec_sources", "prose_counts", "namespaces", "disclosure"):
            items = results[key]
            print(f"  {key:13s} {'PASS' if not items else f'FAIL ({len(items)})'}")
            for item in items:
                print(f"      - {item}")
    return 0 if results["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
