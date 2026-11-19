"""The current Counter Notes publication. Historical research stays reachable, not in search.

All factual product rows come from content/publication.json. Never obtain an intended
ASIN from a redirect observation. No price, star score, fake reviewer or demand claim.
"""
from __future__ import annotations
import html
import json
import posixpath
from pathlib import Path
from email.utils import format_datetime
from datetime import datetime, timezone

from head_meta import head_block, BASE
from link_builder import ASSOCIATES_TAG, build_product_link

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "content/publication.json").read_text())
GUIDES = json.loads((ROOT / "content/guides.json").read_text())
PRODUCTS = {p["key"]: p for p in DATA["products"]}
SOURCES = DATA["sources"]
DATE = DATA["as_of"]
DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."
TOOLS = [
    ("workspace.html", "Workspace overview"), ("suggestions.html", "Suggestions & choices"),
    ("questions.html", "Questions & missing information"), ("measurement.html", "Measurement & campaign ledger"),
    ("executive-summary.html", "Executive summary"), ("intent.html", "Link & intent register"),
    ("flagged.html", "Flagged for Review"), ("publishing.html", "Publishing cadence & design brief"),
    ("products.html", "Research catalog"), ("analysis.html", "Research analysis"),
    ("content.html", "Content engine"), ("compliance.html", "Compliance research"),
    ("tracking.html", "Tracking research"), ("verification.html", "Verification log"),
    ("sources.html", "Source register"), ("summary.html", "Earlier research summary"),
    ("pages/index.html", "Findings hub"), ("decisions/index.html", "Decision hub"),
    ("release/index.html", "Release readiness"), ("audit/index.html", "Independent audit"),
    ("discovery/index.html", "Discovery review"), ("console/index.html", "Owner’s console"),
    ("board/index.html", "Five-product decision board"), ("intake/index.html", "Submitted-link intake"),
    ("brief/index.html", "Earlier design brief"), ("review-decide.html", "Review board"),
    ("review.html", "Review findings"), ("review-questions.html", "Review questions"),
    ("review-ideas.html", "Review ideas"), ("review-trace.html", "Requirements trace"),
    ("pages/suggestions.html", "Findings-hub suggestions"), ("pages/questions.html", "Findings-hub questions"),
    ("design-notes.html", "Design notes"), ("playbook.html", "Design & content playbook"),
    ("paths.html", "Launch paths"), ("marketing/index.html", "Marketing archive"),
    ("marketing/improvements.html", "Earlier improvement board"), ("journal/index.html", "Journal archive"),
    ("research-hub/start.html", "Affiliate Research Hub archive"), ("zone2/index.html", "Platform archive"),
    ("affiliate-lab/index.html", "Affiliate Lab archive"), ("revalidation/index.html", "Revalidation archive"),
    ("northstar/index.html", "Northstar prototype archive"), ("review-2026-11-15.html", "Dated repository review"),
]


# Preserve the complete upstream navigation/footer union, including the shop and
# thermometer desk delivered while this integration was in flight. No board or
# article is deleted and no owner choice is silently changed.
import re as _re
import shop_layout as _prior_chrome
_existing_targets = {url for url, _ in TOOLS}
_preserved_links = list(_prior_chrome.TOOLS) + list(_prior_chrome.READER_NAV)
_preserved_links += [(url, html.unescape(_re.sub(r'<[^>]+>', '', label))) for url, label in
                     _re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', _prior_chrome.footer('', DATE), _re.S)
                     if not url.startswith(('https:', 'http:'))]
_preserved_links += [('marketing/thermometers/index.html', 'Earlier thermometer desk'),
                     ('guides/cleanup-and-counter-space-earlier.html', 'Earlier cleanup/space guide')]
for _url, _label in _preserved_links:
    if _url not in _existing_targets:
        TOOLS.append((_url, _label))
        _existing_targets.add(_url)


def e(value):
    return html.escape(str(value if value is not None else ""), quote=True)


def prefix(rel):
    return "../" * rel.count("/")


def href(rel, target):
    return prefix(rel) + target


def sources(ids):
    links = []
    for sid in dict.fromkeys(ids):
        s = SOURCES[sid]
        product = s["url"].startswith("https://www.amazon.com/dp/")
        links.append(f'<a class="pb-src" href="{e(s["url"])}" target="_blank" rel="{("sponsored " if product else "")}nofollow noopener noreferrer">{e(s["publisher"])} · {e(sid)} ↗</a>')
    return '<span class="cn-sources">' + " ".join(links) + '</span>'


def tools_links(rel):
    return ''.join(f'<a href="{e(href(rel, url))}">{e(label)}</a>' for url, label in TOOLS)


def masthead(rel):
    nav = [("shop.html", "Shop the edit"), ("guides/index.html", "Buying guides"), ("compare.html", "Compare"), ("about.html", "Our approach")]
    items = []
    for url, label in nav:
        current = ' aria-current="page"' if rel == url else ""
        items.append(f'<a href="{e(href(rel, url))}"{current}>{e(label)}</a>')
    links = "".join(items)
    return f'''<header class="cn-mast">
<div class="cn-wrap cn-mast-row"><a class="cn-brand" href="{e(href(rel, 'index.html'))}" aria-label="Counter Notes home"><span class="cn-brand-mark" aria-hidden="true">c<span>n</span></span><span>Counter <em>Notes</em><small>GOOD GEAR. LESS GUESSWORK.</small></span></a>
<nav class="cn-nav" aria-label="Main navigation">{links}<details class="cn-workspace-menu"><summary>Workspace <span aria-hidden="true">⌄</span></summary><div class="cn-menu-links">{tools_links(rel)}</div></details></nav></div>
</header><aside class="cn-disclosure" data-disclosure-strip aria-label="Affiliate disclosure"><div class="cn-wrap"><strong>Affiliate disclosure:</strong> {DISCLOSURE} <a href="{e(href(rel, 'about.html#affiliate-links'))}">How our links work</a></div></aside>'''


def footer(rel):
    return f'''<footer class="cn-footer"><div class="cn-wrap">
<div class="cn-footer-top"><div><a class="cn-footer-brand" href="{e(href(rel, 'index.html'))}">Counter <em>Notes</em></a><p>Less clutter. More considered choices.<br>Kitchen buying guides for the way you actually cook.</p></div><div><h2>Keep exploring</h2><a href="{e(href(rel, 'shop.html'))}">Shop the kitchen edit</a><a href="{e(href(rel, 'guides/index.html'))}">Read the guides</a><a href="{e(href(rel, 'compare.html'))}">Compare the formats</a></div><div><h2>Stay in the loop</h2><a href="{e(href(rel, 'feed.xml'))}" type="application/rss+xml">Subscribe by RSS ↗</a><a href="{e(href(rel, 'about.html'))}">About & editorial standards</a><a href="{e(href(rel, 'privacy.html'))}">Privacy & measurement</a></div></div>
<details class="cn-footer-tools"><summary>Workspace, source registers & research archives</summary><div class="cn-footer-tool-grid">{tools_links(rel)}</div></details>
<div class="cn-footer-bottom"><p><strong>{DISCLOSURE}</strong> Paid product links go directly to Amazon. We are an independent publication; Amazon does not endorse this site.</p><p>AI-assisted, source-led guides—not hands-on tests. Original illustrations are not product photographs. No current prices, star ratings or sales forecasts are displayed. <a href="{e(href(rel, 'flagged.html'))}">Open questions & corrections</a> · <a href="{e(href(rel, 'privacy.html'))}">Privacy</a></p><p>© 2026 Counter Notes · <a href="{e(href(rel, 'sitemap.xml'))}">Sitemap</a></p></div></div></footer>'''


