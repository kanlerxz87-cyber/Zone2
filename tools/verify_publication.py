#!/usr/bin/env python3
"""Current publication + deploy artifact contract. Stdlib, no network or account access.

Checks the artifact users receive, not only the historically generated source files.
This is in addition to (not instead of) every prior namespace gate.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit
import xml.etree.ElementTree as ET

import publication as pub
from package_site import is_product_url

ROOT=Path(__file__).resolve().parents[1]
# T69 (session arena/698addcd): www.w3.org added on the precedent set by CR-8, which added
# www.fsis.usda.gov for exactly this reason - an official standards body became the governing
# citation for a reader-facing rule. W3C authors WCAG, so it is the authoritative source for
# SC 2.5.8 Target Size (Minimum) cited by the Decision Room's accessibility rows.
OFFICIAL_HOSTS={'github.blog','github.com','link.amazon','affiliate-program.amazon.com','www.amazon.com','amazon.com','chefman.com','www.chefman.com','www.emerileveryday.com','www.ftc.gov','ftc.gov','docs.github.com','developers.google.com','support.google.com','www.fsis.usda.gov','www.w3.org'}
CURRENT=pub.indexable_paths()|set(pub.extra_pages())|{'suggestions.html','questions.html'}


class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.refs=[];self.anchors=[];self.canonicals=[];self.robots=[];self.og=[];self.rows=[];self.row=None;self.table_depth=0
        self.tags=[];self.h1=0;self.structured=[];self.in_json=False;self.json_text=''
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);self.tags.append((tag,a))
        if 'id' in a:self.ids.append(a['id'])
        if tag=='h1':self.h1+=1
        if tag=='table':self.table_depth+=1
        if tag=='tr':self.row={'data':False,'anchors':[]}
        if tag=='td' and self.row is not None:self.row['data']=True
        if tag=='a' and a.get('href'):
            self.anchors.append(a)
            if self.row is not None:self.row['anchors'].append(a['href'])
        if tag=='a' and a.get('href'):self.refs.append(a['href'])
        if tag in ('img','script','source') and a.get('src'):self.refs.append(a['src'])
        if tag=='source' and a.get('srcset'):self.refs.extend(x.strip().split()[0] for x in a['srcset'].split(','))
        if tag=='link' and a.get('href'):
            self.refs.append(a['href'])
            if a.get('rel')=='canonical':self.canonicals.append(a['href'])
        if tag=='meta' and a.get('name')=='robots':self.robots.append(a.get('content',''))
        if tag=='meta' and a.get('property')=='og:url':self.og.append(a.get('content',''))
        if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.json_text=''
    def handle_data(self,text):
        if self.in_json:self.json_text+=text
    def handle_endtag(self,tag):
        if tag=='tr' and self.row is not None:
            if self.row['data']:self.rows.append(self.row)
            self.row=None
        if tag=='table':self.table_depth-=1
        if tag=='script' and self.in_json:
            self.structured.append(self.json_text);self.in_json=False


def data_problems(data=None,guides=None):
    data=pub.DATA if data is None else data
    guides=pub.GUIDES if guides is None else guides
    errors=[]
    def fail(text):errors.append(text)
    sources=data['sources']
    for sid,source in sources.items():
        u=urlsplit(source.get('url',''))
        if u.scheme!='https' or u.hostname not in OFFICIAL_HOSTS:fail(f'{sid}: nonofficial/unsafe source URL')
        try:date.fromisoformat(source['checked'])
        except (KeyError,ValueError):fail(f'{sid}: missing dated verification')
        if not source.get('scope'):fail(f'{sid}: missing source scope')
    products=data['products']
    if {p['key'] for p in products}!={'P1','P2','P3','P4','P5'} or len(products)!=5:fail('Exactly five distinct product records required')
    for p in products:
        key=p['key'];intent=p['intent'];obs=p['observation']
        if set(intent)!={'intended_asin','official_listing_url','confirmation_date','source'}:fail(f'{key}: intent schema drift')
        if any(intent.values()):
            if not all(intent.values()):fail(f'{key}: incomplete intended-product confirmation')
            # This release holds no confirmation source; adding one requires its own explicit dated record.
            if intent.get('source') not in sources:fail(f'{key}: unregistered confirming source')
            if sources.get(intent.get('source'),{}).get('kind')!='intent_confirmation':fail(f'{key}: source is not an intended-product confirmation')
            if not re.fullmatch(r'[A-Z0-9]{10}',intent.get('intended_asin','')):fail(f'{key}: invalid intended ASIN')
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',intent.get('confirmation_date','')):fail(f'{key}: no confirmation date')
        if not re.fullmatch(r'[A-Z0-9]{10}',obs.get('observed_asin','')):fail(f'{key}: invalid observed ASIN')
        if obs.get('source') not in sources or not obs.get('observed_at'):fail(f'{key}: missing observation provenance')
        if obs.get('observed_redirect_target')!='https://www.amazon.com/dp/'+obs['observed_asin']:fail(f'{key}: observation/listing mismatch')
        if not re.fullmatch(r'https://link\.amazon/[A-Za-z0-9]{9}',p['submitted']):fail(f'{key}: supplied link changed')
        for label,value,sid,state in p['specs']:
            refs=sid if isinstance(sid,list) else [sid]
            if not refs or any(i not in sources for i in refs):fail(f'{key}/{label}: no registered official source')
            if not value and 'unverified' not in state.lower():fail(f'{key}/{label}: blank without an unverified reason')
            if value and 'unverified' in state.lower():fail(f'{key}/{label}: unverified value must stay blank')
    slugs=[g['slug'] for g in guides]
    if len(slugs)!=len(set(slugs)):fail('Duplicate guide slug')
    for g in guides:
        if not g.get('answer') or not g.get('sections'):fail(f'{g["slug"]}: missing useful answer/sections')
        if any(p not in {'P1','P2','P3','P4','P5'} for p in g['products']):fail('Guide references unknown product')
        for section in g['sections']:
            if not section.get('sources') or any(s not in sources for s in section['sources']):fail(f'{g["slug"]}: unsourced section')
    return errors


def verify(site):
    site=site.resolve();errors=data_problems();parsed={};texts={};product_links=0;factual_rows=0
    if not site.is_dir():return ['Missing packaged site; run tools/package_site.py'],{}
    for path in sorted(site.rglob('*.html')):
        rel=path.relative_to(site).as_posix();text=path.read_text();page=Page(text)
        parsed[rel]=page;texts[rel]=text
        if text.count(pub.DISCLOSURE)<2:errors.append(f'{rel}: disclosure must appear at least twice')
        if 'data-disclosure-strip' not in text:errors.append(f'{rel}: missing masthead disclosure')
        if text.find('data-disclosure-strip')>text.find('<main')>=0:errors.append(f'{rel}: disclosure is after main content')
        expected=pub.BASE+('' if rel=='index.html' else rel)
        if page.canonicals!=[expected]:errors.append(f'{rel}: not exactly one self-canonical')
        wanted='index,follow' if rel in pub.indexable_paths() else 'noindex,follow'
        if page.robots!=[wanted]:errors.append(f'{rel}: incorrect artifact indexing state')
        for a in page.anchors:
            if is_product_url(a['href']):
                product_links+=1
                if 'sponsored' not in a.get('rel','').split():errors.append(f'{rel}: unsponsored product anchor')
            if a.get('data-product-key'):
                key=a['data-product-key'];u=urlsplit(a['href'])
                if re.fullmatch(r'P-0[1-5]',key):key='P'+key[-1]
                if key not in pub.PRODUCTS or u.scheme!='https' or u.hostname!='amazon.com' or u.path!='/dp/'+pub.PRODUCTS[key]['observation']['observed_asin'] or parse_qs(u.query)!={'tag':['shopnow047c-20']}:
                    errors.append(f'{rel}: product CTA destination/tag mismatch')
        if rel in CURRENT:
            if page.h1!=1:errors.append(f'{rel}: expected one H1')
            dupes=[i for i,n in Counter(page.ids).items() if n>1]
            if dupes:errors.append(f'{rel}: duplicate IDs {dupes}')
            if page.og!=[expected]:errors.append(f'{rel}: Open Graph URL mismatch')
            for row in page.rows:
                factual_rows+=1
                if not any(urlsplit(u).hostname in OFFICIAL_HOSTS for u in row['anchors']):errors.append(f'{rel}: factual table row lacks official source')
            for raw in page.structured:
                try:
                    doc=json.loads(raw)
                    if doc.get('@type') in ('Review','Product','AggregateRating'):errors.append(f'{rel}: unsupported review/product markup')
                except ValueError:errors.append(f'{rel}: invalid JSON-LD')
    for rel,page in parsed.items():
        for ref in page.refs:
            u=urlsplit(ref)
            if u.scheme or u.netloc:continue
            target=(site/rel).parent/unquote(u.path) if not u.path.startswith('/') else site/unquote(u.path).removeprefix('/Zone2/')
            target=target.resolve()
            if not u.path:target=site/rel
            if target.is_dir():target/= 'index.html'
            if not target.is_relative_to(site) or not target.is_file():
                errors.append(f'{rel}: missing internal reference {ref}');continue
            target_rel=target.relative_to(site).as_posix()
            # Old hash-router routes are declared data-page attributes rather than IDs.
            if u.fragment and target_rel in parsed:
                dest=parsed[target_rel]
                routes={a.get('data-page') for _,a in dest.tags}
                if unquote(u.fragment).lower() not in {i.lower() for i in dest.ids} and u.fragment not in routes:
                    errors.append(f'{rel}: broken fragment {ref}')
    if set(pub.indexable_paths())-parsed.keys():errors.append('Registered reader page missing from artifact')
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    try:
        locs=[n.text for n in ET.parse(site/'sitemap.xml').findall('s:url/s:loc',ns)]
        wanted={pub.BASE+('' if p=='index.html' else p) for p in pub.indexable_paths()}
        if set(locs)!=wanted or len(locs)!=len(wanted):errors.append('Canonical sitemap differs from reader registry')
        feed=ET.parse(site/'feed.xml')
        if len(feed.findall('./channel/item'))!=len(pub.GUIDES):errors.append('Root RSS guide count mismatch')
    except (OSError,ET.ParseError):errors.append('Missing/invalid canonical sitemap or RSS')
    try:
        config=json.loads((site/'measurement.json').read_text())
        if config.get('enabled') is not False or config.get('endpoint') is not None or config.get('mode')!='github_pages_static':errors.append('Pages measurement must stay OFF')
    except (OSError,ValueError):errors.append('Missing/invalid Pages measurement config')
    try:
        build=json.loads((site/'publication-build.json').read_text())
        if build.get('schema')!='counter-notes-build-v1' or not isinstance(build.get('commit'),str) or not re.fullmatch(r'[0-9a-f]{40}',build['commit']):
            errors.append('Invalid source build metadata')
    except (OSError,ValueError):errors.append('Missing source build metadata')
    for p in site.rglob('*'):
        rel=p.relative_to(site)
        if any(part in {'.git','.local','node_modules','tests','__pycache__'} for part in rel.parts) or '.sqlite' in p.name:errors.append('Private/tooling file leaked to artifact')
    return sorted(set(errors)),{'html_pages':len(parsed),'indexable_pages':len(pub.indexable_paths()),'product_anchors_checked':product_links,'current_factual_rows_checked':factual_rows}


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--site',type=Path,default=ROOT/'_site');args=ap.parse_args()
    errors,stats=verify(args.site)
    print(json.dumps({'ok':not errors,'errors':errors,'stats':stats},indent=2))
    return int(bool(errors))


if __name__=='__main__':raise SystemExit(main())
