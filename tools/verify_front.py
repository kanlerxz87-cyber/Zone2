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
  G8  no page emits a traffic, click, conversion or revenue figure;
  G9  reader links stay in the primary navigation; owner dashboards are grouped under one
      accessible Project & tools disclosure and remain reachable from the footer;
  G10 the current executive-summary product rows match the five intent records and carry
       official Amazon links, with intent fields still explicitly blank.

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
    "summary.html",
    "suggestions.html",
    "questions.html",
    "guides/index.html",
    "guides/basket-air-fryers.html",
    "guides/air-fryer-ovens.html",
    "guides/buying-guide.html".replace("buying-guide", "buying-guides"),
    "guides/method.html",
    # T63 (session 10727edd, 2026-11-19): the reader-first pages build_front.py now writes.
    # Same eight rules; a new page that is not on this list would be ungated.
    "guides/meat-thermometers.html",
    "guides/instant-read-or-wireless-thermometer.html",
    "guides/thermometer-for-air-fryer.html",
    "guides/multi-function-appliance-questions.html",
    "guides/cleanup-and-counter-space.html",
    "behind-the-site.html",
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
    submissions = json.loads((ROOT / "intake" / "data" / "submissions.json").read_text(encoding="utf-8"))["entries"]

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
        # T58 (2026-11-17): the owner supplied the Associates tag, so the rules hardened.
        #  - a product CTA (class="pb-bench-cta") MUST carry the owner's tag;
        #  - any tagged link must carry THE owner's tag, never another account's;
        #  - a citation link (class="pb-src") MUST NOT carry a tag: evidence stays unmonetized.
        for m in re.finditer(r'<a[^>]+href="(https?://(?:www\.)?amazon\.com[^"]*)"[^>]*>', h):
            tag = m.group(0)
            href = m.group(1)
            if "sponsored" not in tag or "nofollow" not in tag:
                fail(errors, f"G4 {rel}: amazon.com link without sponsored+nofollow: {tag[:110]}")
            classes = re.search(r'class="([^"]*)"', tag)
            cls = classes.group(1).split() if classes else []
            if "pb-bench-cta" in cls and "tag=shopnow047c-20" not in href:
                fail(errors, f"G4 {rel}: product CTA without the owner's Associates tag: {href[:110]}")
            if "pb-src" in cls and "tag=" in href:
                fail(errors, f"G4 {rel}: citation link carries an Associates tag; evidence must stay unmonetized: {href[:110]}")
            if "tag=" in href and "tag=shopnow047c-20" not in href:
                fail(errors, f"G4 {rel}: Associates tag other than the owner's on {href[:110]}")

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

        # ---- G9: reader-first navigation; owner tools stay grouped -------------
        nav_match = re.search(r'<nav class="pb-nav" aria-label="Primary navigation">(.*?)</nav>', h, re.S)
        if not nav_match:
            fail(errors, f"G9 {rel}: primary publication navigation missing")
        else:
            nav = nav_match.group(1)
            reader_part = nav.split('<details class="pb-nav-tools"', 1)[0]
            got = [href for href, _ in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', reader_part, re.S)]
            expected = [depth + x for x in (
                "index.html", "marketing/buying-guide.html", "guides/index.html",
                "marketing/comparison.html", "journal/index.html", "marketing/index.html")]
            if got != expected:
                fail(errors, f"G9 {rel}: reader navigation is not the expected six-link publication menu")
            if nav.count('<details class="pb-nav-tools"') != 1 or "Project &amp; tools" not in nav:
                fail(errors, f"G9 {rel}: owner tools are not in one Project & tools disclosure group")
            tool_menu = nav.split('<div class="pb-nav-menu">', 1)[-1].split('</div>', 1)[0]
            tools = (
                "suggestions.html", "questions.html", "brief/index.html", "intake/index.html",
                "board/index.html", "products.html", "analysis.html", "content.html",
                "compliance.html", "tracking.html", "verification.html", "sources.html",
                "flagged.html", "summary.html")
            for target in tools:
                if f'href="{depth}{target}"' not in tool_menu:
                    fail(errors, f"G9 {rel}: Project & tools group is missing {target}")
            footer = re.search(r'<footer class="pb-foot".*?</footer>', h, re.S)
            if not footer:
                fail(errors, f"G9 {rel}: dashboard footer missing")
            else:
                for target in ("brief/index.html", "intake/index.html", "board/index.html",
                               "products.html", "analysis.html", "content.html", "compliance.html",
                               "tracking.html", "verification.html", "sources.html", "summary.html"):
                    if f'href="{depth}{target}"' not in footer.group(0):
                        fail(errors, f"G9 {rel}: footer does not expose {target}")

        proposal_count = len(board["suggestions"])
        if rel == "index.html":
            if "not measured search queries or volume claims" not in h:
                fail(errors, "G9 index.html: buyer-question topics must be labelled as editorial hypotheses")
            if f">{proposal_count} proposals sit on the board" not in h:
                fail(errors, "G9 index.html: suggestion count does not match the decision register")
        if rel == "suggestions.html" and f">{proposal_count} proposals. <em>None is applied yet.</em>" not in h:
            fail(errors, "G9 suggestions.html: headline count does not match the decision register")

        # ---- G10: the five-link summary stays in sync with intent records -----
        if rel == "summary.html":
            product_rows = re.findall(r'<tr id="(SUB-\d+)">(.*?)</tr>', h, re.S)
            if len(product_rows) != len(submissions):
                fail(errors, f"G10 {rel}: rendered {len(product_rows)} product-intent rows, expected {len(submissions)}")
            by_id = {item["id"]: item for item in submissions}
            for sub_id, row in product_rows:
                item = by_id.get(sub_id)
                if not item:
                    fail(errors, f"G10 {rel}: unknown product-intent row {sub_id}")
                    continue
                asin = item.get("observed_redirect_asin", "")
                if asin and f'<code>{asin}</code>' not in row:
                    fail(errors, f"G10 {rel}: {sub_id} does not display its recorded observed ASIN separately from intent")
                if f'href="intake/submissions.html#{sub_id}"' not in row:
                    fail(errors, f"G10 {rel}: {sub_id} does not link to its intent/observation record")
                if not item.get("intended_asin") and "Not confirmed" not in row:
                    fail(errors, f"G10 {rel}: {sub_id} fills or hides an unconfirmed intended ASIN")
            for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', h, re.S):
                if "<td" in row and not re.search(r'href="https://(?:www\.)?(?:amazon\.com|affiliate-program\.amazon\.com|ftc\.gov|developers\.google\.com|docs\.github\.com|support\.google\.com)', row):
                    fail(errors, f"G10 {rel}: summary table row has no official external source link")

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
        od = sg.get("owner_direction")
        if od:
            # T63 (session 10727edd): a row may read "Decided" only with a recorded owner direction
            # whose quote is, word for word, the text of the option it names.
            opt = next((o for o in sg["options"] if o["label"] == od.get("chosen_option")), None)
            if not opt:
                fail(errors, f"G5 {sg['id']}: owner_direction names an option the row does not have")
            elif od.get("quote") != opt["text"]:
                fail(errors, f"G5 {sg['id']}: owner_direction quote is not the option's text verbatim")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(od.get("date", ""))) or not od.get("source"):
                fail(errors, f"G5 {sg['id']}: owner_direction needs an ISO date and a source")
            if not sg.get("status", "").startswith("Decided"):
                fail(errors, f"G5 {sg['id']}: has an owner_direction but status does not say Decided")
        else:
            if "Proposed" not in sg.get("status", ""):
                fail(errors, f"G5 {sg['id']}: status is not 'Proposed — awaiting owner decision'")
            if sg.get("implemented"):
                fail(errors, f"G5 {sg['id']}: marked implemented with no recorded owner direction")
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
