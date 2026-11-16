#!/usr/bin/env python3
"""Negative tests for the review-board gate.

A gate that has only ever passed is a claim, not a control. This file injects thirteen
defects into a copy of the register, runs the real validator against the copy, and requires
every one of them to fail the build. It also runs the unmutated register and requires that
to pass, so a gate that fails everything cannot masquerade as a working one.

Run: python3 tools/test_review_board.py
"""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTER = REPO / "docs" / "review-board.json"
VALIDATOR = REPO / "tools" / "validate_review_board.py"
BASE = json.loads(REGISTER.read_text(encoding="utf-8"))


def run(data: dict) -> tuple[int, str]:
    """Run the real validator against a mutated register; return (exit code, output)."""
    tmp = Path(tempfile.mkdtemp(prefix="z2rb-test-"))
    # The validator imports build_review_board, which reads the register at import time. Point a
    # temporary copy of tools/ + decisions/data/ at the mutated file, and run from there.
    (tmp / "tools").mkdir()
    for f in ("build_review_board.py", "head_meta.py", "validate_review_board.py"):
        (tmp / "tools" / f).write_text((REPO / "tools" / f).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp / "docs").mkdir(parents=True)
    (tmp / "docs" / "review-board.json").write_text(json.dumps(data), encoding="utf-8")
    (tmp / "ledger").mkdir()
    (tmp / "ledger" / "sources.json").write_text(
        (REPO / "ledger" / "sources.json").read_text(encoding="utf-8"), encoding="utf-8"
    )
    for page in ("review.html", "review-questions.html", "review-trace.html", "review-ideas.html"):
        (tmp / page).write_text((REPO / page).read_text(encoding="utf-8"), encoding="utf-8")
    # Pages must resolve their links; copy the minimum tree they point at.
    for d in ("pages", "marketing", "decisions", "assets"):
        dst = tmp / d
        if dst.exists():
            continue
        dst.mkdir()
        for src in (REPO / d).glob("*.html"):
            (dst / src.name).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    (tmp / "decisions" / "index.html").write_text("<a href='x'>x</a>", encoding="utf-8")
    (tmp / "flagged.html").write_text("<a href='x'>x</a>", encoding="utf-8")
    (tmp / "index.html").write_text("<a href='x'>x</a>", encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, str(tmp / "tools" / "validate_review_board.py")],
        capture_output=True, text=True, cwd=tmp,
    )
    return proc.returncode, proc.stdout + proc.stderr


MUTATIONS = []


def mutation(name: str, expect: str):
    def deco(fn):
        MUTATIONS.append((name, expect, fn))
        return fn
    return deco


@mutation("an open question carries an answer", "carries an answer")
def _(d):
    d["questions"][0]["answer"] = "Yes, it is approved."
    return d


@mutation("a cited source is undefined", "cited but not defined")
def _(d):
    d["proposals"][0]["evidence"] = ["S99"]
    return d


@mutation("a source sits on a non-official host", "not an official allowlisted host")
def _(d):
    d["sources"][0]["url"] = "https://example.com/policy"
    return d


@mutation("a source carries no quote", "quote too short")
def _(d):
    d["sources"][1]["quote"] = "short"
    return d


@mutation("a proposal offers one option", "a single option is not a decision")
def _(d):
    d["proposals"][0]["options"] = d["proposals"][0]["options"][:1]
    return d


@mutation("an option states no risk", "empty 'risk'")
def _(d):
    d["proposals"][0]["options"][0]["risk"] = ""
    return d


@mutation("a recommendation names an option that is not offered", "unoffered option")
def _(d):
    d["proposals"][0]["recommendation"] = "Option Q is the only one."
    return d


@mutation("an undecided proposal reads as implemented", "reads as implemented")
def _(d):
    d["proposals"][1]["problem"] = "This was shipped and is now live."
    return d


@mutation("a selected row records no decision note", "no decision note")
def _(d):
    d["proposals"][2]["decision"] = "SELECTED"
    d["proposals"][2]["decision_note"] = ""
    return d


@mutation("a selected row's note names none of its own options", "names none of its own options")
def _(d):
    d["proposals"][2]["decision"] = "SELECTED"
    d["proposals"][2]["decision_note"] = "Owner said yes on 2026-11-16."
    return d


@mutation("a requirement row cites a source, then loses it without saying why", "no statement that no official source")
def _(d):
    row = d["requirements"][0]
    row["source_ids"] = []
    row["verified_against"] = "checked by hand on 2026-11-16"
    return d


@mutation("a proposal waits on a question that does not exist", "waits on unknown question")
def _(d):
    d["proposals"][0]["waiting_on"] = ["PQ-99"]
    return d


@mutation("an idea has no source", "no source - even an idea")
def _(d):
    d["ideas"][0]["source_ids"] = []
    return d


@mutation("a score is outside the declared 1-5 range", "is not an integer 1-5")
def _(d):
    d["proposals"][0]["quality_impact"] = 9
    return d


@mutation("a findings row points at a proposal that does not exist", "is not a proposal on this board")
def _(d):
    d["design_findings"][0]["proposed_fix"] = "PS-99"
    return d


def main() -> int:
    failures = []

    code, out = run(copy.deepcopy(BASE))
    if code != 0:
        failures.append(f"CONTROL: the unmutated register must pass, it failed:\n{out[-1500:]}")
    else:
        print("control (unmutated register)  PASS as expected")

    for name, expect, fn in MUTATIONS:
        data = fn(copy.deepcopy(BASE))
        code, out = run(data)
        if code == 0:
            failures.append(f"NOT CAUGHT: {name} - the gate passed a register it should have refused")
        elif expect not in out:
            failures.append(f"WRONG REASON: {name} - expected {expect!r} in the output, got:\n{out[-800:]}")
        else:
            print(f"injected: {name:62s} caught")

    print()
    if failures:
        print("\n".join(f"FAIL {f}" for f in failures))
        print(f"{len(failures)} of {len(MUTATIONS) + 1} checks failed")
        return 1
    print(f"{len(MUTATIONS)} injected defects, each fired · 1 control passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
