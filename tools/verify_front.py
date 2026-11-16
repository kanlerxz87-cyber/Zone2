#!/usr/bin/env python3
"""Gate for the T50 front-of-house pages (session `arena/9251f262-zone2`).

Run by the deploy workflow after `tools/build_front.py`. It re-reads the eight generated
pages as they sit on disk and fails the build if any of the project's own rules are broken:

  G1  every specification row ends in EITHER a link to an official source OR an explicit
      dash carrying a written reason — never a bare value and never a filled-in guess;
  G2  no page prints a product price;
  G3  every page carries the prescribed Operating Agreement §5 disclosure sentence, in a
      strip above the first product content;
  G4  every outbound product link is marked rel="sponsored nofollow";
  G5  every suggestion row states its status, its options, its recommendation and that it
      is not implemented; every question row states what is known, what is missing and how
      to discover it;
  G6  every internal link resolves to a file that exists;
  G7  every page carries a canonical URL that matches its own path (head_meta contract);
  G8  no page emits a traffic, click, conversion or revenue figure.

It is deliberately strict about the blank rule: an unverified value rendered as a plain
number is treated the same as a fabricated one, because a reader cannot tell them apart.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [
    "index.html",
    "suggestions.html",
    "questions.html",
    "guides/index.html",
    "guides/basket-air-fryers.html",
    "guides/air-fryer-ovens.html",
    "guides/buying-guide.html".replace("buying-guide", "buying-guides"),
    "guides/method.html",
]

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
# A price is a currency amount. The commission percentages (4.50%, 4.00%) and the
# "10-character" ASIN rule are the only numerics this gate must NOT trip on.
PRICE_RE = re.compile(r"(?:US)?\$\s?\d[\d,]*\.?\d{0,2}\b|\b\d[\d,]*\.\d{2}\s?(?:USD|usd)\b")
# A performance *figure* is a number bound to a metric word, e.g. "1,203 visitors",
# "4.2% CTR", "clicks: 812". The words alone are fine — the board is allowed to discuss
# measurement. What the gate forbids is a number attached to one.
METRIC_WORD = r"(?:visitors|visits|page\s?views|sessions|clicks|conversions|impressions|" \
              r"monthly\s+traffic|traffic|revenue|earnings|CTR|click-?through(?:\s+rate)?)"
VANITY_NUM_RE = re.compile(
    rf"\b\d[\d,]*(?:\.\d+)?\s*%?\s+{METRIC_WORD}\b"
    rf"|\b{METRIC_WORD}\s*(?:of|:|=|was|were|is|at)?\s+\d[\d,]*(?:\.\d+)?\s*%?",
    re.I)


def fail(errors: list[str], msg: str) -> None:
    errors.append(msg)


def checks() -> list[str]:
    errors: list[str] = []
    board = json.loads((ROOT / "docs" / "board-9251f262.json").read_text(encoding="utf-8"))

    for rel in PAGES:
        p = ROOT / rel
        if not p.is_file():
            fail(errors, f"G6 missing page: {rel}")
            continue
        h = p.read_text(encoding="utf-8")
        depth = "../" if "/" in rel else ""

        # ---- G1: rows are sourced or explicitly blank -------------------------
        body_rows = re.findall(r'<tr><td class="k">(.*?)</tr>', h, re.S)
        for row in body_rows:
            has_src = 'class="pb-src"' in row
            has_blank = 'class="pb-blank"' in row
            if not has_src and not has_blank:
                fail(errors, f"G1 {rel}: row without a source link or a stated blank: {row[:90]}")
            if has_blank and "<small>" not in row:
                fail(errors, f"G1 {rel}: blank cell carries no written reason: {row[:90]}")

        # ---- G2: no prices ----------------------------------------------------
        for m in PRICE_RE.finditer(h):
            fail(errors, f"G2 {rel}: price-like string {m.group(0)!r}")
        if re.search(r"\b(?:price|list price|MSRP)\b\s*[:=]\s*\d", h, re.I):
            fail(errors, f"G2 {rel}: a numeric price assignment")

        # ---- G3: disclosure above the product content -------------------------
        if DISCLOSURE not in h:
            fail(errors, f"G3 {rel}: prescribed disclosure sentence missing")
        else:
            d_at = h.find(DISCLOSURE)
            if "<main" in h and h.find("<main") < d_at:
                # the disclosure strip sits outside <main>, before it — that is fine;
                # what must not happen is a product table preceding any disclosure.
                pass
            first_table = h.find('<table class="pb-table"')
            if first_table != -1 and d_at > first_table:
                fail(errors, f"G3 {rel}: disclosure appears after product data")

        # ---- G4: sponsored product links --------------------------------------
        for m in re.finditer(r'<a[^>]+href="(https?://(?:www\.)?amazon\.com[^"]*)"[^>]*>', h):
            tag = m.group(0)
            if "sponsored" not in tag or "nofollow" not in tag:
                fail(errors, f"G4 {rel}: amazon.com link without sponsored+nofollow: {tag[:110]}")

        # ---- G6: internal links resolve ---------------------------------------
        for m in re.finditer(r'(?:href|src)="([^"#?]+?)(?:[#?][^"]*)?"', h):
            ref = m.group(1)
            if ref.startswith(("http", "mailto:", "data:")):
                continue
            target = (p.parent / ref).resolve()
            if not target.is_file():
                fail(errors, f"G6 {rel}: broken reference {ref}")

        # ---- G7: canonical matches the path -----------------------------------
        want = "https://kanlerxz87-cyber.github.io/Zone2/" + ("" if rel == "index.html" else rel)
        if f'<link rel="canonical" href="{want}">' not in h:
            fail(errors, f"G7 {rel}: canonical is not {want}")

        # ---- G8: no invented performance metrics ------------------------------
        for m in VANITY_NUM_RE.finditer(h):
            window = h[max(0, m.start() - 90):m.end() + 90]
            # A sentence that says the figure is zero or unmeasured is the honest form and
            # must pass; the gate is only for asserted numbers.
            if re.search(r"\b(zero|0 live|none has been measured|no .{0,24}figure|"
                         r"nothing|unknown|not measured|records nothing)\b", window, re.I):
                continue
            fail(errors, f"G8 {rel}: performance figure asserted: {m.group(0)!r}")

    # ---- G5: board completeness, straight from the dataset --------------------
    for sg in board["suggestions"]:
        if not sg.get("options"):
            fail(errors, f"G5 {sg['id']}: no options")
        if sg.get("recommendation") not in {o["label"] for o in sg["options"]}:
            fail(errors, f"G5 {sg['id']}: recommendation is not one of its options")
        if "Proposed" not in sg.get("status", ""):
            fail(errors, f"G5 {sg['id']}: status is not 'Proposed — awaiting owner decision'")
    for q in board["questions"]:
        for field in ("what_we_know", "what_is_missing", "how_to_discover"):
            if not str(q.get(field, "")).strip():
                fail(errors, f"G5 {q['id']}: empty {field}")
    ids = {s["id"] for s in board["suggestions"]}
    qids = {q["id"] for q in board["questions"]}
    for s in board["suggestions"]:
        for w in s.get("waits_on", []):
            if w not in qids:
                fail(errors, f"G5 {s['id']}: waits on unknown question {w}")
    for q in board["questions"]:
        for b in q.get("blocks", []):
            if b not in ids:
                fail(errors, f"G5 {q['id']}: blocks unknown suggestion {b}")

    return errors


def main() -> int:
    errors = checks()
    if errors:
        print(f"FRONT GATE FAILED — {len(errors)} problem(s):")
        for x in errors:
            print("  •", x)
        return 1
    print(f"front gate OK — {len(PAGES)} pages, all checks pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
