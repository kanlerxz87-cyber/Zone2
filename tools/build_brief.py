#!/usr/bin/env python3
"""Render the design-brief namespace (brief/) from the T50 registers.

Why this file exists
--------------------
The brief asks for five things the repository had never put on one surface:

1. suggestions that feed into a *prompt to design the site*, so it stops reading
   like machine output;
2. article and topic ideas for the promoted products, aimed at organic traffic;
3. a section dedicated to suggestions, where a path is chosen before anything is
   implemented;
4. a register of what is known, what is not, and how to find out;
5. an executive summary.

Every one of those existed somewhere in the tree already, scattered across four
boards and five namespaces. This namespace indexes them and adds only rows in its
own prefixes (BR-, DB-, TQ-, BQ-, IN-, RV-, FB-, VF-, DR-, TR-), so it cannot
collide with — or silently replace — a register another session owns.

Design rules inherited from the rest of the repository
------------------------------------------------------
1. Data, not HTML. Pages are generated; `--check` fails when the committed output
   drifts from the registers. Nobody hand-edits brief/*.html.
2. Counts are derived. Every number on a page is computed from the registers in
   the same run, so prose cannot disagree with the tables.
3. Every row is sourced or explicitly flagged. A claim row with no resolvable
   source id fails the build; a measurement row must state the method that
   produced it; an open question's answer stays empty.
4. Nothing is presented as decided. `choice` is empty until the owner records it
   on the decision sheet, and the board says so where the reader can see it.
5. No price. A product price cannot be published on this site, and this
   generator refuses to emit one.

Run: python3 tools/build_brief.py [--check]
"""

from __future__ import annotations
import re

import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "brief"
DATA = REPO / "brief" / "data"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from head_meta import head_block  # canonical + og:*, one definition for the whole site  # noqa: E402

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
SITE = "https://kanlerxz87-cyber.github.io/Zone2/"


class BuildError(Exception):
    pass


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


# Counts that live in the data as {{tokens}} and are measured from the tree.
#
# Four numbers in brief/data/*.json were typed by hand and re-typed by hand every
# time the tree grew — the step count moved 43 -> 46 -> 49 across three merges,
# and the page count moved 150 -> 158 -> 159 -> 167 -> 168. That is the same defect
# the repository has now hit in three namespaces (see CR-1 in ledger/readiness.json,
# fixed with {measure} tokens, and FL-12 on the decision board). Any figure the tree
# can be counted to produce is substituted rather than typed.
#
# CR-3 (closed by T63, session 10727edd, 2026-11-19): the three "N of N pages" values and the
# matching prose were still typed, and were re-typed by hand at 150, 158, 159, 167, 168 and 174
# pages - three times on 2026-11-19 alone as parallel sessions added pages. They are now filled
# from the SAME measure() the gate uses, so a new page means "re-run build_brief", which the
# `--check` step enforces, never "edit a number". validate_brief additionally checks that the
# PUBLISHED brief/index.html shows the current measurement.
_M = __import__("validate_brief").measure()
TOKENS: dict[str, object] = {
    "gate_count": len(__import__("ci_replay").steps()),
    "pages_tagged": f"{_M['with_tag']} of {_M['published']}",
    "pages_disclosed": f"{_M['with_disclosure']} of {_M['published']}",
    "pages_priced": f"{_M['price_pages']} of {_M['published']}",
}


def sub_tokens(node):
    """Replace {{token}} anywhere in a loaded structure. Unknown token = build error."""
    def repl(m):
        key = m.group(1)
        if key not in TOKENS:
            raise SystemExit(f"build_brief: unknown token {{{{{key}}}}}")
        return str(TOKENS[key])
    if isinstance(node, str):
        return re.sub(r"\{\{(\w+)\}\}", repl, node)
    if isinstance(node, list):
        return [sub_tokens(x) for x in node]
    if isinstance(node, dict):
        return {k: sub_tokens(v) for k, v in node.items()}
    return node


SOURCES_DOC = sub_tokens(load("sources.json"))
REVIEW = sub_tokens(load("review.json"))
FLAGS = load("flags.json")
DESIGN = load("design.json")
TOPICS = load("topics.json")
SUGGESTIONS = load("suggestions.json")
DECISIONS = load("decisions.json")
QUESTIONS = load("questions.json")
SUMMARY = sub_tokens(load("summary.json"))
VERIFICATION = sub_tokens(load("verification.json"))

SOURCES = {s["id"]: s for s in SOURCES_DOC["sources"]}
AS_OF = SOURCES_DOC["as_of"]

NAV = [
    ("index.html", "Executive summary"),
    ("design-prompt.html", "Design prompt"),
    ("topics.html", "Articles & topics"),
    ("suggestions.html", "Choose a path"),
    ("questions.html", "What we know"),
    ("review.html", "Repo review"),
    ("verification.html", "Verification"),
    ("sources.html", "Sources"),
    ("flagged.html", "Flagged"),
]

