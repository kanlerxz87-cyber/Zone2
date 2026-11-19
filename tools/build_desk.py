#!/usr/bin/env python3
"""Decision desk generator — T66, session `arena/6ce606cb-zone2` (2026-11-19).

WHY THIS FILE EXISTS
--------------------
The brief asked for a place to review and choose paths *before* anything is implemented, and
for a clear list of the questions that have to be answered first, each with a way to find the
answer. The T50 board (docs/board-9251f262.json) holds twelve suggestions in one long list.
The desk regroups them, together with the twelve T66 suggestions in docs/front-6ce606cb.json,
under the four goals the brief names:

  shop         make it read like a shop, not an audit
  findable     make it findable
  machinery    make the machinery trustworthy
  publication  make it read like a publication

Every suggestion shows its options, its evidence (an official source, or a statement that the
evidence is this repository), what is still unknown, and how to find it out. Nothing on the
desk is marked decided: where the brief points at an option, the desk says so as a *signal*,
with what has already shipped, and the status stays "Proposed - awaiting owner decision".

WHAT IT WRITES
--------------
  desk/index.html       the four goals, every suggestion, options / evidence / unknowns
  desk/questions.html   the questions, ranked by how many suggestions each one blocks

Inputs are read-only: docs/board-9251f262.json (another session's file), the T66 overlay, and
tools/build_front.py for the shared page chrome (masthead, disclosure strip, footer).

Usage:  python3 tools/build_desk.py           (writes the pages)
        python3 tools/build_desk.py --check   (fails if a written page is stale)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_front as bf  # noqa: E402  — shared chrome, overlay loader, number words

ROOT = bf.ROOT
STATUS = "Proposed - awaiting owner decision"


def e(x: object) -> str:
    return bf.e(x)


def desk_data() -> dict:
    """Board + overlay, merged in memory. Neither input file is written."""
    _facts, board = bf.load()
    ov = bf.extras()["overlay"]
    sources = {k: {"name": v["name"], "url": v["url"]} for k, v in board["sources"].items()}
    sources.update({k: {"name": v["name"], "url": v["url"]} for k, v in ov["sources"].items()})
    sgs = []
    for s in board["suggestions"]:
        sgs.append(dict(s, goal=ov["goal_map"].get(s["id"]), origin="T50 board (2026-11-16)"))
    for s in ov["suggestions"]:
        sgs.append(dict(s, origin="T66 (2026-11-19)"))
    qs = [dict(q, origin="T50 board") for q in board["questions"]]
    qs += [dict(q, origin="T66") for q in ov["questions"]]
    blocks_count = {q["id"]: 0 for q in qs}
    for s in sgs:
        for w in s.get("waits_on", []):
            if w in blocks_count:
                blocks_count[w] += 1
    return {"goals": ov["goals"], "suggestions": sgs, "questions": qs, "sources": sources,
            "signals": ov.get("brief_signals", {}), "blocks_count": blocks_count}


def src_link(d: dict, sid: str | None) -> str:
    if not sid or sid not in d["sources"]:
        return ("<b>Evidence</b> this repository: the observation is recorded in the summary above "
                "and in the T66 verification record, not on an external page.")
    s = d["sources"][sid]
    host = re.sub(r"^www\.", "", re.sub(r"^https?://", "", s["url"]).split("/")[0])
    rel = "sponsored nofollow noopener noreferrer" if "amazon." in s["url"] else "noopener noreferrer"
    return (f'<b>Evidence</b> <a href="{e(s["url"])}" target="_blank" rel="{rel}">'
            f'{e(s["name"])} &middot; {e(host)}</a>')


def suggestion_card(d: dict, sg: dict) -> str:
    qmap = {q["id"]: q for q in d["questions"]}
    opts = []
    for o in sg["options"]:
        rec = o["label"] == sg["recommendation"]
        opts.append(
            f'<div class="pb-opt{" pb-opt--rec" if rec else ""}"><b>Option {e(o["label"])}'
            f'{" &nbsp;(recommended)" if rec else ""}</b><p>{e(o["text"])}</p>'
            f'<div class="cost"><b>Cost</b> {e(o["cost"])}<br><b>Trade-off</b> {e(o["tradeoff"])}</div></div>')
    sig = d["signals"].get(sg["id"])
    signal = ""
    if sig:
        signal = (f'<p class="pb-signal"><b>What the brief asks for:</b> {e(sig["asks"])} That points to '
                  f'<b>Option {e(sig["matches"])}</b>. <b>Already shipped:</b> {e(sig["shipped"])} '
                  f'The choice is still recorded by the owner, not by this desk.</p>')
    unknowns = []
    for w in sg.get("waits_on", []):
        q = qmap[w]
        mark = "answered" if q["status"] == "answered" else "open"
        unknowns.append(
            f'<li><b><a href="questions.html#{e(w)}">{e(w)}</a> ({mark})</b> {e(q["question"])}<br>'
            f'<b>Unknown:</b> {e(q["what_is_missing"])}<br><b>How to find out:</b> {e(q["how_to_discover"])}</li>')
    unk = (f'<ul class="pb-unknowns">{"".join(unknowns)}</ul>' if unknowns else
           '<ul class="pb-unknowns"><li><b>Unknowns:</b> none blocking. This can be decided now.</li></ul>')
    return f"""<article class="pb-decision" id="{e(sg['id'])}">
  <div class="pb-decision-hd">
    <span class="pb-decision-id">{e(sg['id'])}</span>
    <h3>{e(sg['title'])}</h3>
    <span class="pb-pill pb-pill--warn">{e(STATUS)}</span>
  </div>
  <p><b>{e(sg['area'])}.</b> {e(sg['summary'])}</p>
  {signal}
  <div class="pb-opts">{''.join(opts)}</div>
  {unk}
  <div class="pb-decision-ft">
    <span><b>Recommended</b> Option {e(sg['recommendation'])}</span>
    <span>{src_link(d, sg.get('source'))}</span>
    <span><b>From</b> {e(sg['origin'])}</span>
  </div>
