#!/usr/bin/env python3
"""Negative tests for tools/build_readiness.py.

The readiness board is the one page whose whole value is that it cannot drift from the tree it
describes. A gate that has only ever passed is a claim, not a control — so every rule the gate
enforces is injected with the defect it is supposed to catch, one at a time, and the test fails if
the rule does not fire.

The working tree is never modified: the register is read once, mutated in memory, and handed back
to the validator functions.

Usage:
    python3 tools/test_readiness.py
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load_module():
    spec = importlib.util.spec_from_file_location(
        "build_readiness", REPO / "tools" / "build_readiness.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


BR = load_module()
REGISTER = json.loads((REPO / "ledger" / "readiness.json").read_text(encoding="utf-8"))


def row(reg: dict, rid: str) -> dict:
    for r in reg["rows"]:
        if r["id"] == rid:
            return r
    raise KeyError(rid)


def typed_rr10(reg: dict) -> None:
    """Put a hand-typed count back into RR-10, the way the register read before the token fix."""
    row(reg, "RR-10")["site_state"] = (
        "126 of 126 published pages carry the exact sentence 'As an Amazon Associate I earn "
        "from qualifying purchases.', enforced by tools/validate_data.py and tools/audit_site.py."
    )


CASES = [
    (
        "R1 a hand-typed count that disagrees with the tree",
        typed_rr10,
        lambda reg: BR.check_claims(reg),
        "RR-10",
    ),
    (
        "R2 a token naming a measure the generator cannot compute",
        lambda reg: row(reg, "RR-10").__setitem__(
            "site_state", "{not_a_real_measure} published pages carry the disclosure."
        ),
        lambda reg: BR.validate(reg),
        "not_a_real_measure",
    ),
    (
        "R3 a token on a row that declares no measure",
        lambda reg: row(reg, "RR-10").pop("measure"),
        lambda reg: BR.validate(reg),
        "declares no 'measure'",
    ),
    (
        "R4 a token naming a different measure than the row's own",
        lambda reg: row(reg, "RR-10").__setitem__(
            "site_state", "{published_namespaces} published pages carry the disclosure."
        ),
        lambda reg: BR.validate(reg),
        "the row would state a number it is not checked against",
    ),
    (
        "R5 a measured row with no site_state at all",
        lambda reg: row(reg, "RR-10").__setitem__("site_state", ""),
        lambda reg: BR.validate(reg),
        "states no site_state",
    ),
    (
        "R6 a state outside the closed vocabulary",
        lambda reg: row(reg, "RR-01").__setitem__("state", "PROBABLY_FINE"),
        lambda reg: BR.validate(reg),
        "closed vocabulary",
    ),
    (
        "R7 a BLOCKED row that names nobody who can clear it",
        lambda reg: row(reg, "RR-05").__setitem__("blocked_by", []),
        lambda reg: BR.validate(reg),
        "no blocked_by",
    ),
    (
        "R8 a GAP row with no owner action",
        lambda reg: row(reg, "RR-02").__setitem__("owner_action", ""),
        lambda reg: BR.validate(reg),
        "with no owner_action",
    ),
    (
        "R9 a row whose source id does not resolve in the source register",
        lambda reg: row(reg, "RR-01").__setitem__("source_ids", ["S99"]),
        lambda reg: BR.validate(reg),
        "does not resolve in ledger/sources.json",
    ),
    (
        "R10 a quote that is not in the captured Amazon text",
        lambda reg: row(reg, "RR-11").__setitem__("quote", "a sentence Amazon never wrote"),
        lambda reg: BR.validate(reg),
        "not present in the S23 text",
    ),
    (
        "R11 an unresolved token reaching the published page",
        lambda reg: row(reg, "RR-10").__setitem__(
            "site_state", "{not_a_real_measure} published pages carry the disclosure."
        ),
        lambda reg: BR.rendered_claims(
            reg, "<html><body>{not_a_real_measure}</body></html>"
        ),
        "unresolved measure token",
    ),
    (
        "R12 a derived count that the rendered page does not state",
        lambda reg: row(reg, "RR-10").__setitem__(
            "site_state", "{pages_with_disclosure} published pages carry the disclosure."
        ),
        lambda reg: BR.rendered_claims(reg, "<html><body>the sentence was dropped</body></html>"),
        "does not appear on the published page",
    ),
    (
        "R13 a multi-measure row whose site_state names a measure outside its declared list",
        lambda reg: row(reg, "RR-05").__setitem__(
            "site_state",
            "{pages_with_tagged_link} tagged. {pages_with_disclosure} disclosure. "
            "{pages_linking_dp} dp links."
        ),
        lambda reg: BR.validate(reg),
        "the row would state a number it is not checked against",
    ),
]


def main() -> int:
    failures = 0
    for name, mutate, check, expect in CASES:
        reg = copy.deepcopy(REGISTER)
        mutate(reg)
        problems = check(reg)
        joined = "\n".join(problems)
        if any(expect in p for p in problems):
            print(f"  FIRED   {name}")
            for p in problems:
                if expect in p:
                    print(f"          {p}")
                    break
        else:
            print(f"  MISSED  {name}  (expected a problem containing {expect!r})")
            failures += 1

    # The control: the unmutated register must be clean, or the tests above prove nothing.
    reg = copy.deepcopy(REGISTER)
    clean = BR.validate(reg) + BR.check_claims(reg)
    if clean:
        print("  MISSED  control: the unmutated register reported problems")
        for p in clean:
            print(f"          {p}")
        failures += 1
    else:
        print("  FIRED   control: the unmutated register is clean")

    print()
    if failures:
        print(f"{failures} of {len(CASES) + 1} negative tests did not fire as intended")
        return 1
    print(f"{len(CASES) + 1}/{len(CASES) + 1} negative tests fired as intended")
    return 0


if __name__ == "__main__":
    sys.exit(main())