def shell(rel, title, description, body, *, article=None, scripts=(), indexable=None):
    depth = prefix(rel)
    if indexable is None:
        indexable = rel in indexable_paths()
    schema = {"@context": "https://schema.org", "@type": "WebSite" if rel == "index.html" else "WebPage", "name": title,
              "url": BASE + ("" if rel == "index.html" else rel), "publisher": {"@type": "Organization", "name": "Counter Notes", "url": BASE + "about.html"}}
    if article:
        schema.update({"@type": "Article", "headline": title, "datePublished": article["published"],
                       "dateModified": article["published"], "author": {"@type": "Organization", "name": "Counter Notes", "url": BASE + "about.html#authorship"}})
    schema_text = json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c')
    script_tags = ''.join(f'<script src="{e(depth + s)}" defer></script>' for s in ["assets/js/publication.js", "assets/js/events.js", *scripts])
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Counter Notes</title><meta name="description" content="{e(description)}">
{head_block(rel, title=title + ' · Counter Notes', description=description, site_name='Counter Notes', page_type='article' if article else 'website')}
<meta name="robots" content="{('index,follow' if indexable else 'noindex,follow')}">
<link rel="icon" href="{e(depth)}assets/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Counter Notes — new guides" href="{e(depth)}feed.xml">
<link rel="preload" href="{e(depth)}assets/fonts/fraunces-latin-full-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{e(depth)}assets/css/style.css"><link rel="stylesheet" href="{e(depth)}assets/css/publish.css"><link rel="stylesheet" href="{e(depth)}assets/css/publication.css">
<script type="application/ld+json">{schema_text}</script></head><body class="cn-publication"><a class="cn-skip" href="#main">Skip to content</a>
{masthead(rel)}<main id="main" tabindex="-1">{body}</main>{footer(rel)}{script_tags}</body></html>\n'''


def intro(kicker, title, text, *, tail=""):
    return f'<section class="cn-page-intro cn-wrap"><p class="cn-eyebrow">{e(kicker)}</p><h1>{e(title)}</h1><p class="cn-deck">{e(text)}</p>{tail}</section>'


def product_url(p):
    return build_product_link(p["observation"]["observed_asin"], ASSOCIATES_TAG, link_text="View this product listing").href


def product_cta(p, *, cls="cn-button", label="View on Amazon"):
    return f'<a class="{e(cls)}" href="{e(product_url(p))}" target="_blank" rel="sponsored nofollow noopener" data-link-state="TAGGED" data-product-key="{e(p["key"])}">{e(label)} <span aria-hidden="true">↗</span><span class="cn-paid">paid link</span></a>'


def card(p, rel, *, compact=False):
    return f'''<article class="cn-product" data-category="{e(p['category'])}"><a class="cn-product-image cn-tint-{e(p['design'])}" href="{e(href(rel, 'guides/' + p['slug'] + '.html'))}" tabindex="-1" aria-hidden="true"><img src="{e(href(rel, 'assets/img/' + p['design'] + '.svg'))}" width="360" height="250" loading="lazy" alt=""></a>
<div class="cn-product-copy"><p class="cn-eyebrow">{e(p['kicker'])}</p><h3><a href="{e(href(rel, 'guides/' + p['slug'] + '.html'))}">{e(p['name'])}</a></h3><p class="cn-product-type">{e(p['type'])}</p><p>{e(p['reader']['card_line'])}</p><div class="cn-product-source">{sources([p['source']])}</div><div class="cn-product-actions"><a class="cn-text-link" href="{e(href(rel, 'guides/' + p['slug'] + '.html'))}">What to know <span aria-hidden="true">→</span></a>{product_cta(p, cls='cn-retailer-link')}</div></div></article>'''


def guide_card(g, rel):
    return f'''<article class="cn-guide-card"><a href="{e(href(rel, 'guides/' + g['slug'] + '.html'))}" class="cn-guide-art cn-art-{e(g['art'])}" tabindex="-1" aria-hidden="true"><img src="{e(href(rel, 'assets/img/guide-' + g['art'] + '.svg'))}" alt="" width="480" height="300" loading="lazy"></a><p class="cn-eyebrow">{e(g['category'])}</p><h3><a href="{e(href(rel, 'guides/' + g['slug'] + '.html'))}">{e(g['short_title'])}</a></h3><p>{e(g['description'])}</p><a class="cn-text-link" href="{e(href(rel, 'guides/' + g['slug'] + '.html'))}">Read the guide <span aria-hidden="true">→</span></a></article>'''


def collection_note(rel):
    return f'<p class="cn-fineprint">Design illustrations, not product photographs. These are the observed Amazon destinations of the supplied links; intended-product confirmation and enrolled Associates reporting checks remain open. <a href="{e(href(rel, "intent.html"))}">Link & intent record</a>. No price, tested ranking or popularity claim is implied. Guide topics are editorial hypotheses, not measured search queries or volume claims.</p>'


def home():
    body = f'''<section class="cn-hero cn-wrap"><div class="cn-hero-copy"><p class="cn-eyebrow"><span class="cn-dot"></span> THE THOUGHTFUL KITCHEN EDIT</p><h1>Make room for<br><em>better cooking.</em></h1><p class="cn-deck">Good kitchen gear starts with the right questions. Find the air fryer, countertop oven or thermometer that makes sense for your everyday.</p><div class="cn-hero-actions"><a class="cn-button" href="#kitchen-edit">Explore the kitchen edit <span aria-hidden="true">→</span></a><a class="cn-text-link" href="guides/basket-or-oven.html">Not sure where to start?</a></div><p class="cn-hero-note">Thoughtful comparisons. Practical trade-offs. No made-up winners.</p></div><figure class="cn-hero-visual"><picture><source media="(max-width: 700px)" srcset="assets/img/kitchen-editorial-small.webp"><img src="assets/img/kitchen-editorial.webp" width="1264" height="848" fetchpriority="high" alt="Roasted vegetables, a lemon and linen on a warm kitchen counter"></picture><span class="cn-image-stamp">A little less<br><em>guesswork.</em></span><figcaption>AI-generated editorial image · not a cooking test</figcaption></figure></section>
