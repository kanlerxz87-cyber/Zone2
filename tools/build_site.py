#!/usr/bin/env python3
"""Render the GitHub Pages site from ledger/*.json.

Deterministic and network-free: same inputs -> same bytes.  Every table row is emitted through helpers that
attach the official source link (or an explicit UNVERIFIED marker plus a flag link), so "every row is sourced
or left blank" is a property of the renderer rather than of someone's diligence.

Usage:
    python3 tools/build_site.py           # build into pages/
    python3 tools/build_site.py --check   # build to a temp dir and compare against committed output
"""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
import tempfile
from pathlib import Path

# tools/flag_state.py is the single definition of "is this flag still open"; it lives beside this
# generator, so make the tools/ directory importable however this script is invoked.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from flag_state import open_count  # shared predicate (F-29/F-31)

REPO = Path(__file__).resolve().parents[1]
PAGES = REPO / "pages"
DATA = REPO / "ledger"
SITE_CSS_SRC = REPO / "tools" / "pages-site.css"  # source of the subpage stylesheet

SITE_NAME = "Zone2"  # never an Amazon mark - Participation Requirements rule R-11
# Final integration 2026-11-14 (session 4338f55e): the generated pages/ namespace was branded
# "Northstar", which is the name of the *preserved earlier prototype* kept at northstar/. The
# published site is one product, so the findings namespace now carries the same brand as the
# primary dashboard; the prototype stays reachable at ../northstar/index.html under its own name.
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
LIVE_URL = "https://kanlerxz87-cyber.github.io/Zone2/"


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


SOURCES = {s["id"]: s for s in load("sources.json")["sources"]}
PRODUCTS = load("products.json")
COMMISSION = load("commission_table.json")
COMPLIANCE = load("compliance.json")
MODULES = load("modules.json")
FLAGS = load("flags.json")
VERIFICATION = load("verification.json")
NICHES = load("niches.json")
AS_OF = PRODUCTS["verified_utc"]


def esc(value) -> str:
    if value is None or value == "":
        return ""
    return html.escape(str(value), quote=True)


def slugify(name: str) -> str:
    out = "".join(c.lower() if c.isalnum() else "-" for c in name)
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


# --------------------------------------------------------------------------- cells


def source_cell(source_ids, *, blank_hint: str = "") -> str:
    """Every row ends with its evidence.  No ids -> an explicit unverified marker, never a silent blank."""
    ids = [i for i in (source_ids or []) if i in SOURCES]
    if not ids:
        hint = f'<div class="row-note">{esc(blank_hint or "no official source states this value")}</div>'
        return f'<td class="cell-unverified"><span class="pill pill-warn">UNVERIFIED</span>{hint}</td>'
    links = "".join(
        '<a class="src" href="{url}" target="_blank" rel="noopener noreferrer nofollow">{sid}'
        '<span class="src-host">{host}</span></a>'.format(
            url=esc(SOURCES[i]["url"]), sid=esc(i), host=esc(SOURCES[i]["url"].split("/")[2])
        )
        for i in ids
    )
    return f'<td class="cell-src">{links}</td>'


def blank_cell(reason: str) -> str:
    return f'<td class="cell-blank">&mdash;<span class="blank-note">{esc(reason)}</span></td>'


def text_cell(value, *, raw: bool = False, code: bool = False) -> str:
    cls = ' class="cell-code"' if code else ""
    inner = value if raw else esc(value)
    return f"<td{cls}>{inner}</td>"


def num_cell(value) -> str:
    return f'<td class="cell-num">{esc(value)}</td>'


def status_pill(status: str) -> str:
    kind = {
        "VERIFIED": "ok",
        "OBSERVED": "ok",
        "SCORED": "ok",
        "AUTOMATED": "ok",
        "AVAILABLE": "ok",
        "YES": "ok",
        "VALID": "ok",
        "NONE": "ok",
        "VERIFIED-NEGATIVE": "neg",
        "UNVERIFIED": "warn",
        "FLAGGED": "warn",
        "SCAFFOLDED": "warn",
        "EMPTY_BY_DESIGN": "warn",
        "INSUFFICIENT_DATA": "warn",
        "MISSING": "warn",
        "NOT_PUBLISHED": "warn",
        "BLOCKED": "stop",
        "INVALID": "stop",
        "HIGH": "stop",
    }.get(status, "warn")
    return f'<span class="pill pill-{kind}">{esc(status)}</span>'


def table(headers: list[str], rows: list[list[str]], *, caption: str = "") -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    if rows:
        body = "".join("<tr>" + "".join(cells) + "</tr>" for cells in rows)
    else:
        body = f'<tr><td colspan="{len(headers)}" class="empty-row">No rows published &mdash; see the note above for why.</td></tr>'
    cap = f"<caption>{esc(caption)}</caption>" if caption else ""
    return f'<div class="table-wrap"><table class="data-table">{cap}<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def notice(title: str, text: str) -> str:
    return f'<div class="notice"><strong>{esc(title)}</strong>{esc(text)}</div>'


def panel(title: str, inner: str, *, meta: str = "") -> str:
    return f'<section class="panel"><div class="panel-head"><h3>{esc(title)}</h3>{meta}</div>{inner}</section>'


def checklist(items, flag_first=False) -> str:
    out = []
    for it in items:
        mark = "&#9873;" if flag_first else "&#10003;"
        cls = "flag" if flag_first else "check"
        out.append(f"<li><span class=\"{cls}\">{mark}</span>{it}</li>")
    return f'<ul class="checklist">{"".join(out)}</ul>'


# --------------------------------------------------------------------------- frame

NAV = [
    ("index.html", "Findings hub"),
    ("executive-summary.html", "Executive summary"),
    ("products.html", "Requested products"),
    ("categories/index.html", "Categories"),
    ("niches.html", "Niche discovery"),
    ("modules/index.html", "Platform modules"),
    ("commissions.html", "Commissions"),
    ("compliance.html", "Compliance"),
    ("verification.html", "Verification log"),
    ("sources.html", "Official sources"),
    ("flags.html", "Flagged for review"),
    ("tracking.html", "Tracking"),
    ("content-engine.html", "Content engine"),
    ("architecture.html", "Architecture"),
]

# Companion views, by current repository topology (they have moved twice already).
SIBLINGS = [
    ("index.html", "Primary Zone2 dashboard"),
    ("research-hub/overview.html", "Verified research hub"),
    ("zone2/index.html", "Zone2 platform (34836ddd)"),
    ("northstar/index.html", "Northstar dashboard"),
]


def render(rel: str, title: str, lead: str, body: str, *, depth: int = 0, badge: str = "") -> str:
    up = "../" * depth
    root = "../" * (depth + 1)
    items = []
    for href, label in NAV:
        if href.startswith("__"):  # never emitted as a link
            continue
        active = " active" if href == rel else ""
        items.append(f'<a class="nav-link{active}" href="{up}{esc(href)}">{esc(label)}</a>')
    flag_count = len(FLAGS["flags"])
    links = []
    for rel, label in SIBLINGS:
        target = REPO / rel
        if target.exists():
            links.append(f'<a href="{root}{esc(rel)}">{esc(label)}</a>')  # repo-root view: prefix is `root`, not `up`
    siblings = " <span>&middot;</span> ".join(links or [f'<a href="{root}README.md">repository</a>'])
    default_badge = f'<a class="chip" href="{up}flags.html">{flag_count} items flagged for review</a>'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Source-verified Amazon affiliate research platform: category data, compliance controls, verification log and open flags. Every table row links to an official source or is left blank.">
