"""Current Counter Notes publication. Research records are inputs, not buyer copy.

New facts come only from docs/publication.json's dated official-source observations.
Unknown intent and account confirmation fields stay empty; syntax is not attribution.
"""
from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from head_meta import BASE, head_block
from link_builder import ASSOCIATES_TAG, build_product_link
from publication_shell import DISCLOSURE, OPERATOR_LINKS, depth_for, footer, masthead, render_icons

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / 'docs/publication.json').read_text())
OLD_BOARD = json.loads((ROOT / 'docs/board-9251f262.json').read_text())
PRODUCTS = DATA['products']
BY_KEY = {p['key']: p for p in PRODUCTS}
AS_OF = DATA['as_of']

GUIDES = [
    {'slug': 'basket-or-oven', 'title': 'Basket or oven-style air fryer: what should you compare?', 'short': 'Basket or oven? Start with the way you cook.', 'category': 'The format question', 'description': 'Separate baskets, one larger drawer or French doors: compare the layouts before counting presets.', 'sources': ['chefman_dual','chefman_single','emeril'], 'keys': ['P1','P2','P3']},
    {'slug': 'air-fryer-capacity', 'title': 'A no-hype checklist for comparing air fryer capacity', 'short': 'How much air fryer do you actually need?', 'category': 'Size without the guesswork', 'description': 'Combined quarts are only the starting point. Compare the basket layout and leave unmeasured serving estimates out of it.', 'sources': ['chefman_dual','amazon_p1','chefman_single','emeril'], 'keys': ['P1','P3','P2']},
    {'slug': 'cleanup-and-counter-space', 'title': 'How should you assess cleanup and counter-space trade-offs?', 'short': 'The counter-space check worth doing first.', 'category': 'The everyday details', 'description': 'Measure where it will live, check the removable parts, and separate appliance dimensions from required clearance.', 'sources': ['chefman_dual','chefman_single','emeril'], 'keys': ['P1','P3','P2']},
    {'slug': 'multi-function-appliances', 'title': 'What should you ask before buying a multi-function kitchen appliance?', 'short': 'More functions. But which ones will you use?', 'category': 'Beyond the feature list', 'description': 'A practical set of questions about layout, modes, exact variants and the tools already in your kitchen.', 'sources': ['emeril','amazon_p2','chefman_single','amazon_p3'], 'keys': ['P2','P1','P3']},
]


def e(value):
    return html.escape(str(value), quote=True)


def source(key, label=None):
    item = DATA['sources'][key]
    # Evidence links are not monetized, but marketplace product citations still
    # carry sponsored per this project's deliberately conservative link policy.
    rel = 'sponsored nofollow noopener noreferrer' if 'amazon.com/dp/' in item['url'] else 'noopener noreferrer'
    return f'<a class="cn-source" href="{e(item["url"])}" target="_blank" rel="{rel}">{e(label or item["label"])}</a>'


def product_cta(product, *, label='View listing', cls='cn-amazon'):
    link = build_product_link(product['asin_observed'], ASSOCIATES_TAG, link_text=label)
    return (f'<a class="{cls}" href="{e(link.href)}" target="_blank" rel="sponsored nofollow noopener noreferrer" '
            f'data-link-state="TAGGED" data-product-key="{product["key"]}" data-validation-state="awaiting-account-report">'
            f'{e(label)} <span aria-hidden="true">↗</span></a>')


def schema(rel, title, desc, *, article=False):
    payload = {'@context': 'https://schema.org', '@type': 'Article' if article else 'WebPage',
               'headline' if article else 'name': title, 'description': desc, 'url': BASE + ('' if rel == 'index.html' else rel),
               'publisher': {'@type': 'Organization', 'name': DATA['brand'], 'url': BASE}}
    if article:
        payload.update({'author': {'@type': 'Organization', 'name': DATA['author'], 'url': BASE+'about.html'},
                        'datePublished': AS_OF, 'dateModified': AS_OF, 'isAccessibleForFree': True})
    # No Product/Review/Offer, price, rating, invented reviewer or nonexistent test.
    return '<script type="application/ld+json">'+json.dumps(payload, ensure_ascii=False).replace('</','<\\/')+'</script>'


def page(rel, title, description, body, *, article=False):
    root = depth_for(rel)
    meta = head_block(rel, title=title+' · Counter Notes', description=description,
                     site_name='Counter Notes', page_type='article' if article else 'website')
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Counter Notes</title><meta name="description" content="{e(description)}">
{meta}
<link rel="icon" href="{root}assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Counter Notes · new guides" href="{root}feed.xml">
<link rel="stylesheet" href="{root}assets/css/storefront.css">
{schema(rel,title,description,article=article)}
</head><body class="cn-publication"><a class="cn-skip" href="#main">Skip to content</a>
{masthead(rel)}
<main id="main">{render_icons(body)}</main>
{footer(rel)}
<script src="{root}assets/js/measurement-config.js" defer></script><script src="{root}assets/js/events.js" defer></script>
<script src="{root}assets/js/publication.js" defer></script>
</body></html>\n'''


def pagehead(kicker, title, deck, *, byline=False):
    credit = (f'<div class="cn-byline"><span>By {e(DATA["author"])}</span><span>Published 19 November 2026</span><span>Source research · not hands-on testing</span></div>' if byline else '')
    return f'<header class="cn-pagehead"><p class="cn-kicker">{e(kicker)}</p><h1>{e(title)}</h1><p class="cn-deck">{e(deck)}</p>{credit}</header>'


def product_card(product, *, root=''):
    p = product
    first = p['rows'][0]
    fact = first['value']
    return f'''<article class="cn-product-card" data-product-category="{p['category']}" id="edit-{p['key']}">