</article>"""


def build_index(d: dict) -> str:
    sgs = d["suggestions"]
    qs = d["questions"]
    open_q = [q for q in qs if q["status"] != "answered"]
    ready = [s for s in sgs if not [w for w in s.get("waits_on", [])
                                    if next(q for q in qs if q["id"] == w)["status"] != "answered"]]
    first = sorted(open_q, key=lambda q: (-d["blocks_count"][q["id"]], q["id"]))[:5]
    first_li = "".join(
        f'<li><a href="questions.html#{e(q["id"])}"><span>{e(q["id"])} &middot; blocks '
        f'{d["blocks_count"][q["id"]]}</span><b>{e(q["question"])}</b></a></li>' for q in first)

    rows, sections = [], []
    for gk, g in d["goals"].items():
        in_goal = [s for s in sgs if s["goal"] == gk]
        waiting = sum(1 for s in in_goal if s not in ready)
        for s in in_goal:
            waits = ", ".join(f'<a href="questions.html#{e(w)}">{e(w)}</a>' for w in s.get("waits_on", [])) or "&mdash;"
            rows.append(f'<tr><td class="n"><a href="#{e(s["id"])}">{e(s["id"])}</a></td><td>{e(g["title"])}</td>'
                        f'<td>{e(s["title"])}</td><td class="n">{e(s["recommendation"])}</td><td>{waits}</td>'
                        f'<td><span class="pb-pill pb-pill--warn">Proposed</span></td></tr>')
        cards = "".join(suggestion_card(d, s) for s in in_goal)
        sections.append(f"""
<section class="pb-sec pb-goal" id="goal-{e(gk)}"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">{e(g['title'])}</h2>
  <p class="pb-sub">{e(g['blurb'])}</p></div>
  <a class="pb-sec-link" href="#top">Back to the overview &uarr;</a></div>
  <div class="pb-goal-meta"><span><b data-count="goal-{e(gk)}">{len(in_goal)}</b> suggestions</span>
  <span><b>{len(in_goal) - waiting}</b> can be decided now</span>
  <span><b>{waiting}</b> wait on an open question</span></div>
  {cards}
</div></section>""")

    body = f"""
<section class="pb-lead" id="top"><div class="pb-wrap">
  <div class="pb-lead-grid">
    <div>
      <p class="pb-kicker">Decision desk</p>
      <h1 class="pb-h1">{bf.num_word(len(sgs))} ways forward, four goals. <em>You choose.</em></h1>
      <p class="pb-stand">Each suggestion below sets out its options, what each one costs and gives up, the
      evidence behind it, what is still unknown, and how to find it out. Nothing here is marked decided.
      Where the brief already points to an option, the desk says so and shows what has shipped; the choice
      is still yours to record.</p>
      <p class="pb-byline"><b data-count="suggestions">{len(sgs)}</b> suggestions &middot;
      <b data-count="ready">{len(ready)}</b> can be decided now &middot;
      <b data-count="open-questions">{len(open_q)}</b> open questions &middot; updated {e(bf.CHECKED_ON)}</p>
    </div>
    <aside class="pb-takeaways">
      <h2>Answer these first</h2>
      <ul class="pb-picks">{first_li}</ul>
      <p class="pb-fine"><a href="questions.html">All {len(qs)} questions, ranked &rarr;</a></p>
    </aside>
  </div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Overview</h2>
  <p class="pb-sub">One row per suggestion. The id jumps to its options; the question ids jump to what is unknown.</p></div></div>
  <div class="pb-table-scroll"><table class="pb-table pb-rank"><caption>Every suggestion on the desk.
  Status is Proposed for every row until the owner records a choice.</caption>
  <thead><tr><th>Id</th><th>Goal</th><th>Suggestion</th><th>Recommended</th><th>Waits on</th><th>Status</th></tr></thead>
  <tbody>{''.join(rows)}</tbody></table></div>
</div></section>
{''.join(sections)}
<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-note"><b>How a choice gets recorded.</b> Reply with the suggestion id and an option letter (for
  example &ldquo;SG-T66-03: B&rdquo;). The next session records it in the coordination log with the date and
  your words, then does the work. Until then every row keeps the status <em>{e(STATUS)}</em>.
  The original board is still at <a href="../suggestions.html">the suggestion board</a> and
  <a href="../questions.html">the questions register</a>.</div>
