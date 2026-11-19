#!/usr/bin/env python3
"""Build the current buyer publication and review surfaces, not a parallel site.

Facts and intent records: docs/publication.json (fresh, scoped official-source checks).
Historical dashboards and their source ledgers are retained; the deployment projection
adds the shared chrome and marks operator/archive pages noindex without rewriting data.
Run --check to detect output drift. No network or clock is used by this build.
"""
from __future__ import annotations
import sys
from pathlib import Path
import publication
from publication import TARGETS as CURRENT_TARGETS
import build_front_2026_11_19 as retained

# Retain earlier unique guide/desk routes without a second competing homepage.
# Snapshot builder/code and all parallel data remain unchanged.
facts, board = retained.load()
TARGETS = {rel: (lambda fn=fn: fn(facts,board)) for rel,fn in retained.TARGETS if rel not in CURRENT_TARGETS}
TARGETS.update(CURRENT_TARGETS)
load = retained.load

def build_current_summary(_facts=None,_board=None):
    return publication.workroom(rel="summary.html")

TARGETS["summary.html"] = build_current_summary
ROOT = Path(__file__).resolve().parents[1]


def main():
    check = '--check' in sys.argv
    stale = []
    for rel, fn in TARGETS.items():
        want = fn()
        path = ROOT / rel
        if check:
            if not path.is_file() or path.read_text(encoding='utf-8') != want:
                stale.append(rel)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(want, encoding='utf-8')
            print('wrote', rel)
    if stale:
        print('Stale publication outputs: '+', '.join(stale))
        return 1
    print(f'Publication {"current" if check else "built"}: {len(TARGETS)} files')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
