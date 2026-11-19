#!/usr/bin/env python3
"""Inject separated-block prices into the SIX ACTUAL repaired price guards.

No working-tree mutation: namespace validators are pointed at temporary files;
workflow step bodies are executed unchanged in a temporary miniature site.
"""
from __future__ import annotations
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_readiness as readiness
import ci_replay
import validate_audit as audit
import validate_data as data
import validate_decisions as decisions

DISC='As an Amazon Associate I earn from qualifying purchases.'
CONTROL=f'<html><body><p>{DISC}</p><p>Commission example $3.00 under published program rules.</p></body></html>'
BAD=CONTROL.replace('</body>','<p>Current product price: <strong>$123.45</strong>. Buy this appliance.</p></body>')


class PriceGuardTests(unittest.TestCase):
    def test_data_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'price.html'
            with patch.object(data,'REPO',root),patch.object(data,'owned_pages',return_value=[p]):
                for html,expected in [(CONTROL,False),(BAD,True)]:
                    p.write_text(html);report=data.Report();data.check_no_product_prices(report)
                    self.assertEqual(bool(report.errors),expected)

    def test_audit_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'price.html'
            with patch.object(audit,'pages',return_value=[p]):
                for html,expected in [(CONTROL,False),(BAD,True)]:
                    p.write_text(html)
                    self.assertEqual(any('A12' in error for error in audit.check_pages()[0]),expected)

    def test_decision_guard(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/'price.html'
            with patch.object(decisions,'REPO',root),patch.object(decisions,'OUT',root):
                for html,expected in [(CONTROL,False),(BAD,True)]:
                    p.write_text(html);report=decisions.Report();decisions.check_pages(report)
                    self.assertEqual(any('money value' in e for e in report.errors),expected)

    def test_readiness_guard(self):
        self.assertEqual(readiness.no_price_problems(CONTROL),[])
        self.assertTrue(readiness.no_price_problems(BAD))

    def workflow_case(self,step_name,companion=False):
        body=next(body for name,body in ci_replay.steps() if name.startswith(step_name))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);directory=root/'affiliate-lab' if companion else root;directory.mkdir(exist_ok=True)
            for i in range(80 if not companion else 10):(directory/f'control-{i}.html').write_text(CONTROL)
            good=subprocess.run(['bash','-e','-o','pipefail','-c',body],cwd=root,text=True,capture_output=True)
            self.assertEqual(good.returncode,0,good.stdout+good.stderr)
            (directory/'price.html').write_text(BAD)
            bad=subprocess.run(['bash','-e','-o','pipefail','-c',body],cwd=root,text=True,capture_output=True)
            self.assertNotEqual(bad.returncode,0)
            self.assertIn('money value',bad.stdout+bad.stderr)
            self.assertIn('$123.45',bad.stdout+bad.stderr)

    def test_main_workflow_guard(self):
        self.workflow_case('No page prints a price')

    def test_companion_workflow_guard(self):
        self.workflow_case('affiliate-lab discloses',True)


if __name__=='__main__':unittest.main(verbosity=2)