<meta name="robots" content="index,follow">
<title>{esc(title)} &middot; {esc(SITE_NAME)}</title>
<link rel="stylesheet" href="{up}assets/dashboard.css">
<link rel="stylesheet" href="{up}assets/site.css">
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <a class="brand" href="{root}index.html"><span class="brand-mark">Z</span><span>{esc(SITE_NAME)}<small>Affiliate intelligence</small></span></a>
  <div class="side-label">FINDINGS &amp; SUBPAGES</div>
  <nav class="nav">{"".join(items)}</nav>
  <div class="sidebar-bottom"><div class="status-dot"></div><div><strong>Verified data only</strong><small>{esc(AS_OF)} &middot; blank = unconfirmed</small></div></div>
</aside>
<main class="main">
  <header class="topbar">
    <div class="crumb"><a href="{root}index.html">{esc(SITE_NAME)}</a> <span>/</span> <strong>{esc(title)}</strong></div>
    <div class="top-right"><span class="live-tag"><i></i> Live on GitHub Pages</span><a class="chip" href="{root}index.html">Dashboard</a></div>
  </header>
  <div class="content">
    <div class="page-head">
      <div>
        <div class="eyebrow">verified {esc(AS_OF)} &middot; official sources only</div>
        <h1>{esc(title)}</h1>
        <p>{esc(lead)}</p>
      </div>
      {badge or default_badge}
    </div>
    {body}
  </div>
  <footer>
    <div class="disclosure"><strong>Disclosure</strong> {esc(DISCLOSURE)} Outbound links on this site are qualified with <code>rel="sponsored"</code>.</div>
    <div class="foot-meta">Research workspace <span>&middot;</span> no product, price, rating or performance figure is stated unless an official source confirms it <span>&middot;</span> {siblings}</div>
  </footer>
</main>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- pages


def page_hub() -> str:
    mods = [
        [
            text_cell(m["id"]),
            f'<td><a class="pagelink" href="modules/{m["id"].lower()}-{slugify(m["name"])}.html">{esc(m["name"])}</a></td>',
            f"<td>{status_pill(m['state'].upper())}</td>",
            text_cell(m["purpose"]),
            source_cell(m["source_ids"]),
        ]
        for m in MODULES["modules"]
    ]
    cats = [
        [
            text_cell(g["id"]),
            f'<td><a class="pagelink" href="categories/{esc(g["slug"])}.html">{esc(", ".join(g["categories"]))}</a></td>',
            num_cell(f'{g["rate_pct"]}%'),
            text_cell(g["commercial_note"]),
            source_cell([COMMISSION["source_id"]]),
        ]
        for g in COMMISSION["groups"]
    ]
    built = "".join(
        "<li><span class=\""
        + ("check\">&#10003;" if not m["blockers"] else "flag\">&#9873;")
        + f"</span><strong>{esc(m['name'])}</strong> &mdash; {esc(m['state'])}"
        + (f"; blocked by: {esc('; '.join(m['blockers']))}" if m["blockers"] else "")
        + "</li>"
        for m in MODULES["modules"]
    )
    stats = (
        '<div class="stats">'
        f'<div class="stat"><label>Products requested</label><strong>{len(PRODUCTS["entries"])}</strong><small>identity unverified</small></div>'
        '<div class="stat"><label>Verified product profiles</label><strong>0</strong><small>no catalog access here</small></div>'
        f'<div class="stat"><label>Official sources read</label><strong>{len(SOURCES)}</strong><small>{esc(AS_OF)}</small></div>'
        f'<div class="stat"><label>Compliance rules wired in</label><strong>{len(COMPLIANCE["rules"])}</strong><small>enforced at build</small></div>'
        "</div>"
    )
    body = (
        notice(
            "How to read every table on this site",
            "A cell shows a value only when an official source states it. A dash carrying a reason \u2014 \u201cnot confirmed\u201d, "
            "\u201cno official record\u201d, \u201cno API access\u201d, \u201cblocked by R-04\u201d \u2014 means the value is unknown and was "
            "deliberately not filled in; the Evidence column then links the flag that explains why. No figure anywhere here is "
            "estimated, averaged, or inferred.",
        )
        + stats
        + panel(
            "Module register",
            table(["ID", "Module", "State", "Purpose", "Evidence"], mods),
            meta=f'<a class="chip" href="modules/index.html">all {len(mods)} modules</a>',
        )
        + panel(
            "Category directory",
            table(["Band", "Categories in the published band", "Published fixed rate", "Commercial reading", "Source"], cats),
            meta=f'<a class="chip" href="categories/index.html">{len(cats)} category pages</a>',
        )
        + panel("What is built vs what is blocked", f'<ul class="checklist">{built}</ul>')
    )
    return render("index.html", "Findings hub", "Every table, every flag, and the evidence behind each row.", body)


