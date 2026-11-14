"""Deploy gate. Fails the build when data would violate the project's verification contract.

The contract, from the project brief:
  "Every table row must have a source link to an official site. If a value can't be confirmed from an official
   source, leave it blank and flag it as unverified. Never infer or fill in values."

This turns that sentence into an executable check, so the rule survives whoever edits the data next.

Checks
  1. referential integrity   - every source_ids entry resolves to ledger/sources.json
  2. official-host policy    - sources are limited to Amazon / FTC / Google / GitHub official domains
  3. blank-or-sourced        - a populated field needs a source; a blank field needs a flag or why-blank note
  4. no invented metrics     - performance fields must be blank everywhere (clicks/conversion/earnings)
  5. no Amazon marks         - site naming/copy may not include Amazon marks (R-11)
  6. disclosure present      - the required Site sentence is present where a sponsored link exists (R-01/R-02)
  7. cross-session drift     - the published data.js product rows still match ledger/products.json
  8. internal links resolve  - every href in the built site maps to a real file (no broken pages)
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "ledger"

OFFICIAL_HOSTS = {
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "amazon.com",
    "webservices.amazon.com",
    # T23-INTEGRATION: `link.amazon` is Amazon's own delegated top-level domain, and the three
    # links the client supplied are of exactly that form. They are registered as sources because
    # the behaviour of that service is the evidence for flags F-03, F-20, F-21 and F-24. No
    # product attribute is ever sourced to it - only to the amazon.com page it resolves to.
    "link.amazon",
    "www.ftc.gov",
    "ftc.gov",
    "developers.google.com",
    "support.google.com",
    "docs.github.com",
}

# Primary manufacturer pages. They are NOT Amazon sources and may never be used to state an Amazon-side
# fact (price, availability, rating, review count, BSR, category). They are allowed only for manufacturer
# specifications, and only when the source record declares kind="manufacturer" so the distinction between
# "Amazon said this" and "the maker said this" stays visible in the published source column.
MANUFACTURER_HOSTS = {
    "chefman.com",
    "www.chefman.com",
    "www.emerileveryday.com",
    "emerileveryday.com",
}
PERF_FIELDS = ("clicks", "conversion", "orders", "earnings", "revenue", "epc", "impressions")
SITE_NAME = "Zone2"  # this project's own name; must contain no Amazon mark (R-11)
# Changed 2026-11-14 (final integration): the published site is one product, so the name matches
# tools/build_site.py. "Northstar" is the earlier prototype preserved at northstar/.
SITE_NAME_MARKS = [m for m in ("amazon", "amzn", "kindle", "prime", "audible", "imdb") if m in SITE_NAME.lower()]


UNVERIFIED_STATES = {"UNVERIFIED", "NOT_VERIFIED", "BLOCKED", "NEEDS_REVIEW"}
AMAZON_MARKS = ("amazon", "amzn", "alexa", "audible", "imdb", "kindle", "prime", "aws", " Associates")

# Words that would turn an unverified listing into a product claim.
CLAIM_WORDS = ("cheapest", "best-selling", "top rated", "number one", "guaranteed", "editor's choice")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict[str, int] = field(default_factory=dict)

    def fail(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {"ok": not self.errors, "errors": self.errors, "warnings": self.warnings, "stats": self.stats}


def _load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def check_sources(report: Report) -> dict[str, dict]:
    doc = _load("sources.json")
    by_id: dict[str, dict] = {}
    for src in doc["sources"]:
        if src["id"] in by_id:
            report.fail(f"duplicate source id {src['id']}")
        by_id[src["id"]] = src
        url = src.get("url", "")
        host = urlparse(url).netloc.lower()
        if not url.startswith("https://"):
            report.fail(f"{src['id']}: url is not https ({url})")
        if host not in OFFICIAL_HOSTS:
            if host in MANUFACTURER_HOSTS:
                if src.get("kind") != "manufacturer":
                    report.fail(
                        f"{src['id']}: host {host!r} is a manufacturer site and must be declared kind='manufacturer'"
                    )
            else:
                report.fail(f"{src['id']}: host {host!r} is not an official domain allowlisted for sourcing")
        if not src.get("accessed_utc"):
            report.warn(f"{src['id']}: no accessed_utc date recorded")
    report.stats["sources"] = len(by_id)
    return by_id


def _walk_rows(obj, path=""):
    if isinstance(obj, dict):
        if "source_ids" in obj or "id" in obj:
            yield path or "root", obj
        for k, v in obj.items():
            yield from _walk_rows(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_rows(v, f"{path}[{i}]")


def check_rows(report: Report, sources: dict[str, dict]) -> None:
    rows = 0
    for name in ("products.json", "commission_table.json", "compliance.json", "flags.json", "modules.json", "verification.json"):
        doc = _load(name)
        for path, row in _walk_rows(doc):
            rows += 1
            ids = row.get("source_ids") or ([row["source_id"]] if row.get("source_id") else [])
            for sid in ids:
                if sid not in sources:
                    report.fail(f"{name}:{path}: references unknown source id {sid!r}")
            if not ids:
                # A row with no source is allowed only if it is explicitly a method/label row.
                if any(row.get(k) not in (None, "", []) for k in ("value", "rate_pct", "rate")):
                    report.fail(f"{name}:{path}: carries a value but no source_ids")
    report.stats["rows"] = rows


def check_products(report: Report) -> None:
    doc = _load("products.json")
    flags = {f["id"] for f in _load("flags.json")["flags"]}
    for e in doc["entries"]:
        eid = e["id"]
        # 3. blank-or-sourced
        for key in ("title", "brand", "category", "price", "availability", "rating", "review_count", "bsr", "commission_rate"):
            val = e.get(key)
            if val in (None, "", 0):
                if e.get("status") not in UNVERIFIED_STATES:
                    report.fail(f"{eid}.{key}: blank but status is {e.get('status')!r}, expected an unverified state")
                if not e.get("why_blank"):
                    report.fail(f"{eid}.{key}: blank with no why_blank explanation")
                if not (set(e.get("flag_ids", [])) & flags):
                    report.fail(f"{eid}: blank fields must be linked to a flag in ledger/flags.json")
            else:
                if not e.get("source_ids"):
                    report.fail(f"{eid}.{key}: populated value {val!r} without a source - inferred data")
                for word in CLAIM_WORDS:
                    if isinstance(val, str) and word in val.lower():
                        report.fail(f"{eid}.{key}: claim word {word!r} in a product field")
        # 4. no invented metrics
        for key in PERF_FIELDS:
            if e.get(key) not in (None, ""):
                report.fail(f"{eid}.{key}: performance data present but no Associates report is connected")
        for bad in ("inferred", "assumed", "estimated as", "typically retails"):
            if bad in json.dumps(e).lower() and "not " not in json.dumps(e).lower():
                report.warn(f"{eid}: text contains {bad!r} - confirm it is a negation, not an inference")
    report.stats["product_entries"] = len(doc["entries"])


def check_cross_session_drift(report: Report) -> None:
    """The merged landing page keeps its own copy of the product queue (data.js). It must not diverge."""
    js = (REPO / "data.js").read_text(encoding="utf-8") if (REPO / "data.js").exists() else ""
    if not js:
        return
    for e in _load("products.json")["entries"]:
        if e["submitted_url"] not in js:
            report.fail(f"{e['id']}: submitted_url is missing from the landing page's data.js - rows have diverged")


def check_marks(report: Report) -> None:
    """R-11 / Operating Agreement Sec. 5, read precisely.

    What is actually prohibited: an Amazon trademark (or a variant/misspelling) inside a **domain name,
    subdomain name, "tag"/Associates ID, or a username/group name/other identifier on a social site**; and
    copy that **affirmatively implies** endorsement, sponsorship or affiliation.  Descriptive reference to
    Amazon - including the mandated disclosure sentence and negations quoted from the Agreement itself - is
    not a violation, so those are not failed.
    """
    problems: list[str] = []
    reviews: list[str] = []

    # (a) identifiers we control and would publish
    if SITE_NAME_MARKS:
        problems.append(f"site name {SITE_NAME!r} contains an Amazon mark (R-11)")
    config = REPO / "ledger" / "site_config.json"
    if config.exists():
        tag = str(json.loads(config.read_text(encoding="utf-8")).get("associates_tag", "")).lower()
        for mark in ("amazon", "amzn", "prime", "kindle"):
            if mark in tag:
                problems.append(f"configured Associates tag {tag!r} contains an Amazon mark (R-11)")

    # (b) affirmative endorsement claims (negated mentions are quoted policy text, not claims)
    claim = re.compile(r"\b(?:officially )?(?:endorsed|sponsored|partnered|affiliated) with amazon\b", re.I)
    negation = re.compile(r"\b(?:not|no|never|avoid|prohibit|forbid|must not|cannot|free from)\b", re.I)
    for path in sorted(REPO.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            for m in claim.finditer(line):
                if negation.search(line[: m.start()][-160:]) or negation.search(line[max(0, m.start() - 160):m.end() + 40]):
                    continue
                problems.append(f"{path.relative_to(REPO)}: implies endorsement ({m.group(0)!r}) - Sec. 5")

    # (c) a title that leads with a mark can read as an official Amazon property: surface for review only
    for path in sorted(REPO.rglob("*.html")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<title>\s*([A-Z][^<]{0,80})", text)
        if m and re.match(r"^(amazon|amzn|prime|kindle)\b", m.group(1), re.I):
            reviews.append(f"{path.relative_to(REPO)}: <title> starts with an Amazon mark ({m.group(1)[:40]!r})")

    for prob in problems:
        report.fail(prob)
    for rev in reviews:
        report.warn(rev)
    report.stats["mark_findings"] = len(problems)
    report.stats["mark_review_notes"] = len(reviews)


def check_disclosure(report: Report) -> None:
    required = "As an Amazon Associate I earn from qualifying purchases."
    pages = list(owned_pages())
    for path in pages:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'rel="sponsored', text) and required not in text:
            report.fail(f"{path.relative_to(REPO)}: has a sponsored link but not the required Site disclosure (R-01)")
        if re.search(r'class="[^"]*sponsored-link', text) and "disclosure--link" not in text:
            report.fail(f"{path.relative_to(REPO)}: sponsored link without a link-level disclosure (R-02)")


SKIP_DIRS = {".git", "_site", ".cache", ".local", "node_modules", "__pycache__"}


def owned_pages():
    """Files this namespace polices: the generated subpages plus the shared landing page.

    The hub's root-level pages are generated and checked by scripts/verify.py, so re-checking them
    here would duplicate a sibling session's gate and fail on their internal conventions instead of ours.
    """
    roots = [REPO / "pages", REPO / "index.html"]
    for root in roots:
        if root.is_file():
            yield root
            continue
        for path in sorted(root.rglob("*.html")):
            if SKIP_DIRS.intersection(path.parts):
                continue
            yield path


PRICE_CONTEXT = re.compile(r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
# Commission/bounty/payment figures are program economics published in the rate statement, not product
# prices, so they are permitted; a dollar amount in a buying context is not.
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|stream|tax|refund|withhold)\w*", re.I
)


def check_landing_links_here(report: Report) -> None:
    """Discoverability: the primary landing page must link into the generated subpages.

    These pages are reachable by URL, but a namespace nobody can click into is effectively unpublished,
    and this repository has already restructured its root files twice. The check keeps the route intact.
    """
    index = REPO / "index.html"
    if not index.exists():
        report.warn("index.html missing - cannot verify the route into pages/")
        return
    text = index.read_text(encoding="utf-8", errors="ignore")
    linked = 'href="pages/index.html"' in text or 'href="pages/' in text
    if not linked:
        report.fail("index.html: no link into pages/ - the generated subpages would be unreachable from the site")
    else:
        report.stats["landing_links_to_pages"] = 1


def check_flag_count(report: Report) -> None:
    """The dashboard renders a flag count. It must equal the canonical register, never be typed.

    F-17 fixed a typed KPI that read "11 items flagged" while the ledger held 19. The fix derived the
    number from FLAGGED_ROWS, which is the *reader-facing subset*, not the register — so the dashboard
    still understated the site (14 vs 21) after flags were added. This check pins the constant to the
    ledger so the two cannot diverge again.
    """
    doc = _load("flags.json")
    canonical = len(doc.get("flags", []))
    js_path = REPO / "assets" / "js" / "data.js"
    if not js_path.exists():
        report.warn("assets/js/data.js missing - cannot verify the dashboard flag count")
        return
    js = js_path.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r"CANONICAL_FLAG_COUNT\s*=\s*(\d+)", js)
    if not m:
        report.fail("assets/js/data.js: CANONICAL_FLAG_COUNT is missing - the dashboard flag count is not derived from the ledger")
        return
    stated = int(m.group(1))
    if stated != canonical:
        report.fail(
            f"assets/js/data.js: CANONICAL_FLAG_COUNT={stated} but ledger/flags.json holds {canonical} flags "
            "- the dashboard would publish a flag count that disagrees with the register"
        )
    report.stats["canonical_flags"] = canonical

    # T26: the same defect appears one layer up. `index.html` and `flagged.html` used to
    # hard-code "26 items" / "26 flags" in their HTML, so they kept publishing the old
    # number after F-27 was added. A typed count in a template is the same bug as a typed
    # KPI, so refuse it: the caption must render from CANONICAL_FLAG_COUNT instead.
    typed = re.compile(r"(?<![-\w.])(\d{1,4})\s+(?:items?|flags)\b", re.I)
    for name in ("index.html", "flagged.html"):
        path = REPO / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        # Only the reader-facing caption prose matters here, not code samples or data rows.
        for line_no, line in enumerate(text.splitlines(), 1):
            if "<script" in line or "CANONICAL_FLAG_COUNT" in line:
                continue
            for m in typed.finditer(re.sub(r"<[^>]+>", " ", line)):
                stated_line = int(m.group(1))
                if stated_line != canonical:
                    report.fail(
                        f"{name}:{line_no}: typed count '{m.group(0)}' but the register holds "
                        f"{canonical} flags - derive the caption from CANONICAL_FLAG_COUNT"
                    )


def _flag_prose_pages():
    """Pages that speak for THIS namespace's register: the generated subpages plus the root dashboard.

    Deliberately narrower and wider than owned_pages(): it adds the root pages (products.html,
    flagged.html and friends are not in owned_pages()), and it excludes the companion namespaces —
    affiliate-lab/ publishes its OWN register and legitimately says "13 flags", and pages/flags.html
    quotes historical counts (11, 15) while narrating how F-17 and F-26 were found.
    """
    skip_rel = {"pages/flags.html"}
    seen = set()
    for path in sorted((REPO / "pages").rglob("*.html")):
        if SKIP_DIRS.intersection(path.parts):
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel in skip_rel:
            continue
        seen.add(path)
        yield path
    for path in sorted(REPO.glob("*.html")):
        rel = path.relative_to(REPO).as_posix()
        if rel in skip_rel or path in seen:
            continue
        yield path


def check_no_typed_flag_counts(report: Report) -> None:
    """Prose must not hardcode the size of the flag register; it drifts the moment a flag is added.

    F-26 pinned the *KPI* (CANONICAL_FLAG_COUNT) to the ledger. Root flagged.html still carried the
    sentence "26 flags (F-01 … F-26)" in hand-written prose, which no gate compared against the
    register — so when session ba8b2d38 added F-28 (the valid-ASIN control), the page went on telling
    readers the register held 26 while it held 27. Same defect class as F-26, different surface: a
    green `--check` proves the *data* matches the ledger, not that the sentence does.

    The page now renders the count from data; this check keeps a typed number from creeping back in.
    """
    doc = _load("flags.json")
    canonical = len(doc.get("flags", []))
    # A typed register size in prose looks like "26 flags", "26 items flagged", "26 open flags".
    # Deliberately narrow: an "F-01 … F-NN" range check was tried first and rejected, because pages
    # legitimately cite a SUBSET of flags that way (index.html cites <code>F-01…F-03</code> in a table
    # cell). Only a count phrase is unambiguous enough to fail the build on.
    pattern = re.compile(
        r"\b(\d+)\s+(?:flags|items flagged|open flags|flagged items)\b", re.IGNORECASE
    )
    for path in _flag_prose_pages():
        rel = path.relative_to(REPO).as_posix()
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in pattern.finditer(text):
            if int(m.group(1)) != canonical:
                report.fail(
                    f"{rel}: prose states '{m.group(0)}' but ledger/flags.json holds {canonical} - "
                    "render this number from the data (see #flagRegisterCount) instead of typing it"
                )
    report.stats["typed_flag_counts_checked"] = canonical


def check_no_product_prices(report: Report) -> None:
    """No generated page may display a product price.

    Amazon restricts price display to links it serves and to licensed API data, and a price pasted into a
    static page goes stale immediately (see the rules ledger, R-04/R-05). Dollar figures that describe
    program economics - bounty amounts, payment minimums - are allowed, because they are commission data
    quoted from the published statement rather than a product's price.
    """
    hits = []
    for path in owned_pages():
        text = path.read_text(encoding="utf-8", errors="ignore")
        # A row of a table, or a block of prose, is the unit of context: a bounty figure sits in a row
        # whose header says "Published rate", not in a product's price slot.
        units = re.split(r"</tr>|</p>|</li>|<br\s*/?>", re.sub(r"<[^>]+>", " ", text))
        for unit in units:
            for m in MONEY.finditer(unit):
                if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                    hits.append(f"{path.relative_to(REPO)}: money value {m.group(0)!r} in a buying context")
    for h in hits:
        report.fail(h)
    report.stats["price_findings"] = len(hits)


def check_links(report: Report) -> int:
    """Every internal href must resolve to a real file (no broken pages on deploy)."""
    checked = 0
    for path in owned_pages():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
                if href.startswith(("http://", "https://", "mailto:", "javascript:", "//")):
                    continue
                target = (path.parent / href).resolve()
                checked += 1
                if not target.exists():
                    report.fail(f"{path.relative_to(REPO)}: broken internal link -> {href}")
    report.stats["internal_links_checked"] = checked
    return checked


def main(strict: bool = True) -> Report:
    report = Report()
    try:
        sources = check_sources(report)
        check_rows(report, sources)
        check_products(report)
        check_cross_session_drift(report)
        check_marks(report)
        check_disclosure(report)
        check_landing_links_here(report)
        check_flag_count(report)
        check_no_typed_flag_counts(report)
        check_no_product_prices(report)
        check_links(report)
    except FileNotFoundError as exc:
        report.fail(f"required data file missing: {exc}")
    if strict:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        if report.errors:
            print(f"\nVALIDATION FAILED: {len(report.errors)} error(s)", file=sys.stderr)
            return report
    return report


if __name__ == "__main__":  # pragma: no cover
    sys.exit(1 if main().errors else 0)
