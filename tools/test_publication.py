#!/usr/bin/env python3
"""Publication regressions and negative controls; all offline, no affiliate clicks."""
from __future__ import annotations
import copy
import unittest
from pathlib import Path
from publication import DATA, home, suggestions
from publication_shell import apply_chrome, DISCLOSURE
from verify_front import data_errors, html_errors, checks
from price_policy import context_units
from link_builder import build_product_link, LinkPolicyError
import re


class PublicationTests(unittest.TestCase):
    def test_baseline_data(self): self.assertEqual(data_errors(DATA),[])
    def test_all_current_pages(self): self.assertEqual(checks(),[])
    def mutate(self,fn):
        d=copy.deepcopy(DATA);fn(d);self.assertTrue(data_errors(d))
    def test_missing_source(self): self.mutate(lambda d:d['products'][0]['rows'][0].update(source='missing'))
    def test_unofficial_source(self): self.mutate(lambda d:d['sources']['chefman_dual'].update(url='https://blog.example/specs'))
    def test_blank_needs_reason(self): self.mutate(lambda d:d['products'][0]['rows'][0].update(value='',reason=''))
    def test_observation_not_intent(self): self.mutate(lambda d:d['products'][0]['intent'].update(intended_asin=d['products'][0]['asin_observed']))
    def test_field_groups_not_merged(self): self.mutate(lambda d:d['products'][0]['intent'].update(observed_redirect_target='x'))
    def test_no_claimed_attribution(self): self.mutate(lambda d:d['products'][0].update(attribution_report_confirmed=True))
    def test_open_answer_blank(self): self.mutate(lambda d:d['questions'][0].update(answer='assumed'))
    def test_no_preapproved_suggestion(self): self.mutate(lambda d:d['suggestions'][0].update(applied=True))
    def test_no_missing_discovery(self): self.mutate(lambda d:d['questions'][0].update(discover=''))
    def test_recommendation_valid(self): self.mutate(lambda d:d['suggestions'][0].update(recommendation='invented'))
    def test_no_preselection_markup(self): self.assertNotIn(' checked',suggestions())
    def test_no_missing_disclosure(self): self.assertTrue(html_errors(home().replace(DISCLOSURE,''),'index.html'))
    def test_price_injection_caught(self): self.assertTrue(html_errors(home().replace('</main>','<p>Buy now at $149.99.</p></main>'),'index.html'))
    def test_wrong_tag_caught(self): self.assertTrue(html_errors(home().replace('shopnow047c-20','wrong-20'),'index.html'))
    def test_unsponsored_link_caught(self): self.assertTrue(html_errors(home().replace('sponsored nofollow','nofollow'),'index.html'))
    def test_chrome_idempotent(self):
        once=apply_chrome(home(),'index.html')
        self.assertEqual(once,apply_chrome(once,'index.html'))
    def test_price_rule_cannot_be_disabled_by_disclosure(self):
        doc='<p>As an Amazon Associate I earn from qualifying purchases.</p><p>Buy now at the current price of $149.99 today.</p>'
        units=context_units(doc)
        self.assertGreater(len(units),1)
        self.assertTrue(any('$149.99' in x and 'earn' not in x for x in units))
    def test_no_synthesized_amazon_subtags(self):
        with self.assertRaises(LinkPolicyError):
            build_product_link('B0DHZTCNR5','shopnow047c-20',link_text='View listing',subtag='hero')
    def test_no_attribution_override(self):
        with self.assertRaises(LinkPolicyError):
            build_product_link('B0DHZTCNR5','shopnow047c-20',link_text='View listing',extra_params={'tag':'other-20'})
    def test_observation_history_is_preserved(self):
        self.mutate(lambda d:d['products'][3].update(redirect_observations=[]))
    def test_legacy_header_ids_remain_inside_main(self):
        doc='<html><head></head><body><main id="old"><header class="topbar"><span id="crumb">Archive</span></header><p>Original content</p></main></body></html>'
        result=apply_chrome(doc,'pages/index.html')
        self.assertIn('id="crumb"',result)
        self.assertIn('Original content',result)
        self.assertLess(result.index('data-disclosure-strip'),result.index('<main'))
        self.assertEqual(result,apply_chrome(result,'pages/index.html'))
    def test_table_rows_remain_separate(self):
        units=context_units('<tr><td>Commission bounty</td><td>$3</td></tr><tr><td>Buy current price $149.99</td></tr>')
        self.assertTrue(any('$149.99' in x and 'bounty' not in x for x in units))


if __name__=='__main__':unittest.main(verbosity=2)
