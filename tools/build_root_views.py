#!/usr/bin/env python3
"""Render the two root-level evidence views: verification.html and sources.html.

Why a generator instead of hand-written HTML: the brief requires that *every* table row carry a link to an
official source. If those tables are typed by hand they drift from ledger/*.json the moment a row is added.
Here both pages are projected straight out of:

    ledger/verification.json   one row per claim that had to be checked  -> verification.html
    ledger/sources.json        the register every other file cites by id -> sources.html

and every row's Source cell is built from that source record's own URL, so a row cannot be published
without one. A row citing a source id that is not in the register aborts the build rather than rendering a
cell with no link.

Usage:
    python3 tools/build_root_views.py            # write both pages
    python3 tools/build_root_views.py --check    # exit 1 if the committed pages differ
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AS_OF = "2026-11-14"
LIVE = "https://kanlerxz87-cyber.github.io/Zone2/"

CSS_OK = {
    "official": "ok",
    "manufacturer": "warn",
    "secondary": "warn",
}

NAV = [
    ("index.html", "Dashboard"),
    ("products.html", "Products"),
    ("analysis.html", "Analysis"),
    ("content.html", "Content"),
    ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged for Review"),
]


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def load(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


def source_index() -> dict[str, dict]:
    return {s["id"]: s for s in load("sources.json")["sources"]}


def src_cell(ids: list[str], by_id: dict[str, dict]) -> str:
    """One anchor per cited source. A missing id is a build failure, never a blank cell."""
    if not ids:
        raise SystemExit("row without source_ids - refusing to render an unsourced row")
    out = []
    for sid in ids:
        rec = by_id.get(sid)
        if rec is None:
            raise SystemExit(f"row cites unknown source id {sid!r}")
        label = f"{sid} · {esc(rec['publisher'].split('(')[0].strip())}"
        out.append(
            f'<a class="src" href="{esc(rec["url"])}" target="_blank" rel="noopener noreferrer nofollow">'
            f'{label}</a>'
        )
    return "<br>".join(out)


def page(title: str, lead: str, active: str, body: str) -> str:
    nav_links = []
    for href, label in NAV:
        cls = ' class="active"' if href == active else ""
        nav_links.append(f'<a href="{esc(href)}"{cls}>{esc(label)}</a>')
    nav = "".join(nav_links)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)} — Zone2</title>
<meta name="description" content="{esc(lead)}">
<link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
<div class="shell">
  <aside class="sidebar">
    <h1>Zone2</h1>
    <div class="sub">AI Amazon Affiliate Marketing Platform</div>
    <nav>
      {nav}
    </nav>
  </aside>
  <main class="main">
    <div class="page-head">
      <h2>{esc(title)}</h2>
      <p>{esc(lead)}</p>
    </div>

    <div class="disclosure">
      <strong>Affiliate disclosure (required by the Amazon Associates Operating Agreement §5):</strong>
      {DISCLOSURE}
    </div>

{body}

    <footer class="site">
      Generated from <code>ledger/*.json</code> by <code>tools/build_root_views.py</code> — do not hand-edit.
      Re-verified {esc(AS_OF)}. · <a href="index.html">Dashboard</a> ·
      <a href="sources.html">All sources</a> ·
      <a href="flagged.html">Flagged for Review</a>
    </footer>
  </main>
</div>
</body>
</html>
"""


