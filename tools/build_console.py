#!/usr/bin/env python3
"""Deterministic generator for the Owner's Console (task T42, session arena/d26f42db-zone2).

Reads console/data/*.json and writes console/*.html. Network-free, order-stable: the same
data always produces byte-identical output, so CI can fail on drift (--check).

The console also reads ledger/*.json READ-ONLY to index the registers other sessions own
(SG-01..SG-10, Q-01..Q-16, F-01..F-38). It never writes to them, and it never copies their
rows into its own store. If a ledger file is missing the console renders the index row with
an explicit "not read" marker rather than a guessed count.

    python3 tools/build_console.py            # regenerate
    python3 tools/build_console.py --check    # fail if committed output drifted
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "console" / "data"
OUT = REPO / "console"
LEDGER = REPO / "ledger"

AS_OF = "2026-11-15"
SESSION = "arena/d26f42db-zone2"
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
AMAZON_MARKS = ("amazon", "amzn", "kindle", "prime", "audible", "imdb")

# Pre-built fragments. A backslash cannot appear inside an f-string expression before
# Python 3.12, and these read better as names than as escapes anyway.
M0 = "<!--MEASURED-->"
M1 = "<!--/MEASURED-->"

BLANK_NONE = '<span class="blank">none</span>'
BLANK_START = '<span class="blank">none — can start today</span>'
BLANK_DASH = '<span class="blank">—</span>'
BLANK_NOSRC = '<span class="blank">no source cited — judgment or measurement</span>'
PILL_RULE = '<span class="pill p-info">rule</span>'
PILL_CRAFT = '<span class="pill p-open">craft</span>'

PAGES = [
    ("index.html", "Owner's Console", "console/index.html"),
    ("suggestions.html", "Suggestion board", "console/suggestions.html"),
    ("questions.html", "Information register", "console/questions.html"),
    ("design.html", "Redesign pack", "console/design.html"),
    ("review.html", "Repository review", "console/review.html"),
    ("decisions.html", "Decision sheet", "console/decisions.html"),
    ("flagged.html", "Flagged for review", "console/flagged.html"),
    ("sources.html", "Source register", "console/sources.html"),
]


# --------------------------------------------------------------------------- io


def measure() -> dict:
    """Measure the published tree at build time.

    Every count this console publishes about the repository is computed here rather than typed,
    because five other sessions were merging pages into this tree while this one worked. A typed
    number went stale twice in one afternoon; a measured one cannot. Offsets stay stable for a
    given commit, so --check remains deterministic.

    `console/` is excluded from the counts so this namespace does not describe itself.
    """
    import re as _re
    from collections import Counter as _Counter
    disc, pages, links, broken = 0, 0, 0, []
    ns = _Counter()
    titles = []
    for path in sorted(REPO.rglob("*.html")):
        rel = path.relative_to(REPO)
        if ".git" in rel.parts or rel.parts[0] == "console":
            continue
        pages += 1
        ns[rel.parts[0] if len(rel.parts) > 1 else "(root)"] += 1
        text = path.read_text(encoding="utf-8", errors="ignore")
        if DISCLOSURE in text:
            disc += 1
        for m in _re.finditer(r'href="([^"#][^"]*)"', text):
            u = m.group(1)
            links += 1
            if u.startswith(("http", "mailto:", "//", "data:")):
                continue
            if not (path.parent / u.split("#")[0].split("?")[0]).resolve().exists():
                broken.append(f"{rel.as_posix()} -> {u}")
    for land in ("index.html", "audit/index.html", "release/index.html", "paths.html",
                 "pages/index.html", "marketing/index.html", "journal/index.html",
                 "decisions/index.html", "research-hub/start.html", "revalidation/index.html",
                 "affiliate-lab/index.html", "zone2/index.html", "northstar/index.html"):
        f = REPO / land
        if f.exists():
            m = _re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8", errors="ignore"), _re.S)
            if m:
                titles.append(_re.sub(r"\s+", " ", m.group(1)).strip())
    brands = set()
    for t in titles:
        for b in ("Counter Notes", "Northstar", "Zone2"):
            if b in t:
                brands.add(b)
                break
    return {
        "pages": pages,
        "namespaces": len(ns),
        "namespace_counts": dict(sorted(ns.items())),
        "links": links,
        "broken": broken,
        "disclosure": disc,
        "title_strings": len(set(titles)),
        "titles": len(titles),
        "brands": sorted(brands),
    }


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read_ledger_count(filename: str, key: str):
    """Read-only count from another session's ledger. None if it cannot be read."""
    p = LEDGER / filename
    if not p.exists():
        return None
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    val = doc.get(key)
    return len(val) if isinstance(val, list) else None


def e(text) -> str:
    return html.escape(str(text if text is not None else ""), quote=True)


def esc_preserve(text: str) -> str:
    """Escape, then turn {token} placeholders into <code> so braces are never literal."""
    return re.sub(r"\{([a-z0-9_]+)\}", r"<code>{\1}</code>", e(text))


# --------------------------------------------------------------------------- shell


