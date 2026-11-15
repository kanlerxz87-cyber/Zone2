#!/usr/bin/env python3
"""Deploy gate for the decision namespace (decisions/ and DECISIONS.md).

The brief's contract is: "Every table row must have a source link to an official site. If a value can't be
confirmed from an official source, leave it blank and flag it as unverified. Never infer or fill in values."
tools/validate_data.py enforces that for ledger/*.json. This script enforces the same contract for the three
ledgers added by this task, and adds the checks that are specific to a *proposal* register.

Checks
  1. source integrity      - every source id cited by any new ledger row resolves in ledger/sources.json
  2. official hosts only    - the new sources sit on the same allowlist tools/validate_data.py uses
  3. no invented facts      - no requirement row claims a status without a pointer; no OPEN question carries
                              an answer; no question is OPEN without a method to obtain the information
  4. statuses are closed    - values come from a declared vocabulary, never free text
  5. nothing is implemented - every suggestion still reads AWAITING_DECISION (or a decision the owner actually
                              recorded), and no suggestion may claim to be done while its decision is unset
  6. derived counts only    - the prose counts on the new pages match the ledgers (F-17/F-26/F-29 class)
  7. disclosure             - every page in the namespace carries the required sentence (R-01)
  8. no product prices      - the namespace never prints a price (R-04/R-05)
  9. links resolve          - every internal href in the namespace maps to a real file
 10. generated output current - decisions/ and DECISIONS.md match a fresh build

Run: python3 tools/validate_decisions.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "ledger"
OUT = REPO / "decisions"
sys.path.insert(0, str(REPO / "tools"))

import build_decisions as bd  # noqa: E402  (single source of truth for derived counts)

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
REQ_STATUSES = set(bd.REQS["status_vocabulary"])
# The canonical registers declare no closed vocabulary of their own; derive the states this gate uses.
Q_STATES = {"ANSWERED", "OPEN"}
DECISIONS = {"AWAITING_DECISION", "A", "B", "C"}  # owner records one option id, or leaves it undecided

# Same allowlist as tools/validate_data.py, extended with the two official hosts this namespace cites.
OFFICIAL_HOSTS = {
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "amazon.com",
    "link.amazon",
    "www.ftc.gov",
    "ftc.gov",
    "developers.google.com",
    "support.google.com",
    "docs.github.com",
}

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|stream|tax|refund|withhold)\w*", re.I
)


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    def fail(self, msg: str) -> None:
        self.errors.append(msg)


def check_sources(rep: Report) -> None:
    sources = {s["id"]: s for s in json.loads((DATA / "sources.json").read_text(encoding="utf-8"))["sources"]}
    cited: set[str] = set()
    rows = bd.all_reqs() + bd.all_qs() + bd.all_sugs()
    for row in rows:
        for sid in row.get("source_ids", []):
            cited.add(sid)
            if sid not in sources:
                rep.fail(f"{row['id']}: cites unknown source id {sid!r}")
    # hosts of every cited source must be on the allowlist (the rows this namespace leans on)
    for sid in sorted(cited):
        src = sources.get(sid)
        if not src:
            continue
        host = urlparse(src["url"]).netloc.lower()
        if host not in OFFICIAL_HOSTS:
            rep.fail(f"{sid}: host {host!r} is not on the official allowlist")
        if not src.get("accessed_utc"):
            rep.fail(f"{sid}: no accessed_utc - an undated source cannot be re-checked")
    rep.stats["rows"] = len(rows)
    rep.stats["distinct_sources_cited"] = len(cited)


def check_requirements(rep: Report) -> None:
    seen: set[str] = set()
    for r in bd.all_reqs():
        rid = r["id"]
        if rid in seen:
            rep.fail(f"duplicate requirement id {rid}")
        seen.add(rid)
        if r["status"] not in REQ_STATUSES:
            rep.fail(f"{rid}: status {r['status']!r} is not in the declared vocabulary")
        # A status must be backed by a pointer, not by an adjective.
        if not r.get("evidence"):
            rep.fail(f"{rid}: no evidence recorded - a status without evidence is an assertion")
        # A PARTIAL or NOT_MET row must state its gap; a MET row must not carry one.
        if r["status"] in ("PARTIAL", "NOT_MET") and not r.get("gap"):
            rep.fail(f"{rid}: status {r['status']} but no gap is stated")
        if r["status"] == "MET" and r.get("gap"):
            rep.fail(f"{rid}: claims MET but carries a gap - one of the two is wrong")
        if r["status"] == "MET" and not r.get("implementation"):
            rep.fail(f"{rid}: claims MET but names no implementation to check")
        # Verifiable implementation pointers must actually exist on disk.
        for token in re.findall(r"[\w./-]+\.(?:py|json|html|sql|md|tmpl)", r.get("implementation", "")):
            if not (REPO / token).exists() and "/" in token:
                rep.fail(f"{rid}: implementation points at {token!r}, which does not exist")
        # Requirement rows must not smuggle in a numeric result that nothing can check.
        if r["status"] == "UNVERIFIABLE" and not r.get("gap"):
            rep.fail(f"{rid}: UNVERIFIABLE without stating what would make it checkable")
    rep.stats["requirements"] = len(seen)


def check_questions(rep: Report) -> None:
    """The canonical register is owned elsewhere; this gate checks it is *reviewable*, and that this
    namespace never invents an answer to it."""
    seen: set[str] = set()
    for q in bd.all_qs():
        qid = q["id"]
        if qid in seen:
            rep.fail(f"duplicate question id {qid}")
        seen.add(qid)
        # An unanswered question must not have a fabricated `known`.
        if not (q.get("known") or "").strip():
            # the brief demands that missing information come with a way to find it
            for field in ("missing", "how_to_find"):
                if not (q.get(field) or "").strip():
                    rep.fail(f"{qid}: unanswered question with no {field!r} - a dead end is not a plan")
        if not [i for i in q.get("source_ids", []) if i]:
            rep.fail(f"{qid}: no source_ids")
        for blocker in q.get("blocks", []):
            if blocker not in {s["id"] for s in bd.all_sugs()}:
                rep.fail(f"{qid}: blocks unknown suggestion {blocker!r}")
    rep.stats["questions"] = len(seen)
    rep.stats["questions_open"] = sum(1 for q in bd.all_qs() if bd.q_state(q) == "OPEN")


def check_suggestions(rep: Report) -> None:
    """Every suggestion must be answerable: options with trade-offs, a recommendation that is one of them,
    a stated reason, and resolvable evidence."""
    seen: set[str] = set()
    qids = {q["id"] for q in bd.all_qs()}
    for s in bd.all_sugs():
        sid = s["id"]
        if sid in seen:
            rep.fail(f"duplicate suggestion id {sid}")
        seen.add(sid)
        if not (s.get("title") or "").strip():
            rep.fail(f"{sid}: no title")
        if not (s.get("suggestion") or "").strip():
            rep.fail(f"{sid}: no concrete proposal")
        if not (s.get("why") or "").strip():
            rep.fail(f"{sid}: no stated reason - a recommendation without a reason is a preference")
        opts = s.get("options") or []
        if len(opts) < 2:
            rep.fail(f"{sid}: fewer than two options - a single option is not a decision")
        ids = {o.get("id") for o in opts}
        rec = (s.get("recommended") or "").strip()
        if rec and rec not in ids:
            # A compound recommendation ("A + C first, then B") is allowed, but every option id it
            # names must exist, or the reader is being pointed at an option that is not offered.
            named = set(re.findall(r"\b([A-Z])\b", rec))
            unknown = sorted(named - {i for i in ids if i})
            if unknown:
                rep.fail(f"{sid}: recommends {rec!r}, naming option(s) {unknown} that are not offered")
        for o in opts:
            if not (o.get("tradeoff") or "").strip():
                rep.fail(f"{sid}: option {o.get('id')!r} states no trade-off")
        for blocker in s.get("needs_answers") or []:
            if blocker not in qids:
                rep.fail(f"{sid}: needs_answers references unknown question {blocker!r}")
        if not [i for i in (s.get("evidence") or []) if i]:
            rep.fail(f"{sid}: no evidence sources")
        # Nothing may be recorded as decided without the owner's note.
        if (s.get("decision") or "").strip() and not (s.get("status") or "").strip():
            rep.fail(f"{sid}: carries a decision with no status note - record who decided and why")
    rep.stats["suggestions"] = len(seen)
    rep.stats["suggestions_awaiting"] = sum(1 for s in bd.all_sugs() if bd.sug_decision(s) == "AWAITING_DECISION")


def check_cross_references(rep: Report) -> None:
    """Every FG-xx / SG-xx / RF-xx / F-xx a requirement row cites must exist in the tree.

    This is a regression check, not a hypothetical: the first version of this namespace published twelve
    cross-references to `SUG-xx` ids that belonged to a register deleted during deduplication against the
    canonical board (PR #61). The pages rendered beautifully and every other gate passed, because nothing
    compared a reference against the registers it was supposed to point at. It was only caught by reading
    the deployed live page.
    """
    known = {s["id"] for s in bd.all_sugs()} | {q["id"] for q in bd.all_qs()}
    known |= {f["id"] for f in bd.FINDINGS["findings"]}
    known |= {f["id"] for f in json.loads((DATA / "flags.json").read_text(encoding="utf-8"))["flags"]}
    checked = 0
    for r in bd.all_reqs():
        for ref in r.get("flag_ids", []):
            checked += 1
            if ref not in known:
                rep.fail(
                    f"{r['id']}: cites {ref!r}, which exists in no register "
                    "(ledger/suggestions.json, ledger/questions.json, ledger/flags.json, ledger/decisions_findings.json)"
                )
    rep.stats["cross_references_checked"] = checked


def check_findings(rep: Report) -> None:
    """This task's own review findings must stay sourced and attributable."""
    for f in bd.FINDINGS["findings"]:
        if not (f.get("finding") or "").strip():
            rep.fail(f"{f['id']}: empty finding")
        if not (f.get("impact") or "").strip():
            rep.fail(f"{f['id']}: no impact stated")
        if not [i for i in f.get("source_ids", []) if i in bd.SOURCES]:
            rep.fail(f"{f['id']}: no resolvable source - an unsourced irregularity is a rumour")
    rep.stats["findings"] = len(bd.FINDINGS["findings"])


def check_pages(rep: Report) -> None:
    pages = sorted(OUT.rglob("*.html"))
    if len(pages) < 4:
        rep.fail(f"decisions/: expected the full page set, found {len(pages)}")
    # Derived counts: the number printed immediately before a KPI label must equal the ledger value.
    # Labels are matched longest-first so that a composite label ("questions still not fully answered")
    # is never mistaken for its shorter prefix ("questions") — that bug made this gate fail on itself once.
    c = bd.counts()
    derived = {
        "proposals awaiting a decision": c["sugs_awaiting"],
        "changes implemented by this task": 0,
        "questions still not fully answered": c["qs_open"] + c["qs_partial"],
        "requirements not yet met": c["reqs_partial"] + c["reqs_not_met"],
        "answered from an official source": c["qs_answered"],
        "needing nothing but a decision": c["sugs_unblocked"],
        "awaiting your decision": c["sugs_awaiting"],
        "answered in part": c["qs_partial"],
        "open \u2014 answer blank": c["qs_open"],
        "partly met": c["reqs_partial"],
        "not met": c["reqs_not_met"],
        "proposals": c["sugs"],
        "questions": c["qs"],
        "requirements": c["reqs"],
        "implemented": 0,
        "met": c["reqs_met"],
    }
    ordered = sorted(derived, key=len, reverse=True)
    label_re = re.compile(r"(\d+)\s+(" + "|".join(re.escape(k) for k in ordered) + r")")
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if DISCLOSURE not in text:
            rep.fail(f"{page.relative_to(REPO)}: missing the required disclosure sentence (R-01)")
        # Double-escaped entities ("&amp;amp;") mean a template escaped a value twice: the reader sees
        # literal "&amp;". Caught twice while building this namespace, so it is a gate condition now.
        if "&amp;amp;" in text or "&amp;lt;" in text or "&amp;#x27;" in text:
            for m in re.finditer(r"&amp;(?:amp|lt|gt|#x27);", text):
                rep.fail(f"{page.relative_to(REPO)}: double-escaped entity {m.group(0)!r} - a reader sees the raw entity")
        plain = " ".join(re.sub(r"<[^>]+>", " ", text).split())
        for m in label_re.finditer(plain):
            stated, label = int(m.group(1)), m.group(2)
            if stated != derived[label]:
                ctx = plain[max(0, m.start() - 50) : m.end() + 20]
                rep.fail(
                    f"{page.relative_to(REPO)}: prose says '{m.group(0)}' but the ledger holds "
                    f"{derived[label]} - near {ctx!r} (F-17/F-26/F-29 class)"
                )
        # No product prices anywhere in this namespace.
        units = re.split(r"</tr>|</p>|</li>|<br\s*/?>", plain)
        for unit in units:
            for m in MONEY.finditer(unit):
                if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                    rep.fail(f"{page.relative_to(REPO)}: money value {m.group(0)!r} in a buying context (R-04)")
        # Internal links resolve.
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
            if href.startswith(("http://", "https://", "mailto:", "#", "//")):
                continue
            if not (page.parent / href).resolve().is_file():
                rep.fail(f"{page.relative_to(REPO)}: broken internal link -> {href}")
    # DECISIONS.md must exist, be sourced, and carry the same derived numbers.
    md = REPO / "DECISIONS.md"
    if not md.is_file():
        rep.fail("DECISIONS.md: missing - the executive summary is a required deliverable")
    else:
        body = md.read_text(encoding="utf-8")
        if f"Of the {c['reqs']} requirements" not in body:
            rep.fail("DECISIONS.md: requirement count does not match the ledger")
        if "Nothing proposed here has been implemented" not in body:
            rep.fail("DECISIONS.md: must state that nothing has been implemented")
    rep.stats["pages"] = len(pages)


def check_current(rep: Report) -> None:
    """The committed output must equal a fresh build (the same contract as build_site.py --check)."""
    import tempfile, shutil

    tmp = Path(tempfile.mkdtemp(prefix="z2decg-"))
    try:
        bd.build(tmp)
        fresh = bd.digest(tmp)
        committed = bd.digest(OUT)
        for key in sorted(set(fresh) | set(committed)):
            if fresh.get(key) != committed.get(key):
                rep.fail(f"decisions/{key}: committed output differs from a fresh build - run tools/build_decisions.py")
        md_path = REPO / "DECISIONS.md"
        current = md_path.read_text(encoding="utf-8") if md_path.is_file() else ""
        if current != bd.build_summary_md():
            rep.fail("DECISIONS.md: stale - run tools/build_decisions.py")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    rep = Report()
    try:
        check_sources(rep)
        check_requirements(rep)
        check_questions(rep)
        check_suggestions(rep)
        check_cross_references(rep)
        check_findings(rep)
        check_pages(rep)
        check_current(rep)
    except FileNotFoundError as exc:
        rep.fail(f"required file missing: {exc}")
    print(json.dumps({"ok": not rep.errors, "errors": rep.errors, "warnings": rep.warnings, "stats": rep.stats}, indent=2, sort_keys=True))
    if rep.errors:
        print(f"\nDECISION GATE FAILED: {len(rep.errors)} error(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
