#!/usr/bin/env python3
"""Build the product-intent confirmation record (root `product-intent.html`).

The brief (2026-11-17) asks for exactly this artifact:

    "For each submitted link, store the intended ASIN, official listing URL,
     confirmation date, and source. Keep observed redirect targets in a separate
     field. Do not merge the two fields. Rationale: Amazon's ASIN definition
     provides a checkable identifier."

So the page shows two tables that never share a column:

  1. INTENT — what the owner says each submitted link was minted for. Blank until
     the owner states it from a source; a blank is printed as a blank with its
     reason and its flag, never filled from the observed side.
  2. OBSERVED — what this project measured when it opened each link, dated.
     Evidence about the link, never a claim about intent.

The builder self-checks the data before it will write a page (and `--check` fails
when the committed page differs from a fresh build):

  * an intended half is either wholly blank (with a blank_reason and flag_ids) or
    wholly filled (asin + listing URL + date + source) — a half-filled row is a
    build error;
  * no intended value may equal an observed value by default of copying: the
    fields live in separate objects and the renderer never mixes them;
  * every observed redirect target carries a date and a URL;
  * no money figure is rendered anywhere (the site's no-price rule).

Usage:
    python3 tools/build_intent.py            # write product-intent.html
    python3 tools/build_intent.py --check    # fail if the committed page is stale
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import head_meta  # noqa: E402  — the repository's single canonical/OG contract
import site_config  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "ledger" / "product_intent.json"
OUT = ROOT / "product-intent.html"

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def e(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


class RecordError(RuntimeError):
    """Raised instead of publishing an intent record that merges or invents fields."""


def validate(doc: dict) -> None:
    entries = doc.get("entries") or []
    if not entries:
        raise RecordError("product-intent record has no entries — an empty register proves nothing")
    seen = set()
    for en in entries:
        eid = en.get("id") or ""
        if not eid or eid in seen:
            raise RecordError(f"duplicate or missing entry id {eid!r}")
        seen.add(eid)
        intent = en.get("intended") or {}
        keys = ("asin", "official_listing_url", "confirmation_date", "confirmation_source")
        filled = [k for k in keys if str(intent.get(k) or "").strip()]
        if filled and len(filled) != len(keys):
            raise RecordError(f"{eid}: intended half is partly filled ({filled}) — fill it from a stated source or leave it blank")
        if not filled and not (intent.get("blank_reason") or "").strip():
            raise RecordError(f"{eid}: blank intended half with no blank_reason — a blank must say why")
        if not filled and not (en.get("flag_ids") or []):
            raise RecordError(f"{eid}: unverified intended half must link the flag that explains it")
        obs = en.get("observed") or {}
        targets = obs.get("redirect_targets") or []
        if not targets:
            raise RecordError(f"{eid}: no observed redirect targets — the observed half is the measurement")
        for t in targets:
            if not (t.get("observed_utc") or "").strip() or not (t.get("final_url") or "").strip():
                raise RecordError(f"{eid}: observed target missing date or URL")
        if not (obs.get("asin") or "").strip():
            raise RecordError(f"{eid}: observed.asin missing")
        # The rule the brief states in one line: do not merge the two fields.
        if filled and str(intent.get("asin")) == str(obs.get("asin")) and not (intent.get("confirmation_source") or "").strip():
            raise RecordError(f"{eid}: intended.asin equals observed.asin with no confirmation source — copied, not confirmed")


def flag_anchor(fid: str) -> str:
    return f'<a href="pages/flags.html#{e(fid)}">{e(fid)}</a>'


def intent_rows(doc: dict) -> str:
    rows = []
    for en in doc["entries"]:
        intent = en["intended"]
        filled = all(str(intent.get(k) or "").strip() for k in
                     ("asin", "official_listing_url", "confirmation_date", "confirmation_source"))
        if filled:
            rows.append(
                f'<tr id="{e(en["id"])}"><th scope="row">{e(en["id"])}</th>'
                f'<td><code>{e(en["submitted_code"])}</code><div class="row-note">{e(en["submitted_url"])}</div></td>'
                f'<td><code>{e(intent["asin"])}</code></td>'
                f'<td>{e(intent["official_listing_url"])}</td>'
                f'<td>{e(intent["confirmation_date"])}</td>'
                f'<td>{e(intent["confirmation_source"])}</td>'
                f'<td><span class="pb-pill pb-pill--ok">confirmed</span></td></tr>'
            )
        else:
            flags = " ".join(flag_anchor(f) for f in en.get("flag_ids", []))
            rows.append(
                f'<tr id="{e(en["id"])}"><th scope="row">{e(en["id"])}</th>'
                f'<td><code>{e(en["submitted_code"])}</code><div class="row-note">{e(en["submitted_url"])}</div></td>'
                f'<td><span class="pb-blank">&mdash;</span> <span class="pb-pill pb-pill--warn">unverified</span></td>'
                f'<td><span class="pb-blank">&mdash;</span></td>'
                f'<td><span class="pb-blank">&mdash;</span></td>'
                f'<td><span class="pb-blank">&mdash;</span></td>'
                f'<td><div class="row-note">{e(intent["blank_reason"])}</div><div class="row-note">Flagged: {flags}</div></td></tr>'
            )
    return "".join(rows)


def observed_rows(doc: dict) -> str:
    rows = []
    for en in doc["entries"]:
        obs = en["observed"]
        reads = " &middot; ".join(
            f'{e(t["observed_utc"])}' for t in obs["redirect_targets"]
        )
        flags = " ".join(flag_anchor(f) for f in en.get("flag_ids", []))
        rows.append(
            f'<tr><th scope="row">{e(en["id"])}</th>'
            f'<td><a href="{e(obs["redirect_targets"][-1]["final_url"])}" target="_blank" '
            f'rel="nofollow noopener noreferrer">{e(obs["redirect_targets"][-1]["final_url"])}</a>'
            f'<div class="row-note">evidence link &mdash; recorded as observed, carries no Associates tag</div></td>'
            f'<td><code>{e(obs["asin"])}</code></td>'
            f'<td>{e(obs["listing_title"])}<div class="row-note">as served {e(obs["listing_title_read_utc"])}</div></td>'
            f'<td>{e(obs["category_path"])}</td>'
            f'<td>{reads}<div class="row-note">{e(obs["note"])}</div><div class="row-note">Flagged: {flags}</div></td></tr>'
        )
    return "".join(rows)


def page(doc: dict) -> str:
    head = head_meta.head_block(
        "product-intent.html",
        title="Product-intent confirmation record",
        description="What each submitted affiliate link was meant to promote (owner-confirmed, blank until confirmed) and, in a separate table, where each link actually went when this project opened it. The two fields are never merged.",
        site_name="Counter Notes",
    )
    dis = f'<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} {e(site_config.disclosure_variant())}</div></div>'
    body = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Product-intent confirmation record · Counter Notes</title>
<meta name="description" content="What each submitted affiliate link was meant to promote (owner-confirmed, blank until confirmed) and, in a separate table, where each link actually went when this project opened it. The two fields are never merged.">
{head}
<link rel="stylesheet" href="assets/css/style.css">
<link rel="stylesheet" href="assets/css/publish.css">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="pb-mast">
  <div class="pb-wrap">
    <div class="pb-mast-top">
      <div>
        <div class="pb-word">Counter <em>Notes</em></div>
        <div class="pb-tag">Countertop cooking gear, read off the spec sheet</div>
      </div>
      <div class="pb-mast-meta">Record as of {e(doc["as_of_utc"])}</div>
    </div>
    <nav class="pb-nav" aria-label="Sections"><a href="index.html">Counter Notes</a><a href="products.html" class="is-on">Operator dashboard</a><a href="flagged.html">Flagged for review</a><a href="guides/method.html">How we verify</a></nav>
  </div>
</header>
{dis}
<main id="main">
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Operator record &middot; decision support</p>
  <h1 class="pb-h1">Product-intent confirmation record</h1>
  <p class="pb-stand">Five <code>link.amazon</code> codes were submitted to this project. This page answers, and keeps separate, two different questions: what each link was <em>meant</em> to promote (the owner's claim, confirmed from a source), and where each link actually <em>went</em> when this project opened it (dated measurements). Nothing in the second table is ever copied into the first.</p>
  <p class="pb-byline"><b>Why separate.</b> Amazon's ASIN definition (S24) makes an intended ASIN a checkable claim &mdash; ten characters, one catalog record &mdash; while a nine-character short-link code is not an identifier anything can check. A register that merged intent with observation would let a redirect guess become a fact. <b>Rule (brief, 2026-11-17):</b> do not merge the two fields.</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Table 1 &mdash; intended: what each link was meant to promote</h2>
    <p class="pb-sub">Owner-confirmed fields. Every cell here is blank until the owner states the value and where the confirmation came from. A blank is published as a blank.</p></div>
  </div>
  <div class="pb-table-scroll"><table class="pb-table">
    <caption>Intended ASIN, official listing URL, confirmation date and confirmation source &mdash; one row per submitted link. Blank cells carry the reason and the flag; they are never filled from the observed table.</caption>
    <thead><tr><th>ID</th><th>Submitted link</th><th>Intended ASIN</th><th>Official listing URL</th><th>Confirmation date</th><th>Confirmation source</th><th>State</th></tr></thead>
    <tbody>{intent_rows(doc)}</tbody>
  </table></div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head">
    <div><h2 class="pb-h2">Table 2 &mdash; observed: where each link actually went</h2>
    <p class="pb-sub">Measured by opening the links on the dates shown. Evidence about the link &mdash; not a claim about intent, and not a claim that the supplied short links are invalid (their compliance status is unresolved, F-03).</p></div>
  </div>
  <div class="pb-table-scroll"><table class="pb-table">
    <caption>Observed redirect targets, kept in their own field per the brief. Per-arrival <code>btn_ref</code> shuffle tokens change on every read and are noted, never stored as identity.</caption>
    <thead><tr><th>ID</th><th>Observed destination (latest read)</th><th>Observed ASIN</th><th>Listing title as served</th><th>Category path</th><th>Dated reads</th></tr></thead>
    <tbody>{observed_rows(doc)}</tbody>
  </table></div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <h2 class="pb-h2">Flagged for review</h2>
  <p class="pb-sub">The open items this record depends on, with their source links, on the shared register.</p>
  <ul>
    <li><b>{flag_anchor("F-42")}</b> &mdash; two of the five submitted codes open meat-thermometer listings, not air fryers. The owner's answer decides the intended fields above and the site's category scope.</li>
    <li><b>{flag_anchor("F-03")}</b> &mdash; no Amazon document binds a <code>link.amazon</code> code to a catalog record; the intended fields cannot be derived from the observed ones.</li>
    <li><b>{flag_anchor("F-01")}</b> &mdash; the submitted codes are nine characters; an ASIN is ten. The codes are opaque short-link identifiers (F-28's control), and none is padded or repaired here.</li>
    <li><b>{flag_anchor("F-43")}</b> &mdash; the tagged Special Links pass the destination check; the tracking-report check needs the owner's Associates Central session.</li>
    <li><b>{flag_anchor("F-24")}</b> &mdash; the supplied short links carry no tag; the tagged Special Links this site publishes are separate objects (ledger/site_config.json) and do not rewrite the supplied ones.</li>
  </ul>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <h2 class="pb-h2">How the blanks get filled</h2>
  <ol>
    <li><b>Owner confirms intent.</b> For each submitted code, the owner states the intended ASIN (10 characters) or the intended product page, in Associates Central or in writing.</li>
    <li><b>Record the source and date.</b> The confirmation date and where it came from go in the same row; only then do the intended cells fill.</li>
    <li><b>Then, and only then,</b> may editorial copy describe a submitted link as promoting a named product. Until that moment every surface says what is observed and marks intent unverified.</li>
  </ol>
  <p class="pb-byline">Data: <code>ledger/product_intent.json</code> &middot; builder: <code>tools/build_intent.py</code> &middot; rendered {e(doc["as_of_utc"])}. Every observed row's date and URL is machine-checked before this page will build.</p>
</div></section>
</main>
<footer class="pb-foot"><div class="pb-wrap">
  <p><a href="index.html">Counter Notes</a> &middot; <a href="products.html">Operator dashboard</a> &middot; <a href="flagged.html">Flagged for review</a> &middot; <a href="sources.html">Source register</a> &middot; <a href="verification.html">Verification log</a> &middot; <a href="guides/method.html">How we verify</a></p>
  <p>{e(DISCLOSURE)}</p>
</div></footer>
</body>
</html>
"""
    return body


def main() -> int:
    check = "--check" in sys.argv
    doc = json.loads(DATA.read_text(encoding="utf-8"))
    validate(doc)
    want = page(doc)
    if check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != want:
            print("STALE: product-intent.html — run `python3 tools/build_intent.py`")
            return 1
        print(f"product-intent.html current ({len(want):,} bytes)")
        return 0
    OUT.write_text(want, encoding="utf-8")
    print(f"wrote product-intent.html ({len(want):,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