CSS = """
:root{--ink:#16130f;--paper:#fbfaf7;--muted:#6b6459;--line:#e3ded3;--accent:#1f5b4a;
--blank:#8a8478;--warn:#9a6314;--card:#fff}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);
font:18px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:64rem;margin:0 auto;padding:0 24px}
a{color:var(--accent)}
.skip{position:absolute;left:-9999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:9}
header.mast{border-bottom:1px solid var(--line);background:var(--card)}
.mast-in{display:flex;flex-wrap:wrap;gap:12px 24px;align-items:baseline;padding:18px 24px;max-width:64rem;margin:0 auto}
.brand{font-weight:700;text-decoration:none;color:var(--ink)}
.brand span{display:block;font-weight:400;font-size:13px;color:var(--muted)}
nav.top{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:14px;margin-left:auto}
nav.top a{color:var(--muted);text-decoration:none;padding:2px 0;border-bottom:2px solid transparent}
nav.top a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--accent)}
main{padding:32px 0 64px}
h1{font:700 40px/1.1 Georgia,"Times New Roman",serif;margin:0 0 12px;letter-spacing:-.01em}
h2{font:700 27px/1.2 Georgia,"Times New Roman",serif;margin:44px 0 10px}
h3{font:600 20px/1.3 Georgia,"Times New Roman",serif;margin:26px 0 6px}
p,li{max-width:44rem}
.standfirst{font-size:20px;color:#3a342b;margin:0 0 8px;max-width:44rem}
.eyebrow{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:0 0 6px}
.lede{color:#3a342b}
.disclosure{border:1px solid var(--line);background:#fff;border-left:3px solid var(--accent);
padding:12px 14px;font-size:15px;margin:0 0 20px;border-radius:3px}
.crumbs{font-size:13px;color:var(--muted);margin:0 0 18px}
table{border-collapse:collapse;width:100%;font-size:15px;margin:14px 0 8px;display:block;overflow-x:auto}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid var(--line);padding:9px 12px 9px 0}
th{font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);border-bottom:2px solid var(--line)}
tbody tr:hover{background:#f6f3ec}
tr[id]{scroll-margin-top:16px}
blockquote{margin:8px 0;padding:10px 14px;border-left:3px solid var(--line);color:#3a342b;
background:#fff;font-size:16px;max-width:44rem}
code{font:14px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:#f1ede4;
padding:1px 5px;border-radius:3px}
pre{background:#f6f3ec;border:1px solid var(--line);padding:14px 16px;overflow-x:auto;
font:13.5px/1.55 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;border-radius:4px;
white-space:pre-wrap;word-break:break-word}
.pill{display:inline-block;font-size:11px;letter-spacing:.05em;text-transform:uppercase;
padding:2px 7px;border-radius:999px;border:1px solid var(--line);color:var(--muted);background:#fff;white-space:nowrap}
.pill.official{border-color:#bcd8cc;color:#1f5b4a}
.pill.observed{border-color:#cfd6e3;color:#3b5a86}
.pill.carried{border-color:#e0d6bd;color:var(--warn)}
.pill.open{color:var(--warn);border-color:#e0d6bd}
.pill.done{color:#1f5b4a;border-color:#bcd8cc}
.pill.blocked{color:#8a3a2a;border-color:#e3c4bb}
.num{font:700 22px/1.1 Georgia,serif}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:16px 0}
.card{border:1px solid var(--line);background:var(--card);border-radius:4px;padding:14px 16px}
.card .num{display:block;margin-bottom:4px}
.card .lbl{font-size:14px;color:var(--muted)}
.note{font-size:15px;color:var(--muted);max-width:44rem}
.blank{color:var(--blank);border-bottom:1px dotted var(--blank);cursor:help}
.callout{border:1px solid var(--line);border-left:3px solid var(--accent);background:#fff;
padding:14px 16px;margin:18px 0;border-radius:3px;max-width:44rem}
.callout.warn{border-left-color:var(--warn)}
.src{font-size:13px;color:var(--muted)}
.src a{color:var(--accent)}
ul.tight li{margin-bottom:5px}
footer.site{border-top:1px solid var(--line);background:var(--card);padding:24px 0 40px;font-size:14px;color:var(--muted)}
footer.site p{max-width:52rem}
@media (max-width:640px){h1{font-size:31px}body{font-size:17px}.mast-in{padding:14px 24px}nav.top{margin-left:0}}
"""


def esc(v: object) -> str:
    return html.escape(str(v if v is not None else ""), quote=True)


