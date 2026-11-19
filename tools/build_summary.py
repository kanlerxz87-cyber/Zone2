#!/usr/bin/env python3
"""Generate the current, evidence-bounded executive summary.

Inputs are the committed product, intent, flag, source, and commission registers. This
script never edits those registers and never treats an observed redirect as proof of the
intended product. A --check run checks generated-file drift only; it is not a live
re-verification of Amazon or manufacturer pages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from flag_state import open_count
from head_meta import head_block

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
OUT = REPO / "summary.html"

SUMMARY_DESCRIPTION = (
    "Counter Notes executive summary: five supplied Amazon links, their dated observed "
    "destinations, the intended products and Associates checks still unconfirmed, and "
    "the evidence needed for the next decisions."
)
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_ledger(name: str) -> dict:
    return read_json(LEDGER / name)


SOURCES = {row["id"]: row for row in load_ledger("sources.json")["sources"]}
FLAGS = load_ledger("flags.json")["flags"]
PRODUCTS = load_ledger("products.json")
INTENT = read_json(REPO / "docs" / "product-intent.json")
INTENT_BY_CODE = {row["supplied_code"]: row for row in INTENT["links"]}
COMMISSION = load_ledger("commission_table.json")
SPEC_ROWS = [
    spec
    for entry in PRODUCTS["entries"]
    for spec in entry.get("resolved", {}).get("specs", [])
]


def esc(value: object) -> str:
    return (
        str(value if value is not None else "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def src(source_id: str, label: str | None = None) -> str:
    """Render a registered source citation; evidence links are not affiliate links."""
    source = SOURCES.get(source_id)
    if not source:
        raise SystemExit(f"unknown source id {source_id!r} — refusing to render an unsourced claim")
    host = source["url"].split("//", 1)[-1].split("/", 1)[0]
    text = label if label is not None else source_id
    return (
        f'<a class="src" href="{esc(source["url"])}" target="_blank" '
        f'rel="noopener noreferrer nofollow">{esc(text)}'
        f'<span class="src-host">{esc(host)}</span></a>'
    )


def intent_confirmed(row: dict) -> bool:
    intent = row.get("intent", {})
    return bool(
        intent.get("intended_asin")
        and intent.get("confirmation_date")
        and intent.get("confirmation_source")
    )


def checked_records() -> list[dict]:
    """Join the two ledgers by supplied code while keeping intent and observation separate."""
    entries = PRODUCTS.get("entries", [])
    if len(entries) != len(INTENT.get("links", [])):
        raise SystemExit("product and intent registers have different row counts")
    if {row.get("token_as_given") for row in entries} != set(INTENT_BY_CODE):
        raise SystemExit("product and intent registers do not contain the same supplied codes")

    result = []
    for entry in entries:
        code = entry["token_as_given"]
        intent_record = INTENT_BY_CODE[code]
        resolved = entry.get("resolved", {})
        source_ids = list(resolved.get("source_ids", []))
        if not source_ids:
            raise SystemExit(f"{entry['id']}: observed listing has no official source")
        source_ids.extend(
            sid for sid in resolved.get("manufacturer_source_ids", [])
            if sid not in source_ids
        )
        for source_id in source_ids:
            if source_id not in SOURCES:
                raise SystemExit(f"{entry['id']}: unknown official source {source_id}")
        observation = intent_record.get("observation", {})
        if not observation.get("destination_asin") or not observation.get("observed_on"):
            raise SystemExit(f"{code}: destination observation is missing its ASIN or date")
        result.append({
            "entry": entry,
            "resolved": resolved,
            "intent_record": intent_record,
            "intent": intent_record.get("intent", {}),
            "observation": observation,
            "source_ids": source_ids,
        })
    return result


RECORDS = checked_records()
CONFIRMED_INTENTS = sum(1 for row in INTENT["links"] if intent_confirmed(row))
PUBLISHED_SPECIAL_LINKS = [
    row for row in INTENT["links"] if row.get("special_link", {}).get("tag")
]


def product_rows() -> str:
    rows = []
    for record in RECORDS:
        entry = record["entry"]
        resolved = record["resolved"]
        intent = record["intent"]
        observation = record["observation"]
        sources = " ".join(src(sid, sid) for sid in record["source_ids"])
        specs = resolved.get("specs", [])
        verified = sum(1 for row in specs if row.get("status") == "verified")
        conflicts = sum(1 for row in specs if row.get("status") == "conflict")
        unverified = sum(1 for row in specs if row.get("status") == "unverified")

        if intent_confirmed(record["intent_record"]):
            intended = (
                f'{esc(intent["intended_asin"])} '
                f'<small>confirmed {esc(intent["confirmation_date"])}</small>'
            )
        else:
            intended = (
                '<span class="blank">&mdash; unverified &mdash;</span> '
                f'<span class="flag-ref">{esc(intent.get("mapping_status", "UNCONFIRMED"))}</span>'
            )

        special = record["intent_record"].get("special_link", {})
        if special.get("tag"):
            validation = special.get("associates_workflow_validated")
            if validation is None:
                state = "workflow validation pending"
            elif validation is True:
                state = "marked validated in the register"
            else:
                state = "marked not validated in the register"
            special_cell = (
                f'<code>{esc(special["tag"])}</code>'
                f'<small>Site link record; {state}. See {src("S24", "Amazon Special Link help")}.</small>'
            )
        else:
            special_cell = (
                '<span class="blank">&mdash; not published &mdash;</span>'
                '<small>Product intent unresolved; no purchase link is presented.</small>'
            )

        rows.append(f"""<tr>
          <td><a class="src" href="{esc(record['intent_record']['supplied_url'])}" target="_blank" rel="noopener noreferrer nofollow"><code>{esc(entry['token_as_given'])}</code><span class="src-host">link.amazon</span></a><small>Supplied short link; observation recorded {esc(observation['observed_on'])}. Evidence reference, not a purchase CTA.</small></td>
          <td><strong>{esc(resolved.get('brand', ''))}</strong><small>{esc(resolved.get('title', ''))}</small></td>
          <td>{src(record['source_ids'][0], esc(observation['destination_asin']))}<small>Observed {esc(observation['observed_on'])}; this is not the intended-product field.</small></td>
          <td>{intended}<small>Blank unless the intent register has an owner confirmation and source.</small></td>
          <td>{special_cell}</td>
          <td>{verified} verified<small>{conflicts} conflicts · {unverified} unverified in the dated spec ledger</small><small>{sources}</small></td>
        </tr>""")
    return "\n".join(rows)


def blockers_rows() -> str:
    items = [
        (
            "Intended-product identity is unconfirmed",
            "All five intended-ASIN fields are blank. The observed listing destinations remain separate records; the short-link observations do not establish the products intended by the owner.",
            ["S19", "S20", "S21", "S61", "S62", "S24"],
            "F-06",
        ),
        (
            "Associates validation is pending for published Special Links",
            "Three site-generated Special Link records carry the supplied tracking ID. Their Associates-workflow validation fields are null. The two additional observations have no published purchase link because their intent is unresolved. The supplied short links' exact compliance status remains unresolved; this summary does not label them invalid.",
            ["S01", "S02", "S24"],
            "F-24",
        ),
        (
            "No first-party performance report is recorded",
            "No order, conversion, click or earnings result is claimed here. Connect an authorized Associates report before publishing those results.",
            ["S01", "S02"],
            "F-08",
        ),
        (
            "Automated catalog research is not connected",
            "The repository does not contain the account-authorized Creators API inputs needed for live product research. No demand, competition, trend or conversion score is presented.",
            ["S06", "S07", "S08"],
            "F-05",
        ),
    ]
    return "\n".join(
        f'<tr><td><strong>{esc(title)}</strong><small>{esc(detail)}</small></td>'
        f'<td><a href="pages/flags.html#{esc(flag)}">{esc(flag)} · review</a></td>'
        f'<td>{" ".join(src(sid) for sid in source_ids)}</td></tr>'
        for title, detail, source_ids, flag in items
    )


def action_rows() -> str:
    items = [
        (
            "Confirm the intended product for each submitted code",
            "In the intent register, record the intended ASIN, official listing URL, confirmation date and source only after the owner confirms it. Keep each redirect observation separate.",
            ["S24", "S01"],
        ),
        (
            "Validate each Special Link in Associates Central",
            "For each confirmed product, check the link destination and tracking in the enrolled account workflow before treating it as validated. The current register marks these checks pending.",
            ["S01", "S02", "S24"],
        ),
        (
            "Connect authorized catalog research",
            "Use an eligible Associates account and the documented Creators API. Do not substitute scraping or an inferred trend score.",
            ["S06", "S07", "S08"],
        ),
        (
            "Import a dated first-party report before making performance claims",
            "Keep clicks, orders, conversions and earnings blank until an authorized Associates report supplies them.",
            ["S01", "S02"],
        ),
    ]
    return "\n".join(
        f'<tr><td class="num">{index}</td><td><strong>{esc(title)}</strong><small>{esc(detail)}</small></td>'
        f'<td>{" ".join(src(sid) for sid in source_ids)}</td></tr>'
        for index, (title, detail, source_ids) in enumerate(items, 1)
    )


def source_rows() -> str:
    source_ids = [
        "S01", "S02", "S04", "S06", "S07", "S08", "S24",
        "S19", "S20", "S21", "S61", "S62", "S40", "S41",
    ]
    return "\n".join(
        f'<tr><td>{esc(source_id)}</td><td>{esc(SOURCES[source_id]["title"])}</td>'
        f'<td>{src(source_id, "Open official source")}</td></tr>'
        for source_id in source_ids
    )


def build() -> str:
    spec_verified = sum(1 for row in SPEC_ROWS if row.get("status") == "verified")
    spec_conflicts = sum(1 for row in SPEC_ROWS if row.get("status") == "conflict")
    open_flags = open_count(FLAGS)
    tag_values = sorted({row["special_link"]["tag"] for row in PUBLISHED_SPECIAL_LINKS})
    tag_display = ", ".join(f"<code>{esc(value)}</code>" for value in tag_values) or "none recorded"
    tagged_validation_pending = sum(
        1 for row in PUBLISHED_SPECIAL_LINKS
        if row.get("special_link", {}).get("associates_workflow_validated") is None
    )
    recorded_date = esc(COMMISSION.get("as_of", "not recorded"))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{esc(SUMMARY_DESCRIPTION)}">
<meta name="robots" content="index,follow">
<title>Executive summary &middot; Counter Notes</title>
{head_block("summary.html", title="Executive summary · Counter Notes", description=SUMMARY_DESCRIPTION, site_name="Counter Notes")}
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="pages/assets/dashboard.css">
<link rel="stylesheet" href="pages/assets/site.css">
<style>
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(155px,1fr)); gap:12px; margin:18px 0 22px; }}
  .kpi {{ background:#fff; border:1px solid #e3e8ef; border-radius:10px; padding:14px 16px; display:flex; flex-direction:column; gap:4px; }}
  .kpi-num {{ font-size:25px; font-weight:700; line-height:1.1; color:#0f2744; }}
  .kpi-label {{ font-size:12px; color:#5b6b80; line-height:1.4; }}
  .row-note, .data-table td small {{ display:block; font-size:11.5px; color:#6b7a8f; margin-top:4px; line-height:1.45; white-space:normal; }}
  .data-table td small a {{ margin-right:4px; }}
  .num {{ font-variant-numeric:tabular-nums; white-space:nowrap; }}
  .blank {{ color:#8a5a00; background:#fff8e6; border:1px solid #f0dfae; border-radius:4px; padding:1px 5px; font-size:12px; }}
  .flag-ref {{ display:block; font-size:10.5px; color:#8a5a00; margin-top:4px; }}
  .lede {{ font-size:15px; line-height:1.65; color:#33415c; }}
  .src {{ display:inline-block; margin:2px 5px 2px 0; white-space:nowrap; }}
  .src-host {{ display:block; font-size:9px; opacity:.68; font-weight:400; }}
  .source-note {{ font-size:12px; line-height:1.55; color:#5b6b80; }}
  @media (max-width: 760px) {{ .data-table {{ min-width:760px; }} }}
</style>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <a class="brand" href="index.html"><span class="brand-mark">CN</span><span>Counter Notes<small>Product publication</small></span></a>
  <div class="side-label">PROJECT DESK</div>
  <nav class="nav">
    <a class="nav-link" href="index.html">Publication home</a>
    <a class="nav-link active" href="summary.html">Executive summary</a>
    <a class="nav-link" href="products.html">Product register</a>
    <a class="nav-link" href="intent.html">Intent and observations</a>
    <a class="nav-link" href="board/index.html">Open decisions</a>
    <a class="nav-link" href="questions.html">Questions and unknowns</a>
    <a class="nav-link" href="suggestions.html">Review suggestions</a>
    <a class="nav-link" href="verification.html">Verification log</a>
    <a class="nav-link" href="sources.html">Source register</a>
    <a class="nav-link" href="flagged.html">Flagged for review</a>
  </nav>
  <div class="sidebar-bottom"><div class="status-dot"></div><div><strong>Evidence-bounded status</strong><small>Read dates are recorded per source; blank = unconfirmed</small></div></div>
</aside>
<main class="main">
  <header class="topbar">
    <div class="crumb"><a href="index.html">Counter Notes</a> <span>/</span> <strong>Executive summary</strong></div>
    <div class="top-right"><span class="live-tag"><i></i> Release summary · 2026-11-19</span></div>
  </header>
  <div class="content">
    <div class="disclosure"><strong>Affiliate disclosure:</strong> {DISCLOSURE}</div>

    <div class="page-head">
      <div>
        <div class="eyebrow">Current project state &middot; derived from dated repository records</div>
        <h1>Executive summary</h1>
        <p>What is published, what remains unconfirmed, and what evidence is needed next.</p>
      </div>
    </div>

    <section class="panel">
      <div class="panel-head"><h3>At a glance · <span id="flagCountHeading">{len(FLAGS)}</span> registered items</h3><span class="pill">{len(RECORDS)} supplied-link records</span></div>
      <p class="lede">Counter Notes is a buyer-facing product publication supported by a source register and a reviewable project desk. Its front page presents sourced air-fryer listing information; two additional supplied-link destinations are kept as observations, not recommendations. An observed redirect does not establish the intended product.</p>
      <p class="lede">The intent register currently confirms <strong>{CONFIRMED_INTENTS} of {len(INTENT['links'])}</strong> intended-product mappings. {len(PUBLISHED_SPECIAL_LINKS)} site-generated Special Link records carry {tag_display}; Associates-workflow validation is pending for {tagged_validation_pending}. This does not establish the compliance status of the supplied short links or confirm earnings.</p>
      <p class="source-note">The product/spec ledger contains {spec_verified} rows marked verified and {spec_conflicts} marked conflict; the canonical flag register contains <span id="flagCount">{len(FLAGS)}</span> entries, of which {open_flags} remain open. These counts summarize dated repository records, not live checks performed during this build.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Submitted links — observations kept separate from intent</h3><span class="pill">{len(RECORDS)} records</span></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Code supplied</th><th>Observed listing title</th><th>Observed destination</th><th>Intended product</th><th>Site Special Link record</th><th>Dated spec ledger</th></tr></thead>
          <tbody>{product_rows()}</tbody>
        </table>
      </div>
      <p class="row-note">Each observation date is shown beside its destination. The linked Amazon pages are official listing references stored in the source register; this pass did not fetch those pages live. The intended-ASIN field stays blank unless the separate intent register contains a confirmation date and source. <a href="intent.html">Review the intent record</a> · <a href="pages/flags.html#F-06">F-06</a>.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Open checks — not conclusions about the supplied links</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>Open item</th><th>Register</th><th>Official references</th></tr></thead>
          <tbody>{blockers_rows()}</tbody>
        </table>
      </div>
      <p class="row-note">The exact compliance status of the supplied short links is unresolved in the register. No conclusion that they are invalid is made here.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Next evidence to collect</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>#</th><th>Decision or evidence step</th><th>Official references</th></tr></thead>
          <tbody>{action_rows()}</tbody>
        </table>
      </div>
      <p class="row-note">Missing product identity and account-level information should be discovered through the owner's Associates Central records; performance should come from a dated first-party report. Do not fill any of these fields from the observed redirect alone.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Review note — older decision-board wording</h3><span class="pill pill-warn">cross-scope follow-up</span></div>
      <p class="lede">An older suggestion/requirements record still says no Associates ID was supplied and states that the supplied links cannot attribute sales. That wording predates the current owner-supplied ID and site-generated Special Link records; it is not a finding about the supplied short links' exact compliance status. The current intent register leaves Associates-workflow validation pending and keeps the short-link status unresolved.</p>
      <p class="row-note">This integration did not edit the decision-board source data. Review the <a href="board/requirements.html#RQ-22">requirements note</a>, <a href="board/suggestions.html#BS-04">suggestion</a>, and the <a href="intent.html">current intent register</a>.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Rates and performance — limits on what this page says</h3></div>
      <p class="lede">The local commission table is a US-program snapshot recorded as of {recorded_date} and cites Amazon's published statement. This build did not re-fetch that statement; check Amazon's current page before relying on a rate. No rate is assigned to any supplied product.</p>
      <p class="lede">Prices, ratings, review counts, availability, search demand, trends, clicks, orders and earnings are not asserted here. Values without a dated authorized source remain blank in the relevant records.</p>
      <p class="source-note">Official rate statement: {src('S04', 'Amazon Associates Standard Commission Income Statement')} · Program policies and reporting terms: {src('S02', 'Amazon Associates Program Policies')}.</p>
    </section>

    <section class="panel">
      <div class="panel-head"><h3>Official references behind these records</h3></div>
      <div class="table-wrap">
        <table class="data-table">
          <thead><tr><th>ID</th><th>Source</th><th>Open</th></tr></thead>
          <tbody>{source_rows()}</tbody>
        </table>
      </div>
      <p class="row-note">Source read dates and verification methods are in the <a href="sources.html">source register</a> and <a href="verification.html">verification log</a>. This release pass checked local generated outputs and repository gates, not live Amazon or manufacturer pages.</p>
    </section>

    <div class="notice">
      <strong>Reproducible from the repository records.</strong>
      <code>python3 tools/build_summary.py --check</code> checks whether this HTML matches its generator inputs. It does not certify that external sources are still current.
    </div>
  </div>
  <footer>
    <div class="disclosure"><strong>Disclosure</strong> {DISCLOSURE} Outbound product links are qualified with <code>rel="sponsored"</code>.</div>
    <div class="foot-meta">Dated records; no live product-page recheck in this pass <span>&middot;</span>
    <a href="index.html">Publication home</a> <span>&middot;</span> <a href="intent.html">Intent register</a>
    <span>&middot;</span> <a href="questions.html">Open questions</a> <span>&middot;</span> <a href="suggestions.html">Review suggestions</a>
    <span>&middot;</span> <a href="flagged.html">Flagged items</a></div>
  </footer>
</main>
</div>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = build()
    if args.check:
        if not OUT.exists():
            print(json.dumps({"error": "summary.html missing"}))
            return 1
        current = OUT.read_text(encoding="utf-8")
        if hashlib.sha256(current.encode()).hexdigest() != hashlib.sha256(rendered.encode()).hexdigest():
            print(json.dumps({"drifted": ["summary.html"]}))
            return 1
        print(json.dumps({"checked": ["summary.html"], "drifted": []}))
        return 0

    OUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({
        "out": "summary.html",
        "bytes": len(rendered),
        "products": len(RECORDS),
        "confirmed_intents": CONFIRMED_INTENTS,
        "published_special_links": len(PUBLISHED_SPECIAL_LINKS),
        "open_flags": open_count(FLAGS),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