<a class="cn-product-art" href="{root}{p['article']}" aria-label="Read about {e(p['name'])}"><span class="cn-product-type">{e(p['format'])}</span><img src="{root}assets/img/{p['illustration']}.svg" width="400" height="260" loading="lazy" alt="Generic {e(p['format'].lower())} format illustration, not a product photograph"><span class="cn-art-note">Format illustration · not to scale</span></a>
<div class="cn-product-copy"><p class="cn-brand">{e(p['brand'])}</p><h3><a href="{root}{p['article']}">{e(p['name'])}</a></h3><p>{e(p['description'])}</p>
<div class="cn-product-fact"><span>{e(first['label'])}</span>{source(first['source'],fact)}</div>
<div class="cn-card-actions"><a href="{root}{p['article']}">Explore the details <span aria-hidden="true">→</span></a><div>{product_cta(p)}<span class="cn-paid">Amazon · paid link</span></div></div></div></article>'''


def guide_cards(*, root='', limit=None):
    return '<div class="cn-guide-grid">'+''.join(
        f'<a class="cn-guide" href="{root}guides/{g["slug"]}.html"><span class="cn-guide-num">0{i}</span><p class="cn-kicker">{e(g["category"])}</p><h3>{e(g["short"])}</h3><p>{e(g["description"])}</p><span class="cn-guide-arrow">Read the guide <span aria-hidden="true">↗</span></span></a>'
        for i,g in enumerate(GUIDES[:limit],1))+'</div>'


def scope_note(root=''):
    return f'<p class="cn-scope">This edit describes the observed destinations of the five submitted links, not owner-confirmed product intent. Account-level attribution checks are still open. Prices and availability are checked on Amazon; no price or star rating is reproduced here. <a href="{root}workroom.html#intent">Link & intent status</a> · <a href="{root}about.html">How we work</a>.</p>'


def home():
    cards = ''.join(product_card(p) for p in PRODUCTS)
    body = f'''<section class="cn-hero cn-wrap"><div><p class="cn-kicker">The countertop edit · Autumn / Winter 2026</p>
<h1>Good food starts<br>with a <em>better<br>question.</em></h1>
<p class="cn-deck">A bigger basket or a smaller oven? A quick temperature check or wireless monitoring? Find the kitchen gear that fits the way you actually cook.</p>
<div class="cn-buttons"><a class="cn-button" href="#the-edit">Explore the kitchen edit <span aria-hidden="true">↗</span></a><a class="cn-text-link" href="guides/basket-or-oven.html">Start with the buying guide</a></div>
<p class="cn-hero-meta">Thoughtful comparisons. Clear trade-offs. No pretend testing.</p></div>
<figure class="cn-hero-media"><img class="cn-hero-photo" src="assets/img/autumn-kitchen.webp" width="1200" height="896" fetchpriority="high" alt="Conceptual still life of roasted autumn vegetables, lemon and linen on a kitchen counter"><div class="cn-hero-stamp"><span>LESS GUESSWORK</span>Make room for<br>what matters.</div><figcaption>AI-generated food illustration · not product photography or a test result</figcaption></figure></section>
<div class="cn-values cn-wrap"><div><b>01</b><p><strong>Start with your kitchen</strong>Not a list of must-have gadgets.</p></div><div><b>02</b><p><strong>Understand the trade-offs</strong>Format, space and everyday care.</p></div><div><b>03</b><p><strong>Choose on your terms</strong>The details, without the hype.</p></div></div>
<section class="cn-section cn-wrap" id="the-edit"><div class="cn-section-head"><div><p class="cn-kicker">The considered shortlist</p><h2>Five products. A place to start.</h2><p>Three air-fryer formats and two ways to check the cook. Compare the details that matter to you.</p></div>
<div class="cn-filters" role="group" aria-label="Filter the product edit"><button type="button" data-filter="all" aria-pressed="true">The whole edit</button><button type="button" data-filter="air-fryers" aria-pressed="false">Air fryers</button><button type="button" data-filter="thermometers" aria-pressed="false">Thermometers</button></div></div>
<div class="cn-product-grid" data-product-grid>{cards}</div><p class="cn-save-status" data-product-status role="status" aria-live="polite"></p>{scope_note()}</section>
<section class="cn-guides-band"><div class="cn-section cn-wrap"><div class="cn-section-head"><div><p class="cn-kicker">Before you add to basket</p><h2>Better questions. More useful answers.</h2><p>Buying guides for the decisions a feature list doesn’t make for you.</p></div><a class="cn-text-link" href="guides/index.html">All buying guides ↗</a></div>{guide_cards()}</div></section>
<section class="cn-section cn-chooser cn-wrap" id="start-here"><div><p class="cn-kicker">Find your starting point</p><h2>What’s on<br>your mind?</h2><p>You don’t need to compare everything at once. Start with the choice that would change your everyday cooking.</p></div><div class="cn-start-links"><a href="guides/basket-or-oven.html"><span>“I’m deciding between a basket and an oven.”<small>Compare the formats, not just the function count.</small></span><span aria-hidden="true">↗</span></a><a href="guides/cleanup-and-counter-space.html"><span>“My counter is already doing a lot.”<small>Check the footprint and cleanup questions first.</small></span><span aria-hidden="true">↗</span></a><a href="guides/thermometers.html"><span>“I want a clearer view of the cook.”<small>Explore a digital probe and a wireless probe bundle.</small></span><span aria-hidden="true">↗</span></a></div></section>
<section class="cn-section cn-follow cn-wrap"><div><p class="cn-kicker">Keep the good questions coming</p><h2>A quieter kind of kitchen inspiration.</h2><p>Follow new guides in your RSS reader. No inbox signup, no made-up trends. New topics stay proposals until there’s a useful question and evidence to answer it.</p></div><a class="cn-button" href="feed.xml">Follow the edit via RSS <span aria-hidden="true">↗</span></a></section>'''
    return page('index.html','Considered kitchen gear & useful buying guides','Explore air fryers, countertop ovens and kitchen thermometers through useful buying questions, clear trade-offs and source-linked product details.',body)


def spec_table(product, *, selected=None):
    rows = product['rows'] if selected is None else [product['rows'][i] for i in selected]
    cells = []
    for row in rows:
        value = e(row['value']) if row['value'] else f'<span class="cn-blank">—</span><small>Unverified · {e(row["reason"])}</small>'
        cites = source(row['source'])
        if row.get('also_source'):
            cites += '<br>'+source(row['also_source'])
        cells.append(f'<tr data-fact-source="{e(row["source"])}"><td>{e(row["label"])}</td><td>{value}</td><td>{cites}</td></tr>')
    return f'<div class="cn-table-wrap"><table class="cn-table"><caption>{e(product["name"])} · official statements checked {AS_OF}; claims are not independent test results.</caption><thead><tr><th scope="col">What to compare</th><th scope="col">Published detail</th><th scope="col">Official source</th></tr></thead><tbody>{"".join(cells)}</tbody></table></div>'


def guides_index():
    rel = 'guides/index.html'
    body = f'<div class="cn-wrap cn-pagebody">{pagehead("The guide shelf","Start with a useful question.","Practical comparisons for the kitchen you have, not a shopping list for a kitchen you don’t.")}{guide_cards(root="../")}<section class="cn-section"><h2>Browse the edit</h2><div class="cn-related"><a href="basket-air-fryers.html"><small>Air fryers</small>Basket formats</a><a href="air-fryer-ovens.html"><small>Countertop ovens</small>French-door format</a><a href="thermometers.html"><small>Temperature tools</small>Digital & wireless probes</a><a href="method.html"><small>Our approach</small>Sources, authorship & limits</a></div></section><p class="cn-scope">New guides published 19 November 2026. Working questions are editorial hypotheses, not claims about search volume or popularity. <a href="../workroom.html#cadence">Publishing cadence & measurement gates</a>.</p><details class="cn-legacy"><summary>Earlier guide archive · original dates and scope apply</summary><p><a href="../marketing/topics/index.html">Earlier topic guides</a> · <a href="../journal/index.html">Journal archive</a></p></details></div>'
    return page(rel,'Kitchen buying guides', 'Four useful buying questions about air-fryer format, capacity, counter space and multi-function appliances.',body)


def category(slug):
    configs = {
        'basket-air-fryers': ('Air fryers','The basket question.','Compare two independent baskets with one larger basket. Neither layout is a universal winner; the useful choice starts with your usual batch.', ['P1','P3']),
        'air-fryer-ovens': ('Countertop ovens','Make room for the oven format.','A French-door countertop oven is a different layout from a drawer-style air fryer. Check its stated dimensions and exact model before counting functions.', ['P2']),
        'thermometers': ('Kitchen thermometers','A spot check or a connected cook?','Two temperature-tool formats from the submitted listings. Listing claims are not independent accuracy, range or durability tests.', ['P4','P5']),
    }
    if slug == 'buying-guides':
        return page('guides/buying-guides.html','Question-led kitchen buying guides','Choose a practical starting point for your kitchen comparison.',f'<div class="cn-wrap cn-pagebody">{pagehead("Buying guides","Ask the question before choosing the product.","Format, capacity, footprint and functions: four focused places to begin.")}{guide_cards(root="../")}</div>')
    if slug == 'method':
        return method_page()
    label, title, deck, keys = configs[slug]
    cards = ''.join(product_card(BY_KEY[k],root='../') for k in keys)
    facts = ''.join(spec_table(BY_KEY[k]) for k in keys)
    body = f'<div class="cn-wrap cn-pagebody">{pagehead(label,title,deck)}<div class="cn-product-grid">{cards}</div>{scope_note("../")}<section class="cn-section cn-reading"><h2>The details, side by side with their sources.</h2><p>These tables reproduce only the small set of official statements checked for this edit. Unresolved values stay blank. Read the manufacturer’s current instructions for safe use and exact-variant requirements.</p>{facts}</section><a class="cn-button" href="index.html">Browse the buying guides ↗</a></div>'
    return page('guides/'+slug+'.html',label+' · the kitchen edit',deck,body)


def method_page():
    text = f'''<div class="cn-wrap cn-pagebody">{pagehead('The research method','Useful details. Honest limits.','A source-backed buying edit, not a claim that we cooked with or tested these products.')}
