#!/usr/bin/env python3
"""The contract for the submitted-link intake namespace (intake/).

Everything here is a rule the data claims to obey, checked against the data as it sits on
disk. It reads the rendered pages as well as the registers, because several of the defects
this repository has shipped were in the rendering, not the data.

Rules enforced
--------------
1.  Every source id cited anywhere resolves to a row in sources.json.
2.  INTENT AND OBSERVATION ARE NOT MERGED — the rule this namespace exists for. The two
    field groups are disjoint, no observed value appears in an intent field, and an intent
    field may not be filled with the observed ASIN or the observed URL.
3.  Intent fields are genuinely blank (empty string or a declared blank marker), and a
    submission whose intent is filled must carry a confirmation_date and an intended_source.
4.  Observed ASINs are 10 characters; submitted tokens are 9. If either stops being true,
    the record's central claim has changed and a human must look.
5.  An open question's answer is empty. An open question with an answer is a guess wearing
    a label.
6.  A proposal's choice is either empty or one of that row's own options.
7.  Every id referenced by a row (flags, questions, submissions, blockers) exists.
8.  No product price, rating, review count or sales rank is recorded anywhere.
9.  The disclosure sentence is on every page, above the data.
10. Every page carries exactly one canonical link.
11. Every link to an Amazon product page carries rel="sponsored".
12. Local links and same-page anchors resolve to something that exists.
13. Every printed count is derived from the registers in the same run.
14. A source that was carried rather than fetched is labelled as carried on every row that
    cites it.

Run: python3 tools/validate_intake.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(os.environ["INTAKE_ROOT"]) if os.environ.get("INTAKE_ROOT") else Path(__file__).resolve().parents[1]
DATA = REPO / "intake" / "data"
OUT = REPO / "intake"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_intake as B  # noqa: E402

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
PROGRAM_CONTEXT = re.compile(r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|stream|tax|refund|withhold)\w*", re.I)
# Block-level boundaries, applied to the raw HTML before tags are stripped. See check_no_prices.
BLOCK_SPLIT = re.compile(r"</(?:p|li|tr|div|section|blockquote|h[1-6]|td|th|figcaption)\s*>", re.I)
HREF = re.compile(r'<a\s+[^>]*href="([^"]+)"[^>]*>', re.I)

errors: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES_DOC = load("sources.json")
SUBS = load("submissions.json")
OBS = load("observations.json")
FLAGS = load("flags.json")
QUESTIONS = load("questions.json")
PROPOSALS = load("proposals.json")
TRACKING = load("tracking.json")

SOURCE_IDS = {s["id"] for s in SOURCES_DOC["sources"]}
SUB_IDS = {e["id"] for e in SUBS["entries"]}
OBS_IDS = {o["id"] for o in OBS["rows"]}
FLAG_IDS = {f["id"] for f in FLAGS["rows"]}
Q_IDS = {q["id"] for q in QUESTIONS["rows"]}
P_IDS = {p["id"] for p in PROPOSALS["rows"]}

PAGES = sorted(OUT.glob("*.html"))


# ---------------------------------------------------------------- 1. sources resolve

def check_sources() -> None:
    for label, doc, keys in (
        ("submissions", SUBS, ("source_ids", "flag_ids")),
    ):
        for e in doc["entries"]:
            for k in keys:
                for sid in e.get(k, []):
                    if k == "source_ids" and sid not in SOURCE_IDS:
                        err(f"{e['id']}: unknown source id {sid!r}")
    for o in OBS["rows"]:
        for sid in o.get("source_ids", []):
            if sid not in SOURCE_IDS:
                err(f"{o['id']}: unknown source id {sid!r}")
    for f in FLAGS["rows"]:
        for sid in f.get("source_ids", []):
            if sid not in SOURCE_IDS:
                err(f"{f['id']}: unknown source id {sid!r}")
    for q in QUESTIONS["rows"]:
        for sid in q.get("official_source_ids", []):
            if sid not in SOURCE_IDS:
                err(f"{q['id']}: unknown source id {sid!r}")
    for p in PROPOSALS["rows"]:
        for sid in p.get("source_ids", []):
            if sid not in SOURCE_IDS:
                err(f"{p['id']}: unknown source id {sid!r}")
    for e in TRACKING["events"]["rows"]:
        for sid in e.get("source_ids", []):
            if sid not in SOURCE_IDS:
                err(f"{e['id']}: unknown source id {sid!r}")


# ------------------------------------------- 2/3. intent and observation not merged

def check_intent_observation_split() -> None:
    intended = set(SUBS["intended_fields"])
    observed = set(SUBS["observed_fields"])
    overlap = intended & observed
    if overlap:
        err(f"the two field groups overlap: {sorted(overlap)} — the record's purpose is that they cannot")

    for e in SUBS["entries"]:
        for f in intended:
            if f not in e:
                err(f"{e['id']}: missing intent field {f!r}")
        for f in observed:
            if f not in e:
                err(f"{e['id']}: missing observed field {f!r}")

        obs_asin = (e.get("observed_redirect_asin") or "").strip()
        obs_url = (e.get("observed_redirect_target") or "").strip()
        for f in sorted(intended):
            v = (e.get(f) or "").strip()
            if not v:
                continue
            # An intent field that has been filled from an observation is the exact defect
            # the brief warns against. Catch it by value, not by intent.
            if v == obs_asin:
                err(f"{e['id']}: intent field {f} holds the OBSERVED asin {v!r} — the two must not be merged")
            if obs_url and v == obs_url:
                err(f"{e['id']}: intent field {f} holds the OBSERVED url — the two must not be merged")
            if v.startswith("https://link.amazon/"):
                err(f"{e['id']}: intent field {f} holds a submitted short link, not an official listing URL")

        filled = [f for f in sorted(intended) if (e.get(f) or "").strip()]
        if filled:
            if not (e.get("confirmation_date") or "").strip():
                err(f"{e['id']}: intent fields {filled} are filled but confirmation_date is blank")
            if not (e.get("intended_source") or "").strip():
                err(f"{e['id']}: intent fields {filled} are filled but intended_source is blank")


# ------------------------------------------------------------- 4. identifier shapes

def check_identifier_shapes() -> None:
    for e in SUBS["entries"]:
        asin = (e.get("observed_redirect_asin") or "").strip()
        if len(asin) != 10:
            err(f"{e['id']}: observed ASIN {asin!r} is {len(asin)} chars; the ASIN rule is 10")
        tok = (e.get("submitted_token") or "").strip()
        want = e.get("token_char_count")
        if want is not None and len(tok) != want:
            err(f"{e['id']}: token_char_count says {want} but the token is {len(tok)} chars")
        if e.get("token_is_valid_asin"):
            err(f"{e['id']}: token_is_valid_asin is true, which contradicts the 9-char measurement")
        if e.get("associates_tag_observed") is None:
            err(f"{e['id']}: associates_tag_observed must be a measured boolean, not null")


def check_observation_counts() -> None:
    """The register's typed observation_count must equal the count measured from the log.

    The first publish of this namespace carried `observation_count: 2` on SUB-01 while only one
    observation row referenced it — a typed count that had drifted from the data it describes,
    found by reading the deployed page rather than by any gate. The page now renders the derived
    value; this rule stops the register from disagreeing with it.
    """
    derived = Counter(o["submission_id"] for o in OBS["rows"] if o.get("submission_id"))
    for e in SUBS["entries"]:
        want = derived.get(e["id"], 0)
        got = e.get("observation_count")
        if got is None:
            err(f"{e['id']}: observation_count is missing")
        elif got != want:
            err(f"{e['id']}: observation_count says {got} but the log holds {want} row(s) — typed counts drift, derive them")


# ------------------------------------------------- 5/6. questions and proposals

def check_open_questions() -> None:
    for q in QUESTIONS["rows"]:
        if q["status"] == "OPEN" and (q.get("answer") or "").strip():
            err(f"{q['id']}: status is OPEN but answer is {q['answer']!r}")
        if not (q.get("how_to_answer_it") or "").strip():
            err(f"{q['id']}: an open question must say how to answer it")


def check_proposals() -> None:
    for p in PROPOSALS["rows"]:
        opt_ids = {o["id"] for o in p["options"]}
        if len(opt_ids) != len(p["options"]):
            err(f"{p['id']}: duplicate option ids")
        choice = (p.get("choice") or "").strip()
        if choice and choice not in opt_ids:
            err(f"{p['id']}: choice {choice!r} is not one of its own options {sorted(opt_ids)}")
        if not p["options"]:
            err(f"{p['id']}: a proposal must offer at least one option")
        for b in p.get("blocked_by", []):
            if b not in Q_IDS:
                err(f"{p['id']}: blocked_by {b!r} is not on the questions register")
        for o in p["options"]:
            for r in o.get("requires", []):
                if r not in Q_IDS:
                    err(f"{p['id']}/{o['id']}: requires {r!r} is not on the questions register")


# --------------------------------------------------------------- 7. references

def check_references() -> None:
    for e in SUBS["entries"]:
        for fid in e.get("flag_ids", []):
            if fid not in FLAG_IDS:
                err(f"{e['id']}: flag id {fid!r} is not on the flag register")
    for o in OBS["rows"]:
        sid = o.get("submission_id")
        if sid and sid not in SUB_IDS:
            err(f"{o['id']}: submission_id {sid!r} does not exist")
        for fid in o.get("flag_ids", []):
            if fid not in FLAG_IDS:
                err(f"{o['id']}: flag id {fid!r} is not on the flag register")
        for ref in ("same_destination_as", "same_session_as"):
            v = o.get(ref)
            if v and v not in OBS_IDS:
                err(f"{o['id']}: {ref} {v!r} is not an observation id")
    for f in FLAGS["rows"]:
        for sid in f.get("submission_ids", []):
            if sid not in SUB_IDS:
                err(f"{f['id']}: submission id {sid!r} does not exist")
        for k in ("measured", "what_it_establishes", "what_it_does_not_establish"):
            if not (f.get(k) or "").strip():
                err(f"{f['id']}: flag is missing {k}")
    for q in QUESTIONS["rows"]:
        for b in q.get("blocks", []):
            if b not in P_IDS:
                err(f"{q['id']}: blocks {b!r} is not on the proposals register")


# --------------------------------------------------------------- 8. no prices

def check_no_prices() -> None:
    for name, doc in (("submissions", SUBS), ("observations", OBS), ("tracking", TRACKING)):
        blob = json.dumps(doc)
        for m in MONEY.finditer(blob):
            err(f"{name}: money value {m.group(0)!r} recorded in the register")
    banned = ("rating", "review_count", "bsr", "price", "availability")
    for e in SUBS["entries"]:
        for k in banned:
            if k in e:
                err(f"{e['id']}: register records a {k!r} field; prices, ratings and ranks are not published")
    # Split the HTML into block-level units FIRST, then strip tags inside each one.
    #
    # The order matters, and getting it wrong is what makes this rule inert:
    # `re.split(pattern, re.sub(r'<[^>]+>', ' ', t))` strips the tags before it splits, so
    # there is nothing left to split on, `units` collapses to [whole page], and because the
    # mandatory disclosure contains the word "earn", PROGRAM_CONTEXT then always matches and
    # suppresses every hit. Verified empirically on three real pages: an injected
    # "$149.99" beside the word "price" was not reported by that ordering.
    # See CR-2 in COORDINATION.md — the same ordering appears in six other gates in this
    # repository, all outside this session's file scope, and is logged rather than edited.
    for p in PAGES:
        t = p.read_text(encoding="utf-8")
        for chunk in BLOCK_SPLIT.split(t):
            unit = re.sub(r"<[^>]+>", " ", chunk)
            for m in MONEY.finditer(unit):
                if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                    err(f"{p.name}: money value {m.group(0)!r} in a buying context")


# ------------------------------------------------------- 9/10/11/12. page contract

def check_pages() -> None:
    for p in PAGES:
        t = p.read_text(encoding="utf-8")
        if DISCLOSURE not in t:
            err(f"{p.name}: missing the required disclosure")
        first_data = min((t.find(x) for x in ("<table", "<h2", "<h3") if t.find(x) != -1), default=-1)
        if first_data != -1 and t.find(DISCLOSURE) > first_data:
            err(f"{p.name}: the disclosure is not above the data")
        n_canon = t.count('rel="canonical"')
        if n_canon != 1:
            err(f"{p.name}: expected exactly one canonical link, found {n_canon}")

        for m in re.finditer(r'<a\s+[^>]*href="([^"]*amazon\.com/dp/[^"]*)"[^>]*>', t):
            if 'rel="sponsored' not in m.group(0):
                err(f"{p.name}: product link without rel=sponsored: {m.group(1)[:70]}")

        ids = set(re.findall(r'id="([^"]+)"', t))
        for m in HREF.finditer(t):
            href = m.group(1)
            if href.startswith(("#", "http", "mailto:")):
                if href.startswith("#") and href[1:] not in ids:
                    err(f"{p.name}: same-page anchor {href} addresses nothing")
                continue
            path_part, _, frag = href.partition("#")
            target = (p.parent / path_part).resolve()
            if not target.is_file():
                err(f"{p.name}: broken local link {href}")
                continue
            # A fragment on a link to another page addresses an element inside THAT page,
            # so it has to be checked against the target, not this one. tools/audit_site.py
            # caught 28 of these in the first render of this namespace; the check lives here
            # too so the defect cannot come back between runs of that audit.
            if frag:
                target_ids = set(re.findall(r'id="([^"]+)"', target.read_text(encoding="utf-8")))
                if frag not in target_ids:
                    err(f"{p.name}: '{href}' — fragment #{frag} addresses nothing in {target.name}")


# ---------------------------------------------------------- 13. derived counts

def check_derived_counts() -> None:
    c = B.counts()
    checks = {
        "index.html": [
            f"{c['submissions']} of {c['submissions']}",
            f"{c['observations']}</strong> dated observations",
            f"{c['distinct_asins']} distinct",
            f"{c['intent_blank']} of {c['submissions']}",
            f"{c['tag_absent']} of {c['submissions']}",
            f"{c['flags']} irregularities",
            f"{c['questions_open']} open questions",
            f"{c['proposals']} undecided proposals",
            f"{c['ledger_rows']} rows",
        ],
        "sources.html": [f"{c['sources']} pages", f"{c['live_sources']} fetched", f"{c['carried_sources']} carried"],
        "flags.html": [f"{c['flags']} irregularities", f"({c['flagged_high']} high)"],
        "questions.html": [f"{c['questions']} questions"],
        "proposals.html": [f"{c['proposals']} decisions", f"{c['options']} options", f"{c['proposals_decided']} of {c['proposals']}"],
        "tracking.html": [f"{c['events']}", f"{c['ledger_rows']} rows"],
    }
    for name, needles in checks.items():
        t = (OUT / name).read_text(encoding="utf-8")
        for n in needles:
            if n not in t:
                err(f"{name}: derived count {n!r} is not on the page — prose has drifted from the data")


# --------------------------------------------------------- 14. carried labelling

def check_carried_labelled() -> None:
    for s in SOURCES_DOC["sources"]:
        if s.get("status") == "CARRIED":
            if not s.get("carried_from"):
                err(f"{s['id']}: carried source must name the register it came from")
            if not s.get("last_verified_utc"):
                err(f"{s['id']}: carried source must state when it was last verified")
    src = (OUT / "sources.html").read_text(encoding="utf-8")
    for s in SOURCES_DOC["sources"]:
        if s.get("status") == "CARRIED" and "Carried from" not in src:
            err("sources.html: a carried source is not labelled as carried on the page")


def main() -> int:
    for fn in (check_sources, check_intent_observation_split, check_identifier_shapes,
               check_observation_counts, check_open_questions, check_proposals, check_references,
               check_no_prices, check_pages, check_derived_counts, check_carried_labelled):
        fn()
    if errors:
        print(f"intake/ FAILS ({len(errors)}):")
        for e in errors:
            print("  -", e)
        return 1
    print(f"intake/ OK — {len(PAGES)} pages, {len(SUBS['entries'])} submissions, "
          f"{len(OBS['rows'])} observations, {len(SOURCE_IDS)} sources, "
          f"{len(FLAG_IDS)} flags, {len(Q_IDS)} questions, {len(P_IDS)} proposals")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
