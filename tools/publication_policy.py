"""Single indexing policy for the publication; archives are accessible, not index targets.

The user's instruction to give search engines one site authorizes this integration
choice. noindex is applied to the deployment projection, never silently to evidence.
Google: https://developers.google.com/search/docs/crawling-indexing/block-indexing
"""
INDEXED = {
    'index.html', 'about.html', 'privacy.html',
    'guides/index.html', 'guides/basket-air-fryers.html',
    'guides/air-fryer-ovens.html', 'guides/thermometers.html', 'guides/method.html',
    'guides/basket-or-oven.html', 'guides/air-fryer-capacity.html',
    'guides/cleanup-and-counter-space.html', 'guides/multi-function-appliances.html',
    'guides/products/chefman-dual-window.html', 'guides/products/emeril-french-door-360.html',
    'guides/products/chefman-turbofry-8qt.html', 'guides/products/thermomaven-digital.html',
    'guides/products/chef-iq-sense.html',
}
CURRENT_OPERATOR = {'workroom.html','suggestions.html','questions.html','intent.html','flagged.html','summary.html'}


def is_indexable(rel):
    return str(rel) in INDEXED