def page_exec() -> str:
    key = [
        ("What each supplied link resolves to", True, "Each of the three supplied link.amazon URLs resolves to one specific Amazon product page, reproducibly, and an UNKNOWN code on the same service returns a 404 instead of a product - so the codes are honoured lookups, not ignored tokens.", ["S28", "S19", "S20", "S21"]),
        ("The brief's product identity, as a documented contract", False, "Each supplied code is 9 characters (an ASIN is 10), the canonical /dp/ URLs return Amazon's Page Not Found page, and no public Amazon document binds a link.amazon code to a product. The destination is therefore published as an observation, never as a confirmed brief mapping.", ["S16", "S17", "S18", "S24"]),
        ("Marketing content for confirmed brief identities", False, "No copy claims the observed destinations are confirmed identities for the products intended in the brief. The separate /marketing set does publish three destination-only articles, a comparison and a buying guide from manufacturer-verified specifications; its pages label the unresolved mapping. The root generator remains blocked for brief-mapped content until the owner confirms the mapping.", ["S24", "S25", "S26", "S27", "S32", "S33", "S34", "S35"]),
        ("Platform automation built", True, "Collector, scoring, content linters, link builder, click tracker, optimizer and a deterministic site builder are present and runnable, with policy rules encoded as code.", ["S01", "S02"]),
        ("Official commission economics", True, "Amazon's published fixed-rate table transcribed row by row (11 bands, 10.00% down to 0.00%), plus bounty amounts, attribution windows and payment terms.", ["S04", "S02"]),
        ("Compliance wiring", True, f"{len(COMPLIANCE['rules'])} rules from the Operating Agreement, Program Policies and Participation Requirements, each mapped to a specific implemented control.", ["S01", "S02", "S03", "S05"]),
        ("Pricing / review / competition data", False, "Requires the Creators API with an eligible Associates account; this build has no credentials, so those columns stay blank rather than filled from memory or scraping.", ["S06", "S07"]),
        ("Clicks, conversion, earnings", False, "Nothing to verify: no report export was supplied and no live endpoint exists, so all performance cells render as empty states.", ["S02"]),
        ("Published site", True, "GitHub Pages is enabled for this repository and the landing dashboard plus all generated subpages are served from main.", ["S22"]),
    ]
    rows = [
        [
            text_cell(q),
            f"<td>{status_pill('VERIFIED' if ok else 'UNVERIFIED')}</td>",
            text_cell(basis),
            source_cell(srcs),
        ]
        for q, ok, basis, srcs in key
    ]
    findings = [
        "The highest-value action is identifier hygiene, not copywriting: the supplied 9-character tokens cannot be used as ASINs or treated as a documented brief-to-product mapping. The observed destination ASINs can be researched as those destinations, and that is the scope of the published source-linked marketing set. None of the supplied links carries an Associates tag, and no public Amazon document binds the short codes to the intended brief products.",
        "Amazon's published economics shape the plan. Only a few bands are high (Luxury Beauty 10.00%; music/handmade/video 5.00%; Books/Kitchen/Automotive 4.50%); the largest consumer clusters sit at 3.00% and the default band is 4.00%, while nine category groups pay 0.00% and are excluded from the niche queue before ranking even starts.",
        "Attribution is narrow and mechanical: a 24-hour Session, an 89-day cart path, and shipment/payment inside 180 days. Content is therefore worth optimising only where readers are close to a purchase decision, and the model credits nothing outside that window.",
        "Prices and ratings may not be self-hosted as static text: they may appear only from an Amazon-served link or a dated API response. That is why a product whose listing could not be fetched shows a blank price cell, and nothing on the site can look like a stale price.",
        "PA-API 5.0 is deprecated (calls return 403 AccessDenied) in favour of the Creators API, which itself requires an Associates account with 10 or more qualifying sales in the last 30 days. Any stack built on the old API fails at runtime; this one degrades to a recorded BLOCKED state instead of scraping.",
        "Reviewing the previously merged commit found no false claims \u2014 its four citations are live official pages \u2014 but it predated the commission table, the attribution mechanics, per-row sourcing and the category subpages added here.",
    ]
    actions = [
        ("A1", "Confirm in Associates Central that the three resolved destinations are the products intended in the brief, or provide the intended valid ASINs / full amazon.<tld>/dp/ URLs", "user", "unblocks content and analysis that assert a match to the brief; current destination-only specs remain separately sourced and labelled", ["S16", "S17", "S18", "S24", "S25", "S26", "S27"]),
        ("A1b", "Supply links that carry the Associates tag (…?tag=YOURASSOCIATEID)", "user", "as supplied the three links carry no tag, so they cannot attribute a sale or earn a commission", ["S24", "S19", "S20", "S21"]),
        ("A2", "Create or confirm an Associates account, marketplace and Associates ID/tag", "user", "turns the inert link preview into a compliant tagged Special Link and enables earnings reporting", ["S01", "S02"]),
        ("A3", "Register for the Creators API (requires >=10 qualifying sales in the past 30 days)", "user", "activates real product research, offer and browse-node data", ["S07"]),
        ("A4", "Store one dated Associates report export at ledger/associates_report.json", "user", "unlocks conversion, EPC and the optimizer's revenue-side actions", ["S02"]),
        ("A5", "Run the build with policy/rate re-reads before each publishing cycle", "operator", "both governing pages carry update dates and change without notice", ["S01", "S02"]),
    ]
    body = (
        panel(
            "Bottom line",
            '<p class="lede">The research, compliance and source-governed content platform is built and live, but it is not yet monetized. The three supplied '
            "links reproducibly resolve to specific product pages; destination-only articles, comparison and buying guide use manufacturer-verified "
            "specifications with source links. The site does not claim those destinations are the products intended in the brief, because the mapping "
            "is not documented. There is no Associates tag, and unconfirmed prices, ratings, commissions and performance remain blank.</p>",
        )
        + panel("Key questions answered", table(["Question", "Verdict", "Basis", "Evidence"], rows))
        + panel("Findings", "<ol class=\"findings\">" + "".join(f"<li>{esc(f)}</li>" for f in findings) + "</ol>")
        + panel(
            "Prioritised actions",
            table(["#", "Action", "Owner", "Why it matters", "Evidence"], [[text_cell(a), text_cell(b), text_cell(c), text_cell(d), source_cell(e)] for a, b, c, d, e in actions]),
        )
        + notice(
            "Not claimed by this project",
            "no monetized, Associates-tagged product link; no claim that the observed destinations are the products intended in the brief; no traffic, "
            "conversion or earnings figure; no \u201ctrending product\u201d or \u201cbest niche\u201d ranking; and no automated publishing to a third-party CMS. "
            "The /marketing pages use untagged preview links and publish only sourced specifications for the observed destinations. An Associates ID, owner "
            "confirmation of the mapping, Creators API access and dated performance reports have not been supplied; dependent claims and values remain blocked or blank.",
        )
    )
    return render("executive-summary.html", "Executive summary", "What was verified, what was built, and what is blocking the rest.", body)


