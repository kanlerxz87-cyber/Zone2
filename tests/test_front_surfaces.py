#!/usr/bin/env python3
"""Regression tests for current-vs-preserved suggestion and question summaries."""
from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_front
import publication
import verify_front


class DecisionSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.facts, cls.board = build_front.load()
        cls.suggestions = build_front.build_suggestions(cls.facts, cls.board)
        cls.questions = build_front.build_questions(cls.facts, cls.board)

    def test_suggestions_separate_current_proposals_from_preserved_board(self) -> None:
        current = len(publication.PROPOSALS)
        earlier = len(self.board["suggestions"])
        self.assertIn(f'data-current-proposals="{current}"', self.suggestions)
        self.assertIn(f'data-preserved-proposals="{earlier}"', self.suggestions)
        self.assertIn("Current release proposals", self.suggestions)
        self.assertIn("Earlier decision records, preserved", self.suggestions)
        self.assertEqual(verify_front.decision_surface_problems("suggestions.html", self.suggestions, self.board), [])

    def test_questions_separate_current_prerequisites_from_preserved_board(self) -> None:
        current = len(publication.QUESTIONS)
        earlier = len(self.board["questions"])
        self.assertIn(f'data-current-questions="{current}"', self.questions)
        self.assertIn(f'data-preserved-questions="{earlier}"', self.questions)
        self.assertIn("Current release prerequisites", self.questions)
        self.assertIn("Earlier questions, preserved", self.questions)
        self.assertEqual(verify_front.decision_surface_problems("questions.html", self.questions, self.board), [])

    def test_stale_current_suggestion_count_fails_the_gate(self) -> None:
        current = len(publication.PROPOSALS)
        corrupted = self.suggestions.replace(
            f"<b>{current} current proposals</b>",
            f"<b>{current + 1} current proposals</b>",
            1,
        )
        self.assertNotEqual(corrupted, self.suggestions)
        errors = verify_front.decision_surface_problems("suggestions.html", corrupted, self.board)
        self.assertTrue(any("current/preserved summary text" in error for error in errors), errors)

    def test_stale_current_question_count_fails_the_gate(self) -> None:
        current = len(publication.QUESTIONS)
        corrupted = self.questions.replace(
            f"<b>{current} current questions</b>",
            f"<b>{current + 1} current questions</b>",
            1,
        )
        self.assertNotEqual(corrupted, self.questions)
        errors = verify_front.decision_surface_problems("questions.html", corrupted, self.board)
        self.assertTrue(any("current/preserved summary text" in error for error in errors), errors)

    def test_stale_preserved_suggestion_count_fails_the_gate(self) -> None:
        earlier = len(self.board["suggestions"])
        corrupted = self.suggestions.replace(
            f"<b>{earlier} earlier proposals preserved</b>",
            f"<b>{earlier + 1} earlier proposals preserved</b>",
            1,
        )
        errors = verify_front.decision_surface_problems("suggestions.html", corrupted, self.board)
        self.assertTrue(any("current/preserved summary text" in error for error in errors), errors)

    def test_stale_preserved_question_count_fails_the_gate(self) -> None:
        earlier = len(self.board["questions"])
        corrupted = self.questions.replace(
            f"<b>{earlier} earlier questions preserved</b>",
            f"<b>{earlier + 1} earlier questions preserved</b>",
            1,
        )
        errors = verify_front.decision_surface_problems("questions.html", corrupted, self.board)
        self.assertTrue(any("current/preserved summary text" in error for error in errors), errors)

    def test_removed_current_question_row_fails_the_gate(self) -> None:
        corrupted = self.questions.replace('id="Q63-01"', 'id="Q63-XX"', 1)
        errors = verify_front.decision_surface_problems("questions.html", corrupted, self.board)
        self.assertTrue(any("current prerequisite rows differ" in error for error in errors), errors)

    def test_stale_page_update_date_fails_the_gate(self) -> None:
        self.assertNotEqual(build_front.CHECKED_ON, build_front.UPDATED_ON)
        for rel, document in (("suggestions.html", self.suggestions), ("questions.html", self.questions)):
            with self.subTest(page=rel):
                corrupted = document.replace(
                    f"last updated {build_front.UPDATED_ON}",
                    f"last updated {build_front.CHECKED_ON}",
                    1,
                )
                errors = verify_front.decision_surface_problems(rel, corrupted, self.board)
                self.assertTrue(any("G11" in error for error in errors), errors)

    def test_misdated_current_register_fails_the_gate(self) -> None:
        for rel, document in (("suggestions.html", self.suggestions), ("questions.html", self.questions)):
            with self.subTest(page=rel):
                corrupted = document.replace(
                    f'data-current-as-of="{publication.DATE}"',
                    'data-current-as-of="1900-01-01"',
                    1,
                )
                errors = verify_front.decision_surface_problems(rel, corrupted, self.board)
                self.assertTrue(any("dates are not explicit" in error for error in errors), errors)

    def test_misdated_earlier_suggestion_register_fails_the_gate(self) -> None:
        compiled = str(self.board["compiled_utc"])
        corrupted = self.suggestions.replace(
            f'data-board-compiled="{compiled}"',
            'data-board-compiled="1900-01-01"',
            1,
        )
        errors = verify_front.decision_surface_problems("suggestions.html", corrupted, self.board)
        self.assertTrue(any("dates are not explicit" in error for error in errors), errors)

    def test_misdated_owner_direction_rollup_fails_the_gate(self) -> None:
        dates = [
            row["owner_direction"]["date"]
            for row in self.board["suggestions"]
            if row.get("owner_direction") and row["owner_direction"].get("date")
        ]
        latest_direction = max(dates)
        corrupted = self.suggestions.replace(
            f'data-owner-directions-through="{latest_direction}"',
            'data-owner-directions-through="1900-01-01"',
            1,
        )
        errors = verify_front.decision_surface_problems("suggestions.html", corrupted, self.board)
        self.assertTrue(any("dates are not explicit" in error for error in errors), errors)

    def test_misdated_earlier_question_register_fails_the_gate(self) -> None:
        compiled = str(self.board["compiled_utc"])
        corrupted = self.questions.replace(
            f'data-board-compiled="{compiled}"',
            'data-board-compiled="1900-01-01"',
            1,
        )
        errors = verify_front.decision_surface_problems("questions.html", corrupted, self.board)
        self.assertTrue(any("dates are not explicit" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main(verbosity=2)
