#!/usr/bin/env python3
"""Publish the measurement design as a decision surface.

Why this page exists
--------------------
The brief asks for a platform that "tracks clicks and conversions, and continuously
optimizes campaigns". Nothing is tracked, and the site's own validator refuses a
populated click or conversion field. That gap is honest but not actionable: an owner
cannot choose a measurement plan from the sentence "no data exists".

This renders `docs/measurement-t40.json` as the plan: every event, what it would let
the owner decide, what it deliberately does not collect, and what blocks it. Nothing
is implemented by publishing it, and the page says so above the first table.

The most important row is EV-04. Conversion data can only come from Associates
reporting, which needs an account. Any number this project could compute in place of
that would be invented, so the row stays BLOCKED and the table stays empty.

Run: python3 tools/build_measurement.py [--check]
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "discovery" / "measurement.html"
DATA_PATH = REPO / "docs" / "measurement-t40.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_discovery as bd  # noqa: E402  reuse the shell, NAV and source register

DATA = json.loads(DATA_PATH.read_text(encoding="utf-8"))
DISCLOSURE = bd.DISCLOSURE
AS_OF = DATA["as_of"]

STATUS_PILL = {
    "DESIGNED": "pill-warn",
    "BLOCKED": "pill-bad",
    "LIVE": "pill-ok",
}


def esc(v) -> str:
    return html.escape(str(v), quote=True)


def status_pill(s: str) -> str:
    return f'<span class="pill {STATUS_PILL.get(s, "pill")}">{esc(s)}</span>'


def source_cell(ids) -> str:
    return bd.source_cell(ids)


def page() -> str:
    events = "".join(
        f'<tr id="{esc(e["id"])}">'
        f'<td class="id">{esc(e["id"])}<div class="note-sm">{status_pill(e["status"])}</div></td>'
        f'<td><code>{esc(e["name"])}</code>'
        f'<div class="note-sm"><strong>Fires on:</strong> {esc(e["fires_on"])}</div>'
        f'<div class="note-sm"><strong>Would decide:</strong> {esc(e["decides"])}</div></td>'
        f'<td>{"".join(f"<code>{esc(f)}</code><br>" for f in e["fields"])}'
        f'<div class="note-sm"><strong>Not collected on purpose:</strong> '
        f'{esc("; ".join(e["deliberately_not_collected"]))}</div></td>'
        f'<td>{esc(e.get("blocked_by", "—"))}</td></tr>'
        for e in DATA["events"]
    )

    principles = "".join(
        f'<tr id="{esc(p["id"])}">'
        f'<td class="id">{esc(p["id"])}</td>'
        f'<td><strong>{esc(p["rule"])}</strong>'
        f'<div class="note-sm">{esc(p["why"])}</div></td>'
        f'{source_cell(p["source_ids"])}</tr>'
        for p in DATA["principles"]
    )

    decisions = "".join(
        f'<tr id="{esc(d["id"])}">'
        f'<td class="id">{esc(d["id"])}</td>'
        f'<td><strong>{esc(d["decision"])}</strong>'
        f'<div class="note-sm">{esc(d["rule"])}</div></td>'
        f'<td>{esc(", ".join(d["needs"]))}</td>'
        f'<td><span class="pill pill-bad">no data</span></td></tr>'
        for d in DATA["decisions_enabled"]
    )

    gaps = "".join(
        f'<li id="{esc(g["id"])}"><strong>{esc(g["id"])}</strong> — {esc(g["item"])} '
        f'<span class="note-sm">Affects {esc(g["blocks"])}</span></li>'
        for g in DATA["open_items"]
    )

    body = f"""
<h1>What could be measured, and what it would let you decide</h1>
<p class="lede">The platform claims to track clicks and conversions and optimize campaigns. It tracks nothing.
That is not laziness: with no tagged link, no analytics and no Associates account there is nothing to track, and
the site's own validator refuses an invented number. This page is the plan that would change it — every event,
the decision it supports, and what blocks it.</p>

<div class="note">
  <p><strong>Nothing on this page is implemented.</strong> Every event below is marked DESIGNED or BLOCKED, never
  LIVE. There is no script, no endpoint, no cookie and no account behind any row. The build fails if an event is
  ever marked LIVE while the suggestion that authorises it
  (<a href="suggestions.html#DS-11">DS-11</a>) still carries no recorded decision.</p>
</div>

<h2>The rules a measurement layer has to survive</h2>
<p>Written first, because they rule out most of the obvious designs. Each is anchored to the official page that
constrains it.</p>
<div class="tablewrap">
  <table>
    <caption>From <code>docs/measurement-t40.json</code>. A design that violates one of these is not
    implemented, however useful the data would be.</caption>
    <thead><tr><th>ID</th><th>Rule</th><th>Official source</th></tr></thead>
    <tbody>{principles}</tbody>
  </table>
</div>

<h2>The events</h2>
<div class="tablewrap">
  <table>
    <caption>The last column is the honest one. An event that cannot fire today says why.</caption>
    <thead><tr><th>ID</th><th>Event and the decision it supports</th><th>Fields, and what is refused</th><th>Blocked by</th></tr></thead>
    <tbody>{events}</tbody>
  </table>
</div>

<h2>What each measurement would let you decide</h2>
<div class="tablewrap">
  <table>
    <caption>Every row reads "no data" today. That column is the point of this page.</caption>
    <thead><tr><th>ID</th><th>Decision</th><th>Needs</th><th>Available today</th></tr></thead>
    <tbody>{decisions}</tbody>
  </table>
</div>

<h2>What is still unresolved before anything could be collected</h2>
<ul>{gaps}</ul>

<h2>Privacy, stated carefully</h2>
<p>{esc(DATA["privacy_and_consent"]["position"])}</p>
<p>{esc(DATA["privacy_and_consent"]["what_is_asserted"])}</p>
<div class="note">
  <p><strong>What this page does not claim.</strong> {esc(DATA["privacy_and_consent"]["what_is_not_asserted"])}</p>
</div>

<h2>The honest position today</h2>
<p>Until an Associates account exists, the answer to "is this working" is <em>unknown</em>, and the site should
say so rather than print a number that looks like an answer. The one thing a cookie-free counter would change
before an account exists is narrower and still worth having: it would say which page sends people to which
product, which is the only input needed to decide what to write next.</p>
<p>That choice is <a href="suggestions.html#DS-11">DS-11</a>. Its options are a cookie-free first-party counter,
a third-party analytics script, or waiting for Associates reporting alone — and the trade-offs are stated on the
row.</p>
"""
    return bd.page(
        "Measurement plan",
        "What this site could measure, the decision each measurement supports, what it refuses to collect, and what "
        "blocks it — nothing implemented, every event marked DESIGNED or BLOCKED.",
        body,
        here="measurement.html",
        crumbs=[("index.html", "Overview"), ("measurement.html", "Measurement plan")],
    )


def build() -> str:
    doc = page()
    if DISCLOSURE not in doc:
        raise SystemExit("measurement.html: missing the required Site disclosure")
    return doc


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    doc = build()
    if check:
        stale = not OUT.is_file() or OUT.read_text(encoding="utf-8") != doc
        print(json.dumps({"out": "discovery/measurement.html", "stale": stale}, indent=2))
        return 1 if stale else 0
    OUT.write_text(doc, encoding="utf-8")
    n = len(DATA["events"])
    live = sum(1 for e in DATA["events"] if e["status"] == "LIVE")
    print(json.dumps({"out": "discovery/measurement.html", "events": n, "live": live}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
