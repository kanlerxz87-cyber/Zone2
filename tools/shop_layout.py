"""Shared front-of-house chrome: masthead, disclosure strip, footer (T66, session 75efdf57).

One module, so the reader pages built by tools/build_front.py (index, summary, suggestions,
questions, guides/*) and by tools/build_shop.py (shop/**) cannot drift apart.

Markup contract (merged 2026-11-19 with session cf98ff65's G9 gate in tools/verify_front.py):
  * <nav class="pb-nav" aria-label="Primary navigation"> holds the READER links first, then ONE
    <details class="pb-nav-tools"> group labelled "Project & tools" with every owner dashboard -
    the brief's "keep every dashboard surface reachable from the footer and a single navigation
    group".
  * The Operating Agreement disclosure sentence sits in a strip directly under the masthead on
    every page and is repeated in the footer.
  * <footer class="pb-foot"> links every published namespace, so tools/audit_site.py's orphan
    check and G9's footer check both hold.
  * Wording about the Associates tag follows cf98ff65's correction: the tag was supplied by the
    owner; its account status has not been confirmed (briefing OQ-02).
"""
from __future__ import annotations

import html

from link_builder import ASSOCIATES_TAG

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def e(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


#: Reader navigation, shop first. tools/verify_front.py (G9) pins this exact list.
READER_NAV = [
    ("index.html", "Counter Notes"),
    ("shop/index.html", "Shop"),
    ("shop/air-fryers.html", "Air fryers"),
    ("shop/meat-thermometers.html", "Meat thermometers"),
    ("shop/guides/index.html", "Guides"),
    ("shop/compare.html", "Compare"),
]

#: The one owner-facing group. G9 requires the first fourteen; the last two are T66 additions.
TOOLS = [
    ("suggestions.html", "Suggestions"),
    ("questions.html", "Open questions"),
    ("brief/index.html", "Design brief"),
    ("intake/index.html", "Submitted links"),
    ("board/index.html", "Decision board"),
    ("products.html", "Products dashboard"),
    ("analysis.html", "Analysis"),
    ("content.html", "Content engine"),
    ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking"),
    ("verification.html", "Verification log"),
    ("sources.html", "Source register"),
    ("flagged.html", "Flagged for review"),
    ("summary.html", "Executive summary"),
    ("shop/briefing.html", "Owner briefing"),
    ("intent.html", "Link & intent register"),
]


def _links(depth: str, items: list[tuple[str, str]], active: str) -> str:
    out = []
    for href, label in items:
        cur = ' class="is-on" aria-current="page"' if href == active else ""
        out.append(f'<a href="{e(depth + href)}"{cur}>{e(label)}</a>')
    return "".join(out)


def masthead(depth: str, active: str, checked_on: str) -> str:
    tools_cur = ' aria-current="page"' if active in {h for h, _ in TOOLS} else ""
    return f"""<header class="pb-mast">
  <div class="pb-wrap">
    <div class="pb-mast-top">
      <a class="pb-brand" href="{e(depth)}index.html">
        <div class="pb-word">Counter <em>Notes</em></div>
        <div class="pb-tag">Kitchen gear, explained before you buy</div>
      </a>
      <div class="pb-mast-meta">Sources re-read {e(checked_on)}</div>
    </div>
    <nav class="pb-nav" aria-label="Primary navigation">{_links(depth, READER_NAV, active)}<details class="pb-nav-tools"><summary{tools_cur}>Project &amp; tools</summary><div class="pb-nav-menu">{_links(depth, TOOLS, active)}</div></details></nav>
  </div>
</header>
<div class="pb-disc"><div class="pb-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} When you buy through a &ldquo;Check today&rsquo;s price&rdquo; button we may earn a commission, at no extra cost to you. Those buttons are marked <em>(paid link)</em> and carry the Associates tag supplied for this project (<code>{e(ASSOCIATES_TAG)}</code>); its account status has not been confirmed. Links to manufacturer and government pages are not affiliate links.</div></div>"""


def footer(depth: str, checked_on: str) -> str:
    d = e(depth)
    return f"""<footer class="pb-foot">
  <div class="pb-wrap">
    <div class="pb-foot-grid">
      <div><h4>Shop</h4><ul>
        <li><a href="{d}shop/index.html">All five products</a></li>
        <li><a href="{d}shop/air-fryers.html">Air fryers</a></li>
        <li><a href="{d}shop/meat-thermometers.html">Meat thermometers</a></li>
        <li><a href="{d}shop/compare.html">Compare side by side</a></li>
        <li><a href="{d}shop/guides/index.html">Buying guides</a></li>
      </ul></div>
      <div><h4>Read</h4><ul>
        <li><a href="{d}index.html">Front page</a></li>
        <li><a href="{d}guides/index.html">Guide archive</a></li>
        <li><a href="{d}marketing/buying-guide.html">Which air fryer to buy</a></li>
        <li><a href="{d}marketing/comparison.html">Air fryer head-to-head</a></li>
        <li><a href="{d}marketing/articles/index.html">The three write-ups</a></li>
        <li><a href="{d}journal/index.html">Journal</a></li>
        <li><a href="{d}marketing/index.html">All articles</a></li>
      </ul></div>
      <div><h4>Decide</h4><ul>
        <li><a href="{d}shop/briefing.html">Owner briefing</a></li>
        <li><a href="{d}suggestions.html">Suggestion board</a></li>
        <li><a href="{d}questions.html">Open questions</a></li>
        <li><a href="{d}intent.html">Link &amp; intent register</a></li>
        <li><a href="{d}paths.html">Launch paths</a></li>
        <li><a href="{d}brief/index.html">Design brief</a></li>
        <li><a href="{d}intake/index.html">Submitted-link register</a></li>
        <li><a href="{d}board/index.html">Decision board</a></li>
        <li><a href="{d}flagged.html">Flagged for review</a></li>
      </ul></div>
      <div><h4>Evidence &amp; platform</h4><ul>
        <li><a href="{d}summary.html">Executive summary</a></li>
        <li><a href="{d}verification.html">Verification log</a></li>
        <li><a href="{d}sources.html">Source register</a></li>
        <li><a href="{d}guides/method.html">How we verify</a></li>
        <li><a href="{d}marketing/verification.html">Marketing verification</a></li>
        <li><a href="{d}products.html">Products</a></li>
        <li><a href="{d}analysis.html">Analysis</a></li>
        <li><a href="{d}content.html">Content engine</a></li>
        <li><a href="{d}compliance.html">Compliance</a></li>
        <li><a href="{d}tracking.html">Tracking</a></li>
        <li><a href="{d}pages/index.html">Findings hub</a></li>
      </ul></div>
    </div>
    <div class="pb-foot-detail">
      <p><strong>{e(DISCLOSURE)}</strong> Amazon and the Amazon mark are trademarks of Amazon.com, Inc.
      or its affiliates. Counter Notes is independent and not affiliated with Amazon or with any
      manufacturer named here. Product buttons are Special Links carrying the supplied Associates tag
      <code>{e(ASSOCIATES_TAG)}</code>, marked <code>rel="sponsored nofollow"</code> and
      <em>(paid link)</em>; whether that tag's account is active has not been confirmed.</p>
      <p>We have not tested these products in a kitchen. Everything stated about them comes from the
      manufacturer&rsquo;s page or the Amazon listing, linked next to each figure. Where two official pages
      disagree we print both; where none states a value we leave a dash and say why. No price, star
      rating or review count is printed on this site &mdash; the Associates Program Policies restrict
      price display to content Amazon itself serves. Traffic, conversion and revenue figures appear
      nowhere, because none has been imported from a first-party report. The on-site click counter
      records aggregate page and link events only &mdash; no cookie, no visitor identifier.</p>
      <p><strong>Decision surfaces.</strong>
      <a href="{d}review-decide.html">Review board</a> &middot;
      <a href="{d}review.html">Review: findings</a> &middot;
      <a href="{d}review-questions.html">Review: questions</a> &middot;
      <a href="{d}review-ideas.html">Review: ideas</a> &middot;
      <a href="{d}review-trace.html">Requirements trace</a> &middot;
      <a href="{d}pages/suggestions.html">Findings-hub suggestions</a> &middot;
      <a href="{d}pages/questions.html">Findings-hub questions</a> &middot;
      <a href="{d}design-notes.html">Design notes</a> &middot;
      <a href="{d}playbook.html">Design &amp; content playbook</a></p>
      <p><strong>Operator surfaces and earlier builds.</strong>
      <a href="{d}pages/categories/index.html">Commission categories</a> &middot;
      <a href="{d}decisions/index.html">Decision hub</a> &middot;
      <a href="{d}release/index.html">Release readiness</a> &middot;
      <a href="{d}audit/index.html">Independent audit</a> &middot;
      <a href="{d}discovery/index.html">Discovery review</a> &middot;
      <a href="{d}console/index.html">Owner&rsquo;s Console</a> &middot;
      <a href="{d}marketing/improvements.html">Improvement board</a> &middot;
      <a href="{d}research-hub/start.html">Affiliate Research Hub</a> &middot;
      <a href="{d}zone2/index.html">Zone2 platform build</a> &middot;
      <a href="{d}affiliate-lab/index.html">Affiliate Lab</a> &middot;
      <a href="{d}revalidation/index.html">Revalidation</a> &middot;
      <a href="{d}northstar/index.html">Northstar prototype</a></p>
      <p><a href="{d}journal/dual-basket-air-fryers.html">Two baskets beat one long timer</a> &middot;
      <a href="{d}journal/basket-vs-oven.html">Choose by geometry</a> &middot;
      <a href="{d}journal/why-every-number-has-a-source.html">Why every number links to its source</a> &middot;
      <a href="{d}marketing/feed.xml">RSS feed</a></p>
      <p>Official sources re-read {e(checked_on)}.
      <a href="https://affiliate-program.amazon.com/">Amazon Associates</a> &middot;
      <a href="https://affiliate-program.amazon.com/help/operating/policies">Program Policies</a> &middot;
      <a href="https://affiliate-program.amazon.com/help/operating/agreement">Operating Agreement</a> &middot;
      <a href="https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews">FTC endorsement guidance</a> &middot;
      <a href="{d}sources.html">full source register</a></p>
    </div>
  </div>
</footer>"""