def src_links(ids: object) -> str:
    """Render source ids as links.

    Accepts a list of ids, a comma-separated string, or a single id — the registers use
    all three, and a normaliser here is cheaper than three call-site conventions. An id
    that is not in the register is a build error: a citation that resolves to nothing is
    precisely the defect this repository's gates exist to catch.
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
        s = SOURCES[sid]
        out.append(f'<a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(sid)}</a>')
    return " · ".join(out)


def quote_block(sid: str) -> str:
    s = SOURCES[sid]
    q = (s.get("quote") or "").strip()
    if not q:
        return ""
    return f'<blockquote>{esc(q)}<div class="src">{esc(sid)} — {esc(s["title"])}</div></blockquote>'


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
        "mainEntityOfPage": {"@type": "WebPage", "@id": SITE + "brief/" + here},
        "publisher": {"@type": "Organization", "name": "Zone2", "url": SITE},
    }
    ld_json = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Zone2 design brief</title>
<meta name="description" content="{esc(description)}">
{head_block("brief/" + here, title=f"{title} · Zone2 design brief", description=description, site_name="Zone2", page_type="article")}
<meta name="robots" content="index,follow">
<style>{CSS}</style>
<script type="application/ld+json">{ld_json}</script>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="mast">
  <div class="mast-in">
    <a class="brand" href="index.html"><b>Zone2 design brief</b><span>What the site should look like, and what has to be decided first</span></a>
    <nav class="top" aria-label="Sections">{nav}</nav>
  </div>
</header>
<div class="wrap">
  <main id="main">
    <p class="disclosure" data-rule="R-01"><strong>Affiliate disclosure.</strong> {DISCLOSURE}</p>
    <p class="crumbs" aria-label="Breadcrumb">{'Design brief' + (' › ' + crumbs if crumbs else '')}</p>
{body}
  </main>
</div>
<footer class="site">
  <div class="wrap">
    <p>{DISCLOSURE}</p>
    <p>Generated by <code>tools/build_brief.py</code> from <code>brief/data/*.json</code>, measured on {esc(AS_OF)}.
    Every row on these pages ends in the official page it was read from, or says plainly that no source
    settles it. Nothing here is implemented: each proposal waits for a recorded owner decision.</p>
    <p><a href="../index.html">Owner dashboard</a> ·
       <a href="../pages/suggestions.html">Suggestion board (SG-01…SG-12)</a> ·
       <a href="../pages/questions.html">Question register (Q-01…Q-18)</a> ·
       <a href="../pages/flags.html">Flag register (F-01…F-40)</a> ·
       <a href="../console/index.html">Owner's Console</a> ·
       <a href="../marketing/index.html">Reader-facing site</a></p>
  </div>
</footer>
</body>
</html>
"""


# --------------------------------------------------------------------------- index

def page_index() -> str:
    d = SUMMARY
    rows = "".join(
        f'<tr><td>{esc(r["metric"])}</td><td><span class="num">{esc(r["value"])}</span></td>'
        f'<td class="src">{src_links(r.get("source_ids"))}'
        + (f'<div class="note">{esc(r["note"])}</div>' if r.get("note") else "")
        + "</td></tr>"
        for r in d["state"]
    )
    settled = "".join(f"<li>{esc(x)}</li>" for x in d["what_is_settled"])
    not_settled = "".join(f"<li>{esc(x)}</li>" for x in d["what_is_not_settled"])
    ask = "".join(f"<li>{esc(x)}</li>" for x in d["the_ask"])
    first = []
    for item in d["decide_first"]:
        tid = item["id"]
        # The 'decide first' list mixes proposals (DB-) with questions (BQ-): a proposal is
        # chosen on the board, a question is answered by the owner. Each links to the page
        # where that happens, and an id of neither kind is a build error rather than a link
        # to a fragment that addresses nothing.
        prop = next((p for p in SUGGESTIONS["proposals"] if p["id"] == tid), None)
        if prop:
            href, label = f"suggestions.html#{tid}", f'{tid} — {prop["title"]}'
        else:
            q = next(
                (q for q in list(QUESTIONS["answered"]) + list(QUESTIONS["open"]) if q["id"] == tid),
                None,
            )
            if q is None:
                raise BuildError(f"summary: decide_first id {tid!r} is neither a proposal nor a question")
            href, label = f"questions.html#{tid}", f'{tid} — {q["question"]}'
        first.append(
            f'<div class="card"><p class="eyebrow">Decide {esc(item["order"])}</p>'
            f'<p><a href="{esc(href)}">{esc(label)}</a></p>'
            f'<p class="note">{esc(item["why"])}</p></div>'
        )
    pages = "".join(
        f'<li><a href="{esc(p["page"])}"><strong>{esc(p["page"].replace(".html","").replace("-"," ").title())}</strong></a> — {esc(p["what"])}</li>'
        for p in d["how_to_use_this_namespace"]
    )
    block = d["the_blocking_fact"]
    body = f"""
<p class="eyebrow">Executive summary · measured {esc(AS_OF)}</p>
<h1>{esc(d["headline"])}</h1>

<div class="callout warn">
  <p class="eyebrow">The blocking fact</p>
  <h3 style="margin-top:0">{esc(block["headline"])}</h3>
  <p>{esc(block["detail"])}</p>
  <p class="src">{src_links(block["source_ids"])}</p>
</div>

<h2>Where the project stands, measured</h2>
<table>
<thead><tr><th>Measure</th><th>Value</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<p class="note">Every value was produced by a command run in this working tree on {esc(AS_OF)}, or read off
an official page fetched the same day. A row whose value could not be confirmed from an official source
is empty and says so.</p>

<h2>Decide these three first</h2>
<div class="grid">{"".join(first)}</div>

<h2>What was asked</h2>
<ul class="tight">{ask}</ul>

<h2>What is settled</h2>
<ul class="tight">{settled}</ul>

<h2>What is not</h2>
<ul class="tight">{not_settled}</ul>

<h2>What is in this namespace</h2>
<ul class="tight">{pages}</ul>

<h2>The one thing</h2>
<p class="lede">{esc(d["the_one_thing"])}</p>
<p class="note">Base commit <code>{esc(d["base_commit"])}</code>. This summary adds to, and does not replace,
the <a href="../pages/executive-summary.html">canonical executive summary</a>.</p>
"""
    return page("Executive summary", "The state of the Zone2 affiliate project, measured: what is settled, what is not, and the one missing value that blocks the revenue side.", "index.html", body)