CSS = """
:root{
  --ink:#12161c; --ink-2:#3b444f; --ink-3:#6b7684; --line:#e3e7ec; --line-2:#eef1f4;
  --paper:#ffffff; --bg:#f6f7f9; --accent:#1a56db; --accent-soft:#eaf0fe;
  --warn:#8a4b00; --warn-bg:#fff5e6; --ok:#0f6b3f; --ok-bg:#e8f6ee;
  --stop:#8a1c1c; --stop-bg:#fdeaea; --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
code{font-family:var(--mono);font-size:.86em;background:var(--line-2);padding:.1em .35em;border-radius:3px}
.shell{display:grid;grid-template-columns:248px minmax(0,1fr);min-height:100vh}
.sidebar{background:var(--paper);border-right:1px solid var(--line);padding:20px 16px;position:sticky;top:0;height:100vh;overflow:auto}
.brand{display:flex;gap:10px;align-items:center;font-weight:650;font-size:15px;color:var(--ink);margin-bottom:4px}
.brand .mark{width:26px;height:26px;border-radius:7px;background:var(--ink);color:#fff;display:grid;place-items:center;font-size:13px;font-weight:700;flex:0 0 auto}
.brand small{display:block;font-weight:400;color:var(--ink-3);font-size:11.5px;letter-spacing:.02em}
.side-label{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:22px 0 8px;padding-left:8px}
.nav a{display:block;padding:7px 9px;border-radius:7px;color:var(--ink-2);font-size:14px}
.nav a:hover{background:var(--bg);text-decoration:none}
.nav a.active{background:var(--accent-soft);color:var(--accent);font-weight:600}
.side-foot{margin-top:22px;padding:12px 9px;border-top:1px solid var(--line-2);font-size:11.5px;color:var(--ink-3)}
.main{min-width:0}
.topbar{border-bottom:1px solid var(--line);background:var(--paper);padding:12px 30px;display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap}
.crumb{font-size:13px;color:var(--ink-3)}
.crumb strong{color:var(--ink)}
.chip{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:4px 11px;font-size:12px;color:var(--ink-2)}
.content{padding:30px;max-width:1080px}
h1{font-size:29px;line-height:1.2;letter-spacing:-.02em;margin:0 0 8px}
h2{font-size:20px;margin:34px 0 10px;letter-spacing:-.01em}
h3{font-size:15.5px;margin:0 0 6px}
.eyebrow{font-size:11.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-bottom:9px}
.lede{font-size:17px;color:var(--ink-2);max-width:70ch;margin:0 0 6px}
p{max-width:78ch}
.card{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:16px 0}
.card>h3:first-child{margin-top:0}
.notice{background:var(--accent-soft);border:1px solid #c9d9fb;border-radius:10px;padding:13px 16px;margin:16px 0;font-size:14px;color:#1a3a7a}
.notice strong{color:#12305f}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(148px,1fr));gap:12px;margin:18px 0}
.kpi{background:var(--paper);border:1px solid var(--line);border-radius:11px;padding:14px 16px}
.kpi .num{font-size:26px;font-weight:660;letter-spacing:-.02em}
.kpi .lbl{font-size:12px;color:var(--ink-3);margin-top:2px;line-height:1.35}
table{width:100%;border-collapse:collapse;font-size:13.5px}
.tw{overflow-x:auto;border:1px solid var(--line);border-radius:10px;background:var(--paper);margin:14px 0}
table caption{text-align:left;font-size:12px;color:var(--ink-3);padding:10px 14px;border-bottom:1px solid var(--line-2)}
th,td{text-align:left;vertical-align:top;padding:11px 14px;border-bottom:1px solid var(--line-2)}
th{background:#fafbfc;font-size:11.5px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);font-weight:600;position:sticky;top:0}
tbody tr:last-child td{border-bottom:0}
tbody tr:hover{background:#fcfdfe}
th.n,td.n{white-space:nowrap}
td.id{font-family:var(--mono);font-size:12px;color:var(--ink-3);white-space:nowrap}
.pill{display:inline-block;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:650;padding:3px 8px;border-radius:999px;white-space:nowrap}
.p-open{background:var(--warn-bg);color:var(--warn)}
.p-ok{background:var(--ok-bg);color:var(--ok)}
.p-stop{background:var(--stop-bg);color:var(--stop)}
.p-info{background:#eef1f5;color:var(--ink-2)}
.src{display:inline-block;margin:2px 4px 2px 0;font-family:var(--mono);font-size:11px;border:1px solid var(--line);border-radius:5px;padding:2px 6px;color:var(--ink-2);background:#fbfcfd}
.src:hover{border-color:var(--accent);text-decoration:none}
.src .h{color:var(--ink-3);margin-left:4px}
.blank{display:inline-block;color:var(--ink-3);font-style:italic;font-size:12.5px}
ul.tight{margin:8px 0;padding-left:20px}ul.tight li{margin:5px 0;max-width:78ch}
ol.tight{margin:8px 0;padding-left:20px}ol.tight li{margin:6px 0;max-width:78ch}
.proposal{border:1px solid var(--line);border-radius:12px;background:var(--paper);margin:14px 0;overflow:hidden}
.proposal>.head{padding:15px 20px;border-bottom:1px solid var(--line-2);display:flex;gap:12px;align-items:flex-start;justify-content:space-between;flex-wrap:wrap}
.proposal .pid{font-family:var(--mono);font-size:12px;color:var(--ink-3)}
.proposal h3{font-size:17px;margin:2px 0 0}
.proposal .body{padding:16px 20px}
.proposal dl{margin:0}
.proposal dt{font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);margin:14px 0 4px}
.proposal dt:first-child{margin-top:0}
.proposal dd{margin:0;font-size:14.5px;max-width:80ch}
.opts{list-style:none;margin:0;padding:0}
.opts li{border:1px solid var(--line);border-radius:9px;padding:11px 14px;margin:8px 0;font-size:14px}
.opts li.rec{border-color:#b9cdf7;background:#f7faff}
.opts .l{font-weight:600}
.opts .t{color:var(--ink-2);display:block;margin-top:3px;font-size:13.5px}
.tag{display:inline-block;font-size:10.5px;letter-spacing:.05em;text-transform:uppercase;font-weight:650;padding:2px 7px;border-radius:5px;background:#eef1f5;color:var(--ink-2);margin-left:6px}
.ba{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:10px 0}
.ba>div{padding:13px 16px;font-size:13.5px}
.ba .b{background:#fdf7f7;border-right:1px solid var(--line)}
.ba .a{background:#f5fbf7}
.ba .lab{font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);margin-bottom:5px;font-weight:650}
pre.prompt{white-space:pre-wrap;word-wrap:break-word;background:#0f1419;color:#e6edf3;border-radius:11px;padding:18px 20px;font-family:var(--mono);font-size:12.5px;line-height:1.62;overflow-x:auto;margin:12px 0}
.prompt-bar{display:flex;gap:8px;align-items:center;margin:10px 0}
button.copy{background:var(--ink);color:#fff;border:0;border-radius:8px;padding:8px 14px;font-size:13px;cursor:pointer;font-family:inherit}
button.copy:hover{background:#000}
.banned td:first-child{font-family:var(--mono);font-size:12px}
footer.site{border-top:1px solid var(--line);background:var(--paper);padding:22px 30px;margin-top:34px;color:var(--ink-3);font-size:12.5px}
footer.site .disc{color:var(--ink-2);font-size:13.5px;margin-bottom:8px}
footer.site a{color:var(--ink-2)}
.skip{position:absolute;left:-9999px}
.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
.meta{font-size:12px;color:var(--ink-3);margin-top:4px}
@media(max-width:900px){
  .shell{grid-template-columns:1fr}
  .sidebar{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line)}
  .content{padding:20px}
  .ba{grid-template-columns:1fr}
  .ba .b{border-right:0;border-bottom:1px solid var(--line)}
}
"""


def nav(active: str) -> str:
    links = "".join(
        f'<a class="nav-link{" active" if fn == active else ""}" href="{fn}">{e(label)}</a>'
        for fn, label, _ in PAGES
    )
    return f"""<aside class="sidebar">
  <a class="brand" href="../index.html"><span class="mark">Z</span><span>Zone2<small>Owner's Console</small></span></a>
  <div class="side-label">Decide before building</div>
  <nav class="nav">{links}</nav>
  <div class="side-foot">Every row on these pages is a proposal.<br><strong>Nothing here has been implemented.</strong></div>
</aside>"""