</div></section>
"""
    return bf.page("desk/index.html", title="Decision desk: every suggestion, by goal · Counter Notes",
                   description="Every open suggestion for Counter Notes, grouped by goal, with options, evidence, unknowns and how to find them out. Nothing is marked decided.",
                   active="desk/index.html", body=body, depth="../")


def question_card(d: dict, q: dict) -> str:
    pill = "ok" if q["status"] == "answered" else "flag"
    blocks = [s for s in d["suggestions"] if q["id"] in s.get("waits_on", [])]
    bl = ", ".join(f'<a href="index.html#{e(s["id"])}">{e(s["id"])}</a>' for s in blocks) or "nothing on the desk"
    src = ""
    if q.get("source") and q["source"] in d["sources"]:
        s = d["sources"][q["source"]]
        rel = "sponsored nofollow noopener noreferrer" if "amazon." in s["url"] else "noopener noreferrer"
        src = f'<span><b>Source</b> <a href="{e(s["url"])}" target="_blank" rel="{rel}">{e(s["name"])}</a></span>'
    return f"""<article class="pb-decision" id="{e(q['id'])}">
  <div class="pb-decision-hd">
    <span class="pb-decision-id">{e(q['id'])}</span>
    <h3>{e(q['question'])}</h3>
    <span class="pb-pill pb-pill--{pill}">{e(q['status'])}</span>
  </div>
  <p><b>What we know.</b> {e(q['what_we_know'])}</p>
  <p><b>What is missing.</b> {e(q['what_is_missing'])}</p>
  <p><b>How to find out.</b> {e(q['how_to_discover'])}</p>
  <div class="pb-decision-ft">
    <span><b>Blocks</b> {bl}</span>
    {src}
    <span><b>From</b> {e(q['origin'])}</span>
  </div>
</article>"""


def build_questions(d: dict) -> str:
    qs = d["questions"]
    open_q = sorted([q for q in qs if q["status"] != "answered"],
                    key=lambda q: (-d["blocks_count"][q["id"]], q["id"]))
    answered = [q for q in qs if q["status"] == "answered"]
    rows = "".join(
        f'<tr><td class="n">{i}</td><td><a href="#{e(q["id"])}">{e(q["id"])}</a></td><td>{e(q["question"])}</td>'
        f'<td class="n">{d["blocks_count"][q["id"]]}</td><td>{e(q["how_to_discover"])}</td></tr>'
        for i, q in enumerate(open_q, 1))
    body = f"""
<section class="pb-lead"><div class="pb-wrap">
  <p class="pb-kicker">Decision desk &middot; questions</p>
  <h1 class="pb-h1">Answer these first, <em>in this order</em>.</h1>
  <p class="pb-stand pb-measure">A choice made before its question is answered is a guess. The open questions are
  ranked by how many suggestions each one holds up. Each says what is known, what is missing, and the one action
  that would close it.</p>
  <p class="pb-byline"><b data-count="questions">{len(qs)}</b> questions &middot;
  <b data-count="open-questions">{len(open_q)}</b> open &middot; <b>{len(answered)}</b> answered &middot;
  updated {e(bf.CHECKED_ON)}</p>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-table-scroll"><table class="pb-table pb-rank"><caption>Open questions, most-blocking first.
  &ldquo;Blocks&rdquo; counts the suggestions on the desk that wait on the question.</caption>
  <thead><tr><th>#</th><th>Id</th><th>Question</th><th>Blocks</th><th>How to find out</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Open</h2></div>
  <a class="pb-sec-link" href="index.html">Back to the desk &rarr;</a></div>
  {''.join(question_card(d, q) for q in open_q)}
</div></section>

<section class="pb-sec"><div class="pb-wrap">
  <div class="pb-sec-head"><div><h2 class="pb-h2">Answered</h2>
  <p class="pb-sub">Kept here so a settled point is not argued again.</p></div></div>
  {''.join(question_card(d, q) for q in answered)}
</div></section>
"""
    return bf.page("desk/questions.html", title="Questions to answer first · Counter Notes",
                   description="The open questions behind every decision on Counter Notes, ranked by how many suggestions each one blocks, with what is known, what is missing and how to find out.",
                   active="desk/index.html", body=body, depth="../")


TARGETS = [("desk/index.html", build_index), ("desk/questions.html", build_questions)]


def main() -> int:
    check = "--check" in sys.argv
    d = desk_data()
    stale = []
    for rel, fn in TARGETS:
        out = ROOT / rel
        want = fn(d)
        if check:
            if not out.exists() or out.read_text(encoding="utf-8") != want:
                stale.append(rel)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(want, encoding="utf-8")
            print(f"  wrote {rel} ({len(want):,} bytes)")
    if check:
        if stale:
            for s in stale:
                print(f"  STALE: {s} — run `python3 tools/build_desk.py`")
            return 1
        print(f"desk pages current ({len(TARGETS)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
