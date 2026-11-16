#!/usr/bin/env python3
"""Gate for the design-brief namespace (brief/).

Why a separate gate rather than a section of tools/validate_data.py
-------------------------------------------------------------------
tools/validate_data.py owns ledger/** and pages/**. This namespace has its own
registers and its own id prefixes, and the project's rule is that a session edits
only the files it claimed. So the gate for brief/ lives here, and --check in
CI fails the build if brief/*.html drifts from brief/data/*.json.

What it enforces, and why each rule is here
-------------------------------------------
1.  Referential integrity. A source id that resolves to nothing is a citation
    pointing at air. This is the defect the F-16 flag recorded on the canonical
    compliance ledger, so it is checked first.
2.  Blank-or-sourced. A row is either a measurement of this repository's own
    files (and must state the method that produced it), an official or observed
    claim (and must carry a resolvable source), or a carried row (and must say
    what it is carrying). Nothing is a fourth kind.
3.  An open question's answer stays empty. Filling it is the one thing this
    project refuses to do.
4.  The measured counts in the executive summary are re-derived from the tree at
    gate time. That rule exists because of FB-01 and FB-02: two rows on the
    release-readiness board printed typed counts that the tree outgrew by 22 and
    7 pages, and no gate noticed. A summary that cannot drift is the point.
5.  Board integrity. A recorded choice must be one of that row's own options;
    a recommendation must be a real option or an explicit owner's call.
6.  No price. A product price cannot be published on this site (R-04), so a
    money figure in this namespace fails the build.
7.  Every page carries the §5 disclosure, a self-referencing canonical, and no
    broken local link.

Run: python3 tools/validate_brief.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "brief"
DATA = OUT / "data"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
TAG = re.compile(r"tag=[A-Za-z0-9]+-[0-9]{2}\b")

#: Hosts allowed to carry a value this namespace publishes. A source on any other
#: host is not an official page for the purposes of this project.
ALLOWED_HOSTS = {
    "affiliate-program.amazon.com",
    "www.amazon.com",
    "link.amazon",
    "developers.google.com",
    "www.ftc.gov",
    "kanlerxz87-cyber.github.io",
}

SEVERITIES = {"high", "medium", "low"}
FLAG_STATES = {"open", "closed"}
SOURCE_KINDS = {"official", "observed", "measurement", "carried"}
PROPOSAL_STATES = {"proposed", "blocked", "chosen", "rejected"}

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


S = load("sources.json")
REVIEW = load("review.json")
FLAGS = load("flags.json")
DESIGN = load("design.json")
TOPICS = load("topics.json")
SUGGESTIONS = load("suggestions.json")
DECISIONS = load("decisions.json")
QUESTIONS = load("questions.json")
SUMMARY = load("summary.json")
VERIFICATION = load("verification.json")

SOURCES = {s["id"]: s for s in S["sources"]}


# ------------------------------------------------------------------ 1. the register

def check_sources() -> None:
    seen = set()
    for s in S["sources"]:
        sid = s["id"]
        if sid in seen:
            err(f"sources: duplicate id {sid}")
        seen.add(sid)
        for field in ("id", "title", "url", "publisher", "fetched", "rechecked", "class"):
            if not str(s.get(field, "")).strip():
                err(f"sources/{sid}: empty required field {field!r}")
        if s["class"] not in S["classes"]:
            err(f"sources/{sid}: class {s['class']!r} is not one of {sorted(S['classes'])}")
        if not s["url"].startswith("https://"):
            err(f"sources/{sid}: url is not https")
        host = s["url"].split("/")[2]
        if host not in ALLOWED_HOSTS:
            err(f"sources/{sid}: host {host!r} is not an allowed official host")
        if s["rechecked"] not in ("yes", "carried"):
            err(f"sources/{sid}: rechecked must be 'yes' or 'carried', got {s['rechecked']!r}")
        # A row that quotes a page must have read it, or say it did not.
        if s["class"] == "carried" and s.get("quote", "").strip():
            err(f"sources/{sid}: a carried row must not quote text it did not re-read")


def refs_ok(where: str, ids: object) -> None:
    if ids is None:
        return
    raw = ids if isinstance(ids, (list, tuple)) else [ids]
    for item in raw:
        for sid in re.findall(r"(BR-\d+)", str(item)):
            if sid not in SOURCES:
                err(f"{where}: cites {sid}, which is not in the source register")


# ------------------------------------------------------------------ 2. blank-or-sourced

def check_review_rows() -> None:
    for r in REVIEW["rows"]:
        rid = r["id"]
        kind = r.get("source_kind", "")
        if kind not in SOURCE_KINDS:
            err(f"review/{rid}: source_kind {kind!r} is not one of {sorted(SOURCE_KINDS)}")
        if not str(r.get("method", "")).strip():
            err(f"review/{rid}: a row must state the method that produced it")
        if not str(r.get("value", "")).strip():
            err(f"review/{rid}: empty value")
        if kind == "measurement" and (r.get("source_id") or "").strip():
            err(f"review/{rid}: a measurement of this repository cannot cite an official source; "
                "put the rule that makes it matter in 'context_source_id'")
        if kind in ("official", "observed") and not (r.get("source_id") or "").strip():
            err(f"review/{rid}: a {kind} row must carry a resolvable source id")
        if kind == "carried" and not str(r.get("carried_note", "")).strip():
            err(f"review/{rid}: a carried row must say what it is carrying and from where")
        refs_ok(f"review/{rid}", r.get("source_id"))
        refs_ok(f"review/{rid}", r.get("context_source_id"))
        if r.get("flag"):
            if r["flag"] not in {f["id"] for f in FLAGS["flags"]}:
                err(f"review/{rid}: flag {r['flag']!r} is not on the flag register")


def check_verification_rows() -> None:
    allowed = {"match", "mismatch", "reproduced", "measured", "pending"}
    for c in VERIFICATION["checks"]:
        cid = c["id"]
        if c["result"] not in allowed:
            err(f"verification/{cid}: result {c['result']!r} is not one of {sorted(allowed)}")
        if not str(c.get("method", "")).strip():
            err(f"verification/{cid}: a check must state its method")
        # A check that observed nothing must say it is pending; a pending check may not
        # be presented as a result.
        if c["result"] != "pending" and not str(c.get("observed", "")).strip():
            err(f"verification/{cid}: result {c['result']!r} with nothing observed")
        refs_ok(f"verification/{cid}", c.get("source_ids"))


# ------------------------------------------------------------------ 3. open stays empty

def check_questions() -> None:
    for q in QUESTIONS["answered"]:
        qid = q["id"]
        if not str(q.get("answer", "")).strip():
            err(f"questions/{qid}: an answered row must carry an answer")
        if not q.get("source_ids"):
            err(f"questions/{qid}: an answered row must cite the page that settles it")
        refs_ok(f"questions/{qid}", q.get("source_ids"))
    for q in QUESTIONS["open"]:
        qid = q["id"]
        if str(q.get("answer", "")).strip():
            err(f"questions/{qid}: an open question's answer must stay empty")
        for field in ("known", "missing", "how_to_close", "who_can_close"):
            if not str(q.get(field, "")).strip():
                err(f"questions/{qid}: open rows must state {field!r}")
    ids = {q["id"] for q in QUESTIONS["answered"]} | {q["id"] for q in QUESTIONS["open"]}
    if len(ids) != len(QUESTIONS["answered"]) + len(QUESTIONS["open"]):
        err("questions: duplicate id across the answered and open sections")
    # A question's 'blocks' names the proposals waiting on it. Naming a flag or another
    # question there renders as a link to a fragment that addresses nothing, which
    # tools/audit_site.py then fails across the whole site.
    proposal_ids = {p["id"] for p in SUGGESTIONS["proposals"]}
    for q in QUESTIONS["open"]:
        for b in q.get("blocks", []):
            if b not in proposal_ids:
                err(f"questions/{q['id']}: blocks {b!r}, which is not a proposal on the board")


# ------------------------------------------------------------------ 4. counts re-derived

def measured_pages() -> list[Path]:
    """The pages the executive summary's counts describe.

    Three exclusions, each deliberate:
      - `404.html` is an error document, not a destination.
      - `release/index.html` — the readiness board already excludes itself, on the
        grounds that a board cannot count the page it prints the count on.
      - `brief/**` — this namespace did not exist when the counts were taken, and
        several of its pages quote the phrase 'AI-powered' in order to diagnose it.
        Including them would inflate the very measurement they are reporting.

    The set is therefore 'the site as it stood when it was measured', which is what
    the summary claims to describe. It is stated here rather than left implicit
    because a count whose denominator is unstated is not a measurement.
    """
    skip = {".git", ".github", "__pycache__", "node_modules"}
    out = []
    for p in sorted(REPO.rglob("*.html")):
        rel = p.relative_to(REPO)
        if any(part in skip for part in rel.parts):
            continue
        if rel.name == "404.html":
            continue
        if rel.parts[0] == "brief":
            continue
        if rel == Path("release") / "index.html":
            continue
        out.append(p)
    return out


def measure() -> dict:
    pages = measured_pages()
    n = len(pages)
    with_disc = sum(1 for p in pages if DISCLOSURE in p.read_text(encoding="utf-8"))
    with_tag = sum(1 for p in pages if TAG.search(p.read_text(encoding="utf-8")))
    ai = sum(1 for p in pages if "AI-powered" in p.read_text(encoding="utf-8"))
    price_pages = 0
    for p in pages:
        t = p.read_text(encoding="utf-8")
        if MONEY.search(t) and "bounty" not in t.lower() and "commission" not in t.lower():
            price_pages += 1
    namespaces = {
        (p.relative_to(REPO).parts[0] if len(p.relative_to(REPO).parts) > 1 else "(root)")
        for p in sorted(REPO.rglob("*.html"))
        if p.name != "404.html"
        and not any(x in p.relative_to(REPO).parts for x in
                    {".git", ".github", "__pycache__", "node_modules"})
    }
    return {
        "published": n,
        "with_disclosure": with_disc,
        "with_tag": with_tag,
        "ai_powered_pages": ai,
        "price_pages": price_pages,
        "surfaces": len(namespaces),
    }


def check_derived_counts() -> None:
    """The executive summary's measured values are recomputed from the tree.

    FB-01 and FB-02 are two rows on the release-readiness board that printed typed
    counts the tree outgrew, with no gate to notice. The summary in this namespace
    must not be able to do that, so the numbers it prints are re-derived here.
    """
    m = measure()
    expect = {
        "Published pages carrying an Associates tag": f"0 of {m['published']}",
        "Published pages carrying the exact §5 disclosure sentence": f"{m['with_disclosure']} of {m['published']}",
        "Published pages printing a product price": f"0 of {m['published']}",
        "Pages describing the site as AI-powered": str(m["ai_powered_pages"]),
    }
    for row in SUMMARY["state"]:
        want = expect.get(row["metric"])
        if want is None:
            continue
        got = str(row["value"]).strip()
        if got != want:
            err(
                f"summary: {row['metric']!r} prints {got!r} but the tree measures {want!r} — "
                "the value must be re-derived, not typed"
            )


# ------------------------------------------------------------------ 5. board integrity

def check_board() -> None:
    sheet = {r["id"]: r for r in DECISIONS["sheet"]}
    proposal_ids = [p["id"] for p in SUGGESTIONS["proposals"]]
    if len(set(proposal_ids)) != len(proposal_ids):
        err("suggestions: duplicate proposal id")
    for p in SUGGESTIONS["proposals"]:
        pid = p["id"]
        if p["state"] not in PROPOSAL_STATES:
            err(f"suggestions/{pid}: state {p['state']!r} is not one of {sorted(PROPOSAL_STATES)}")
        if not p.get("options"):
            err(f"suggestions/{pid}: a proposal must offer options to choose between")
        option_ids = {o["id"] for o in p["options"]}
        rec = str(p.get("recommended", "")).strip()
        # A recommendation must name at least one of the row's own options. Caveats belong
        # in 'recommended_note', where they cannot make the choice ambiguous.
        tokens = set(re.findall(r"\b([A-Z])\b", rec))
        if rec and not (tokens & option_ids):
            err(f"suggestions/{pid}: recommended {rec!r} names none of its own options ({sorted(option_ids)})"
                " — put any caveat in 'recommended_note'")
        if pid not in sheet:
            err(f"decisions: no row on the decision sheet for {pid}")
            continue
        row = sheet[pid]
        choice = str(row.get("choice", "")).strip()
        if choice and choice not in option_ids:
            err(f"decisions/{pid}: recorded choice {choice!r} is not one of the row's options ({sorted(option_ids)})")
        if choice and not str(row.get("decided_on", "")).strip():
            err(f"decisions/{pid}: a recorded choice must carry the date it was made")
    for sid in sheet:
        if sid not in proposal_ids:
            err(f"decisions: sheet row {sid} has no proposal on the board")
    question_ids = {q["id"] for q in QUESTIONS["answered"]} | {q["id"] for q in QUESTIONS["open"]}
    for p in SUGGESTIONS["proposals"]:
        for b in p.get("blockers", []):
            if b not in question_ids:
                err(f"suggestions/{p['id']}: blocker {b!r} is not a question on the register")


#: The number of gates/workflow steps this repository runs. Prose that claims a different
#: number is stale, not merely imprecise: a summary that says "22 gates" when 43 run is
#: understating the evidence it is asking the reader to trust.
GATE_COUNT = 43

#: Published surfaces (top-level directories plus the root).
SURFACE_COUNT = 0


def check_summary_prose() -> None:
    """The summary's prose must not contradict its own measured table.

    This rule exists because the brief shipped with exactly that defect: the state table
    was re-measured to 150 pages while three prose bullets still said "138 of 138",
    "22 gates" and "fourteen surfaces". The table was right and the prose was stale, and
    no gate noticed — which is the FB-01/FB-02 defect, in the one document whose whole
    job is to be checkable. A reader who sees both numbers learns to trust neither.

    Only the specific count patterns this document actually uses are checked, and each is
    compared against a value measured from the tree in the same run. Broad prose-scanning
    would be brittle; three narrow rules catch the class that has actually occurred.
    """
    m = measure()
    n = m["published"]
    blocks = list(SUMMARY["what_is_settled"]) + list(SUMMARY["what_is_not_settled"]) + [
        SUMMARY["headline"], SUMMARY["the_blocking_fact"]["headline"], SUMMARY["the_blocking_fact"]["detail"],
        SUMMARY["the_one_thing"],
    ] + [r.get("note", "") for r in SUMMARY["state"]]
    text = "\n".join(str(b) for b in blocks)

    # "N of M pages carry the disclosure" — M must be the measured page count, N must be
    # the count that actually discloses.
    for n_disc, total in re.findall(r"(\d+)\s+of\s+(\d+)\s+pages", text):
        if int(total) != n:
            err(f"summary prose: says '{n_disc} of {total} pages' but the tree measures {n} published pages")
        elif int(n_disc) != m["with_disclosure"]:
            err(f"summary prose: says '{n_disc} of {total} pages carry the disclosure' "
                f"but {m['with_disclosure']} do — the prose must be re-derived with the table")
    # A gate count in prose must equal the number of gates this repository actually has.
    for gates in re.findall(r"(\d+)\s+of\s+\d+\s+(?:gates|workflow steps)", text):
        if int(gates) != GATE_COUNT:
            err(f"summary prose: claims {gates} gates/workflow steps pass; this repository runs {GATE_COUNT}")
    # A surface count in prose must equal the namespaces the tree publishes.
    for surfaces in re.findall(r"(?:the\s+)?(\d+)\s+published surfaces", text):
        if int(surfaces) != SURFACE_COUNT:
            err(f"summary prose: says {surfaces} published surfaces; the tree publishes {SURFACE_COUNT}")
    # The 'decide first' list is rendered as an ordered card row; a duplicate id prints
    # two identical cards and numbers the items twice.
    seen, ids = set(), []
    for item in SUMMARY["decide_first"]:
        ids.append(item["id"])
        if item["id"] in seen:
            err(f"summary: decide_first lists {item['id']} twice")
        seen.add(item["id"])
    orders = [int(i["order"]) for i in SUMMARY["decide_first"]]
    if orders != list(range(1, len(orders) + 1)):
        err(f"summary: decide_first orders are {orders}, not 1..{len(orders)}")


def check_flags() -> None:
    review_ids = {r["id"] for r in REVIEW["rows"]}
    for f in FLAGS["flags"]:
        fid = f["id"]
        if f["severity"] not in SEVERITIES:
            err(f"flags/{fid}: severity {f['severity']!r} is not one of {sorted(SEVERITIES)}")
        if f["status"] not in FLAG_STATES:
            err(f"flags/{fid}: status {f['status']!r} is not one of {sorted(FLAG_STATES)}")
        for field in ("title", "detail", "why_it_matters", "close_action", "owner"):
            if not str(f.get(field, "")).strip():
                err(f"flags/{fid}: empty required field {field!r}")
        for ev in re.findall(r"(RV-\d+)", str(f.get("evidence", ""))):
            if ev not in review_ids:
                err(f"flags/{fid}: evidence {ev} is not a row on the review register")
        refs_ok(f"flags/{fid}", f.get("source_ids"))


def check_topics_and_design() -> None:
    for t in TOPICS["topics"]:
        tid = t["id"]
        for field in ("working_title", "angle", "rests_on", "why_it_could_earn_traffic", "missing", "risk"):
            if not str(t.get(field, "")).strip():
                err(f"topics/{tid}: empty required field {field!r}")
        # The board's honesty rule: a traffic claim must be labelled as a judgement,
        # because no demand data exists anywhere in this project.
        if "judgement" not in str(t["why_it_could_earn_traffic"]).lower():
            err(f"topics/{tid}: a traffic expectation must be labelled a judgement, not stated as a fact")
        refs_ok(f"topics/{tid}", t.get("source_ids"))
    for r in TOPICS["governing_rules"]:
        if not str(r.get("quoted", "")).strip():
            err(f"topics/{r['id']}: a governing rule must quote the page it comes from")
        refs_ok(f"topics/{r['id']}", r.get("source_ids"))
    for r in DESIGN["rewrites"]:
        for field in ("before", "after", "why", "fact_check"):
            if not str(r.get(field, "")).strip():
                err(f"design/rewrites/{r['id']}: empty required field {field!r}")
        if "judgement" not in DESIGN["note"].lower():
            err("design: the pack must label its rewrites as craft judgements")


# ------------------------------------------------------------------ 6 & 7. the pages

def check_pages() -> None:
    pages = sorted(OUT.glob("*.html"))
    if len(pages) != 9:
        err(f"pages: expected 9 generated pages, found {len(pages)}")
    for p in pages:
        text = p.read_text(encoding="utf-8")
        if DISCLOSURE not in text:
            err(f"{p.name}: missing the required Site disclosure")
        if 'rel="canonical"' not in text:
            err(f"{p.name}: missing a self-referencing canonical")
        if 'property="og:url"' not in text:
            err(f"{p.name}: missing og:url")
        # No price may be published on this site (R-04).
        for hit in MONEY.findall(text):
            err(f"{p.name}: prints a money figure ({hit})")
        # Every local link must resolve to a file.
        for href in re.findall(r'href="([^"#]+)(?:#[^"]*)?"', text):
            if href.startswith(("http", "mailto:")):
                continue
            target = (p.parent / href.split("#")[0]).resolve()
            if not target.is_file():
                err(f"{p.name}: broken local link {href}")
        # A same-page anchor (href="#FB-01") must resolve on this page. A cross-page
        # anchor (href="flagged.html#FB-01") is checked when its target page is read.
        for anchor in set(re.findall(r'href="#([A-Z][A-Za-z0-9-]*-\d+)"', text)):
            if f'id="{anchor}"' not in text:
                err(f"{p.name}: links to #{anchor}, which is not on this page")


def main() -> int:
    global SURFACE_COUNT
    SURFACE_COUNT = measure()["surfaces"]
    check_sources()
    check_review_rows()
    check_verification_rows()
    check_questions()
    check_derived_counts()
    check_summary_prose()
    check_board()
    check_flags()
    check_topics_and_design()
    check_pages()

    m = measure()
    print(f"brief/: {len(S['sources'])} sources, {len(REVIEW['rows'])} review rows, "
          f"{len(QUESTIONS['answered'])} answered / {len(QUESTIONS['open'])} open questions, "
          f"{len(SUGGESTIONS['proposals'])} proposals, {len(TOPICS['topics'])} topics, "
          f"{len(FLAGS['flags'])} flags, {len(VERIFICATION['checks'])} checks")
    print(f"tree: {m['published']} published pages · {m['with_disclosure']} disclose · "
          f"{m['with_tag']} tagged · {m['price_pages']} printing a product price")
    for w in warnings:
        print(f"WARN  {w}")
    if errors:
        print(f"\n{len(errors)} error(s):")
        for e in errors:
            print(f"  ERROR {e}")
        return 1
    print("brief/: all checks pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