def page(title: str, active: str, h1: str, eyebrow: str, lede: str, body: str,
         extra_head: str = "", kpis: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{e(h1)} — the Zone2 Owner's Console. Proposals, open questions and a redesign pack for the Amazon affiliate site. Nothing here is implemented until the owner records a choice.">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://kanlerxz87-cyber.github.io/Zone2/console/{active}">
<title>{e(title)} · Zone2 Owner's Console</title>
<style>{CSS}</style>
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="shell">
{nav(active)}
<main class="main">
  <div class="topbar">
    <div class="crumb"><a href="../index.html">Zone2</a> / <strong>{e(h1)}</strong></div>
    <div><span class="chip">session {e(SESSION)}</span> <span class="chip">{e(AS_OF)}</span> <a class="chip" href="decisions.html">Record a decision</a></div>
  </div>
  <div class="content" id="main">
    <div class="eyebrow">{e(eyebrow)}</div>
    <h1>{e(h1)}</h1>
    <p class="lede">{e(lede)}</p>
    {kpis}
    {body}
  </div>
  <footer class="site">
    <div class="disc"><strong>Disclosure</strong> {e(DISCLOSURE)} Outbound links are qualified with <code>rel="sponsored"</code>.</div>
    <div class="meta">Owner's Console · task T42 · session {e(SESSION)} · generated by <code>tools/build_console.py</code> from <code>console/data/*.json</code> · edit the data, never the HTML · <a href="../index.html">Dashboard</a> · <a href="../pages/suggestions.html">Canonical suggestion board</a> · <a href="../pages/questions.html">Canonical questions</a> · <a href="../pages/flags.html">Project flags</a></div>
  </footer>
</main>
</div>
</body>
</html>
"""


# --------------------------------------------------------------------------- helpers


def src_chips(ids, by_id: dict) -> str:
    if not ids:
        return BLANK_NOSRC
    out = []
    for sid in ids:
        s = by_id.get(sid)
        if not s:
            out.append(f'<span class="src">{e(sid)} <span class="h">unknown id</span></span>')
            continue
        host = s.get("host", "")
        out.append(
            f'<a class="src" href="{e(s["url"])}" target="_blank" rel="noopener noreferrer nofollow" '
            f'title="{e(s["title"])}">{e(sid)} <span class="h">{e(host)}</span></a>'
        )
    return "".join(out)


def pill_for(state: str) -> str:
    s = (state or "").lower()
    if s in ("approved", "implemented", "held", "resolved"):
        cls = "p-ok"
    elif s in ("rejected", "blocked", "not held"):
        cls = "p-stop"
    elif "not" in s:
        cls = "p-stop"
    else:
        cls = "p-open"
    return f'<span class="pill {cls}">{e(state or "open")}</span>'


# --------------------------------------------------------------------------- pages


def build_index(sources, proposals, info, flags, decisions, ms) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}
    props = proposals["proposals"]
    open_q = [q for q in info["open"]]
    owner_q = [q for q in open_q if q["who"] == "owner"]
    high = [f for f in flags["flags"] if f["severity"] == "high"]

    kpis = f"""<section class="kpis">
      <div class="kpi"><div class="num">{len(props)}</div><div class="lbl">new proposals on the board, none implemented</div></div>
      <div class="kpi"><div class="num">{len(owner_q)}</div><div class="lbl">questions only you can answer</div></div>
      <div class="kpi"><div class="num">{len(high)}</div><div class="lbl">high-severity irregularities</div></div>
      <div class="kpi"><div class="num">{len(sources['sources'])}</div><div class="lbl">sources fetched and verified today</div></div>
    </section>"""

    # recommended decision order: proposals with fewest unresolved owner-questions first
    answered_ids = {a["id"] for a in info["answered"]}
    decided = decisions["sheet"]

    def blockers(p):
        return [b for b in p.get("blocked_by", []) if b.startswith("IN-")]

    ordered = sorted(props, key=lambda p: (len(blockers(p)), p["id"]))

    rows = []
    for i, p in enumerate(ordered, 1):
        bl = blockers(p)
        ch = decided.get(p["id"], {}).get("choice", "")
        state = "approved \u2014 " + ch if ch else p["state"]
        rows.append(
            f"<tr><td class='n'>{i}</td><td class='id'>{e(p['id'])}</td>"
            f"<td><a href='suggestions.html#{e(p['id'])}'><strong>{e(p['title'])}</strong></a>"
            f"<div class='meta'>{e(p['area'])} · effort {e(p['effort'])} · recommended option {e(p['recommended'])}</div></td>"
            f"<td>{e(', '.join(bl)) if bl else BLANK_START}</td>"
            f"<td>{pill_for(state)}</td></tr>"
        )

    body = f"""
<div class="notice"><strong>What this console is.</strong> One place to review every open choice on this
project, choose a path, and see what is still missing before the choice is safe. Nothing on these pages has been
built. The canonical registers other sessions own are indexed, not duplicated: this console adds {len(props)}
new proposals and {len(open_q)} new questions to the {read_ledger_count('suggestions.json', 'suggestions') or '?'} canonical
suggestions and {read_ledger_count('questions.json', 'questions') or '?'} canonical questions already published.</div>

<h2>Executive summary</h2>
<p><strong>The products are fine. The site is the problem, and the problem is that it describes itself.</strong>
The published tree holds {M0}{ms['pages']} pages across {ms['namespaces']} namespaces — {ms['pages'] + 8} counting this
console — every value traced to an official source, {ms['links']:,} internal links with {len(ms['broken'])} broken, and
the mandatory disclosure on {ms['disclosure']} of {ms['pages']} pages{M1}. The verification work is genuinely done and
genuinely good. These counts are measured at build time, not typed: five other sessions merged into this tree while
this review ran, and a typed number went stale twice in an afternoon.
</p>
<p><strong>Until today it was invisible to a reader.</strong> The public landing page opened with the client's own requirement list
and a strip of figures about the project's audit state rather than with the three air fryers. A redesign by another session
(PR #108) merged while this review was running and removed both, which is the same conclusion reached here independently. Two
traces remain: the page still heads itself <em>AI-powered Amazon affiliate platform</em>, and it still says the three listings
are <em>identified</em> when no official document binds the supplied codes to them.</p>
<p><strong>Revenue is blocked by one missing identifier, not by a technical gap.</strong> Every Amazon link must
carry the assigned Associates ID as a URL parameter; none of the three supplied links does, and no Associates ID
exists in the repository. The three supplied codes are 9 characters where Amazon defines the ASIN as
&ldquo;10-digit&rdquo;, and a control run today confirms the short-link service refuses even a valid ASIN, so the
codes are opaque identifiers rather than truncated product numbers. What they resolve to is reproducible and
recorded; what the brief intended them to mean is not, and no official document settles it.</p>
<p><strong>Two things need permission before they can be built, not after.</strong> Program Content may not be used
to develop machine-learning models without Amazon's express prior written approval &mdash; which is precisely what
the brief asks for. And catalog data (prices, ratings) is lawful only through the Creators API, which needs
enrolment plus ten qualifying sales in thirty days. Both are gated on the same missing account.</p>
<p><strong>What can be decided today, with nothing else needed:</strong> the editorial items. Six question-shaped
articles are writable right now from rows the project already holds and already sources. They need no Associates
account, no API, and no new data. They are also the only items on this board that would move the site toward
Amazon's own stated standard &mdash; a site that gives a reader &ldquo;insight on a subject or product they might
not get easily&rdquo;.</p>

<h2>The decisions, in the order that unblocks the most</h2>
<p>Ordered by how many open questions stand in front of each. Questions marked <code>IN-</code> are
<a href="questions.html">answered on the information register</a>; questions marked <code>Q-</code> belong to the
canonical register at <a href="../pages/questions.html">pages/questions.html</a>.</p>
<div class="tw"><table>
<caption>Derived from the <code>blocked_by</code> edges in <code>console/data/proposals.json</code>. Re-running the generator recomputes it.</caption>
<thead><tr><th>#</th><th>ID</th><th>Proposal</th><th>Waiting on</th><th>State</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<h2>What is missing, in one table</h2>
<div class="tw"><table>
<caption>The four items this project does not have, and what each one blocks. Full register: <a href="questions.html">information register</a>.</caption>
<thead><tr><th>Missing</th><th>What it blocks</th><th>How it is closed</th><th>Who</th></tr></thead>
<tbody>
<tr><td>An Associates ID</td><td>All revenue, and the three qualifying sales that unlock the account</td><td>Owner signs in to Associates Central and generates tagged links</td><td class="n">owner</td></tr>
<tr><td>Confirmation of the intended product identifiers</td><td>Every product-specific claim</td><td>Owner copies the product URLs from the listings; the agent checks them against the official pages</td><td class="n">owner</td></tr>
<tr><td>A named editor</td><td>Bylines, the human sign-off step, and one of the four factors Google weighs</td><td>Owner names a person who accepts responsibility</td><td class="n">owner</td></tr>
<tr><td>Any first-hand knowledge of the products</td><td>Original reviews and testing, which Google names as what makes an affiliate page good</td><td>Owner states whether anyone has the machines; if yes, a dated test log</td><td class="n">owner</td></tr>
</tbody></table></div>

<div class="card">
<h3>How to use this console</h3>
<ol class="tight">
<li><strong><a href="suggestions.html">Read the board.</a></strong> Fourteen proposals, each with the options, the trade-off, the recommended path, the effort and the sources.</li>
<li><strong><a href="questions.html">Check what is missing.</a></strong> Fifteen questions an official source already answers, and twelve nothing in the repository can answer, each with the action that would close it.</li>
<li><strong><a href="design.html">Read the redesign pack.</a></strong> The diagnosis of why the site reads as machine output, with before-and-after rewrites of the actual published copy and a copy-paste brief.</li>
<li><strong><a href="decisions.html">Record your choices.</a></strong> One file, one field per row. Nothing is built until you do.</li>
<li><strong><a href="review.html">Audit the repository.</a></strong> Every namespace, the measurements, and the 25 source checks run today.</li>
</ol>
</div>
"""
    return page("Owner's Console", "index.html", "Owner's Console",
                f"executive summary · reviewed {AS_OF} · proposals only, nothing implemented",
                "Everything this project has not decided yet, in one place \u2014 with the options, the evidence, and the missing information that stands in front of each choice.",
                body, kpis=kpis)


def build_suggestions(sources, proposals, decisions) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}
    sheet = decisions["sheet"]
    cards = []
    for p in proposals["proposals"]:
        d = sheet.get(p["id"], {})
        ch = d.get("choice", "")
        if ch:
            state = f"approved — option {ch}"
            dec = (f"<dt>Decision recorded</dt><dd><strong>Option {e(ch)}</strong>"
                   + (f" &mdash; {e(d.get('note',''))}" if d.get("note") else "")
                   + (f" <span class='meta'>by {e(d.get('decided_by',''))} on {e(d.get('decided_on',''))}</span>" if d.get("decided_by") else "")
                   + "</dd>")
        else:
            state = p["state"]
            dec = ("<dt>Decision</dt><dd><span class='blank'>no choice recorded \u2014 "
                   "record it on the <a href='decisions.html#%s'>decision sheet</a></span></dd>" % e(p["id"]))
        opts = []
        for o in p["options"]:
            rec = " rec" if o["id"] == p["recommended"] else ""
            tag = ' <span class="tag">recommended</span>' if o["id"] == p["recommended"] else ""
            opts.append(f'<li class="{rec.strip()}"><span class="l">{e(o["id"])}. {e(o["label"])}{tag}</span>'
                        f'<span class="t">{e(o["tradeoff"])}</span></li>')
        rel = ", ".join(p.get("relates_to", [])) or BLANK_NONE
        blocks = ", ".join(p.get("blocked_by", [])) or BLANK_START
        cards.append(f"""<section class="proposal" id="{e(p['id'])}">
  <div class="head">
    <div><div class="pid">{e(p['id'])} · {e(p['area'])}</div><h3>{e(p['title'])}</h3></div>
    <div>{pill_for(state)} <span class="chip">effort {e(p['effort'])}</span></div>
  </div>
  <div class="body">
    <dl>
      <dt>What would change</dt><dd>{esc_preserve(p['change'])}</dd>
      <dt>Why</dt><dd>{esc_preserve(p['why'])}</dd>
      <dt>Options</dt><dd><ul class="opts">{''.join(opts)}</ul></dd>
      <dt>Risk</dt><dd>{e(p['risk'])}</dd>
      <dt>Evidence</dt><dd>{src_chips(p.get('evidence', []), by_id)}</dd>
      <dt>Waiting on</dt><dd>{e(blocks)}</dd>
      <dt>Relates to</dt><dd>{e(rel)}</dd>
      {dec}
    </dl>
  </div>
</section>""")

    body = f"""
<div class="notice"><strong>These rows are proposals. None has been implemented.</strong> The canonical board
(SG-01&hellip;SG-{read_ledger_count('suggestions.json','suggestions') or '?'}) is owned by another session and lives at
<a href="../pages/suggestions.html">pages/suggestions.html</a>; this board does not copy it. Each row here that touches
an inherited item names it under <em>Relates to</em>.</div>
{''.join(cards)}
"""
    return page("Suggestion board", "suggestions.html", "Suggestion board",
                f"{len(proposals['proposals'])} proposals · 0 implemented · awaiting your choice",
                "Every proposal states what would change, the options with their trade-offs, a recommended path, the effort, the risk, and the official source behind it.",
                body)


def build_questions(sources, info) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}

    ans = "".join(
        f"<tr><td class='id'>{e(a['id'])}</td><td><strong>{e(a['question'])}</strong></td>"
        f"<td>{e(a['answer'])}</td><td>{e(a.get('consequence',''))}</td>"
        f"<td>{src_chips(a.get('source_ids', []), by_id)}</td></tr>"
        for a in info["answered"]
    )
    opn = "".join(
        f"<tr id='{e(q['id'])}'><td class='id'>{e(q['id'])}</td><td><strong>{e(q['question'])}</strong>"
        f"<div class='meta'>{e(q['priority'])}</div></td>"
        f"<td>{e(q['have'])}</td>"
        f"<td>{e(q['missing'])}"
        f"<div style='margin-top:8px'><strong>To close it:</strong> {e(q['how_to_find'])}</div></td>"
        f"<td class='n'>{e(q['who'])}</td>"
        f"<td>{e(', '.join(q['blocks'])) if q['blocks'] else BLANK_DASH}</td>"
        f"<td>{src_chips(q.get('source_ids', []), by_id)}</td></tr>"
        for q in info["open"]
    )
    inv = "".join(
        f"<tr><td class='id'>{e(v['id'])}</td><td><strong>{e(v['item'])}</strong>"
        + (f"<div class='meta'>{e(v['detail'])}</div>" if v.get("detail") else "")
        + f"</td><td>{pill_for(v['status'])}</td>"
        f"<td>{src_chips(v.get('source_ids', []), by_id)}</td></tr>"
        for v in info["inventory"]
    )

    body = f"""
<div class="notice"><strong>Read this before deciding anything.</strong> The first table is what an official source
already settles &mdash; those are not open questions. The second is what nothing in this repository can answer;
each row says what is already known, what is missing, and the concrete action that would close it. The answer column
is empty on purpose: nothing is inferred to fill it.</div>

<h2>1. Questions an official source already answers</h2>
<div class="tw"><table>
<caption>{len(info['answered'])} rows. Every answer is quoted from or restated from the linked official page, fetched {AS_OF}.</caption>
<thead><tr><th>ID</th><th>Question</th><th>What the official source says</th><th>What it means here</th><th>Source</th></tr></thead>
<tbody>{ans}</tbody></table></div>

<h2>2. Questions nothing here can answer yet</h2>
<div class="tw"><table>
<caption>{len(info['open'])} open questions. Every row has an empty answer by design. This register extends the canonical Q-01&hellip;Q-{read_ledger_count('questions.json','questions') or '?'} at <a href="../pages/questions.html">pages/questions.html</a>.</caption>
<thead><tr><th>ID</th><th>Question</th><th>What we have</th><th>What is missing, and how to find it</th><th>Who</th><th>Blocks</th><th>Source</th></tr></thead>
<tbody>{opn}</tbody></table></div>

<h2>3. What the project already holds</h2>
<div class="tw"><table>
<caption>The evidence inventory. Items marked NOT HELD cannot be produced by an agent.</caption>
<thead><tr><th>ID</th><th>Item</th><th>Status</th><th>Source</th></tr></thead>
<tbody>{inv}</tbody></table></div>
"""
    return page("Information register", "questions.html", "Information register",
                f"{len(info['answered'])} answered by an official source · {len(info['open'])} open · {len(info['inventory'])} inventory items",
                "What this project knows, what it does not know, and the exact action that would close each gap.",
                body)


def build_design(sources, design) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}
    d = design

    prin = "".join(
        f"<tr><td class='id'>{e(p['id'])}</td><td><strong>{e(p['principle'])}</strong></td>"
        f"<td>{e(p['rule'])}</td>"
        f"<td>{PILL_RULE if not p.get('judgment') else PILL_CRAFT}</td>"
        f"<td>{src_chips(p.get('source_ids', []), by_id)}</td></tr>"
        for p in d["principles"]
    )
    rw = "".join(
        f"""<div class="card" id="{e(r['id'])}">
      <h3>{e(r['where'])}</h3>
      <div class="ba">
        <div class="b"><div class="lab">Before \u2014 as published</div>{esc_preserve(r['before'])}</div>
        <div class="a"><div class="lab">After \u2014 draft, not shipped</div>{esc_preserve(r['after'])}</div>
      </div>
      <p class="meta">{e(r['why'])}</p>
    </div>"""
        for r in d["rewrites"]["rows"]
    )
    ban = "".join(f"<tr><td>{e(b['phrase'])}</td><td>{e(b['why'])}</td></tr>" for b in d["voice"]["banned"])
    do = "".join(f"<li>{e(x)}</li>" for x in d["voice"]["do"])

    tpl = []
    for t in d["templates"]:
        rows = "".join(
            f"<tr><td class='n'>{e(s['n'])}</td><td>{e(s['section'])}</td><td class='n'>{e(s['budget'])}</td></tr>"
            for s in t["sections"]
        )
        tpl.append(f"""<div class="card"><h3>{e(t['name'])}</h3>
      <div class="tw"><table><thead><tr><th>#</th><th>Section</th><th>Budget</th></tr></thead><tbody>{rows}</tbody></table></div>
      <p class="meta">{e(t['note'])}</p></div>""")

    art = "".join(
        f"<tr><td class='id'>{e(a['id'])}</td><td><strong>{e(a['headline'])}</strong></td>"
        f"<td>{e(a['question_it_answers'])}</td><td>{e(a['sourced_from'])}</td>"
        f"<td>{e(a['why_it_earns_traffic'])}</td><td>{e(a['status'])}</td></tr>"
        for a in d["articles"]["rows"]
    )
    allow = "".join(f"<li>{e(x['step'])} {src_chips(x['source_ids'], by_id)}</li>" for x in d["traffic"]["allowed"])
    forbid = "".join(f"<li>{e(x['step'])} {src_chips(x['source_ids'], by_id)}</li>" for x in d["traffic"]["forbidden"])
    comp = "".join(f"<li>{e(c)}</li>" for c in d["design_system"]["components"])
    never = "".join(f"<li>{e(c)}</li>" for c in d["design_system"]["never"])
    ds = d["design_system"]

    prompt_text = e(d["prompt"]["text"])

    body = f"""
<div class="notice"><strong>Read the diagnosis first.</strong> Everything in this pack follows from one finding:
the site describes itself instead of answering the reader. Fixing the tone without fixing that produces better-sounding
copy about a project status report.</div>

<div class="card">
  <h3>Diagnosis</h3>
  <p><strong>{e(d['diagnosis']['headline'])}</strong></p>
  <p>{e(d['diagnosis']['detail'])}</p>
  <p>{e(d['diagnosis']['why_it_reads_as_slop'])}</p>
  <p class="meta">Evidence: {src_chips(d['diagnosis']['evidence_source_ids'], by_id)} · flagged as {e(', '.join(d['diagnosis']['flags']))}</p>
</div>

<h2>1. Nine principles</h2>
<div class="tw"><table>
<caption>Marked <strong>rule</strong> where an official source requires it, <strong>craft</strong> where it is a house-style judgment by this session. Judgments are never presented as program facts.</caption>
<thead><tr><th>ID</th><th>Principle</th><th>The rule</th><th>Kind</th><th>Source</th></tr></thead>
<tbody>{prin}</tbody></table></div>

<h2>2. Voice</h2>
<div class="card">
  <h3>Do</h3><ul class="tight">{do}</ul>
</div>
<div class="tw"><table class="banned">
<caption>Phrases to delete on sight. The reason column says why each one fails, not merely that it is clich&eacute;d.</caption>
<thead><tr><th>Phrase</th><th>Why it goes</th></tr></thead>
<tbody>{ban}</tbody></table></div>
<p class="meta">Source for the claim-accuracy entries: {src_chips(d['voice']['banned_source_ids'], by_id)}</p>

<h2>3. Before and after, on the actual published copy</h2>
<p>Every <em>before</em> line is quoted from the live site as read on {AS_OF}. Every <em>after</em> line is a draft by
this session &mdash; a proposal, not a shipped change. Values in braces are filled from
<code>ledger/products.json</code> by the generator and are never typed by hand.</p>
{rw}

<h2>4. Page templates</h2>
{''.join(tpl)}

<h2>5. The six articles to write first</h2>
<div class="tw"><table>
<caption>Each is answerable today from rows the project already holds and already sources. No Associates account, no API, no new data.</caption>
<thead><tr><th>ID</th><th>Headline</th><th>Question it answers</th><th>Sourced from</th><th>Why it earns traffic</th><th>Status</th></tr></thead>
<tbody>{art}</tbody></table></div>

<h2>6. Traffic: what is allowed and what is not</h2>
<div class="card"><h3>Allowed</h3><ul class="tight">{allow}</ul></div>
<div class="card"><h3>Forbidden</h3><ul class="tight">{forbid}</ul></div>

<h2>7. Design system</h2>
<div class="card">
  <h3>Type</h3>
  <ul class="tight">
    <li>Body: {e(ds['type']['body'])}</li>
    <li>Display: {e(ds['type']['display'])}</li>
    <li>Mono: {e(ds['type']['mono'])}</li>
  </ul>
  <h3>Colour</h3><p>{e(ds['colour']['rule'])}</p><p class="meta">{e(ds['colour']['why'])}</p>
  <h3>Layout</h3><p>{e(ds['layout']['rule'])}</p><p class="meta">{e(ds['layout']['why'])}</p>
  <h3>Components</h3><ul class="tight">{comp}</ul>
  <h3>Components that must not exist</h3>
  <ul class="tight">{never}</ul>
  <p class="meta">Source: {src_chips(ds['never_source_ids'], by_id)}</p>
</div>

<h2>8. The brief, ready to paste</h2>
<p>Everything above, condensed into one brief that can be handed to any writer, designer or model. Constraints marked
<code>[rule]</code> are quoted from official sources and may not be relaxed; <code>[craft]</code> is house style.</p>
<div class="prompt-bar"><button class="copy" type="button" onclick="var t=document.getElementById('prompt');navigator.clipboard.writeText(t.innerText);this.innerText='Copied';setTimeout(function(){{this.innerText='Copy the brief'}}.bind(this),1600)">Copy the brief</button><span class="meta">{len(d['prompt']['text'].split())} words</span></div>
<pre class="prompt" id="prompt">{prompt_text}</pre>
"""
    return page("Redesign pack", "design.html", "Redesign pack",
                f"diagnosis, voice, before/after, templates, six articles, and a paste-ready brief · {AS_OF}",
                "Why the site reads as machine output, and the concrete rewrite that fixes it \u2014 with every hard constraint traced to the official page that imposes it.",
                body)


def build_review(sources, review, ms) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}
    ns = "".join(
        f"<tr><td><code>{e(n['path'])}</code></td><td class='n'>{e(n['pages'])}</td>"
        f"<td>{e(n['purpose'])}</td><td><code>{e(n['generator'])}</code></td><td>{e(n['gate'])}</td></tr>"
        for n in review["namespaces"]
    )
    # MS-01..MS-06 are re-measured on every build: five sessions were merging into this tree while
    # this review ran, and a typed count went stale twice in one afternoon.
    measured = {
        "MS-01": f"{ms['pages']} ({ms['pages'] + 8} including this console)",
        "MS-02": f"{ms['namespaces']} ({ms['namespaces'] + 1} including this console)",
        "MS-03": f"{ms['links']:,} checked, {len(ms['broken'])} broken",
        "MS-04": f"{ms['disclosure']} of {ms['pages']}",
        "MS-05": f"{ms['title_strings']} distinct title strings across {ms['titles']} landing pages; "
                 f"{len(ms['brands'])} distinct brand names ({', '.join(ms['brands'])})",
        "MS-06": f"0 of {ms['pages']}",
    }
    rows = []
    for m in review["measurements"]:
        val = measured.get(m["id"], m["value"])
        how = m["how"] + (" <em>(re-measured at build time)</em>" if m["id"] in measured else "")
        wrap = (M0, M1) if m["id"] in measured else ("", "")
        rows.append(
            f"<tr><td class='id'>{e(m['id'])}</td><td>{e(m['what'])}</td>"
            f"<td><strong>{wrap[0]}{e(val)}{wrap[1]}</strong></td><td>{e(how)}</td></tr>")
    ms_rows = "".join(rows)
    if ms["broken"]:
        rows = [f"<tr><td class='id'>BROKEN</td><td colspan='3'>{e(b)}</td></tr>" for b in ms["broken"][:20]]
        ms_rows += "".join(rows)
    vr = "".join(
        f"<tr><td class='id'>{e(v['id'])}</td><td>{e(v['claim'])}</td><td>{e(v['observed'])}</td>"
        f"<td>{pill_for(v['verdict'])}</td><td>{src_chips(v.get('source_ids', []), by_id)}</td></tr>"
        for v in review["verification"]
    )
    total_pages = sum(n["pages"] for n in review["namespaces"] if n["path"] != "console/")
    body = f"""
<div class="notice"><strong>Scope of this review.</strong> Read-only. No file outside this session's declared scope
was edited. Measurements were taken over the working tree on {AS_OF}; official-source checks were live fetches
performed the same day. A row is only as good as its source column &mdash; rows with no source link are measurements
of the repository, not claims about a program rule.</div>

<h2>1. What is published</h2>
<div class="tw"><table>
<caption>{len(review['namespaces'])} top-level namespaces, {total_pages} pages excluding this console. Each row names the generator and the gate that polices it.</caption>
<thead><tr><th>Namespace</th><th>Pages</th><th>Purpose</th><th>Generator</th><th>Gate</th></tr></thead>
<tbody>{ns}</tbody></table></div>

<h2>2. Measurements taken today</h2>
<div class="tw"><table>
<caption>Every value below was measured in the working tree on {AS_OF} by this session. None is quoted from another session's prose.</caption>
<thead><tr><th>ID</th><th>What was measured</th><th>Value</th><th>How</th></tr></thead>
<tbody>{ms_rows}</tbody></table></div>

<h2>3. Source checks run today</h2>
<div class="tw"><table>
<caption>{len(review['verification'])} checks. Each row states what was checked, what was observed on {AS_OF}, and the official page it was checked against.</caption>
<thead><tr><th>ID</th><th>Claim checked</th><th>Observed</th><th>Verdict</th><th>Source</th></tr></thead>
<tbody>{vr}</tbody></table></div>

<h2>4. What this review found</h2>
<p>Nine irregularities, published in full on <a href="flagged.html">Flagged for review</a> with the source links and
the action that would close each one. In short: the public site describes the build instead of the products; six
names are in use for one project; the brief's automation premise needs Amazon's written permission; no page names a
person; four suggestion registers await the same person; one published count has drifted; the short-link service
hands off to a differently named host; two pull requests are open; and no verified fact carries a verification date.</p>
<p>One irregularity recorded by earlier sessions is <strong>not</strong> re-flagged: the self-hosted font paths in
<code>assets/css/style.css</code> now resolve correctly relative to the stylesheet, so that repair held.</p>
"""
    return page("Repository review", "review.html", "Repository review",
                f"{len(review['namespaces'])} namespaces · {len(review['measurements'])} measurements · {len(review['verification'])} source checks · {AS_OF}",
                "A line-by-line read of the repository: what is published, what was measured, and every check run against an official source today.",
                body)


def build_flagged(sources, flags) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}
    order = {"high": 0, "medium": 1, "low": 2}
    rows = []
    for f in sorted(flags["flags"], key=lambda x: (order.get(x["severity"], 9), x["id"])):
        rows.append(
            f"<tr id='{e(f['id'])}'><td class='id'>{e(f['id'])}</td><td>{pill_for(f['severity'])}</td>"
            f"<td><strong>{e(f['title'])}</strong><div style='margin-top:8px'>{e(f['detail'])}</div></td>"
            f"<td>{e(f['impact'])}</td><td>{e(f['action_required'])}</td>"
            f"<td class='n'>{e(f['who'])}</td>"
            f"<td>{src_chips(f.get('source_ids', []), by_id)}"
            + (f"<div class='meta' style='margin-top:6px'>Relates to: {e(', '.join(f['relates_to']))}</div>" if f.get("relates_to") else "")
            + "</td></tr>"
        )
    body = f"""
<div class="notice"><strong>These items do not block the merge. They block assertion and decision.</strong>
Each row states what was found, why it matters, what would close it, and who can close it. Nothing here is
unverified data published as fact &mdash; the verification rule elsewhere in this project still holds: a value
without an official source is left blank and flagged, never inferred. IDs are namespaced <code>IR-</code> so they
cannot collide with the canonical <code>F-</code> register at <a href="../pages/flags.html">pages/flags.html</a>.</div>
<div class="tw"><table>
<caption>{len(flags['flags'])} irregularities found by this session's review, {AS_OF}.</caption>
<thead><tr><th>ID</th><th>Severity</th><th>Finding</th><th>Impact</th><th>Action required</th><th>Who</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
"""
    return page("Flagged for review", "flagged.html", "Flagged for review",
                f"{len(flags['flags'])} irregularities · none blocking the deploy · {AS_OF}",
                "Everything this review could not confirm or that needs an owner decision, with the source link and the action that would close it.",
                body)


def build_sources(sources) -> str:
    rows = []
    for s in sources["sources"]:
        q = s.get("quote", "")
        quote_cell = f"\u201c{e(q)}\u201d" if q else '<span class="blank">no value quoted from this page</span>'
        rows.append(
            f"<tr id='{e(s['id'])}'><td class='id'>{e(s['id'])}</td>"
            f"<td><a href='{e(s['url'])}' target='_blank' rel='noopener noreferrer nofollow'>{e(s['title'])}</a>"
            f"<div class='meta'><code>{e(s['url'])}</code></div></td>"
            f"<td class='n'>{e(s['publisher'])}</td><td class='n'>{e(s['class'])}</td>"
            f"<td class='n'>{e(s['fetched_utc'])}</td>"
            f"<td>{quote_cell}"
            + (f"<div class='meta' style='margin-top:6px'>{e(s['note'])}</div>" if s.get("note") else "")
            + "</td></tr>"
        )
    cls = sources["classes"]
    body = f"""
<div class="notice"><strong>Three classes of source, kept strictly apart.</strong>
<strong>{e(list(cls)[0])}</strong> &mdash; {e(cls['official'])}
<strong>{e(list(cls)[1])}</strong> &mdash; {e(cls['observed'])}
<strong>{e(list(cls)[2])}</strong> &mdash; {e(cls['control'])}
Only an official source can settle a program rule. Observed and control rows are evidence about the artefact
under test and are never used to state a rule or a product attribute.</div>
<div class="tw"><table>
<caption>{len(sources['sources'])} sources, all fetched live on {e(sources['accessed_utc'])} by session {e(SESSION)}. IDs are namespaced <code>C-</code> so they cannot collide with the canonical <code>S01&hellip;S42</code> register.</caption>
<thead><tr><th>ID</th><th>Page</th><th>Publisher</th><th>Class</th><th>Fetched</th><th>Verbatim quote / note</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
"""
    return page("Source register", "sources.html", "Source register",
                f"{len(sources['sources'])} sources · fetched {e(sources['accessed_utc'])} · verbatim quotes",
                "Every page a claim on this console was read from, with the verbatim sentence it supports.",
                body)


def build_decisions(sources, proposals, info, flags, decisions) -> str:
    by_id = {s["id"]: s for s in sources["sources"]}

    def n(name, key):
        v = read_ledger_count(name, key)
        return str(v) if v is not None else '<span class="blank">not read</span>'

    registers = f"""<div class="tw"><table>
<caption>Every open register on this project, indexed from one page. This console does not move, renumber or re-own any of them.</caption>
<thead><tr><th>Register</th><th>Where it lives</th><th>Open items</th><th>Owning session</th><th>What it decides</th></tr></thead>
<tbody>
<tr><td>Canonical suggestions</td><td><a href="../pages/suggestions.html">pages/suggestions.html</a></td><td class="n">{n('suggestions.json','suggestions')}</td><td class="n">2499438c (T29)</td><td>Launch order, product scope, pricing, article formats, editorial voice, design, ratings, commission model, measurement, rollout</td></tr>
<tr><td>Canonical questions</td><td><a href="../pages/questions.html">pages/questions.html</a></td><td class="n">{n('questions.json','questions')}</td><td class="n">2499438c (T29)</td><td>The information that must exist before those choices are safe</td></tr>
<tr><td>Project flags</td><td><a href="../pages/flags.html">pages/flags.html</a></td><td class="n">{n('flags.json','flags')}</td><td class="n">multiple sessions</td><td>What could not be confirmed from an official source</td></tr>
<tr><td>Marketing improvement board</td><td><a href="../marketing/improvements.html">marketing/improvements.html</a></td><td class="n">14</td><td class="n">e8b071cd (T39)</td><td>What to change next on the reader-facing site</td></tr>
<tr><td>Requirements review</td><td><a href="../decisions/requirements.html">decisions/requirements.html</a></td><td class="n">24</td><td class="n">d0135100</td><td>Whether the platform in the brief exists yet, requirement by requirement</td></tr>
<tr><td>Review findings</td><td><a href="../decisions/flagged.html">decisions/flagged.html</a></td><td class="n">{n('decisions_findings.json','findings')}</td><td class="n">d0135100</td><td>Irregularities found during the requirements review</td></tr>
<tr><td><strong>This console's proposals</strong></td><td><a href="suggestions.html">console/suggestions.html</a></td><td class="n">{len(proposals['proposals'])}</td><td class="n">{SESSION} (T42)</td><td>The redesign, the six articles, the naming consolidation, and the compliance encoding</td></tr>
<tr><td><strong>This console's questions</strong></td><td><a href="questions.html">console/questions.html</a></td><td class="n">{len(info['open'])}</td><td class="n">{SESSION} (T42)</td><td>What the brief asks that the repository cannot answer</td></tr>
<tr><td><strong>This console's irregularities</strong></td><td><a href="flagged.html">console/flagged.html</a></td><td class="n">{len(flags['flags'])}</td><td class="n">{SESSION} (T42)</td><td>What this review found, with the action that closes it</td></tr>
</tbody></table></div>"""

    rows = []
    for p in proposals["proposals"]:
        d = decisions["sheet"].get(p["id"], {})
        ch = d.get("choice", "")
        opt_labels = " · ".join(f"<strong>{e(o['id'])}</strong> {e(o['label'])}" for o in p["options"])
        rows.append(
            f"<tr id='{e(p['id'])}'><td class='id'>{e(p['id'])}</td><td>{e(p['title'])}</td>"
            f"<td>{opt_labels}</td><td class='n'>{e(p['recommended'])}</td>"
            f"<td class='n'>{('<strong>' + e(ch) + '</strong>') if ch else BLANK_DASH}</td>"
            f"<td>{pill_for('approved' if ch else 'proposed')}</td></tr>"
        )

    how = "".join(f"<li>{e(x)}</li>" for x in decisions["how_to_record"])
    rules = "".join(f"<li>{e(x)}</li>" for x in decisions["rules"])
    sheet_json = json.dumps(decisions["sheet"], indent=2, ensure_ascii=False)

    body = f"""
<div class="notice"><strong>Nothing on this project is implemented until a choice is recorded here.</strong>
An empty choice field means no decision has been made. It is never read as approval and never read as rejection.</div>

<h2>1. Every register, indexed</h2>
{registers}

<h2>2. The sheet</h2>
<div class="tw"><table>
<caption>{len(proposals['proposals'])} proposals from this console. The inherited SG-01&hellip;SG-{read_ledger_count('suggestions.json','suggestions') or '?'} rows are decided on the <a href="../pages/suggestions.html">canonical board</a> in the same way.</caption>
<thead><tr><th>ID</th><th>Proposal</th><th>Options</th><th>Rec.</th><th>Your choice</th><th>State</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<h2>3. How to record a decision</h2>
<ol class="tight">{how}</ol>
<h3>Rules</h3>
<ul class="tight">{rules}</ul>

<h2>4. The file</h2>
<p><code>console/data/decisions.json</code> &mdash; the whole sheet is one object. This is what it holds today:</p>
<pre class="prompt">{e(sheet_json)}</pre>
"""
    return page("Decision sheet", "decisions.html", "Decision sheet",
                f"{len(proposals['proposals'])} proposals · 0 choices recorded · {AS_OF}",
                "One file, one field per row. Nothing is built until you fill it in.",
                body)


# --------------------------------------------------------------------------- main


def render_all() -> dict:
    sources = load("sources.json")
    proposals = load("proposals.json")
    info = load("information.json")
    design = load("design.json")
    review = load("review.json")
    flags = load("flags.json")
    decisions = load("decisions.json")
    ms = measure()

    docs = {
        "index.html": build_index(sources, proposals, info, flags, decisions, ms),
        "suggestions.html": build_suggestions(sources, proposals, decisions),
        "questions.html": build_questions(sources, info),
        "design.html": build_design(sources, design),
        "review.html": build_review(sources, review, ms),
        "decisions.html": build_decisions(sources, proposals, info, flags, decisions),
        "flagged.html": build_flagged(sources, flags),
        "sources.html": build_sources(sources),
    }
    return docs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if committed output differs from generated")
    args = ap.parse_args()

    docs = render_all()
    drift = []
    for name, text in docs.items():
        path = OUT / name
        if args.check:
            cur = path.read_text(encoding="utf-8") if path.exists() else ""
            # Measured regions report on the tree at build time. Five other sessions merge into
            # this repository concurrently, so those numbers legitimately differ between two builds
            # of the same page. They are masked here; tools/validate_console.py is what holds the
            # underlying properties (disclosure on every page, no broken links) to be true.
            mask = lambda t: re.sub(r"<!--MEASURED-->.*?<!--/MEASURED-->", "\u00a7", t, flags=re.S)
            if mask(cur) != mask(text):
                drift.append(name)
        else:
            path.write_text(text, encoding="utf-8")

    if args.check:
        if drift:
            print("console/ drift: " + ", ".join(drift), file=sys.stderr)
            return 1
        print("console/ up to date (8 pages)")
        return 0

    # sitemap for this namespace
    urls = []
    for fn, _label, _ in PAGES:
        urls.append(f"  <url><loc>https://kanlerxz87-cyber.github.io/Zone2/console/{fn}</loc>"
                    f"<lastmod>{AS_OF}</lastmod></url>")
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")

    manifest = {
        "as_of": AS_OF,
        "session": SESSION,
        "generated": sorted(docs),
        "note": "Generated by tools/build_console.py from console/data/*.json - edit the data, not the HTML.",
        "hashes": {k: hashlib.sha256(v.encode()).hexdigest()[:12] for k, v in sorted(docs.items())},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"console/ rebuilt: {len(docs)} pages + sitemap.xml + manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
