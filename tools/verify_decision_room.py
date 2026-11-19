#!/usr/bin/env python3
"""Gate for the Decision Room and design brief (T69, session `arena/698addcd-zone2`).

`tools/build_decision_room.py` writes the two pages from `content/decision-room.json`. This gate
re-reads them **as they sit on disk** and fails the build if a page breaks one of the rules the
project already holds every other reader page to:

  D1  the Operating Agreement disclosure sentence is present, above `<main>`, and repeated in
      the footer (the same rule S3/G3 apply to the shop and front pages);
  D2  every page carries a canonical URL that is its own live path, and `index,follow`;
  D3  every internal link and asset reference resolves to a file on disk;
  D4  no price, and no asserted traffic / conversion / revenue / search-volume figure —
      a page about decisions is exactly where an invented number would do the most damage;
  D5  every decision row shows its status, all of its options, the cost and the give-up for each
      option, a recommendation that is one of its own options, its evidence, and the single
      answer that unblocks it;
  D6  every cited source resolves to an https URL, and every source id used by a row exists in
      the register (a dangling id would be an unlinked claim);
  D7  every owner question is referenced by at least one decision, and every decision that names
      `owner_question` names one that exists in the register;
  D8  the rendered pages match `content/decision-room.json` — i.e. `build_decision_room.py
      --check` would pass — so a hand edit to the HTML cannot diverge from the register;
  D9  no decision row claims to be `fixed` unless it carries a written note of what was fixed,
      and no row marked `open` or `blocked` describes itself as implemented.

Exit code 1 on any failure, with every failure printed.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "content" / "decision-room.json"
PAGES = ["decision-room.html", "decision-prompt.html"]
BASE = "https://kanlerxz87-cyber.github.io/Zone2/"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

# A price, or a performance figure bound to a metric word. Percentages are allowed: every source
# register in this repository quotes a commission rate, and those are policy facts, not forecasts.
MONEY = re.compile(r"(?:US)?\$\s?\d[\d,]*\.?\d{0,2}\b|\b\d[\d,]*\.\d{2}\s?(?:USD|usd)\b")
METRIC = re.compile(
    r"\b\d[\d,.]*\s*(?:%|percent)[^.]{0,40}\b(?:conversion|click[- ]through|CTR|revenue|earnings?|ROI|increase|uplift)\b"
    r"|\b(?:conversion rate|click[- ]through rate|search volume|monthly searches|estimated revenue|projected revenue)\b[^.]{0,30}?\b\d",
    re.I,
)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


class Refs(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.external: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.refs.append(a["src"])
        if tag == "link" and a.get("href"):
            if a.get("rel") == "stylesheet":
                self.refs.append(a["href"])
        if tag == "img" and a.get("src"):
            self.refs.append(a["src"])
        if tag == "a" and a.get("href"):
            href = a["href"]
            if href.startswith(("http://", "https://")):
                self.external.append(href)
            elif not href.startswith(("#", "mailto:")):
                self.refs.append(href.split("#", 1)[0])


def main() -> int:
    errors: list[str] = []
    data = json.loads(DATA.read_text(encoding="utf-8"))
    known_sources = set(data["sources"])
    known_questions = {q["id"] for q in data["owner_questions"]}
    referenced_questions: set[str] = set()

    # ---- D5 / D6 / D7 / D9: the register itself --------------------------------
    for d in data["decisions"]:
        rid = d.get("id", "<no id>")
        for field in ("id", "cluster", "title", "question", "status", "evidence",
                      "options", "recommendation", "recommendation_reason", "unblocks_with"):
            if not d.get(field):
                fail(errors, f"D5 {rid}: missing '{field}'")
        if d.get("status") not in {"open", "fixed", "blocked"}:
            fail(errors, f"D5 {rid}: unknown status {d.get('status')!r}")
        options = d.get("options") or []
        if len(options) < 2:
            fail(errors, f"D5 {rid}: needs at least two options")
        ids = [o.get("id") for o in options]
        if d.get("recommendation") not in ids:
            fail(errors, f"D5 {rid}: recommendation {d.get('recommendation')!r} is not one of its options {ids}")
        for o in options:
            for field in ("id", "label", "costs", "gives_up"):
                if not o.get(field):
                    fail(errors, f"D5 {rid}: option {o.get('id')} missing '{field}'")
        if not d.get("evidence"):
            fail(errors, f"D5 {rid}: no evidence")
        for item in d.get("evidence") or []:
            if not item.get("claim"):
                fail(errors, f"D5 {rid}: evidence entry without a claim")
            sid = item.get("src")
            if sid not in known_sources:
                fail(errors, f"D6 {rid}: evidence cites unknown source id {sid!r}")
        if d.get("status") == "fixed":
            if not d.get("fixed_note"):
                fail(errors, "D9 %s: marked fixed but has no fixed_note" % rid)
        else:
            if d.get("fixed_note"):
                fail(errors, f"D9 {rid}: not fixed but carries a fixed_note")
        oq = d.get("owner_question")
        if oq:
            if oq not in known_questions:
                fail(errors, f"D7 {rid}: owner_question {oq!r} does not exist")
            referenced_questions.add(oq)

    for src_id, src in data["sources"].items():
        url = src.get("url", "")
        if not url.startswith("https://"):
            fail(errors, f"D6 source {src_id}: not an https URL ({url!r})")
        if not src.get("label"):
            fail(errors, f"D6 source {src_id}: no label")
    # Every declared question should unblock something, or it is noise on the owner's desk.
    for q in data["owner_questions"]:
        if q["id"] not in referenced_questions:
            fail(errors, f"D7 {q['id']}: no decision names it in owner_question")
        for b in q.get("blocks") or []:
            if b not in {d["id"] for d in data["decisions"]}:
                fail(errors, f"D7 {q['id']}: blocks unknown decision {b!r}")

    # ---- D8: rendered output is the register ----------------------------------
    sys.path.insert(0, str(ROOT / "tools"))
    import build_decision_room as gen  # noqa: E402
    rendered_pages: list[tuple[str, str]] = []
    for name, builder in (("decision-room.html", gen.build_room), ("decision-prompt.html", gen.build_prompt)):
        try:
            rendered_pages.append((name, builder(data)))
        except Exception as exc:  # a malformed register must fail the gate, not traceback
            fail(errors, f"D8 {name}: renderer raised {type(exc).__name__}: {exc}")
    for name, rendered in rendered_pages:
        path = ROOT / name
        if not path.is_file():
            fail(errors, f"D8 {name}: not generated — run tools/build_decision_room.py")
        elif path.read_text(encoding="utf-8") != rendered:
            fail(errors, f"D8 {name}: on disk differs from content/decision-room.json — re-run tools/build_decision_room.py")

    # ---- per-page HTML rules --------------------------------------------------
    for rel in PAGES:
        path = ROOT / rel
        if not path.is_file():
            continue
        h = path.read_text(encoding="utf-8")

        main_at = h.find("<main")
        first = h.find(DISCLOSURE)
        if first == -1:
            fail(errors, f"D1 {rel}: disclosure sentence missing")
        elif main_at == -1 or first > main_at:
            fail(errors, f"D1 {rel}: disclosure is not above <main>")
        foot = h.find("<footer")
        if foot == -1 or DISCLOSURE not in h[foot:]:
            fail(errors, f"D1 {rel}: disclosure not repeated in the footer")

        want = f'<link rel="canonical" href="{BASE}{rel}">'
        if want not in h:
            fail(errors, f"D2 {rel}: canonical is not {BASE}{rel}")
        if '<meta name="robots" content="index,follow">' not in h:
            fail(errors, f"D2 {rel}: not index,follow")
        if h.count("<h1") != 1:
            fail(errors, f"D2 {rel}: expected exactly one <h1>, found {h.count('<h1')}")

        refs = Refs()
        refs.feed(h)
        for ref in refs.refs:
            if ref in ("", "#"):
                continue
            if not (path.parent / ref).resolve().is_file():
                fail(errors, f"D3 {rel}: broken reference {ref}")
        for url in refs.external:
            parts = urlsplit(url)
            if parts.scheme not in ("http", "https"):
                fail(errors, f"D3 {rel}: unexpected external scheme {url}")

        for m in MONEY.finditer(h):
            fail(errors, f"D4 {rel}: price-like value {m.group(0)!r}")
        for m in METRIC.finditer(h):
            fail(errors, f"D4 {rel}: asserted performance figure {m.group(0)!r}")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"decision room gate PASS: {len(PAGES)} pages, {len(data['decisions'])} decisions, "
          f"{len(data['owner_questions'])} owner questions, {len(data['sources'])} sources")
    return 0


if __name__ == "__main__":
    sys.exit(main())
