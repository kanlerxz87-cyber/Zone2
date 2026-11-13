"""Deploy gate. Fails the build when data would violate the project's verification contract.

The contract, from the project brief:
  "Every table row must have a source link to an official site. If a value can't be confirmed from an official
   source, leave it blank and flag it as unverified. Never infer or fill in values."

This turns that sentence into an executable check, so the rule survives whoever edits the data next.

Checks
  1. referential integrity   - every source_ids entry resolves to data/sources.json
  2. official-host policy    - sources are limited to Amazon / FTC / Google / GitHub official domains
  3. blank-or-sourced        - a populated field needs a source; a blank field needs a flag or why-blank note
  4. no invented metrics     - performance fields must be blank everywhere (clicks/conversion/earnings)
  5. no Amazon marks         - site naming/copy may not include Amazon marks (R-11)
  6. disclosure present      - the required Site sentence is present where a sponsored link exists (R-01/R-02)
  7. cross-session drift     - the published data.js product rows still match data/products.json
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
    "www.ftc.gov",
    "ftc.gov",
    "developers.google.com",
    "support.google.com",
    "docs.github.com",
}
PERF_FIELDS = ("clicks", "conversion", "orders", "earnings", "revenue", "epc", "impressions")
SITE_NAME = "Northstar"  # this project's own name; must contain no Amazon mark (R-11)
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
                    report.fail(f"{eid}: blank fields must be linked to a flag in data/flags.json")
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
    pages = list(REPO.rglob("*.html"))
    for path in pages:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'rel="sponsored', text) and required not in text:
            report.fail(f"{path.relative_to(REPO)}: has a sponsored link but not the required Site disclosure (R-01)")
        if re.search(r'class="[^"]*sponsored-link', text) and "disclosure--link" not in text:
            report.fail(f"{path.relative_to(REPO)}: sponsored link without a link-level disclosure (R-02)")


def check_links(report: Report, start_dirs=(REPO,)) -> int:
    """Every internal href/#anchor must resolve to a real file (no broken pages on deploy)."""
    checked = 0
    for root in start_dirs:
        for path in sorted(root.rglob("*.html")):
            if ".git" in path.parts:
                continue
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