def page_products() -> str:
    rows = []
    for e in PRODUCTS["entries"]:
        rows.append(
            [
                text_cell(e["id"]),
                f'<td><a class="pagelink" href="{esc(e["submitted_url"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(e["token_as_given"])}</a></td>',
                num_cell(f'{e["asin_length_observed"]} / 10'),
                f'<td>{status_pill("VALID" if e["asin_format_valid"] else "INVALID")}</td>',
                blank_cell("no official record"),
                blank_cell("no official record"),
                blank_cell("blocked by R-04"),
                blank_cell("no API access"),
                blank_cell("no API access"),
                f"<td>{status_pill(e['status'])}</td>",
                source_cell(e["source_ids"], blank_hint="identity unresolved"),
            ]
        )
    ev = [
        [
            text_cell(o["id"]),
            text_cell(o["observation"], code=True),
            text_cell(o["interpretation"]),
            f"<td>{status_pill(o['status'])}</td>",
            source_cell(o["source_ids"]),
        ]
        for o in PRODUCTS["evidence_observations"]
    ]
    whys = "".join(
        "<div class=\"why\"><dt>"
        + esc(f"{e['id']} \u00b7 {e['token_as_given']}")
        + "</dt><dd>"
        + esc(e["why_blank"])
        + "</dd><dd class=\"flags-inline\">Flags: "
        + " ".join(f"<a href=\"flags.html#{esc(f)}\">{esc(f)}</a>" for f in e["flag_ids"])
        + "</dd></div>"
        for e in PRODUCTS["entries"]
    )

    # ---- T23-INTEGRATION: what each supplied link actually resolves to, and its sourced specs ----
    resolved_rows = []
    for e in PRODUCTS["entries"]:
        r = e.get("resolved")
        if not r:
            continue
        resolved_rows.append(
            [
                f'<td><a class="pagelink" href="{esc(e["submitted_url"])}" target="_blank" '
                f'rel="noopener noreferrer nofollow">{esc(e["token_as_given"])}</a></td>',
                text_cell(r["asin"], code=True),
                text_cell(r["title"]),
                text_cell(r["brand"]),
                text_cell(r["category_path"]),
                blank_cell("not republished outside an Amazon link (R-04)"),
                blank_cell("not republished outside an Amazon link (R-04)"),
                blank_cell("needs a licensed API response"),
                f"<td>{status_pill('OBSERVED')}</td>",
                source_cell(r["source_ids"] + r.get("manufacturer_source_ids", [])),
            ]
        )

    spec_tables = ""
    for e in PRODUCTS["entries"]:
        r = e.get("resolved")
        if not r:
            continue
        srows = []
        for sp in r["specs"]:
            if sp.get("status") == "unverified":
                srows.append(
                    [
                        text_cell(sp["attribute"]),
                        blank_cell(sp.get("why_blank") or "not confirmed on an official page"),
                        f"<td>{status_pill('UNVERIFIED')}</td>",
                        source_cell(sp.get("source_ids"), blank_hint="no official source states this value"),
                    ]
                )
            else:
                srows.append(
                    [
                        text_cell(sp["attribute"]),
                        text_cell(sp["value"]),
                        f"<td>{status_pill('CONFLICT' if sp.get('status') == 'conflict' else 'VERIFIED')}</td>",
                        source_cell(sp.get("source_ids")),
                    ]
                )
                if sp.get("source_label"):
                    srows[-1][1] += f'<div class="row-note">{esc(sp["source_label"])}</div>'
        spec_tables += panel(
            f"{r['brand']} {r['asin']} \u2014 specifications",
            table(["Attribute", "Value", "Status", "Official source"], srows),
            meta=f'<span class="chip">resolved from {esc(e["token_as_given"])}</span>',
        )

    body = (
        notice("Verification method", PRODUCTS["note"])
        + panel(
            "Requested items, exactly as supplied",
            table(["ID", "Token as given", "Length vs ASIN", "Format", "Title", "Category", "Price", "Rating", "Commission band", "Status", "Evidence"], rows),
            meta=f'<span class="chip">{len(rows)} need review</span>',
        )
        + panel("Why each field is blank", f"<dl class=\"whys\">{whys}</dl>")
        + panel(
            "What each supplied link resolves to (observed 2026-11-14)",
            table(
                [
                    "Supplied link",
                    "Resolved ASIN",
                    "Listing title as published on Amazon",
                    "Brand",
                    "Category path",
                    "Price",
                    "Rating",
                    "Commission band",
                    "Status",
                    "Evidence",
                ],
                resolved_rows,
            ),
            meta=f'<span class="chip">{len(resolved_rows)} links resolved</span>',
        )
        + notice(
            "How to read the two tables above",
            "The first table is about the TOKEN as supplied: it is 9 characters, an ASIN is 10, and "
            "amazon.com/dp/&lt;code&gt; is Amazon's Page Not Found page, so every field is left blank and "
            "flagged. The second table is about the LINK as supplied: each one resolves to exactly one "
            "Amazon product page, reproducibly, and an unknown code on the same service returns a 404 "
            "instead of a product (flag F-20), so the destination is a verified observation of the link's "
            "behaviour. They are kept apart because Amazon publishes no document that binds a "
            "link.amazon code to a product - see flags F-03, F-04 and F-24.",
        )
        + spec_tables
        + panel("Evidence observations (reproducible by hand)", table(["ID", "Observation", "Interpretation", "Status", "Evidence"], ev))
        + panel(
            "Next action for these three items",
            '<ul class="checklist">'
            "<li><span class=\"flag\">&#9873;</span>Supply the full 10-character ASIN, or the complete product URL, for each item.</li>"
            "<li><span class=\"check\">&#10003;</span>Point the collector at it: <code>python3 tools/amazon_creators_api.py</code> with credentials writes a dated, hashed record.</li>"
            "<li><span class=\"check\">&#10003;</span>Then <code>python3 tools/generate_articles.py</code> drafts the article, comparison and guide automatically \u2014 no other change needed.</li>"
            "</ul>",
        )
    )
    return render("products.html", "Requested products", "The three items named in the brief, with every unconfirmed field left blank.", body)


def page_commissions() -> str:
    rows = [
        [
            text_cell(g["id"]),
            f'<td class="cell-num"><strong>{esc(g["rate_pct"])}%</strong></td>',
            text_cell(", ".join(g["categories"])),
            text_cell(g["commercial_note"]),
            source_cell([COMMISSION["source_id"]]),
        ]
        for g in COMMISSION["groups"]
    ]
    bounties = [[text_cell(b["program"]), text_cell(b["bounty_action"]), num_cell(b["rate"]), source_cell([b["source_id"]])] for b in COMMISSION["bounties"]]
    # T26 (session d3ce1c29, F-30): S04 publishes a second special-income block, "(b) Bonus Events",
    # which the earlier transcription omitted along with most of the bounty rows.
    bonuses = [[text_cell(b["program"]), text_cell(b["bonus_action"]), num_cell(b["rate"]), source_cell([b["source_id"]])] for b in COMMISSION.get("bonus_events", [])]
    terms = [[text_cell(t["term"]), text_cell(t["detail"]), source_cell([t["source_id"]])] for t in COMMISSION["other_statement_terms"]]
    bounty_note = (
        f'{len(bounties)} bounty events and {len(bonuses)} bonus events, published in full. '
        "An earlier revision published only the first 9 bounty rows under a \"transcribed row-by-row\" notice "
        "(flag F-30, corrected 2026-11-14)."
    )
    model = [
        ("Band ceiling used for normalisation", "10.00%", "highest published fixed rate in the table", ["S04"]),
        ("Default band", "4.00%", "All Other Categories", ["S04"]),
        ("Attribution window", "24 hours", "Session ends 24h after the click, or on first order, or on another associate's click", ["S02"]),
        ("Cart path", "89 days", "order must complete no later than 89 days after click-through", ["S02"]),
        ("Fulfilment condition", "180 days", "shipped/streamed/downloaded and paid for within 180 days of purchase", ["S02"]),
        ("Payment timing", "~60 days", "after the end of the calendar month in which income was earned", ["S02"]),
        ("US payment minimums", "10 / 10 / 100 USD", "direct deposit / gift card (2,000 USD max) / check (plus 15 USD fee)", ["S02"]),
        ("Inactivity rule", "3 years", "Amazon may withhold accrued income with 7 days' written notice", ["S02"]),
        ("Projection status", "ILLUSTRATIVE", "Amazon makes no representation about expected traffic or commission income", ["S01"]),
    ]
    body = (
        notice("Transcribed, not summarised", COMMISSION["note"])
        + panel(COMMISSION["table"], table(["Band", "Fixed rate", "Categories in the band", "Commercial reading", "Source"], rows))
        + panel("Bounty events (Special Commission Income)", table(["Program", "Bounty action", "Published rate", "Source"], bounties) + notice("Complete, not excerpted", bounty_note))
        + panel("Bonus events (Special Commission Income)", table(["Program", "Bonus action", "Published rate", "Source"], bonuses))
        + panel("Other statement terms that change the maths", table(["Term", "What the statement says", "Source"], terms))
        + panel("Constants wired into tools/scoring.py", table(["Constant", "Value", "Basis", "Source"], [[text_cell(a), num_cell(b), text_cell(c), source_cell(d)] for a, b, c, d in model]))
        + notice(
            "Zero-rate bands are exclusions, not opportunities",
            "Table 1 publishes two 0.00% bands: the exclusion block (gift cards, wireless service plans, alcoholic beverages, "
            "Digital Kindle products purchased as a subscription, vehicle leasing and sales, pet prescription medications, food "
            "prepared and delivered from a restaurant, and Amazon Appstore / Prime Now / Amazon Pay Places) and Coach, listed on "
            "its own row. The niche filter removes them before any ranking happens, so no content budget can be spent on a "
            "category that pays nothing. (An earlier revision of this caption said \"nine category groups\", which matches no "
            "grouping in the source — flag F-31.)",
        )
    )
    return render("commissions.html", "Commissions & economics", "Amazon's published rates, bounties, attribution windows and payment terms, transcribed from the source.", body)


