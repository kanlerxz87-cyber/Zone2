#!/usr/bin/env python3
"""Negative tests for tools/validate_intake.py.

A gate that has only ever passed is a claim, not a control. This file injects fifteen
defects into a throwaway copy of the namespace — one at a time — and asserts that each one
makes the validator fail. It then asserts the unmutated copy is clean, because a gate that
fires on everything is as useless as one that fires on nothing.

Two of these are worth naming because they are the whole point of the namespace:

  case 1  intent merged with observation — an intent field quietly filled with the observed
          ASIN. This is the defect the brief warns against and the record exists to make
          impossible. If this case ever stops firing, the namespace has failed at its one job.

  case 3  an open question acquiring an answer. Every answer on the register is empty
          because the honest answer is not knowable here; a filled one is a guess.

Run: python3 tools/test_intake.py
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "tools" / "validate_intake.py"

CASES: list[tuple[str, str]] = []


def case(cid: str, description: str):
    def deco(fn):
        CASES.append((cid, description))
        fn.cid = cid
        return fn
    return deco


def load(root: Path, name: str) -> dict:
    return json.loads((root / "intake" / "data" / name).read_text(encoding="utf-8"))


def save(root: Path, name: str, doc: dict) -> None:
    (root / "intake" / "data" / name).write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------- the 15 defects

@case("1", "an intent field is filled with the OBSERVED asin (the merge the record forbids)")
def d1(root: Path) -> None:
    d = load(root, "submissions.json")
    e = d["entries"][0]
    e["intended_asin"] = e["observed_redirect_asin"]
    save(root, "submissions.json", d)


@case("2", "an intent field is filled with no confirmation date or source")
def d2(root: Path) -> None:
    d = load(root, "submissions.json")
    d["entries"][1]["intended_listing_url"] = "https://www.amazon.com/dp/B09B7SB46R"
    save(root, "submissions.json", d)


@case("3", "an open question carries an answer")
def d3(root: Path) -> None:
    d = load(root, "questions.json")
    d["rows"][0]["answer"] = "probably B0CDY277D3"
    save(root, "questions.json", d)


@case("4", "a proposal's recorded choice is not one of its own options")
def d4(root: Path) -> None:
    d = load(root, "proposals.json")
    d["rows"][0]["choice"] = "IP-01-z"
    save(root, "proposals.json", d)


@case("5", "a row cites a source id that does not exist")
def d5(root: Path) -> None:
    d = load(root, "flags.json")
    d["rows"][0]["source_ids"].append("IN-99")
    save(root, "flags.json", d)


@case("6", "a carried source does not name the register it came from")
def d6(root: Path) -> None:
    d = load(root, "sources.json")
    for s in d["sources"]:
        if s.get("status") == "CARRIED":
            s.pop("carried_from", None)
            break
    save(root, "sources.json", d)


@case("7", "an observed ASIN is not 10 characters")
def d7(root: Path) -> None:
    d = load(root, "submissions.json")
    d["entries"][2]["observed_redirect_asin"] = "B08DKYBT"
    save(root, "submissions.json", d)


@case("8", "the disclosure is removed from a page")
def d8(root: Path) -> None:
    p = root / "intake" / "index.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace("As an Amazon Associate I earn from qualifying purchases.", "", 2)
    p.write_text(t, encoding="utf-8")


@case("9", "a product link loses rel=sponsored")
def d9(root: Path) -> None:
    p = root / "intake" / "submissions.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace(' rel="sponsored nofollow"', "", 1)
    p.write_text(t, encoding="utf-8")


@case("10", "a local link points at a file that does not exist")
def d10(root: Path) -> None:
    p = root / "intake" / "index.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace('href="flags.html"', 'href="no-such-page.html"', 1)
    p.write_text(t, encoding="utf-8")


@case("11", "a same-page anchor addresses nothing")
def d11(root: Path) -> None:
    p = root / "intake" / "flags.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace('href="#IF-02"', 'href="#IF-99"', 1)
    p.write_text(t, encoding="utf-8")


@case("12", "a money figure appears in a buying context")
def d12(root: Path) -> None:
    p = root / "intake" / "index.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace("<h2>What was measured", '<p>The current price is $149.99 today.</p>\n<h2>What was measured', 1)
    p.write_text(t, encoding="utf-8")


@case("13", "a row references a flag that is not on the register")
def d13(root: Path) -> None:
    d = load(root, "submissions.json")
    d["entries"][3]["flag_ids"].append("IF-77")
    save(root, "submissions.json", d)


@case("14", "the two field groups overlap, so intent and observation could be merged")
def d14(root: Path) -> None:
    d = load(root, "submissions.json")
    d["observed_fields"].append("intended_asin")
    save(root, "submissions.json", d)


@case("15", "a printed count drifts from the data it is derived from")
def d15(root: Path) -> None:
    p = root / "intake" / "flags.html"
    t = p.read_text(encoding="utf-8")
    t = t.replace("8 irregularities", "12 irregularities")  # every occurrence, incl. the body
    p.write_text(t, encoding="utf-8")


# ------------------------------------------------------------------- harness

def make_tree(tmp: Path) -> Path:
    """A throwaway copy of just what the gate reads.

    The pages' footers link out to sibling namespaces (`../pages/flags.html` and friends).
    Those really exist in the repository, and the gate is right to check them, so rather
    than weaken the gate for the test we stand up placeholder files for every `../` link
    the namespace makes. If the footer grows a link to something that does not exist in the
    real repository, the gate still catches it there — and the baseline here stays honest.
    """
    root = tmp / "repo"
    (root / "tools").mkdir(parents=True)
    shutil.copytree(REPO / "intake", root / "intake")
    for f in ("head_meta.py", "build_intake.py", "validate_intake.py"):
        shutil.copy(REPO / "tools" / f, root / "tools" / f)
    for page in (root / "intake").glob("*.html"):
        for m in re.finditer(r'href="(\.\./[^"#]+)', page.read_text(encoding="utf-8")):
            target = (page.parent / m.group(1)).resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("<!DOCTYPE html><title>placeholder</title>\n", encoding="utf-8")
    return root


def run_validator(root: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, INTAKE_ROOT=str(root))
    return subprocess.run([sys.executable, str(root / "tools" / "validate_intake.py")],
                          capture_output=True, text=True, env=env, cwd=str(root))


def main() -> int:
    failures: list[str] = []

    # The unmutated tree must be clean: a gate that fires on everything is as useless as
    # one that fires on nothing.
    with tempfile.TemporaryDirectory() as td:
        root = make_tree(Path(td))
        r = run_validator(root)
        if r.returncode != 0:
            failures.append("baseline: the unmutated namespace FAILED the gate\n" + r.stdout)

    for cid, description in CASES:
        fn = globals()[f"d{cid}"]
        with tempfile.TemporaryDirectory() as td:
            root = make_tree(Path(td))
            fn(root)
            r = run_validator(root)
            if r.returncode == 0:
                failures.append(f"case {cid}: defect did NOT fire — {description}")
            elif "FAILS" not in (r.stdout + r.stderr):
                failures.append(f"case {cid}: exited non-zero but not through the gate — {description}")

    if failures:
        print(f"test_intake FAILED ({len(failures)}):")
        for f in failures:
            print("  -", f)
        return 1
    print(f"test_intake OK — baseline clean and all {len(CASES)} injected defects fired")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
