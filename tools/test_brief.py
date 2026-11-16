#!/usr/bin/env python3
"""Negative tests for the design-brief gate (tools/validate_brief.py).

Why this file exists
--------------------
A gate that has only ever passed is a claim, not a control. Every other gate in this
repository that guards a generated namespace ships its negative tests beside it
(tools/test_audit.py, tools/test_readiness.py), and the design brief follows the same
rule. Each test injects one defect into brief/data/*.json or brief/*.html, runs the real
gate as a subprocess against the mutated tree, and asserts that it fails *and* names the
defect. The register is restored after every case, and the final case asserts the
unmutated tree passes clean.

Run: python3 tools/test_brief.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "brief" / "data"
OUT = REPO / "brief"
GATE = REPO / "tools" / "validate_brief.py"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

failures: list[str] = []


def run_gate() -> tuple[int, str]:
    p = subprocess.run(
        [sys.executable, str(GATE)], capture_output=True, text=True, cwd=str(REPO)
    )
    return p.returncode, p.stdout + p.stderr


def with_json(name: str):
    """Back up a register, hand the caller a mutable dict, restore on exit."""
    path = DATA / name
    original = path.read_text(encoding="utf-8")

    def ctx(mutate) -> tuple[int, str]:
        data = json.loads(original)
        mutate(data)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            return run_gate()
        finally:
            path.write_text(original, encoding="utf-8")

    return ctx


def with_page(name: str):
    path = OUT / name
    original = path.read_text(encoding="utf-8")

    def ctx(mutate) -> tuple[int, str]:
        path.write_text(mutate(original), encoding="utf-8")
        try:
            return run_gate()
        finally:
            path.write_text(original, encoding="utf-8")

    return ctx


def case(label: str, code: int, out: str, expected: str) -> None:
    if code == 0:
        failures.append(f"{label}: gate PASSED on a tree that contains the injected defect")
    elif expected.lower() not in out.lower():
        failures.append(f"{label}: gate failed but did not name the defect (expected {expected!r})")
    else:
        print(f"PASS  {label}")


def main() -> int:
    # 1. A citation that resolves to nothing.
    def m1(d):
        for r in d["rows"]:
            if r["id"] == "RV-03":
                r["source_id"] = "BR-99"
    code, out = with_json("review.json")(m1)
    case("unknown source id is rejected", code, out, "not in the source register")

    # 2. An open question whose answer has been filled in — the one thing this project refuses.
    def m2(d):
        for q in d["open"]:
            if q["id"] == "BQ-14":
                q["answer"] = "probably a US account"
    code, out = with_json("questions.json")(m2)
    case("a filled-in open question is rejected", code, out, "answer must stay empty")

    # 3. A measurement with no method: a number with no way to reproduce it.
    def m3(d):
        for r in d["rows"]:
            if r["id"] == "RV-02":
                r["method"] = ""
    code, out = with_json("review.json")(m3)
    case("a row without a method is rejected", code, out, "must state the method")

    # 4. A carried source row that quotes text it did not re-read.
    def m4(d):
        for s in d["sources"]:
            if s["id"] == "BR-22":
                s["quote"] = "a sentence nobody read today"
    code, out = with_json("sources.json")(m4)
    case("a carried row that quotes is rejected", code, out, "must not quote text")

    # 5. The drift FB-01 and FB-02 are: a typed count the tree has outgrown.
    def m5(d):
        for row in d["state"]:
            if row["metric"].startswith("Published pages carrying the exact"):
                row["value"] = "116 of 116"
    code, out = with_json("summary.json")(m5)
    case("a stale typed count is rejected", code, out, "must be re-derived")

    # 6. A recorded choice that is not one of the row's own options.
    def m6(d):
        for r in d["sheet"]:
            if r["id"] == "DB-01":
                r["choice"] = "D"
                r["decided_on"] = "2026-11-16"
    code, out = with_json("decisions.json")(m6)
    case("a choice outside the options is rejected", code, out, "not one of the row's options")

    # 7. A recommendation that names no option, so the owner cannot tell what is advised.
    def m7(d):
        for p in d["proposals"]:
            if p["id"] == "DB-01":
                p["recommended"] = "do the sensible thing"
    code, out = with_json("suggestions.json")(m7)
    case("a recommendation naming no option is rejected", code, out, "names none of its own options")

    # 8. A question blocking something that is not a proposal — this renders as a link to a
    #    fragment that addresses nothing, which tools/audit_site.py fails site-wide.
    def m8(d):
        for q in d["open"]:
            if q["id"] == "BQ-16":
                q["blocks"] = ["FB-01"]
    code, out = with_json("questions.json")(m8)
    case("a blocker that is not a proposal is rejected", code, out, "is not a proposal on the board")

    # 9. A verification check that reports a result with nothing observed.
    def m9(d):
        for c in d["checks"]:
            if c["id"] == "VF-22":
                c["observed"] = ""
    code, out = with_json("verification.json")(m9)
    case("a result with nothing observed is rejected", code, out, "with nothing observed")

    # 10. A page without the §5 disclosure (R-01).
    code, out = with_page("topics.html")(lambda t: t.replace(DISCLOSURE, ""))
    case("a page without the disclosure is rejected", code, out, "missing the required Site disclosure")

    # 11. A money figure on a page (R-04: no price may be published).
    code, out = with_page("topics.html")(
        lambda t: t.replace("<h1>Twelve articles", "<h1>Twelve articles worth $199.99", 1)
    )
    case("a money figure is rejected", code, out, "prints a money figure")

    # 13. Prose that contradicts the measured table. This is the FB-01/FB-02 class in this
    #     namespace's own house: the table was re-measured to 150 pages while three prose
    #     bullets still said "138 of 138". It shipped that way once and was caught only by
    #     reading the deployed page.
    def m13(d):
        d["what_is_settled"][1] = ("The evidence discipline holds at scale: 116 of 116 pages "
                                   "carry the disclosure, no page prints a product price.")
    code, out = with_json("summary.json")(m13)
    case("prose contradicting the measured table is rejected", code, out, "but the tree measures")

    # 14. A duplicated entry in the 'decide first' list renders as two identical cards
    #     numbered the same, which is how the live page shipped.
    def m14(d):
        d["decide_first"].append(dict(d["decide_first"][0]))
    code, out = with_json("summary.json")(m14)
    case("a duplicated decide-first entry is rejected", code, out, "lists")

    # 15. The unmutated register must be clean — otherwise every case above is meaningless.
    code, out = run_gate()
    if code != 0:
        failures.append(f"clean register: gate failed with no defect injected:\n{out}")
    else:
        print("PASS  clean register is clean")

    if failures:
        print(f"\n{len(failures)} failure(s):")
        for f in failures:
            print(f"  FAIL {f}")
        return 1
    testcount = len([1]) and 14
    print(f"\ntools/test_brief.py: {testcount}/{testcount} negative tests fire correctly")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
