"""Shared front-of-house chrome: masthead, disclosure strip, footer (T63, session 75efdf57).

One module, so the reader-facing pages built by tools/build_front.py (index, suggestions,
questions, guides/*) and tools/build_shop.py (shop/**) cannot drift apart.

Rules this file enforces by construction:
  * ONE reader navigation (Home, Air fryers, Meat thermometers, Guides, Compare) and ONE
    "Behind the scenes" group that holds every dashboard - the brief's "keep every dashboard
    surface reachable from the footer and a single navigation group".
  * The Operating Agreement disclosure sentence sits in a strip directly under the masthead on
    every page and is repeated in the footer ("Keep the disclosure above the fold on every page").
  * The footer links every published namespace, so tools/audit_site.py's orphan check holds.
"""
from __future__ import annotations

import html

from link_builder import ASSOCIATES_TAG

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def e(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


READER_NAV = [
    ("index.html", "Home"),
    ("shop/air-fryers.html", "Air fryers"),
    ("shop/meat-thermometers.html", "Meat thermometers"),
    ("shop/guides/index.html", "Guides"),
    ("shop/compare.html", "Compare"),
]

BEHIND_THE_SCENES = [
    ("shop/briefing.html", "Owner briefing: summary, suggestions, questions"),
    ("flagged.html", "Flagged for review"),
    ("suggestions.html", "Suggestion board"),
    ("questions.html", "Open questions"),
    ("intent.html", "Link and intent register"),
    ("intake/index.html", "Submitted links"),
    ("board/index.html", "Decision board"),
    ("brief/index.html", "Design brief"),
    ("verification.html", "Verification log"),
    ("sources.html", "Source register"),
    ("products.html", "Operator dashboard"),
]


def masthead(depth: str, active: str) -> str:
    items = []
    for href, label in READER_NAV:
        on = ' class="is-on" aria-current="page"' if href == active else ""
        items.append(f'<a href="{e(depth + href)}"{on}>{e(label)}</a>')
    more = "".join(f'<a href="{e(depth + h)}">{e(l)}</a>' for h, l in BEHIND_THE_SCENES)
    return f"""<header class="sh-mast">
  <div class="sh-wrap sh-mast-row">
    <a class="sh-logo" href="{e(depth)}index.html">Counter <em>Notes</em><span>Kitchen gear, explained before you buy</span></a>
    <nav class="sh-nav" aria-label="Sections">{''.join(items)}<details class="sh-more"><summary>Behind the scenes</summary><div class="sh-more-panel">{more}</div></details></nav>
  </div>
</header>
<div class="pb-disc sh-disc"><div class="sh-wrap"><strong>Affiliate disclosure.</strong> {e(DISCLOSURE)} When you buy through a &ldquo;Check today&rsquo;s price&rdquo; button we may earn a commission, at no extra cost to you. Those buttons are marked <em>(paid link)</em>; links to manufacturer and government pages are not affiliate links.</div></div>"""


def footer(depth: str, checked_on: str) -> str:
    d = e(depth)
    return f"""<footer class="sh-foot">
  <div class="sh-wrap">
    <div class="sh-foot-grid">
      <div><h4>Shop</h4><ul>
        <li><a href="{d}shop/index.html">All five products</a></li>
        <li><a href="{d}shop/air-fryers.html">Air fryers</a></li>
        <li><a href="{d}shop/meat-thermometers.html">Meat thermometers</a></li>
        <li><a href="{d}shop/compare.html">Compare side by side</a></li>
      </ul></div>
      <div><h4>Guides</h4><ul>
        <li><a href="{d}shop/guides/index.html">All buying guides</a></li>
        <li><a href="{d}guides/index.html">Earlier guides</a></li>
        <li><a href="{d}marketing/buying-guide.html">Which air fryer to buy</a></li>
        <li><a href="{d}marketing/comparison.html">Air fryer head-to-head</a></li>
        <li><a href="{d}journal/index.html">Journal</a></li>
      </ul></div>
      <div><h4>Behind the scenes</h4><ul>
        <li><a href="{d}shop/briefing.html">Owner briefing</a></li>
        <li><a href="{d}flagged.html">Flagged for review</a></li>
        <li><a href="{d}suggestions.html">Suggestion board</a></li>
        <li><a href="{d}questions.html">Open questions</a></li>
        <li><a href="{d}summary.html">Executive summary</a></li>
        <li><a href="{d}guides/method.html">How we verify</a></li>
      </ul></div>
      <div><h4>Registers</h4><ul>
        <li><a href="{d}intent.html">Link and intent register</a></li>
        <li><a href="{d}intake/index.html">Submitted links</a></li>
        <li><a href="{d}board/index.html">Decision board</a></li>
        <li><a href="{d}brief/index.html">Design brief</a></li>
        <li><a href="{d}verification.html">Verification log</a></li>
        <li><a href="{d}sources.html">Source register</a></li>
      </ul></div>
    </div>
    <div class="sh-foot-detail">
      <p><strong>{e(DISCLOSURE)}</strong> Amazon and the Amazon logo are trademarks of Amazon.com, Inc.
      or its affiliates. Counter Notes is independent and not affiliated with Amazon or with any
      manufacturer named here. Product buttons are Special Links carrying the Associates tag
      <code>{e(ASSOCIATES_TAG)}</code>, marked <code>rel="sponsored nofollow"</code>.</p>
      <p>We have not tested these products in a kitchen. Everything stated about them comes from the
      manufacturer's page or the Amazon listing, linked next to each figure. Where two official pages
      disagree we print both; where none states a value we leave a dash and say why. No price, star
      rating or review count is printed on this site &mdash; those live on the listing. No traffic,
      click or revenue figure appears anywhere, because none has been measured.</p>
      <p><strong>Every dashboard, register and earlier build.</strong>
      <a href="{d}products.html">Products</a> &middot;
      <a href="{d}analysis.html">Analysis</a> &middot;
      <a href="{d}content.html">Content engine</a> &middot;
      <a href="{d}compliance.html">Compliance</a> &middot;
      <a href="{d}tracking.html">Tracking</a> &middot;
      <a href="{d}paths.html">Launch paths</a> &middot;
      <a href="{d}review-decide.html">Review board</a> &middot;
      <a href="{d}review.html">Review: findings</a> &middot;
      <a href="{d}review-questions.html">Review: questions</a> &middot;
      <a href="{d}review-ideas.html">Review: ideas</a> &middot;
      <a href="{d}review-trace.html">Requirements trace</a> &middot;
      <a href="{d}design-notes.html">Design notes</a> &middot;
      <a href="{d}playbook.html">Design &amp; content playbook</a> &middot;
      <a href="{d}pages/index.html">Findings hub</a> &middot;
      <a href="{d}pages/suggestions.html">Findings-hub suggestions</a> &middot;
      <a href="{d}pages/questions.html">Findings-hub questions</a> &middot;
      <a href="{d}pages/categories/index.html">Commission categories</a> &middot;
      <a href="{d}decisions/index.html">Decision hub</a> &middot;
      <a href="{d}release/index.html">Release readiness</a> &middot;
      <a href="{d}audit/index.html">Independent audit</a> &middot;
      <a href="{d}discovery/index.html">Discovery review</a> &middot;
      <a href="{d}console/index.html">Owner&rsquo;s Console</a> &middot;
      <a href="{d}marketing/index.html">Counter Notes archive</a> &middot;
      <a href="{d}marketing/articles/index.html">The three write-ups</a> &middot;
      <a href="{d}marketing/verification.html">Marketing verification</a> &middot;
      <a href="{d}marketing/improvements.html">Improvement board</a> &middot;
      <a href="{d}research-hub/start.html">Affiliate Research Hub</a> &middot;
      <a href="{d}zone2/index.html">Zone2 platform build</a> &middot;
      <a href="{d}affiliate-lab/index.html">Affiliate Lab</a> &middot;
      <a href="{d}revalidation/index.html">Revalidation</a> &middot;
      <a href="{d}northstar/index.html">Northstar prototype</a> &middot;
      <a href="{d}journal/dual-basket-air-fryers.html">Two baskets beat one long timer</a> &middot;
      <a href="{d}journal/basket-vs-oven.html">Choose by geometry</a> &middot;
      <a href="{d}journal/why-every-number-has-a-source.html">Why every number links to its source</a></p>
      <p>Official sources re-read {e(checked_on)}.
      <a href="https://affiliate-program.amazon.com/help/operating/policies">Associates Program Policies</a> &middot;
      <a href="https://affiliate-program.amazon.com/help/operating/agreement">Operating Agreement</a> &middot;
      <a href="https://www.ftc.gov/business-guidance/advertising-marketing/endorsements-influencers-reviews">FTC endorsement guidance</a></p>
    </div>
  </div>
</footer>"""
