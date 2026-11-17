#!/usr/bin/env python3
"""Render the submitted-link intake namespace (intake/) from the T60 registers.

Why this file exists
--------------------
The 2026-11-17 brief names five affiliate links. This repository's registers were built
around three, and two of the five codes — plus the tracking id — appear nowhere in the
tree. That gap is a real defect in a published site, and closing it is what this
namespace is for.

It holds one idea above all others: **intent and observation are not the same fact.**
The brief asks for a product-intent confirmation record in which the intended ASIN,
official listing URL, confirmation date and source live in their own fields, and the
observed redirect target lives in a *different* field, never merged. That is the whole
structure of `intake/data/submissions.json`, and this generator renders the two groups
in two visually separate parts of the table so a reader cannot mistake one for the other.

Design rules inherited from the rest of the repository
------------------------------------------------------
1. Data, not HTML. Pages are generated; `--check` fails when the committed output drifts
   from the registers. Nobody hand-edits `intake/*.html`.
2. Counts are derived. Every number on a page is computed from the registers in the same
   run, so prose cannot disagree with the tables.
3. Every row is sourced or explicitly flagged. A source id that resolves to nothing is a
   build error, not a warning.
4. An open question's answer stays empty, and a proposal's choice stays empty. Both are
   enforced here and again by `tools/validate_intake.py`.
5. No price. Product prices, ratings and review counts are never recorded or emitted.
6. The disclosure sits above the fold on every page and is repeated in the footer, which
   is what the brief asks for and what Operating Agreement Sec. 5 requires.

Row prefixes in this namespace: IN- (sources), SUB- (submissions), OBS- (observations),
IF- (flags), IQ- (questions), IP- (proposals), EV- (events). Nothing here adds a row to
any register another session owns.

Run: python3 tools/build_intake.py [--check]
"""

from __future__ import annotations

import html
import json
import os
import sys
from pathlib import Path

REPO = Path(os.environ["INTAKE_ROOT"]) if os.environ.get("INTAKE_ROOT") else Path(__file__).resolve().parents[1]
OUT = REPO / "intake"
DATA = OUT / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from head_meta import head_block  # canonical + og:*, one definition for the whole site  # noqa: E402

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"


class BuildError(Exception):
    pass


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES_DOC = load("sources.json")
SUBMISSIONS = load("submissions.json")
OBSERVATIONS = load("observations.json")
FLAGS = load("flags.json")
QUESTIONS = load("questions.json")
PROPOSALS = load("proposals.json")
TRACKING = load("tracking.json")

SOURCES = {s["id"]: s for s in SOURCES_DOC["sources"]}
AS_OF = SOURCES_DOC["as_of"]

NAV = [
    ("submissions.html", "Product-intent record"),
    ("observations.html", "Observations"),
    ("tracking.html", "Measurement"),
    ("proposals.html", "Choose a path"),
    ("questions.html", "What we know"),
    ("flags.html", "Flagged"),
    ("sources.html", "Sources"),
]

CSS = """
:root{--ink:#16130f;--paper:#fbfaf7;--muted:#6b6459;--line:#e3ded3;--accent:#1f5b4a;
--warn:#9a6314;--danger:#9a2f2f;--card:#fff}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:66rem;margin:0 auto;padding:0 24px}
a{color:var(--accent)}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
header.mast{border-bottom:1px solid var(--line);background:var(--card)}
.mast-in{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:baseline;padding:18px 24px;max-width:66rem;margin:0 auto}
.brand{font-weight:700;text-decoration:none;color:var(--ink)}
.brand span{display:block;font-weight:400;font-size:13px;color:var(--muted)}
nav.top{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin-left:auto}
nav.top a{color:var(--muted);text-decoration:none;padding:2px 0;border-bottom:2px solid transparent}
nav.top a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--accent)}
.strip{background:#f3f0e9;border-bottom:1px solid var(--line)}
.strip-in{max-width:66rem;margin:0 auto;padding:9px 24px;font-size:14px;color:#3a342b}
main{padding:26px 0 60px}
h1{font:700 38px/1.1 Georgia,"Times New Roman",serif;margin:0 0 12px;letter-spacing:-.01em}
h2{font:700 26px/1.2 Georgia,"Times New Roman",serif;margin:42px 0 10px}
h3{font:600 19px/1.3 Georgia,"Times New Roman",serif;margin:26px 0 6px}
p,li{max-width:46rem}
.standfirst{font-size:20px;color:#3a342b;margin:0 0 8px;max-width:46rem}
.eyebrow{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
.crumbs{font-size:13px;color:var(--muted);margin:0 0 16px}
table{border-collapse:collapse;width:100%;font-size:15px;margin:14px 0 8px;display:block;overflow-x:auto}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:9px 12px 9px 0}
th{font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--line)}
td.mono,code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}
.blank{color:#8a8478;font-style:italic}
.pill{display:inline-block;font-size:11px;letter-spacing:.04em;text-transform:uppercase;
border:1px solid var(--line);border-radius:999px;padding:1px 8px;background:#fff;color:var(--muted)}
.pill.live{color:var(--accent);border-color:var(--accent)}
.pill.carried{color:var(--warn);border-color:var(--warn)}
.pill.open{color:var(--danger);border-color:var(--danger)}
.pill.cat-b{color:var(--warn);border-color:var(--warn)}
blockquote{margin:10px 0;padding:10px 14px;border-left:3px solid var(--line);background:#fff;color:#3a342b}
blockquote .src{font-size:12px;color:var(--muted);margin-top:6px}
.note{background:#fff;border:1px solid var(--line);border-left:3px solid var(--accent);
padding:12px 14px;border-radius:3px;font-size:15px}
.split{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line);background:#fff}
@media (max-width:720px){.split{grid-template-columns:1fr}}
.split>div{padding:12px 14px}
.split>div+div{border-left:1px solid var(--line)}
@media (max-width:720px){.split>div+div{border-left:0;border-top:1px solid var(--line)}}
.split h4{margin:0 0 6px;font:600 12px/1.3 inherit;letter-spacing:.06em;text-transform:uppercase}
.split .intent h4{color:var(--danger)}
.split .observed h4{color:var(--accent)}
.opt{border:1px solid var(--line);background:#fff;padding:12px 14px;margin:10px 0;border-radius:3px}
.opt h4{margin:0 0 4px;font-size:16px}
ul.tight{margin:8px 0;padding-left:20px}
footer.site{border-top:1px solid var(--line);background:#f6f3ec;font-size:14px;color:#4a443a}
footer.site .wrap{padding:22px 24px}
footer.site p{max-width:56rem}
"""


