#!/usr/bin/env python3
"""Stage the ACTUAL Pages artifact, enforcing one reader publication globally.

Research generators retain reproducible, dated evidence. The deployment transform is
separate and deterministic: all product anchors sponsored, all archives noindex,
all pages disclosed twice, self-canonicals, and only reader pages in the root sitemap.
Only _site is uploaded; never upload the checkout, private SQLite data or .git.
"""
from __future__ import annotations
import argparse
import html
import json
import subprocess
import os
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from head_meta import BASE
import publication as pub

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
SKIP = {'.git','.github','.local','.cache','_site','node_modules','__pycache__','.venv','.pytest_cache','tests','test-results','playwright-report'}
EXTENSIONS = {'.html','.css','.js','.json','.xml','.txt','.svg','.jpg','.jpeg','.png','.webp','.gif','.woff','.woff2','.ico','.md','.csv','.pdf','.py','.sql'}
CURRENT = pub.indexable_paths() | set(pub.extra_pages()) | {'suggestions.html','questions.html','guides/basket-air-fryers.html','guides/air-fryer-ovens.html','guides/buying-guides.html','guides/method.html'}


class Anchor(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.attrs={}
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.attrs=dict(attrs)


def is_product_url(value):
    try:
        return urlsplit(value).hostname in {'amazon.com','www.amazon.com','link.amazon','amzn.to'}
    except ValueError:
        return False


def sponsor_anchors(doc):
    def replace(match):
        raw=match.group(0)
        parsed=Anchor(raw)
        if not is_product_url(parsed.attrs.get('href','')):
            return raw
        rel=set((parsed.attrs.get('rel') or '').split()) | {'sponsored','nofollow','noopener'}
        # Do not deliberately suppress the referring site on product links.
        rel.discard('noreferrer')
        value=' '.join(name for name in ('sponsored','nofollow','noopener') if name in rel)
        value+=''.join(' '+name for name in sorted(rel-{'sponsored','nofollow','noopener'}))
        attr='rel="'+html.escape(value,quote=True)+'"'
        pattern=r'(?<![\w-])rel\s*=\s*(?:"[^"]*"|\x27[^\x27]*\x27)'
        if re.search(pattern,raw,re.I):
            return re.sub(pattern,attr,raw,count=1,flags=re.I)
        return raw[:-1]+' '+attr+'>'
    # A literal <a> inside JavaScript is data, not an HTML token. Rewriting it
    # can break quoting or template syntax. Runtime-generated links are covered
    # by the small archive-links observer inserted before archived scripts run.
    segments=re.split(r'(<(?:script|style)\b[^>]*>.*?</(?:script|style)\s*>)',doc,flags=re.I|re.S)
    return ''.join(segment if re.match(r'<(?:script|style)\b',segment,re.I) else re.sub(r'<a\b[^>]*>',replace,segment,flags=re.I) for segment in segments)


def transform(doc, rel):
    depth=pub.prefix(rel)
    indexable=rel in pub.indexable_paths()
    # A self-canonical does not pretend unrelated historical evidence duplicates the home page.
    doc=re.sub(r'<link\b(?=[^>]*\brel\s*=\s*["\x27]canonical["\x27])[^>]*>\s*','',doc,flags=re.I)
    doc=re.sub(r'<meta\b(?=[^>]*\bname\s*=\s*["\x27]robots["\x27])[^>]*>\s*','',doc,flags=re.I)
    meta=f'<link rel="canonical" href="{BASE + ("" if rel=="index.html" else rel)}">\n<meta name="robots" content="{("index,follow" if indexable else "noindex,follow")}">\n'
    if rel not in CURRENT and '<body class="cn-publication">' not in doc:
        meta+=f'<link rel="stylesheet" href="{depth}assets/css/publication.css">\n'
        # Keep the archived source content intact; only replace a pre-main masthead.
        old=re.search(r'<header\b[^>]*>.*?</header>',doc,re.S|re.I)
        main=re.search(r'<main\b',doc,re.I)
        if old and (not main or old.start()<main.start()):
            doc=doc[:old.start()]+doc[old.end():]
        banner=f'<div class="cn-archive-banner"><div class="cn-wrap"><span>Dated research archive · earlier implementation states may have changed.</span><a href="{depth}executive-summary.html">Read the current release summary →</a></div></div>'
        header=pub.masthead(rel)+banner+f'<script src="{depth}assets/js/archive-links.js"></script><script src="{depth}assets/js/publication.js" defer></script>'
        doc=re.sub(r'(<body\b[^>]*>)',lambda m:m.group(1)+'\n'+header,doc,count=1,flags=re.I)
        foot=f'<div class="cn-archive-footer"><strong>{pub.DISCLOSURE}</strong> <a href="{depth}workspace.html">All workspace tools</a> · <a href="{depth}index.html">Counter Notes publication</a> · <a href="{depth}privacy.html">Current privacy notice</a></div>'
        doc=re.sub(r'</body>',lambda m:foot+'\n'+m.group(0),doc,count=1,flags=re.I)
        doc=re.sub(r'<script\b[^>]*src=["\x27][^"\x27]*assets/js/events\.js["\x27][^>]*>\s*</script>','',doc,flags=re.I)
    doc=re.sub(r'</head>',lambda m:meta+m.group(0),doc,count=1,flags=re.I)
    return sponsor_anchors(doc)


def source_files():
    for directory,dirs,files in os.walk(ROOT):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith('.'))
        parent=Path(directory)
        rel_dir=parent.relative_to(ROOT)
        for name in sorted(files):
            path=parent/name
            if path.is_symlink() or name.startswith('.'):
                continue
            rel=path.relative_to(ROOT)
            if rel.parts[0]=='measurement' and rel.as_posix()!='measurement/README.md':
                continue
            if path.suffix.lower() not in EXTENSIONS:
                continue
            if path.suffix.lower() in {'.sqlite3','.log'}:
                continue
            yield path, rel


def build(out=OUT):
    out=out.resolve()
    # Never delete a caller-selected path. Cleanup is constrained to our own known staging dir.
    if out != OUT.resolve():
        raise ValueError('Only the repository _site staging path may be replaced')
    if out.exists():
        shutil.rmtree(out)
    out.mkdir()
    pages=0
    for src,rel in source_files():
        target=out/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        if src.suffix=='.html':
            target.write_text(transform(src.read_text(encoding='utf-8'),rel.as_posix()),encoding='utf-8')
            pages+=1
        elif rel.name=='sitemap.xml' and rel.parts[0]!='sitemap.xml':
            target.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>'+BASE+'sitemap.xml</loc></sitemap></sitemapindex>\n')
        elif rel.name=='feed.xml' and len(rel.parts)>1:
            target.write_text(pub.feed(),encoding='utf-8')
        else:
            shutil.copyfile(src,target)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if not re.fullmatch(r'[0-9a-f]{40}',commit):
        raise ValueError('Cannot identify source checkout commit for the deployment artifact')
    (out/'publication-build.json').write_text(json.dumps({'schema':'counter-notes-build-v1','commit':commit},sort_keys=True)+'\n')
    (out/'.nojekyll').write_text('')
    return pages


def main():
    n=build()
    print(f'Packaged {n} HTML pages into _site; {len(pub.indexable_paths())} reader URLs indexable, evidence archives retained as noindex.')


if __name__=='__main__':main()