<div class="cn-reading-grid"><article class="cn-reading"><h2>What an official source can tell you</h2><p>It can establish what a manufacturer or listing says on a particular date. It cannot turn a claimed response time into an independent test, resolve an owner’s product intent, or tell us which product a reader will prefer.</p><h2>What happens when sources disagree?</h2><p>We preserve both observations and leave a single normalized value unverified. For example, Chefman’s page states 400°F for its stainless-steel model while the observed Amazon title says 450°F Hi-Fry. {source('chefman_single')} · {source('amazon_p3')}.</p><h2>Why no price, stars or “best overall” score?</h2><p>No licensed live catalog feed, independent product test or authorized conversion report is connected here. This publication chooses not to reproduce static prices or ratings and does not invent a ranking from them. Amazon’s rules place conditions on Program Content, price display and review use. {source('policies')}.</p><h2>Who wrote this?</h2><p>{e(DATA['author_note'])} The organization byline identifies this project’s research desk; it is not a fictional human reviewer. <a href="../about.html">Read the authorship statement</a>.</p><h2>What still needs confirmation?</h2><p>The intended ASIN for each submission, enrolled account eligibility, attribution reports, source conflicts and production measurement hosting. <a href="../questions.html">Open the questions register</a> for what is known, what is not and how to find out.</p></article><aside class="cn-side"><h2>Before you buy</h2><p>Match the current listing’s exact model and variant to the manufacturer’s instructions.</p><a href="../workroom.html#intent">Link & intent status</a><a href="../flagged.html">Flagged for Review</a><a href="index.html">Buying guides</a></aside></div></div>'''
    return page('guides/method.html','How Counter Notes researches products','The source, authorship and verification limits behind the Counter Notes buying edit.',text)


def guide_article(slug):
    g = next(x for x in GUIDES if x['slug']==slug)
    sections = {
        'basket-or-oven': '''<h2>Start with the opening, not the preset count.</h2><p>The layout is the first comparison worth making: two separate baskets, one basket, or French doors. Chefman describes independent baskets and a Sync Finish setting on its dual-window model; Emeril describes an oven-style French-door appliance. {dual} · {oven}.</p><div class="cn-callout"><p><strong>Our editorial starting point:</strong> Picture the meal you usually make. Do you want separate containers for two dishes, a single drawer for one batch, or an oven-style space? That question narrows the comparison without pretending there is one best format.</p></div><h2>Use the published details to check that first choice.</h2><p>The tables below show the capacities and layouts stated on the official pages. A larger quoted volume is not an independent cooking-performance result, and the formats are not interchangeable simply because each can air fry.</p><h2>Ask before buying</h2><ul><li>Is the exact listing the basket/door format you mean to buy?</li><li>Where will the appliance sit, and what does its matching manual require around it?</li><li>Are the removable parts and their care instructions suitable for your routine?</li></ul><p>These are decision prompts, not a tested verdict. If a specification is essential, check the exact current variant rather than choosing the more attractive number in a conflicting headline.</p>''',
        'air-fryer-capacity': '''<h2>Separate combined capacity from the space in one basket.</h2><p>The dual-basket Chefman is described as 6 Qt combined, with two independent 3 Qt baskets in the Amazon title. Chefman’s stainless-steel page separately lists an 8 Qt variant. Those are different layouts, not two ways of describing the same chamber. {dual} · {dual_listing} · {single}.</p><div class="cn-callout"><p><strong>The no-hype checklist:</strong> Record the total capacity, the number of containers, the exact variant and any stated usable internal dimensions. If the last field is not established by the checked source, leave it blank instead of converting quarts into a guessed portion count.</p></div><h2>Do not invent a household-size formula.</h2><p>This guide does not assign a number of servings to a quart figure. No practical portion test was performed here. Match the container shape to the foods and portions you actually plan to cook, using the manufacturer’s instructions for the exact model.</p><h2>Check these before adding to basket</h2><ul><li>Is the quoted capacity total, per basket or for a different variant?</li><li>Does your usual food need one continuous space or separate containers?</li><li>Can you obtain the usable dimensions if a particular dish must fit?</li><li>Have you also checked the appliance footprint and required clearance?</li></ul><p>The official capacity statements are below. They are a starting point for the comparison, not an assertion that a particular family should buy a particular product.</p>''',
        'cleanup-and-counter-space': '''<h2>Write down the space you have first.</h2><p>Emeril publishes its appliance dimensions as 16.9 inches deep, 15.8 inches wide and 14.8 inches high. Chefman publishes the two basket models’ dimensions in its own stated order. Keep that order with the source instead of silently assigning width/depth labels the page does not use. {oven} · {dual} · {single}.</p><div class="cn-callout"><p><strong>Our practical check:</strong> Measure the intended location, then consult the exact model’s manual for ventilation and opening requirements. The external appliance footprint is not the same as a verified safe installation envelope.</p></div><h2>Read care instructions at the part level.</h2><p>Chefman calls the dual-window baskets nonstick and dishwasher-safe; its stainless-steel page calls the basket top-rack dishwasher-safe. Those statements concern the named parts. They do not establish that an entire appliance is dishwasher-safe. {dual} · {single}.</p><h2>Questions worth settling now</h2><ul><li>What room is required for the door or basket to open?</li><li>What clearance does the matching current manual specify?</li><li>Which exact removable parts are covered by the care claim?</li><li>Will you still want the appliance there after cooking and cleanup?</li></ul><p>We have not performed a cleaning-time or counter-clearance test. Required ventilation values and actual cleanup times are not filled in from an appliance’s dimensions or a marketing adjective.</p>''',
        'multi-function-appliances': '''<h2>Start with a job you need done.</h2><p>Emeril’s official product page presents an oven with multiple cooking modes. It also contains different preset counts: 25 in a specification tile and 24 in its description; the observed Amazon title says 24. This guide does not choose one number or treat a larger count as proof of better cooking. {oven} · {oven_listing}.</p><div class="cn-callout"><p><strong>Our editorial rule:</strong> Make a short list of cooking tasks you genuinely want to add. Compare those with the named modes and the instructions for the exact model, rather than shopping by the longest feature list.</p></div><h2>Confirm the variant, not just the product family.</h2><p>The observed Chefman 8 Qt Amazon title advertises a 450°F Hi-Fry option while the manufacturer’s stainless-steel product page states a 400°F maximum. Until the exact variant/manual is established, that is a conflict to investigate, not a number to average. {single} · {single_listing}.</p><h2>Ask these four questions</h2><ul><li>Which named modes would I actually use?</li><li>Does the exact variant include the accessory required for my intended task?</li><li>What equipment would it genuinely replace in my own kitchen?</li><li>Do the capacity, opening and care requirements still fit my space and routine?</li></ul><p>No cooking-quality, running-cost, replacement-savings or revenue claim follows from the mode count. Where that evidence has not been collected, a useful comparison stops short of a made-up answer.</p>'''
    }
    prose = sections[slug].format(dual=source('chefman_dual'),dual_listing=source('amazon_p1'),single=source('chefman_single'),oven=source('emeril'),oven_listing=source('amazon_p2'),single_listing=source('amazon_p3'))
    selected = [0,1] if slug in {'basket-or-oven','air-fryer-capacity'} else None
    tables = ''.join(spec_table(BY_KEY[k],selected=selected) for k in g['keys'])
    others = ''.join(f'<a href="{x["slug"]}.html"><small>{e(x["category"])}</small>{e(x["short"])}</a>' for x in GUIDES if x['slug']!=slug)
    body = f'''<div class="cn-wrap cn-pagebody"><a class="cn-back" href="index.html">← Buying guides</a>{pagehead(g['category'],g['title'],g['description'],byline=True)}<div class="cn-reading-grid"><article class="cn-reading">{prose}<h2>The official statements behind the comparison</h2>{tables}<h2>Keep the decision grounded.</h2><p>No hands-on product test, price comparison or popularity study was performed. Product names refer to observed link destinations, not confirmed owner intent. Read the current product instructions and resolve any essential specification conflict before buying.</p><h2>Read next</h2><div class="cn-related">{others}</div></article><aside class="cn-side"><h2>In this edit</h2>{''.join(f'<a href="../{BY_KEY[k]["article"]}">{e(BY_KEY[k]["name"])}</a>' for k in g['keys'])}<p>Research checked {AS_OF}. Listing and manufacturer statements are attributed, not independently tested.</p><a href="method.html">Our research method</a></aside></div></div>'''
    return page('guides/'+slug+'.html',g['title'],g['description'],body,article=True)


def product_article(key):
    p = BY_KEY[key]
    category_path = 'thermometers' if p['category'] == 'thermometers' else ('air-fryer-ovens' if key == 'P2' else 'basket-air-fryers')
    category_label = 'Kitchen thermometers' if p['category'] == 'thermometers' else 'Air-fryer formats'
    body = f'''<div class="cn-wrap cn-pagebody"><a class="cn-back" href="../../guides/{category_path}.html">← {category_label}</a>{pagehead(p['format'],p['name'],p['description'],byline=True)}<div class="cn-reading-grid"><article class="cn-reading"><p class="cn-kicker">The useful distinction</p><h2>{e(p['angle'])}</h2><p>{e(p['tradeoff'])}</p><p>The details below are attributed to the official manufacturer or Amazon pages, checked {AS_OF}. They describe published statements, not performance measured by this publication.</p>{spec_table(p)}<h2>Before choosing this format</h2><ul><li>Match the exact model, included accessories and relevant installation or connectivity requirements to the current instructions.</li><li>Use the product’s operating instructions for safe setup, temperature limits and cleaning.</li><li>Do not treat an advertising accuracy, speed, capacity or range claim as an independent practical test.</li></ul><div class="cn-notice">This listing is an observed destination of a submitted link. Intended product confirmation and account-level affiliate attribution checks remain open. No price, star rating, tested winner or purchase outcome is claimed.</div><div class="cn-buttons">{product_cta(p,label='View current listing',cls='cn-button')}<span class="cn-paid">Amazon · paid link · price and availability set there</span></div></article><aside class="cn-side"><h2>Compare the format</h2><img src="../../assets/img/{p['illustration']}.svg" width="400" height="260" alt="Generic appliance or tool format illustration; not this product’s photograph"><p>Original format illustration. Not to scale, and not product photography.</p><a href="../../guides/{category_path}.html">Compare the formats</a><a href="../../about.html">Research & authorship</a></aside></div></div>'''
    return page(p['article'],p['name']+' · a research-based look',p['description'],body,article=True)


def legacy(kind):
    parts=[]
    for row in OLD_BOARD[kind]:
        title = row.get('title',row.get('question',''))
        parts.append(f'<article class="cn-question" id="{e(row["id"])}"><span class="cn-proposal-id">{e(row["id"])} · archived 16 November 2026</span><h2>{e(title)}</h2><p>Historical proposal/question; not a current implementation status. <a href="board/index.html">Retained decision archive</a>. The current status and open gates are listed above.</p></article>')
    return '<details class="cn-legacy"><summary>Earlier review references · retained anchors, original dates apply</summary>'+''.join(parts)+'</details>'


def suggestions():
    cards=[]
    for s in DATA['suggestions']:
        options=[]
        for opt in s['options']:
            recommended='<span class="cn-recommended">Suggested path · not selected</span>' if opt['id']==s['recommendation'] else ''
            options.append(f'<label class="cn-option">{recommended}<input type="radio" name="{s["id"]}" value="{opt["id"]}" data-decision-option><strong>{e(opt["label"])}</strong><small>{e(opt["detail"])}</small></label>')
        cards.append(f'''<article class="cn-proposal" id="{s['id']}" data-proposal><span class="cn-proposal-id">{s['id']} · {s['priority']}</span><div class="cn-proposal-head"><h2>{e(s['title'])}</h2><span class="cn-status">{e(s['state'])}</span></div><p><strong>What we know.</strong> {e(s['known'])}</p><p><strong>Still needed.</strong> {e(s['missing'])}</p><fieldset class="cn-options"><legend>Review the paths · neither is preselected</legend>{''.join(options)}</fieldset><div class="cn-proposal-meta"><span><strong>Effort:</strong> {e(s['effort'])}</span><span><strong>Risk:</strong> {e(s['risk'])}</span><span><strong>Official reference:</strong> {source(s['source'])}. This supports the criterion, not an implementation claim or the effort estimate.</span><span><strong>Implementation:</strong> Not applied by this board. A saved selection is a review draft only.</span></div></article>''')
    body = f'''<div class="cn-wrap cn-pagebody">{pagehead('Workroom · suggestions','Choose the next step. Before changing the site.','Six proposals with options, knowns, missing information, risk and a suggested path. Nothing is selected for you and nothing here deploys a change.')}