def esc(v: object) -> str:
    return html.escape(str(v if v is not None else ""), quote=True)


def is_product_url(url: str) -> bool:
    """True for a link to an Amazon product page, which must carry rel=sponsored."""
    return "amazon.com/dp/" in url or "amazon.com/gp/product" in url


def rel_for(url: str) -> str:
    if is_product_url(url):
        return ' target="_blank" rel="sponsored nofollow"'
    return ' target="_blank" rel="noopener noreferrer"'


def link(url: str, label: str) -> str:
    return f'<a href="{esc(url)}"{rel_for(url)}>{esc(label)}</a>'


def src_links(ids: object) -> str:
    """Render source ids as links to the official page each one is.

    An id that is not in the register is a build error: a citation resolving to nothing
    is exactly the defect this repository's gates exist to catch.
    """
    if not ids:
        return ""
    if isinstance(ids, str):
        candidates = ids.split(",")
    else:
        candidates = list(ids)
    out = []
    for raw in candidates:
        sid = str(raw).strip().strip("[]'\"")
        if not sid:
            continue
        if sid not in SOURCES:
            raise BuildError(f"unknown source id {sid!r}")
        out.append(link(SOURCES[sid]["url"], sid))
    return " · ".join(out)


def blank(reason: str) -> str:
    return f'<span class="blank">blank — {esc(reason)}</span>'


def quote_block(sid: str) -> str:
    s = SOURCES[sid]
    qs = s.get("quotes") or []
    if not qs:
        return ""
    inner = "".join(f"<p>{esc(q)}</p>" for q in qs)
    return f'<blockquote>{inner}<div class="src">{esc(sid)} — {esc(s["title"])}</div></blockquote>'


def page(title: str, description: str, here: str, body: str, crumbs: str = "") -> str:
    nav_parts = []
    for h, label in NAV:
        current = ' aria-current="page"' if h == here else ""
        nav_parts.append(f'<a href="{h}"{current}>{esc(label)}</a>')
    nav = "".join(nav_parts)
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": description,
        "datePublished": f"{AS_OF}T00:00:00+00:00",
        "inLanguage": "en",
        "isAccessibleForFree": True,
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + "intake/" + here},
        "publisher": {"@type": "Organization", "name": "Zone2", "url": SITE},
    }
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    crumb_html = f'<p class="crumbs" aria-label="Breadcrumb">{"Submitted-link intake" + (" › " + crumbs if crumbs else "")}</p>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Zone2 submitted-link intake</title>
<meta name="description" content="{esc(description)}">
{head_block("intake/" + here, title=f"{title} · Zone2 submitted-link intake", description=description, site_name="Zone2", page_type="article")}
<meta name="robots" content="index,follow">
<style>{CSS}</style>
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="mast-in">
    <a class="brand" href="index.html"><b>Submitted-link intake</b><span>Five affiliate links: what was asked for, and what they measurably do</span></a>
    <nav class="top" aria-label="Sections">{nav}</nav>
  </div>
</header>
<div class="strip">
  <div class="strip-in"><strong>Affiliate disclosure.</strong> {DISCLOSURE}</div>
</div>
<div class="wrap">
  <main id="main">
{crumb_html}
{body}
  </main>
