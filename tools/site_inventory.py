"""Source-tree inventory for the earlier design brief; NOT deployed artifact metrics.

The exclusions are explicit and shared by the generator and validator. The deployed
publication is checked separately by verify_publication.py, after the archive transform.
"""
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
DISCLOSURE='As an Amazon Associate I earn from qualifying purchases.'
SKIP={'.git','.github','__pycache__','node_modules','.local','_site'}
TAG=re.compile(r'[?&]tag=[A-Za-z0-9]+-[0-9]{2}\b')


def pages(root=ROOT):
    return [p for p in sorted(root.rglob('*.html')) if not any(part in SKIP for part in p.relative_to(root).parts) and p.name!='404.html' and p.relative_to(root).parts[0]!='brief' and p.relative_to(root)!=Path('release/index.html')]


def measure(root=ROOT):
    docs=pages(root)
    texts=[p.read_text(encoding='utf-8') for p in docs]
    return {
        'published':len(docs),
        'with_disclosure':sum(DISCLOSURE in s for s in texts),
        'with_tag':sum(bool(TAG.search(s)) for s in texts),
        'ai_powered_pages':sum('AI-powered' in s for s in texts),
        'price_pages':sum(bool(re.search(r'\$\s?\d',s)) and 'bounty' not in s.lower() and 'commission' not in s.lower() for s in texts),
        'surfaces':len({(p.relative_to(root).parts[0] if len(p.relative_to(root).parts)>1 else '(root)') for p in root.rglob('*.html') if p.name!='404.html' and not any(part in SKIP for part in p.relative_to(root).parts)})
    }