<div class="cn-notice">This review tool saves only when you choose “Save review draft”. Drafts stay in this browser; they are not shared, do not approve publication and are not analytics. Export the draft to retain a dated review record. Avoid personal information.</div>
<div class="cn-review-tools"><span><b>{len(DATA['suggestions'])} proposals</b> · recommendations are not approvals</span><div class="cn-buttons"><button class="cn-button" type="button" data-save-decisions>Save review draft</button><button class="cn-text-link" type="button" data-export-decisions>Export JSON</button><button class="cn-text-link" type="button" data-reset-decisions>Clear draft</button></div><span class="cn-save-status" data-decision-status role="status" aria-live="polite">No implementation action is connected.</span></div>
{''.join(cards)}<p class="cn-scope"><a href="questions.html">What information is still missing?</a> · <a href="workroom.html#cadence">Publishing cadence</a> · <a href="workroom.html#design-prompt">Design prompt for the next iteration</a></p>{legacy('suggestions')}</div>'''
    return page('suggestions.html','Suggestions & review decisions','Review six improvement proposals, compare options, save an optional local draft and export it without applying changes.',body)


def questions():
    cards=''.join(f'''<article class="cn-question" id="{q['id']}"><span class="cn-proposal-id">{q['id']} · OPEN / UNVERIFIED</span><h2>{e(q['question'])}</h2><dl><dt>Already known</dt><dd>{e(q['known'])}</dd><dt>Still missing</dt><dd>{e(q['missing'])}</dd><dt>Confirmed answer</dt><dd><span class="cn-blank">—</span> <small>Unverified; not filled from an observation or assumption.</small></dd><dt>How to discover it</dt><dd>{e(q['discover'])}</dd><dt>Official reference</dt><dd>{source(q['source'])} · a criterion, not proof that the missing information exists.</dd></dl></article>''' for q in DATA['questions'])
    body=f'<div class="cn-wrap cn-pagebody">{pagehead("Workroom · questions","What can we reasonably decide?","Start with the information we have. Keep unanswered fields blank. Name the missing evidence and the action that can obtain it before choosing a path.")}<p class="cn-scope">Updated {AS_OF}. All {len(DATA["questions"])} current answers remain unverified. Account-only actions are recorded for authorized follow-up, not falsely marked complete.</p>{cards}<p><a class="cn-text-link" href="suggestions.html">Review the suggestions ↗</a></p>{legacy("questions")}</div>'
    return page('questions.html','Questions, knowns & missing information','Seven current questions with known information, missing evidence, blank confirmed answers and a concrete discovery step.',body)


def about():
    body=f'''<div class="cn-wrap cn-pagebody">{pagehead('Our approach','A considered edit, not a catalogue of superlatives.','Counter Notes is an independent kitchen buying-guide project. Its job is to make the next question easier to answer, not to manufacture certainty.')}<div class="cn-reading-grid"><article class="cn-reading"><h2 id="authorship">Who is behind the words?</h2><p>{e(DATA['author_note'])} “{e(DATA['author'])}” is an organization byline for this project, not a fictional person, a certification or a claim of culinary expertise.</p><p>AI assists with organizing sources, drafting and reproducible site building. A published source-linked statement shows what an official page says, not an independent finding about real-world performance. An accountable human editor and firsthand test records have not been supplied; that gap remains on the <a href="questions.html#CN-Q06">questions register</a>.</p><h2>What makes the shortlist?</h2><p>The five products in this edit are the observed destinations of the five Amazon links supplied in the project brief. They were not selected by an invented popularity, commission, “best seller” or conversion score. Intended-product confirmations are still blank.</p><h2 id="affiliate">How the affiliate relationship works</h2><p><strong>{DISCLOSURE}</strong> When you follow a link marked “paid link” and make a qualifying purchase, a commission may be earned. Amazon sets the price, availability and order terms. This is an independent publication, not Amazon’s store or an Amazon-endorsed service. {source('agreement')}.</p><p>The configured tracking ID is <code>{ASSOCIATES_TAG}</code>. A correctly formatted URL is not confirmation of enrolled account eligibility or successful attribution. One link per product still needs destination and tracking-report validation in the enrolled workflow. {source('policies')}.</p><h2>What we do not claim</h2><p>No hands-on tests, product-use experience, star ratings, static prices, actual conversion results, profitable niches or future revenue are asserted by this edit. We do not call a topic trending without dated demand evidence. The <a href="guides/method.html">research method</a> explains the limits.</p><h2>Images and illustrations</h2><p>The food still life is AI-generated conceptual imagery, not food prepared in a product test. Product-format drawings are original schematic illustrations, not photographs or exact representations of the named models. No Amazon product image is copied into this design.</p><h2>Corrections and editorial decisions</h2><p>Source disagreements and missing evidence are kept in the public <a href="flagged.html">Flagged for Review</a> area. Proposed improvements go to the <a href="suggestions.html">review board</a> before any additional implementation. The repository’s <a href="https://github.com/kanlerxz87-cyber/Zone2/issues">issue tracker</a> is available for corrections; do not include account credentials or personal order information.</p></article><aside class="cn-side"><h2>Open by design</h2><a href="guides/method.html">The research method</a><a href="workroom.html#sources">Sources checked for this edit</a><a href="privacy.html">Privacy & measurement</a><a href="feed.xml">Follow the RSS feed</a></aside></div></div>'''
    return page('about.html','About the publication, authorship & affiliate disclosure','How Counter Notes uses AI-assisted source research, labels its limits and discloses its affiliate links.',body)


def privacy():
    body=f'''<div class="cn-wrap cn-pagebody">{pagehead('Privacy & measurement','Measure the page. Not the person.','Implementation status checked 19 November 2026. This notice describes actual code and hosting boundaries, not a certification of legal compliance.')}<article class="cn-reading"><div class="cn-notice"><strong>Production status:</strong> The GitHub Pages site has no connected analytics collector. Its client configuration is disabled: no browser event is sent or queued for later collection. The self-hosted service is implemented and tested, not provisioned on a production host.</div><h2>What the self-hosted counter is designed to collect</h2><p>Once it is deliberately deployed and enabled, it counts page loads, direct product-link clicks and the disclosure strip entering at least half of a browser viewport. It stores a server-assigned UTC day, registered page path, event name and, where applicable, a static product key or disclosure position. These are raw event counts, not unique people, eligible Amazon Sessions or proof that someone read the disclosure.</p><p>The client sets no cookie, writes no analytics data to browser storage, generates no visitor/session identifier, sends no referrer or query string and does not fingerprint a device. It honors Global Privacy Control and Do Not Track. The application suppresses HTTP access logs and stores daily aggregates rather than individual requests. A host/reverse proxy may independently handle IP addresses; that must be configured and reviewed before production activation.</p><h2>Retention and delivery limits</h2><p>The implemented default is a rolling 90 days for event/report data. Purging runs on ingestion/export and via a documented scheduled command. The counter is best effort: blocked scripts, unavailable endpoints, opted-out browsers and filtering cause undercounts; sophisticated bots can cause overcounts. Origin checks and a global budget do not authenticate human visitors. No unique-session or conversion rate is inferred.</p><h2>Orders and searches are different data sources</h2><p>Purchase/order data can only enter through an authorized Associates export; query performance can only enter through an authorized Search Console export that has been reviewed for personal information. Browser events cannot claim either. Each import records the official source URL, channel, period, import time and SHA-256 of the supplied normalized file. No real export is available here. {source('policies')} · {source('search')}.</p><h2>The optional review draft</h2><p>The suggestions page stores choices in this browser only when “Save review draft” is pressed. Its key is <code>counter-notes-review-v1</code>. This functional storage is not analytics, is not sent to a server and does not approve a change. “Clear draft” removes it. Export produces a local JSON file. Do not enter personal information.</p><h2>GitHub and Amazon</h2><p>GitHub states that Pages logs visitor IP addresses for security, regardless of sign-in status. That hosting behavior is separate from this site’s own counter. {source('pages')}.</p><p>Amazon receives requests when you follow its links and applies its own policies. We do not collect your Amazon login, cart or order information. Product links remain direct; they are not silently opened or routed through an analytics redirect.</p><h2>Before collection is enabled</h2><p>Provision an owner-controlled HTTPS endpoint, review lawful basis/consent and the operator notice for the applicable jurisdictions, disable or appropriately manage host-level logs, verify retention and test persistence without production test clicks. A cookie-free design alone does not settle privacy-law obligations. <a href="suggestions.html#CN-S02">Review the hosting proposal</a>.</p></article></div>'''
    return page('privacy.html','Privacy, storage & measurement status','What the counter does and does not collect, its disabled GitHub Pages status, report provenance and optional review-draft storage.',body)


def intent_table():
    rows=''.join(f'<tr><td>{p["key"]}</td><td><a href="{p["submitted_url"]}" rel="sponsored nofollow noopener noreferrer" target="_blank">{e(p["submitted_url"].split("/")[-1])}</a></td><td class="cn-blank">—<small>Intended ASIN unverified</small></td><td class="cn-blank">—<small>Intent listing URL unverified</small></td><td class="cn-blank">—<small>Confirmation date/source unavailable</small></td><td><a href="{p["observed_redirect_target"]}" rel="sponsored nofollow noopener noreferrer" target="_blank"><code>{p["asin_observed"]}</code></a><small>Observed {p["observed_on"]}; not intent. {e(p["observation_note"])}</small></td></tr>' for p in PRODUCTS)
    return f'<div class="cn-table-wrap"><table class="cn-table cn-intent"><caption>Intent and redirect observations are separate fields in docs/publication.json. A short-link token is not declared invalid or treated as an ASIN. The last two submissions have inconsistent initial/repeat observations; the latest result is shown.</caption><thead><tr><th>Product</th><th>Submitted link</th><th>Intended ASIN</th><th>Confirmed listing</th><th>Confirmation</th><th>Observed destination · official listing</th></tr></thead><tbody>{rows}</tbody></table></div>'


def current_flags():
    flags=[('CN-F01','Intended products and account attribution are not confirmed.','The five observations are not owner intent. Tagged URL syntax is not an eligible-account or attributed-order report.','policies'),('CN-F02','Production analytics is not connected.','The self-hosted service is tested, but GitHub Pages cannot run it and no owner-controlled collector host is provisioned.','pages'),('CN-F03','No authorized conversion or query export exists here.','Keep clicks, eligible Sessions, reported orders, earnings and query-demand conclusions empty until evidence is imported.','search'),('CN-F04','Exact-variant specifications still conflict.','Chefman 8 Qt maximum-temperature statements disagree; Emeril’s own preset sections disagree. Do not choose a marketable number.','chefman_single'),('CN-F05','Authorship and product imagery are research-only.','No human-use credentials or hands-on test evidence has been supplied. Format diagrams and a labelled AI food scene are not product photographs.','ftc'),('CN-F06','Last-two link observations are inconsistent.','The initial and repeat exact-link fetch records on 19 November disagree. The repeat matches the historical ledger. No cause, stable routing, invalidity or owner intent is inferred; verify through the enrolled workflow.','policies')]
    rows=''.join(f'<tr id="{f[0]}"><td>{f[0]}</td><td><strong>{e(f[1])}</strong><small>{e(f[2])}</small></td><td>Needs review · non-blocking for the research publication</td><td>{source(f[3])}</td></tr>' for f in flags)
    return '<div class="cn-table-wrap"><table class="cn-table"><caption>Current integration flags · 19 November 2026. Official references explain the constraint; repository status is an implementation observation.</caption><thead><tr><th>ID</th><th>Issue & discovery/action needed</th><th>State</th><th>Official reference</th></tr></thead><tbody>'+rows+'</tbody></table></div>'


def workroom():
    status=[('Publication front page','Implemented','One buyer-first front door, five product cards, four focused guides and consistent navigation.','helpful'),('Affiliate disclosure & link markup','Implemented controls; not official approval','Disclosure under the masthead and in the footer. All outbound marketplace product links marked sponsored.','agreement'),('Product intent / account attribution','Unverified','Five observed destinations; all intent confirmations and first-party attribution reports remain unavailable.','policies'),('Measurement','Implemented / production blocked','Three public aggregate events plus two local report-import events. Static production config disabled.','pages'),('Search & outcomes','Unmeasured','No authorized Search Console or Associates export. No profitable-niche, conversion or revenue conclusion.','search')]
    rows=''.join(f'<tr><td>{e(a)}</td><td>{e(b)}</td><td>{e(c)}</td><td>{source(d)}</td></tr>' for a,b,c,d in status)
    srcrows=''.join(f'<tr><td>{e(k)}</td><td>{source(k)}<small>Fetched {e(s["checked_on"])}</small></td><td>{e(s["quote"])}</td></tr>' for k,s in DATA['sources'].items())
    links=''.join(f'<a href="{href}">{e(label)}</a>' for href,label in OPERATOR_LINKS if href!='workroom.html')
    c=DATA['cadence']
    body=f'''<div class="cn-wrap cn-pagebody">{pagehead('The Workroom','A clear front door. An open back room.','The current executive summary, questions, review proposals and evidence—kept separate from the buyer’s reading experience. No account-only action is marked complete without evidence.')}
