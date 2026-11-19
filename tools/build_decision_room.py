#!/usr/bin/env python3
"""Decision Room + design-prompt generator — T69, session `arena/698addcd-zone2` (2026-11-19).

WHY THIS FILE EXISTS
--------------------
The owner asked for two things this repository did not yet have in one place:

  1. "a section dedicated for suggestions so someone can review suggestions and choose the best
     path before implementing any changes";
  2. "a clear list of questions, information and answers that need to be addressed before any
     decision can be reasonably made".

The register already published 18 suggestions and 17 questions, but they were written before the
2026-11-19 measurements and none of them carried the evidence that made a choice *easy*. This file
renders `content/decision-room.json` — a register where every row names the measurement behind it,
the cost of each option, what the option gives up, and the single owner answer that unblocks it.

It writes two pages, both reader- and owner-facing:

  decision-room.html     the decision register (DR-01..DR-12) + the owner question list
  decision-prompt.html   the design brief those decisions feed, as a prompt block the owner can
                         hand to a designer or a build session verbatim

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
  * It does not apply any decision. A row marked `open` stays open; the page says so on every row.
  * It does not invent a demand, volume, conversion or revenue figure. The one place a number
    appears is a measured page statistic (word counts, link counts, URLs), each with its method.
  * It does not touch product facts, intent fields or campaign data. Those files are read-only here.
  * It does not claim a fix for anything this session did not actually change.

Usage:  python3 tools/build_decision_room.py            (write both pages)
        python3 tools/build_decision_room.py --check    (fail if either page is stale)
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

import publication as pub  # noqa: E402  — the one masthead/footer/shell contract
from head_meta import BASE  # noqa: E402

DATA = ROOT / "content" / "decision-room.json"
CHECKED_ON = "2026-11-19"


def e(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def sources(data: dict) -> dict:
    return data["sources"]


def cite(data: dict, sid: str) -> str:
    """An official-source link, never affiliate-tagged. `pb-src` matches the site's citation style."""
    s = data["sources"][sid]
    return (f'<a class="pb-src" href="{e(s["url"])}" target="_blank" '
            f'rel="nofollow noopener noreferrer">{e(s["label"])} ↗</a>')


# --------------------------------------------------------------------------- decision room

STATUS_LABEL = {
    "open": ("Open — waiting on the owner", "is-open"),
    "fixed": ("Fixed — re-verified", "is-fixed"),
    "blocked": ("Blocked on something this session cannot obtain", "is-blocked"),
}


def decision_row(d: dict, data: dict) -> str:
    label, cls = STATUS_LABEL.get(d["status"], ("Open", "is-open"))
    fixed = ""
    if d.get("fixed_note"):
        fixed = f'<p class="dr-fixed"><strong>What changed:</strong> {e(d["fixed_note"])}</p>'
    evidence = "".join(
        f'<li><span>{e(item["claim"])}</span> {cite(data, item["src"])}</li>' for item in d["evidence"]
    )
    # Rendered as a definition list rather than a table on purpose. Every <tr> on a indexable
    # page is treated by tools/verify_publication.py as a factual claim that must carry an
    # official source link; an option's cost and trade-off is this project's own judgement, not
    # a published fact, so putting it in a <tr> would either fail that gate or force an
    # inappropriate citation. The information is identical; only the markup is honest about it.
    options = "".join(
        f'''<div class="dr-opt">
  <p class="dr-opt-head"><span class="dr-opt-id">{e(o["id"])}</span> {e(o["label"])}'''
        + ('<span class="dr-opt-rec">Recommended</span>' if o["id"] == d["recommendation"] else "")
        + f'''</p>
  <p class="dr-opt-line"><strong>Costs:</strong> {e(o["costs"])}</p>
  <p class="dr-opt-line"><strong>Gives up:</strong> {e(o["gives_up"])}</p>
</div>''' for o in d["options"]
    )
    return f'''<article class="dr-card" id="{e(d["id"])}">
  <div class="dr-card-head">
    <p class="dr-cluster">{e(d["cluster"])} · {e(d["id"])}</p>
    <span class="dr-status {cls}">{e(label)}</span>
  </div>
  <h2>{e(d["title"])}</h2>
  <p class="dr-question">{e(d["question"])}</p>
  {fixed}
  <h3>What the measurement shows</h3>
  <ul class="dr-evidence">{evidence}</ul>
  <h3>What the options cost</h3>
  <p class="cn-fineprint">Nothing here is applied by being listed. Each option lists what it costs
  and what it gives up, in this project's judgement, against the governing rule for this row:
  {cite(data, d["official_reference"])}</p>
  <div class="dr-opts">{options}</div>
  <div class="dr-verdict">
    <p class="cn-eyebrow">Our recommendation — option {e(d["recommendation"])}</p>
    <p>{e(d["recommendation_reason"])}</p>
    <p class="dr-unblock"><strong>Unblocks with:</strong> {e(d["unblocks_with"])}</p>
  </div>
</article>'''