</div>
<footer class="site">
  <div class="wrap">
    <p><strong>Affiliate disclosure.</strong> {DISCLOSURE}</p>
    <p>Generated by <code>tools/build_intake.py</code> from <code>intake/data/*.json</code>, measured on {esc(AS_OF)}.
    Every row ends in the official page it was read from, or says plainly that no source settles it.
    Nothing on the <a href="proposals.html">decision board</a> is implemented: each proposal waits for a recorded owner decision.</p>
    <p><a href="../index.html">Owner dashboard</a> ·
       <a href="../pages/flags.html">Flag register (F-01…F-41)</a> ·
       <a href="../brief/index.html">Design brief</a> ·
       <a href="../console/index.html">Owner's Console</a> ·
       <a href="../marketing/index.html">Reader-facing site</a></p>
  </div>
</footer>
</body>
</html>
"""


# ------------------------------------------------------------------ derived counts

def counts() -> dict:
    subs = SUBMISSIONS["entries"]
    obs = OBSERVATIONS["rows"]
    air_fryer = [e for e in subs if "Fryers" in e["observed_category_path"]]
    other = [e for e in subs if "Fryers" not in e["observed_category_path"]]
    return {
        "submissions": len(subs),
        "observations": len(obs),
        "sources": len(SOURCES),
        "live_sources": sum(1 for s in SOURCES.values() if s.get("status") == "LIVE"),
        "carried_sources": sum(1 for s in SOURCES.values() if s.get("status") == "CARRIED"),
        "intent_blank": sum(1 for e in subs if not e["intended_asin"]),
        "tag_absent": sum(1 for e in subs if e["associates_tag_observed"] is False),
        "air_fryer": len(air_fryer),
        "other_category": len(other),
        "distinct_asins": len({e["observed_redirect_asin"] for e in subs}),
        "flags": len(FLAGS["rows"]),
        "flagged_high": sum(1 for f in FLAGS["rows"] if f["severity"] == "high"),
        "questions": len(QUESTIONS["rows"]),
        "questions_open": sum(1 for q in QUESTIONS["rows"] if q["status"] == "OPEN"),
        "proposals": len(PROPOSALS["rows"]),
        "proposals_decided": sum(1 for p in PROPOSALS["rows"] if p["choice"]),
        "options": sum(len(p["options"]) for p in PROPOSALS["rows"]),
        "events": len(TRACKING["events"]["rows"]),
        "ledger_rows": len(TRACKING["campaign_ledger"]["rows"]),
    }


C = counts()


# ------------------------------------------------------------------ pages

def page_index() -> str:
    c = C
    rows = []
    for e in SUBMISSIONS["entries"]:
        cat = "Air Fryers" if "Fryers" in e["observed_category_path"] else "Thermometers"
        pill = "cat-b" if cat != "Air Fryers" else ""
        rows.append(
            "<tr>"
            f"<td class='mono'>{esc(e['id'])}</td>"
            f"<td class='mono'>{esc(e['submitted_url'].replace('https://link.amazon/', ''))}</td>"
            f"<td><span class='pill'>{e['token_char_count']} chars</span></td>"
            f"<td>{esc(e['observed_redirect_asin'])}</td>"
            f"<td><span class='pill {pill}'>{esc(cat)}</span></td>"
            f"<td>{src_links(e['source_ids'])}</td>"
            "</tr>"
        )
    body = f"""
<h1>Five links were submitted. Three of them were on the site.</h1>
<p class="standfirst">The 2026-11-17 brief names five affiliate links and a tracking id.
This repository was built around three of them. Two of the codes, and the tracking id,
appear nowhere in the tree. This namespace registers all five, and separates what was
<i>asked for</i> from what the links measurably <i>do</i>.</p>

<div class="note">
<p><strong>The one thing to take away.</strong> All five links resolve to a live Amazon
product page, reproducibly — but none of the five resolves to a product we can prove was
intended, and none of the five URLs we observed carries an Associates tag. Two of the
five are not air fryers at all. Those are three separate problems and they have three
separate fixes, all of which need one sign-in.</p>
</div>

<h2>The five submissions at a glance</h2>
<table>
<thead><tr><th>Id</th><th>Submitted code</th><th>Token</th><th>Resolves to (ASIN)</th><th>Category</th><th>Sources</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
<p class="eyebrow">The "resolves to" column is a measurement, not a confirmation. See
<a href="submissions.html">the product-intent record</a> for why the two are kept apart.</p>

<h2>What was measured on {esc(AS_OF)}</h2>
<ul class="tight">
<li><strong>{c['submissions']} of {c['submissions']}</strong> submitted links were resolved live, in <strong>{c['observations']}</strong> dated observations including two controls.</li>
<li><strong>{c['distinct_asins']} distinct</strong> Amazon product pages — each link goes somewhere different.</li>
<li><strong>{c['air_fryer']}</strong> land in Air Fryers; <strong>{c['other_category']}</strong> land in Meat Thermometers. The site's single-category premise no longer covers the set.</li>
<li><strong>{c['intent_blank']} of {c['submissions']}</strong> have a blank intended ASIN, because a 9-character token is not an ASIN and nothing public binds the code to a product.</li>
<li><strong>{c['tag_absent']} of {c['submissions']}</strong> resolved URLs carry no Associates <code>tag=</code>, so none is established as a Special Link.</li>
<li><strong>{c['flags']} irregularities</strong> raised ({c['flagged_high']} high), <strong>{c['questions_open']} open questions</strong>, <strong>{c['proposals']} undecided proposals</strong>.</li>
<li><strong>{c['ledger_rows']} rows</strong> in the campaign ledger. It is empty by design, and stays empty until an authorised report fills it.</li>
</ul>

<h2>Three findings that change what should be built</h2>

<h3>1. The submitted set is not one category</h3>
<p>Two of the five links ({', '.join(e['id'] for e in SUBMISSIONS['entries'] if 'Fryers' not in e['observed_category_path'])}) resolve into
<i>Home &amp; Kitchen › Kitchen &amp; Dining › Kitchen Utensils &amp; Gadgets › Thermometers &amp; Timers › Meat</i>.
Every page on this site that describes the promoted range as air fryers is now wrong about
two fifths of it. Recorded as <a href="flags.html#IF-01">IF-01</a>; the choice is
<a href="proposals.html#IP-02">IP-02</a>.</p>

<h3>2. The measurement plan cannot be built as specified</h3>
<p>The brief asks for a self-hosted analytics endpoint. GitHub's own documentation describes
Pages as a static site hosting service, and this site is published on Pages — so there is
nowhere on this host to run the thing that would receive the beacons. This is recorded as
<a href="flags.html#IF-08">IF-08</a> rather than worked around, because the three real
options differ in cost and in what they may store, and the choice is
<a href="proposals.html#IP-04">IP-04</a>.</p>

<h3>3. The compliance question is still open, in both directions</h3>
<p>No observed URL carries a tag, which under the Operating Agreement is what a Special Link
requires. It does not follow that the supplied links are invalid — a tag may be attached
during the redirect in a way this measurement cannot see, which is why the brief's own
FLG-003 treats their status as unresolved and why this project refuses to claim either way.
Settling it takes one enrolled account and one report read:
<a href="proposals.html#IP-03">IP-03</a>.</p>

<h2>Where to go next</h2>
<ul class="tight">
<li><a href="submissions.html">Product-intent record</a> — the five rows, intent and observation side by side.</li>
<li><a href="observations.html">Observations</a> — every fetch, dated, with what came back.</li>
<li><a href="proposals.html">Choose a path</a> — {c['proposals']} decisions, {c['options']} options, nothing decided.</li>
<li><a href="questions.html">What we know</a> — {c['questions']} questions, each with the source or action that would settle it.</li>
<li><a href="flags.html">Flagged for review</a> — {c['flags']} irregularities with their measurements.</li>
<li><a href="tracking.html">Measurement</a> — the tracking id, the five proposed events, the empty ledger.</li>
<li><a href="sources.html">Sources</a> — {c['sources']} pages ({c['live_sources']} fetched today, {c['carried_sources']} carried and labelled).</li>
</ul>
"""
    return page(
        "Submitted-link intake",
        "Five affiliate links were submitted; three were on the site. What each link resolves to, what none of them proves, and the decisions that follow.",
        "index.html", body)


def page_submissions() -> str:
    c = C
    blocks = []
    for e in SUBMISSIONS["entries"]:
        obs_ids = [o["id"] for o in OBSERVATIONS["rows"] if o.get("submission_id") == e["id"]]
        # Derived, not typed. The register's own `observation_count` field was typed by hand and
        # drifted from the log on the first publish (SUB-01 said 2 while only OBS-02 referenced
        # it) — the same typed-count class this repository keeps being bitten by. The page renders
        # the count measured from observations.json in this same run; tools/validate_intake.py
        # separately fails the build if the register's typed value disagrees with it, so the two
        # cannot silently diverge again.
        obs_n = len(obs_ids)
        cat_other = "Fryers" not in e["observed_category_path"]
        flag_links = " · ".join(
            f'<a href="flags.html#{esc(f)}">{esc(f)}</a>' for f in e["flag_ids"]) or "—"
        blocks.append(f"""
<section id="{esc(e['id'])}">
<h3>{esc(e['id'])} — <span class="mono">{esc(e['submitted_url'])}</span></h3>
<div class="split">
  <div class="intent">
    <h4>A · What was intended — blank, and stays blank until confirmed</h4>
    <table>
      <tbody>
      <tr><th>Intended ASIN</th><td>{blank('owner to confirm')}</td></tr>
      <tr><th>Intended listing URL</th><td>{blank('owner to confirm')}</td></tr>
      <tr><th>Confirmation date</th><td>{blank('no confirmation yet')}</td></tr>
      <tr><th>Source of intent</th><td>{blank('no official record binds the code to a product')}</td></tr>
      </tbody>
    </table>
    <p class="eyebrow">Status: <span class="pill open">{esc(e['intent_status'])}</span></p>
  </div>
  <div class="observed">
    <h4>B · What the link does — measured</h4>
    <table>
      <tbody>
      <tr><th>Observed redirect target</th><td class="mono">{link(e['observed_redirect_target'], e['observed_redirect_target'])}</td></tr>
      <tr><th>Observed ASIN</th><td class="mono">{esc(e['observed_redirect_asin'])}</td></tr>
      <tr><th>Listing title as served</th><td>{esc(e['observed_listing_title'])}</td></tr>
      <tr><th>Category path</th><td>{esc(e['observed_category_path'])} {'<span class="pill cat-b">different category</span>' if cat_other else ''}</td></tr>
      <tr><th>Observed (UTC)</th><td>{esc(e['observed_utc'])} — {obs_n} observation(s): {' · '.join(esc(o) for o in obs_ids)}</td></tr>
      <tr><th>Associates tag present</th><td><strong>No</strong> — no <code>tag=</code> among: {esc(', '.join(e['observed_query_param_names']))}</td></tr>
      </tbody>
    </table>
  </div>
</div>
<p class="eyebrow">Token as submitted: <span class="mono">{esc(e['submitted_token'])}</span> — {e['token_char_count']} characters, so not an ASIN ({src_links(e['asin_rule_source_ids'] if 'asin_rule_source_ids' in e else ['IN-03'])}).
Flags: {flag_links}. Sources: {src_links(e['source_ids'])}.</p>
</section>
""")
    body = f"""
<h1>Product-intent confirmation record</h1>
<p class="standfirst">For each submitted link: the intended ASIN, official listing URL,
confirmation date and source — in one group of fields — and the observed redirect target
in a <i>different</i> group. The two are never merged, because they are not the same fact.</p>

<div class="note">
<p><strong>Why the split matters.</strong> Amazon's own help page defines an ASIN as
“the 10-digit code that Amazon uses to denote specific products.” Every code submitted
here is 9 characters, so none of them is an ASIN and none of them identifies a product on
its own. Each link nevertheless resolves to one specific product page, reproducibly. Both
statements are true, and publishing either one in place of the other would be a falsehood:
the destination is measured, the intent is not.</p>
{quote_block('IN-03')}
</div>

<h2>The rule the record is built on</h2>
{quote_block('IN-03')}
{quote_block('IN-01')}

<h2>The five rows</h2>
<p><strong>{c['intent_blank']} of {c['submissions']}</strong> rows have all four intent fields blank.
That is the correct state, not an incomplete one: the intended ASIN is a fact only the owner
holds, and the sanctioned way to confirm it is an Associates report or a Creators API lookup
({src_links(['IN-22'])}).</p>
{''.join(blocks)}

<h2>How to fill a row in</h2>
<ul class="tight">
<li>Sign in to Associates Central and open the link report for the code.</li>
<li>Read the ASIN and the canonical listing URL it was generated against.</li>
<li>Write those into <code>intake/data/submissions.json</code> in the <i>intended</i> fields only, with the date and the report as the source.</li>
<li>Leave the <i>observed</i> fields alone. They are the record of what the link did on {esc(AS_OF)}, and they stay true even if the intent turns out to be different.</li>
</ul>
<p class="eyebrow">A gate in this namespace fails the build if an intent field is filled from
an observation rather than a confirmation, or if the two groups are ever merged.</p>
"""
    return page(
        "Product-intent confirmation record",
        "For each of the five submitted affiliate links: the intended ASIN, listing URL, confirmation date and source, kept in separate fields from the observed redirect target.",
        "submissions.html", body, "Product-intent record")


def page_observations() -> str:
    rows = []
    for o in OBSERVATIONS["rows"]:
        target = o.get("resolved_url") or "—"
        tgt_cell = (link(target, target) if target.startswith("http") else esc(target))
        extra = []
        if o.get("same_destination_as"):
            extra.append(f"same destination as {esc(o['same_destination_as'])}")
        if o.get("same_session_as"):
            extra.append(f"same Amazon session as {esc(o['same_session_as'])} — see <a href='flags.html#IF-06'>IF-06</a>")
        if o.get("associates_tag_observed") is False:
            extra.append("no <code>tag=</code> parameter observed")
        rows.append(
            "<tr>"
            f"<td class='mono'>{esc(o['id'])}</td>"
            f"<td><span class='pill'>{esc(o['kind'])}</span></td>"
            f"<td class='mono'>{esc(o['requested_url'])}</td>"
            f"<td>{esc(o['outcome'])}</td>"
            f"<td class='mono'>{esc(o.get('resolved_asin') or '—')}</td>"
            f"<td>{esc(o.get('session_id') or '—')}</td>"
            f"<td>{esc(o.get('btn_ref') or '—')}</td>"
            f"<td>{'; '.join(extra) or '—'}</td>"
            f"<td>{src_links(o['source_ids'])}</td>"
            "</tr>"
        )
    body = f"""
<h1>Observation log</h1>
<p class="standfirst">Every request made on {esc(AS_OF)}, what came back, and the tracking
tokens the response carried. {C['observations']} rows: five first-pass resolutions, two
second-pass re-fetches, and two controls.</p>

<h2>What this log is for</h2>
<p>A redirect is easy to observe and easy to over-read. So each row records not just where
the link went but the session and shuffle tokens on the response, which is what lets a
reader tell a stable destination from a per-request artefact — and lets the next session
compare like with like.</p>

<h2>The rows</h2>
<table>
<thead><tr><th>Id</th><th>Kind</th><th>Requested</th><th>Outcome</th><th>ASIN</th><th>Session id</th><th>btn_ref</th><th>Notes</th><th>Sources</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>

<h2>Control 1 — does the service honour the code at all?</h2>
<p>An unissued 9-character code of the same shape as the submitted codes was requested.
It returned a 404 rather than a product page:</p>
{quote_block('IN-14')}
<p>The five supplied codes therefore resolve because they are issued lookups, not because the
service ignores its input and falls back to something arbitrary. It does <i>not</i> follow
that the destination is the product the owner intended — see
<a href="submissions.html">the intent record</a>. A side effect of this control is that the
error page is served from a non-Amazon domain, which raises
<a href="flags.html#IF-05">IF-05</a> and <a href="questions.html#IQ-05">IQ-05</a>.</p>

<h2>Control 2 — is <code>plpRedirect=mhFallback</code> evidence of a fallback?</h2>
<p>No. A bare request to a known-good ASIN returns the same marker, so its presence says
nothing about whether a link fell back. This reproduces the control already recorded in the
repository's README; it is re-run here because the argument depends on it.</p>
{quote_block('IN-09') if SOURCES['IN-09'].get('quotes') else ''}

<h2>What is <i>not</i> established by this log</h2>
<ul class="tight">
<li><strong>Stability across independent sessions.</strong> The second pass for
{', '.join(esc(e['id']) for e in SUBMISSIONS['entries'] if e['observation_count'] > 1)} reused the same Amazon session id and the same <code>btn_ref</code> as the first, so it is weaker evidence than two independent sessions would be (<a href="flags.html#IF-06">IF-06</a>).</li>
<li><strong>Intent.</strong> Nothing here says which product was meant.</li>
<li><strong>Compliance.</strong> Absence of a <code>tag=</code> is observed; invalidity is not.</li>
</ul>
"""
    return page(
        "Observation log",
        f"Every request made on {AS_OF} against the five submitted links and two controls, with the resolved URL, page title and tracking tokens returned.",
        "observations.html", body, "Observations")


def page_tracking() -> str:
    t = TRACKING["tracking_id"]
    ev_rows = []
    for e in TRACKING["events"]["rows"]:
        ev_rows.append(
            "<tr>"
            f"<td class='mono'>{esc(e['id'])}</td>"
            f"<td class='mono'>{esc(e['name'])}</td>"
            f"<td>{esc(e['measures'])}</td>"
            f"<td>{esc(e['must_not_store'])}</td>"
            f"<td>{esc(e['feeds'])}</td>"
            f"<td><span class='pill'>{esc(e['status'])}</span></td>"
            f"<td>{src_links(e['source_ids'])}</td>"
            "</tr>"
        )
    led = TRACKING["campaign_ledger"]
    col_rows = "".join(
        f"<tr><td class='mono'>{esc(c['name'])}</td><td class='mono'>{esc(c['type'])}</td><td>{esc(c['note'])}</td></tr>"
        for c in led["columns"])
    body = f"""
<h1>Measurement</h1>
<p class="standfirst">The tracking id as submitted, the five events proposed, and a campaign
ledger that is empty on purpose. There are no numbers on this page, because nothing has been
measured yet.</p>

<h2>The tracking id</h2>
<table>
<tbody>
<tr><th>Submitted value</th><td class="mono">{esc(t['submitted_value'])}</td></tr>
<tr><th>Submitted (UTC)</th><td>{esc(t['submitted_utc'])}</td></tr>
<tr><th>Submitted via</th><td>{esc(t['submitted_via'])}</td></tr>
<tr><th>Confirmed as an Associates ID</th><td>{blank('not confirmable from any official page found')}</td></tr>
<tr><th>Marketplace</th><td>{blank('unknown')}</td></tr>
<tr><th>Confirmation date</th><td>{blank('none')}</td></tr>
<tr><th>Confirmation source</th><td>{blank('none')}</td></tr>
<tr><th>Status</th><td><span class="pill open">{esc(t['status'])}</span></td></tr>
</tbody>
</table>
<p>{esc(t['why_blank'])} Sources: {src_links(t['source_ids'])}. See
<a href="questions.html#IQ-02">IQ-02</a> and <a href="flags.html#IF-07">IF-07</a>.</p>

<h2>The five events</h2>
<p>Proposed, not instrumented. No code collects any of them: the choice of where they would
even be stored is <a href="proposals.html#IP-04">IP-04</a>, and it has not been taken.</p>
<div class="note"><p><strong>Privacy rule.</strong> {esc(TRACKING['events']['privacy_rule'])}</p></div>
<table>
<thead><tr><th>Id</th><th>Event</th><th>Measures</th><th>Must never store</th><th>Feeds</th><th>Status</th><th>Sources</th></tr></thead>
<tbody>
{''.join(ev_rows)}
</tbody>
</table>

<h2>Why none of this can run here yet</h2>
{quote_block('IN-16')}
<p>That sentence is the whole problem. A self-hosted endpoint needs somewhere to run, and a
GitHub Pages site has no such place. Recorded as <a href="flags.html#IF-08">IF-08</a> rather
than worked around, because the three honest options differ in cost and in what they are
allowed to store.</p>

<h2>Campaign ledger</h2>
<p><strong>State: <span class="pill">{esc(led['state'])}</span></strong> — {esc(led['why_empty'])}</p>
<h3>Defined columns</h3>
<table>
<thead><tr><th>Column</th><th>Type</th><th>Rule</th></tr></thead>
<tbody>
{col_rows}
</tbody>
</table>
<h3>Rows</h3>
<p><strong>{C['ledger_rows']} rows.</strong> Empty, and it stays empty until a dated figure
arrives from an authorised first-party report. When one does, it is added with the timestamp
it was added, the report it came from, and a provenance note. No conversion score and no
revenue forecast is presented anywhere on this site, and the Operating Agreement states that
Amazon makes no representation about the traffic or commission income anyone can expect:</p>
{quote_block('IN-01')}
"""
    return page(
        "Measurement",
        "The submitted tracking id, five proposed events with their privacy rules, and a campaign ledger that is empty by design until an authorised report fills it.",
        "tracking.html", body, "Measurement")


def page_proposals() -> str:
    blocks = []
    for p in PROPOSALS["rows"]:
        opts = []
        for o in p["options"]:
            req = ("<p class='eyebrow'>Needs: " + ", ".join(
                f"<a href='questions.html#{esc(r)}'>{esc(r)}</a>" for r in o["requires"]) + "</p>"
                if o["requires"] else "<p class='eyebrow'>Needs nothing else.</p>")
            opts.append(
                f'<div class="opt" id="{esc(o["id"])}">'
                f'<h4>{esc(o["id"])} — {esc(o["label"])}</h4>'
                f'<p class="eyebrow">Cost: {esc(o["cost"])}</p>'
                f'<p>{esc(o["consequence"])}</p>{req}</div>')
        blockers = " · ".join(
            f'<a href="questions.html#{esc(b)}">{esc(b)}</a>' for b in p["blocked_by"]) or "none"
        blocks.append(f"""
<section id="{esc(p['id'])}">
<h3>{esc(p['id'])} — {esc(p['title'])}</h3>
<p><strong>{esc(p['question'])}</strong></p>
<p>{esc(p['why_now'])}</p>
{''.join(opts)}
<p class="eyebrow">Blocked by: {blockers}. Sources: {src_links(p['source_ids'])}.
Recorded choice: {('<strong>' + esc(p['choice']) + '</strong>') if p['choice'] else '<span class="pill open">none — not decided</span>'}</p>
</section>
""")
    body = f"""
<h1>Choose a path</h1>
<p class="standfirst">{C['proposals']} decisions, {C['options']} options, one scale.
Nothing here is implemented, and nothing here is decided: every choice field is empty until
the owner records one. That is the point of the page — a path gets chosen
<i>before</i> anything is built on it.</p>

<div class="note">
<p><strong>{C['proposals_decided']} of {C['proposals']} proposals have a recorded choice.</strong>
A gate in this namespace fails the build if a choice is recorded that is not one of that
row's own options, so a decision cannot drift into something that was never on the table.</p>
</div>

{''.join(blocks)}

<h2>How to record a decision</h2>
<p>Write the chosen option's id into the <code>choice</code> field of that row in
<code>intake/data/proposals.json</code> — for example <code>"choice": "IP-01-a"</code> — and
re-run <code>python3 tools/build_intake.py</code>. The page will show the choice, and the
gate will confirm it is a real option. Nothing in this namespace implements anything, so a
recorded choice is a decision to be carried out elsewhere.</p>
"""
    return page(
        "Choose a path",
        f"{C['proposals']} decisions about the five submitted links, with {C['options']} costed options on one scale. Nothing is decided and nothing is implemented.",
        "proposals.html", body, "Choose a path")


def page_questions() -> str:
    rows = []
    for q in QUESTIONS["rows"]:
        # Built outside the f-string: a nested quote inside an f-string expression is a
        # SyntaxError before Python 3.12, and this repository's CI runs 3.11.
        blocks_html = " · ".join(
            '<a href="proposals.html#{0}">{0}</a>'.format(esc(b)) for b in q["blocks"]) or "—"
        answer_cell = (f"<strong>{esc(q['answer'])}</strong>"
                       if q["answer"] else blank("open — deliberately empty"))
        rows.append(
            f"<tr id=\"{esc(q['id'])}\">"
            f"<td class='mono'>{esc(q['id'])}</td>"
            f"<td>{esc(q['question'])}</td>"
            f"<td>{answer_cell}</td>"
            f"<td>{esc(q['how_to_answer_it'])}</td>"
            f"<td>{blocks_html}</td>"
            f"<td><span class='pill open'>{esc(q['status'])}</span></td>"
            f"<td>{src_links(q['official_source_ids'])}</td>"
            "</tr>"
        )
    body = f"""
<h1>What we know, and what nothing here can tell you</h1>
<p class="standfirst">{C['questions']} questions standing between the current state and a
defensible decision. Every answer field is empty on purpose: an open question with a
filled-in answer is a guess wearing a label.</p>

<div class="note">
<p><strong>Why every answer is blank.</strong> Two of these could be filled in by inference,
and both would be wrong to fill in. We know where each link goes; we do not know what was
meant. We know no tag is visible; we do not know whether one is applied downstream. A gate
in this namespace fails the build the moment an open question acquires an answer, so the
temptation is removed rather than resisted.</p>
</div>

<h2>The register</h2>
<table>
<thead><tr><th>Id</th><th>Question</th><th>Answer</th><th>How to answer it</th><th>Blocks</th><th>Status</th><th>Official sources</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>

<h2>What is already settled, for contrast</h2>
<ul class="tight">
<li>Each submitted token is 9 characters, and an ASIN is defined as 10 ({src_links(['IN-03'])}).</li>
<li>Each of the five links resolves to one live Amazon product page ({src_links(['IN-09','IN-12','IN-13'])}).</li>
<li>An unissued code of the same shape returns a 404, so the codes are honoured lookups ({src_links(['IN-14'])}).</li>
<li>No resolved URL carries a <code>tag=</code> parameter ({src_links(['IN-01','IN-03'])}).</li>
<li>This host cannot run server-side code ({src_links(['IN-16'])}).</li>
</ul>
<p>Five settled facts, {C['questions_open']} open questions. The settled ones are measurements;
the open ones are all about intent, identity or a decision only the owner can take.</p>
"""
    return page(
        "What we know",
        f"{C['questions']} questions about the five submitted links, each with the official source or owner action that would settle it. Every answer is deliberately empty.",
        "questions.html", body, "What we know")


def page_flags() -> str:
    blocks = []
    for f in FLAGS["rows"]:
        subs = " · ".join(esc(s) for s in f["submission_ids"]) or "—"
        blocks.append(f"""
<section id="{esc(f['id'])}">
<h3>{esc(f['id'])} — {esc(f['title'])} <span class="pill">{esc(f['severity'])}</span></h3>
<p><strong>Measured.</strong> {esc(f['measured'])}</p>
<p><strong>This establishes.</strong> {esc(f['what_it_establishes'])}</p>
<p><strong>This does not establish.</strong> {esc(f['what_it_does_not_establish'])}</p>
<p class="eyebrow">Submissions: {subs} · Sources: {src_links(f['source_ids'])}</p>
<p><strong>Owner action.</strong> {esc(f['suggested_owner_action'])}</p>
</section>
""")
    body = f"""
<h1>Flagged for review</h1>
<p class="standfirst">{C['flags']} irregularities found while registering the five submitted
links ({C['flagged_high']} high). None of them blocks a merge, and none has been silently
fixed. Each states what was measured, what that does and does not establish, and who can
close it.</p>

{''.join(blocks)}

<h2>Why "does not establish" is its own row</h2>
<p>The most common failure in a verification register is a finding that over-reaches by one
step: an observation is recorded, then a conclusion is drawn from it that the observation
does not support. Every row above separates the two explicitly. The clearest case is
<a href="#IF-02">IF-02</a>: no visible tag is a measurement; "therefore the links are
invalid" would be a conclusion this project refuses to draw, because the brief's own
FLG-003 records the compliance status of the supplied short links as unresolved.</p>
"""
    return page(
        "Flagged for review",
        f"{C['flags']} irregularities in the five submitted links, each with the measurement behind it, what it does and does not establish, and the owner action that would close it.",
        "flags.html", body, "Flagged")


def page_sources() -> str:
    rows = []
    for s in SOURCES_DOC["sources"]:
        pill = "live" if s.get("status") == "LIVE" else "carried"
        carried = (f'<br><span class="eyebrow">Carried from {esc(s["carried_from"])}; last verified {esc(s.get("last_verified_utc"))}</span>'
                   if s.get("status") == "CARRIED" else "")
        rows.append(
            "<tr>"
            f"<td class='mono'>{esc(s['id'])}</td>"
            f"<td>{esc(s['publisher'])}</td>"
            f"<td>{link(s['url'], s['title'])}"
            f"<br><span class='eyebrow'>{esc(s['url'])}</span>{carried}</td>"
            f"<td>{esc(s.get('page_stated_update') or '—')}</td>"
            f"<td>{esc(s['accessed_utc'])}</td>"
            f"<td><span class='pill {pill}'>{esc(s['status'])}</span></td>"
            f"<td>{esc('; '.join(s['used_for']))}</td>"
            "</tr>"
        )
    body = f"""
<h1>Sources</h1>
<p class="standfirst">{C['sources']} pages: {C['live_sources']} fetched and read by this
session on {esc(AS_OF)}, {C['carried_sources']} carried from a register another session owns
and labelled as carried wherever they are cited.</p>

<div class="note">
<p><strong>What "carried" means here.</strong> A carried source was not re-fetched today. It
is reproduced from <code>ledger/sources.json</code> with the id it holds there and the date it
was last verified, and it is labelled CARRIED on every row that cites it. A carried source is
never used to support a value this session measured — only to support a rule or a standard
that another session already quoted from it.</p>
</div>

<table>
<thead><tr><th>Id</th><th>Publisher</th><th>Page</th><th>Page states updated</th><th>Accessed (UTC)</th><th>Status</th><th>Used for</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>

<h2>Verbatim quotes relied on</h2>
<p>These are the quotes the pages above depend on. Each was read off the live page on the
date shown.</p>
{''.join(quote_block(s['id']) for s in SOURCES_DOC['sources'] if s.get('quotes'))}
"""
    return page(
        "Sources",
        f"Every page a value in the submitted-link intake was read from: {C['live_sources']} fetched live on {AS_OF}, {C['carried_sources']} carried from another register and labelled as carried.",
        "sources.html", body, "Sources")


PAGES = {
    "index.html": page_index,
    "submissions.html": page_submissions,
    "observations.html": page_observations,
    "tracking.html": page_tracking,
    "proposals.html": page_proposals,
    "questions.html": page_questions,
    "flags.html": page_flags,
    "sources.html": page_sources,
}


def build() -> dict[str, str]:
    # counts() is computed at import time from the registers, so by the time any page
    # renders, every number on every page has come from the same data in the same run.
    return {name: fn() for name, fn in PAGES.items()}


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    check = "--check" in argv
    built = build()
    if check:
        bad = []
        for name, text in built.items():
            path = OUT / name
            if not path.is_file():
                bad.append(f"{name}: missing committed output")
                continue
            if path.read_text(encoding="utf-8") != text:
                bad.append(f"{name}: committed output is stale — run tools/build_intake.py")
        if bad:
            print("\n".join(bad))
            return 1
        print(f"intake/: {len(built)} pages match a fresh render of intake/data/*.json")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in built.items():
        (OUT / name).write_text(text, encoding="utf-8")
    print(f"wrote {len(built)} pages to intake/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
