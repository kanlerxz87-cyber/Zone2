#!/usr/bin/env python3
"""Decision-board gate — T58, session `arena/1bfbc559-zone2` (2026-11-17).

Holds board/ to the same contract as every other namespace in this repository, plus
three rules that are specific to what this board is:

  1. NOTHING IS DECIDED.  Every suggestion carries an empty `chosen` field. The board
     exists so a path is picked before work starts; the moment a row is pre-filled it
     becomes a work list, which is a different thing.
  2. AN OPEN QUESTION CARRIES NO ANSWER.  A question whose state is not `answered` has an
     empty answer. Empty is how this register says the information does not exist yet.
  3. INTENT AND OBSERVATION NEVER MERGE.  No field in a row's `intent` group may hold a
     value copied from that row's `observation` group. That is the whole point of the
     record the brief asked for, and it is the rule most quietly broken by a well-meaning
     later edit.

Plus the rules the repository applies everywhere: every row sourced to a page in the
register, every printed count derived rather than typed, the disclosure on every page and
above the content, internal links and fragments resolving, outbound product links marked
sponsored, and no page printing a product price.

Usage:  python3 tools/validate_board.py [--data DIR] [--html DIR]
        Exits non-zero on any error. --data/--html exist so tools/test_board.py can point
        the gate at a mutated copy and prove each check actually fires.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
MONEY = re.compile(r"\$\s?\d[\d,]*(?:\.\d{1,2})?")
PRICE_CONTEXT = re.compile(
    r"\b(price|pricing|current price|list price|buy|add to cart|deal|discount|sale|offer)\b", re.I)
PROGRAM_CONTEXT = re.compile(
    r"\b(bounty|commission|income|payment|minimum|check|gift card|fee|earn|rate|trial|"
    r"stream|tax|refund|withhold)\w*", re.I)

PAGES = ["index.html", "products.html", "suggestions.html", "questions.html",
         "requirements.html", "topics.html", "sources.html", "verification.html",
         "flagged.html"]


class Board:
    def __init__(self, data: Path, html: Path) -> None:
        self.data = data
        self.html = html
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def load(self, name: str) -> dict:
        try:
            return json.loads((self.data / f"{name}.json").read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            self.err(f"{name}.json: unreadable ({exc})")
            return {}


# --------------------------------------------------------------------- 1. sourcing


def check_sourcing(b: Board) -> None:
    sources = b.load("sources")
    known = {s.get("id") for s in sources.get("sources", [])}
    for sid in sorted(known):
        if not sid:
            b.err("sources: a source row has no id")

    for s in sources.get("sources", []):
        sid = s.get("id", "?")
        if not s.get("url", "").startswith("http"):
            b.err(f"sources: {sid} has no usable URL")
        if not s.get("publisher"):
            b.err(f"sources: {sid} has no publisher")
        if s.get("status") not in ("carried",) and not str(s.get("status", "")).startswith("live"):
            b.err(f"sources: {sid} has status {s.get('status')!r} — must be 'live_<date>' or 'carried'")
        if s.get("status") == "carried" and not s.get("carried_note"):
            b.err(f"sources: {sid} is carried but carries no carried_note")
        if not s.get("quote"):
            b.err(f"sources: {sid} states nothing (empty quote)")

    used: set[str] = set()

    def walk(node, path: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "source_ids" and isinstance(v, list):
                    if not v:
                        b.err(f"{path}.source_ids: empty — every row needs at least one source")
                    for sid in v:
                        if sid not in known:
                            b.err(f"{path}.source_ids: {sid!r} is not in board/data/sources.json")
                        used.add(sid)
                else:
                    walk(v, f"{path}.{k}")
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]")

    for name in ("products", "questions", "requirements", "suggestions", "topics",
                 "verification", "flags"):
        walk(b.load(name), name)

    for sid in sorted(known - used):
        b.warn(f"sources: {sid} is defined but cited by no row")


# --------------------------------------------------------- 2. blank, flagged, nothing decided


def check_blanks_and_board_integrity(b: Board) -> None:
    # --- products: the two field groups -------------------------------------
    for r in b.load("products").get("rows", []):
        rid = r.get("id", "?")
        intent = r.get("intent", {})
        obs = r.get("observation", {})
        filled = [k for k, v in intent.items() if str(v).strip()]
        if filled and len(filled) != len(intent):
            b.err(f"{rid}.intent: partially filled ({', '.join(filled)}) — the four intent "
                  f"fields travel together or stay empty together")
        if not filled and not r.get("intent_blank_reason", "").strip():
            b.err(f"{rid}.intent: empty with no intent_blank_reason — a blank must say why")
        if filled:
            if not intent.get("confirmation_date"):
                b.err(f"{rid}.intent: filled but has no confirmation date")
            if not intent.get("source_of_confirmation"):
                b.err(f"{rid}.intent: filled but has no source of confirmation")
        # rule 3: intent may never borrow a value from observation
        for k, v in intent.items():
            if not str(v).strip():
                continue
            for ok, ov in obs.items():
                if str(ov).strip() and str(v).strip() == str(ov).strip():
                    b.err(f"{rid}: intent.{k} holds the observation value of "
                          f"observation.{ok} — the two field groups must never merge")
        if str(r.get("status", "")).upper() == "VERIFIED" and filled != list(intent):
            b.err(f"{rid}: marked VERIFIED but its intent fields are not complete")

    # --- questions: an open question carries no answer ----------------------
    for q in b.load("questions").get("questions", []):
        qid = q.get("id", "?")
        state = q.get("state")
        if state not in ("answered", "open", "unanswerable-here"):
            b.err(f"{qid}: unknown state {state!r}")
        if state != "answered":
            if str(q.get("answer", "")).strip():
                b.err(f"{qid}: state is {state!r} but an answer is filled in — an open "
                      f"question must stay empty")
            if not str(q.get("how_to_close", "")).strip():
                b.err(f"{qid}: open with no stated way to close it")
            if not str(q.get("who_can_close", "")).strip():
                b.err(f"{qid}: open with nobody named who can close it")
        else:
            if not str(q.get("answer", "")).strip():
                b.err(f"{qid}: marked answered but the answer is empty")

    # --- suggestions: nothing is chosen -------------------------------------
    for s in b.load("suggestions").get("rows", []):
        sid = s.get("id", "?")
        if str(s.get("chosen", "")).strip():
            b.err(f"{sid}: carries a chosen option — this board is where a path is picked, "
                  f"not where work is recorded")
        opts = s.get("options", [])
        if len(opts) < 2:
            b.err(f"{sid}: has {len(opts)} option(s) — a choice needs at least two")
        ids = [o.get("id") for o in opts]
        if len(set(ids)) != len(ids):
            b.err(f"{sid}: duplicate option ids")
        for o in opts:
            for field in ("label", "what", "effort", "risk", "reversibility"):
                if not str(o.get(field, "")).strip():
                    b.err(f"{sid} option {o.get('id')}: missing {field}")
            if not o.get("source_ids"):
                b.err(f"{sid} option {o.get('id')}: unsourced")
        if not str(s.get("lean", "")).strip():
            b.err(f"{sid}: has no lean recorded")

    # --- every row of every register must say something ---------------------
    text_rules = [
        ("requirements", "rows", ["id", "requirement", "brief_status", "measured_status",
                                  "verdict", "measured", "evidence", "gap"]),
        ("topics", "rows", ["id", "working_title", "cluster", "why_this_shape", "rests_on",
                            "status", "existing_page"]),
        ("verification", "rows", ["id", "claim", "method", "result"]),
        ("flags", "rows", ["id", "title", "what", "evidence", "why_it_matters", "status",
                           "owner_action"]),
        ("questions", "questions", ["id", "question", "known", "not_known", "how_to_close",
                                    "who_can_close", "cost_if_left_open"]),
        ("suggestions", "rows", ["id", "title", "why_now"]),
    ]
    for name, key, fields in text_rules:
        for r in b.load(name).get(key, []):
            rid = r.get("id", "?")
            for f in fields:
                if f == "brief_status":
                    continue  # the brief leaves several status cells empty on purpose
                if not str(r.get(f, "")).strip():
                    b.err(f"{name}: {rid}.{f} is empty")

    vocab = set(b.load("requirements").get("verdict_vocabulary", {}))
    for r in b.load("requirements").get("rows", []):
        if r.get("verdict") not in vocab:
            b.err(f"requirements: {r.get('id')} has verdict {r.get('verdict')!r}, "
                  f"outside the published vocabulary")

    for r in b.load("flags").get("rows", []):
        if r.get("severity") not in ("high", "medium", "low", "informational"):
            b.err(f"flags: {r.get('id')} has severity {r.get('severity')!r}")


# --------------------------------------------------------------- 3. derived counts


def check_derived_counts(b: Board) -> None:
    """A count printed on these pages must still match the tree.

    tools/build_board.py records every token it substituted and the value it gave it.
    This re-measures the tree with the same function and compares — so a number typed
    into the data, or a number that the tree has outgrown since, fails here rather than
    on the deployed page. This repository has shipped that defect twice (FB-01, FB-02).
    """
    sys.path.insert(0, str(REPO / "tools"))
    try:
        import build_board as bb  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001
        b.err(f"could not import tools/build_board.py to re-measure: {exc}")
        return

    recorded_path = b.data / "measured.json"
    if not recorded_path.is_file():
        b.err("measured.json is missing — run tools/build_board.py")
        return
    recorded = json.loads(recorded_path.read_text(encoding="utf-8"))
    subs = recorded.get("substitutions", {})

    fresh = bb.measure()
    for key, val in sorted(subs.items()):
        if key not in fresh:
            b.err(f"measured.json: token {key!r} no longer exists in the measurement set")
        elif str(fresh[key]) != str(val):
            b.err(f"derived count drift: {key} was printed as {val!r} but the tree "
                  f"measures {fresh[key]!r} — re-run tools/build_board.py")
    if not subs:
        b.err("measured.json records no substitutions — the derived-count rule is inert")


# ------------------------------------------------------------------- 4. the pages


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, int]] = []
        self.stylesheets: list[str] = []
        self.main_at: int | None = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "main" and self.main_at is None:
            self.main_at = self.getpos()[0]
        if tag == "link" and a.get("rel") == "stylesheet":
            self.stylesheets.append(a.get("href", ""))
        if tag == "a" and a.get("href"):
            self.links.append((a["href"], self.getpos()[0]))


def check_pages(b: Board) -> None:
    parsed: dict[str, Page] = {}
    heads: dict[str, str] = {}
    bodies: dict[str, str] = {}

    for name in PAGES:
        path = b.html / name
        if not path.is_file():
            b.err(f"{name}: missing — run tools/build_board.py")
            continue
        text = path.read_text(encoding="utf-8")
        p = Page()
        p.feed(text)
        parsed[name] = p
        head_end = text.find("</head>")
        heads[name] = text[: head_end if head_end > 0 else 0]
        bodies[name] = text

        if DISCLOSURE not in text:
            b.err(f"{name}: missing the required disclosure sentence")
        elif p.main_at is not None and text.find(DISCLOSURE) > text.find("<main"):
            b.err(f"{name}: the disclosure sits inside <main> — it has to be above the content")
        if text.count(DISCLOSURE) < 2:
            b.err(f"{name}: the disclosure appears once — it must be above the fold and in the footer")

        if "{{" in text and re.search(r"\{\{\w+\}\}", text):
            b.err(f"{name}: an unsubstituted token survived into the output")

    # head meta
    titles: dict[str, str] = {}
    descs: dict[str, str] = {}
    for name, head in heads.items():
        m = re.search(r"<title[^>]*>(.*?)</title>", head, re.S | re.I)
        if not m or not m.group(1).strip():
            b.err(f"{name}: no <title>")
        else:
            titles[name] = m.group(1).strip()
        m = re.search(r"<meta\s+name=[\"']description[\"']\s+content=[\"'](.*?)[\"']", head, re.S | re.I)
        if not m or not m.group(1).strip():
            b.err(f"{name}: no meta description")
        else:
            descs[name] = m.group(1).strip()
        if f'canonical" href="{ "https://kanlerxz87-cyber.github.io/Zone2/board/" + name }"' not in head:
            b.err(f"{name}: wrong or missing canonical")
        for prop in ("og:type", "og:site_name", "og:title", "og:description", "og:url"):
            if prop not in head:
                b.err(f"{name}: missing {prop}")

    for label, mapping in (("title", titles), ("meta description", descs)):
        seen: dict[str, str] = {}
        for name, val in mapping.items():
            if val in seen:
                b.err(f"{name}: duplicate {label} with {seen[val]}")
            seen[val] = name

    # links, fragments, stylesheets
    for name, p in parsed.items():
        for href, line in p.links:
            if href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
                if not href.startswith("https://"):
                    b.err(f"{name}:{line}: non-https external link {href}")
                continue
            if href.startswith("#"):
                if href[1:] and href[1:] not in p.ids:
                    b.err(f"{name}:{line}: fragment {href} addresses nothing in this page")
                continue
            target_name, _, frag = href.partition("#")
            target_name = target_name.split("?")[0]
            target = (b.html / target_name) if not target_name.startswith("../") \
                else (b.html.parent / target_name[3:])
            if target_name.startswith("../") and target_name[3:] in ("COORDINATION.md",):
                if not (b.html.parent / "COORDINATION.md").is_file():
                    b.err(f"{name}:{line}: {href} does not resolve")
                continue
            if not target.is_file():
                b.err(f"{name}:{line}: {href} does not resolve")
                continue
            if frag and target_name.endswith(".html"):
                tp = parsed.get(target.name)
                if tp is None:
                    tp = Page()
                    tp.feed(target.read_text(encoding="utf-8"))
                if frag not in tp.ids:
                    b.err(f"{name}:{line}: {href} — fragment #{frag} addresses nothing in {target.name}")
        for css in p.stylesheets:
            if not (b.html / css).is_file():
                b.err(f"{name}: stylesheet {css} does not resolve")

    # sponsored outbound product links + no prices
    for name, text in bodies.items():
        for m in re.finditer(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>", text, re.I):
            href, tag = m.group(1), m.group(0)
            if re.search(r"(amazon\.com/dp/|amazon\.com/[^/]*/dp/|link\.amazon/|amzlinks\.in/)", href):
                rel = re.search(r"rel=[\"']([^\"']*)[\"']", tag, re.I)
                if not rel or "sponsored" not in rel.group(1).lower():
                    b.err(f"{name}: product link {href} is not marked rel=\"sponsored\"")
        # Split FIRST, then strip tags. The other four copies of this rule in the
        # repository strip first and then split on tags that no longer exist, so every
        # page collapses to one unit and the program-economics exemption swallows every
        # product price. See FL-13 on board/flagged.html.
        units = [re.sub(r"<[^>]+>", " ", u)
                 for u in re.split(r"</tr>|</p>|</li>|<br\s*/?>", text)]
        for unit in units:
            for m in MONEY.finditer(unit):
                if PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit):
                    b.err(f"{name}: money value {m.group(0)!r} in a buying context")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(REPO / "board" / "data"))
    ap.add_argument("--html", default=str(REPO / "board"))
    args = ap.parse_args(argv)

    b = Board(Path(args.data), Path(args.html))
    check_sourcing(b)
    check_blanks_and_board_integrity(b)
    check_derived_counts(b)
    check_pages(b)

    if b.warnings:
        print("warnings:")
        for w in b.warnings:
            print(f"  WARN  {w}")
    if b.errors:
        print(f"{len(b.errors)} error(s):")
        for err in b.errors:
            print(f"  ERROR {err}")
        return 1
    print(f"board/: all checks pass ({len(PAGES)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