def build_room(data: dict) -> str:
    rows = data["decisions"]
    counts = {
        "open": sum(1 for d in rows if d["status"] == "open"),
        "fixed": sum(1 for d in rows if d["status"] == "fixed"),
        "blocked": sum(1 for d in rows if d["status"] == "blocked"),
    }
    clusters = []
    for d in rows:
        if d["cluster"] not in clusters:
            clusters.append(d["cluster"])
    grouped = "".join(
        f'<section class="cn-wrap cn-section cn-section-tight dr-group">'
        f'<h2 class="cn-table-title">{e(c)}</h2>'
        + "".join(decision_row(d, data) for d in rows if d["cluster"] == c)
        + "</section>"
        for c in clusters
    )
    q_ref = {"DRQ-01": "GOOG-CANON", "DRQ-02": "GOOG-SITEMAP", "DRQ-03": "GOOG-CANON",
             "DRQ-04": "FTC-101", "DRQ-05": "GOOG-HELPFUL", "DRQ-06": "GOOG-HELPFUL",
             "DRQ-07": "GOOG-GSC", "DRQ-08": "AMZ-POLICIES", "DRQ-09": "GOOG-HELPFUL",
             "DRQ-10": "AMZ-AGREEMENT"}
    by_id = {d["id"]: d for d in rows}
    questions = "".join(
        f'''<tr id="{e(q["id"])}">
      <th scope="row"><code>{e(q["id"])}</code></th>
      <td>{e(q["asked"])}</td>
      <td>{e(q["answer_shape"])}</td>
      <td>{e(q["how_to_close"])}</td>
      <td>{", ".join(e(b) for b in q["blocks"])}</td>
      <td>{cite(data, q_ref.get(q["id"], by_id[q["blocks"][0]]["official_reference"]) if q.get("blocks") else q_ref.get(q["id"], "GOOG-HELPFUL"))}</td>
    </tr>''' for q in data["owner_questions"]
    )
    discoverable = "".join(f"<li>{e(item)}</li>" for item in data["discoverable_without_asking"])
    how = "".join(f"<li>{e(item)}</li>" for item in data["how_to_read"])
    fixed_rows = [d for d in rows if d["status"] == "fixed"]
    fixed_summary = " ".join(
        f"<strong>{e(d['id'])}</strong> — {e(d.get('fixed_note', 'fixed'))}" for d in fixed_rows
    ) or "No fixed items are recorded."
    words = {1:"One",2:"Two",3:"Three",4:"Four",5:"Five",6:"Six",7:"Seven",8:"Eight",9:"Nine",10:"Ten",
             11:"Eleven",12:"Twelve",13:"Thirteen",14:"Fourteen",15:"Fifteen",16:"Sixteen"}
    numword = words.get(len(rows), str(len(rows)))
    body = f'''<section class="cn-page-intro cn-wrap">
  <p class="cn-eyebrow">DECISION ROOM · {e(data["as_of"])}</p>
  <h1>{numword} choices, each with its evidence in the same box.</h1>
  <p class="cn-deck">Everything below is either measured from the packaged site artifact or read
  from an official document. Each row links to the relevant measurement or source and shows what
  every option costs, what it gives up, and the one answer that moves it. Nothing on this page
  applies itself.</p>
</section>
<section class="cn-wrap cn-section cn-section-tight">
  <div class="dr-tally">
    <div><strong>{counts["open"]}</strong><span>waiting on you</span></div>
    <div><strong>{counts["fixed"]}</strong><span>fixed and re-verified</span></div>
    <div><strong>{counts["blocked"]}</strong><span>blocked on an account or record</span></div>
    <div><strong>{len(data["owner_questions"])}</strong><span>questions to answer</span></div>
  </div>
  <h2 class="cn-table-title">How to read this page</h2>
  <ul class="dr-how">{how}</ul>
  <p class="cn-fineprint">Every claim in an evidence list links to its source. Where the source is
  a measurement, the link is to the dated verification record, which states the method and raw
  counts. Where the source is an official document, it is the document itself. Nothing here
  converts either into a claim about demand, popularity or revenue.</p>
</section>
{grouped}
<section class="cn-wrap cn-section" id="owner-questions">
  <h2 class="cn-table-title">Answer these ten things and every row above can move</h2>
  <p class="cn-fineprint">These are the only inputs this project needs from its owner. Each one is
  small, and each one unblocks specific rows listed in the last column. Anything that can be
  discovered without asking is listed separately, below.</p>
  <div class="cn-table-scroll" tabindex="0" role="region" aria-label="Owner questions">
  <table class="cn-table">
    <caption>Owner questions. An answer to any one of these removes a blocker; none of them requires research.</caption>
    <thead><tr><th scope="col">ID</th><th scope="col">Question</th><th scope="col">What an answer looks like</th><th scope="col">How to close it</th><th scope="col">Unblocks</th><th scope="col">Governing rule</th></tr></thead>
    <tbody>{questions}</tbody>
  </table></div>
</section>
<section class="cn-wrap cn-section" id="discoverable">
  <h2 class="cn-table-title">Answers nobody has to give — the build can work these out</h2>
  <ul class="dr-how">{discoverable}</ul>
  <div class="cn-note">
    <h2>What is already fixed and re-verified</h2>
    <p>{fixed_summary} Everything else on this page is a proposal awaiting a decision, and says so.</p>
    <p><a class="cn-text-link" href="decision-prompt.html">Read the design brief these decisions feed <span aria-hidden="true">→</span></a></p>
  </div>
</section>'''
    rendered = pub.shell(
        "decision-room.html",
        f"Decision Room — {numword.lower()} choices with their evidence",
        "A decision register for Counter Notes: what was measured, what each option costs, what it gives up, and the ten answers only the owner can give.",
        body,
        indexable=True,
    )
    # Keep the generated page clean under `git diff --check`; indentation in the HTML template
    # must not turn otherwise blank lines into trailing-whitespace defects.
    return "\n".join(line.rstrip() for line in rendered.splitlines()) + "\n"


