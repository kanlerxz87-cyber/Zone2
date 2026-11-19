#!/usr/bin/env python3
"""Serve the actual Pages artifact to a real browser using a temporary counter DB.

No production credentials, API calls, campaign rows or external affiliate navigation.
Install QA-only npm dependencies with `npm ci --prefix tools/browser --ignore-scripts`.
"""
from __future__ import annotations
import json
import os
import subprocess
import tempfile
import threading
from pathlib import Path
from analytics_server import make_server

ROOT=Path(__file__).resolve().parents[1]


def main():
    if not (ROOT/'_site/index.html').is_file():
        raise SystemExit('Build the deployment artifact first: python tools/build_publication.py')
    with tempfile.TemporaryDirectory() as temp:
        server=make_server(host='127.0.0.1',port=0,origins=['http://localhost'],
                           db_path=Path(temp)/'isolated.sqlite3',site_root=ROOT/'_site')
        origin=f'http://127.0.0.1:{server.server_port}'
        server.origins.add(origin)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            result=subprocess.run(['node','tools/browser/smoke.cjs'],cwd=ROOT,
                                  env={**os.environ,'CN_TEST_ORIGIN':origin},timeout=300)
            if result.returncode:return result.returncode
            rows=server.store.export()['daily_events']
            names={r['name'] for r in rows}
            if names!={'page_view','product_link_click','disclosure_view'}:
                print(json.dumps({'unexpected_isolated_events':rows},indent=2));return 1
            print('Browser public-event persistence verified in a temporary DB; no campaign/report data created.')
        finally:
            server.shutdown();server.server_close();thread.join(timeout=5)
    return 0


if __name__=='__main__':raise SystemExit(main())
