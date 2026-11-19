#!/usr/bin/env python3
"""Negative tests for the Decision Room gate (T69, session `arena/698addcd-zone2`).

Every mutation is in-memory: the register is deep-copied, broken in one specific way, and the
gate's checks are run against the copy. Nothing on disk is touched, so a failing test can never
leave the repository in a broken state.

These exist because a gate that cannot fail is decoration. Each test below corresponds to one
rule in tools/verify_decision_room.py, and asserts that the rule actually fires.
"""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_decision_room as gen  # noqa: E402
import verify_decision_room as gate  # noqa: E402

DATA = json.loads((ROOT / "content" / "decision-room.json").read_text(encoding="utf-8"))


def register_problems(data: dict) -> list[str]:
    """Run only the register-level rules (D5/D6/D7/D9) so a mutation is isolated from page output."""
    errors: list[str] = []
    known_sources = set(data["sources"])
    known_questions = {q["id"] for q in data["owner_questions"]}
    referenced: set[str] = set()
    for d in data["decisions"]:
        rid = d.get("id", "<no id>")
        for field in ("id", "cluster", "title", "question", "status", "evidence",
                      "options", "recommendation", "recommendation_reason", "unblocks_with"):
            if not d.get(field):
                errors.append(f"D5 {rid}: missing '{field}'")
        if d.get("status") not in {"open", "fixed", "blocked"}:
            errors.append(f"D5 {rid}: unknown status")
        options = d.get("options") or []
        if len(options) < 2:
            errors.append(f"D5 {rid}: needs two options")
        if d.get("recommendation") not in [o.get("id") for o in options]:
            errors.append(f"D5 {rid}: recommendation is not one of its options")
        for o in options:
            for field in ("id", "label", "costs", "gives_up"):
                if not o.get(field):
                    errors.append(f"D5 {rid}: option missing '{field}'")
        for item in d.get("evidence") or []:
            if item.get("src") not in known_sources:
                errors.append(f"D6 {rid}: unknown source id")
        if d.get("status") == "fixed" and not d.get("fixed_note"):
            errors.append(f"D9 {rid}: fixed without a note")
        if d.get("status") != "fixed" and d.get("fixed_note"):
            errors.append(f"D9 {rid}: note on a row that is not fixed")
        oq = d.get("owner_question")
        if oq:
            if oq not in known_questions:
                errors.append(f"D7 {rid}: unknown owner_question")
            referenced.add(oq)
    for q in data["owner_questions"]:
        if q["id"] not in referenced:
            errors.append(f"D7 {q['id']}: nothing references it")
    return errors


class CleanRegister(unittest.TestCase):
    def test_committed_register_is_clean(self):
        self.assertEqual(register_problems(DATA), [])

    def test_rendered_pages_are_current(self):
        self.assertEqual(gen.build_room(DATA), (ROOT / "decision-room.html").read_text(encoding="utf-8"))
        self.assertEqual(gen.build_prompt(DATA), (ROOT / "decision-prompt.html").read_text(encoding="utf-8"))


class Mutations(unittest.TestCase):
    def mutated(self, change) -> list[str]:
        data = copy.deepcopy(DATA)
        change(data)
        return register_problems(data)

    def test_dangling_source_id_fails(self):
        def change(d):
            d["decisions"][0]["evidence"][0]["src"] = "T69-NOT-A-SOURCE"
        self.assertTrue(any("unknown source id" in p for p in self.mutated(change)))

    def test_recommendation_must_be_an_option(self):
        def change(d):
            d["decisions"][0]["recommendation"] = "Z"
        self.assertTrue(any("not one of its options" in p for p in self.mutated(change)))

    def test_option_must_state_its_cost(self):
        def change(d):
            d["decisions"][0]["options"][0]["costs"] = ""
        self.assertTrue(any("missing 'costs'" in p for p in self.mutated(change)))

    def test_option_must_state_what_it_gives_up(self):
        def change(d):
            d["decisions"][0]["options"][0]["gives_up"] = ""
        self.assertTrue(any("missing 'gives_up'" in p for p in self.mutated(change)))

    def test_fixed_row_needs_a_written_note(self):
        def change(d):
            row = next(r for r in d["decisions"] if r["status"] == "fixed")
            row.pop("fixed_note", None)
        self.assertTrue(any("fixed without a note" in p for p in self.mutated(change)))

    def test_open_row_cannot_claim_a_fix(self):
        def change(d):
            row = next(r for r in d["decisions"] if r["status"] == "open")
            row["fixed_note"] = "pretend this was fixed"
        self.assertTrue(any("note on a row that is not fixed" in p for p in self.mutated(change)))

    def test_decision_cannot_point_at_a_missing_question(self):
        def change(d):
            d["decisions"][0]["owner_question"] = "DRQ-999"
        self.assertTrue(any("unknown owner_question" in p for p in self.mutated(change)))

    def test_orphan_owner_question_fails(self):
        def change(d):
            d["owner_questions"].append({"id": "DRQ-ORPHAN", "asked": "nobody asks this",
                                         "answer_shape": "n/a", "blocks": [], "how_to_close": "n/a"})
        self.assertTrue(any("nothing references it" in p for p in self.mutated(change)))

    def test_unknown_status_fails(self):
        def change(d):
            d["decisions"][0]["status"] = "maybe"
        self.assertTrue(any("unknown status" in p for p in self.mutated(change)))

    def test_single_option_fails(self):
        def change(d):
            d["decisions"][0]["options"] = d["decisions"][0]["options"][:1]
        self.assertTrue(any("needs two options" in p for p in self.mutated(change)))


class PageGuards(unittest.TestCase):
    """The price and performance guards, exercised against a mutated render."""

    def test_price_guard_fires(self):
        text = gen.build_room(DATA).replace(
            "<h1>", "<h1>$1,299 and a 3.1% conversion rate. ", 1)
        self.assertTrue(gate.MONEY.search(text))
        self.assertTrue(gate.METRIC.search(text))

    def test_clean_page_trips_neither_guard(self):
        text = gen.build_room(DATA)
        self.assertIsNone(gate.MONEY.search(text))
        self.assertIsNone(gate.METRIC.search(text))

    def test_commission_percentages_are_not_treated_as_prices(self):
        # 4.50% appears throughout this repository's source registers as a policy fact.
        self.assertIsNone(gate.MONEY.search("the 4.50% rate in the official table"))
        self.assertIsNone(gate.METRIC.search("the documented commission rate is 4.50%"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
