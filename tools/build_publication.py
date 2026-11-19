#!/usr/bin/env python3
"""Build the actual Pages artifact, with one chrome/indexing/link contract.

Keep historical source files and data intact. Deploy this projection rather than the
repository (which previously published conflict markers and build-only files). Every
HTML body keeps its local IDs and evidence; operator/archive pages are noindex,follow,
still linked from the Workroom/footer and never blocked by robots.txt.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from head_meta import BASE, head_block
from publication_policy import INDEXED, CURRENT_OPERATOR
from publication_shell import apply_chrome, depth_for

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
SKIP = {'.git','.github','.local','.cache','node_modules','__pycache__','_site','.venv'}
SUFFIXES = {'.html','.css','.js','.svg','.jpg','.jpeg','.png','.webp','.gif','.woff2','.xml','.txt','.json','.md','.py','.sql'}


class Head(HTMLParser):
    def __init__(self):
        super().__init__(); self.title=''; self.description=''; self.in_title=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='title': self.in_title=True
        if tag=='meta' and a.get('name')=='description': self.description=a.get('content','')
    def handle_endtag(self,tag):
        if tag=='title': self.in_title=False
    def handle_data(self,value):
        if self.in_title: self.title+=value


class Anchor(HTMLParser):
    def __init__(self): super().__init__(); self.a={}
    def handle_starttag(self,tag,attrs):
        if tag=='a': self.a=dict(attrs)


def is_marketplace(url):
    host=(urlsplit(html.unescape(url)).hostname or '').lower()
    return (host in {'link.amazon','amzn.to','www.amazon.com','amazon.com'}
            or bool(re.fullmatch(r'(?:www\.)?amazon\.(?:co\.uk|ca|de|fr|it|es|nl|com\.au|co\.jp|in)',host)))


def sponsored_links(document):
    def patch(match):
        tag=match[0]; p=Anchor(); p.feed(tag)
        if not is_marketplace(p.a.get('href','')): return tag
        rel=set((p.a.get('rel') or '').split())|{'sponsored','nofollow','noopener','noreferrer'}
        value=' '.join(sorted(rel))
        if re.search(r'\brel\s*=',tag,re.I):
            return re.sub(r'\brel\s*=\s*([\"\']).*?\1',f'rel="{value}"',tag,count=1,flags=re.I)
        return tag[:-1]+f' rel="{value}">'
    return re.sub(r'<a\b[^>]*>',patch,document,flags=re.I)


def transform(document,rel):
    h=Head(); h.feed(document.split('</head>',1)[0])
    title=h.title.strip()
    if not title: raise ValueError(f'{rel}: cannot invent a missing title')
    # A missing historical description is transcribed from its existing title, not
    # from new product facts. All current publication pages have their own descriptions.
    desc=h.description.strip() or title
    document=apply_chrome(document,rel)
    document=re.sub(r'<link\b[^>]*rel=[\"\']canonical[\"\'][^>]*>\s*','',document,flags=re.I)
    document=re.sub(r'<meta\b[^>]*(?:property=[\"\']og:[^\"\']+[\"\']|name=[\"\'](?:twitter:card|robots|googlebot)[\"\'])[^>]*>\s*','',document,flags=re.I)
    block=head_block(rel,title=title,description=desc,site_name='Counter Notes', page_type='article' if rel.startswith('guides/products/') or rel in {'guides/basket-or-oven.html','guides/air-fryer-capacity.html','guides/cleanup-and-counter-space.html','guides/multi-function-appliances.html'} else 'website')
    directive='index,follow' if rel in INDEXED else 'noindex,follow'
    document=document.replace('</head>',block+f'\n<meta name="robots" content="{directive}">\n</head>')
    if rel not in INDEXED and rel not in CURRENT_OPERATOR:
        root=depth_for(rel)
        banner=f'<div class="cn-archive" role="note">Retained Workroom record · original dates and verification scope apply. <a href="{root}workroom.html">Read the current executive summary</a> or <a href="{root}index.html">return to the publication</a>.</div>'
        document=document.replace('</aside>', '</aside>'+banner,1)
    if rel=='flagged.html':
        from publication import current_flags
        # Keep the existing flags/data/script/anchors; prepend the current dated flags.
        insert='<section class="cn-wrap cn-section" id="cn-current-flags"><p class="cn-kicker">Current integration · 19 November 2026</p><h2>Flagged for Review</h2>'+current_flags()+'</section>'
        document=re.sub(r'(<main\b[^>]*>)',lambda m:m[1]+insert,document,count=1)
    # New skip link targets the existing main ID where one exists; otherwise a
    # focusable content marker is inserted, leaving legacy IDs/routes untouched.
    if 'class="cn-skip"' not in document:
        document=re.sub(r'(<body\b[^>]*>)',r'\1<a class="cn-skip" href="#cn-content">Skip to content</a>',document,count=1)
        document=document.replace('</aside>','</aside><div id="cn-content" tabindex="-1"></div>',1)
    root=depth_for(rel)
    if 'assets/js/link-policy.js' not in document:
        document=document.replace('</body>',f'<script src="{root}assets/js/link-policy.js" defer></script>\n</body>')
    return sponsored_links(document)


def source_files():
    for base,dirs,files in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith('.'))
        for name in sorted(files):
            path=Path(base)/name
            rel=path.relative_to(ROOT)
            if path.is_symlink(): continue
            if path.suffix.lower() not in SUFFIXES and rel.as_posix()!='.nojekyll': continue
            yield path,rel


def build():
    if OUT.resolve()!=ROOT/'_site': raise ValueError('refusing an unsafe output path')
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    pages=[]
    for path,rel in source_files():
        dest=OUT/rel; dest.parent.mkdir(parents=True,exist_ok=True)
        if path.suffix=='.html':
            dest.write_text(transform(path.read_text(encoding='utf-8'),rel.as_posix()),encoding='utf-8')
            pages.append(rel.as_posix())
        elif path.suffix == '.css':
            # Keep prototype sources intact, but do not initiate Google Fonts
            # requests from an otherwise self-hosted publication artifact.
            css=path.read_text(encoding='utf-8')
            css=re.sub(r"@import\s+url\(['\"]?https://fonts\.googleapis\.com/[^;]+;\s*", '', css)
            dest.write_text(css,encoding='utf-8')
        else:
            shutil.copyfile(path,dest)
    if not INDEXED <= set(pages): raise ValueError('index policy names missing pages: '+str(INDEXED-set(pages)))
    # Preserve the already-shipped feed address, now with the same current items.
    shutil.copyfile(OUT/'feed.xml',OUT/'marketing/feed.xml')
    (OUT/'marketing/robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
    # Legacy sitemap location points to the one authoritative root sitemap.
    for sitemap in OUT.rglob('sitemap.xml'):
        if sitemap == OUT/'sitemap.xml': continue
        sitemap.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>'+BASE+'sitemap.xml</loc></sitemap></sitemapindex>\n')
    (OUT/'.nojekyll').touch()
    report={'html_pages':len(pages),'indexed_pages':sorted(INDEXED),'indexable_count':len(INDEXED),
            'archive_and_operator_noindex':len(pages)-len(INDEXED),'production_analytics':'not_connected',
            'note':'Deployment projection; historical page bodies are retained, not freshly fact-verified.'}
    (OUT/'publication-manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return OUT


if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    build()
