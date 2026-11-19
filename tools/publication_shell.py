"""One reader masthead, disclosure and footer. Also used by the deploy projection.

The projection preserves historical page bodies and URLs; it does not re-verify or
rewrite their data. Workroom/archival surfaces remain reachable but are noindex.
"""
from __future__ import annotations

import html
import re
from pathlib import PurePosixPath

DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."

OPERATOR_LINKS = [
    ("workroom.html", "Workroom overview"), ("suggestions.html", "Suggestions & decisions"),
    ("questions.html", "Questions & missing information"), ("intent.html", "Link & intent register"),
    ("flagged.html", "Flagged for Review"), ("summary.html", "Executive summary archive"),
    ("products.html", "Product dashboard"), ("analysis.html", "Analysis"),
    ("content.html", "Content engine"), ("compliance.html", "Compliance"),
    ("tracking.html", "Tracking dashboard"), ("sources.html", "Source register"),
    ("verification.html", "Verification history"), ("paths.html", "Launch paths"),
    ("playbook.html", "Editorial playbook"), ("design-notes.html", "Design notes"),
    ("review-decide.html", "Review decisions"), ("review.html", "Review findings"),
    ("review-questions.html", "Review questions"), ("review-ideas.html", "Review ideas"),
    ("review-trace.html", "Review requirements"), ("review-2026-11-15.html", "Dated review"),
    ("pages/index.html", "Findings hub"), ("decisions/index.html", "Decision hub"),
    ("release/index.html", "Release readiness"), ("audit/index.html", "Independent audit"),
    ("discovery/index.html", "Discovery review"), ("discovery/measurement.html", "Five-event measurement contract"),
    ("console/index.html", "Owner’s Console"), ("brief/index.html", "Design brief archive"),
    ("intake/index.html", "Submitted-link intake"), ("board/index.html", "Decision board archive"),
    ("marketing/improvements.html", "Editorial improvement archive"),
    ("research-hub/start.html", "Research Hub archive"), ("zone2/index.html", "Platform prototype"),
    ("affiliate-lab/index.html", "Affiliate Lab archive"), ("revalidation/index.html", "Revalidation archive"),
    ("northstar/index.html", "Northstar prototype"), ("journal/index.html", "Journal archive"),
    ("marketing/index.html", "Earlier front page"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def depth_for(rel):
    return "../" * (len(PurePosixPath(rel).parts) - 1)


def masthead(rel="index.html"):
    root = depth_for(rel)
    nav = [
        ("index.html#the-edit", "Shop the edit"),
        ("guides/basket-air-fryers.html", "Air fryers"),
        ("guides/thermometers.html", "Thermometers"),
        ("guides/index.html", "Buying guides"),
        ("about.html", "Our approach"),
    ]
    links = ""
    for href, label in nav:
        current = ' aria-current="page"' if rel == href else ""
        links += f'<a href="{root}{href}"{current}>{label}</a>'
    return f'''<header class="cn-masthead" data-cn-shell="v1">
<div class="cn-topline cn-wrap"><span>THE CONSIDERED KITCHEN</span><span>AN INDEPENDENT BUYING EDIT</span></div>
<div class="cn-mast-row cn-wrap"><a class="cn-wordmark" href="{root}index.html" aria-label="Counter Notes home">counter<span>notes</span><b aria-hidden="true">✳</b></a>
<span class="cn-brand-note">Fewer maybes.<br>Better kitchen decisions.</span>
<a class="cn-feed-link" href="{root}feed.xml">Follow the edit <span aria-hidden="true">↗</span></a></div>
<div class="cn-navline"><nav class="cn-nav cn-wrap" aria-label="Main navigation">{links}
<details class="cn-workroom"><summary>Workroom <span aria-hidden="true">+</span></summary>
<div><p>BEHIND THE PUBLICATION</p><a href="{root}workroom.html">Executive summary & all tools</a><a href="{root}suggestions.html">Review suggestions</a><a href="{root}questions.html">Questions & missing information</a><a href="{root}flagged.html">Flagged for Review</a></div></details>
</nav></div></header>
<aside class="cn-disclosure" data-disclosure-strip><p class="cn-wrap"><strong>Affiliate disclosure</strong> · {DISCLOSURE} We may earn a commission from links marked “paid link”. <a href="{root}about.html#affiliate">How this works</a></p></aside>'''


def footer(rel="index.html"):
    root = depth_for(rel)
    operator = "".join(f'<a href="{root}{href}">{esc(label)}</a>' for href, label in OPERATOR_LINKS)
    return f'''<footer class="cn-footer"><div class="cn-wrap">
<div class="cn-footer-grid"><div><a class="cn-wordmark" href="{root}index.html">counter<span>notes</span><b aria-hidden="true">✳</b></a><p>A little more considered.<br>A lot less kitchen guesswork.</p><p class="cn-muted">Independent, AI-assisted source research.<br>Not hands-on product testing.</p></div>
<div><h2>Find your fit</h2><a href="{root}guides/basket-air-fryers.html">Air fryers</a><a href="{root}guides/air-fryer-ovens.html">Countertop ovens</a><a href="{root}guides/thermometers.html">Thermometers</a><a href="{root}guides/index.html">Buying guides</a></div>
<div><h2>The publication</h2><a href="{root}about.html">Our approach & authorship</a><a href="{root}feed.xml">RSS · follow new guides</a><a href="{root}privacy.html">Privacy & measurement</a><a href="{root}workroom.html">Workroom · all dashboards</a></div>
<div><h2>Review before changing</h2><a href="{root}suggestions.html">Suggestions & options</a><a href="{root}questions.html">Questions & information gaps</a><a href="{root}intent.html">Product-intent records</a><a href="{root}flagged.html">Flagged for Review</a></div></div>
<details class="cn-operator-index"><summary>All operator tools & retained research <span aria-hidden="true">+</span></summary><nav aria-label="Operator tools">{operator}</nav></details>
<div class="cn-footer-small"><p><strong>{DISCLOSURE}</strong> Product buttons are direct Amazon links marked sponsored. A configured tag is not an account-level attribution confirmation. Product-intent and reporting checks remain open.</p><p>No static prices, star ratings, invented test results or revenue forecasts. GitHub Pages production analytics is not connected; the self-hosted service is implemented. <a href="{root}privacy.html">Measurement status</a>.</p><p>© 2026 Counter Notes · Independent of Amazon · <a href="https://affiliate-program.amazon.com/help/operating/agreement">Operating Agreement</a> · <a href="https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers">FTC disclosure guidance</a></p></div>
</div></footer>'''


def apply_chrome(document: str, rel: str) -> str:
    """Idempotent deploy-only chrome normalization; preserve legacy content IDs.

    A legacy page's first header is often INSIDE main and contains live router
    IDs. Never replace it with the global masthead. Put the new masthead at the
    body boundary, and keep the old local navigation in the archived body.
    """
    root = depth_for(rel)
    shell = r'<header\b[^>]*data-cn-shell="v1"[^>]*>.*?</header>\s*<aside\b[^>]*data-disclosure-strip[^>]*>.*?</aside>'
    if re.search(shell, document, flags=re.S):
        document = re.sub(shell, lambda _: masthead(rel), document, count=1, flags=re.S)
    else:
        document = re.sub(r'(<body\b[^>]*>)', lambda m: m[1] + '\n' + masthead(rel), document, count=1)
    current_footer = r'<footer\b[^>]*class="cn-footer"[^>]*>.*?</footer>'
    if re.search(current_footer, document, flags=re.S):
        document = re.sub(current_footer, lambda _: footer(rel), document, count=1, flags=re.S)
    else:
        # Put the global footer outside the legacy page's layout wrapper.
        document = re.sub(r'<footer\b[^>]*>.*?</footer>', '', document, count=1, flags=re.S)
        document = document.replace('</body>', footer(rel) + '\n</body>')
    body = re.search(r'<body\b([^>]*)>', document)
    if body is None:
        raise ValueError(f'{rel}: missing body element')
    attrs = body[1]
    if 'cn-publication' not in attrs:
        if 'class="' in attrs:
            attrs = attrs.replace('class="', 'class="cn-publication ', 1)
        else:
            attrs += ' class="cn-publication"'
        document = document[:body.start()] + '<body' + attrs + '>' + document[body.end():]
    if 'assets/css/storefront.css' not in document:
        document = document.replace('</head>', f'<link rel="stylesheet" href="{root}assets/css/storefront.css">\n</head>')
    if 'assets/js/events.js' in document and 'assets/js/measurement-config.js' not in document:
        document = re.sub(r'(<script src="[^\"]*assets/js/events\.js")', f'<script src="{root}assets/js/measurement-config.js" defer></script>\n\\1', document)
    return document