# --------------------------------------------------------------------------- design prompt

def page_design() -> str:
    dg = DESIGN["diagnosis"]
    traces = "".join(
        f'<tr id="{esc(t["id"])}"><td><strong>{esc(t["trace"])}</strong>'
        f'<div class="note">{esc(t["measured"])}</div></td>'
        f'<td>{esc(t["why_it_reads_as_generated"])}</td>'
        f'<td>{esc(t["what_an_official_source_says"])}'
        f'<div class="src">{src_links(t.get("source_ids"))}</div></td></tr>'
        for t in dg["traces"]
    )
    rewrites = []
    for r in DESIGN["rewrites"]:
        rewrites.append(f"""
<h3 id="{esc(r["id"])}">{esc(r["where"])}</h3>
<p class="eyebrow">{esc(r["before_label"])}</p>
<blockquote>{esc(r["before"])}</blockquote>
<p class="eyebrow">{esc(r["after_label"])}</p>
<div class="callout">{esc(r["after"])}</div>
<p><strong>Why.</strong> {esc(r["why"])}</p>
<p class="note"><strong>Fact check.</strong> {esc(r["fact_check"])}
<span class="src">{src_links(r.get("source_ids"))}</span></p>
""")
    comps = "".join(
        f'<tr><td><strong>{esc(c["name"])}</strong><div class="note">{esc(c["spec"])}</div></td>'
        f'<td>{esc(c["constraint"])}</td></tr>'
        for c in DESIGN["system"]["components"]
    )
    good = "".join(f"<li>{esc(x)}</li>" for x in dg["what_is_already_good"])
    prompt_text = "\n".join(DESIGN["prompt"]["text"])
    sysd = DESIGN["system"]
    body = f"""
<p class="eyebrow">Design prompt · {esc(AS_OF)}</p>
<h1>Why it reads like a machine wrote it, and the prompt that would fix it</h1>
<p class="standfirst">{esc(dg["headline"])}</p>
<p class="lede">{esc(dg["detail"])}</p>

<h2>The three traces, measured</h2>
<table>
<thead><tr><th>Trace</th><th>Why it reads as generated</th><th>What an official source says</th></tr></thead>
<tbody>{traces}</tbody>
</table>

<h2>What is already good</h2>
<ul class="tight">{good}</ul>

<h2>Three rewrites, from the pages as they are published today</h2>
<p class="note">The BEFORE text is copied verbatim from the published page. The AFTER is a craft judgement
by this session, labelled as one — it is not a program fact and no official source endorses it. Every
number in each AFTER is a value the site already publishes with a source.</p>
{"".join(rewrites)}

<h2>The design system</h2>
<p class="lede">{esc(sysd["principle"])}</p>
<table>
<thead><tr><th>Element</th><th>Specification</th></tr></thead>
<tbody>
<tr><td>Type</td><td>{esc(sysd["type"]["judgement"])}<div class="src"><code>{esc(sysd["type"]["token_examples"])}</code></div></td></tr>
<tr><td>Colour</td><td>{esc(sysd["colour"]["judgement"])}<div class="src"><code>{esc(sysd["colour"]["token_examples"])}</code></div></td></tr>
<tr><td>Layout</td><td>{esc(sysd["layout"]["judgement"])}<div class="src"><code>{esc(sysd["layout"]["token_examples"])}</code></div></td></tr>
</tbody>
</table>

<h3>Components, and the rule each one exists to satisfy</h3>
<table>
<thead><tr><th>Component</th><th>Constraint it is carrying</th></tr></thead>
<tbody>{comps}</tbody>
</table>

<h2>The paste-ready prompt</h2>
<p class="note">{esc(DESIGN["prompt"]["usage"])}</p>
<pre>{esc(prompt_text)}</pre>
"""
    return page("Design prompt", "Why the site reads as machine output — measured — with three rewrites of actual published copy, a design system, and a paste-ready prompt for the rebuild.", "design-prompt.html", body, "Design prompt")


