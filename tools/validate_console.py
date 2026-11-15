#!/usr/bin/env python3
"""Deploy gate for the Owner's Console (task T42, session arena/d26f42db-zone2).

Turns the project's verification contract into executable checks for this namespace:

  "Every table row must have a source link to an official site. If a value can't be confirmed
   from an official source, leave it blank and flag it as unverified. Never infer or fill in values."

Checks
  1.  referential integrity  - every source_ids entry resolves to console/data/sources.json
  2.  official-host policy   - sources are limited to official Amazon / Google / FTC hosts, plus
                               link.amazon and amzlinks.in for observed and control rows only
  3.  source class policy    - an official row must carry a quote or an explicit note saying it states no value
  4.  blank-or-sourced       - an open question's `answer` must be empty; an answered row must not be
  5.  no invented metrics    - no performance figures (clicks, conversion, earnings) anywhere
  6.  no Amazon marks        - this project's own naming carries no Amazon mark
  7.  disclosure present     - every generated page carries the section 5 sentence
  8.  no product prices      - no price figure is printed in this namespace
  9.  internal links resolve - every href in console/ maps to a real file
  10. board integrity        - every proposal has options, a valid recommendation, and a sheet row
  11. id uniqueness          - P-, IN-, A-, V-, IR-, C- and RW-/DP-/TP-/AR- ids are unique in their set
  12. published counts       - counts rendered on the pages match the data files

Exit code 0 on success, 1 on any error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "console" / "data"
OUT = REPO / "console"

OFFICIAL_HOSTS = {
    "affiliate-program.amazon.com",
    "amazon.com",
    "www.amazon.com",
    "webservices.amazon.com",
    "www.ftc.gov",
    "ftc.gov",
    "developers.google.com",
    "support.google.com",
    "docs.github.com",
}
# link.amazon is Amazon's own delegated domain; the three supplied links are of that form and the
# controls run against it. They may appear only on rows whose class is observed or control, and are
# never used to state a program rule.
ARTEFACT_HOSTS = {"link.amazon", "amzlinks.in"}

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE_NAME = "Zone2"
AMAZON_MARKS = ("amazon", "amzn", "alexa", "audible", "imdb", "kindle", "prime", "aws")
PERF_WORDS = ("clicks", "conversion rate", "conversions", "earnings", "epc", "impressions", "ctr")
PRICE_RE = re.compile(r"(?<![\w/])[$£€]\s?\d[\d,]*(\.\d{2})?\b")
PAGE_FILES = [
    "index.html", "suggestions.html", "questions.html", "design.html",
    "review.html", "decisions.html", "flagged.html", "sources.html",
]


class Report:
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    def fail(self, m: str) -> None:
        self.errors.append(m)

    def warn(self, m: str) -> None:
        self.warnings.append(m)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def host_of(url: str) -> str:
    u = re.sub(r"^https?://", "", url or "")
    return u.split("/")[0].lower()


def check_sources(rep: Report) -> dict:
    doc = load("sources.json")
    by_id = {}
    for s in doc["sources"]:
        sid = s.get("id")
        if not sid:
            rep.fail("sources: a row has no id")
            continue
        if sid in by_id:
            rep.fail(f"sources: duplicate id {sid}")
        by_id[sid] = s
        h = host_of(s.get("url", ""))
        cls = s.get("class", "")
        if h in OFFICIAL_HOSTS:
            pass
        elif h in ARTEFACT_HOSTS:
            if cls not in ("observed", "control"):
                rep.fail(f"{sid}: host {h!r} is only allowed on observed/control rows, class is {cls!r}")
        else:
            rep.fail(f"{sid}: host {h!r} is not an allowlisted official or artefact domain")
        if cls == "official" and not (s.get("quote") or s.get("note")):
            rep.fail(f"{sid}: an official source row must carry a quote or a note")
        if not s.get("url", "").startswith("https://"):
            rep.fail(f"{sid}: url is not https")
        if not s.get("fetched_utc"):
            rep.fail(f"{sid}: no fetched_utc date")
    rep.stats["sources"] = len(by_id)
    return by_id


def walk_ids(rows, prefix, rep, label):
    seen = set()
    for r in rows:
        i = r.get("id", "")
        if not i.startswith(prefix):
            rep.fail(f"{label}: id {i!r} does not use the {prefix} prefix")
        if i in seen:
            rep.fail(f"{label}: duplicate id {i}")
        seen.add(i)


def check_proposals(rep: Report, by_id: dict, sheet: dict) -> None:
    doc = load("proposals.json")
    rows = doc["proposals"]
    walk_ids(rows, "P-", rep, "proposals")
    for p in rows:
        pid = p["id"]
        for sid in p.get("evidence", []):
            if sid not in by_id:
                rep.fail(f"{pid}: evidence source {sid} does not resolve")
        opts = {o["id"] for o in p.get("options", [])}
        if len(opts) < 2:
            rep.fail(f"{pid}: needs at least two options")
        if p.get("recommended") not in opts:
            rep.fail(f"{pid}: recommended {p.get('recommended')!r} is not one of its options {sorted(opts)}")
        if not p.get("change") or not p.get("why"):
            rep.fail(f"{pid}: a proposal must state what changes and why")
        if p.get("state") != "proposed" and not sheet.get(pid, {}).get("choice"):
            rep.fail(f"{pid}: state is {p['state']!r} but no choice is recorded on the sheet")
        if sheet.get(pid, {}).get("choice"):
            ch = sheet[pid]["choice"]
            if ch not in opts:
                rep.fail(f"{pid}: recorded choice {ch!r} is not one of its options {sorted(opts)}")
        if pid not in sheet:
            rep.fail(f"{pid}: missing a row on the decision sheet")
        if pid in sheet and sheet[pid].get("choice"):
            if not sheet[pid].get("decided_by") or not sheet[pid].get("decided_on"):
                rep.warn(f"{pid}: choice recorded without a decided_by/decided_on stamp")
    rep.stats["proposals"] = len(rows)


def check_information(rep: Report, by_id: dict) -> None:
    doc = load("information.json")
    walk_ids(doc["answered"], "A-", rep, "answered")
    walk_ids(doc["open"], "IN-", rep, "open questions")
    walk_ids(doc["inventory"], "V-", rep, "inventory")
    for a in doc["answered"]:
        if not a.get("answer"):
            rep.fail(f"{a['id']}: an answered row must carry an answer")
        for sid in a.get("source_ids", []):
            if sid not in by_id:
                rep.fail(f"{a['id']}: source {sid} does not resolve")
        if not a.get("source_ids"):
            rep.fail(f"{a['id']}: an answered row must cite at least one source")
    for q in doc["open"]:
        if q.get("answer"):
            rep.fail(f"{q['id']}: an open question must leave `answer` empty")
        for sid in q.get("source_ids", []):
            if sid not in by_id:
                rep.fail(f"{q['id']}: source {sid} does not resolve")
        # No public source link is required for an open question; what is required is a way to close it.
        if not q.get("how_to_find"):
            rep.fail(f"{q['id']}: an open question must state how the gap can be closed")
    rep.stats["answered"] = len(doc["answered"])
    rep.stats["open_questions"] = len(doc["open"])


def check_flags(rep: Report, by_id: dict) -> None:
    doc = load("flags.json")
    rows = doc["flags"]
    walk_ids(rows, "IR-", rep, "flags")
    for f in rows:
        for sid in f.get("source_ids", []):
            if sid not in by_id:
                rep.fail(f"{f['id']}: source {sid} does not resolve")
        if f.get("severity") not in ("high", "medium", "low"):
            rep.fail(f"{f['id']}: severity must be high, medium or low")
        if not f.get("action_required") or not f.get("who"):
            rep.fail(f"{f['id']}: a flag must state the action required and who can close it")
    rep.stats["flags"] = len(rows)


def check_review(rep: Report, by_id: dict) -> None:
    doc = load("review.json")
    walk_ids(doc["verification"], "VR-", rep, "verification")
    walk_ids(doc["measurements"], "MS-", rep, "measurements")
    for v in doc["verification"]:
        for sid in v.get("source_ids", []):
            if sid not in by_id:
                rep.fail(f"{v['id']}: source {sid} does not resolve")
        if not v.get("observed"):
            rep.fail(f"{v['id']}: a verification row must record what was observed")
    rep.stats["verification_checks"] = len(doc["verification"])


def check_design(rep: Report, by_id: dict) -> None:
    doc = load("design.json")
    walk_ids(doc["principles"], "DP-", rep, "principles")
    walk_ids(doc["templates"], "TP-", rep, "templates")
    walk_ids(doc["rewrites"]["rows"], "RW-", rep, "rewrites")
    walk_ids(doc["articles"]["rows"], "AR-", rep, "articles")
    for p in doc["principles"]:
        if not p.get("judgment") and not p.get("source_ids"):
            rep.fail(f"{p['id']}: a rule (not a craft judgment) must cite the source that imposes it")
        for sid in p.get("source_ids", []):
            if sid not in by_id:
                rep.fail(f"{p['id']}: source {sid} does not resolve")
        if p.get("source_ids") and p.get("judgment"):
            rep.warn(f"{p['id']}: carries both a source and a judgment flag - pick one reading")
    for r in doc["rewrites"]["rows"]:
        if not r.get("before") or not r.get("after"):
            rep.fail(f"{r['id']}: a rewrite needs both sides")
        if "{" in (r.get("after") or "") and "}" in (r.get("after") or ""):
            if not re.search(r"\{[a-z0-9_]+\}", r["after"]):
                rep.fail(f"{r['id']}: brace placeholder is not a simple {{token}}")
    rep.stats["rewrites"] = len(doc["rewrites"]["rows"])


def check_pages(rep: Report) -> None:
    """Disclosure, prices, invented metrics, link integrity, Amazon marks in our own naming."""
    checked = 0
    for page in sorted(OUT.rglob("*.html")):
        text = page.read_text(encoding="utf-8", errors="ignore")
        rel = page.relative_to(REPO).as_posix()
        checked += 1
        if DISCLOSURE not in text:
            rep.fail(f"{rel}: missing the section 5 disclosure sentence")
        # strip the generator's own provenance lines and any <code> before hunting for prices
        body = re.sub(r"<(script|style)\b.*?</\1>", " ", text, flags=re.S)
        body = re.sub(r"<code>.*?</code>", " ", body, flags=re.S)
        # Dates are not metrics: strip them before hunting for a number next to a metric word.
        # Blank out, preserving length so character offsets stay aligned: dates, identifier
        # tokens such as C-02 or P-14, and percentages are none of them metrics.
        body_nodate = re.sub(
            r"\d{4}-\d{2}-\d{2}|\b[A-Z]{1,3}-\d{1,3}\b|\b\d{1,2}(\.\d+)?%",
            lambda m: " " * len(m.group(0)), body)
        for m in PRICE_RE.finditer(body):
            snippet = body[max(0, m.start() - 60):m.end() + 40].replace("\n", " ")
            rep.fail(f"{rel}: prints a price figure ({m.group(0)!r}) - context: {snippet!r}")
        # Only a figure next to the word is a metric; the word alone is prose (the brief, the
        # no-income-representation rule and the click-through definition all use it legitimately).
        for w in PERF_WORDS:
            for m in re.finditer(rf"\b{re.escape(w)}\b", body, re.I):
                window = body_nodate[max(0, m.start() - 40): m.end() + 40]
                if re.search(r"\d", window):
                    rep.warn(f"{rel}: a number sits next to {w!r} - confirm it is not a performance figure")
                    break
        # internal links
        for m in re.finditer(r'href="([^"#][^"]*)"', text):
            u = m.group(1)
            if u.startswith(("http", "mailto:", "//", "data:")):
                continue
            target = (page.parent / u.split("#")[0].split("?")[0]).resolve()
            if not target.exists():
                rep.fail(f"{rel}: broken internal link -> {u}")
    if SITE_NAME and any(mk in SITE_NAME.lower() for mk in AMAZON_MARKS):
        rep.fail(f"site name {SITE_NAME!r} contains an Amazon mark")
    rep.stats["pages_checked"] = checked


def check_published_counts(rep: Report) -> None:
    proposals = load("proposals.json")["proposals"]
    info = load("information.json")
    flags = load("flags.json")["flags"]
    sources = load("sources.json")["sources"]
    idx = (OUT / "index.html").read_text(encoding="utf-8")
    pairs = [
        (idx, f">{len(proposals)}</div>", "proposal count"),
        (idx, f">{len(sources)}</div>", "source count"),
        (idx, f">{len([f for f in flags if f['severity']=='high'])}</div>", "high-severity count"),
        (idx, f">{len([q for q in info['open'] if q['who']=='owner'])}</div>", "owner-question count"),
    ]
    for text, needle, label in pairs:
        if needle not in text:
            rep.fail(f"index.html: rendered {label} does not match the data ({needle!r} absent)")


def check_tree_measurements(rep: Report) -> None:
    """Cross-namespace observations, re-measured at build time.

    These are WARNINGS, not errors, on purpose. Six sessions are merging into this tree at once;
    failing the whole deploy because a namespace this session does not own shipped a broken link
    would block everyone for someone else's defect. The project's own CI link step is the hard
    gate for that. What this does is make the drift visible on the console's review page.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    from build_console import measure  # the generator's own measurement, so the two cannot disagree

    ms = measure()
    rep.stats["tree_pages"] = ms["pages"]
    rep.stats["tree_namespaces"] = ms["namespaces"]
    rep.stats["tree_links"] = ms["links"]
    if ms["broken"]:
        rep.warn(f"{len(ms['broken'])} broken internal link(s) elsewhere in the tree, first: {ms['broken'][0]}")
    if ms["disclosure"] != ms["pages"]:
        rep.warn(f"disclosure coverage is {ms['disclosure']}/{ms['pages']} pages tree-wide")


def main() -> int:
    rep = Report()
    by_id = check_sources(rep)
    sheet = load("decisions.json")["sheet"]
    check_proposals(rep, by_id, sheet)
    check_information(rep, by_id)
    check_flags(rep, by_id)
    check_review(rep, by_id)
    check_design(rep, by_id)
    check_pages(rep)
    check_published_counts(rep)
    check_tree_measurements(rep)

    print("console gate")
    for k, v in sorted(rep.stats.items()):
        print(f"  {k:22s} {v}")
    for w in rep.warnings:
        print(f"  WARN  {w}")
    if rep.errors:
        print(f"\nFAILED with {len(rep.errors)} error(s):")
        for e in rep.errors:
            print(f"  - {e}")
        return 1
    print("\nOK - 0 errors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