<section id="summary"><p class="cn-kicker">Executive summary · {AS_OF}</p><div class="cn-table-wrap"><table class="cn-table"><caption>Status is measured from this implementation; the official references state the relevant criteria, not a third-party approval.</caption><thead><tr><th>Area</th><th>Current state</th><th>Important detail</th><th>Official reference</th></tr></thead><tbody>{rows}</tbody></table></div></section>
<div class="cn-workroom-grid"><a class="cn-workroom-card" href="suggestions.html"><span>REVIEW FIRST</span><h2>Suggestions & paths</h2><p>Compare options, risks and missing evidence. Save an optional review draft; nothing auto-applies.</p></a><a class="cn-workroom-card" href="questions.html"><span>KNOWNS / UNKNOWNS</span><h2>Questions to settle</h2><p>Blank answers, named information gaps and practical discovery steps.</p></a><a class="cn-workroom-card" href="privacy.html"><span>IMPLEMENTED ≠ CONNECTED</span><h2>Measurement status</h2><p>What the five events can record, what is tested and what still needs authorized access.</p></a></div>
<section class="cn-section cn-reading" id="flags"><h2>Flagged for Review · current integration</h2>{current_flags()}<p><a href="flagged.html">Full retained flagged register</a>. Earlier records keep their original dates and are not silently called fresh verifications.</p></section>
<section class="cn-reading" id="intent"><h2>Five links. Two separate questions.</h2><p>What a link opened is an observation. What the owner intended is a confirmation record. The intended ASIN, official intent listing, date and source remain blank for every submission. The exact compliance status of the supplied short links is unresolved; none is declared invalid. The owner’s configured tag is <code>{ASSOCIATES_TAG}</code>. The original unresolved short-link compliance question is retained at <a href="https://kanlerxz87-cyber.github.io/Zone3/flagged.html#FLG-003">Zone3 · FLG-003</a>; that historical review is not an official Amazon determination.</p>{intent_table()}<p>Before scaling, validate one Special Link per intended product in the enrolled Associates workflow and confirm destination and the authorized tracking report. Do not make self-purchases, simulate shoppers or infer orders from our click counter. {source('policies')}.</p></section>
<section class="cn-section cn-reading" id="cadence"><h2>A cadence with a stop button.</h2><p><strong>{e(c['status'])}.</strong></p><p>{e(c['weekly'])}</p><div class="cn-callout"><p>{e(c['publish_gate'])}</p></div><p>{e(c['monthly'])}</p><p>{e(c['topic_rule'])} {source('helpful')} · {source('search')}.</p></section>
<section class="cn-reading" id="design-prompt"><h2>A useful prompt for the next design iteration.</h2><div class="cn-callout"><p>Design Counter Notes as an independent kitchen publication, not a compliance dashboard. Keep a warm ivory canvas, deep green typography, restrained terracotta accents, generous space and a serif/sans editorial hierarchy. Lead with a product-intent question, an honest shortlist and useful buying guides. Keep the disclosure directly under the masthead and in the footer. Use original/licensed imagery or clearly labelled conceptual illustrations. Never invent a human reviewer, first-hand experience, price, rating, trend or performance score. Keep all research dashboards under one Workroom navigation group. Suggestions need options, risks, missing evidence and a review draft—not an automatic deploy button. Expand only after measured reader queries and authorized reports justify the next topic.</p></div><p>This is a design recommendation, not evidence of market demand. {source('helpful')}.</p></section>
<section class="cn-section" id="sources"><h2>Official sources checked for this edit</h2><div class="cn-table-wrap"><table class="cn-table"><caption>A fresh check is limited to the statements actually read. Older research remains dated in its own registers.</caption><thead><tr><th>Reference</th><th>Official page & check date</th><th>Statement read / verification scope</th></tr></thead><tbody>{srcrows}</tbody></table></div></section>
<section id="tools"><h2>All tools & retained research</h2><p class="cn-scope">These pages remain reachable for review. Earlier dashboards are retained records, not competing publication homepages or fresh account-level verifications.</p><label for="tool-search" class="cn-search-label">Find an operator area</label><input id="tool-search" class="cn-search" type="search" placeholder="Try “tracking”, “source” or “decision”" data-tool-search><nav class="cn-directory" data-tool-directory aria-label="All operator areas">{links}</nav><p class="cn-save-status" role="status" data-tool-status></p></section></div>'''
    return page('workroom.html','Workroom · executive summary, decisions & evidence','Current executive summary, source register, five-product intent records, review flags, publishing cadence and all operator tools.',body)


def feed():
    items=[]
    for g in GUIDES:
        url=BASE+'guides/'+g['slug']+'.html'
        pub=format_datetime(datetime.fromisoformat(AS_OF).replace(tzinfo=timezone.utc))
        items.append(f'<item><title>{xml_escape(g["title"])}</title><link>{url}</link><guid isPermaLink="true">{url}</guid><pubDate>{pub}</pubDate><description>{xml_escape(g["description"])}</description></item>')
    # Preserve subscriptions to the eight previously shipped guides with original date.
    old=json.loads((ROOT/'marketing/data/editorial.json').read_text())
    for g in old['guides']:
        url=BASE+'marketing/topics/'+g['slug']
        pub=format_datetime(datetime.fromisoformat(old['as_of']).replace(tzinfo=timezone.utc))
        items.append(f'<item><title>{xml_escape(g["title"])}</title><link>{url}</link><guid isPermaLink="true">{url}</guid><pubDate>{pub}</pubDate><description>{xml_escape(g["hook"])}</description></item>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>Counter Notes · the kitchen edit</title><link>'+BASE+'</link><description>Considered kitchen gear and useful buying questions.</description><language>en</language><atom:link href="'+BASE+'feed.xml" rel="self" type="application/rss+xml"/>'+''.join(items)+'</channel></rss>\n'


TARGETS = {
    'index.html': home, 'suggestions.html': suggestions, 'questions.html': questions,
    'guides/index.html': guides_index, 'about.html': about, 'privacy.html': privacy, 'workroom.html': workroom,
    **{f'guides/{slug}.html': (lambda s=slug: category(s)) for slug in ['basket-air-fryers','air-fryer-ovens','buying-guides','thermometers','method']},
    **{f'guides/{g["slug"]}.html': (lambda s=g['slug']: guide_article(s)) for g in GUIDES},
    **{p['article']: (lambda k=p['key']: product_article(k)) for p in PRODUCTS},
    'feed.xml': feed,
}