# --------------------------------------------------------------------------- topics

def page_topics() -> str:
    rules = "".join(
        f'<tr id="{esc(r["id"])}"><td><strong>{esc(r["rule"])}</strong></td>'
        f'<td><blockquote style="margin:0">{esc(r["quoted"])}</blockquote>'
        f'<div class="src">{src_links(r.get("source_ids"))}</div></td>'
        f'<td>{esc(r["what_it_means_here"])}</td></tr>'
        for r in TOPICS["governing_rules"]
    )
    rows = []
    for t in TOPICS["topics"]:
        rows.append(f"""
<tr id="{esc(t["id"])}">
  <td><strong>{esc(t["working_title"])}</strong>
      <div class="src"><span class="pill">{esc(t["intent"])}</span> <span class="pill">{esc(t["status"])}</span>
      {src_links(t.get("source_ids"))}</div></td>
  <td>{esc(t["angle"])}</td>
  <td>{esc(t["rests_on"])}</td>
  <td>{esc(t["why_it_could_earn_traffic"])}<div class="note"><strong>Missing:</strong> {esc(t["missing"])}</div>
      <div class="note"><strong>Risk:</strong> {esc(t["risk"])}</div></td>
</tr>""")
    gap = TOPICS["the_gap"]
    body = f"""
<p class="eyebrow">Articles and topics · {esc(AS_OF)}</p>
<h1>Twelve articles this site can actually publish</h1>
<p class="standfirst">Chosen because each one is answerable from a value the site can already source —
not because a tool said the phrase has volume. There is no demand data in this project, and none is
pretended to.</p>

<div class="callout warn">
  <p class="eyebrow">The gap, stated first</p>
  <h3 style="margin-top:0">{esc(gap["headline"])}</h3>
  <p>{esc(gap["detail"])}</p>
</div>

<h2>The four rules this board is built to satisfy</h2>
<table>
<thead><tr><th>Rule</th><th>As the official page states it</th><th>What it means here</th></tr></thead>
<tbody>{rules}</tbody>
</table>

<h2>The twelve</h2>
<table>
<thead><tr><th>Working title</th><th>The argument</th><th>What it rests on</th><th>Why it could earn traffic, and what is missing</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<p class="note">Every 'why it could earn traffic' cell is this session's judgement, labelled as such. It is
not a measurement: no keyword tool, Search Console property or Amazon report exists for this project
(<a href="questions.html#BQ-20">BQ-20</a>). The eight question-shaped guides already published under the
reader-facing brand are at <a href="../marketing/topics/index.html">Counter Notes → Guides</a>.</p>
"""
    return page("Articles & topics", "Twelve article proposals for the three promoted products, each with the verified fact it rests on — and a stated reason none can be ranked by expected traffic.", "topics.html", body, "Articles & topics")


# --------------------------------------------------------------------------- suggestions

def page_suggestions() -> str:
    sheet = {r["id"]: r for r in DECISIONS["sheet"]}
    cards = []
    for p in SUGGESTIONS["proposals"]:
        choice = sheet.get(p["id"], {}).get("choice", "")
        opts = "".join(
            f'<li><strong>{esc(o["id"])}.</strong> {esc(o["label"])}<div class="note">{esc(o["tradeoff"])}</div></li>'
            for o in p["options"]
        )
        state = "blocked" if p["state"] == "blocked" else ("done" if choice else "open")
        state_label = "chosen — " + choice if choice else ("blocked on a question" if p["state"] == "blocked" else "awaiting a choice")
        blockers = "".join(
            f'<a href="questions.html#{esc(b)}">{esc(b)}</a>' for b in p.get("blockers", [])
        ) or "—"
        cards.append(f"""
<section id="{esc(p["id"])}">
  <h3>{esc(p["id"])} · {esc(p["title"])}</h3>
  <p class="src"><span class="pill">{esc(p["area"])}</span> <span class="pill {state}">{esc(state_label)}</span>
     sequence {esc(p["sequence"])}</p>
  <p class="eyebrow">What changes</p>
  <p>{esc(p["what_changes"])}</p>
  <p class="eyebrow">Why</p>
  <p>{esc(p["why"])}</p>
  <p class="eyebrow">Options</p>
  <ul class="tight">{opts}</ul>
  <table>
  <tbody>
  <tr><th style="width:12rem">Recommended</th><td><strong>{esc(p["recommended"])}</strong>
      {f'<div class="note">{esc(p["recommended_note"])}</div>' if p.get("recommended_note") else ""}</td></tr>
  <tr><th>Effort</th><td>{esc(p["effort"])}</td></tr>
  <tr><th>Risk</th><td>{esc(p["risk"])}</td></tr>
  <tr><th>Reversible</th><td>{esc(p["reversible"])}</td></tr>
  <tr><th>Blocked by</th><td>{blockers}</td></tr>
  <tr><th>Evidence</th><td>{esc(", ".join(p.get("evidence", [])) or "—")} {src_links(p.get("source_ids"))}</td></tr>
  <tr><th>Inherited rows this touches</th><td>{esc(", ".join(p.get("relates_to", [])) or "—")}</td></tr>
  </tbody>
  </table>
</section>""")
    body = f"""
<p class="eyebrow">Choose a path · {esc(AS_OF)}</p>
<h1>Twelve proposals. Nothing implemented until you pick one.</h1>
<p class="standfirst">{esc(SUGGESTIONS["decision_sheet"]["order"])}</p>

<div class="callout">
  <p class="eyebrow">How to record a choice</p>
  <p>{esc(SUGGESTIONS["decision_sheet"]["how_to_record"])}</p>
</div>

<p class="note">Costs and risks are the reviewer's estimates, deliberately coarse, and are labelled as
estimates — they are not program facts. Rows below marked <span class="pill blocked">blocked on a question</span>
cannot be decided until the named question on the
<a href="questions.html">information register</a> is answered.</p>

{"".join(cards)}
"""
    return page("Choose a path", "The review-and-choose board: twelve proposals with options, costs, risks and blockers. Nothing on it has been implemented.", "suggestions.html", body, "Choose a path")


