#!/usr/bin/env python3
"""Deploy gate for the discovery namespace (discovery/).

The brief's contract, restated for a review surface:

    "Every table row must have a source link to an official site. If a value can't be
     confirmed from an official source, leave it blank and flag it as unverified.
     Never infer or fill in values."

That sentence is easy to satisfy in a table of product specs and easy to break in a
table of *judgements*. So this gate holds the discovery registers to nine rules, and
every one of them is a defect this repository has actually shipped at least once in
another namespace:

  1. source integrity     - every cited id resolves, in the discovery register or the
                            project ledger; a dangling citation is a rumour with a number
  2. official hosts only  - sources sit on the same allowlist the rest of the repo uses
  3. quotes are real      - every discovery source carries the text relied on; the gate
                            refuses a source with no quote, because that is a paraphrase
                            wearing a citation
  4. questions unanswered - an OPEN question carries no answer; an OPEN question states
                            what is missing AND how to obtain it, or it is a dead end
  5. suggestions answerable - two or more options, a trade-off per option, a
                            recommendation that names only offered options, resolvable
                            evidence, and blockers that exist
  6. nothing implemented  - nothing may read as decided while `decision` is empty
  7. derived counts       - the numbers printed on the hub match the registers
  8. disclosure and links - every page carries the required sentence (R-01) and every
                            internal href resolves to a file on disk
  9. generated output current - discovery/ matches a fresh render

Run: python3 tools/validate_discovery.py
"""

from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "discovery"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
sys.path.insert(0, str(REPO / "tools"))

import build_discovery as bd  # noqa: E402  (single source of truth for the derived counts)

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

# Words that would turn a proposal into an implemented change. If any of these appears
# in a row whose `decision` is empty, the page is claiming work has happened.
DONE_WORDS = re.compile(
    r"\b(has been (?:implemented|shipped|added|built|deployed)|"
    r"we (?:implemented|shipped|built|deployed)|"
    r"is now (?:live|implemented|published)|"
    r"completed|done)\b",
    re.I,
)

MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")



class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, int] = {}

    def fail(self, msg: str) -> None:
        self.errors.append(msg)


