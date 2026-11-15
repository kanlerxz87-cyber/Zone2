#!/usr/bin/env python3
"""Negative tests for tools/validate_audit.py.

Every check in the audit gate is injected with the defect it is supposed to catch, one at a
time, against a temporary copy of audit/data/. The test fails if a check does not fire. This is
the same discipline the repository's older gates were put through before they were trusted —
a gate that has only ever passed is a claim, not a control.

The working tree is never modified: each case writes to a temp directory and points the
validator at it via AUDIT_DATA_DIR.

Usage:
    python3 tools/test_audit.py
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "audit" / "data"


def run_validator(workdir: Path) -> tuple[int, str]:
    """workdir is the temp *audit* directory: it holds data/ and the generated pages."""
    env = dict(os.environ)
    env["AUDIT_DATA_DIR"] = str(workdir)
    # validate_audit loads from audit/data via load(); the env override is honoured there.
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "validate_audit.py")],
        capture_output=True, text=True, env=env, cwd=str(REPO),
    )
    return r.returncode, r.stdout + r.stderr


def mutate(name: str, fn, sabotage: str = "") -> list[str]:
    """Copy the data dir, apply fn to the named file's parsed JSON, run the validator."""
    root = Path(tempfile.mkdtemp(prefix="audit-test-"))
    # Mirror the real layout: <root>/audit/data/*.json and <root>/audit/*.html
    tmp = root / "audit"
    (tmp / "data").mkdir(parents=True)
    for f in DATA.glob("*.json"):
        shutil.copy(f, tmp / "data" / f.name)
    target = tmp / "data" / name
    d = json.loads(target.read_text(encoding="utf-8"))
    fn(d)
    target.write_text(json.dumps(d, indent=2), encoding="utf-8")
    # the pages must be regenerated from the mutated data for the page-level checks to see it
    env = dict(os.environ)
    env["AUDIT_DATA_DIR"] = str(tmp)
    subprocess.run([sys.executable, str(REPO / "tools" / "build_audit.py")],
                   capture_output=True, text=True, env=env, cwd=str(REPO))
    if sabotage == "badge":
        # prove the label is load-bearing by removing it from the rendered page
        m = tmp / "method.html"
        m.write_text(m.read_text(encoding="utf-8").replace('class="badge warn">carried', 'class="badge ok">fetched'), encoding="utf-8")
    if sabotage == "count":
        # prove the count check is load-bearing by typing a wrong number into the page
        i = tmp / "index.html"
        t = i.read_text(encoding="utf-8")
        import re as _re
        t = _re.sub(r'(<div class="c"><b>)(\d+)(</b><span>findings)', r'\g<1>99\g<3>', t, count=1)
        i.write_text(t, encoding="utf-8")
    code, out = run_validator(tmp)
    shutil.rmtree(root, ignore_errors=True)
    return [line.strip() for line in out.splitlines() if line.strip().startswith(("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13"))]


CASES = [
    (
        "A1 unverified row with no reason",
        "findings.json",
        lambda d: d["findings"][0].update({"status": "UNVERIFIED", "unverified_because": ""}),
        "A1",
    ),
    (
        "A2 verified row quoting a rule with no source and no measurement",
        "findings.json",
        lambda d: d["findings"][0].update({"source_ids": [], "evidence": "it is obviously true"}),
        "A2",
    ),
    (
        "A3 citation of an unregistered source id",
        "findings.json",
        lambda d: d["findings"][0].update({"source_ids": ["SA-99"]}),
        "A3",
    ),
    (
        "A4 a source with no URL",
        "sources.json",
        lambda d: d["sources"][0].update({"url": ""}),
        "A4",
    ),
    (
        "A5 the method page renders a carried source without its badge",
        "sources.json",
        lambda d: d["sources"][0].update({"rechecked": "carried", "fetched": "carried from ledger/sources.json"}),
        "A5",
        "badge",
    ),
    (
        "A6 a recommendation with one option",
        "suggestions.json",
        lambda d: d["recommendations"][0].update({"options": d["recommendations"][0]["options"][:1]}),
        "A6",
    ),
    (
        "A6 a recommendation whose 'cost' does not declare itself an estimate",
        "suggestions.json",
        lambda d: d["recommendations"][0].update({"cost": "about an hour"}),
        "A6",
    ),
    (
        "A7 a blocked recommendation that names no gap",
        "suggestions.json",
        lambda d: d["recommendations"][0].update({"status": "blocked_on_information", "depends_on": []}),
        "A7",
    ),
    (
        "A8 a gap with no way to close it",
        "gaps.json",
        lambda d: d["gaps"][0].update({"how_to_close": ""}),
        "A8",
    ),
    (
        "A9 a cost row pointing at a decision that does not exist",
        "decision-cost.json",
        lambda d: d["decisions"][0].update({"recommendation": "R-99"}),
        "A9",
    ),
    (
        "A10 a count typed into the page that does not match the data",
        "findings.json",
        lambda d: d["findings"].append(dict(d["findings"][0], id="A-99")),
        "A10",
        "count",
    ),
]


def main() -> int:
    failures = []
    for case in CASES:
        label, fname, fn, expect = case[:4]
        sabotage = case[4] if len(case) > 4 else ""
        errs = mutate(fname, fn, sabotage)
        hit = any(e.startswith(expect) for e in errs)
        print(f"  {'FIRED ' if hit else 'MISSED'}  {label}" + (f"  -> {errs[0][:90]}" if errs and hit else ""))
        if not hit:
            failures.append(label)

    print()
    if failures:
        print(f"{len(failures)} check(s) did not fire on the defect they exist to catch:")
        for f in failures:
            print("  ", f)
        return 1
    print(f"{len(CASES)}/{len(CASES)} negative tests fired as intended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
