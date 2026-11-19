"""Source-tree measurements shared by register renderers and gates.

Never count the generated deployment bundle, private runtime/browser dependencies,
or a bare tag string in prose as a published tagged link.
"""
from __future__ import annotations
import os
from functools import lru_cache
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

SKIP_DIRS={'.git','.github','.local','.cache','_site','node_modules','__pycache__','.venv'}


def source_html(root: Path):
    for base,dirs,files in os.walk(root):
        dirs[:]=sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.'))
        for name in sorted(files):
            if name.endswith('.html'):
                yield Path(base)/name


class Links(HTMLParser):
    def __init__(self): super().__init__();self.tagged=False
    def handle_starttag(self,tag,attrs):
        if tag!='a': return
        a=dict(attrs); u=urlsplit(a.get('href',''))
        if u.scheme not in {'https','http'} or (u.hostname or '').lower() not in {'amazon.com','www.amazon.com'}: return
        value=parse_qs(u.query).get('tag',[])
        if len(value)==1 and re.fullmatch(r'[A-Za-z0-9]+-\d{2}',value[0]): self.tagged=True


@lru_cache(maxsize=384)
def has_tagged_link(document: str) -> bool:
    if not re.search(r'tag=|%[0-9A-Fa-f]{2}', document):
        return False
    p=Links();p.feed(document);return p.tagged


def brief_pages(root):
    return [p for p in source_html(root) if p.name!='404.html'
            and p.relative_to(root).parts[0]!='brief'
            and p.relative_to(root).as_posix()!='release/index.html']


def brief_measure(root):
    pages=brief_pages(root)
    documents=[p.read_text(encoding='utf-8') for p in pages]
    from price_policy import context_units
    # Same buying/program context rule as the canonical dataset validator.
    from validate_data import MONEY, PRICE_CONTEXT, PROGRAM_CONTEXT
    def priced(text):
        return any(MONEY.search(unit) and PRICE_CONTEXT.search(unit) and not PROGRAM_CONTEXT.search(unit)
                   for unit in context_units(text))
    namespaces={p.relative_to(root).parts[0] if len(p.relative_to(root).parts)>1 else '(root)'
                for p in source_html(root) if p.name!='404.html'}
    return {'published':len(pages),
            'with_disclosure':sum('As an Amazon Associate I earn from qualifying purchases.' in t for t in documents),
            'with_tag':sum(has_tagged_link(t) for t in documents),
            'ai_powered_pages':sum('AI-powered' in t for t in documents),
            'price_pages':sum(priced(t) for t in documents),
            'surfaces':len(namespaces)}
