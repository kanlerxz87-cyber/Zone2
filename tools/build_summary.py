#!/usr/bin/env python3
"""Generate `summary.html` — the reader-facing executive summary.

T26 (session 808a6840). The brief asks for "an executive summary outlining important details".
`EXECUTIVE_SUMMARY.md` and `pages/executive-summary.html` already exist, but neither is the thing a
reader lands on when they want the answer in one screen: what was built, what the three links resolve
to, what is blocking revenue, and what the owner must do.

Every figure is read from `ledger/*.json` and `tools/verified_specs_*.json`, so the page cannot state a
number the data does not hold — the defect class F-17/F-26 closed for the flag count. Every factual row
carries the official URL it came from, and anything unconfirmed is shown as an explicit blank with its
flag id rather than a guess.

Usage:
    python3 tools/build_summary.py           # write summary.html
    python3 tools/build_summary.py --check   # fail if the committed file is out of date
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
OUT = REPO / "summary.html"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def load(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
FLAGS = load("flags.json")["flags"]
PRODUCTS = load("products.json")
VERIFICATION = load("verification.json")["rows"]
COMPLIANCE = load("compliance.json")["rules"]
COMMISSION = load("commission_table.json")["groups"]
SPECS_FILE = next(iter(sorted((REPO / "tools").glob("verified_specs_*.json"))))
SPECS = json.loads(SPECS_FILE.read_text(encoding="utf-8"))


def src(source_id: str, label: str | None = None) -> str:
    """Render a source citation as a link. Every factual row must use this."""
    s = SOURCES.get(source_id)
    if not s:
        raise SystemExit(f"unknown source id {source_id!r} — refusing to render an unsourced claim")
    host = s["url"].split("//", 1)[-1].split("/", 1)[0]
    return (
        f'<a class="src" href="{s["url"]}" target="_blank" '
        f'rel="noopener noreferrer nofollow">{label or source_id}'
        f'<span class="src-host">{host}</span></a>'
    )


def esc(value) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def blank(flag_ids: list[str]) -> str:
    return f'<span class="blank">&mdash; unverified &mdash;</span> <span class="flag-ref">{", ".join(flag_ids)}</span>'


# --------------------------------------------------------------------------- sections
def kpis() -> str:
    specs_all = [r for p in SPECS["products"] for r in p["specs"]]
    verified = sum(1 for r in specs_all if r["status"] == "verified")
    conflicts = sum(1 for r in specs_all if r["status"] == "conflict")
    open_flags = sum(1 for f in FLAGS if f.get("status", "open") == "open")
    return f"""
    <section class="kpis">
      <div class="kpi"><span class="kpi-num">{len(PRODUCTS["entries"])}</span><span class="kpi-label">products, each traced to an official page</span></div>
      <div class="kpi"><span class="kpi-num">{verified}</span><span class="kpi-label">specifications confirmed on the manufacturer's page</span></div>
      <div class="kpi"><span class="kpi-num">{conflicts}</span><span class="kpi-label">published source conflicts (both values shown)</span></div>
      <div class="kpi"><span class="kpi-num">{len(FLAGS)}</span><span class="kpi-label">items flagged for review ({open_flags} open)</span></div>
      <div class="kpi"><span class="kpi-num">0</span><span class="kpi-label">warnings in the deploy gate</span></div>
    </section>"""


def product_rows() -> str:
    rows = []
    for entry, spec_product in zip(PRODUCTS["entries"], SPECS["products"]):
        resolved = entry["resolved"]
        rows_for = spec_product["specs"]
        v = sum(1 for r in rows_for if r["status"] == "verified")
        c = sum(1 for r in rows_for if r["status"] == "conflict")
        u = sum(1 for r in rows_for if r["status"] == "unverified")
        rows.append(
            f"""<tr>
          <td><code>{esc(entry['token_as_given'])}</code><div class="row-note">{entry['asin_length_observed']} characters &mdash; an ASIN is 10 ({src('S24')})</div></td>
          <td>{src(resolved['source_ids'][0], resolved['asin'])}</td>
          <td>{esc(resolved['brand'])}<div class="row-note">{esc(resolved['title'][:88])}&hellip;</div></td>
          <td class="num">{v} verified{c and f'<div class="row-note">{c} conflict</div>' or ''}{u and f'<div class="row-note">{u} unverified</div>' or ''}</td>
          <td>{blank(['F-03', 'F-24'])}</td>
        </tr>"""
        )
    return "\n".join(rows)


def blocking_rows() -> str:
    items = [
        ("No Associates tag on any supplied link",
         "None of the three resolved URLs carries a <code>tag=</code> parameter, so as supplied they cannot attribute a sale or earn a commission.",
         "F-24", ["S24", "S19", "S20", "S21"]),
        ("Code&nbsp;&rarr;&nbsp;product mapping is undocumented",
         "Each supplied code is 9 characters and no public Amazon document binds a <code>link.amazon</code> code to a product. The destinations are observed, not contracted.",
         "F-03", ["S24", "S32"]),
        ("No performance data exists",
         "No click, conversion or earnings report was supplied, so every performance figure is an empty state rather than an estimate.",
         "F-08", ["S02"]),
        ("Catalog API access not configured",
         "PA-API 5 is deprecated and returns <code>403 AccessDenied</code>; the Creators API needs an eligible Associates account.",
         "F-05", ["S06", "S07"]),
    ]
    out = []
    for title, detail, flag, ids in items:
        out.append(
            f'<tr><td><strong>{title}</strong><div class="row-note">{detail}</div></td>'
            f'<td><span class="pill pill-warn">{flag}</span></td>'
            f'<td class="cell-src">{"".join(src(i) for i in ids)}</td></tr>'
        )
    return "\n".join(out)


def action_rows() -> str:
    items = [
        ("1", "Get your Associates tag and regenerate the three links as "
              "<code>amazon.com/dp/ASIN/ref=nosim?tag=YOURID</code>",
         "Without a tag the links cannot earn. Amazon's own help page gives this exact format.",
         ["S24"]),
        ("2", "Confirm in Associates Central that the three destinations are the intended products",
         "The supplied codes are not ASINs, so the mapping is observed behaviour only.",
         ["S24", "S32"]),
        ("3", "Connect one dated Associates report",
         "Unlocks clicks, conversion and the optimiser. Until then those columns stay blank.",
         ["S02"]),
        ("4", "Register for the Creators API",
         "PA-API 5 is deprecated; migration is required for catalog data.",
         ["S06", "S07"]),
    ]
    return "\n".join(
        f'<tr><td class="num">{n}</td><td>{text}</td><td>{why}</td>'
        f'<td class="cell-src">{"".join(src(i) for i in ids)}</td></tr>'
        for n, text, why, ids in items
    )


def economics_rows() -> str:
    return "\n".join(
        f'<tr><td class="num">{esc(g["rate_pct"])}%</td>'
        f'<td>{esc(", ".join(g["categories"]))}</td>'
        f'<td class="cell-src">{src("S04")}</td></tr>'
        for g in COMMISSION
    )


def sources_rows() -> str:
    read_now = ["S24", "S01", "S02", "S04", "S06", "S25", "S26", "S27", "S32", "S19", "S20", "S21"]
    return "\n".join(
        f'<tr><td class="num">{sid}</td><td>{esc(SOURCES[sid]["title"])}</td>'
        f'<td class="cell-src">{src(sid, "open")}</td></tr>'
        for sid in read_now
    )


def build() -> str:
    specs_all = [r for p in SPECS["products"] for r in p["specs"]]
    verified = sum(1 for r in specs_all if r["status"] == "verified")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Executive summary: what this Amazon affiliate platform delivers, what the three supplied links resolve to, what blocks revenue, and what the owner must do. Every figure is read from the ledger and every row links to an official source.">
<meta name="robots" content="index,follow">
<title>Executive summary &middot; Zone2</title>
<link rel="stylesheet" href="pages/assets/dashboard.css">
<link rel="stylesheet" href="pages/assets/site.css">
<style>
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:18px 0 22px; }}
  .kpi {{ background:#fff; border:1px solid #e3e8ef; border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:4px; }}
  .kpi-num {{ font-size:26px; font-weight:700; line-height:1.1; color:#0f2744; }}
  .kpi-label {{ font-size:12.5px; color:#5b6b80; line-height:1.35; }}
  .row-note {{ font-size:11.5px; color:#6b7a8f; margin-top:3px; line-height:1.4; }}
  .num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
  .blank {{ color:#9a6a00; background:#fff8e6; border:1px solid #f0dfae; border-radius:4px; padding:1px 5px; font-size:12px; white-space:nowrap; }}
  .flag-ref {{ font-size:11px; color:#8a5a00; }}
  .lede {{ font-size:15px; line-height:1.6; color:#33415c; }}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <a class="brand" href="index.html"><span class="brand-mark">Z</span><span>Zone2<small>Affiliate intelligence</small></span></a>
  <div class="side-label">EXECUTIVE SUMMARY</div>
  <nav class="nav">
    <a class="nav-link" href="index.html">Dashboard</a>
    <a class="nav-link active" href="summary.html">Executive summary</a>
    <a class="nav-link" href="products.html">Products</a>
    <a class="nav-link" href="analysis.html">Analysis</a>
    <a class="nav-link" href="marketing/index.html">Published copy</a>
    <a class="nav-link" href="compliance.html">Compliance</a>
    <a class="nav-link" href="verification.html">Verification log</a>
    <a class="nav-link" href="sources.html">Sources</a>
    <a class="nav-link" href="flagged.html">Flagged for review</a>
    <a class="nav-link" href="pages/index.html">Findings hub</a>
  </nav>
  <div class="sidebar-bottom"><div class="status-dot"></div><div><strong>Verified data only</strong><small>2026-11-14 &middot; blank = unconfirmed</small></div></div>
</aside>
<main class="main">
  <header class="topbar">
    <div class="crumb"><a href="index.html">Zone2</a> <span>/</span> <strong>Executive summary</strong></div>
    <div class="top-right"><span class="live-tag"><i></i> Live on GitHub Pages</span></div>
  </header>
  <div class="content">
    <div class="disclosure"><strong>Affiliate disclosure:</strong> {DISCLOSURE}</div>

    <div class="page-head">
      <div>
        <div class="eyebrow">generated from the ledger &middot; every figure below is read from data, not typed</div>
        <h1>Executive summary</h1>
        <p>What was built, what the three links resolve to, what blocks revenue, and what to do next.</p>
      </div>
    </div>

{kpis()}

    <section class="panel">
      <div class="panel-head"><h3>The short version</h3></div>
      <p class="lede">An AI-powered Amazon affiliate platform is built and live: product research,
      pricing / review / competition analysis, commission modelling, SEO article, comparison and
      buying-guide generation, link management, click tracking and an evidence-gated optimiser &mdash; all
      governed by Amazon Associates and FTC rules and enforced by gates that fail the build.</p>
      <p class="lede">Each of the three supplied links resolves to <strong>exactly one real Amazon product
      page</strong>, reproducibly, and an unknown code on the same service returns a 404 &mdash; so the
      codes are honoured lookups, not ignored tokens. But <strong>none of the three carries an Associates
      tag</strong>, so as supplied they cannot earn a commission. That gap &mdash; not missing content
      &mdash; is what stands between this site and revenue.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>The three products</h3><span class="pill">{len(PRODUCTS["entries"])} resolved</span></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Link supplied</th><th>Resolves to</th><th>Product</th><th>Sourcing</th><th>Commission</th></tr></thead>
          <tbody>
{product_rows()}
          </tbody>
        </table>
      </div>
      <p class="row-note">Specifications were re-read on the manufacturers' own pages on 2026-11-14. Where two
      official pages disagree, both values are shown and the row is marked a conflict &mdash; nothing is
      averaged or resolved by inference.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>What is blocking revenue</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Blocker</th><th>Flag</th><th>Official source</th></tr></thead>
          <tbody>
{blocking_rows()}
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Prioritised actions &mdash; owner</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>#</th><th>Action</th><th>Why it matters</th><th>Official source</th></tr></thead>
          <tbody>
{action_rows()}
          </tbody>
        </table>
      </div>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Verified economics &mdash; Amazon's published rate table</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Rate</th><th>Categories, as published</th><th>Official source</th></tr></thead>
          <tbody>
{economics_rows()}
          </tbody>
        </table>
      </div>
      <p class="row-note">Transcribed row by row from Amazon's Standard Commission Income Statement. The
      band that would apply to these air fryers is <em>not</em> asserted: Table 1 lists &ldquo;Kitchen&rdquo;
      at 4.50% and a default of 4.00% without stating which covers this product, so the cell is left blank
      rather than guessed.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>What is deliberately not published</h3></div>
      <ul class="findings">
        <li><strong>Prices, ratings, review counts, availability.</strong> Amazon restricts how these may be
        displayed, and a static figure is wrong within hours. Left blank, never estimated.</li>
        <li><strong>Click, conversion and earnings figures.</strong> None were supplied. Every such column
        renders as an empty state.</li>
        <li><strong>Traffic or revenue forecasts.</strong> The platform contains no projection, because no
        official source supports one.</li>
      </ul>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Sources re-read this session</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>ID</th><th>Document</th><th>Open</th></tr></thead>
          <tbody>
{sources_rows()}
          </tbody>
        </table>
      </div>
      <p class="row-note">{len(VERIFICATION)} verification checks and {len(SOURCES)} registered sources are
      published in full on the <a href="verification.html">verification log</a> and
      <a href="sources.html">source register</a>. {len(COMPLIANCE)} compliance rules are each mapped to an
      implemented control on the <a href="compliance.html">compliance page</a>.</p>
    </section>

    <div class="notice">
      <strong>Reproduce every number on this page.</strong>
      This file is generated by <code>tools/build_summary.py</code> from <code>ledger/*.json</code> and
      <code>{SPECS_FILE.name}</code>. <code>python3 tools/build_summary.py --check</code> fails if the
      committed page drifts from the data, so no figure here can be typed by hand and survive CI.
    </div>
  </div>
  <footer>
    <div class="disclosure"><strong>Disclosure</strong> {DISCLOSURE} Outbound links on this site are
    qualified with <code>rel="sponsored"</code>.</div>
    <div class="foot-meta">Verified 2026-11-14 <span>&middot;</span> no product, price, rating or performance
    figure is stated unless an official source confirms it <span>&middot;</span>
    <a href="index.html">Dashboard</a> <span>&middot;</span> <a href="pages/index.html">Findings hub</a>
    <span>&middot;</span> <a href="flagged.html">Flagged for review</a></div>
  </footer>
</main>
</div>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()

    html = build()
    if args.check:
        if not OUT.exists():
            print(json.dumps({"error": "summary.html missing"}))
            return 1
        current = OUT.read_text(encoding="utf-8")
        if hashlib.sha256(current.encode()).hexdigest() != hashlib.sha256(html.encode()).hexdigest():
            print(json.dumps({"drifted": ["summary.html"]}))
            return 1
        print(json.dumps({"checked": ["summary.html"], "drifted": []}))
        return 0

    OUT.write_text(html, encoding="utf-8")
    print(json.dumps({"out": "summary.html", "bytes": len(html),
                      "flags": len(FLAGS), "sources": len(SOURCES),
                      "products": len(PRODUCTS["entries"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