<div class="cn-principles"><div class="cn-wrap"><span><b aria-hidden="true">↗</b> Direct links to official sources</span><span><b aria-hidden="true">◎</b> Choose by your cooking routine</span><span><b aria-hidden="true">✧</b> Honest about what we haven’t tested</span></div></div>
<section class="cn-section cn-wrap" id="kitchen-edit"><div class="cn-section-heading"><div><p class="cn-eyebrow">A PLACE TO START</p><h2>Different kitchens.<br>Different kinds of useful.</h2></div><a class="cn-text-link" href="shop.html">Shop the full edit <span aria-hidden="true">→</span></a></div><div class="cn-product-grid">{''.join(card(PRODUCTS[k], 'index.html') for k in ('P1','P2','P3'))}</div>{collection_note('index.html')}</section>
<section class="cn-finder-section"><div class="cn-wrap cn-finder" id="finder"><div><p class="cn-eyebrow">LET’S NARROW IT DOWN</p><h2>What would help<br><em>in your kitchen?</em></h2><p>Choose the job you have in mind.<br>We’ll point you to a useful place to compare.</p></div><form id="kitchen-finder"><label for="kitchen-priority">I’m looking for…</label><select id="kitchen-priority" name="priority"><option value="two">Separate baskets for two dishes</option><option value="one">One uninterrupted basket</option><option value="oven">An oven-style cooking space</option><option value="temperature">A way to check food temperature</option></select><button class="cn-button" type="submit">Show me where to start <span aria-hidden="true">→</span></button><p class="cn-finder-result" id="finder-result" role="status">A starting point, not a tested recommendation.</p><noscript><p><a href="compare.html">Compare all the formats without JavaScript.</a></p></noscript></form></div></section>
<section class="cn-section cn-wrap"><div class="cn-section-heading"><div><p class="cn-eyebrow">BEFORE YOU ADD TO CART</p><h2>Better questions.<br>More considered choices.</h2></div><a class="cn-text-link" href="guides/index.html">All buying guides <span aria-hidden="true">→</span></a></div><div class="cn-guide-grid">{''.join(guide_card(g,'index.html') for g in GUIDES[:3])}</div></section>
<section class="cn-section cn-wrap cn-temperature"><div class="cn-temperature-intro"><p class="cn-eyebrow">THE SMALL-TOOLS EDIT</p><h2>Go beyond<br><em>“looks done.”</em></h2><p>Instant-read or connected? Start with how you want to check your food, then look at the exact model’s instructions.</p><a class="cn-text-link" href="guides/instant-read-or-wireless.html">Find your temperature tool <span aria-hidden="true">→</span></a><p class="cn-fineprint">USDA explains why color alone is not a reliable safety check. {sources(['USDA'])}</p></div><div class="cn-product-grid cn-grid-two">{''.join(card(PRODUCTS[k], 'index.html', compact=True) for k in ('P4','P5'))}</div></section>
<section class="cn-editorial-note cn-wrap"><span class="cn-editorial-symbol" aria-hidden="true">cn.</span><div><p class="cn-eyebrow">A NOTE ON OUR APPROACH</p><h2>Useful advice doesn’t need<br>an invented test score.</h2><p>We turn official product information into practical questions and comparisons. We haven’t tested these products in a kitchen, and we won’t pretend we have. You’ll find the trade-offs, the sources, and the details still worth checking.</p><a class="cn-text-link" href="about.html">How Counter Notes is made <span aria-hidden="true">→</span></a></div></section>
{rss_block('index.html')}'''
    return shell('index.html', 'Thoughtful kitchen gear & buying guides', 'Compare air fryers, countertop ovens and thermometers with question-led buying guides and practical trade-offs. Good gear. Less guesswork.', body)


def rss_block(rel):
    return f'<section class="cn-rss"><div class="cn-wrap"><div><p class="cn-eyebrow">A GOOD READ, NOT MORE NOISE</p><h2>Keep a little room for good ideas.</h2><p>Follow new guides in your RSS reader. No email form, tracking pixels or inbox clutter.</p></div><a class="cn-button cn-button-light" href="{e(href(rel, "feed.xml"))}">Follow Counter Notes <span aria-hidden="true">↗</span></a></div></section>'


def shop():
    rel = 'shop.html'
    body = intro('THE KITCHEN EDIT', 'Find the format that fits your routine.', 'Three air-fryer formats. Two temperature tools. Start with the job you want to do, then check the exact listing and model instructions.')
    body += '<section class="cn-wrap cn-section cn-section-tight"><div class="cn-filters" role="group" aria-label="Filter the kitchen edit"><button type="button" data-filter="all" aria-pressed="true">The full edit</button><button type="button" data-filter="air-fryers" aria-pressed="false">Air fryers & ovens</button><button type="button" data-filter="thermometers" aria-pressed="false">Temperature tools</button><span id="filter-status" role="status">All five product notes</span></div><div class="cn-product-grid">'
    body += ''.join(card(p, rel) for p in PRODUCTS.values()) + '</div>' + collection_note(rel) + '</section>'
    return shell(rel, 'Shop the kitchen edit', 'Explore five observed Amazon listings: Chefman air fryers, an Emeril countertop oven, and ThermoMaven and CHEF iQ thermometers.', body)


def spec_table(p):
    rows = []
    for label, value, sid, status in p['specs']:
        missing = not value
        content = e(value) if value else '<span class="cn-empty" aria-label="Unverified value">—</span>'
        rows.append(f'<tr><th scope="row">{e(label)}</th><td>{content}<small class="cn-value-note">{e(status)}</small></td><td>{sources(sid if isinstance(sid, list) else [sid])}</td></tr>')
    return '<div class="cn-table-scroll" tabindex="0" role="region" aria-label="Official specification rows"><table class="cn-table"><caption>Official information read 19 November 2026. A dash is unverified, not an estimate. Manufacturer/listing statements are not independent test results.</caption><thead><tr><th scope="col">What to compare</th><th scope="col">What the source says</th><th scope="col">Official source</th></tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'


def product_page(p):
    """A reader-facing product note.

    T68 (session 5f7f77a4, 2026-11-19): the five notes used to differ only in their name, one intro
    sentence, one trade-off sentence and five table rows; a lexical comparison put a third of two
    notes in common (`chef-iq-sense` vs `thermomaven-instant-read` measured 0.389). Everything here
    below the masthead is now written per product: fit / not-a-fit, the trade-off in words, and the
    checks a buyer can actually perform. The specification table is unchanged and every value in it
    still comes from `content/publication.json` with a link to the official page that states it.
    """
    rel = 'guides/' + p['slug'] + '.html'
    g = GUIDES[4] if p['category'] == 'thermometers' else GUIDES[0]
    r = p['reader']
    fit = ''.join(f'<li>{e(x)}</li>' for x in r['fit_for'])
    notfit = ''.join(f'<li>{e(x)}</li>' for x in r['not_for'])
    checks = ''.join(f'<article class="cn-check"><h3>{e(c["heading"])}</h3><p>{e(c["body"])}</p></article>'
                     for c in r['checks'])
    body = f'''<section class="cn-wrap cn-product-hero"><div><p class="cn-eyebrow">PRODUCT NOTES · {e(p['brand'])}</p><h1>{e(p['name'])}</h1><p class="cn-deck">{e(p['question'])}</p><p class="cn-lede">{e(r['dek'])}</p><p class="cn-byline">By <a href="../about.html#authorship">Counter Notes</a> · AI-assisted product notes · Sources checked {e(r['reviewed'])}<br>Source-based comparison, not a hands-on review.</p>{product_cta(p)}<p class="cn-fineprint">Current price and availability are on Amazon. This direct link uses the supplied tracking ID; enrolled-account attribution has not been confirmed.</p></div><figure class="cn-product-hero-art cn-tint-{e(p['design'])}"><img src="../assets/img/{e(p['design'])}.svg" width="360" height="250" alt="Generic illustration of the {e(p['type'].lower())} format"><figcaption>Design illustration · not a photograph of this model</figcaption></figure></section>
