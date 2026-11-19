#!/usr/bin/env python3
"""Verify the actual deployment artifact, not just a source-tree approximation."""
from __future__ import annotations
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from head_meta import BASE
from publication_policy import INDEXED
from publication_shell import DISCLOSURE
from build_publication import is_marketplace

ROOT=Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.refs=[]; self.ids=set(); self.routes=set(); self.canonical=[]; self.robots=[]; self.products=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if 'data-page' in a: self.routes.add(a['data-page'])
        if tag=='meta' and a.get('name')=='robots': self.robots.append(a.get('content',''))
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a.get('href'))
        if tag=='a' and is_marketplace(a.get('href','')): self.products.append(a)
        if tag=='a' and a.get('href'): self.refs.append((a['href'],True))
        if tag=='link' and a.get('href') and a.get('rel') in {'stylesheet','icon','alternate'}: self.refs.append((a['href'],False))
        if tag in {'img','script'} and a.get('src'): self.refs.append((a['src'],False))


def validate(root):
    problems=[]; parsed={}; documents={}
    for f in sorted(root.rglob('*.html')):
        rel=f.relative_to(root).as_posix(); text=f.read_text(); p=Page();p.feed(text)
        parsed[rel]=p;documents[rel]=text
        if text.count(DISCLOSURE)<2: problems.append(rel+': disclosure missing at masthead/footer')
        if 'data-disclosure-strip' not in text or 'data-cn-shell="v1"' not in text: problems.append(rel+': common shell missing')
        if '<main' in text and text.find(DISCLOSURE)>text.find('<main'): problems.append(rel+': disclosure below main content')
        want=BASE+('' if rel=='index.html' else rel)
        if p.canonical!=[want]: problems.append(rel+': canonical must be singular and self-referencing')
        robots='index,follow' if rel in INDEXED else 'noindex,follow'
        if p.robots!=[robots]: problems.append(rel+': indexing policy mismatch')
        for a in p.products:
            if not {'sponsored','nofollow','noopener','noreferrer'}<=set(a.get('rel','').split()): problems.append(rel+': marketplace link not sponsored')
        if re.search(r'^(?:<<<<<<<|=======|>>>>>>>)',text,re.M): problems.append(rel+': unresolved merge marker')
    for rel,p in parsed.items():
        for ref,fragment in p.refs:
            u=urlsplit(ref)
            if u.scheme or ref.startswith('//'): continue
            path=unquote(u.path)
            target=((root/rel).parent/path).resolve() if path else root/rel
            if path.endswith('/'): target/='index.html'
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                problems.append(f'{rel}: broken local reference {ref}'); continue
            if fragment and u.fragment and target.suffix=='.html':
                key=target.relative_to(root).as_posix(); dest=parsed.get(key)
                if dest and u.fragment.lower() not in {x.lower() for x in dest.ids} and u.fragment not in dest.routes:
                    problems.append(f'{rel}: broken fragment {ref}')
    if not INDEXED <= set(parsed): problems.append('index policy points at missing pages')
    try:
        locs=[x.text for x in ET.parse(root/'sitemap.xml').findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
        expected={BASE+('' if p=='index.html' else p) for p in INDEXED}
        if len(locs)!=len(set(locs)) or set(locs)!=expected: problems.append('sitemap must list exactly the selected publication pages')
        for name in ['feed.xml','marketing/feed.xml']:
            feed=ET.parse(root/name)
            for item in feed.findall('./channel/item'):
                url=item.findtext('link') or ''
                if not url.startswith(BASE) or url.removeprefix(BASE) not in parsed: problems.append(name+': item does not resolve')
                from email.utils import parsedate_to_datetime
                try: parsedate_to_datetime(item.findtext('pubDate'))
                except (ValueError,TypeError): problems.append(name+': invalid RSS date')
    except (OSError,ET.ParseError) as exc: problems.append('XML failure: '+str(exc))
    config=(root/'assets/js/measurement-config.js').read_text()
    if not re.search(r'enabled:\s*false',config) or not re.search(r'endpoint:\s*""',config): problems.append('Pages must not falsely enable a nonexistent collector')
    return problems,{'html_pages':len(parsed),'indexable_pages':len(INDEXED),'marketplace_links':sum(len(p.products) for p in parsed.values())}


def main():
    root=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'_site'
    if not root.is_dir(): print('Build the artifact first: python tools/build_publication.py');return 1
    root=root.resolve(); problems,stats=validate(root)
    print(json.dumps({'ok':not problems,'stats':stats,'problems':problems},indent=2))
    return bool(problems)


if __name__=='__main__':raise SystemExit(main())