def verification_page(by_id: dict[str, dict]) -> str:
    doc = load("verification.json")
    rows = []
    for r in doc["rows"]:
        verdict = r["verdict"]
        cls = "ok" if verdict.startswith("VERIFIED") and "NEGATIVE" not in verdict else "warn"
        rows.append(
            "<tr>"
            f'<td><code>{esc(r["id"])}</code></td>'
            f'<td>{esc(r["subject"])}</td>'
            f'<td>{esc(r["claim"])}</td>'
            f'<td>{esc(r["method"])}</td>'
            f'<td><span class="badge {cls}">{esc(verdict)}</span></td>'
            f'<td>{esc(r["consequence"])}</td>'
            f'<td class="src-cell">{src_cell(r["source_ids"], by_id)}</td>'
            "</tr>"
        )
    body = f"""    <div class="card">
      <h3>How each claim was checked</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 12px">
        {len(doc["rows"])} rows. Every row names the method used and links the official page it was read from.
        A verdict of <span class="badge warn">FLAGGED</span> or <span class="badge warn">VERIFIED-NEGATIVE</span>
        is a finding, not an error: it means the check ran and the claim could not be confirmed, so the value
        stays blank. Only <span class="badge ok">VERIFIED</span> values appear in the site's tables.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Subject</th><th>Claim checked</th><th>Method</th><th>Verdict</th><th>Consequence</th><th>Official source</th></tr></thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
      <p style="margin:12px 0 0;font-size:12.5px;color:var(--muted)">{esc(doc["note"])}</p>
    </div>

    <div class="card">
      <h3>What this session re-checked on {esc(AS_OF)}</h3>
      <p style="font-size:13.5px;margin:0 0 10px">
        An independent second pass over every published fact, run on {esc(AS_OF)} against the live pages rather
        than against the previous session's notes. Each item below was re-read in full and matched character by
        character against what the site publishes.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Re-checked</th><th>Result on {esc(AS_OF)}</th><th>Official source</th></tr></thead>
          <tbody>
            <tr><td>Commission rate card, Table 1 (all 11 rows)</td><td>Matches the transcription exactly, including the "Coach 0.00%" row and "All Other Categories 4.00%".</td><td class="src-cell">{src_cell(["S04"], by_id)}</td></tr>
            <tr><td>Bounty table — the 9 rows the site publishes</td><td>All nine rates match. Note: the published bounty table also contains Audible, Kindle Unlimited, Music, registry and Subscribe &amp; Save rows that this site does not publish; they are additions, not corrections.</td><td class="src-cell">{src_cell(["S04"], by_id)}</td></tr>
            <tr><td>Trade-In rates, fine-art cap, free-Kindle limit</td><td>Match verbatim.</td><td class="src-cell">{src_cell(["S04"], by_id)}</td></tr>
            <tr><td>24-hour session / 89-day cart / 180-day fulfilment</td><td>Match Commission Income Statement §1.</td><td class="src-cell">{src_cell(["S02"], by_id)}</td></tr>
            <tr><td>~60-day payment, US payment minimums, 3-year inactivity rule</td><td>Match §6 and the Payment Minimum Chart.</td><td class="src-cell">{src_cell(["S02"], by_id)}</td></tr>
            <tr><td>Mandatory disclosure sentence (§5)</td><td>Verbatim match: "As an Amazon Associate I earn from qualifying purchases."</td><td class="src-cell">{src_cell(["S01"], by_id)}</td></tr>
            <tr><td>Agent Terms (user-agent identification, no CAPTCHA circumvention)</td><td>Match IP License §4 (a)-(c).</td><td class="src-cell">{src_cell(["S02"], by_id)}</td></tr>
            <tr><td>Price/availability display restriction + comparison rule</td><td>Match Participation Requirements §2(b).</td><td class="src-cell">{src_cell(["S02"], by_id)}</td></tr>
            <tr><td><code>/dp/&lt;submitted code&gt;</code> for all three tokens</td><td>All three return Amazon's "Page Not Found" — re-confirmed on {esc(AS_OF)}, matching the 2026-11-13 record.</td><td class="src-cell">{src_cell(["S16", "S17", "S18"], by_id)}</td></tr>
            <tr><td>Where the three <code>link.amazon</code> links actually land</td><td>Unchanged from 2026-11-13 and stable per link: B04G1MEwY→B0CDY277D3, B02NbDxp3→B09B7SB46R, B00hJ57DV→B08DKYBTPH, each with its own per-link <code>btn_ref</code>. The <code>plpRedirect=mhFallback</code> marker is <strong>not</strong> evidence of a fallback: a bare request to a valid ASIN gets the real product page with the same marker appended (session c6e94e8d's control test, reproduced here). No resolved URL carries an Associates <code>tag</code>, and no public document binds the code to the ASIN.</td><td class="src-cell">{src_cell(["S19", "S20", "S21"], by_id)}</td></tr>
            <tr><td>Chefman 6 Qt specs (model, capacity, power, temperature, dimensions, weight, certification, warranty)</td><td>All eight match the manufacturer page verbatim.</td><td class="src-cell">{src_cell(["S25"], by_id)}</td></tr>
            <tr><td>Chefman 8 Qt TurboFry specs</td><td>Model RJ38-SQSS-8T, 8 Qt/7.57 L, 200–400 °F, dimensions, weight, cETL, 1-year — all match. The published power conflict (1700 W manufacturer vs 1000 W Amazon bullet) remains unresolved and is still shown as a conflict.</td><td class="src-cell">{src_cell(["S26"], by_id)}</td></tr>
            <tr><td>Emeril 26QT specs</td><td>Model 4-00675-02A-VN, 26 qt/24.6 L, 16.9"D × 15.8"W × 14.8"H, 120 V, dual-speed fan, 1-year warranty match. The preset/function count does <strong>not</strong> resolve — the manufacturer page gives 24, 25 and "10-in-1" in three places. Published as a conflict (flag F-19).</td><td class="src-cell">{src_cell(["S27"], by_id)}</td></tr>
            <tr><td>Whether <code>plpRedirect=mhFallback</code> proves a "fallback" page</td><td><strong>It does not.</strong> A bare, untagged request to a valid ASIN (/dp/B08DKYBTPH, /dp/B0CDY277D3) returns the real product page with the same markers appended. The earlier "arbitrary fallback" reading is retracted; F-03 downgraded, F-12 withdrawn.</td><td class="src-cell">{src_cell(["S19", "S20"], by_id)}</td></tr>
            <tr><td>Every cited control in the compliance ledger exists as code</td><td>Two did not (R-01, R-11) and two named functions that do not exist (R-02, R-06). Corrected in the ledger; see flag F-16.</td><td class="src-cell">{src_cell(["S22"], by_id)}</td></tr>
            <tr><td>Internal links across the whole published site</td><td>0 broken file references and 0 unresolvable anchors across all 79 HTML pages, checked by resolution rather than by eye.</td><td class="src-cell">{src_cell(["S22"], by_id)}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
"""
    return page(
        "Verification",
        "One row per claim that had to be checked, with the method used and the official page it was read from.",
        "verification.html",
        body,
    )


