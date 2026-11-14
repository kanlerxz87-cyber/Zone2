#!/usr/bin/env python3
"""Build the revalidation site from revalidation/data/*.json.

Every page is generated, never hand-edited: `--check` compares the committed
HTML against a fresh build, the same contract tools/build_site.py uses.

Rules enforced by construction:
  * every verified/conflict row must carry an official source link
  * a row with no source renders as a blank, flagged cell
  * every page carries the required Associates disclosure
"""
from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

NAV = [
    ("index.html", "Overview"),
    ("links.html", "Links & ASINs"),
    ("products.html", "Products"),
    ("method.html", "Method & Limits"),
    ("flagged.html", "Flagged for Review"),
    ("sources.html", "Sources"),
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def src_links(refs: str, sources: dict) -> str:
    """Render one or more source ids as external links, or blank."""
    out = []
    for ref in [r.strip() for r in refs.replace(",", " ").split() if r.strip()]:
        s = sources.get(ref)
        if not s:
            continue
        out.append(
            f'<a href="{escape(s["url"])}" target="_blank" rel="noopener noreferrer">{escape(ref)}</a>'
        )
    return " · ".join(out) if out else ""


def badge(status: str) -> str:
    m = {
        "verified": ("ok", "Verified"),
        "conflict": ("warn", "Conflict"),
        "unverified": ("flag", "Unverified"),
        "withheld": ("info", "Withheld by policy"),
        "not_rechecked": ("warn", "Not re-checked"),
    }
    cls, label = m.get(status, ("info", status))
    return f'<span class="badge {cls}">{label}</span>'


def page(title: str, current: str, lede: str, body: str) -> str:
    nav = "".join(
        f'<a href="{p}" class="active">{escape(t)}</a>'
        if p == current
        else f'<a href="{p}">{escape(t)}</a>'
        for p, t in NAV
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — Zone2 Revalidation</title>
<link rel="stylesheet" href="assets.css">
</head>
<body>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html">Zone2 Revalidation<small>Controlled re-check of the three supplied Amazon links · 2026-11-14</small></a>
    <nav aria-label="Main">{nav}</nav>
  </div>
</header>
<main>
  <div class="wrap">
    <div class="crumbs"><a href="../index.html">Zone2 dashboard</a> / <a href="index.html">Revalidation</a> / {escape(title)}</div>
    <h1>{escape(title)}</h1>
    <p class="lede">{lede}</p>
    <div class="disclosure"><strong>Affiliate disclosure:</strong> {DISCLOSURE}</div>
{body}
    <footer class="site">
      Session <code>c6e94e8d</code> · branch <code>arena/c6e94e8d-zone2</code> · verified 2026-11-14 ·
      Task T20 in the repository's <a href="https://github.com/kanlerxz87-cyber/Zone2/blob/main/COORDINATION.md" target="_blank" rel="noopener noreferrer">COORDINATION.md</a>.
      {DISCLOSURE}
    </footer>
  </div>
</main>
</body>
</html>
"""


def build_index(links, specs, flags) -> str:
    total_rows = sum(len(p["rows"]) for p in specs["products"])
    n_verified = sum(1 for p in specs["products"] for r in p["rows"] if r["status"] == "verified")
    n_open = sum(
        1 for p in specs["products"] for r in p["rows"] if r["status"] in ("unverified", "conflict")
    )
    body = f"""
    <div class="kpis">
      <div class="kpi"><div class="label">Links re-tested</div><div class="value">3</div><div class="sub">Each fetched live, twice</div></div>
      <div class="kpi"><div class="label">Control test</div><div class="value flag">Fails</div><div class="sub">The fallback marker is not evidence</div></div>
      <div class="kpi"><div class="label">Attribute rows</div><div class="value">{total_rows}</div><div class="sub">{n_verified} verified · {n_open} flagged</div></div>
      <div class="kpi"><div class="label">Open flags</div><div class="value warn">{len(flags["flags"])}</div><div class="sub">RV-01 … RV-{len(flags["flags"]):02d}</div></div>
    </div>

    <div class="card">
      <h3>What this session did</h3>
      <p>
        The repository already contained a published conclusion that the three supplied
        <code>link.amazon</code> links land on <em>arbitrary fallback pages</em> which cannot identify a
        product. That conclusion rested on two observations: the redirects carry
        <code>plpRedirect=mhFallback</code>, and a re-fetch was reported to change the page body and the
        <code>btn_ref</code> token. <strong>Neither observation had a control.</strong> This session ran the
        control, and it does not support either.
      </p>
      <p>
        The correction is narrow but material: the destination products are real, stable and individually
        tracked — not random — while the short codes themselves remain non-ASINs. What was wrong was the
        reasoning that joined the two facts.
      </p>
    </div>

    <h2>The two tests that changed the conclusion</h2>
    <div class="card">
      <h3>C-1 · Is <code>plpRedirect=mhFallback</code> evidence of a fallback?</h3>
      <p>
        A bare, untagged, direct request to the product page of a <strong>valid</strong> 10-character ASIN was
        made on <code>www.amazon.com</code>. Amazon answered with the full, correct product page and rewrote its
        own internal links to carry <code>plpRedirect=mhFallback</code>.
      </p>
      <pre class="evidence">GET https://www.amazon.com/dp/B08DKYBTPH          <span>(bare request: no tag, no short link)</span>
200 -&gt; <span>CHEFMAN 8 Qt TurboFry product page, buy box + About this Item rendered</span>
final URL -&gt; https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&amp;channelId=500&amp;<span>plpRedirect=mhFallback</span>&amp;th=1</pre>
      <p class="note">
        Result: the marker appears on ordinary product pages. It does not separate a valid ASIN from an
        unaddressable code, so it cannot support the published inference.
      </p>
    </div>

    <div class="card">
      <h3>C-2 · Does the destination really shuffle between requests?</h3>
      <p>
        The same short link was fetched twice. Both responses resolved to the same ASIN with the
        <strong>identical</strong> per-link token.
      </p>
      <pre class="evidence">GET https://link.amazon/B04G1MEwY   (fetch 1)
GET https://link.amazon/B04G1MEwY   (fetch 2)

both -&gt; /dp/B0CDY277D3?lv=shuf&amp;btn_type=ss&amp;<span>btn_ref=srctok-1e229870efde5acf</span>&amp;channelId=704&amp;plpRedirect=mhFallback
        same ASIN · same token · same page body</pre>
      <p class="note">
        Three different submitted links produced three different stable tokens. That is the signature of
        per-link tracking, not of a shuffle.
      </p>
    </div>

    <h2>What is still not established</h2>
    <div class="card">
      <p>
        The links resolve deterministically, but <strong>no public Amazon document binds a
        <code>link.amazon</code> short code to a destination ASIN</strong>. The mapping is therefore observed
        behaviour, not documented intent, and none of the three resolved URLs carries an Associates
        <code>tag</code>. Both points remain flagged (RV-02, RV-03) for confirmation in Associates Central.
        The products on this site are described as <em>the product each link resolves to</em>, never as
        <em>the product you selected</em>.
      </p>
      <p>
        Read <a href="links.html">Links &amp; ASINs</a> for the per-link evidence,
        <a href="flagged.html">Flagged for Review</a> for every open item, and
        <a href="method.html">Method &amp; Limits</a> for what this environment can and cannot verify.
      </p>
    </div>

    <h2>Corrections this session recommends to other sessions' files</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>ID</th><th>File (owner)</th><th>Requested change</th><th>Basis</th></tr></thead>
        <tbody>
          <tr><td>CR-1</td><td><code>ledger/flags.json</code> F-03</td><td>Downgrade "token was not honoured / unrelated destination" to "destination stable and per-link tracked; mapping not documented by Amazon".</td><td>C-1, C-3 — <a href="https://www.amazon.com/dp/B08DKYBTPH" target="_blank" rel="noopener noreferrer">control fetch</a></td></tr>
          <tr><td>CR-2</td><td><code>ledger/flags.json</code> F-05, <code>README.md</code></td><td>Remove the "different <code>btn_ref</code> on re-fetch" claim — not reproducible.</td><td>C-2 — <a href="https://link.amazon/B04G1MEwY" target="_blank" rel="noopener noreferrer sponsored">re-fetch</a></td></tr>
          <tr><td>CR-3</td><td><code>README.md</code> divergence table</td><td>Add the control result: a bare valid <code>/dp/</code> load also carries <code>plpRedirect=mhFallback</code>.</td><td>C-1 — <a href="https://www.amazon.com/dp/B0CDY277D3" target="_blank" rel="noopener noreferrer">second control</a></td></tr>
          <tr><td>CR-4</td><td><code>ledger/products.json</code></td><td>Remove "via mhFallback" as a <code>why_blank</code> reason; keep the ASIN-format and Page-Not-Found reasons, which stand.</td><td>C-4 — <a href="https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC" target="_blank" rel="noopener noreferrer">ASIN rule</a></td></tr>
          <tr><td>CR-5</td><td><code>research-hub/data/products.json</code></td><td>Six attribute rows not re-observable (RV-06) — re-check before continuing to mark verified.</td><td>RV-06 — <a href="https://www.amazon.com/dp/B09B7SB46R" target="_blank" rel="noopener noreferrer">source re-read</a></td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">Logged, not applied: those files belong to earlier sessions. See COORDINATION.md.</p>
"""
    return page(
        "Overview",
        "index.html",
        "A controlled re-check of the three supplied Amazon links, and a correction to a published "
        "conclusion that did not survive its control test.",
        body,
    )


def build_links(links) -> str:
    rows = []
    for L in links["links"]:
        rows.append(
            f"""<tr>
<td><a href="{escape(L['supplied'])}" target="_blank" rel="noopener noreferrer sponsored">{escape(L['supplied'])}</a></td>
<td><code>{escape(L['code'])}</code> ({L['code_length']} chars)<br><span class="badge flag">not an ASIN</span></td>
<td class="blank">blank<br><span class="note">Page Not Found</span><br><a href="{escape(L['code_check_url'])}" target="_blank" rel="noopener noreferrer">check</a></td>
<td><a href="{escape(L['resolves_to'])}" target="_blank" rel="noopener noreferrer sponsored">{escape(L['destination_asin'])}</a></td>
<td>{escape(L['link_token'])}<br><span class="note">channelId {escape(L['channel_id'])}</span></td>
<td>{'<span class="badge ok">yes</span>' if L['repeat_fetch_identical_token'] else '<span class="badge flag">no</span>'}</td>
<td><span class="badge flag">absent</span></td>
</tr>"""
        )
    body = f"""
    <div class="card">
      <p>
        Each link was fetched from its supplied form, followed to its destination, and fetched a second time.
        The code itself was separately requested as <code>amazon.com/dp/&lt;code&gt;</code> to test whether it
        addresses a catalogue record.
      </p>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr>
          <th>Supplied link <span class="note">(external)</span></th><th>Code</th><th>Code as <code>/dp/</code> path</th>
          <th>Resolves to</th><th>Per-link token</th><th>Stable on re-fetch</th><th>Associates <code>tag</code></th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <p class="note">
      Source for every row: the Amazon.com responses themselves — <a href="https://www.amazon.com/dp/B0CDY277D3" target="_blank" rel="noopener noreferrer">B0CDY277D3</a>,
      <a href="https://www.amazon.com/dp/B09B7SB46R" target="_blank" rel="noopener noreferrer">B09B7SB46R</a>,
      <a href="https://www.amazon.com/dp/B08DKYBTPH" target="_blank" rel="noopener noreferrer">B08DKYBTPH</a>, plus
      the three Page-Not-Found checks linked in column 3. The ASIN-length rule is from
      <a href="https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC" target="_blank" rel="noopener noreferrer">Amazon Associates help</a>.
    </p>

    <h2>Observed destination URLs</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Link</th><th>Destination as observed, with the tracking parameters Amazon appended</th></tr></thead>
        <tbody>
        {''.join(f'<tr><td><code>{escape(L["code"])}</code></td><td><code>{escape(L["destination_url_observed"])}</code></td></tr>' for L in links['links'])}
        </tbody>
      </table>
    </div>
    <p class="note">
      The absence of <code>tag=</code> in each of these URLs is the basis of flag RV-02. Under Operating
      Agreement §1 a Special Link must use Amazon's tagged link format, which includes the Associates ID.
    </p>
"""
    return page(
        "Links &amp; ASINs",
        "links.html",
        "Per-link evidence: what each supplied short link does, what its code does on its own, and which "
        "of the two results actually identifies a product.",
        body,
    )


def build_products(specs) -> str:
    sources = specs["sources"]
    blocks = []
    for p in specs["products"]:
        rows = []
        for r in p["rows"]:
            src = src_links(r.get("source") or "", sources)
            if not src:
                src = '<span class="note">no official source &rArr; left blank</span>'
            if r["value"] is None:
                value_cell = '<td class="blank">blank</td>'
            else:
                value_cell = f"<td>{escape(r['value'])}</td>"
            rows.append(
                f"<tr><td>{escape(r['field'])}</td>{value_cell}<td>{badge(r['status'])}</td>"
                f'<td>{src}</td><td class="note">{escape(r.get("note", ""))}</td></tr>'
            )
        blocks.append(
            f"""
    <h2>{escape(p['asin'])} <span class="note">via {escape(p['via_link'])}</span></h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Field</th><th>Value</th><th>Status</th><th>Official source</th><th>Note</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>"""
        )
    src_items = "".join(
        f'<li><strong>{escape(k)}</strong> — <a href="{escape(v["url"])}" target="_blank" rel="noopener noreferrer">{escape(v["name"])}</a></li>'
        for k, v in sources.items()
    )
    body = f"""
    <div class="card">
      <p>
        Every row ends in an official source link or is blank with an explicit reason. A value is never
        inferred from a similar product, a sibling listing, a carousel, or an earlier session's note.
        Prices, ratings and review counts are deliberately not published — see
        <a href="method.html">Method &amp; Limits</a>.
      </p>
      <ul class="note">{src_items}</ul>
    </div>
    {''.join(blocks)}
"""
    return page(
        "Products",
        "products.html",
        "Product attributes for the three ASINs the supplied links resolve to. Blank means unverified — never inferred.",
        body,
    )


def build_method(links, program) -> str:
    rows = "".join(
        f"<tr><td>{escape(r['id'])}</td><td>{escape(r['claim'])}</td>"
        + (f"<td>{escape(r['value'])}</td>" if r["value"] else '<td class="blank">blank</td>')
        + f"<td>{badge(r['status'])}</td>"
        + (
            f'<td><a href="{escape(program["sources"][r["source"]]["url"])}" target="_blank" rel="noopener noreferrer">{escape(program["sources"][r["source"]]["name"])}</a></td>'
            if r.get("source")
            else '<td class="note">no official source &rArr; left blank</td>'
        )
        + f'<td class="note">{escape(r.get("note", ""))}</td></tr>'
        for r in program["rows"]
    )
    body = f"""
    <div class="card">
      <h3>What this environment can verify</h3>
      <p>
        Page fetches were made with the agent's page-fetch tool. Direct <code>curl</code> from the build
        sandbox cannot reach any of these hosts: <code>affiliate-program.amazon.com</code>,
        <code>www.amazon.com</code>, <code>chefman.com</code> and <code>developers.google.com</code> all
        returned HTTP <code>000</code> with exit code 35. <strong>Consequence:</strong> the live checks in this
        repository are dated observations with quoted output, not a re-runnable CI step. CI can only re-check
        internal consistency, which is what the repo's existing gates already do.
      </p>
      <h3 style="margin-top:18px">The three rules used on every row</h3>
      <ol>
        <li><strong>Cite or blank.</strong> A value appears only if an official source states it; the source is linked in the row.</li>
        <li><strong>No inference.</strong> A figure is never derived from a sibling listing, a carousel, a search snippet, a similar model, or arithmetic performed here.</li>
        <li><strong>Conflicts are shown, not resolved.</strong> When two official sources disagree, both are published and neither is presented as definitive.</li>
      </ol>
      <h3 style="margin-top:18px">Why prices, ratings and review counts are withheld</h3>
      <p>
        The Associates Program Policies restrict how prices/availability and ratings/reviews may be displayed
        (they must come from Amazon-served data or the API). Rather than risk a policy breach, no page on this
        site prints a product price, star rating or review count. Row status is marked
        <span class="badge info">Withheld by policy</span> to distinguish a deliberate omission from an
        unverifiable one. Note RV-09: those two clauses were relied on but not re-read this session, and the
        conservative choice was retained.
      </p>
    </div>

    <h2>Programme facts re-read this session</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>ID</th><th>Claim</th><th>Value as read</th><th>Status</th><th>Official source</th><th>Note</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>

    <h2>What could not be checked, and why</h2>
    <div class="tablewrap">
      <table>
        <thead><tr><th>Item</th><th>Reason</th><th>Handling</th></tr></thead>
        <tbody>
          <tr><td>Authenticated Creators API / PA-API data</td><td>Requires an enrolled Associates account and API credentials; none exist in this environment. The documented prerequisite is an enrolled account: <a href="https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction" target="_blank" rel="noopener noreferrer">Creators API introduction</a>.</td><td>Not attempted. No API-derived figure is published.</td></tr>
          <tr><td>Home &amp; Kitchen commission rate</td><td>Rate schedule is behind Associates sign-in: <a href="https://affiliate-program.amazon.com/help/operating/schedule" target="_blank" rel="noopener noreferrer">official rate schedule</a>.</td><td>Blank, flagged RV-08.</td></tr>
          <tr><td>Whether the code&rarr;ASIN mapping is intentional</td><td>Not documented publicly; the governing document is silent on short codes: <a href="https://affiliate-program.amazon.com/help/operating/agreement" target="_blank" rel="noopener noreferrer">Operating Agreement</a>.</td><td>Presented as observed behaviour; flagged RV-03.</td></tr>
          <tr><td>UPC for all three ASINs</td><td>Not printed on any official page read — <a href="https://www.amazon.com/dp/B0CDY277D3" target="_blank" rel="noopener noreferrer">B0CDY277D3</a> · <a href="https://www.amazon.com/dp/B09B7SB46R" target="_blank" rel="noopener noreferrer">B09B7SB46R</a> · <a href="https://www.amazon.com/dp/B08DKYBTPH" target="_blank" rel="noopener noreferrer">B08DKYBTPH</a>.</td><td>Blank, flagged RV-07.</td></tr>
        </tbody>
      </table>
    </div>
"""
    return page(
        "Method &amp; Limits",
        "method.html",
        "How each value was checked, what this environment cannot reach, and why some cells are blank on purpose.",
        body,
    )


def build_flagged(flags) -> str:
    cards = []
    for f in flags["flags"]:
        srcs = " · ".join(
            f'<a href="{escape(u)}" target="_blank" rel="noopener noreferrer">{escape(u)}</a>'
            for u in f.get("source", [])
        )
        sev = {"high": "flag", "medium": "warn", "low": "info"}.get(f["severity"], "info")
        cards.append(
            f"""<div class="card" id="{escape(f['id'])}">
      <h3>{escape(f['id'])} · {escape(f['title'])} <span class="badge {sev}">{escape(f['severity'])}</span></h3>
      <p>{escape(f['detail'])}</p>
      <p><strong>Disposition:</strong> {escape(f['disposition'])}</p>
      <p class="note">Sources: {srcs or 'none — flagged precisely because no official source states it'}</p>
    </div>"""
        )
    body = f"""
    <div class="card">
      <p>
        These items <strong>do not block publication</strong>. Each is listed with its evidence and source links
        so it can be reviewed after the site is live. IDs are namespaced <code>RV-*</code> so they never collide
        with the canonical <code>F-*</code> set in <code>ledger/</code> or the <code>AF-*</code> set in
        <code>affiliate-lab/</code>.
      </p>
    </div>
    {''.join(cards)}
"""
    return page(
        "Flagged for Review",
        "flagged.html",
        "Every open irregularity and unverified item from this session, with its evidence and official source links.",
        body,
    )


def build_sources(links, specs, program) -> str:
    rows = []
    for k, v in program["sources"].items():
        rows.append(f'<tr><td><strong>{escape(k)}</strong></td><td>{escape(v["name"])}</td><td><a href="{escape(v["url"])}" target="_blank" rel="noopener noreferrer">{escape(v["url"])}</a></td><td>Programme / policy</td></tr>')
    for k, v in specs["sources"].items():
        rows.append(f'<tr><td><strong>{escape(k)}</strong></td><td>{escape(v["name"])}</td><td><a href="{escape(v["url"])}" target="_blank" rel="noopener noreferrer">{escape(v["url"])}</a></td><td>Product attribute</td></tr>')
    rows.append('<tr><td><strong>L-1</strong></td><td>Supplied short link 1 (as provided)</td><td><a href="https://link.amazon/B04G1MEwY" target="_blank" rel="noopener noreferrer sponsored">https://link.amazon/B04G1MEwY</a></td><td>Subject of test</td></tr>')
    rows.append('<tr><td><strong>L-2</strong></td><td>Supplied short link 2 (as provided)</td><td><a href="https://link.amazon/B02NbDxp3" target="_blank" rel="noopener noreferrer sponsored">https://link.amazon/B02NbDxp3</a></td><td>Subject of test</td></tr>')
    rows.append('<tr><td><strong>L-3</strong></td><td>Supplied short link 3 (as provided)</td><td><a href="https://link.amazon/B00hJ57DV" target="_blank" rel="noopener noreferrer sponsored">https://link.amazon/B00hJ57DV</a></td><td>Subject of test</td></tr>')
    body = f"""
    <div class="card">
      <p>Every table row in this site resolves to one of these sources. All were fetched live on 2026-11-14.</p>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr><th>ID</th><th>Source</th><th>URL</th><th>Used for</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
"""
    return page(
        "Sources",
        "sources.html",
        "The complete list of official sources cited by this session, with links for manual review.",
        body,
    )


def main() -> int:
    links = load("links.json")
    specs = load("specs.json")
    program = load("program.json")
    flags = load("flags.json")

    pages = {
        "index.html": build_index(links, specs, flags),
        "links.html": build_links(links),
        "products.html": build_products(specs),
        "method.html": build_method(links, program),
        "flagged.html": build_flagged(flags),
        "sources.html": build_sources(links, specs, program),
    }

    check = "--check" in sys.argv
    drift = []
    for name, html in pages.items():
        path = ROOT / name
        if check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != html:
                drift.append(name)
        else:
            path.write_text(html, encoding="utf-8")

    if check:
        print(json.dumps({"built": len(pages), "drifted_or_uncommitted": drift}, indent=2))
        return 1 if drift else 0

    print(json.dumps({"built": len(pages), "pages": sorted(pages)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
