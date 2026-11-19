#!/usr/bin/env python3
"""Synthetic link-shape checks only. No Amazon request or enrollment assumption."""
from pathlib import Path
import sys
import unittest
from urllib.parse import parse_qs,urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from link_builder import ASSOCIATES_TAG,LinkPolicyError,build_product_link


class IssuedTagTests(unittest.TestCase):
    def link(self,**kwargs):
        return build_product_link('B0CDY277D3',ASSOCIATES_TAG,link_text='Open this product listing',**kwargs)

    def test_current_link_is_unchanged(self):
        self.assertEqual(self.link().href,'https://amazon.com/dp/B0CDY277D3?tag=shopnow047c-20')

    def test_no_static_campaign_tag_is_minted(self):
        with self.assertRaises(LinkPolicyError):self.link(subtag='kitchen-hero')

    def test_no_per_reader_tag_is_minted(self):
        with self.assertRaises(LinkPolicyError):self.link(subtag='user-123')

    def test_attribution_cannot_be_overridden(self):
        for key in ('tag','TAG','linkCode','ascsubtag'):
            with self.subTest(key=key),self.assertRaises(LinkPolicyError):self.link(extra_params={key:'not-issued-20'})

    def test_unreviewed_dimensions_and_competing_tracking_fail_closed(self):
        for key in ('aff_id','clickid','visitor'):
            with self.subTest(key=key),self.assertRaises(LinkPolicyError):self.link(extra_params={key:'synthetic'})

    def test_empty_legacy_arguments_do_not_change_exact_id(self):
        link=self.link(subtag='',extra_params={})
        self.assertEqual(parse_qs(urlsplit(link.href).query),{'tag':[ASSOCIATES_TAG]})

    def test_tag_with_trailing_newline_is_not_accepted(self):
        with self.assertRaises(LinkPolicyError):
            build_product_link('B0CDY277D3',ASSOCIATES_TAG+'\n',link_text='Open this product listing')


if __name__=='__main__':unittest.main(verbosity=2)
