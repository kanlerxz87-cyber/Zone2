#!/usr/bin/env python3
"""Negative tests for the decision-board gate — T58, session 1bfbc559.

Every check in tools/validate_board.py is proven to fire by injecting the defect it exists
to catch into a throwaway copy of board/ and asserting the gate fails with the expected
message. A gate that has only ever passed is a claim, not a control: this repository's own
history is the argument — the defect class these rules were written for (a typed count the
tree outgrew) shipped twice before anything recomputed it.

Usage:  python3 tools/test_board.py
        Exits non-zero if any injected defect fails to fire, or if the unmutated board
        fails to pass.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BOARD = REPO / "board"
DATA = BOARD / "data"
VALIDATOR = REPO / "tools" / "validate_board.py"

PAGES = ["index.html", "products.html", "suggestions.html", "questions.html",
         "requirements.html", "topics.html", "sources.html", "verification.html",
         "flagged.html"]


def snapshot(root: Path) -> None:
    """A minimal mirror of the repo layout, so relative links resolve as they do on disk.

    The board's pages link upward (../index.html, ../marketing/comparison.html …) and
    sideways (assets/board.css). Without stand-ins for those targets the gate fails on
    link resolution for every case, and the negative tests would prove nothing.
    """
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "board" / "assets").mkdir(parents=True, exist_ok=True)
    for f in DATA.glob("*.json"):
        shutil.copy2(f, root / "data" / f.name)
    for name in PAGES:
        shutil.copy2(BOARD / name, root / "board" / name)
    shutil.copy2(BOARD / "assets" / "board.css", root / "board" / "assets" / "board.css")
    # Stand-ins for everything the board links to outside its own namespace.
    for rel in ("index.html", "COORDINATION.md", "suggestions.html", "questions.html",
                "flagged.html", "marketing/comparison.html", "marketing/buying-guide.html",
                "guides/index.html", "brief/index.html"):
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("<!DOCTYPE html><html><body>stand-in</body></html>\n", encoding="utf-8")


def run_gate(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), "--data", str(root / "data"),
         "--html", str(root / "board")],
        capture_output=True, text=True, cwd=str(REPO),
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def load(root: Path, name: str) -> dict:
    return json.loads((root / "data" / f"{name}.json").read_text(encoding="utf-8"))


def save(root: Path, name: str, obj: dict) -> None:
    (root / "data" / f"{name}.json").write_text(
        json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def first(root: Path, name: str, key: str):
    return load(root, name)[key][0]


def replace_first(root: Path, name: str, key: str, obj) -> None:
    d = load(root, name)
    d[key][0] = obj
    save(root, name, d)


def edit_html(root: Path, page: str, old: str, new: str) -> None:
    p = root / "board" / page
    t = p.read_text(encoding="utf-8")
    if old not in t:
        raise AssertionError(f"defect fixture not found in {page}: {old[:80]!r}")
    p.write_text(t.replace(old, new, 1), encoding="utf-8")


# --------------------------------------------------------------- the defect cases


def d_chosen(root: Path) -> None:
    replace_first(root, "suggestions", "rows",
                  {**first(root, "suggestions", "rows"), "chosen": "A"})


def d_open_answer(root: Path) -> None:
    d = load(root, "questions")
    for q in d["questions"]:
        if q["state"] == "open":
            q["answer"] = "Yes, obviously."
            break
    save(root, "questions", d)


def d_merge_fields(root: Path) -> None:
    d = load(root, "products")
    r = d["rows"][0]
    r["intent"]["intended_asin"] = r["observation"]["observed_asin"]
    r["intent"]["official_listing_url"] = r["observation"]["observed_redirect_url"]
    save(root, "products", d)


def d_blank_without_reason(root: Path) -> None:
    d = load(root, "products")
    d["rows"][0]["intent_blank_reason"] = ""
    save(root, "products", d)


def d_partial_intent(root: Path) -> None:
    d = load(root, "products")
    d["rows"][0]["intent"]["intended_asin"] = "B0SOMETHIN1"
    save(root, "products", d)


def d_unknown_source(root: Path) -> None:
    d = load(root, "questions")
    d["questions"][0]["source_ids"] = ["BD-99"]
    save(root, "questions", d)


def d_carried_without_note(root: Path) -> None:
    d = load(root, "sources")
    for s in d["sources"]:
        if s["status"] == "carried":
            s.pop("carried_note", None)
            break
    save(root, "sources", d)


def d_one_option(root: Path) -> None:
    d = load(root, "suggestions")
    d["rows"][0]["options"] = d["rows"][0]["options"][:1]
    save(root, "suggestions", d)


def d_empty_gap(root: Path) -> None:
    d = load(root, "requirements")
    d["rows"][0]["gap"] = ""
    save(root, "requirements", d)


def d_bad_severity(root: Path) -> None:
    d = load(root, "flags")
    d["rows"][0]["severity"] = "critical"
    save(root, "flags", d)


def d_bad_verdict(root: Path) -> None:
    d = load(root, "requirements")
    d["rows"][0]["verdict"] = "fine"
    save(root, "requirements", d)


def d_drifted_count(root: Path) -> None:
    p = root / "data" / "measured.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    key = next(iter(d["substitutions"]))
    d["substitutions"][key] = str(d["substitutions"][key]) + "7"
    p.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")


def d_no_disclosure(root: Path) -> None:
    page = root / "board" / "topics.html"
    text = page.read_text(encoding="utf-8")
    page.write_text(
        text.replace("As an Amazon Associate I earn from qualifying purchases.",
                     "We may earn a commission."),
        encoding="utf-8")


def d_price(root: Path) -> None:
    edit_html(root, "topics.html",
              "<p class=\"eyebrow\">Topics</p>",
              "<p class=\"eyebrow\">Topics</p><p>Buy it now for $129.99 while the deal lasts.</p>")


def d_unsponsored(root: Path) -> None:
    edit_html(root, "products.html",
              'rel="sponsored nofollow noopener"', 'rel="nofollow noopener"')


def d_duplicate_title(root: Path) -> None:
    src = (root / "board" / "index.html").read_text(encoding="utf-8")
    theirs = re.search(r"<title[^>]*>(.*?)</title>", src, re.S).group(1)
    page = root / "board" / "topics.html"
    text = page.read_text(encoding="utf-8")
    mine = re.search(r"<title[^>]*>(.*?)</title>", text, re.S).group(0)
    page.write_text(text.replace(mine, f"<title>{theirs}</title>"), encoding="utf-8")


def d_dead_fragment(root: Path) -> None:
    edit_html(root, "index.html", "suggestions.html#BS-01", "suggestions.html#BS-99")


def d_empty_method(root: Path) -> None:
    d = load(root, "verification")
    d["rows"][0]["method"] = ""
    save(root, "verification", d)


def d_missing_quote(root: Path) -> None:
    d = load(root, "sources")
    d["sources"][0]["quote"] = ""
    save(root, "sources", d)


# id, injector, a fragment of the message the gate must produce
CASES: list[tuple[str, object, str]] = [
    ("a suggestion is pre-chosen", d_chosen, "carries a chosen option"),
    ("an open question carries an answer", d_open_answer, "an answer is filled in"),
    ("intent borrows an observation value", d_merge_fields, "must never merge"),
    ("an empty intent with no reason", d_blank_without_reason, "no intent_blank_reason"),
    ("a partially filled intent block", d_partial_intent, "partially filled"),
    ("a row cites a source that does not exist", d_unknown_source, "is not in board/data/sources.json"),
    ("a carried source with no carried_note", d_carried_without_note, "carried but carries no carried_note"),
    ("a suggestion with only one option", d_one_option, "a choice needs at least two"),
    ("a requirement row with an empty gap", d_empty_gap, "is empty"),
    ("a flag with an unknown severity", d_bad_severity, "has severity"),
    ("a requirement with an off-vocabulary verdict", d_bad_verdict, "outside the published vocabulary"),
    ("a printed count the tree has outgrown", d_drifted_count, "derived count drift"),
    ("a page with the disclosure removed", d_no_disclosure, "missing the required disclosure"),
    ("a page printing a product price", d_price, "in a buying context"),
    ("a product link with no rel=sponsored", d_unsponsored, 'is not marked rel="sponsored"'),
    ("two pages sharing one title", d_duplicate_title, "duplicate title"),
    ("a fragment that addresses nothing", d_dead_fragment, "fragment #BS-99 addresses nothing"),
    ("a verification row with no method", d_empty_method, "is empty"),
    ("a source that states nothing", d_missing_quote, "states nothing"),
]


def main() -> int:
    # 0. the unmutated board must be clean
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        snapshot(root)
        code, out = run_gate(root)
        if code != 0:
            print("UNMUTATED BOARD FAILED — the negative tests would be meaningless:")
            print(out)
            return 1
    print(f"unmutated board: clean")

    failures = []
    for label, injector, expect in CASES:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot(root)
            try:
                injector(root)  # type: ignore[operator]
            except AssertionError as exc:
                failures.append(f"{label}: fixture broken — {exc}")
                print(f"  BROKEN  {label}")
                continue
            code, out = run_gate(root)
            if code == 0:
                failures.append(f"{label}: injected but the gate PASSED")
                print(f"  MISS    {label}")
            elif expect not in out:
                failures.append(f"{label}: gate failed, but not with {expect!r}")
                print(f"  OTHER   {label} -> {out.strip().splitlines()[-1][:110]}")
            else:
                print(f"  fires   {label}")

    print()
    if failures:
        print(f"{len(failures)} of {len(CASES)} injected defects were NOT caught:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"all {len(CASES)} injected defects fired; unmutated board clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