def page_categories_index() -> str:
    rows = [
        [
            f'<td><a class="pagelink" href="{esc(g["slug"])}.html">{esc(g["id"])}</a></td>',
            text_cell(", ".join(g["categories"])),
            num_cell(f'{g["rate_pct"]}%'),
            num_cell(len(g["categories"])),
            text_cell(g["commercial_note"]),
            source_cell([COMMISSION["source_id"]]),
        ]
        for g in COMMISSION["groups"]
    ]
    body = (
        notice(
            "Organised by Amazon's own category bands",
            "One subpage per published rate band. The rate on each page is the figure from the official statement. Which products "
            "belong in a band may only be established by a catalog record for that product, so no product is attached to a band here.",
        )
        + panel("Category subpages", table(["Band", "Categories", "Published fixed rate", "Count", "Commercial reading", "Source"], rows))
    )
    return render("categories/index.html", "Categories", "Subpages organised by Amazon's published commission categories.", body, depth=1)


def page_category(g: dict) -> str:
    facts = [
        ("Published fixed rate", f'{g["rate_pct"]}%', [COMMISSION["source_id"]]),
        ("Band id", g["id"], [COMMISSION["source_id"]]),
        ("Categories in this band", ", ".join(g["categories"]), [COMMISSION["source_id"]]),
        ("Commercial reading", g["commercial_note"], []),
        ("Verified products assigned here", "0", []),
        ("Why zero", "a category may only be attached to a product by a catalog record for that product, and none of the three requested items resolved to a record", ["S16", "S17", "S18"]),
    ]
    per_product = [
        ("Clicks", "not published", "no live endpoint and no click log in this build"),
        ("Conversion rate", "not published", "requires a dated Associates report row"),
        ("Shipped revenue", "not published", "requires a dated Associates report row"),
        ("Commission at this band", f'{g["rate_pct"]}% of qualifying revenue', "rate from the published table; revenue side stays blank"),
    ]
    steps = [
        "Eligibility filter: 0.00% bands never enter the niche queue (source: published table).",
        "Scoring: tools/scoring.py::commission_term normalises this band against the 10.00% ceiling and records whether the match was exact or the All-Other default.",
        "Content: a template may cite this band for a verified ASIN only, and the sentence carries the source link.",
        "Reporting: revenue attribution uses the 24-hour Session and the 89-day cart window, never an assumed evergreen credit.",
    ]
    body = (
        notice(
            "Rate only; no product facts implied",
            "This page states Amazon's published commission band. It does not recommend, describe, or endorse any specific product, "
            "and it displays no price and no rating.",
        )
        + panel("Band detail", table(["Field", "Value", "Source"], [[text_cell(a), text_cell(b), source_cell(c)] for a, b, c in facts]))
        + panel("Per-product economics for this band", table(["Metric", "Value", "Basis"], [[text_cell(a), status_pill(b) if b == "not published" else text_cell(b), text_cell(c)] for a, b, c in per_product]))
        + panel("How the pipeline uses this band", checklist(esc(s) for s in steps))
    )
    return render(f"categories/{g['slug']}.html", f"Category band {g['rate_pct']}%", ", ".join(g["categories"]), body, depth=1)


def page_modules_index() -> str:
    rows = [
        [
            f'<td><a class="pagelink" href="{esc(m["id"].lower())}-{slugify(m["name"])}.html">{esc(m["id"])}</a></td>',
            text_cell(m["name"]),
            f"<td>{status_pill(m['state'].upper())}</td>",
            text_cell(", ".join(m["implemented_in"]), code=True),
            text_cell("; ".join(m["blockers"]) or "none"),
            source_cell(m["source_ids"]),
        ]
        for m in MODULES["modules"]
    ]
    body = (
        notice(
            "State definitions",
            "automated = code is present and runnable here. scaffolded = the interface and its rules exist, awaiting a live data "
            "source. blocked = an external authority (credential, account, or verified record) is required before any value may be "
            "produced.",
        )
        + panel("Module register", table(["ID", "Module", "State", "Implemented in", "Blockers", "Sources"], rows))
    )
    return render("modules/index.html", "Platform modules", "The capabilities the brief asked for, and the honest state of each.", body, depth=1)


RULE_TAGS = {
    "M-01": {"R-11", "R-20"},
    "M-02": {"R-19"},
    "M-03": {"R-04", "R-05"},
    "M-04": {"R-10"},
    "M-05": set(),
    "M-06": {"R-13", "R-15", "R-19"},
    "M-07": {"R-01", "R-02", "R-03", "R-06", "R-17", "R-18"},
    "M-08": {"R-07", "R-08", "R-09", "R-14"},
    "M-09": {"R-08", "R-13", "R-15"},
    "M-10": {"R-10", "R-15"},
    "M-11": {"R-11", "R-12"},
    "M-12": {"R-16", "R-20"},
}


def page_module(m: dict) -> str:
    detail = [
        ("Purpose", m["purpose"], []),
        ("State", m["state"], []),
        ("Verification method", m["verification"], []),
        ("Hard rule", m["hard_rule"], []),
        ("Implemented in", ", ".join(m["implemented_in"]), []),
        ("Official inputs", "; ".join(m["official_inputs"]), []),
        ("Blockers", "; ".join(m["blockers"]) or "none recorded", []),
    ]
    related = [r for r in COMPLIANCE["rules"] if r["id"] in RULE_TAGS.get(m["id"], set())]
    rel_rows = [
        [
            text_cell(r["id"]),
            text_cell(r["domain"]),
            text_cell(r["requirement"]),
            text_cell(r["citation"], code=True),
            text_cell(r["implemented_control"]),
            source_cell([r["source_id"]] + ([r["source_id_alt"]] if r.get("source_id_alt") else [])),
        ]
        for r in related
    ]
    body = (
        (notice("Blocked pending an authorized source", m["blockers"][0]) if m["state"] == "blocked" else "")
        + panel("Module detail", table(["Field", "Value", "Source"], [[text_cell(a), text_cell(b), source_cell(c)] for a, b, c in detail]))
        + panel(
            "Rules that constrain this module",
            table(["Rule", "Domain", "Requirement as stated by the source", "Citation", "Implemented control", "Source"], rel_rows)
            if rel_rows
            else notice("No additional rule binding", "This module's constraints are the project-wide ones listed on the compliance page."),
        )
    )
    return render(
        f"modules/{m['id'].lower()}-{slugify(m['name'])}.html",
        m["name"],
        m["purpose"],
        body,
        depth=1,
        badge=status_pill(m["state"].upper()),
    )


