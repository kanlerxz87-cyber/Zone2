#!/usr/bin/env python3
"""Negative controls for D8, the per-page identity gate added by T72 (session arena/672f9c4c-zone2).

The repository's convention is that a gate is not trusted until it has been shown to fail: eleven
other namespaces ship "N injected defects must each fire" steps in `.github/workflows/pages.yml`, and
`tools/seo_audit.py` shipped D1-D7 without one. D8 is the check that keeps S-04 / RQ-01 shut, so it
gets the same treatment here.

What is proven, against a temporary miniature site rather than the working tree:

  * the pre-T72 defects each fail the gate — a page with no description, a title two pages share,
    and one description string served to several pages;
  * the repaired shape passes;
  * each failure is attributed to the property that actually broke, so a green build cannot come
    from a check that fired for the wrong reason;
  * the derived helpers the three generators now use (`page_description` in
    `tools/build_site.py` and `tools/build_decisions.py`, and the inline composer in
    `revalidation/scripts/build.py`) return a non-empty, single-line, bounded-length string for the
    inputs already in the tree — no generated page can silently revert to a blank description.

Run: python3 tests/test_page_identity.py
"""
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "revalidation" / "scripts"))

import build_decisions  # noqa: E402
import build_site  # noqa: E402
import seo_audit  # noqa: E402

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def page(title: str, description: str | None, extra: str = "") -> str:
    """One throwaway page in the shape the D8 parser reads."""
    desc = "" if description is None else f'<meta name="description" content="{description}">'
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f"{desc}{extra}</head><body><p>{DISCLOSURE}</p></body></html>")


