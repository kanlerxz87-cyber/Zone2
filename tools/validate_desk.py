#!/usr/bin/env python3
"""Gate for the T63 decision desk, overlay and thermometer guides (session `arena/6ce606cb-zone2`).

  D1  every suggestion (T50 board + T63 overlay) has a valid goal, a unique id, options with
      text/cost/trade-off, a recommendation that is one of its options, and a Proposed status;
  D2  every waits_on names a known question; every question's blocks names a known suggestion;
      every question states what is known, what is missing and how to find out;
  D3  every cited source key exists in a register and is an https URL; brief signals name a
      known suggestion and one of its options;
  D4  desk/index.html and desk/questions.html: every id rendered once, counts printed equal the
      derived counts, nothing rendered as decided, disclosure before the first table, canonical
      matches the path, no price, internal links resolve, amazon links sponsored+nofollow;
  D5  thermometer guides: every paragraph, list item, table row or note inside the article that
      states a Fahrenheit figure carries a citation link in the same block; every food-safety row
      cites FoodSafety.gov; every highlighted thermometer attribute exists in the ledger rows.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_desk as bd  # noqa: E402
import build_front as bf  # noqa: E402

ROOT = bf.ROOT
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
PRICE_RE = re.compile(r"(?:US)?\$\s?\d[\d,]*\.?\d{0,2}\b")
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"


def main() -> int:
    errs: list[str] = []
    d = bd.desk_data()
    ov = bf.extras()["overlay"]
    sids = [s["id"] for s in d["suggestions"]]
    qids = {q["id"] for q in d["questions"]}

    # D1
    for i in {x for x in sids if sids.count(x) > 1}:
        errs.append(f"D1 duplicate suggestion id {i}")
    for s in d["suggestions"]:
        if s.get("goal") not in d["goals"]:
            errs.append(f"D1 {s['id']}: goal {s.get('goal')!r} is not one of {list(d['goals'])}")
        if not s.get("options"):
            errs.append(f"D1 {s['id']}: no options")
        for o in s.get("options", []):
            for f in ("label", "text", "cost", "tradeoff"):
                if not str(o.get(f, "")).strip():
                    errs.append(f"D1 {s['id']}: option missing {f}")
        if s.get("recommendation") not in {o["label"] for o in s.get("options", [])}:
            errs.append(f"D1 {s['id']}: recommendation is not one of its options")
        if "Proposed" not in s.get("status", ""):
            errs.append(f"D1 {s['id']}: status is not Proposed")
    # D2
    for s in d["suggestions"]:
        for w in s.get("waits_on", []):
            if w not in qids:
                errs.append(f"D2 {s['id']}: waits on unknown question {w}")
    for q in d["questions"]:
        for b in q.get("blocks", []):
            if b not in sids:
                errs.append(f"D2 {q['id']}: blocks unknown suggestion {b}")
        for f in ("what_we_know", "what_is_missing", "how_to_discover"):
            if not str(q.get(f, "")).strip():
                errs.append(f"D2 {q['id']}: empty {f}")
    # D3
    for item in d["suggestions"] + d["questions"]:
        sid = item.get("source")
        if sid and sid not in d["sources"]:
            errs.append(f"D3 {item['id']}: unknown source {sid}")
    for k, s in d["sources"].items():
        if not s["url"].startswith("https://"):
            errs.append(f"D3 source {k}: not an https URL")
    for k, sig in d["signals"].items():
        sg = next((s for s in d["suggestions"] if s["id"] == k), None)
        if not sg:
            errs.append(f"D3 brief signal for unknown suggestion {k}")
        elif sig["matches"] not in {o["label"] for o in sg["options"]}:
            errs.append(f"D3 brief signal {k}: option {sig['matches']} does not exist")

    # D4
    for rel, ids, counts in (
        ("desk/index.html", sids, {"suggestions": len(sids),
                                   "open-questions": sum(1 for q in d["questions"] if q["status"] != "answered")}),
        ("desk/questions.html", sorted(qids), {"questions": len(qids),
                                               "open-questions": sum(1 for q in d["questions"] if q["status"] != "answered")}),
    ):
        p = ROOT / rel
        if not p.is_file():
            errs.append(f"D4 missing {rel}")
            continue
        h = p.read_text(encoding="utf-8")
        for i in ids:
            n = h.count(f'id="{i}"')
            if n != 1:
                errs.append(f"D4 {rel}: id {i} rendered {n} times")
        for key, want in counts.items():
            m = re.search(rf'data-count="{key}">(\d+)<', h)
            if not m or int(m.group(1)) != want:
                errs.append(f"D4 {rel}: printed {key} {m.group(1) if m else 'absent'} != derived {want}")
        if re.search(r'pb-pill[^"]*">\s*(?:decided|approved|done)\b', h, re.I):
            errs.append(f"D4 {rel}: a row is rendered as decided")
        dpos, tpos = h.find(DISCLOSURE), h.find("<table")
        if dpos == -1 or (tpos != -1 and dpos > tpos):
            errs.append(f"D4 {rel}: disclosure missing or after the first table")
        if f'<link rel="canonical" href="{SITE}{rel}">' not in h:
            errs.append(f"D4 {rel}: canonical does not match the path")
        for m in PRICE_RE.finditer(h):
            errs.append(f"D4 {rel}: price-like string {m.group(0)!r}")
        for m in re.finditer(r'href="([^"#?]+?)(?:[#?][^"]*)?"', h):
            ref = m.group(1)
            if ref.startswith(("http", "mailto:")):
                continue
            if not (p.parent / ref).resolve().is_file():
                errs.append(f"D4 {rel}: broken link {ref}")
        for m in re.finditer(r'<a[^>]+href="https?://(?:www\.)?amazon\.[^"]*"[^>]*>', h):
            if "sponsored" not in m.group(0) or "nofollow" not in m.group(0):
                errs.append(f"D4 {rel}: amazon link without sponsored+nofollow")

    # D5
    for g in ov["guides"]:
        p = ROOT / "guides" / g["slug"]
        if not p.is_file():
            errs.append(f"D5 missing guide {g['slug']}")
            continue
        h = p.read_text(encoding="utf-8")
        m = re.search(r'<article class="pb-article">(.*?)</article>', h, re.S)
        if not m:
            errs.append(f"D5 {g['slug']}: no article body")
            continue
        art = m.group(1)
        blocks = re.findall(r"<p[ >].*?</p>|<li>.*?</li>|<tr>.*?</tr>|<div class=\"pb-note\">.*?</div>", art, re.S)
        for b in blocks:
            if re.search(r"(?:&deg;|°)\s*F", b) and 'class="pb-src"' not in b:
                errs.append(f"D5 {g['slug']}: temperature without a citation: {re.sub('<[^>]+>', '', b)[:90]!r}")
    for r in ov["food_safety"]:
        if r.get("src") != "FS1":
            errs.append(f"D5 food-safety row {r['attr']!r} is not cited to FoodSafety.gov (FS1)")
    for t in ov["thermometers"]:
        th = next(x for x in bf.extras()["thermos"] if x["key"] == t["key"])
        have = {r["attr"] for r in th["rows"]}
        for hl in t["highlights"]:
            if hl not in have:
                errs.append(f"D5 {t['key']}: highlight {hl!r} is not a ledger row")

    if errs:
        print(f"DESK GATE FAILED — {len(errs)} problem(s):")
        for x in errs:
            print("  •", x)
        return 1
    print(f"desk gate OK — {len(sids)} suggestions in {len(d['goals'])} goals, {len(qids)} questions, "
          f"{len(ov['guides'])} guides; D1–D5 pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