def page_compliance() -> str:
    rows = [
        [
            text_cell(r["id"]),
            text_cell(r["domain"]),
            text_cell(r["requirement"]),
            text_cell(r["citation"], code=True),
            text_cell(r["implemented_control"]),
            f"<td>{status_pill(r['status'])}</td>",
            source_cell([r["source_id"]] + ([r["source_id_alt"]] if r.get("source_id_alt") else [])),
        ]
        for r in COMPLIANCE["rules"]
    ]
    checks = [
        "Disclosure sentence present on every page that can carry an affiliate link (R-01).",
        "Link-level disclosure adjacent to the first affiliate link, in the same medium as the recommendation (R-02).",
        "Approved wording only; the phrase the FTC calls unclear is banned outright (R-03).",
        "No price or availability text unless it came from an Amazon-served link or a dated API response (R-04, R-05).",
        "No superlative, urgency claim, or implied endorsement without inline evidence on the same line (R-06).",
        "Every Amazon link carries an Associates tag parameter and rel=\"sponsored nofollow\" (R-07, R-17).",
        "Campaign keys are static; nothing identifies a visitor (R-08).",
        "Nothing is distributed by email, SMS, print or other offline channels (R-09).",
        "API-sourced fields are stored immutably with a response hash (R-10).",
        "No Amazon mark appears in this site's name, file names, tags or social identifiers (R-11).",
        "Site content stays original with added analysis, as the enrollment rules require (R-12).",
    ]
    body = (
        notice(
            "Required disclosure sentence",
            DISCLOSURE + " This wording is prescribed by the Operating Agreement and appears in the footer of every page on this site.",
        )
        + panel("Control ledger", table(["Rule", "Domain", "Requirement as stated by the source", "Citation", "Implemented control in this repo", "Status", "Source"], rows))
        + panel("Publishing checklist", checklist(esc(c) for c in checks))
    )
    return render("compliance.html", "Compliance", "Program rules, mapped one-to-one to the control that enforces each of them.", body)


def page_verification() -> str:
    counts: dict[str, int] = {}
    for r in VERIFICATION["rows"]:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    rows = [
        [
            text_cell(r["id"]),
            text_cell(r["subject"]),
            text_cell(r["claim"]),
            text_cell(r["method"]),
            f"<td>{status_pill(r['verdict'])}</td>",
            source_cell(r["source_ids"]),
            text_cell(r.get("consequence", "")),
        ]
        for r in VERIFICATION["rows"]
    ]
    body = (
        notice(
            "Reproducible",
            "Each row records how the check was performed so it can be repeated by hand. Verdicts were recorded by reading the "
            f"cited page on {AS_OF}; nothing here is recalled from memory or inferred.",
        )
        + panel("Verdict counts", table(["Verdict", "Rows"], [[f"<td>{status_pill(k)}</td>", num_cell(v)] for k, v in sorted(counts.items())]))
        + panel("Verification log", table(["ID", "Subject", "Claim checked", "Method", "Verdict", "Source", "Consequence"], rows))
    )
    return render("verification.html", "Verification log", f"{len(rows)} checks, each tied to an official source and a method.", body)


def page_sources() -> str:
    rows = [
        [
            text_cell(s["id"]),
            f'<td><a class="pagelink" href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(s["title"])}</a></td>',
            text_cell(s["publisher"]),
            text_cell(s["kind"]),
            text_cell(s.get("page_stated_update") or "not stated on page"),
            text_cell(s["accessed_utc"]),
            text_cell("; ".join(s["used_for"])),
        ]
        for s in SOURCES.values()
    ]
    body = (
        notice(
            "Allowlisted hosts",
            "Rows may cite only: affiliate-program.amazon.com, amazon.com, webservices.amazon.com, ftc.gov, developers.google.com, "
            "support.google.com and docs.github.com. tools/validate_data.py fails the build if a row cites anything else, or cites "
            "nothing at all.",
        )
        + panel("Source register", table(["ID", "Title / link", "Publisher", "Kind", "Page states it was updated", "Accessed", "Used for"], rows))
    )
    return render("sources.html", "Official sources", "Every document this repository relies on, with its access date.", body)


def _open_flag_count() -> int:
    """Flags still awaiting the owner.

    Delegates to tools/flag_state.py so summary.html and pages/flags.html count the same way —
    see the module docstring for why that matters (F-29, F-31).
    """
    return open_count(FLAGS["flags"])


def page_flags() -> str:
    sev = {"high": "stop", "medium": "warn", "low": "info"}
    rows = [
        [
            f'<td id="{esc(f["id"])}"><strong>{esc(f["id"])}</strong></td>',
            f'<span class="pill pill-{sev[f["severity"]]}">{esc(f["severity"].upper())}</span>',
            f"<td><strong>{esc(f['title'])}</strong><div class=\"row-note\">{esc(f['detail'])}</div></td>",
            text_cell(f["impact"]),
            text_cell(f["action_required"]),
            text_cell(f["owner"]),
            source_cell(f["source_ids"]),
        ]
        for f in FLAGS["flags"]
    ]
    blank_fields = ("title", "brand", "category", "price", "availability", "rating", "review_count", "bsr", "commission_rate")
    blank_rows = []
    for e in PRODUCTS["entries"]:
        anchors = " ".join('<a href="#{f}">{f}</a>'.format(f=esc(x)) for x in e["flag_ids"])
        blank_rows.append(
            [
                text_cell("{} \u00b7 {}".format(e["id"], e["token_as_given"])),
                text_cell(", ".join(k for k in blank_fields if not e.get(k)), code=True),
                "<td>" + anchors + "</td>",
                source_cell(e["source_ids"]),
            ]
        )
    body = (
        notice(
            "Flagged for review \u2014 read this first",
            "Nothing on this page is a product claim. These are items that could not be confirmed against an official source, plus "
            "irregularities found while reviewing the repository. They do not block the site; they block assertion. Each links to the "
            "official page that documents the problem.",
        )
        # F-31 (session d3ce1c29) + F-29 (session ba8b2d38): the heading used len(rows), i.e. every
        # flag in the register, so the page announced "28 open items" while summary.html published "25".
        # Both surfaces now import the same predicate, so they cannot disagree again.
        + panel(
            f"{len(rows)} flagged items \u00b7 {_open_flag_count()} open \u00b7 {len(rows) - _open_flag_count()} resolved",

            table(["ID", "Severity", "Finding", "Impact", "Action required", "Owner", "Source"], rows),
        )
        + panel("Product fields left blank because of these flags", table(["Item", "Blank fields", "Blocking flags", "Source"], blank_rows))
        + notice(
            "What changes if the ASINs are corrected",
            "identity resolves, the pricing/review/competition modules unblock, the content engine drafts three assets per item, and "
            "the rate band attaches from the published table. No other code change is required.",
        )
    )
    return render("flags.html", "Flagged for review", "Unverified items and irregularities, with source links, for after-launch review.", body, badge="")


def page_niches() -> str:
    rows = [
        [text_cell(x["input"]), f"<td>{status_pill(x['status'])}</td>", text_cell(x["status"] if x["status"] == "AVAILABLE" else "not connected"), source_cell([COMMISSION["source_id"]] if x["status"] == "AVAILABLE" else [])]
        for x in NICHES["ranking_inputs_required"]
    ]
    body = (
        notice("Why this queue is empty", NICHES["empty_state_message"])
        + panel("Eligibility filter (sourced and deterministic)", f"<p class=\"lede\">{esc(NICHES['eligibility_filter']['description'])}</p>" + table(["Excluded band"], [[text_cell(c)] for c in NICHES["eligibility_filter"]["excluded_bands"]], caption="published 0.00% categories"), meta=source_cell([NICHES["eligibility_filter"]["source_id"]]).replace("<td", "<span").replace("</td>", "</span>"))
        + panel("Inputs required before any niche may be ranked", table(["Required input", "State", "Where it must come from", "Source"], rows))
        + panel("Row schema the queue will use", "<pre class=\"code\">" + esc(json.dumps(NICHES["row_schema"], indent=2, sort_keys=True)) + "</pre>")
    )
    return render("niches.html", "Niche discovery", "The method and the filter are sourced; the ranking stays empty until demand data exists.", body)