def check_sources(rep: Report) -> None:
    ledger = {s["id"]: s for s in json.loads((REPO / "ledger" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    disco = {s["id"]: s for s in bd.GD_SOURCES}
    overlap = set(ledger) & set(disco)
    if overlap:
        rep.fail(f"source ids redefined in both registers: {sorted(overlap)}")

    cited: dict[str, list[str]] = {}
    for row in bd.FINDINGS + bd.QUESTIONS + bd.SUGGESTIONS:
        ids = row.get("source_ids") if "source_ids" in row else row.get("evidence")
        for sid in ids or []:
            cited.setdefault(sid, []).append(row["id"])
    if not cited:
        rep.fail("no row cites any source - the register is unattributable")

    for sid, by in sorted(cited.items()):
        src = disco.get(sid) or ledger.get(sid)
        if src is None:
            rep.fail(f"source {sid} (cited by {', '.join(by)}) resolves to nothing")
            continue
        host = urlparse(src["url"]).netloc
        if host.startswith("www."):
            host = host[4:]
        if host not in OFFICIAL_HOSTS:
            rep.fail(f"source {sid} points at {host!r}, which is not an official allowlisted host")
    rep.stats["sources_cited"] = len(cited)
    rep.stats["sources_defined"] = len(disco)


def check_quotes(rep: Report) -> None:
    """A discovery source without the text it relies on is a paraphrase wearing a citation."""
    for s in bd.GD_SOURCES:
        if len((s.get("quote") or "").strip()) < 40:
            rep.fail(f"{s['id']}: no quoted text - the register must carry what the page actually says")
        if not (s.get("used_for") or "").strip():
            rep.fail(f"{s['id']}: quote with no stated use - a source nobody uses is decoration")
        if not (s.get("title") or "").strip():
            rep.fail(f"{s['id']}: no title")
    rep.stats["quotes_checked"] = len(bd.GD_SOURCES)


def check_questions(rep: Report) -> None:
    ids = set()
    for q in bd.QUESTIONS:
        qid = q["id"]
        if qid in ids:
            rep.fail(f"duplicate question id {qid}")
        ids.add(qid)
        for field in ("question", "known", "missing", "how_to_obtain"):
            if not (q.get(field) or "").strip():
                # `known` may be empty ONLY if missing/how_to_obtain explain the dead end;
                # but a question with no `question` or no route is unusable either way.
                if field in ("question", "missing", "how_to_obtain"):
                    rep.fail(f"{qid}: empty {field!r} - an unanswerable row is not a question")
        if (q.get("answer") or "").strip() and not (q.get("answer_source_ids") or []):
            rep.fail(f"{qid}: has an answer with no source - an unsourced answer is a guess")
        if not (q.get("source_ids") or []):
            rep.fail(f"{qid}: no source_ids - even an unknown must be anchored to what is known")
        for sid in q.get("source_ids") or []:
            if sid not in bd.SOURCES and sid not in bd.LEDGER:
                rep.fail(f"{qid}: cites unknown source {sid!r}")
        for b in q.get("blocks") or []:
            if b not in {s["id"] for s in bd.SUGGESTIONS}:
                rep.fail(f"{qid}: blocks unknown suggestion {b!r}")
    rep.stats["questions"] = len(ids)
    rep.stats["questions_open"] = sum(1 for q in bd.QUESTIONS if bd.q_state(q) == "OPEN")


def check_suggestions(rep: Report) -> None:
    ids = set()
    qids = {q["id"] for q in bd.QUESTIONS}
    for s in bd.SUGGESTIONS:
        sid = s["id"]
        if sid in ids:
            rep.fail(f"duplicate suggestion id {sid}")
        ids.add(sid)
        for field in ("title", "suggestion", "why", "recommended"):
            if not (s.get(field) or "").strip():
                rep.fail(f"{sid}: empty {field!r}")
        opts = s.get("options") or []
        if len(opts) < 2:
            rep.fail(f"{sid}: {len(opts)} option(s) - a single option is not a decision")
        opt_ids = {o.get("id") for o in opts}
        for o in opts:
            if not (o.get("tradeoff") or "").strip():
                rep.fail(f"{sid}: option {o.get('id')!r} states no trade-off")
            if not (o.get("label") or "").strip():
                rep.fail(f"{sid}: option {o.get('id')!r} has no label")
        named = set(re.findall(r"\b([A-Z])\b", s.get("recommended") or ""))
        unknown = sorted(named - {i for i in opt_ids if i})
        if unknown:
            rep.fail(f"{sid}: recommends {s['recommended']!r}, naming unoffered option(s) {unknown}")
        if not (s.get("evidence") or []):
            rep.fail(f"{sid}: no evidence - a recommendation without evidence is a preference")
        for e in s.get("evidence") or []:
            if e not in bd.SOURCES and e not in bd.LEDGER:
                rep.fail(f"{sid}: cites unknown evidence source {e!r}")
        for b in s.get("needs_answers") or []:
            if b not in qids:
                rep.fail(f"{sid}: waits on unknown question {b!r}")
        # Rule 6: nothing may read as decided or implemented while `decision` is empty.
        if not (s.get("decision") or "").strip():
            blob = json.dumps({k: v for k, v in s.items() if k != "options"}, ensure_ascii=False)
            m = DONE_WORDS.search(blob)
            if m:
                rep.fail(f"{sid}: reads as implemented ({m.group(0)!r}) but carries no recorded decision")
            if (s.get("status") or "") not in ("awaiting owner decision",):
                rep.fail(f"{sid}: undecided row with status {s.get('status')!r}")
    rep.stats["suggestions"] = len(ids)
    rep.stats["suggestions_awaiting"] = sum(1 for s in bd.SUGGESTIONS if bd.sug_state(s) == "AWAITING_DECISION")
    rep.stats["unblocked"] = sum(1 for s in bd.SUGGESTIONS if not (s.get("needs_answers") or []))


def check_findings(rep: Report) -> None:
    ids = set()
    sev = set(bd.DATA["severity_vocabulary"])
    for f in bd.FINDINGS:
        fid = f["id"]
        if fid in ids:
            rep.fail(f"duplicate finding id {fid}")
        ids.add(fid)
        for field in ("finding", "why_it_matters", "recommendation", "area"):
            if not (f.get(field) or "").strip():
                rep.fail(f"{fid}: empty {field!r}")
        if f.get("severity") not in sev:
            rep.fail(f"{fid}: severity {f.get('severity')!r} is not in the declared vocabulary")
        if not (f.get("source_ids") or []):
            rep.fail(f"{fid}: no official source - an unsourced finding is a rumour")
        # A finding that says something costs money or blocks a claim must show its measurement,
        # otherwise the reader cannot tell it apart from an opinion.
        if f.get("severity") != "cosmetic" and not (f.get("measurement") or "").strip():
            rep.fail(f"{fid}: severity {f['severity']!r} with no stated measurement")
    rep.stats["findings"] = len(ids)


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            href = a["href"]
            if not href.startswith(("http", "#", "mailto:")):
                self.refs.append(href.split("#", 1)[0])


def check_pages(rep: Report) -> None:
    pages = sorted(OUT.glob("*.html"))
    if len(pages) < len(bd.PAGES):
        rep.fail(f"discovery/: expected {len(bd.PAGES)} pages, found {len(pages)}")
    bad = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if DISCLOSURE not in text:
            rep.fail(f"{page.name}: missing the required Site disclosure sentence (R-01)")
        if "<h1" not in text:
            rep.fail(f"{page.name}: no h1")
        if "name=\"description\"" not in text:
            rep.fail(f"{page.name}: no meta description")
        if "<link rel=\"canonical\"" not in text:
            rep.fail(f"{page.name}: no canonical URL")
        p = LinkParser()
        p.feed(text)
        for ref in p.refs:
            if not (page.parent / ref).is_file():
                bad.append(f"{page.name}: broken internal link {ref!r}")
        # Stricter than the rest of the repo, on purpose. This namespace has no reason to print a
        # currency figure at all, so the repo-wide "program economics are allowed" exception is not
        # applied here: its \w* suffix lets "checkout" satisfy "check", which is how the first version
        # of this gate let an injected "$129.99 at checkout" through. Any currency figure fails.
        for m in MONEY.finditer(re.sub(r"<[^>]+>", " ", text)):
            bad.append(f"{page.name}: prints a currency figure {m.group(0)!r} - this namespace never shows a price")
    if bad:
        for b in bad:
            rep.fail(b)
    rep.stats["pages"] = len(pages)


def check_counts(rep: Report) -> None:
    """The hub prints numbers; they must be the numbers, not last week's numbers."""
    hub = (OUT / "index.html").read_text(encoding="utf-8")
    c = bd.counts()
    expectations = {
        "findings": c["findings"],
        "findings_blocking": c["findings_blocking"],
        "questions_open": c["questions_open"],
        "suggestions": c["suggestions"],
    }
    for key, want in expectations.items():
        if f"<b>{want}</b>" not in hub:
            rep.fail(f"index.html: does not print the derived count {want} for {key}")
    sugs = (OUT / "suggestions.html").read_text(encoding="utf-8")
    if f"{c['suggestions']} proposals" not in sugs:
        rep.fail("suggestions.html: proposal count is not the derived count")
    rep.stats.update(expectations)


def check_current(rep: Report) -> None:
    """`--check` on the generator is the same test; run it here so one command gates both."""
    for name, doc in bd.build().items():
        path = OUT / name
        if not path.is_file():
            rep.fail(f"{name}: not generated")
        elif path.read_text(encoding="utf-8") != doc:
            rep.fail(f"{name}: stale - run python3 tools/build_discovery.py")


def main() -> int:
    rep = Report()
    for fn in (check_sources, check_quotes, check_questions, check_suggestions, check_findings, check_pages, check_counts, check_current):
        try:
            fn(rep)
        except Exception as exc:  # a gate that crashes must fail, not pass
            rep.fail(f"{fn.__name__} crashed: {exc!r}")
    print(json.dumps({"errors": rep.errors, "warnings": rep.warnings, "stats": rep.stats}, indent=2, ensure_ascii=False))
    if rep.errors:
        print(f"\nFAIL {len(rep.errors)} error(s)")
        return 1
    print(f"\nOK {rep.stats.get('pages', 0)} pages · {rep.stats.get('findings', 0)} findings · "
          f"{rep.stats.get('questions', 0)} questions · {rep.stats.get('suggestions', 0)} suggestions · "
          f"{rep.stats.get('sources_cited', 0)} cited sources · 0 failures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