<section class="cn-wrap cn-reading-wide cn-section-tight">
<p class="cn-lede cn-lede-body">{e(r['lede'])}</p>
<div class="cn-two-notes cn-fit-grid"><div><p class="cn-eyebrow">A GOOD FIT IF</p><ul class="cn-fit">{fit}</ul></div><div><p class="cn-eyebrow">LESS OF A FIT IF</p><ul class="cn-not-fit">{notfit}</ul></div></div>
<h2 class="cn-table-title">The trade-off, stated plainly</h2><p>{e(r['tradeoff'])}</p>
<h2 class="cn-table-title">What is worth checking before you decide</h2><div class="cn-checks">{checks}</div><p class="cn-section-source">Sources for this section: {sources(r['sources'])}</p>
<h2 class="cn-table-title">The details worth checking</h2>{spec_table(p)}
<aside class="cn-note cn-verdict"><h2>If you are deciding now</h2><p>{e(r['verdict'])}</p></aside>
<aside class="cn-note"><h2>About this particular link</h2><p>The supplied short link was observed leading to ASIN <code>{e(p['observation']['observed_asin'])}</code> on {e(DATE)}. An observed destination is not proof of the product the sender intended. The intent fields and the enrolled Associates tracking-report check remain unconfirmed. We do not declare the supplied short link invalid.</p><p><a href="../intent.html">See the separate intent and observation fields</a> · {sources(['AMZ-LINKS','AMZ-AGREEMENT'])}</p></aside>
<div class="cn-next-read"><p class="cn-eyebrow">BEFORE YOU DECIDE</p><h2><a href="{e(g['slug'])}.html">{e(g['title'])}</a></h2><p>{e(g['description'])}</p><a class="cn-text-link" href="../compare.html">Compare the formats →</a></div></section>'''
    return shell(rel, p['name'] + ': what to know before buying', r['dek'], body)


def guides_index():
    rel = 'guides/index.html'
    body = intro('THE BUYING-GUIDE SHELF', 'A good question is a good place to start.', 'Capacity, counter space, cleanup and temperature tools. Practical reading for a more considered kitchen—not a list of supposed bests.')
    body += '<section class="cn-wrap cn-section cn-section-tight"><div class="cn-guide-grid">' + ''.join(guide_card(g,rel) for g in GUIDES) + '</div><div class="cn-note"><h2>Browse the earlier research</h2><p>The original specification tables and dated articles are preserved for reference. <a href="basket-air-fryers.html">Basket air fryers</a> · <a href="air-fryer-ovens.html">Air-fryer ovens</a> · <a href="buying-guides.html">Earlier buying guides</a> · <a href="method.html">Source method</a>. They are not fresh hands-on tests. Additional preserved treatments: <a href="meat-thermometers.html">thermometer category</a> · <a href="instant-read-or-wireless-thermometer.html">earlier instant-read/wireless guide</a> · <a href="thermometer-for-air-fryer.html">thermometers with an air fryer</a> · <a href="multi-function-appliance-questions.html">multifunction questions</a> · <a href="cleanup-and-counter-space-earlier.html">earlier cleanup/space guide</a> · <a href="../shop/guides/index.html">earlier shop guides</a> · <a href="../marketing/thermometers/index.html">thermometer desk</a>.</p></div></section>' + rss_block(rel)
    return shell(rel, 'Question-led kitchen buying guides', 'Practical guides to air fryer capacity, basket versus oven formats, cleanup, counter space, multifunction appliances and thermometers.', body)


def guide_page(g):
    rel = 'guides/' + g['slug'] + '.html'
    toc = ''.join(f'<a href="#{e(s["id"])}">{e(s["heading"])}</a>' for s in g['sections'])
    blocks = ''.join(f'<section id="{e(s["id"])}"><h2>{e(s["heading"])}</h2>' + ''.join(f'<p>{e(p)}</p>' for p in s['paragraphs']) + f'<p class="cn-section-source">Source context: {sources(s["sources"])}</p></section>' for s in g['sections'])
    next_g = GUIDES[(GUIDES.index(g) + 1) % len(GUIDES)]
    body = f'''<header class="cn-article-head cn-wrap"><p class="cn-eyebrow">{e(g['category'])} · THE COUNTER NOTES GUIDES</p><h1>{e(g['title'])}</h1><p class="cn-deck">{e(g['description'])}</p><p class="cn-byline">By <a href="../about.html#authorship">Counter Notes</a> · Published 19 November 2026<br>AI-assisted and source-led. Not a hands-on test or a measured trend.</p></header><div class="cn-wrap cn-article-layout"><aside class="cn-toc"><h2>In this guide</h2>{toc}<a class="cn-toc-compare" href="../compare.html">Compare the formats ↗</a></aside><article class="cn-article"><div class="cn-quick-answer"><p class="cn-eyebrow">THE SHORT ANSWER</p><p>{e(g['answer'])}</p></div>{blocks}<div class="cn-note"><h2>What this guide can—and cannot—tell you</h2><p>Our advice connects official product information to practical buying questions. We have not cooked with, measured, cleaned or tested these products. No product score, price, popularity or sales result is implied. Unconfirmed details remain unverified.</p><a href="../about.html">Read our editorial standards</a></div><div class="cn-next-read"><p class="cn-eyebrow">KEEP READING</p><h2><a href="{e(next_g['slug'])}.html">{e(next_g['title'])}</a></h2></div></article></div><section class="cn-section cn-wrap"><div class="cn-section-heading"><div><p class="cn-eyebrow">PUT THE QUESTION TO A PRODUCT</p><h2>Explore the relevant formats.</h2></div></div><div class="cn-product-grid{(' cn-grid-two' if len(g['products']) == 2 else '')}">{''.join(card(PRODUCTS[k],rel) for k in g['products'])}</div>{collection_note(rel)}</section>'''
    return shell(rel, g['title'], g['description'], body, article=g)


def compare():
    body = intro('SIDE BY SIDE', 'Compare the job, not the hype.', 'Different formats solve different shopping questions. The rows below keep manufacturer statements, listing descriptions and unresolved details separate.')
    body += '<section class="cn-wrap cn-section-tight cn-compare-list">'
    for p in PRODUCTS.values():
        body += f'<article id="{e(p["key"])}"><div class="cn-compare-heading"><img src="assets/img/{e(p["design"])}.svg" width="180" height="125" alt="Generic format illustration"><div><p class="cn-eyebrow">{e(p["type"])}</p><h2><a href="guides/{e(p["slug"])}.html">{e(p["name"])}</a></h2><p>{e(p["tradeoff"])}</p></div></div>{spec_table(p)}<p class="cn-compare-link">{product_cta(p, cls="cn-retailer-link")}</p></article>'
    body += collection_note('compare.html') + '</section>'
    return shell('compare.html', 'Compare air fryer and thermometer formats', 'Official specification rows for the five observed Amazon listings, with sources, practical trade-offs and unverified details left blank.', body)


def about():
    body = intro('OUR APPROACH', 'Less guesswork. More useful questions.', 'Counter Notes is an independent, AI-assisted kitchen buying publication. We help you compare the information that matters before buying; we do not pretend a spec sheet is a hands-on test.')
    body += f'''<div class="cn-wrap cn-reading cn-prose"><section id="authorship"><h2>Who makes Counter Notes?</h2><p>The publication is maintained through this repository and AI-assisted research and development. “Counter Notes” is the organizational author, not an invented person. No named human editor, professional testing credential, or physical product testing is claimed. A designated human review and contact process is an open item on the <a href="questions.html">questions register</a>.</p><p>Our guides combine source information with explicitly editorial decision exercises. We do not reproduce customer reviews, star ratings or claimed personal experience. {sources(['FTC','GOOGLE-HELPFUL'])}</p></section><section><h2>How we use sources</h2><p>Product rows link to manufacturer pages or official Amazon listings and carry a checked date. A manufacturer statement is attributed as a statement, not treated as our own test result. An unresolved conflict stays unresolved; a value outside our verification scope stays blank.</p><p>The complete historical research remains accessible from the Workspace. New source checks on 19 November 2026 are scoped to the current publication’s rows and guides—not a claim that every historical sentence was re-verified. <a href="docs/verification-37333afd.md">Read the dated verification record</a>.</p></section><section id="affiliate-links"><h2>How our affiliate links work</h2><p><strong>{DISCLOSURE}</strong> Product buttons marked “paid link” point directly to Amazon using the owner-supplied tracking ID <code>shopnow047c-20</code>. Amazon handles pricing, checkout and orders.</p><p>A correctly shaped link is not proof of enrollment or attribution. We have not accessed an authenticated Associates tracking report. The supplied short links’ exact compliance status remains unresolved; we do not call them invalid. Intended product identity and observed redirect destinations are kept in different fields in the <a href="intent.html">intent register</a>. {sources(['AMZ-AGREEMENT','AMZ-LINKS'])}</p></section><section><h2>Why there are no prices, ratings or “best” scores</h2><p>No licensed, fresh API pricing or ratings feed is connected. We therefore do not display current prices, availability, customer star ratings or review excerpts. Price and review-data automation stays gated on authorized access and policy checks. No popularity, conversion or revenue forecast is offered. {sources(['AMZ-POLICIES','AMZ-AGREEMENT'])}</p></section><section><h2>What the images show</h2><p>The front-page food image is AI-generated editorial artwork, not a meal cooked in any featured appliance. The original appliance and tool illustrations show generic formats, not exact product appearance, scale or dimensions. They are labelled accordingly. No Amazon product photography is copied or cached.</p></section><section><h2>Corrections, privacy and new guides</h2><p>Known uncertainties are published on <a href="flagged.html">Flagged for Review</a>. Review choices live on the <a href="suggestions.html">suggestions board</a>. Read the <a href="privacy.html">privacy notice</a> and follow our <a href="feed.xml">RSS feed</a> for new guides. Email capture is not presented as working without a real subscription service.</p></section></div>'''
    return shell('about.html', 'About our source-led kitchen publication', 'How Counter Notes uses AI assistance, official sources, affiliate links and original illustrations—and the testing and account checks we have not performed.', body)


def privacy():
    body = intro('PRIVACY & MEASUREMENT', 'Measure the page. Not the person.', 'A narrow, first-party measurement design: aggregate events, no reader IDs, and no invented purchase attribution. Updated 19 November 2026.')
    body += f'''<div class="cn-wrap cn-reading cn-prose"><h2>What is active on GitHub Pages?</h2><p>The published Pages configuration disables event collection. No counter events are transmitted or stored in browser storage. GitHub Pages is static hosting and cannot run our writable collector. The collector is implemented, but a permanent owner-controlled host is not provisioned. {sources(['GH-PAGES'])}</p><h2>What changes on a self-hosted deployment?</h2><p>When the complete site runs with our same-origin collector, the browser can send a visible page-load event, a click on a marked Amazon product link, and an observed disclosure-strip intersection. Only registered page paths, a static product label, a broad referrer category and a daily count are stored. No cookies, localStorage, fingerprints, reader/session identifiers, raw referrers, search strings, email addresses or IP/user-agent fields are written by the counter.</p><p>Do Not Track and Global Privacy Control disable collection. Browser events are not retried or persisted on your device. A failed count must not stop you following a link. A disclosure event is not proof of individual compliance, and counts are not unique readers or sessions.</p><h2>Optional operator review preferences</h2><p>The Suggestions page can save the operator’s explicitly selected proposal options in localStorage and export them on request. Those choices never leave the browser automatically, are not used by the analytics counter, and can be cleared on that page. No reader identifier is generated.</p><h2>Network metadata and other companies</h2><p>The hosting and network infrastructure necessarily receives connection information. GitHub states that it logs visitor IP addresses for security. A future reverse proxy or analytics host must have its logging configured and reviewed; we cannot promise that every infrastructure provider stores no network data. Amazon’s own policies apply when you follow a link there. {sources(['GH-PAGES'])}</p><h2>Retention and reports</h2><p>The self-hosted counter’s retention is 90 days for daily aggregates and imported report periods; deployments must run the documented daily prune task and apply the same limit to backups. No public endpoint exposes statistics. Purchase information can only come from an authorized first-party Associates report, not from watching a click. Search query reports require authorized Search Console access and a reviewed non-personal topic allowlist.</p><h2>No blanket legal assurance</h2><p>This describes the engineering and the current deployment state, not a determination of GDPR, ePrivacy, CCPA or other legal compliance. The site operator’s identity, jurisdictional assessment and privacy-contact process require review before a permanent analytics rollout. These gaps are on the <a href="flagged.html">Flagged for Review page</a>.</p><p><a href="measurement.html">Read the five-event contract and deployment gate</a> · <a href="measurement/README.md">Self-hosting documentation</a></p></div>'''
    return shell('privacy.html', 'Privacy and aggregate measurement', 'Current Pages collection state, self-hosted aggregate counters, privacy signals, 90-day retention and the limits of purchase attribution.', body)


QUESTIONS = [
    ('Q63-01','Which exact product was intended for each submitted link?','All five public destinations were observed on 19 November.','Intended ASIN, official listing URL, confirmation date and confirming source.','Obtain a product-intent confirmation or enrolled Associates link record; never copy the observation into intent.','AMZ-LINKS'),
    ('Q63-02','Does the supplied tracking ID attribute eligible activity?','The owner supplied shopnow047c-20; direct product links use it.','Authenticated enrollment and tracking-report evidence.','Validate one link per product in the enrolled workflow and inspect the authorized report. Do not generate artificial clicks or buy through your own links.','AMZ-POLICIES'),
    ('Q63-03','Where will a permanent first-party collector run?','A runnable same-origin collector and five-event contract exist; Pages cannot run it.','Owner-controlled public host, TLS, persistence and log/retention review.','Deploy the documented service on authorized infrastructure; confirm actual POST persistence before setting production collection active.','GH-PAGES'),
    ('Q63-04','Which buyer questions actually bring readers?','Question-shaped guides and one canonical reader sitemap/feed are shipped.','Verified Search Console property and authorized query reports.','Verify the URL-prefix property through the owner’s Google account; import authorized reviewed query/page aggregates. Never infer popularity from a working title.','GOOGLE-OWNERSHIP'),
    ('Q63-05','Who is accountable for human editorial and privacy review?','Counter Notes is identified as an AI-assisted organizational author; no physical testing is claimed.','Named responsible operator, contact route and review sign-off.','Designate the operator and review process, then publish only details the operator authorizes. Do not invent a person or credentials.','FTC'),
    ('Q63-06','Can current prices, ratings or review analysis be displayed?','No authorized fresh API feed is connected; those fields are not displayed.','API access, exact permitted use, expiry handling and policy review.','Use authorized Amazon tooling and review the current IP/API terms before enabling any data module; do not scrape or copy reviews.','AMZ-POLICIES'),
    ('Q63-07','Which version resolves the conflicting specifications?','The Emeril preset/accessory counts and Chefman temperature wording disagree across official page sections.','Exact model/version and authoritative clarification.','Check the purchase-time model manual and ask the manufacturer to reconcile the conflicting statements. Keep disputed values unverified.','AMZ-LINKS'),
    ('Q68-01','Is one site being indexed, or 210 competing destinations?','The root sitemap lists the 16 reader URLs; the deployed HTML also contains 192 other crawlable pages that are absent from it and carry no robots directive.','A decision on which operator/archive surfaces should be excluded from Search, and by which mechanism.','Choose one of S68-01 A–C; then apply the chosen mechanism in the build and prove it with the existing discoverability gate. Crawl budget and ranking effect are not asserted here.','GOOGLE-SPAM'),
    ('Q68-02','Does any buyer question actually bring a reader?','Five question-shaped guides and one RSS feed are published; no query data exists.','A verified Search Console property and authorized query/page report.','Verify the property through the owner’s Google account and import reviewed aggregates. A working title is an editorial hypothesis, never a volume claim.','GOOGLE-OWNERSHIP'),
    ('Q68-03','How thick is the product photography problem?','All five notes use a labelled generic SVG illustration; no product photograph or Amazon-hosted image is used.','The owner’s decision on S68-02, plus written confirmation of any image rights relied on.','Read the Associates IP licence and image requirements, then record a dated decision before any photograph is added.','AMZ-POLICIES'),
    ('Q68-04','Is the title of every reader page distinct and descriptive?','Each indexable page carries its own title and meta description, generated per page.','Nothing is missing for the mechanical check; whether the wording earns clicks needs search impression data.','Keep the per-page titles under the existing gate; measure with Search Console before rewriting from instinct.','GOOGLE-SNIPPET'),
]


def question_register():
    rows = ''.join(f'<tr id="{e(i)}"><th scope="row">{e(i)}<br>{e(q)}</th><td>{e(known)}</td><td>{e(missing)}</td><td><span class="cn-empty">—</span><small class="cn-value-note">Unverified / open</small></td><td>{e(action)} {sources([sid])}</td></tr>' for i,q,known,missing,action,sid in QUESTIONS)
    return '<div class="cn-table-scroll" tabindex="0" role="region" aria-label="Current known and unknown register"><table class="cn-table"><caption>Current information gaps. The official link constrains the rule; it does not establish an account-specific answer. Open answers deliberately remain blank.</caption><thead><tr><th>Question</th><th>What we know</th><th>What is missing</th><th>Answer</th><th>How to discover it / official reference</th></tr></thead><tbody>' + rows + '</tbody></table></div>'


PROPOSALS = [
    ('S63-01','Choose the next evidence-backed topic','GOOGLE-HELPFUL','Q63-04', [('A','Use measured Search Console questions','Requires authorized reports; strongest evidence of actual arrivals.'),('B','Commission a clearly labelled editorial hypothesis','Can proceed without demand data; do not call it trending.'),('C','Refresh an existing guide first','Less new content; resolves source drift before expanding.')],'A'),
    ('S63-02','Choose the permanent measurement path','GH-PAGES','Q63-03', [('A','Self-host the publication and collector together','Same-origin, persistent aggregate counters; requires a real host and TLS.'),('B','Keep static Pages with collection off','No new infrastructure; no first-party event history.'),('C','Review a controlled first-party proxy deployment','Requires authorized DNS/routing and infrastructure privacy review.')],'A'),
    ('S63-03','Choose how far to expand the kitchen edit','AMZ-LINKS','Q63-01', [('A','Hold new products until intent and link checks pass','Slower expansion; preserves current source and attribution gates.'),('B','Research new formats without publishing paid links','Builds knowledge; does not establish profitable demand.'),('C','Broaden categories after measured reader demand','Needs reports and a new source review for every product.')],'A'),
    ('S63-04','Choose an accountable editorial review path','FTC','Q63-05', [('A','Name a responsible human reviewer and corrections contact','Requires real operator details and review time, not an invented byline.'),('B','Keep the transparent organizational byline for now','Accurate current state; leaves human accountability unresolved.')],'A'),
    ('S63-05','Choose how readers follow new guides','GOOGLE-HELPFUL','Q63-05', [('A','Keep the shipped RSS feed as the capture path','Works now without email collection or a subscription backend.'),('B','Add consent-based email after provider/privacy review','Needs an authorized service, real unsubscribe handling and privacy-contact details.')],'A'),
    ('S68-01','Decide what search engines are meant to index','GOOGLE-SPAM','Q68-01', [('A','Keep the reader publication as the only indexable surface and exclude the operator/archive pages from crawling with robots.txt','One directive file; no page content changes; every dashboard stays reachable and linked for the owner.'),('B','Index the research hub as a second citable reference site','A second surface to maintain and defend; risks splitting the site’s topical focus.'),('C','Leave the deployed state as it is and accept 192 crawlable pages outside the sitemap','No build cost; leaves the duplicate-purpose surfaces in front of search engines.')],'A'),
    ('S68-02','Decide the imagery standard now that the notes are text-complete','AMZ-POLICIES','Q68-03', [('A','Keep labelled original illustrations and add no photography','Accurate and rights-safe today; a buyer still cannot see the actual product inside this site.'),('B','Use only imagery served through Amazon’s licensed tooling, where the terms allow it','Closest to what a buyer expects; depends on API access this project does not have.'),('C','Commission original photography of owned units','Strongest editorial asset; requires owning the units and a real photographer.')],'A'),
    ('S68-03','Decide whether the five product notes stay thin doorways or become full guides','GOOGLE-HELPFUL','Q68-01', [('A','Keep each note focused and link it into a longer question-led guide','Every note already links to a guide; low build cost; keeps pages short and specific.'),('B','Expand each note into a 1,500-word standalone review','More per-page depth; repeats what the guides already say and risks the duplication this session measured.'),('C','Merge the five notes into one comparison page','One strong page; loses the per-product entry point a searcher lands on.')],'A'),
    ('S68-04','Decide whether the meta descriptions are worth rewriting before any impression data exists','GOOGLE-SNIPPET','Q68-04', [('A','Keep the current per-page descriptions and let Google choose the snippet','No work; Google documents the description as a snippet input, not a ranking factor.'),('B','Rewrite every reader description around the benefit a searcher sees first','A later click-through experiment; no ranking or traffic claim can be attached yet.'),('C','Remove the meta descriptions and let the snippet come from page text','Less control over the snippet; nothing in the current evidence favours either side.')],'A'),
]


def suggestions_current():
    cards = []
    for ident,title,sid,qid,options,recommended in PROPOSALS:
        opts = ''.join(f'<label class="cn-choice"><input type="radio" name="{e(ident)}" value="{e(code)}"><span><strong>{e(code)} · {e(label)}{(" · recommended" if code==recommended else "")}</strong><small>{e(cost)}</small></span></label>' for code,label,cost in options)
        cards.append(f'<article class="cn-proposal" id="{e(ident)}" data-proposal="{e(ident)}"><p class="cn-eyebrow">{e(ident)} · PROPOSED, NOT IMPLEMENTED</p><h3>{e(title)}</h3><p>Evidence needed: <a href="questions.html#{e(qid)}">{e(qid)}</a>. Official context: {sources([sid])}</p><fieldset><legend>Record a preferred path for review</legend>{opts}</fieldset><p class="cn-choice-state" data-choice-state role="status">No local preference recorded.</p></article>')
    return f'''<section class="cn-wrap cn-section-tight" id="current-proposals"><div class="cn-note"><h2>Review a path before applying it.</h2><p>These are new strategic proposals, not automatic changes. You may record a preference below. It stays in this browser only and does not approve a deployment, submit account data or change the site. Export the review record if you want it retained outside this device.</p><div class="cn-review-controls"><button type="button" class="cn-button" id="export-choices">Export review choices</button><button type="button" class="cn-plain-button" id="clear-choices">Clear local choices</button><span id="review-status" role="status"></span></div></div>{''.join(cards)}</section>'''


def measurement():
    rows = [
        ('EV-01','page_view','Visible page load; registered page and broad referrer category','Implemented; permanent Pages collector absent','GH-PAGES'),
        ('EV-02','product_link_click','Trusted primary/middle click on a marked direct Amazon product link','Implemented; permanent Pages collector absent','AMZ-POLICIES'),
        ('EV-03','disclosure_view','Actual disclosure-strip intersection; unknown without observer support','Implemented; permanent Pages collector absent','FTC'),
        ('EV-04','conversion_import','Authorized Associates export only; local importer, not a browser event','Importer tested; first-party report not supplied','AMZ-AGREEMENT'),
        ('EV-05','search_query_import','Authorized Search Console export; reviewed non-personal topic allowlist','Importer tested; verified property/report not supplied','GOOGLE-HELPFUL'),
    ]
    trs = ''.join(f'<tr id="{i}"><th scope="row">{i}<br><code>{n}</code></th><td>{e(f)}</td><td>{e(s)}</td><td>{sources([sid])}</td></tr>' for i,n,f,s,sid in rows)
    body = intro('MEASUREMENT & CAMPAIGNS','Count what happened. Never invent what sold.','The five-event implementation is ready to self-host. GitHub Pages collection is off: a static deployment is not a writable analytics endpoint.')
    body += f'''<section class="cn-wrap cn-section-tight"><div class="cn-note"><h2>Production deployment gate: open</h2><p>The first-party SQLite collector runs in the self-hosted preview and is covered by automated tests. A temporary sandbox is not a permanent host. Until an authorized public host persists events, production event history is unavailable—not zero.</p><p><a href="measurement/README.md">Run/deploy the service</a> · <a href="privacy.html">Privacy and retention</a> · <a href="questions.html#Q63-03">Information required</a></p></div><div class="cn-table-scroll" tabindex="0" role="region" aria-label="Five-event contract"><table class="cn-table"><caption>Five defined events, distinct from deployment or imported-report availability.</caption><thead><tr><th>Event</th><th>Definition</th><th>Actual state</th><th>Official reference</th></tr></thead><tbody>{trs}</tbody></table></div><h2 class="cn-table-title">Campaign observations</h2><div class="cn-empty-state"><span aria-hidden="true">↗</span><h3>No authorized report has been imported.</h3><p>Timestamp, source, channel, eligible sessions, clicks and reported orders will remain blank until supplied by an authorized first-party report. The importer retains a dated file-hash provenance trail. A page view is not an eligible session and a click is not an order.</p>{sources(['AMZ-AGREEMENT','AMZ-POLICIES'])}</div><h2 class="cn-table-title">What is deliberately not measured</h2><p>No reader ID, cookie, fingerprint, per-user sub-tag, raw referrer, search string or IP/user-agent field. Daily aggregates expire after 90 days with the documented prune task. Infrastructure logging and legal review remain explicit deployment gates. Counters cannot reconstruct a person’s path, deduplicate people, prove bots are excluded, or prove that a disclosure preceded an individual purchase.</p><p>Conversion and query importers reject browser submissions, unknown fields, unreviewed queries, future dates and overlapping periods. They never calculate a profitability score or revenue forecast. Source attestation is an operator assertion, not independent authentication of a report.</p></section>'''
    return shell('measurement.html','Measurement, event contract & campaign ledger','Actual implementation and deployment states for five privacy-preserving events and an empty, provenance-defined campaign ledger.',body,indexable=False)


def intent():
    trs = []
    for p in PRODUCTS.values():
        obs=p['observation']
        blanks=''.join('<td><span class="cn-empty">—</span><small class="cn-value-note">Unconfirmed; not copied from observation</small></td>' for _ in range(4))
        trs.append(f'<tr id="{e(p["key"])}"><th scope="row">{e(p["key"])}<br><a href="{e(p["submitted"])}" rel="sponsored nofollow noopener noreferrer" target="_blank">{e(p["submitted"])}</a></th>{blanks}<td><code>{e(obs["observed_asin"])}</code><br><a href="{e(obs["observed_redirect_target"])}" rel="sponsored nofollow noopener noreferrer" target="_blank">{e(obs["observed_redirect_target"])}</a><small class="cn-value-note">Observed {e(obs["observed_at"])}. Canonical listing component; request query tokens not retained here.</small></td><td>Pending enrolled workflow and report evidence. {sources([obs["source"],"AMZ-LINKS"])}</td></tr>')
    body=intro('LINK & PRODUCT-INTENT REGISTER','What was intended ≠ where a link went.','These two records answer different questions. All intended-product fields remain blank. Publicly observed destinations are stored separately and never promoted into confirmations.')
    body+=f'''<section class="cn-wrap cn-section-tight"><div class="cn-table-scroll" tabindex="0" role="region" aria-label="Product intent and observed destinations"><table class="cn-table"><caption>Intent fields are unconfirmed for every supplied link. A short-link token is not asserted to be an ASIN; its format alone does not establish link compliance.</caption><thead><tr><th>Submitted link</th><th>Intended ASIN</th><th>Official intended listing URL</th><th>Confirmation date</th><th>Confirming source</th><th>Observed redirect target (separate)</th><th>Associates validation / official reference</th></tr></thead><tbody>{''.join(trs)}</tbody></table></div><div class="cn-note"><h2>What the next check must establish</h2><p>Use the enrolled Associates workflow to confirm the destination and tracking report for one link per product before scaling. The tracking ID supplied by the owner is <code>shopnow047c-20</code>. The current product buttons use direct tagged URLs to the observed listings, but an account-level report and intended-product confirmation are not available to this repository.</p><p>The supplied short links are not declared invalid. Their exact compliance status remains unresolved, including the externally referenced <a href="https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003">FLG-003 record</a>. No automatic repair, artificial clicks or purchases through our own links is authorized. {sources(['AMZ-AGREEMENT','AMZ-POLICIES','AMZ-LINKS'])}</p></div></section>'''
    return shell('intent.html','Product-intent confirmations & observed destinations','Five submitted links with intended ASIN, official intended listing URL, confirmation date and source kept separate from observed redirect targets.',body,indexable=False)


CURRENT_FLAGS = [
    ('CN-01','Open','Intent and enrolled tracking remain unconfirmed','All five intended-product records stay blank. Direct tagged listing URLs are not authenticated evidence of enrollment or report attribution.','AMZ-LINKS','Confirm intended products and one enrolled-workflow link/report per product before scaling.'),
    ('CN-02','Open','Permanent analytics host not provisioned','The collector and imports are implemented and tested; production Pages collection remains disabled. A sandbox preview is not a permanent analytics deployment.','GH-PAGES','Deploy on authorized first-party infrastructure and verify persistence, logging, TLS and retention.'),
    ('CN-03','Open','Search demand and profitability are not established','No authorized Search Console query report or Associates order report was supplied. Editorial questions are hypotheses, not trending or high-converting findings.','GOOGLE-HELPFUL','Verify the property and import authorized first-party reports before choosing topics from measured queries.'),
    ('CN-04','Open','Human accountability and jurisdictional privacy review','No real human reviewer/contact details or site-operator legal assessment were supplied. No fictional persona or blanket privacy-compliance claim is added.','FTC','Designate a responsible reviewer/contact and review the production privacy arrangement.'),
    ('CN-05','Open','Conflicting mode, preset, accessory and temperature claims','The Emeril page says 10-in-1 and 11-in-1 modes, 24 and 25 presets, and its accessory count differs from the Amazon title, and Chefman temperature wording differs from the listing title. Disputed values stay unverified.','M3','Confirm the exact model/version and request manufacturer clarification.'),
    ('CN-06','Repaired; retained','Committed deployment workflow contained conflict markers','Both intake and decision-board checks were retained when removing unresolved Git merge markers. Replay now fails fast on markers and pipeline errors.','GH-PAGES','Keep full CI and the packaged-site contract green before merging.'),
    ('CN-07','Repaired; retained','Product-price gates stripped tags before splitting blocks','The existing price checks could treat the entire page as one unit and let an unrelated commission disclosure suppress a product-price failure. The split order is repaired and regression-tested.','AMZ-POLICIES','Retain injected-defect tests for all affected validators.'),
    ('CN-08','Open','Legacy Pages publisher is still enabled','The direct settings write was denied (403). Official API documentation requires Administration write as well as Pages write; the deployment job cannot assume this authority. Actions deploys the verified artifact, but does not disable the legacy source.','GH-PAGES-ADMIN','A repository administrator/maintainer with manage-Pages permission must select GitHub Actions as the Pages source to prevent a second publisher on future pushes. No credentials are requested in chat.'),
    ('CN-09','Advisory','Inherited Actions runtime declarations need review','The successful GitHub run warned that inherited Node20 action declarations are forced onto Node24. No insecure runtime opt-out is set; this is an advisory, not a failed build or deployment.','GH-ACTIONS-RUNTIME','Review official Node24-capable action releases and update compatible versions with full checks. Do not downgrade the runner or claim untested dependency upgrades are complete.'),
    ('CN-11','Repaired; retained','Five product notes shared a third of their text','Measured before repair with 8-word shingles (Jaccard): chef-iq-sense × thermomaven-instant-read 0.389, chefman-dual-basket × chefman-single-basket 0.363. Each note now carries per-product fit, not-a-fit, trade-off, four checks and a verdict; the worst pair is 0.163 and tools/note_overlap.py fails the build above 0.25. The threshold is this project’s own budget, not an engine’s published rule.','GOOGLE-SPAM','Keep every new product note below the gate; treat the threshold as reviewable, not as a ranking fact.'),
    ('CN-10','Repaired; retained','Unused link options could mint or overwrite tracking IDs','The legacy builder could concatenate an unissued static campaign suffix and allow query parameters to replace the tag. Current reader links never used those options. The helper now refuses both paths and preserves the exact supplied ID; dedicated negative tests cover them.','AMZ-POLICIES','Keep the legacy campaign registry empty until identity/enrolled-report checks pass. Approved identifiers must be supplied with provenance, never synthesized from a label.'),
]


def flags():
    rows=''.join(f'<tr id="{i}"><th scope="row">{i}<br>{e(title)}</th><td>{e(state)}</td><td>{e(detail)}</td><td>{e(action)}</td><td>{sources([sid])}</td></tr>' for i,state,title,detail,sid,action in CURRENT_FLAGS)
    body=intro('FLAGGED FOR REVIEW','The open questions stay in the open.','Current release irregularities and external gates, followed by the preserved historical flag register. An unverified product field stays blank. Open items do not disguise themselves as passed checks.')
    body+='<section class="cn-wrap cn-section-tight"><div class="cn-table-scroll" tabindex="0" role="region" aria-label="Current release flags"><table class="cn-table"><caption>Current release review · 19 November 2026. Repository findings cite the official rule or platform reference; reproduction details are in the dated verification record.</caption><thead><tr><th>Finding</th><th>State</th><th>Evidence / limitation</th><th>How to resolve</th><th>Official reference</th></tr></thead><tbody>'+rows+'</tbody></table></div><p>Independent repeated checks also reported initial/repeat variation for the last two short links. <a href="docs/source-observations-33e03d63.json">The dated T67 observation record</a> is preserved separately; it does not replace current observations, confirm intent, establish a routing cause, or declare a link invalid.</p><p><a href="docs/verification-37333afd.md">Dated verification and reproduction record</a> · <a href="questions.html">Questions and discovery actions</a></p><h2 class="cn-table-title">Historical source-governed flags</h2><p>These are dated research findings, not a claim that their original status text describes the current release. Read each full record and its date. Current states above take precedence for this release.</p>'
    ledger=json.loads((ROOT/'ledger/flags.json').read_text())['flags']
    old_sources={s['id']:s for s in json.loads((ROOT/'ledger/sources.json').read_text())['sources']}
    historical=[]
    for f in ledger:
        official=' '.join(f'<a href="{e(old_sources[s]["url"])}" target="_blank" rel="sponsored nofollow noopener noreferrer">{e(s)} ↗</a>' for s in f.get('source_ids',[]) if s in old_sources)
        historical.append(f'<tr id="{e(f["id"])}"><th scope="row"><a href="pages/flags.html#{e(f["id"])}">{e(f["id"])}</a></th><td>{e(f.get("title",f.get("issue","Dated finding")))}</td><td>{official or sources(["AMZ-AGREEMENT"])}</td></tr>')
    body+='<div class="cn-table-scroll" tabindex="0" role="region" aria-label="Historical flags"><table class="cn-table" data-historical-flags><caption>Preserved canonical ledger flags; follow the full record for original dates, evidence and actions.</caption><thead><tr><th>ID / full record</th><th>Finding</th><th>Original official sources / rule reference</th></tr></thead><tbody>'+''.join(historical)+'</tbody></table></div></section>'
    return shell('flagged.html','Flagged for Review','Current irregularities, missing evidence and external launch gates, plus the preserved source-governed historical flag register.',body,indexable=False)


def summary():
    body=intro('EXECUTIVE SUMMARY · 19 NOVEMBER 2026','A publication first. A gated platform behind it.','Counter Notes now leads with useful kitchen product choices and buyer questions. Research, evidence and review tools remain reachable without dominating the reader experience.')
    rows=[
        ('Reader experience','Product-led landing page; five product notes in two kitchen clusters; guide shelf, format comparison, honest authorship and original labelled imagery.','GOOGLE-HELPFUL'),
        ('Findability','One canonical reader sitemap and root RSS feed. Operator/archive pages remain reachable but are noindex in the deployed artifact. Indexing and rankings are not guaranteed.','GOOGLE-CANONICAL'),
        ('Affiliate links','Owner-supplied shopnow047c-20 used on direct reader product links. Every deployed Amazon product link is sponsored. No enrolled tracking report or intended-product confirmation is asserted.','AMZ-AGREEMENT'),
        ('Measurement','Five-event service implemented: three aggregate browser counters plus two local first-party report importers. Permanent Pages collector absent; production config stays disabled.','GH-PAGES'),
        ('Automation','Deterministic page/feed/sitemap builds, source and intent gates, strict event validation, report provenance and an editorial planning command. No autonomous revenue optimization or authorized AI/API research feed is claimed.','AMZ-POLICIES'),
        ('Publishing cadence','Proposed cadence: review one question-led guide each Monday, with source refresh first. Only evidence-approved content is published; missed gates leave proposals as drafts. RSS is the working follow path.','GOOGLE-HELPFUL'),
        ('Known unknowns','Product intent, enrollment/report attribution, permanent hosting, Search Console ownership, actual demand/orders, operator contact and human review. Open answers remain blank.','FTC'),
    ]
    trs=''.join(f'<tr><th scope="row">{e(t)}</th><td>{e(d)}</td><td>{sources([s])}</td></tr>' for t,d,s in rows)
    body+=f'<section class="cn-wrap cn-section-tight"><div class="cn-table-scroll" tabindex="0" role="region" aria-label="Executive summary"><table class="cn-table"><caption>Shipped capabilities versus external evidence. Official links constrain the policy/platform statements; code and test provenance are in the dated release record.</caption><thead><tr><th>Area</th><th>Actual state</th><th>Official reference</th></tr></thead><tbody>{trs}</tbody></table></div><div class="cn-note"><h2>Recommended next path</h2><p>Validate one enrolled link per product, provision a real first-party measurement host, verify Search Console, then choose the next guide from authorized query evidence. Do not scale an optimization loop on absent conversion data. These recommendations are reviewable choices, not a claim that external account work has been completed.</p><p><a href="suggestions.html">Review the proposals</a> · <a href="questions.html">Information required before deciding</a> · <a href="flagged.html">Flagged irregularities</a> · <a href="docs/verification-37333afd.md">Verification scope and sources</a></p></div></section>'
    return shell('executive-summary.html','Executive summary: publication & measurement release','What shipped, what was verified, what remains gated and the recommended evidence-led path for the Amazon affiliate platform.',body,indexable=False)


def publishing():
    body=intro('EDITORIAL WORKFLOW','A weekly review. Not an automatic content flood.','Proposed cadence: review one question-shaped guide each Monday. Refresh the sources, check the claims and disclosures, then publish only if the evidence gate passes.')
    rows=''.join(f'<tr><th scope="row">{e(g["title"])}</th><td>Published 19 November 2026; editorial hypothesis, not measured demand.</td><td><a href="guides/{e(g["slug"])}.html">Read guide</a> {sources(["GOOGLE-HELPFUL"])}</td></tr>' for g in GUIDES)
    body+=f'''<section class="cn-wrap cn-reading-wide cn-prose"><h2>The loop</h2><p>The weekly timing is a review proposal, not approval to auto-publish. <code>python3 tools/editorial_plan.py</code> produces a local draft plan only. It does not call a language model, scrape Amazon or change a published page.</p><ol><li>Import authorized query/order reports only when available. Preserve timestamp, source, channel and hash provenance.</li><li>Choose a buyer question with a clear decision it helps. Without query data, mark it an editorial hypothesis, not a trend.</li><li>Read the exact official model sources. Keep conflicts visible and unverified values blank.</li><li>Draft useful trade-offs with transparent authorship. No invented personal testing, reviews or performance claims.</li><li>Check disclosure above the fold, sponsored product links, source rows, intent separation, image rights and current API rules.</li><li>Build the page, root sitemap and RSS feed together; run CI and the packaged-site gate before publishing.</li><li>Review real arrivals and imported orders. No forecast or optimization score substitutes for missing reports.</li></ol><p>{sources(['GOOGLE-HELPFUL','AMZ-POLICIES','FTC'])}</p><h2>A reusable design and content prompt</h2><blockquote>Design Counter Notes as a warm, independent kitchen publication: cream paper, forest-green type, restrained ochre accents, generous whitespace, a confident serif headline and concise everyday language. Lead with the product’s use case and trade-off. Group air fryers/ovens and thermometers into useful buyer-question clusters. Use original, clearly labelled editorial imagery—not fake product testing. Keep evidence one click away and all operator tools in a Workspace group and footer. Never invent prices, ratings, hands-on experience, popularity or conversions. An unknown field stays blank with a source-linked flag. Build mobile-first, keyboard-accessible pages with one clear next step.</blockquote><h2>Published question cluster</h2><div class="cn-table-scroll" tabindex="0" role="region" aria-label="Published editorial cluster"><table class="cn-table"><caption>Working hypotheses turned into source-led guides; no search-volume claim.</caption><thead><tr><th>Question</th><th>State</th><th>Page and official editorial guidance</th></tr></thead><tbody>{rows}</tbody></table></div><h2>What AI automation is allowed to do</h2><p>Assist with structured drafting, source-linked organization, linting and proposals. It may not manufacture API access, perform undeclared scraping, claim a high-converting niche without reports, bypass Amazon Agent rules, self-approve claims or silently publish an optimization experiment. The existing API adapter remains credential-gated. This release adds no unattended Amazon-page scraper and no LLM service is connected. {sources(['AMZ-POLICIES'])}</p><p><a href="suggestions.html">Choose a future direction</a> · <a href="measurement.html">Measurement prerequisites</a> · <a href="feed.xml">Root RSS feed</a></p></section>'''
    return shell('publishing.html','Publishing cadence, editorial gates & design prompt','A weekly evidence-gated publishing plan, question-shaped content cluster and reusable publication design prompt.',body,indexable=False)


def workspace():
    body=intro('THE WORKSPACE','The machinery, kept out of the shop window.','Review decisions, inspect the evidence and check deployment gates. These are operator tools and preserved research—not a second set of competing storefronts.')
    body+='<section class="cn-wrap cn-section-tight"><div class="cn-workspace-cards">'+''.join(f'<a href="{e(url)}"><span aria-hidden="true">↗</span><h2>{e(label)}</h2></a>' for url,label in TOOLS if url!='workspace.html')+'</div><div class="cn-note"><h2>Start with the current release</h2><p>The executive summary, current questions, measurement contract and Flagged for Review page describe this release. Earlier namespaces retain their dated findings; read them as history rather than proof that an external account or service is active today.</p></div></section>'
    return shell('workspace.html','Workspace: decisions, evidence & platform tools','All dashboards, review boards, source registers and historical builds from one navigation group.',body,indexable=False)


def indexable_paths():
    return {'index.html','shop.html','compare.html','guides/index.html','about.html','privacy.html'} | {'guides/'+g['slug']+'.html' for g in GUIDES} | {'guides/'+p['slug']+'.html' for p in PRODUCTS.values()}


def extra_pages():
    pages={'shop.html':shop(), 'compare.html':compare(), 'about.html':about(), 'privacy.html':privacy(),
           'measurement.html':measurement(),'intent.html':intent(),'flagged.html':flags(),'workspace.html':workspace(),
           'publishing.html':publishing(),'executive-summary.html':summary()}
    pages.update({'guides/'+g['slug']+'.html':guide_page(g) for g in GUIDES})
    pages.update({'guides/'+p['slug']+'.html':product_page(p) for p in PRODUCTS.values()})
    return pages


def feed():
    from xml.sax.saxutils import escape
    items=[]
    for g in GUIDES:
        url=BASE+'guides/'+g['slug']+'.html'
        pub=format_datetime(datetime.fromisoformat(g['published']).replace(tzinfo=timezone.utc),usegmt=True)
        items.append(f'<item><title>{escape(g["title"])}</title><link>{url}</link><guid isPermaLink="true">{url}</guid><pubDate>{pub}</pubDate><description>{escape(g["description"])}</description></item>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Counter Notes — new guides</title><link>'+BASE+'</link><description>Thoughtful kitchen buying guides. Good gear. Less guesswork.</description><language>en-us</language><atom:link href="'+BASE+'feed.xml" rel="self" type="application/rss+xml"/>'+''.join(items)+'</channel></rss>\n'
