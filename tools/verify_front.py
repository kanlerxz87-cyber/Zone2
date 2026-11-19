#!/usr/bin/env python3
"""Current-publication gate: source rows, blank intent, disclosures, direct links and output drift.

An offline structural check does not claim to re-fetch official sources or prove
account enrollment. Those limits and the dated checks are published in the Workroom.
"""
from __future__ import annotations

import copy
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from publication import DATA, TARGETS, AS_OF
from publication_shell import DISCLOSURE

ROOT=Path(__file__).resolve().parents[1]
PAGES=[p for p in TARGETS if p.endswith('.html')]
OFFICIAL={'chefman.com','www.emerileveryday.com','www.amazon.com','affiliate-program.amazon.com',
          'www.ftc.gov','developers.google.com','support.google.com','docs.github.com','link.amazon'}
MONEY=re.compile(r'(?:US)?\$\s?\d[\d,]*(?:\.\d{1,2})?')


class Refs(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.anchors=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a': self.anchors.append(a)
        if tag in {'a','link'} and a.get('href'): self.refs.append(a['href'])
        if tag in {'img','script'} and a.get('src'): self.refs.append(a['src'])


def data_errors(data):
    errors=[]
    if len(data['products'])!=5: errors.append('exactly five submitted products required')
    if len({p['key'] for p in data['products']})!=5: errors.append('duplicate product key')
    for key,s in data['sources'].items():
        if urlsplit(s.get('url','')).hostname not in OFFICIAL: errors.append(f'{key}: unofficial/missing source')
        if not s.get('checked_on') or not s.get('quote'): errors.append(f'{key}: missing check date or scope')
    for p in data['products']:
        if not re.fullmatch(r'[A-Z0-9]{10}',p['asin_observed']): errors.append(p['key']+': invalid observed ASIN shape')
        intent=p.get('intent',{})
        if set(intent)!={'intended_asin','official_listing_url','confirmation_date','source'}: errors.append(p['key']+': intent field group incomplete')
        if any(intent.values()): errors.append(p['key']+': intent filled without a separately reviewed confirmation workflow')
        observations=p.get('redirect_observations',[])
        if not observations or observations[-1].get('target_asin')!=p['asin_observed']:
            errors.append(p['key']+': latest dated observation does not match the displayed destination')
        if p.get('attribution_report_confirmed'): errors.append(p['key']+': attribution cannot be asserted without authorized evidence')
        if set(intent)&{'observed_redirect_target','asin_observed'}: errors.append(p['key']+': observation merged with intent')
        for row in p['rows']:
            if row.get('source') not in data['sources']: errors.append(p['key']+': unregistered fact source')
            if not row.get('value') and not row.get('reason'): errors.append(p['key']+': blank without reason')
    for s in data['suggestions']:
        ids={o['id'] for o in s['options']}
        if len(ids)<2 or s['recommendation'] not in ids: errors.append(s['id']+': invalid review options')
        if s.get('selected') or s.get('applied'): errors.append(s['id']+': proposal pre-applied')
        for field in ['known','missing','effort','risk']:
            if not s.get(field): errors.append(s['id']+': missing '+field)
        if s.get('source') not in data['sources']: errors.append(s['id']+': missing official reference')
    for q in data['questions']:
        if q.get('answer'): errors.append(q['id']+': open answer filled')
        if not q.get('discover') or not q.get('missing'): errors.append(q['id']+': missing discovery action')
    return errors


def html_errors(document,rel):
    errors=[]
    p=Refs(); p.feed(document)
    if document.count(DISCLOSURE)<2: errors.append(rel+': needs masthead and footer disclosure')
    if '<main' not in document or document.find(DISCLOSURE)>document.find('<main'): errors.append(rel+': disclosure must precede main')
    if 'data-disclosure-strip' not in document: errors.append(rel+': no visible strip marker')
    if MONEY.search(document): errors.append(rel+': static currency amount')
    canonical='https://kanlerxz87-cyber.github.io/Zone2/'+('' if rel=='index.html' else rel)
    if f'<link rel="canonical" href="{canonical}">' not in document: errors.append(rel+': wrong canonical')
    for anchor in p.anchors:
        href=anchor.get('href',''); u=urlsplit(href)
        if u.hostname in {'amazon.com','www.amazon.com','link.amazon'}:
            if not {'sponsored','nofollow'}<=set(anchor.get('rel','').split()): errors.append(rel+': unsponsored product link')
        if anchor.get('data-product-key'):
            if u.hostname not in {'amazon.com','www.amazon.com'} or parse_qs(u.query).get('tag')!=['shopnow047c-20']:
                errors.append(rel+': CTA has wrong destination/tag')
            if anchor.get('data-validation-state')!='awaiting-account-report': errors.append(rel+': missing account-validation gate')
    for ref in p.refs:
        if ref.startswith(('https:','http:','mailto:','data:','#')): continue
        path=ref.split('#')[0].split('?')[0]
        target=(ROOT/rel).parent/path
        if not target.is_file(): errors.append(f'{rel}: broken local reference {ref}')
    for body in re.findall(r'<tbody>(.*?)</tbody>',document,re.S):
        for row in re.findall(r'<tr\b[^>]*>.*?</tr>',body,re.S):
            urls=re.findall(r'href="(https://[^\"]+)"',row)
            if not any(urlsplit(u).hostname in OFFICIAL for u in urls): errors.append(rel+': table row has no official reference')
    return errors


def checks():
    errors=data_errors(DATA)
    for rel in PAGES:
        path=ROOT/rel
        if not path.is_file(): errors.append('missing '+rel); continue
        errors+=html_errors(path.read_text(),rel)
        if path.read_text()!=TARGETS[rel](): errors.append('stale '+rel)
    return errors


def main():
    errors=checks()
    if errors:
        print('\n'.join(errors)); return 1
    print(f'Publication gate passed: {len(PAGES)} pages; source-linked rows, five separated intent records, no fabricated outcomes')
    return 0


if __name__=='__main__': raise SystemExit(main())
