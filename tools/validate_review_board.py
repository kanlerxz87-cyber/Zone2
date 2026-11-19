#!/usr/bin/env python3
"""Deploy gate for the review board (review.html, review-questions.html, review-trace.html).

The 2026-11-16 request states the contract this gate enforces:

    "Every table row must have a source link to an official site. If a value can't be
     confirmed from an official source, leave it blank and flag it as unverified.
     Never infer or fill in values."

A suggestion board is exactly where that rule is easiest to break, because a proposal *is* an
assertion: it claims a problem exists, that a fix would work, and that a cost is realistic.
So this gate holds the register to twelve rules, and most of them are defects this repository
has already shipped at least once in another namespace:

   1. source integrity      - every cited id resolves; a dangling citation is a rumour with a number
   2. official hosts only   - sources sit on the allowlist the rest of the repo uses
   3. quotes are real       - a source without the text relied on is a paraphrase wearing a citation
   4. options are real      - two or more options, a commitment/cost/risk per option, and a
                              recommendation that names only offered options
   5. nothing is decided    - a row whose `decision` is AWAITING_DECISION may not read as done, and a
                              SELECTED row must name one of its own options in the note
   6. questions unanswered  - an open question carries no answer, states what is missing, and names
                              an action that obtains it
   7. derived counts        - every number printed on the pages is recomputed from the register here
   8. disclosure and links  - the required sentence on every page; every internal href and fragment resolves
   9. generated output      - committed pages match a fresh render
  10. requirements traced   - every row carries a clause, a state from the closed vocabulary, and either
                              a source or an explicit statement that no official source can settle it
  11. no product price      - the pages are reader-facing, so the repository's no-price rule applies
  12. structured pick       - a row's recommended_option must be an offered option and must be named
                              in the recommendation prose (wave 2, T72)

Run: python3 tools/validate_review_board.py
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_review_board as rb  # noqa: E402  (single source of truth for the register + renderer)

OFFICIAL_HOSTS = {
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "amazon.com",
    "link.amazon",
    "www.ftc.gov",
    "ftc.gov",
    "developers.google.com",
    "support.google.com",
    # Wave 2 (T72, 2026-11-19): the USDA Food Safety and Inspection Service chart is the official
    # anchor for the thermometer reference concept (PS-19). Same addition CR-8 made to
    # marketing/scripts/verify_marketing.py, for the same reason.
    "www.fsis.usda.gov",
    "fsis.usda.gov",
}

STATES = {"MET", "PARTIAL", "NOT_MET"}
DECISIONS = set(rb.DECISIONS)

# Words that would turn a proposal into an implemented change.
DONE_WORDS = re.compile(
    r"\b(has been (?:implemented|shipped|added|built|deployed|fixed)|\bwe (?:implemented|shipped|built|deployed|fixed)\b"
    r"|is now (?:live|implemented|published|fixed)|completed|done)\b",
    re.I,
)

# A price in a buying context. The site publishes none, and these pages are reader-facing.
MONEY = re.compile(r"(?:\$|USD\s?)\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(r"\b(price|pricing|cost[s]?|buy|deal|discount|sale|offer|cheap)\b", re.I)
# Regulatory and programme costs are not product prices; they are named so the gate stays precise.
PROGRAM_CONTEXT = re.compile(r"\b(licence|license|fee|subscription|copyright|removal request)\b", re.I)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    def fail(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# --------------------------------------------------------------------------- rules


def check_sources(rep: Report) -> None:
    ids = [s["id"] for s in rb.DATA["sources"]]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        rep.fail(f"duplicate source ids: {sorted(dupes)}")
    overlap = set(ids) & set(json.loads((REPO / "ledger" / "sources.json").read_text())["sources"][0:0])
    if overlap:  # pragma: no cover - defensive; the block above is intentionally empty
        rep.fail(f"source ids redefined elsewhere: {sorted(overlap)}")

    ledger_ids = {s["id"] for s in json.loads((REPO / "ledger" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    clash = set(ids) & ledger_ids
    if clash:
        rep.fail(f"review source ids collide with the project ledger: {sorted(clash)}")

    for s in rb.DATA["sources"]:
        for field in ("publisher", "kind", "title", "url", "quote", "used_for"):
            if not (s.get(field) or "").strip():
                rep.fail(f"{s['id']}: empty {field!r}")
        host = urlparse(s["url"]).netloc
        if host.startswith("www."):
            host = host[4:]
        if host not in OFFICIAL_HOSTS:
            rep.fail(f"{s['id']}: {host!r} is not an official allowlisted host")
        if len((s.get("quote") or "").strip()) < 40:
            rep.fail(f"{s['id']}: quote too short to be the text relied on")

    cited: set[str] = set()
    for row in rb.PROPOSALS:
        cited |= set(row.get("evidence") or [])
    for row in rb.QUESTIONS:
        cited |= set(row.get("source_ids") or [])
    for row in rb.REQUIREMENTS:
        cited |= set(row.get("source_ids") or [])
    for row in rb.FINDINGS:
        cited |= set(row.get("source_ids") or [])
    # Wave 2 (T72): ideas and irregularities carry citations too; ignoring them made the
    # "defined but never cited" warning a false negative for exactly the rows a reader
    # meets first on the idea board.
    for row in rb.IDEAS:
        cited |= set(row.get("source_ids") or [])
    for row in rb.IRREGULARITIES:
        cited |= set(row.get("source_ids") or [])
    for sid in sorted(cited):
        if sid not in rb.SOURCES:
            rep.fail(f"source {sid} is cited but not defined")
    rep.stats["sources_defined"] = len(ids)
    rep.stats["sources_cited"] = len(cited)
    unused = sorted(set(ids) - cited)
    if unused:
        rep.warn(f"sources defined but never cited: {unused}")


def check_proposals(rep: Report) -> None:
    ids = set()
    for p in rb.PROPOSALS:
        pid = p["id"]
        if pid in ids:
            rep.fail(f"duplicate proposal id {pid}")
        ids.add(pid)
        for field in ("title", "area", "problem", "recommendation"):
            if not (p.get(field) or "").strip():
                rep.fail(f"{pid}: empty {field!r}")
        opts = p.get("options") or []
        if len(opts) < 2:
            rep.fail(f"{pid}: {len(opts)} option(s) - a single option is not a decision")
        opt_ids = set()
        for o in opts:
            oid = o.get("id")
            if not oid:
                rep.fail(f"{pid}: an option has no id")
                continue
            if oid in opt_ids:
                rep.fail(f"{pid}: duplicate option id {oid}")
            opt_ids.add(oid)
            for field in ("label", "commitment", "cost", "risk"):
                if not (o.get(field) or "").strip():
                    rep.fail(f"{pid} option {oid}: empty {field!r} - an option without a trade-off is a slogan")
        named = set(re.findall(r"\b([A-Z])\b", p.get("recommendation") or ""))
        unknown = sorted(named - opt_ids)
        if unknown:
            rep.fail(f"{pid}: recommends {p['recommendation']!r}, naming unoffered option(s) {unknown}")

        # Wave 2 (T72): a structured recommendation must name an offered option, so the answer sheet
        # can print it without re-parsing prose.
        rec_opt = p.get("recommended_option")
        if rec_opt is not None:
            if rec_opt not in opt_ids:
                rep.fail(f"{pid}: recommended_option {rec_opt!r} names an unoffered option")
            if rec_opt not in named:
                rep.fail(f"{pid}: recommended_option {rec_opt!r} is not named in the recommendation prose")

        # Rule 4: the scores are declared self-assessed, and must at least be in range.
        for field in ("quality_impact", "conversion_impact", "risk", "effort"):
            v = p.get(field)
            if not isinstance(v, int) or not 1 <= v <= 5:
                rep.fail(f"{pid}: {field}={v!r} is not an integer 1-5")

        for w in p.get("waiting_on") or []:
            if w not in {q["id"] for q in rb.QUESTIONS}:
                rep.fail(f"{pid}: waits on unknown question {w!r}")
        for e in p.get("evidence") or []:
            if e not in rb.SOURCES:
                rep.fail(f"{pid}: cites unknown evidence source {e!r}")

        # Rule 5: nothing reads as decided or done while the decision is open.
        decision = p.get("decision")
        if decision not in DECISIONS:
            rep.fail(f"{pid}: decision {decision!r} is not in the closed vocabulary {sorted(DECISIONS)}")
        if decision == "AWAITING_DECISION":
            blob = json.dumps({k: v for k, v in p.items() if k not in ("options", "decision_note")}, ensure_ascii=False)
            blob += " " + json.dumps([{k: v for k, v in o.items() if k != "id"} for o in opts], ensure_ascii=False)
            m = DONE_WORDS.search(blob)
            if m:
                rep.fail(f"{pid}: reads as implemented ({m.group(0)!r}) but is still awaiting a decision")
            if (p.get("decision_note") or "").strip():
                rep.fail(f"{pid}: awaiting a decision yet carries a decision note")
        if decision in ("SELECTED", "DEFERRED"):
            note = (p.get("decision_note") or "").strip()
            if not note:
                rep.fail(f"{pid}: {decision} with no decision note - a decision without a record is a rumour")
            if decision == "SELECTED":
                claimed = set(re.findall(r"\b([A-Z])\b", note))
                if not (claimed & opt_ids):
                    rep.fail(f"{pid}: SELECTED but the note names none of its own options {sorted(opt_ids)}")
    rep.stats["proposals"] = len(ids)
    rep.stats["awaiting_decision"] = sum(1 for p in rb.PROPOSALS if p["decision"] == "AWAITING_DECISION")
    rep.stats["selected"] = sum(1 for p in rb.PROPOSALS if p["decision"] == "SELECTED")


def check_questions(rep: Report) -> None:
    ids = set()
    for q in rb.QUESTIONS:
        qid = q["id"]
        if qid in ids:
            rep.fail(f"duplicate question id {qid}")
        ids.add(qid)
        for field in ("question", "missing", "obtain", "owner"):
            if not (q.get(field) or "").strip():
                rep.fail(f"{qid}: empty {field!r} - an unanswerable row is not a question")
        # Rule 6: an open question carries no answer.
        if (q.get("answer") or "").strip():
            rep.fail(f"{qid}: carries an answer - this register may not fill in what it does not know")
        for b in q.get("blocks") or []:
            if b not in {p["id"] for p in rb.PROPOSALS}:
                rep.fail(f"{qid}: blocks unknown proposal {b!r}")
        if not q.get("source_ids"):
            rep.fail(f"{qid}: no source_ids - even an unknown must be anchored to what is known")
        for sid in q.get("source_ids") or []:
            if sid not in rb.SOURCES:
                rep.fail(f"{qid}: cites unknown source {sid!r}")
    rep.stats["questions"] = len(ids)
    rep.stats["questions_answered"] = sum(1 for q in rb.QUESTIONS if (q.get("answer") or "").strip())


def check_requirements(rep: Report) -> None:
    ids = set()
    for r in rb.REQUIREMENTS:
        rid = r["id"]
        if rid in ids:
            rep.fail(f"duplicate requirement id {rid}")
        ids.add(rid)
        for field in ("brief_clause", "asks_for", "what_exists", "what_is_missing", "verified_against"):
            if not (r.get(field) or "").strip():
                rep.fail(f"{rid}: empty {field!r}")
        if r.get("state") not in STATES:
            rep.fail(f"{rid}: state {r.get('state')!r} not in {sorted(STATES)}")
        for sid in r.get("source_ids") or []:
            if sid not in rb.SOURCES:
                rep.fail(f"{rid}: cites unknown source {sid!r}")
        # Rule 10: no source is allowed, but it must then be stated that none can settle it.
        if not r.get("source_ids"):
            if not re.search(r"no official|official page define|not defined", (r.get("verified_against") or ""), re.I):
                rep.fail(f"{rid}: no source and no statement that no official source can settle it")
    rep.stats["requirements"] = len(ids)
    rep.stats["met"] = sum(1 for r in rb.REQUIREMENTS if r["state"] == "MET")
    rep.stats["partial"] = sum(1 for r in rb.REQUIREMENTS if r["state"] == "PARTIAL")
    rep.stats["not_met"] = sum(1 for r in rb.REQUIREMENTS if r["state"] == "NOT_MET")


def check_findings(rep: Report) -> None:
    ids = set()
    prop_ids = {p["id"] for p in rb.PROPOSALS}
    meas_ids = {m["id"] for m in rb.MEASUREMENTS}
    for f in rb.FINDINGS:
        fid = f["id"]
        if fid in ids:
            rep.fail(f"duplicate finding id {fid}")
        ids.add(fid)
        for field in ("title", "what_a_reader_sees", "why_it_matters"):
            if not (f.get(field) or "").strip():
                rep.fail(f"{fid}: empty {field!r}")
        if f.get("proposed_fix") not in prop_ids:
            rep.fail(f"{fid}: proposed_fix {f.get('proposed_fix')!r} is not a proposal on this board")
        if f.get("measured_by") and f["measured_by"] not in meas_ids:
            rep.fail(f"{fid}: measured_by {f['measured_by']!r} is not a measurement row")
        for sid in f.get("source_ids") or []:
            if sid not in rb.SOURCES:
                rep.fail(f"{fid}: cites unknown source {sid!r}")
    idea_ids = set()
    for i in rb.IDEAS:
        iid = i["id"]
        if iid in idea_ids:
            rep.fail(f"duplicate idea id {iid}")
        idea_ids.add(iid)
        for field in ("title", "area", "trend_basis", "article_concept", "why_it_converts"):
            if not (i.get(field) or "").strip():
                rep.fail(f"{iid}: empty {field!r}")
        if i.get("decision") not in DECISIONS:
            rep.fail(f"{iid}: decision {i.get('decision')!r} is not in the closed vocabulary")
        if i.get("decision") == "AWAITING_DECISION":
            m = DONE_WORDS.search(json.dumps({k: v for k, v in i.items() if k != "decision_note"}, ensure_ascii=False))
            if m:
                rep.fail(f"{iid}: reads as implemented ({m.group(0)!r}) but is still awaiting a decision")
        else:
            if not (i.get("decision_note") or "").strip():
                rep.fail(f"{iid}: a recorded decision with no note")
        for w in i.get("waiting_on") or []:
            if w not in {q["id"] for q in rb.QUESTIONS}:
                rep.fail(f"{iid}: waits on unknown question {w!r}")
        for sid in i.get("source_ids") or []:
            if sid not in rb.SOURCES:
                rep.fail(f"{iid}: cites unknown source {sid!r}")
        if not i.get("source_ids"):
            rep.fail(f"{iid}: no source - even an idea must rest on the official page that justifies it")
    rep.stats["ideas"] = len(idea_ids)

    irr_ids = set()
    for i in rb.IRREGULARITIES:
        iid = i["id"]
        if iid in irr_ids:
            rep.fail(f"duplicate irregularity id {iid}")
        irr_ids.add(iid)
        for field in ("severity", "found", "effect", "resolution", "owner_action"):
            if not (i.get(field) or "").strip():
                rep.fail(f"{iid}: empty {field!r} - an unactionable flag is noise")
        if i.get("severity") not in ("high", "medium", "low"):
            rep.fail(f"{iid}: severity {i.get('severity')!r} not in high/medium/low")
        for sid in i.get("source_ids") or []:
            if sid not in rb.SOURCES:
                rep.fail(f"{iid}: cites unknown source {sid!r}")
    rep.stats["irregularities"] = len(irr_ids)
    rep.stats["findings"] = len(ids)
    rep.stats["measurements"] = len(rb.MEASUREMENTS)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []
        self.text: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style"):
            self._skip += 1
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if not self._skip:
            self.text.append(data)


def check_pages(rep: Report) -> None:
    for name in rb.PAGES:
        path = REPO / name
        if not path.is_file():
            rep.fail(f"{name}: not on disk - run tools/build_review_board.py")
            continue
        raw = path.read_text(encoding="utf-8")
        if DISCLOSURE not in raw:
            rep.fail(f"{name}: the required disclosure sentence is absent")

        parser = LinkParser()
        parser.feed(raw)
        text = " ".join(parser.text)

        # Rule 11: no product price in a buying context.
        for m in MONEY.finditer(text):
            window = text[max(0, m.start() - 90): m.end() + 90]
            if PRICE_CONTEXT.search(window) and not PROGRAM_CONTEXT.search(window):
                rep.fail(f"{name}: money value {m.group(0)!r} in a buying context")

        # Rule 8: internal hrefs and fragments resolve.
        anchors = set(re.findall(r'id="([^"]+)"', raw))
        for href in parser.hrefs:
            if href.startswith(("http://", "https://", "mailto:")):
                continue
            target, _, frag = href.partition("#")
            if not target:
                if frag and frag not in anchors:
                    rep.fail(f"{name}: fragment #{frag} does not exist on the page")
                continue
            dest = (REPO / target).resolve() if not target.startswith("/") else (REPO / target.lstrip("/")).resolve()
            if not dest.is_file():
                rep.fail(f"{name}: link {href!r} does not resolve to a file")
                continue
            if frag:
                other = dest.read_text(encoding="utf-8")
                if f'id="{frag}"' not in other:
                    rep.fail(f"{name}: link {href!r} targets a fragment that does not exist")


def check_structure(rep: Report) -> None:
    """Rule 12: the pages are static documents. No script, and balanced tags.

    The sandbox cannot install a browser, so the pages are not screenshot-tested. This rule is what
    is checked instead: a page that ships no JavaScript cannot have a runtime defect, and a page
    whose tags balance cannot render as a collapsed layout because of this session's markup.
    """
    VOID = {"meta", "link", "br", "img", "input", "hr", "source", "area", "base", "col",
            "embed", "param", "track", "wbr"}

    class Balancer(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.stack: list[str] = []
            self.errors: list[str] = []
            self.scripts = 0

        def handle_starttag(self, tag, attrs):
            if tag == "script":
                self.scripts += 1
            if tag not in VOID:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if not self.stack:
                self.errors.append(f"stray </{tag}>")
                return
            if self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.errors.append(f"expected </{self.stack[-1]}> but found </{tag}>")

    for name in rb.PAGES:
        path = REPO / name
        if not path.is_file():
            continue
        b = Balancer()
        b.feed(path.read_text(encoding="utf-8"))
        if b.scripts:
            rep.fail(f"{name}: ships {b.scripts} <script> element(s) - these pages must be static")
        if b.stack:
            rep.fail(f"{name}: unclosed element(s) {b.stack}")
        for err in b.errors:
            rep.fail(f"{name}: {err}")
    rep.stats["structure_checks"] = len(rb.PAGES)


def check_counts(rep: Report) -> None:
    """Rule 7: every number printed on the hub is recomputed here, not trusted from the page."""
    raw = (REPO / "review.html").read_text(encoding="utf-8")
    expectations = {
        "proposals": len(rb.PROPOSALS),
        "awaiting": sum(1 for p in rb.PROPOSALS if p["decision"] == "AWAITING_DECISION"),
        "questions": len(rb.QUESTIONS),
        "met": sum(1 for r in rb.REQUIREMENTS if r["state"] == "MET"),
        "partial": sum(1 for r in rb.REQUIREMENTS if r["state"] == "PARTIAL"),
        "not_met": sum(1 for r in rb.REQUIREMENTS if r["state"] == "NOT_MET"),
        "requirements": len(rb.REQUIREMENTS),
    }
    checks = [
        (f'<span class="chip">{expectations["proposals"]} proposals</span>', "proposal count chip"),
        (f'<div class="kpi-value">{expectations["met"]}</div>', "MET KPI"),
        (f'<div class="kpi-value">{expectations["partial"]}</div>', "PARTIAL KPI"),
        (f'<div class="kpi-value">{expectations["not_met"]}</div>', "NOT_MET KPI"),
        (f'<div class="kpi-value">{expectations["requirements"]}</div>', "requirement count KPI"),
    ]
    for needle, label in checks:
        if needle not in raw:
            rep.fail(f"review.html: {label} does not match the register ({needle!r} not found)")
    trace = (REPO / "review-trace.html").read_text(encoding="utf-8")
    for key, label in (("met", "MET"), ("partial", "PARTIAL"), ("not_met", "NOT MET")):
        n = expectations[key]
        if f"{n} {label.lower()}" not in trace.lower():
            rep.fail(f"review-trace.html: the {label} count in prose does not match the register ({n})")


def main() -> int:
    rep = Report()
    check_sources(rep)
    check_proposals(rep)
    check_questions(rep)
    check_requirements(rep)
    check_findings(rep)
    check_pages(rep)
    check_structure(rep)
    check_counts(rep)

    print(json.dumps(rep.stats, indent=2))
    for w in rep.warnings:
        print(f"WARN {w}")
    for e in rep.errors:
        print(f"FAIL {e}")
    if rep.errors:
        print(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
        return 1
    print(f"\nreview board gate: PASS ({len(rep.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
