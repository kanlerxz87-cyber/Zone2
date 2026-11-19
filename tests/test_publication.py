#!/usr/bin/env python3
"""Negative tests for source/intent/artifact rules. All mutations are temporary/in-memory."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import package_site as package
import publication as pub
import verify_publication as verify


class DataTests(unittest.TestCase):
    def mutation(self,change,expected):
        data=copy.deepcopy(pub.DATA);guides=copy.deepcopy(pub.GUIDES)
        change(data,guides)
        self.assertTrue(any(expected in issue for issue in verify.data_problems(data,guides)),expected)

    def test_clean_data(self):self.assertEqual(verify.data_problems(),[])
    def test_nonofficial_source(self):self.mutation(lambda d,g:d['sources']['M1'].update(url='https://unofficial.example/facts'),'nonofficial')
    def test_source_without_date(self):self.mutation(lambda d,g:d['sources']['M1'].update(checked=''),'dated')
    def test_missing_row_source(self):self.mutation(lambda d,g:d['products'][0]['specs'][0].__setitem__(2,'MADE_UP'),'registered official source')
    def test_blank_without_reason(self):self.mutation(lambda d,g:d['products'][0]['specs'][0].__setitem__(1,''),'blank without')
    def test_unverified_value_filled(self):self.mutation(lambda d,g:d['products'][1]['specs'][3].__setitem__(1,'25'),'must stay blank')
    def test_partial_intent(self):self.mutation(lambda d,g:d['products'][0]['intent'].update(intended_asin='B0CDY277D3'),'incomplete intended')
    def test_observation_is_not_confirmation(self):
        self.mutation(lambda d,g:d['products'][0]['intent'].update(intended_asin='B0CDY277D3',official_listing_url='https://www.amazon.com/dp/B0CDY277D3',confirmation_date='2026-11-19',source='M2'),'not an intended-product confirmation')
    def test_bad_observed_asin(self):self.mutation(lambda d,g:d['products'][0]['observation'].update(observed_asin='B04G1MEwY'),'invalid observed ASIN')
    def test_observation_listing_mismatch(self):self.mutation(lambda d,g:d['products'][0]['observation'].update(observed_redirect_target='https://www.amazon.com/dp/B09B7SB46R'),'observation/listing mismatch')
    def test_duplicate_product(self):self.mutation(lambda d,g:d['products'][0].update(key='P2'),'five distinct')
    def test_unsourced_guide(self):self.mutation(lambda d,g:g[0]['sections'][0].update(sources=[]),'unsourced section')


class TransformTests(unittest.TestCase):
    def test_archive_sponsored_disclosed_noindex_selfcanonical(self):
        text='''<html><head><link rel="canonical" href="https://wrong.example"><meta name="robots" content="index,follow"></head><body><header>Old masthead</header><main><h1>Evidence</h1><a href='https://www.amazon.com/dp/B0CDY277D3' rel='noopener'>Source</a></main></body></html>'''
        out=package.transform(text,'journal/record.html');parsed=verify.Page(out)
        self.assertEqual(parsed.canonicals,[pub.BASE+'journal/record.html'])
        self.assertEqual(parsed.robots,['noindex,follow'])
        self.assertGreaterEqual(out.count(pub.DISCLOSURE),2)
        self.assertLess(out.index('data-disclosure-strip'),out.index('<main'))
        self.assertNotIn('Old masthead',out)
        self.assertIn('sponsored',next(a['rel'] for a in parsed.anchors if 'amazon.com/dp' in a['href']))
        self.assertIn('Evidence',out)

    def test_existing_sponsored_tokens_retained(self):
        out=package.sponsor_anchors('<a href="https://amazon.com/dp/B0CDY277D3" rel="ugc noreferrer nofollow sponsored">Listing</a>')
        rel=verify.Page(out).anchors[0]['rel'].split()
        self.assertEqual(set(rel),{'ugc','nofollow','sponsored','noopener'})

    def test_external_policy_not_relabelled_product(self):
        src='<a href="https://affiliate-program.amazon.com/help/operating/policies" rel="noopener">Rule</a>'
        self.assertEqual(package.sponsor_anchors(src),src)

    def test_javascript_literal_is_not_rewritten_as_html(self):
        raw = "<script>var x = '<a href=\"https://amazon.com/dp/B0CDY277D3\">Listing</a>';</script>"
        self.assertEqual(package.sponsor_anchors(raw),raw)
        self.assertIn('archive-links.js',package.transform('<html><head></head><body>'+raw+'</body></html>','zone2/test.html'))

    def test_short_link_is_sponsored_not_invalidated(self):
        out=package.sponsor_anchors('<a href="https://link.amazon/B04G1MEwY">Supplied</a>')
        parsed=verify.Page(out)
        self.assertIn('sponsored',parsed.anchors[0]['rel'])
        self.assertEqual(parsed.anchors[0]['href'],'https://link.amazon/B04G1MEwY')

    def test_only_known_staging_path_may_be_replaced(self):
        with self.assertRaises(ValueError):package.build(ROOT/'content')


class ArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):package.build()
    def test_clean_artifact(self):
        errors,stats=verify.verify(ROOT/'_site')
        self.assertEqual(errors,[])
        self.assertEqual(stats['indexable_pages'],16)
        self.assertGreater(stats['html_pages'],180)

    def mutate(self,rel,change,expected):
        path=ROOT/'_site'/rel;original=path.read_text()
        try:
            path.write_text(change(original));errors,_=verify.verify(ROOT/'_site')
            self.assertTrue(any(expected in error for error in errors),expected)
        finally:path.write_text(original)

    def test_build_metadata_is_required(self):self.mutate('publication-build.json',lambda s:'{}','source build metadata')
    def test_removed_disclosure(self):self.mutate('shop.html',lambda s:s.replace(pub.DISCLOSURE,''),'disclosure must appear')
    def test_unsponsored_anchor(self):self.mutate('shop.html',lambda s:s.replace('rel="sponsored nofollow noopener"','rel="nofollow noopener"',1),'unsponsored product')
    def test_noindex_archive_is_mandatory(self):self.mutate('pages/index.html',lambda s:s.replace('noindex,follow','index,follow'),'indexing state')
    def test_wrong_canonical(self):self.mutate('shop.html',lambda s:s.replace('rel="canonical" href="'+pub.BASE+'shop.html"','rel="canonical" href="'+pub.BASE+'"'),'self-canonical')
    def test_dead_fragment(self):self.mutate('shop.html',lambda s:s.replace('href="guides/chefman-dual-basket.html"','href="guides/chefman-dual-basket.html#missing"',1),'broken fragment')
    def test_wrong_tracking_id(self):self.mutate('shop.html',lambda s:s.replace('?tag=shopnow047c-20','?tag=wrong-20',1),'CTA destination/tag')
    def test_unsafe_static_config(self):self.mutate('measurement.json',lambda s:s.replace('false','true'),'Pages measurement must stay OFF')
    def test_table_source_removed(self):self.mutate('guides/chefman-dual-basket.html',lambda s:s.replace('href="https://chefman.com/products/turbofry-touch-dual-window-air-fryer"','href="https://unofficial.example"'),'table row lacks official')


if __name__=='__main__':unittest.main(verbosity=2)
