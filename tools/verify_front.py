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
  G9  reader links (incl. the shop) stay in the primary navigation; owner dashboards are grouped under one
      accessible Project & tools disclosure and remain reachable from the footer;
  G10 the current executive-summary product rows match the five intent records and carry
       official Amazon links, with intent fields still explicitly blank;
  G11 the suggestion/question register bylines use the page-update date, not an older
       product-source check date.

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
    "guides/cleanup-and-counter-space-earlier.html",
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


def decision_surface_problems(rel: str, document: str, board: dict) -> list[str]:
    """Keep current-release rollups separate from the date-stamped preserved board."""
    sys.path.insert(0, str(ROOT / "tools"))
    import publication
    from build_front import CHECKED_ON, UPDATED_ON, num_word

    errors: list[str] = []
    current_date = publication.DATE
    page_kind = "suggestions" if rel == "suggestions.html" else "questions"
    date_summary_match = re.search(
        rf'<p class="pb-byline" data-summary-dates="{page_kind}"[^>]*>.*?</p>',
        document,
        re.S,
    )
    date_summary = date_summary_match.group(0) if date_summary_match else ""
    if f"Page last updated {UPDATED_ON}" not in date_summary:
        errors.append(f"G11 {rel}: current page-update label 'last updated {UPDATED_ON}' is missing")
    if CHECKED_ON != UPDATED_ON and f"Page last updated {CHECKED_ON}" in date_summary:
        errors.append(f"G11 {rel}: source-check date is incorrectly presented as the page-update date")
    compiled = str(board.get("compiled_utc") or "unknown")
    directions = [
        str(row["owner_direction"].get("date", ""))
        for row in board.get("suggestions", [])
        if row.get("owner_direction") and row["owner_direction"].get("date")
    ]
    latest_direction = max(directions, default=compiled)

    if rel == "suggestions.html":
        current_count = len(publication.PROPOSALS)
        current_questions = len(publication.QUESTIONS)
        preserved = board["suggestions"]
        preserved_count = len(preserved)
        owner_directions = sum(bool(row.get("owner_direction")) for row in preserved)
        expected_summary = (
            f'<p class="pb-byline" data-current-proposals="{current_count}" '
            f'data-current-questions="{current_questions}" '
            f'data-preserved-proposals="{preserved_count}" '
            f'data-owner-directions="{owner_directions}">'
        )
        if expected_summary not in document:
            errors.append("G9 suggestions.html: current and preserved register counts are not separately derived")
        summary_match = re.search(re.escape(expected_summary) + r"(.*?)</p>", document, re.S)
        summary_text = summary_match.group(0) if summary_match else ""
        for label in (
            f"{current_count} current proposals",
            f"{current_questions} current questions",
            f"{preserved_count} earlier proposals preserved",
            f"{owner_directions} earlier owner directions recorded",
        ):
            if label not in summary_text:
                errors.append(f"G9 suggestions.html: missing current/preserved summary text {label!r}")
        for label in (
            f"{num_word(current_count, cap=True)} current proposals to review.",
            f"{num_word(preserved_count)} earlier proposals are preserved below.",
        ):
            if label not in document:
                errors.append(f"G9 suggestions.html: missing current/preserved heading text {label!r}")
        expected_dates = (
            f'data-summary-dates="suggestions" data-page-updated="{UPDATED_ON}" '
            f'data-current-as-of="{current_date}" data-board-compiled="{compiled}" '
            f'data-owner-directions-through="{latest_direction}"'
        )
        if expected_dates not in date_summary:
            errors.append("G9 suggestions.html: current release and preserved-board dates are not explicit")
        for label in (
            f"current release data as of <time datetime=\"{current_date}\">{current_date}</time>",
            f"earlier board compiled <time datetime=\"{compiled}\">{compiled}</time>",
            f"owner directions recorded through <time datetime=\"{latest_direction}\">{latest_direction}</time>",
        ):
            if label not in date_summary:
                errors.append(f"G9 suggestions.html: visible date label {label!r} is missing")
        if f'id="current-proposals"' not in document or "Current release proposals" not in document:
            errors.append("G9 suggestions.html: current proposals do not have a distinct labelled section")
        if "Earlier decision records, preserved" not in document or "Earlier decision board ·" not in document:
            errors.append("G9 suggestions.html: the preserved suggestion register is not clearly labelled")

        expected_current_ids = [row[0] for row in publication.PROPOSALS]
        actual_current_ids = re.findall(r'<article class="cn-proposal" id="([^"]+)" data-proposal=', document)
        if actual_current_ids != expected_current_ids:
            errors.append("G9 suggestions.html: rendered current proposal rows differ from the current proposal register")
        expected_preserved_ids = [row["id"] for row in preserved]
        actual_preserved_ids = re.findall(r'<article class="pb-decision" id="([^"]+)"', document)
        if actual_preserved_ids != expected_preserved_ids:
            errors.append("G9 suggestions.html: preserved suggestion rows differ from the dated source board")

    elif rel == "questions.html":
        current_count = len(publication.QUESTIONS)
        preserved = board["questions"]
        preserved_count = len(preserved)
        answered = sum(row.get("status") == "answered" for row in preserved)
        open_count = preserved_count - answered
        expected_summary = (
            f'<p class="pb-byline" data-current-questions="{current_count}" '
            f'data-preserved-questions="{preserved_count}" '
            f'data-preserved-open="{open_count}" '
            f'data-preserved-answered="{answered}">'
        )
        if expected_summary not in document:
            errors.append("G9 questions.html: current and preserved question counts are not separately derived")
        summary_match = re.search(re.escape(expected_summary) + r"(.*?)</p>", document, re.S)
        summary_text = summary_match.group(0) if summary_match else ""
        for label in (
            f"{current_count} current questions",
            f"{preserved_count} earlier questions preserved",
            f"{open_count} earlier questions open",
            f"{answered} earlier questions answered",
        ):
            if label not in summary_text:
                errors.append(f"G9 questions.html: missing current/preserved summary text {label!r}")
        if f"{current_count} current questions. Each includes what is known" not in document:
            errors.append("G9 questions.html: current question summary is missing its discovery-context caption")
        expected_dates = (
            f'data-summary-dates="questions" data-page-updated="{UPDATED_ON}" '
            f'data-current-as-of="{current_date}" data-board-compiled="{compiled}"'
        )
        if expected_dates not in date_summary:
            errors.append("G9 questions.html: current release and preserved-board dates are not explicit")
        for label in (
            f"current release data as of <time datetime=\"{current_date}\">{current_date}</time>",
            f"earlier question board compiled <time datetime=\"{compiled}\">{compiled}</time>",
        ):
            if label not in date_summary:
                errors.append(f"G9 questions.html: visible date label {label!r} is missing")
        if f'id="current-release-questions"' not in document or "Current release prerequisites" not in document:
            errors.append("G9 questions.html: current prerequisite register has no distinct label")
        if "Earlier questions, preserved" not in document or "Earlier question register ·" not in document:
            errors.append("G9 questions.html: the earlier question register is not clearly labelled")

        expected_current_ids = [row[0] for row in publication.QUESTIONS]
        actual_current_ids = re.findall(r'<tr id="(Q\d+-[^"]+)"', document)
        if actual_current_ids != expected_current_ids:
            errors.append("G9 questions.html: current prerequisite rows differ from the current question register")
        expected_preserved_ids = [
            row["id"] for row in preserved if row.get("status") != "answered"
        ] + [row["id"] for row in preserved if row.get("status") == "answered"]
        actual_preserved_ids = re.findall(r'<article class="pb-decision" id="([^"]+)"', document)
        if actual_preserved_ids != expected_preserved_ids:
            errors.append("G9 questions.html: preserved question rows differ from the dated source board")

    return errors


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
                fail(errors, f"G3 {rel}: disclosure must be above main content")
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
        # One canonical reader menu, while retaining every prior dashboard/footer link.
        # The previous exact eight-link design is preserved in shop_layout for its dated
        # source pages; the deployed/current publication has a compact four-link menu.
        from verify_publication import Page
        import publication
        nav_match = re.search(r'<nav class="cn-nav" aria-label="Main navigation">(.*?)</nav>', h, re.S)
        if not nav_match:
            fail(errors, f"G9 {rel}: primary publication navigation missing")
        else:
            nav = nav_match.group(1)
            reader_part = nav.split('<details class="cn-workspace-menu"', 1)[0]
            got = [a['href'] for a in Page(reader_part).anchors]
            expected = [depth+x for x in ('shop.html','guides/index.html','compare.html','about.html')]
            if got != expected:
                fail(errors, f"G9 {rel}: reader navigation differs from the canonical compact menu")
            if nav.count('<details class="cn-workspace-menu"') != 1:
                fail(errors, f"G9 {rel}: tools must be in exactly one Workspace group")
            footer = re.search(r'<footer class="cn-footer".*?</footer>', h, re.S)
            if not footer:
                fail(errors, f"G9 {rel}: dashboard footer missing")
            for target, _label in publication.TOOLS:
                if f'href="{depth}{target}"' not in nav:
                    fail(errors, f"G9 {rel}: Workspace group is missing {target}")
                if footer and f'href="{depth}{target}"' not in footer.group(0):
                    fail(errors, f"G9 {rel}: footer is missing preserved target {target}")

        proposal_count = len(board["suggestions"])
        if rel == "index.html":
            if "not measured search queries or volume claims" not in h:
                fail(errors, "G9 index.html: buyer-question topics must be labelled as editorial hypotheses")
            if "proposals sit on the board" in h and f">{proposal_count} proposals sit on the board" not in h:
                fail(errors, "G9 index.html: suggestion count does not match the decision register")
        if rel in {"suggestions.html", "questions.html"}:
            for problem in decision_surface_problems(rel, h, board):
                fail(errors, problem)

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

        # ---- G11: page freshness is distinct from source freshness -----------
        if rel in {"suggestions.html", "questions.html"}:
            sys.path.insert(0, str(ROOT / "tools"))
            from build_front import CHECKED_ON, UPDATED_ON
            current = f"last updated {UPDATED_ON}"
            stale = f"last updated {CHECKED_ON}"
            if current not in h:
                fail(errors, f"G11 {rel}: current page-update label {current!r} is missing")
            if CHECKED_ON != UPDATED_ON and stale in h:
                fail(errors, f"G11 {rel}: source-check date is incorrectly presented as the page-update date")

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