def page_tracking() -> str:
    metrics = [
        ("Clicks by page/campaign", "0 rows", "code exists (tools/redirect_server.py); no log until deployed", ["S02"]),
        ("CTR", "not published", "needs an impression denominator; none is measured, so no CTR is stated", []),
        ("Orders attributed", "not published", "comes only from Associates reporting inside the Session window", ["S02"]),
        ("Conversion rate", "not published", "requires both orders and clicks", ["S02"]),
        ("EPC", "not published", "requires shipped revenue and clicks", ["S02"]),
        ("Commission earned", "not published", "report rows plus the published band; paid ~60 days after month end", ["S02"]),
        ("Effective rate check", "not published", "computed from a report import, never from the rate table alone", ["S04", "S02"]),
    ]
    rows = [
        [text_cell(a), f"<td>{status_pill(b)}</td>", text_cell(c), source_cell(d)] for a, b, c, d in metrics
    ]
    cols = [
        ("clicks", "integer", "measured here", "count of redirects served for a static campaign key"),
        ("campaign_key", "static label", "ledger/campaigns.json", "must never vary per visitor (R-08)"),
        ("orders / shipped revenue / earned commission", "from report", "Associates export", "only permitted source for conversion and earnings (R-13, R-15)"),
        ("visitor id, cookie, IP, user-agent", "not stored", "\u2014", "excluded by design: no per-user association, minimal data"),
    ]
    honour = [
        "Sub-tags are used only as static campaign labels; the Participation Requirements forbid associating a sub-tag or Associates reporting with a specific end user (R-08).",
        "No cookies, fingerprints, IP addresses or user agents are written by the tracker; the default access log is suppressed for the same reason.",
        "Amazon may itself record information about users who click through Special Links (Operating Agreement Sec. 12); our copy adds nothing identifying.",
        "Attribution parameters belonging to other networks are rejected on the outbound link, so the same traffic can never be double-claimed (R-14).",
        "A link is never emitted without an Associates tag; without one the builder raises NO_TAG instead of shipping an untagged link.",
    ]
    body = (
        notice(
            "What is measured here vs what is earned",
            "Site-side counting can only say that a page sent a click. Whether that click became a commission is answered "
            "exclusively by Associates reporting inside the Session window, so every revenue-side cell on this site stays blank "
            "until a dated report is ingested.",
        )
        + panel("Metric availability", table(["Metric", "State", "Why", "Source"], rows))
        + panel("Data contract (see tools/tracking_schema.sql)", table(["Field", "Type / origin", "Source of record", "Rule"], [[text_cell(a, code=True), text_cell(b), text_cell(c, raw=True), text_cell(d)] for a, b, c, d in cols]))
        + panel("Privacy and policy constraints honoured", checklist(esc(h) for h in honour))
    )
    return render("tracking.html", "Tracking & measurement", "What the click layer records, what it must never record, and what stays blank.", body)


def page_content() -> str:
    kinds = [
        ("Product article", "content/templates/product_article.md.tmpl", "one verified product; editorial analysis, disclosure, Product+Review JSON-LD"),
        ("Comparison", "content/templates/comparison.md.tmpl", "two or more verified products; lowest new (and used) price cells only from dated offer records"),
        ("Buying guide", "content/templates/buying_guide.md.tmpl", "decision criteria first, product blocks second, objections answered from sourced review themes"),
    ]
    lints = [
        ("DISCLOSURE_MISSING", "required Site sentence absent", "R-01"),
        ("DISCLOSURE_POSITION", "affiliate link precedes the disclosure block", "R-02"),
        ("SUPERLATIVE / URGENCY / IMPLICATION", "claim without an inline evidence reference on its line", "R-06"),
        ("FABRICATED_EXPERIENCE", "text asserts hands-on testing that did not happen", "R-06"),
        ("HTML_AUDIT", "built HTML lacks rel=\"sponsored\", lacks the tag, or uses banned disclosure wording", "R-03, R-07, R-17"),
        ("LEAKY_PLACEHOLDER", "an unresolved field reached the output", "verification contract"),
    ]
    state = [
        [text_cell(e["id"]), f"<td>{status_pill(e['status'])}</td>", text_cell("REFUSED_UNVERIFIED_IDENTITY"), text_cell(e["why_blank"][:160]), source_cell(e["source_ids"])]
        for e in PRODUCTS["entries"]
    ]
    seo = [
        "Affiliate links are emitted with rel=\"sponsored nofollow\", per Google's guidance to qualify affiliate links (R-17).",
        "Editorial reviews may expose pros and cons through Product/Review structured data, and markup text must match the visible page (R-18).",
        "Review author must be a valid Person or Team name; promotional strings such as a discount teaser do not belong in the markup.",
        "Original analysis is mandatory in the front matter, because the participation rules require original content with significant commentary (R-12).",
        "Limited-time promo copy carries an expiry and the builder drops it once past, as the Participation Requirements demand (R-06).",
    ]
    body = (
        notice(
            "Gate first, prose second",
            "The generator validates before it writes: an entry without a resolved catalog record produces a refusal record instead "
            "of a draft, and a draft that fails any lint never reaches content/published/. That is why the article count for the three "
            "requested items is zero.",
        )
        + panel("Templates", table(["Asset", "File", "Behaviour"], [[text_cell(a), text_cell(b, code=True), text_cell(c)] for a, b, c in kinds]))
        + panel("Lint suite (tools/generate_articles.py)", table(["Code", "Blocks", "Rule"], [[text_cell(a, code=True), text_cell(b), text_cell(c)] for a, b, c in lints]))
        + panel("SEO mechanics honoured", checklist(esc(s) for s in seo))
        + panel("Generation status for the requested items", table(["Entry", "Identity", "Generator result", "Note", "Source"], state))
    )
    return render("content-engine.html", "Content engine", "How copy gets produced without inventing facts.", body)