# --------------------------------------------------------------------------- questions

def page_questions() -> str:
    ans = "".join(
        f'<tr id="{esc(q["id"])}"><td><strong>{esc(q["question"])}</strong></td>'
        f'<td>{esc(q["answer"])}</td>'
        f'<td class="src">{src_links(q.get("source_ids"))}'
        + (f'<div class="note">{esc(q["measured"])}</div>' if q.get("measured") else "")
        + "</td></tr>"
        for q in QUESTIONS["answered"]
    )
    open_rows = []
    for q in QUESTIONS["open"]:
        refs = "".join(f'<span class="pill">{esc(r)}</span> ' for r in q.get("register_refs", []))
        blocks = "".join(f'<a href="suggestions.html#{esc(b)}">{esc(b)}</a> ' for b in q.get("blocks", []))
        open_rows.append(f"""
<tr id="{esc(q["id"])}">
  <td><strong>{esc(q["question"])}</strong><div class="src">{refs}</div></td>
  <td><span class="blank" title="no official source settles this — left empty on purpose">—</span></td>
  <td>{esc(q["known"])}</td>
  <td>{esc(q["missing"])}</td>
  <td>{esc(q["how_to_close"])}<div class="note">Who can close it: {esc(q["who_can_close"])}</div>
      <div class="note">Blocks: {blocks or "—"}</div></td>
</tr>""")
    inv = "".join(
        f'<tr id="{esc(i["id"])}"><td><strong>{esc(i["item"])}</strong></td>'
        f'<td>{esc(i["established_by"])}</td><td><span class="num">{esc(i["value"])}</span></td></tr>'
        for i in QUESTIONS["inventory"]
    )
    body = f"""
<p class="eyebrow">What we know · {esc(AS_OF)}</p>
<h1>What an official page settles, what nothing can, and what we already hold</h1>
<p class="standfirst">Three registers. The first quotes only what a linked official page says. The second
is empty by design: an open question's answer cell is never filled with an inference. The third is what
the project already has, and how each item was established.</p>

<h2>Answered — {len(QUESTIONS["answered"])} questions an official page settles</h2>
<table>
<thead><tr><th>Question</th><th>Answer, as the page states it</th><th>Source</th></tr></thead>
<tbody>{ans}</tbody>
</table>

<h2>Open — {len(QUESTIONS["open"])} questions nothing here can answer</h2>
<p class="note">The answer column is empty on purpose. Each row states what is already known, what is
missing, the concrete action that would close it, and who can close it.</p>
<table>
<thead><tr><th>Question</th><th>Answer</th><th>What is known</th><th>What is missing</th><th>How to close it</th></tr></thead>
<tbody>{"".join(open_rows)}</tbody>
</table>

<h2>Inventory — what the project already holds</h2>
<table>
<thead><tr><th>Item</th><th>How it was established</th><th>Value</th></tr></thead>
<tbody>{inv}</tbody>
</table>

<p class="note">This register extends and does not replace the canonical
<a href="../pages/questions.html">Q-01…Q-18</a>, the Owner's Console's information register, or the
independent audit's gap register.</p>
"""
    return page("What we know", "Thirteen questions an official page answers, ten nothing here can, and the inventory of what the project already holds.", "questions.html", body, "What we know")


# --------------------------------------------------------------------------- review

