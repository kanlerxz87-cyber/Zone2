#!/usr/bin/env python3
"""Hold the audit/ namespace to the same contract as every other namespace in this repository.

A review page is the easiest place in a project to publish an unsourced opinion, so this gate
checks the things that would make this one untrustworthy:

  A1  every finding row is VERIFIED or explicitly UNVERIFIED with a reason — nothing in between
  A2  every VERIFIED row that cites an external rule carries a source id that resolves
  A3  every source id used anywhere resolves in audit/data/sources.json
  A4  no source is quoted without a URL, a fetch date and a re-checked marker
  A5  a source marked `carried` must say so on the rendered page (the label is not optional)
  A6  every recommendation names a finding, at least two options and one recommended option
  A7  every recommendation in a blocking state names the gap that blocks it
  A8  every gap names how it can be closed and who can close it
  A9  every decision-cost row points at a recommendation or a gap that exists
  A10 every count printed on a page equals the count derived from the data (no typed numbers)
  A11 the disclosure sentence is present on every audit page
  A12 no page prints a money value in a buying context (the same rule the whole repository uses)
  A13 every internal link and fragment resolves
  A14 the committed HTML matches a fresh build (drift is a failure, not a warning)

Each check is negative-tested in tools/test_audit.py: a gate that has never been made to fail is
a claim, not a control.

Usage:
    python3 tools/validate_audit.py            # report; non-zero exit on any error
    python3 tools/validate_audit.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_OUT = Path(os.environ["AUDIT_DATA_DIR"]) if os.environ.get("AUDIT_DATA_DIR") else None
AUDIT = _OUT if _OUT else REPO / "audit"
# Honoured only by tools/test_audit.py, so each check can be made to fail on purpose.
DATA = (_OUT / "data") if _OUT else AUDIT / "data"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|stream|tax|refund|withhold)\w*", re.I
)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: list[tuple[str, int]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and a.get("href"):
            self.refs.append((a["href"], self.getpos()[0]))
        if tag == "link" and a.get("rel") == "stylesheet":
            self.refs.append((a.get("href", ""), self.getpos()[0]))


def pages() -> list[Path]:
    return sorted(AUDIT.glob("*.html"))


def check_rows(findings: dict, sources: dict) -> list[str]:
    problems = []
    for f in findings["findings"]:
        st = f.get("status")
        if st not in ("VERIFIED", "UNVERIFIED"):
            problems.append(f"A1 {f['id']}: status {st!r} is not VERIFIED or UNVERIFIED")
        if st == "UNVERIFIED" and not f.get("unverified_because", "").strip():
            problems.append(f"A1 {f['id']}: UNVERIFIED without a reason (unverified_because is empty)")
        for sid in f.get("source_ids", []):
            if sid not in sources:
                problems.append(f"A3 {f['id']}: cites unknown source id {sid!r}")
        # A2: a row that quotes an external rule must carry a source
        if st == "VERIFIED" and not f.get("source_ids") and not f.get("unverified_because"):
            # permitted only for rows whose evidence is a repository measurement; make the
            # author say so explicitly rather than leaving it ambiguous
            if "measured" not in f.get("evidence", "").lower() and "counted" not in f.get("evidence", "").lower() \
               and "parsed" not in f.get("evidence", "").lower() and "read of" not in f.get("evidence", "").lower() \
               and "searched" not in f.get("evidence", "").lower() and "get " not in f.get("evidence", "").lower():
                problems.append(
                    f"A2 {f['id']}: VERIFIED with no source id and no stated measurement method"
                )
    return problems


def check_sources(sources: dict) -> list[str]:
    problems = []
    for sid, s in sources.items():
        for field in ("title", "url", "publisher", "fetched", "rechecked", "quote"):
            if not str(s.get(field, "")).strip():
                problems.append(f"A4 {sid}: missing {field}")
        if s.get("rechecked") not in ("yes", "carried"):
            problems.append(f"A4 {sid}: rechecked must be 'yes' or 'carried', got {s.get('rechecked')!r}")
        if s.get("rechecked") == "carried" and "carried" not in s.get("fetched", ""):
            problems.append(f"A4 {sid}: marked carried but the fetch note does not say so")
        if not s.get("url", "").startswith("https://"):
            problems.append(f"A4 {sid}: url is not https")
    return problems


def check_suggestions(sugg: dict, findings: dict, gaps: dict) -> list[str]:
    problems = []
    finding_ids = {f["id"] for f in findings["findings"]}
    gap_ids = {g["id"] for g in gaps["gaps"]}
    for r in sugg["recommendations"]:
        if r["finding"] not in finding_ids:
            problems.append(f"A6 {r['id']}: names finding {r['finding']!r} which does not exist")
        if len(r.get("options", [])) < 2:
            problems.append(f"A6 {r['id']}: fewer than two options")
        if not r.get("recommended"):
            problems.append(f"A6 {r['id']}: no recommended option")
        elif r["recommended"] not in {o["id"] for o in r["options"]}:
            problems.append(f"A6 {r['id']}: recommended option {r['recommended']!r} is not one of its options")
        if r["status"] == "blocked_on_information" and not r.get("depends_on"):
            problems.append(f"A7 {r['id']}: blocked_on_information but names no blocking gap")
        for g in r.get("depends_on", []):
            if g not in gap_ids:
                problems.append(f"A7 {r['id']}: depends on unknown gap {g!r}")
        for field in ("cost", "risk", "reversible", "why", "suggestion"):
            if not str(r.get(field, "")).strip():
                problems.append(f"A6 {r['id']}: missing {field}")
        # every cost/risk statement must declare itself an estimate, since it is not a program fact
        for field in ("cost", "risk"):
            if not str(r.get(field, "")).startswith("estimate:"):
                problems.append(f"A6 {r['id']}: {field} does not declare itself an estimate")
    return problems


def check_gaps(gaps: dict, sugg: dict) -> list[str]:
    problems = []
    rec_ids = {r["id"] for r in sugg["recommendations"]}
    for g in gaps["gaps"]:
        if not g.get("how_to_close", "").strip():
            problems.append(f"A8 {g['id']}: names no way to close it")
        if not g.get("who", "").strip():
            problems.append(f"A8 {g['id']}: names nobody who can close it")
        if g["status"] not in ("OPEN", "PARTIALLY_ANSWERED", "ANSWERED"):
            problems.append(f"A8 {g['id']}: unknown status {g['status']!r}")
        for b in g.get("blocks", []):
            if b not in rec_ids and not re.fullmatch(r"D-\d\d", b):
                problems.append(f"A8 {g['id']}: blocks unknown id {b!r}")
    return problems


def check_cost(cost: dict, sugg: dict, gaps: dict) -> list[str]:
    problems = []
    rec_ids = {r["id"] for r in sugg["recommendations"]}
    gap_ids = {g["id"] for g in gaps["gaps"]}
    for d in cost["decisions"]:
        if d.get("recommendation") and d["recommendation"] not in rec_ids:
            problems.append(f"A9 {d['id']}: points at unknown recommendation {d['recommendation']!r}")
        if d.get("gap") and d["gap"] not in gap_ids:
            problems.append(f"A9 {d['id']}: points at unknown gap {d['gap']!r}")
        if not d.get("consequence_of_waiting", "").strip():
            problems.append(f"A9 {d['id']}: does not state what happens if nothing is decided")
    return problems


def derivable_counts() -> set[int]:
    """Every number that can legitimately appear in a count card, computed from the data."""
    findings = load("findings.json")["findings"]
    recs = load("suggestions.json")["recommendations"]
    gaps = load("gaps.json")["gaps"]
    cost = load("decision-cost.json")["decisions"]
    traffic = load("traffic.json")
    out = {
        len(findings), len(recs), len(gaps), len(cost),
        sum(len(s["rows"]) for s in traffic["sections"]),
        sum(1 for f in findings if f["severity"] == "high"),
        sum(1 for f in findings if f["status"] == "UNVERIFIED"),
        sum(1 for f in findings if f["severity"] == "none"),
        sum(1 for r in recs if r["status"] == "awaiting_owner_decision"),
        sum(1 for r in recs if r["status"] == "blocked_on_information"),
        sum(1 for r in recs if r["status"] == "implemented_this_session"),
        sum(1 for g in gaps if g["status"] == "OPEN"),
        sum(1 for g in gaps if g["status"] == "PARTIALLY_ANSWERED"),
        sum(1 for x in cost if x["sequence"].startswith("1")),
        sum(1 for x in cost if x["reversible"].startswith("yes")),
        len(traffic["cannot_verify"]),
        sum(1 for s in traffic["sections"] for r in s["rows"] if r["verdict"].startswith("MET")),
        sum(1 for s in traffic["sections"] for r in s["rows"] if r["verdict"].startswith("PARTIAL")),
        sum(1 for s in traffic["sections"] for r in s["rows"] if r["verdict"].startswith("NOT MET")),
        sum(1 for s in load("sources.json")["sources"] if s.get("rechecked") == "carried"),
        len(load("sources.json")["sources"]),
        # the page count is a measurement recorded in the findings data, not a typed number
        int(load("findings.json")["repo_state"]["pages_published"]),
        0,  # "answers invented" — the card that states the register holds no inference
    }
    return out


def check_counts(parsed: dict[str, Page], html_text: dict[str, str]) -> list[str]:
    problems = []
    findings = load("findings.json")["findings"]
    recs = load("suggestions.json")["recommendations"]
    gaps = load("gaps.json")["gaps"]
    traffic = load("traffic.json")
    cost = load("decision-cost.json")["decisions"]

    derived = {
        "audit/index.html": len(findings),
        "audit/suggestions.html": len(recs),
        "audit/gaps.html": len(gaps),
        "audit/decision-cost.html": len(cost),
    }
    # The first count on each page is the row count of the data that drives it. Compare every
    # rendered count on that page against every value derivable from the same data, so a stale
    # number in the second card cannot hide behind a correct first one.
    for page, n in derived.items():
        text = html_text[page]
        rendered = [int(x) for x in re.findall(r'<div class="c"><b>(\d+)</b><span>', text)]
        if not rendered:
            problems.append(f"A10 {page}: no derived count found")
            continue
        if rendered[0] != n:
            problems.append(f"A10 {page}: first count says {rendered[0]} but the data holds {n}")
        # every rendered count must be reproducible from the files this namespace owns
        allowed = set(derivable_counts())
        allowed.add(n)
        for v in rendered:
            if v not in allowed:
                problems.append(
                    f"A10 {page}: renders the number {v}, which is not derivable from audit/data/*.json"
                )

    # the traffic page's rule count
    rules = sum(len(s["rows"]) for s in traffic["sections"])
    text = html_text["audit/traffic.html"]
    m = re.search(r'<div class="c"><b>(\d+)</b><span>documented rules checked', text)
    if not m or int(m.group(1)) != rules:
        problems.append(f"A10 audit/traffic.html: rule count does not match the data ({rules})")

    # findings page's own severity and status counts
    high = sum(1 for f in findings if f["severity"] == "high")
    m = re.search(r'<div class="c"><b>(\d+)</b><span>high severity', html_text["audit/index.html"])
    if not m or int(m.group(1)) != high:
        problems.append(f"A10 audit/index.html: high-severity count does not match the data ({high})")
    unv = sum(1 for f in findings if f["status"] == "UNVERIFIED")
    m = re.search(r'<div class="c"><b>(\d+)</b><span>explicitly unverified', html_text["audit/index.html"])
    if not m or int(m.group(1)) != unv:
        problems.append(f"A10 audit/index.html: unverified count does not match the data ({unv})")
    return problems


def check_pages() -> list[str]:
    problems = []
    html_text = {}
    parsed = {}
    for p in pages():
        text = p.read_text(encoding="utf-8")
        # Under a test redirect the page lives in a temp root; key it the same way either way.
        key = f"audit/{p.name}"
        html_text[key] = text
        if DISCLOSURE not in text:
            problems.append(f"A11 {p.name}: missing the required disclosure sentence")
        # A12: no product price in a buying context (split first, then strip tags: CR-4 / FL-13)
        units = [re.sub(r"<[^>]+>", " ", u) for u in re.split(r"</tr>|</p>|</li>|<br\s*/?>", text)]
        for unit in units:
            for m in MONEY.finditer(unit):
                if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                    problems.append(f"A12 {p.name}: money value {m.group(0)!r} in a buying context")
        pg = Page()
        pg.feed(text)
        parsed[p.name] = pg
        for ref, line in pg.refs:
            if ref.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, frag = ref.partition("#")
            tgt = (p.parent / target).resolve() if target else p
            if not tgt.is_file():
                problems.append(f"A13 {p.name}:{line}: missing {ref}")
                continue
            if frag:
                tp = parsed.get(tgt.name) if tgt.parent == p.parent else None
                if tp is None:
                    tp = Page()
                    tp.feed(tgt.read_text(encoding="utf-8"))
                if frag not in tp.ids:
                    problems.append(f"A13 {p.name}:{line}: fragment #{frag} addresses nothing in {tgt.name}")
    return problems, html_text


def check_carried_labels(html_text: dict[str, str], sources: dict) -> list[str]:
    problems = []
    text = html_text["audit/method.html"]
    for sid, s in sources.items():
        if s.get("rechecked") == "carried":
            # the method page must render the carried badge on that row
            row = re.search(rf'<td class="id">{re.escape(sid)}</td>.*?</tr>', text, re.S)
            if not row:
                problems.append(f"A5 {sid}: carried source does not appear on the method page")
            elif 'badge warn">carried' not in row.group(0):
                problems.append(f"A5 {sid}: carried source is rendered without the carried badge")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sources = {s["id"]: s for s in load("sources.json")["sources"]}
    findings = load("findings.json")
    sugg = load("suggestions.json")
    gaps = load("gaps.json")
    traffic = load("traffic.json")
    cost = load("decision-cost.json")

    page_problems, html_text = check_pages()

    # drift
    sys.path.insert(0, str(REPO / "tools"))
    import build_audit  # noqa: E402

    fresh = build_audit.build()
    drift = [rel for rel, text in fresh.items()
             if not (REPO / rel).is_file() or (REPO / rel).read_text(encoding="utf-8") != text]

    problems = {
        "rows": check_rows(findings, sources),
        "sources": check_sources(sources),
        "suggestions": check_suggestions(sugg, findings, gaps),
        "gaps": check_gaps(gaps, sugg),
        "decision_cost": check_cost(cost, sugg, gaps),
        "counts": check_counts(None, html_text),
        "pages": page_problems,
        "carried_labels": check_carried_labels(html_text, sources),
        "drift": [f"A14 committed output drifted: {d}" for d in drift],
    }

    total = sum(len(v) for v in problems.values())
    if args.json:
        print(json.dumps({"ok": total == 0, "errors": total, "by_check": {k: len(v) for k, v in problems.items()},
                          "detail": problems}, indent=2))
    else:
        for name, errs in problems.items():
            status = "PASS" if not errs else f"FAIL ({len(errs)})"
            print(f"  {name:16s} {status}")
            for err in errs:
                print(f"      {err}")
        print()
        print(f"{total} error(s) — {'OK' if total == 0 else 'FAILED'}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
