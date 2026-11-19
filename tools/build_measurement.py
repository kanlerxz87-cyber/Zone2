#!/usr/bin/env python3
"""Render the original five-event register with ACTUAL implementation/deployment states.

Current contract: docs/measurement-t40.json. Earlier versions remain in Git history.
A runnable counter is not a deployment; a client queue is not durable measurement.
Run python3 tools/build_measurement.py [--check].
"""
from __future__ import annotations
import html
import json
import sys
from pathlib import Path
import build_discovery as bd

REPO=Path(__file__).resolve().parents[1]
OUT=REPO/'discovery/measurement.html'
DATA=json.loads((REPO/'docs/measurement-t40.json').read_text())
DISCLOSURE=bd.DISCLOSURE


def esc(value):
    return html.escape(str(value),quote=True)


def page():
    events=''.join(f'<tr id="{esc(ev["id"])}"><th scope="row">{esc(ev["id"])}<br><code>{esc(ev["name"])}</code></th><td><strong>{esc(ev["status"])}</strong><br>{esc(ev["fires_on"])}<p>{esc(ev["persistence"])}</p></td><td>{"<br>".join(esc(f) for f in ev["fields"])}<p>Not collected: {esc("; ".join(ev["deliberately_not_collected"]))}</p></td><td>{esc(ev["decides"])}<p>Blocker: {esc(ev["blocked_by"])}</p></td>{bd.source_cell(ev["source_ids"])}</tr>' for ev in DATA['events'])
    principles=''.join(f'<tr id="{esc(p["id"])}"><th scope="row">{esc(p["id"])}</th><td><strong>{esc(p["rule"])}</strong><p>{esc(p["why"])}</p></td>{bd.source_cell(p["source_ids"])}</tr>' for p in DATA['principles'])
    decisions=''.join(f'<tr id="{esc(d["id"])}"><th scope="row">{esc(d["id"])}<br>{esc(d["decision"])}</th><td>{esc(d["rule"])}</td><td>{esc(", ".join(d["needs"]))}</td><td>Unavailable: no production history or authorized report</td>{bd.source_cell(["S58"])}</tr>' for d in DATA['decisions_enabled'])
    gaps=''.join(f'<li id="{esc(g["id"])}"><strong>{esc(g["id"])}</strong> {esc(g["item"])} <small>Limits {esc(g["blocks"])}.</small></li>' for g in DATA['open_items'])
    body=f'''<h1>The five-event contract: implemented is not deployed</h1><p class="lede">Updated 19 November 2026. A same-origin collector and authorized-report importers are implemented. Production GitHub Pages collection is disabled because static Pages cannot run the writable endpoint. No real report has been supplied.</p><div class="note"><p><strong>Current release:</strong> <a href="../measurement.html">measurement & campaign ledger</a> · <a href="../privacy.html">privacy notice</a> · <a href="../measurement/README.md">run/deploy documentation</a>. Earlier wording called a browser-only queue LIVE. That did not establish durable collection; the queue is removed. A sandbox preview is explicitly test data, not production activity.</p></div><h2>Measurement principles</h2><div class="tablewrap"><table><caption>Engineering rules and official context—not a blanket legal assurance.</caption><thead><tr><th>ID</th><th>Rule and limitation</th><th>Official source</th></tr></thead><tbody>{principles}</tbody></table></div><h2>Five defined events</h2><div class="tablewrap"><table><caption>Implementation, persistence, availability and official rule context are separate.</caption><thead><tr><th>Event</th><th>Actual state / trigger</th><th>Fields / exclusions</th><th>Decision / blocker</th><th>Official context</th></tr></thead><tbody>{events}</tbody></table></div><h2>What evidence would support decisions?</h2><div class="tablewrap"><table><caption>No authorized performance observation is currently available.</caption><thead><tr><th>Decision</th><th>Interpretation limit</th><th>Events needed</th><th>Available evidence</th><th>Official rule context</th></tr></thead><tbody>{decisions}</tbody></table></div><h2>Deployment and report gaps</h2><ul>{gaps}</ul><h2>Privacy and consent, stated carefully</h2><p>{esc(DATA['privacy_and_consent']['position'])}</p><p>{esc(DATA['privacy_and_consent']['what_is_asserted'])}</p><div class="note"><p>{esc(DATA['privacy_and_consent']['what_is_not_asserted'])}</p></div><p>The earlier decision <a href="suggestions.html#DS-11">DS-11</a> remains traceable. Current hosting alternatives are reviewable on <a href="../suggestions.html#S63-02">S63-02</a>; selecting an option does not provision infrastructure.</p>'''
    return bd.page('Measurement contract','Five implemented event contracts, disabled production collection, authorized-report gates and a separate deployment state.',body,here='measurement.html',crumbs=[('index.html','Overview'),('measurement.html','Measurement contract')])


def build():
    doc=page()
    if DISCLOSURE not in doc:raise SystemExit('Missing disclosure')
    return doc


def main(argv=None):
    check='--check' in (sys.argv[1:] if argv is None else argv)
    doc=build()
    if check:
        stale=not OUT.is_file() or OUT.read_text()!=doc
        print(json.dumps({'out':'discovery/measurement.html','stale':stale}))
        return int(stale)
    OUT.write_text(doc)
    print('Updated discovery/measurement.html: five events, production OFF')
    return 0


if __name__=='__main__':raise SystemExit(main())
