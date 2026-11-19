#!/usr/bin/env python3
"""Negative-test the repaired rule in actual validators and workflow blocks.

All fixtures live outside the checkout; no production file or campaign is mutated.
"""
from __future__ import annotations
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import build_readiness
import validate_data
import validate_audit
import validate_decisions
from ci_replay import steps
from site_inventory import has_tagged_link, source_html

ROOT=Path(__file__).resolve().parents[1]
DISCLOSURE='As an Amazon Associate I earn from qualifying purchases.'
CLEAN=f'<!doctype html><html><head><title>Fixture</title></head><body><p>{DISCLOSURE}</p><p>Published bounty payment $3.</p></body></html>'
BAD=CLEAN.replace('</body>','<p>Buy now at the current price of $149.99.</p></body>')


class PriceRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        self.page=self.root/'index.html'
    def tearDown(self): self.temp.cleanup()
    def test_dataset_validator_not_exempted_by_earn_elsewhere(self):
        for html,expected in [(CLEAN,False),(BAD,True)]:
            self.page.write_text(html); report=validate_data.Report()
            with patch.object(validate_data,'REPO',self.root),patch.object(validate_data,'owned_pages',return_value=[self.page]):
                validate_data.check_no_product_prices(report)
            self.assertEqual(any('buying context' in e for e in report.errors),expected)
    def test_audit_validator_not_exempted_by_earn_elsewhere(self):
        for html,expected in [(CLEAN,False),(BAD,True)]:
            self.page.write_text(html)
            with patch.object(validate_audit,'pages',return_value=[self.page]): errors,_=validate_audit.check_pages()
            self.assertEqual(any('A12' in e for e in errors),expected)
    def test_decision_validator_not_exempted_by_earn_elsewhere(self):
        for html,expected in [(CLEAN,False),(BAD,True)]:
            for n in range(4): (self.root/f'page{n}.html').write_text(html)
            report=validate_decisions.Report()
            with patch.object(validate_decisions,'REPO',self.root),patch.object(validate_decisions,'OUT',self.root):
                validate_decisions.check_pages(report)
            self.assertEqual(any('buying context' in e for e in report.errors),expected)
    def test_readiness_validator_not_exempted_by_earn_elsewhere(self):
        self.assertEqual(build_readiness.no_price_problems(CLEAN),[])
        self.assertTrue(build_readiness.no_price_problems(BAD))
    def workflow_case(self,name,affiliate=False):
        for n in range(70): (self.root/f'page{n}.html').write_text(CLEAN)
        sub=self.root/'affiliate-lab';sub.mkdir()
        for n in range(10): (sub/f'page{n}.html').write_text(CLEAN)
        script=next(body for title,body in steps() if name in title)
        env={**os.environ,'PYTHONPATH':str(ROOT)}
        clean=subprocess.run(['bash','-c',script],cwd=self.root,env=env,capture_output=True,text=True)
        self.assertEqual(clean.returncode,0,clean.stdout+clean.stderr)
        target=(sub if affiliate else self.root)/'page0.html';target.write_text(BAD)
        bad=subprocess.run(['bash','-c',script],cwd=self.root,env=env,capture_output=True,text=True)
        self.assertNotEqual(bad.returncode,0)
        self.assertIn('buying context',bad.stdout+bad.stderr)
    def test_main_workflow_price_block(self): self.workflow_case('No page prints a price')
    def test_affiliate_workflow_price_block(self): self.workflow_case('affiliate-lab discloses',affiliate=True)
    def test_tagged_prose_is_not_a_link(self):
        self.assertFalse(has_tagged_link('<p>The tag is shopnow047c-20, e.g. ?tag=shopnow047c-20.</p>'))
        self.assertTrue(has_tagged_link('<a href="https://www.amazon.com/dp/B0DHZTCNR5?tag=shopnow047c-20">View listing</a>'))
        self.assertFalse(has_tagged_link('<a href="https://other.example/?tag=shopnow047c-20">Other</a>'))
    def test_source_inventory_excludes_projection_and_runtime(self):
        self.page.write_text(CLEAN)
        for folder in ['_site','.local','node_modules']:
            (self.root/folder).mkdir();(self.root/folder/'duplicate.html').write_text(CLEAN)
        self.assertEqual(list(source_html(self.root)),[self.page])


if __name__=='__main__': unittest.main(verbosity=2)