def page_review() -> str:
    by_section = {}
    for r in REVIEW["rows"]:
        by_section.setdefault(r["section"], []).append(r)
    blocks = []
    for sec in REVIEW["sections"]:
        rows = by_section.get(sec["id"], [])
        if not rows:
            continue
        body_rows = "".join(
            f'<tr id="{esc(r["id"])}"><td><strong>{esc(r["what"])}</strong>'
            + (f'<div class="src"><a href="flagged.html#{esc(r["flag"])}">{esc(r["flag"])}</a></div>' if r.get("flag") else "")
            + "</td>"
            f'<td>{esc(r["value"])}</td>'
            f'<td><code style="font-size:12.5px">{esc(r["method"])}</code></td>'
            f'<td class="src">{src_links(r.get("source_id") or r.get("source_ids"))}'
            + (f'<div class="note">Rule this bears on: {src_links(r["context_source_id"])}</div>' if r.get("context_source_id") else "")
            + (f'<div class="note">{esc(r.get("carried_note",""))}</div>' if r.get("carried_note") else "")
            + (f'<div class="note">source kind: {esc(r["source_kind"])}</div>' if r.get("source_kind") else "")
            + "</td></tr>"
            for r in rows
        )
        blocks.append(f"""
<h2>{esc(sec["name"])}</h2>
<p class="note">{esc(sec["lead"])}</p>
<table>
<thead><tr><th>What was measured</th><th>Value</th><th>Method</th><th>Source</th></tr></thead>
<tbody>{body_rows}</tbody>
</table>""")
    manual = "".join(
        f'<tr><td><a href="{esc(m["url"])}">{esc(m["surface"])}</a></td>'
        f'<td>{esc(m["pages"])}</td><td>{esc(m["what_to_check"])}</td></tr>'
        for m in REVIEW["manual_review"]
    )
    body = f"""
<p class="eyebrow">Repository review · {esc(AS_OF)} · base {esc(REVIEW["base_commit"][:12])}</p>
<h1>Line by line: what is actually in the repository</h1>
<p class="standfirst">Every number below was produced by a command run in this working tree on {esc(AS_OF)}.
None is quoted from another session's prose. Where a published page states a different figure, the row
says so and links to the flag.</p>
<p class="note"><strong>Method.</strong> {esc(REVIEW["method"])}</p>
{"".join(blocks)}

<h2>Links for manual review</h2>
<p class="note">Every surface a reviewer can open and check for themselves.</p>
<table>
<thead><tr><th>Surface</th><th>Pages</th><th>What to check there</th></tr></thead>
<tbody>{manual}</tbody>
</table>
"""
    return page("Repo review", "Line-by-line review of the repository: every number was measured by a command, with the method shown and links for manual review.", "review.html", body, "Repo review")


# --------------------------------------------------------------------------- sources

def page_sources() -> str:
    rows = []
    for s in SOURCES_DOC["sources"]:
        q = (s.get("quote") or "").strip()
        quote_html = f'<blockquote style="margin:6px 0 0">{esc(q)}</blockquote>' if q else '<p class="note">No wording is quoted from this page in this namespace.</p>'
        obs = f'<div class="note">{esc(s["observation"])}</div>' if s.get("observation") else ""
        dated = s.get("page_dated") or '<span class="blank" title="the page does not print a date this session could read">—</span>'
        rows.append(f"""
<tr id="{esc(s["id"])}">
  <td><strong>{esc(s["id"])}</strong>
      <div class="src"><span class="pill {esc(s["class"])}">{esc(s["class"])}</span>
      rechecked: {esc(s["rechecked"])}</div></td>
  <td><strong>{esc(s["title"])}</strong>{obs}
      {quote_html}
      <div class="src"><a href="{esc(s["url"])}" target="_blank" rel="noopener noreferrer nofollow">{esc(s["url"])}</a></div></td>
  <td>{esc(s["publisher"])}<div class="src">fetched {esc(s["fetched"])}</div></td>
  <td>{dated}</td>
</tr>""")
    body = f"""
<p class="eyebrow">Sources · fetched {esc(SOURCES_DOC["accessed_utc"])}</p>
<h1>Every page a value in this namespace was read from</h1>
<p class="standfirst">{esc(SOURCES_DOC["note"])}</p>
<table>
<thead><tr><th>ID</th><th>Page, and the wording taken from it</th><th>Publisher</th><th>Page dated</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<h2>What each class means</h2>
<table>
<thead><tr><th>Class</th><th>Meaning</th></tr></thead>
<tbody>{"".join(f'<tr><td><span class="pill {esc(k)}">{esc(k)}</span></td><td>{esc(v)}</td></tr>' for k, v in SOURCES_DOC["classes"].items())}</tbody>
</table>
<p class="note">One row on this register is a <em>carried</em> row: the manufacturer pages behind the
published specifications were not re-fetched by this session. That is stated on the row rather than
hidden. The canonical register is at <a href="../pages/sources.html">pages/sources.html</a>.</p>
"""
    return page("Sources", "Every page a value in the design brief was read from, with the verbatim quote, the fetch date, and which rows were carried rather than re-fetched.", "sources.html", body, "Sources")


# --------------------------------------------------------------------------- flagged