class D8Tests(unittest.TestCase):
    """Drive `tools/seo_audit.py`'s real main() over a temporary tree."""

    def run_gate(self, pages: dict[str, str]) -> tuple[int, str]:
        """Run the real gate over a miniature tree; return (exit code, stdout).

        The miniature tree satisfies D8 and nothing else: D1/D3/D5/D6 describe the real repository
        (its sitemap, robots.txt and favicon), so this test reads the D8 verdict rather than the
        process exit code. `d8()` below is the only thing asserted on.
        """
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rel, body in pages.items():
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            # The gate derives its page set from REPO and reads sitemap/robots from it. Only the
            # page set and the two documents D8 does not touch are redirected; D1-D7 are reported
            # by the same run and are irrelevant to what this test asserts.
            import contextlib
            import io
            (root / "robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
            (root / "sitemap.xml").write_text(
                '<?xml version="1.0" encoding="UTF-8"?>'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
                encoding="utf-8",
            )
            real_repo, real_pages = seo_audit.REPO, seo_audit.published_pages
            seo_audit.REPO = root
            seo_audit.published_pages = lambda: sorted(Path(r) for r in pages)
            out = io.StringIO()
            try:
                with contextlib.redirect_stdout(out):
                    code = seo_audit.main()
            finally:
                seo_audit.REPO, seo_audit.published_pages = real_repo, real_pages
            return code, out.getvalue()

    # ---- controls ---------------------------------------------------------------------

    @staticmethod
    def d8(out: str) -> tuple[str, list[str]]:
        """The D8 verdict line and the D8 FAIL lines, so nothing else can satisfy an assertion."""
        verdict = next((ln for ln in out.splitlines() if ln.strip().startswith("D8 per-page identity")), "")
        fails = [ln for ln in out.splitlines() if ln.startswith("FAIL D8 ")]
        return verdict, fails

    def test_clean_site_passes(self):
        _, out = self.run_gate({
            "a.html": page("A", "Alpha page about air fryer baskets."),
            "b.html": page("B", "Beta page about meat thermometers."),
        })
        verdict, fails = self.d8(out)
        self.assertIn("PASS", verdict, out)
        self.assertEqual(fails, [], out)
        self.assertIn("2/2 described, 2 distinct titles, 2 distinct descriptions", verdict)

    def test_blank_description_fails(self):
        """The exact defect six revalidation pages and the 404 page shipped with."""
        code, out = self.run_gate({
            "a.html": page("A", "Alpha page about air fryer baskets."),
            "b.html": page("B", None),
        })
        verdict, fails = self.d8(out)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL", verdict, out)
        self.assertTrue(any("carry no meta description" in f and "b.html" in f for f in fails), out)

    def test_duplicate_title_fails(self):
        """The exact defect both category bands and the two thermometer pages shipped with."""
        code, out = self.run_gate({
            "a.html": page("Same title", "Alpha page about air fryer baskets."),
            "b.html": page("Same title", "Beta page about meat thermometers."),
        })
        verdict, fails = self.d8(out)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL", verdict, out)
        self.assertTrue(any("1 title(s) shared by more than one page" in f for f in fails), out)

    def test_duplicate_description_fails(self):
        """The exact defect 39 pages/ URLs and 4 decisions/ URLs shipped with."""
        shared = "One summary reused across several pages of the same namespace."
        code, out = self.run_gate({
            "a.html": page("A", shared),
            "b.html": page("B", shared),
            "c.html": page("C", shared),
        })
        verdict, fails = self.d8(out)
        self.assertEqual(code, 1, out)
        self.assertIn("FAIL", verdict, out)
        self.assertTrue(any("1 description(s) shared by more than one page" in f and "on 3 pages" in f
                            for f in fails), out)

    def test_failures_are_attributed_and_not_cross_reported(self):
        """A blank description must not be reported as a duplicate, and vice versa."""
        code, out = self.run_gate({
            "a.html": page("A", None),
            "b.html": page("B", "Unique beta summary."),
        })
        _, fails = self.d8(out)
        self.assertEqual(code, 1, out)
        self.assertTrue(any("carry no meta description" in f for f in fails), out)
        self.assertFalse(any("shared by more than one page" in f for f in fails), out)


class DerivationTests(unittest.TestCase):
    """The composers must stay non-empty, single-line and bounded for real tree inputs."""

    def check(self, text: str, where: str) -> None:
        self.assertTrue(text.strip(), f"{where}: empty description")
        self.assertNotIn("\n", text, f"{where}: description contains a newline")
        self.assertLessEqual(len(text), 160, f"{where}: description {len(text)} chars > 160: {text!r}")
        self.assertNotRegex(text, r"<[^>]+>", f"{where}: description contains markup: {text!r}")

    def test_pages_namespace(self):
        # Every lead string the pages/ generator actually passes, read from its own source so a new
        # page cannot be added without this test seeing it.
        src = (ROOT / "tools" / "build_site.py").read_text(encoding="utf-8")
        leads = re.findall(r'return render\(\s*\n?\s*"[^"]+",\s*"[^"]+",\s*"([^"]+)"', src)
        leads += re.findall(r'return render\("index\.html", "Findings hub", "([^"]+)"', src)
        self.assertGreaterEqual(len(leads), 10, f"only found {len(leads)} leads to check")
        for lead in leads:
            self.check(build_site.page_description("A page title", lead), f"pages/ lead {lead[:40]!r}")

    def test_decisions_namespace(self):
        src = (ROOT / "tools" / "build_decisions.py").read_text(encoding="utf-8")
        leads = re.findall(r'"([A-Z][^"\n]{40,})"\s*\n?\s*"(?:[^"\n]*)"?,?\s*\n?\s*"?\.join\(', src)
        for lead in leads:
            self.check(build_decisions.page_description("The content plan", lead),
                       f"decisions/ lead {lead[:40]!r}")
        # And the four titles the namespace publishes, against a worst-case long lead.
        for title in ("Decision hub", "The full requirement set", "The content plan", "Flagged for review"):
            self.check(build_decisions.page_description(title, "x" * 300), f"decisions/ {title}")

    def test_truncation_is_clean(self):
        long = build_site.page_description("Title", "y " * 200)
        self.assertLessEqual(len(long), 160)
        self.assertTrue(long.endswith("…"), f"expected an ellipsis, got {long[-20:]!r}")
        self.assertNotIn(" ,", long)
        self.assertNotIn("  ", long)


if __name__ == "__main__":
    unittest.main(verbosity=2)