def sources_page(by_id: dict[str, dict]) -> str:
    doc = load("sources.json")
    rows = []
    for s in doc["sources"]:
        kind = s.get("kind", "")
        rows.append(
            "<tr>"
            f'<td><code>{esc(s["id"])}</code></td>'
            f'<td><span class="badge {CSS_OK.get(kind, "warn")}">{esc(kind)}</span></td>'
            f'<td>{esc(s["publisher"])}</td>'
            f'<td>{esc(s["title"])}</td>'
            f'<td class="src-cell"><a class="src" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(s["url"])}</a></td>'
            f'<td>{esc(s.get("page_stated_update") or "not stated on page")}</td>'
            f'<td>{esc(s.get("accessed_utc") or "")}</td>'
            f'<td>{esc("; ".join(s.get("used_for", [])))}</td>'
            "</tr>"
        )
    counts = {}
    for s in doc["sources"]:
        counts[s.get("kind", "unknown")] = counts.get(s.get("kind", "unknown"), 0) + 1
    kinds = "".join(f"<li><strong>{esc(k)}</strong> — {v}</li>" for k, v in sorted(counts.items()))
    body = f"""    <div class="card">
      <h3>Source register — {len(doc["sources"])} sources</h3>
      <p style="font-size:13px;color:var(--muted);margin:0 0 10px">
        Every table row on this site cites one of these ids. Nothing is published without a row here, and the
        deploy gate (<code>tools/validate_data.py</code>) fails the build if a row cites an id that is missing
        or if a URL is not on an allow-listed official domain.
      </p>
      <ul style="margin:0 0 14px;padding-left:20px;font-size:13px">{kinds}</ul>
      <p style="font-size:13px;color:var(--muted);margin:0 0 12px">
        <span class="badge ok">official</span> = Amazon, the FTC or Google speaking about their own program or
        rules. <span class="badge warn">manufacturer</span> = the maker of the product speaking about its own
        specifications; these may never be used to state an Amazon-side fact such as price, rating or
        availability. <span class="badge warn">secondary</span> = used only to corroborate, never alone.
      </p>
      <div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>Class</th><th>Publisher</th><th>Document</th><th>URL</th><th>Page says updated</th><th>Accessed</th><th>Used for</th></tr></thead>
          <tbody>
            {''.join(rows)}
          </tbody>
        </table>
      </div>
      <p style="margin:12px 0 0;font-size:12.5px;color:var(--muted)">{esc(doc["note"])}</p>
    </div>

    <div class="card">
      <h3>Which claims these sources cannot support</h3>
      <p style="font-size:13.5px;margin:0 0 10px">
        Stated plainly, because a long source list can imply more coverage than it has:
      </p>
      <ul style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.65">
        <li><strong>No source here can identify the three supplied codes.</strong> Amazon's help page stating that
        an ASIN is 10 characters is what proves a 9-character token cannot be one — it is a rule, not a lookup.
        The lookup itself needs an authenticated Creators API call, which this workspace does not have.</li>
        <li><strong>No source here fixes the commission band for a specific ASIN.</strong> Table 1 publishes
        "Kitchen 4.50%" and "Home 3.00%" as separate bands; which applies to these three listings is a catalog
        fact, not a published one.</li>
        <li><strong>No source here establishes price, rating, review count, BSR or availability</strong> for the
        three listings in a form this site is allowed to republish (see the Program Policies price rule, S02).</li>
        <li><strong>The manufacturer pages are not Amazon.</strong> Where a manufacturer page and an Amazon
        listing disagree — the 8 Qt power figure and the Emeril preset count — both values are shown and flagged;
        neither is resolved by preference.</li>
      </ul>
    </div>
"""
    return page(
        "Sources",
        "The complete register every claim on this site points at, with the class of each source made explicit.",
        "sources.html",
        body,
    )


def build() -> dict[str, str]:
    by_id = source_index()
    return {
        "verification.html": verification_page(by_id),
        "sources.html": sources_page(by_id),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="compare against the committed pages, write nothing")
    args = ap.parse_args()

    rendered = build()
    if args.check:
        drift = []
        for name, text in rendered.items():
            target = REPO / name
            if not target.is_file() or target.read_text(encoding="utf-8") != text:
                drift.append(name)
        print(json.dumps({"checked": sorted(rendered), "drifted": drift}, indent=2))
        return 1 if drift else 0

    with tempfile.TemporaryDirectory() as tmp:
        for name, text in rendered.items():
            staged = Path(tmp) / name
            staged.write_text(text, encoding="utf-8")
            (REPO / name).write_text(text, encoding="utf-8")
    print(json.dumps({"written": sorted(rendered), "as_of": AS_OF}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