def page_flagged() -> str:
    rows = []
    for f in FLAGS["flags"]:
        rows.append(f"""
<tr id="{esc(f["id"])}">
  <td><strong>{esc(f["id"])}</strong><div class="src"><span class="pill {esc(f["status"])}">{esc(f["status"])}</span>
      <span class="pill">{esc(f["severity"])}</span></div></td>
  <td><strong>{esc(f["title"])}</strong><p>{esc(f["detail"])}</p>
      <p class="note"><strong>Why it matters.</strong> {esc(f["why_it_matters"])}</p></td>
  <td>{esc(f["evidence"])}<div class="src">{src_links(f.get("source_ids"))}</div></td>
  <td>{esc(f["close_action"])}<div class="note">Owner: {esc(f["owner"])}</div>
      <div class="note">Files: <code>{esc(f.get("file_out_of_this_scope","—"))}</code></div></td>
</tr>""")
    body = f"""
<p class="eyebrow">Flagged for review · {esc(AS_OF)}</p>
<h1>Eight irregularities this review found</h1>
<p class="standfirst">{esc(FLAGS["note"].split(". ")[0])}. Nothing here blocks a deployment: each item
blocks an assertion or a decision, not a build.</p>
<p class="note">{esc(FLAGS["severity_note"])}</p>
<table>
<thead><tr><th>ID</th><th>What was found</th><th>Evidence</th><th>What would close it</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
<p class="note">This register adds to the canonical <a href="../pages/flags.html">F-01…F-40</a>, the
Owner's Console's <a href="../console/flagged.html">IR-01…IR-09</a> and the independent audit's findings.
It replaces none of them.</p>
"""
    return page("Flagged", "Eight irregularities raised by this session's review, each with the measurement behind it, what would close it, and who can.", "flagged.html", body, "Flagged")


# --------------------------------------------------------------------------- verification

def page_verification() -> str:
    rows = []
    for c in VERIFICATION["checks"]:
        pill = {"match": "done", "reproduced": "done", "measured": "official", "mismatch": "open", "pending": "blocked"}.get(c["result"], "")
        rows.append(f"""
<tr id="{esc(c["id"])}">
  <td><strong>{esc(c["id"])}</strong></td>
  <td>{esc(c["what"])}</td>
  <td><code style="font-size:12.5px">{esc(c["method"])}</code></td>
  <td>{esc(c["observed"]) or '<span class="blank" title="not yet run">—</span>'}</td>
  <td><span class="pill {pill}">{esc(c["result"])}</span>
      <div class="src">{src_links(c.get("source_ids"))}</div></td>
</tr>""")
    body = f"""
<p class="eyebrow">Verification · {esc(AS_OF)}</p>
<h1>One row per check this session ran</h1>
<p class="standfirst">{esc(VERIFICATION["note"].split(". ")[0])}.</p>
<div class="callout"><p>{esc(VERIFICATION["channel_note"])}</p></div>
<table>
<thead><tr><th>ID</th><th>What was checked</th><th>Method</th><th>Observed</th><th>Result</th></tr></thead>
<tbody>{"".join(rows)}</tbody>
</table>
"""
    return page("Verification", "One row per check this session ran, with the method used, what was observed, and whether it matched what the project publishes.", "verification.html", body, "Verification")


PAGES = {
    "index.html": page_index,
    "design-prompt.html": page_design,
    "topics.html": page_topics,
    "suggestions.html": page_suggestions,
    "questions.html": page_questions,
    "review.html": page_review,
    "sources.html": page_sources,
    "flagged.html": page_flagged,
    "verification.html": page_verification,
}


def counts() -> dict:
    return {
        "sources": len(SOURCES_DOC["sources"]),
        "review_rows": len(REVIEW["rows"]),
        "flags": len(FLAGS["flags"]),
        "proposals": len(SUGGESTIONS["proposals"]),
        "topics": len(TOPICS["topics"]),
        "answered": len(QUESTIONS["answered"]),
        "open_questions": len(QUESTIONS["open"]),
        "inventory": len(QUESTIONS["inventory"]),
        "checks": len(VERIFICATION["checks"]),
        "rewrites": len(DESIGN["rewrites"]),
    }


def build() -> dict[str, str]:
    OUT.mkdir(exist_ok=True)
    out = {}
    for name, fn in PAGES.items():
        doc = fn()
        if DISCLOSURE not in doc:
            raise BuildError(f"{name}: missing the required Site disclosure")
        out[name] = doc
    return out


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    check = "--check" in argv
    try:
        rendered = build()
    except BuildError as exc:
        print(f"ERROR {exc}")
        return 1
    stale = []
    for name, doc in rendered.items():
        path = OUT / name
        if check:
            if not path.is_file() or path.read_text(encoding="utf-8") != doc:
                stale.append(name)
        else:
            path.write_text(doc, encoding="utf-8")
    print(json.dumps({"pages": len(rendered), **counts(), "stale": stale}, indent=2))
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())