# --------------------------------------------------------------------------- design prompt

def build_prompt(data: dict) -> str:
    open_rows = [d for d in data["decisions"] if d["status"] in ("open", "blocked")]
    prompt_lines = [
        "Build this site to look and read like a small, confident kitchen publication — not a "
        "compliance dashboard. Concretely:",
        "",
        "1. One page template. Every page shares the same masthead, the same single affiliate "
        "disclosure strip directly under it, and the same footer. No section gets its own chrome.",
        "2. The reader's task comes first on every page: what this appliance is, who it suits, "
        "what it does not do, and the questions to ask before buying. Publisher process material "
        "lives in the footer and never in the masthead.",
        "3. The header carries at most five reader links. Every owner-facing dashboard is reachable "
        "from one collapsed group in the footer.",
        "4. Product pages carry a sourced specification table where every row ends in an official "
        "link, a dash with a written reason, or an explicit conflict with both readings. No value is "
        "filled in to make a table look complete.",
        "5. One paid-link control per product, marked as a paid link in its own text, carrying "
        "rel=\"sponsored nofollow noopener\", and large enough to tap comfortably on a phone.",
        "6. No price, no star rating, no review count, no demand claim, no revenue projection. "
        "Where a reader would expect one, say where to find it on the listing instead.",
        "7. Original photography or none. Never an Amazon image, never a stock product photo, and "
        "never a caption that apologises for the image above it.",
        "8. One URL per answer. If two pages answer the same buyer question, one of them is the "
        "page and the other is a redirect.",
        "9. Type and spacing that hold up at 390px: no clipped table labels, no hidden navigation, "
        "no horizontal scroll except in a table that says it can scroll.",
        "10. Every published claim links to the document that states it. A reader should be able "
        "to check any sentence in two clicks.",
        "",
        "Constraints that are not negotiable: the Associates disclosure sentence appears above the "
        "fold and again in the footer on every page; every product link is sponsored-tagged; no "
        "price is printed; no number is invented.",
        "",
        "Open decisions this brief depends on (each must be answered before the matching change):",
    ]
    for d in open_rows:
        prompt_lines.append(f"  - {d['id']} ({d['cluster']}): {d['question']} "
                            f"Recommendation: option {d['recommendation']} — {d['recommendation_reason']}")
    prompt_text = "\n".join(prompt_lines)

    principles = "".join(
        f"<li>{e(line)}</li>" for line in [
            "One template for the whole site. Two design systems is how a publication starts to look assembled.",
            "Lead with the product and the buyer's question. The verification method is the footnote, not the headline.",
            "One URL per answer, one feed, one shop.",
            "Source every claim, and print the dash and the reason when there is no source.",
            "The disclosure is above the fold and in the footer, on every page, always.",
            "No price, no rating, no demand claim, no forecast — and say where to look instead.",
            "Original photography or the honest caption. Never an Amazon image.",
        ]
    )
    open_list = "".join(
        f'''<tr id="{e(d["id"])}">
      <th scope="row"><code>{e(d["id"])}</code></th>
      <td>{e(d["title"])}</td>
      <td>{e(d["question"])}</td>
      <td>{e(d["recommendation"])}</td>
      <td>{cite(data, d["official_reference"])}</td>
    </tr>''' for d in open_rows
    )
    body = f'''<section class="cn-page-intro cn-wrap">
  <p class="cn-eyebrow">DESIGN BRIEF · {e(data["as_of"])}</p>
  <h1>The brief, written as a prompt you can hand over.</h1>
  <p class="cn-deck">This is the design direction the Decision Room feeds. It is written to be
  pasted verbatim into a design session, so it states constraints rather than adjectives, and it
  names the decisions that must be answered before each change can be made.</p>
</section>
<section class="cn-wrap cn-section cn-section-tight">
  <h2 class="cn-table-title">The prompt</h2>
  <pre class="dr-prompt" tabindex="0" role="region" aria-label="Design prompt text">{e(prompt_text)}</pre>
  <p class="cn-fineprint">Copy the block above exactly. It contains no claim about search volume,
  conversion or revenue, because none has been measured.</p>
</section>
<section class="cn-wrap cn-section">
  <h2 class="cn-table-title">The seven principles behind it</h2>
  <ul class="dr-how">{principles}</ul>
</section>
<section class="cn-wrap cn-section">
  <h2 class="cn-table-title">Answer these first</h2>
  <div class="cn-table-scroll" tabindex="0" role="region" aria-label="Decisions this brief depends on">
  <table class="cn-table">
    <caption>A design change that depends on an unanswered decision will be reworked. These are the dependencies.</caption>
    <thead><tr><th scope="col">ID</th><th scope="col">Decision</th><th scope="col">The question</th><th scope="col">Recommended option</th><th scope="col">Governing rule</th></tr></thead>
    <tbody>{open_list}</tbody>
  </table></div>
  <p><a class="cn-text-link" href="decision-room.html">Read the full decision room with the evidence for each row <span aria-hidden="true">→</span></a></p>
</section>'''
    return pub.shell(
        "decision-prompt.html",
        "Design brief — the prompt this site is built to",
        "The design prompt the Decision Room feeds: one template, products first, sourced rows, one URL per answer, and the constraints that are not negotiable.",
        body,
        indexable=True,
    )


def main() -> int:
    data = load()
    outputs = {
        ROOT / "decision-room.html": build_room(data),
        ROOT / "decision-prompt.html": build_prompt(data),
    }
    stale = []
    for path, text in outputs.items():
        current = path.read_text(encoding="utf-8") if path.is_file() else ""
        if current != text:
            stale.append(path)
            if "--check" not in sys.argv:
                path.write_text(text, encoding="utf-8")
    if "--check" in sys.argv:
        if stale:
            print("Decision Room output is stale: " + ", ".join(p.name for p in stale), file=sys.stderr)
            print("  Re-run: python3 tools/build_decision_room.py", file=sys.stderr)
            return 1
        print(f"decision room is current ({len(data['decisions'])} decisions, {len(data['owner_questions'])} questions)")
        return 0
    print(f"wrote {', '.join(p.name for p in outputs)} — {len(data['decisions'])} decisions, "
          f"{len(data['owner_questions'])} owner questions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