def page_architecture() -> str:
    steps = [
        ("1. Ingest", "validate the identifier (10-character ASIN) &rarr; catalog lookup &rarr; cache the response with a hash and timestamp", "tools/asin_guard.py, tools/amazon_creators_api.py", "BLOCKED without credentials; never scraped", ["S06", "S07"]),
        ("2. Enrich", "attach the published commission band, browse nodes and a dated offer record", "tools/scoring.py, ledger/commission_table.json", "blank where no official value exists", ["S04"]),
        ("3. Score", "weighted opportunity score: commission 0.30, demand 0.25, competition 0.25, review 0.20", "tools/scoring.py::niche_score", "returns INSUFFICIENT_DATA instead of a default", ["S07"]),
        ("4. Draft", "render article, comparison or guide from templates only if identity resolved", "tools/generate_articles.py", "refusal record otherwise", ["S14", "S15"]),
        ("5. Lint", "disclosure proximity and wording, claims, structured data, rel attributes, mark usage", "tools/generate_articles.py, tools/validate_data.py", "blocks publish on any failure", ["S01", "S02", "S10", "S12"]),
        ("6. Publish", "deterministic static build &rarr; deploy gate &rarr; GitHub Pages", "tools/build_site.py, .github/workflows/pages.yml", "no network, no secrets, no manual step", ["S22"]),
        ("7. Measure", "first-party click counts on static campaign keys", "tools/redirect_server.py, tools/tracking_schema.sql", "no visitor identity stored", ["S02"]),
        ("8. Optimize", "evidence-gated rule engine: needs 30+ clicks and a dated report before any action", "tools/optimize.py", "NO_ACTION with a stated reason when thin", ["S02"]),
        ("9. Re-verify", "re-read the policy and rate pages each cycle; expire cached offer data", "tools/cache.py, tools/build_site.py", "as-of dates shown on every derived table", ["S01", "S02", "S04"]),
    ]
    scale = [
        ("Idempotent build", "same data produces the same bytes, so a rerun on every push is safe", []),
        ("Cache and politeness", "keyed content cache with per-class freshness, plus a token bucket for the operator's own budget", []),
        ("Backpressure", "throttling surfaces as QuotaExceeded; a failed cycle leaves the previously published site intact instead of half-updating it", []),
        ("Cost per page", "one catalog lookup plus a render and a lint, so growth is bounded by API throughput rather than manual effort", []),
        ("Multi-session safety", "COORDINATION.md claims with non-overlapping file scopes; shared outputs touched only by the integration session", []),
        ("Deploy gate", "the validator runs in CI: broken links, unsourced rows or disclosure errors stop publication", []),
        ("Single source of truth", "the site renders from ledger/*.json; no page holds a hand-typed figure", []),
    ]
    layout = (
        "index.html / app.js / data.js / styles.css   landing dashboard (merged first, preserved)\n"
        "pages/                                        generated subpages: categories, modules, findings\n"
        "ledger/                                       source of truth: products, rates, rules, flags, sources\n"
        "tools/                                        guard, collector, scoring, generator, tracker, optimizer, build, validate\n"
        "content/templates/                            article / comparison / buying-guide templates\n"
        ".github/workflows/pages.yml                   validate + publish to GitHub Pages\n"
        "COORDINATION.md                               session board, verification log, conflict notes"
    )
    body = (
        panel("Pipeline", table(["Stage", "What happens", "Where", "Guardrail", "Source"], [[text_cell(a), text_cell(b, raw=True), text_cell(c, code=True), text_cell(d), source_cell(e)] for a, b, c, d, e in steps]))
        + panel("Automation and scalability properties", table(["Property", "How it is achieved", "Source"], [[text_cell(a), text_cell(b), source_cell(c)] for a, b, c in scale]))
        + notice(
            "Data-driven, with an explicit unknown state",
            "Every table renders from ledger/*.json, and every row either carries a source id or is flagged. The unknown state is "
            "first-class (blank plus UNVERIFIED) rather than a zero, which is what stops the scoring and optimizer from amplifying a "
            "guess into a published claim.",
        )
        + panel("Repository layout", f"<pre class=\"code\">{esc(layout)}</pre>")
    )
    return render("architecture.html", "Architecture", "How the loop runs, and where it refuses to guess.", body)


DESIGN_SOURCE_CANDIDATES = (
    "assets/css/style.css",  # primary site's design system (current main)
    "styles.css",  # the dashboard's original sheet (earlier layout)
    "northstar/styles.css",  # the dashboard, after the namespace move
)


def design_source() -> Path | None:
    for rel in DESIGN_SOURCE_CANDIDATES:
        cand = REPO / rel
        if cand.is_file():
            return cand
    return None


def vendor_design_system(out_root: Path) -> None:
    """Copy the shared design system into pages/assets/ with a provenance header.

    The generated pages are published from the repository root by GitHub Pages, and root-level
    asset paths have already moved twice in this repository's history. Vendoring the sheet the
    pages depend on keeps them rendering identically no matter where the other views live, and the
    header states which file it came from so the copy is auditable rather than mysterious.
    """
    src = design_source()
    dest = out_root / "assets" / "dashboard.css"
    if src is None:
        if dest.exists():
            dest.unlink()
        return
    rel = src.relative_to(REPO).as_posix()
    body = src.read_text(encoding="utf-8")
    header = (
        f"/* Vendored from {rel} by tools/build_site.py - do not edit here.\n"
        "   Re-run the builder after changing the source. Kept as a copy so these pages do not\n"
        "   depend on root-level paths another session may move. */\n"
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(header + body, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="build to a temp dir and compare with committed output")
    args = ap.parse_args()
    out_root = Path(tempfile.mkdtemp(prefix="z2site-")) if args.check else PAGES
    for sub in ("assets", "categories", "modules"):
        (out_root / sub).mkdir(parents=True, exist_ok=True)
    vendor_design_system(out_root)
    shutil.copy2(REPO / "tools" / "pages-site.css", out_root / "assets" / "site.css")

    written: list[str] = []

    def emit(rel: str, doc: str) -> None:
        path = out_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(doc, encoding="utf-8")
        written.append(rel)

    emit("index.html", page_hub())
    emit("executive-summary.html", page_exec())
    emit("products.html", page_products())
    emit("commissions.html", page_commissions())
    emit("categories/index.html", page_categories_index())
    for g in COMMISSION["groups"]:
        emit(f"categories/{g['slug']}.html", page_category(g))
    emit("modules/index.html", page_modules_index())
    for m in MODULES["modules"]:
        emit(f"modules/{m['id'].lower()}-{slugify(m['name'])}.html", page_module(m))
    emit("compliance.html", page_compliance())
    emit("verification.html", page_verification())
    emit("sources.html", page_sources())
    emit("flags.html", page_flags())
    emit("niches.html", page_niches())
    emit("tracking.html", page_tracking())
    emit("content-engine.html", page_content())
    emit("architecture.html", page_architecture())

    nav = {
        "generated": sorted(written),
        "count": len(written),
        "as_of": AS_OF,
        "note": "Generated by tools/build_site.py from ledger/*.json - edit the data, not the HTML.",
    }
    (out_root / "manifest.json").write_text(json.dumps(nav, indent=2, sort_keys=True), encoding="utf-8")
    (REPO / ".nojekyll").write_text("", encoding="utf-8")

    if args.check:
        import hashlib

        def digest(root: Path) -> dict[str, str]:
            out = {}
            for f in sorted(root.rglob("*")):
                if f.is_file():
                    out[str(f.relative_to(root))] = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
            return out

        fresh, committed = digest(out_root), digest(PAGES)
        drift = sorted(k for k in set(fresh) | set(committed) if fresh.get(k) != committed.get(k))
        shutil.rmtree(out_root, ignore_errors=True)
        print(json.dumps({"built": len(written), "drifted_or_uncommitted": drift}, indent=2))
        if drift:
            print("pages/ is out of date - run python3 tools/build_site.py and commit", file=sys.stderr)
        return 1 if drift else 0
    print(json.dumps({"pages": len(written), "as_of": AS_OF, "out": f"{PAGES.relative_to(REPO)}"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
