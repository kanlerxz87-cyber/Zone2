# Northstar — AI-powered Amazon affiliate research platform

A source-verified affiliate intelligence workspace: a live dashboard, category subpages, a compliance engine,
and the automation that connects them. **Every table row links to an official source, or the value is left
blank and flagged. Nothing is inferred.**

**Live site:** https://kanlerxz87-cyber.github.io/Zone2/ ·
**Executive summary:** [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) ·
**Coordination & verification log:** [`COORDINATION.md`](COORDINATION.md)

## Start here

| Page | What it answers |
|---|---|
| [Landing dashboard](index.html) | Research snapshot, product queue, content pipeline, compliance, flags |
| [Findings hub](pages/index.html) | Every table, every flag, and the evidence behind each row |
| [Executive summary](pages/executive-summary.html) | What was verified, what was built, what is blocking the rest |
| [Requested products](pages/products.html) | The three items named in the brief, with each blank field explained |
| [Categories](pages/categories/index.html) | One subpage per published Amazon commission band (11) |
| [Niche discovery](pages/niches.html) | The sourced eligibility filter and why the ranking queue is empty |
| [Platform modules](pages/modules/index.html) | The 12 capabilities and the honest state of each |
| [Commissions](pages/commissions.html) | Published rates, bounties, attribution windows, payment terms |
| [Compliance](pages/compliance.html) | 20 program rules mapped 1:1 to the control that enforces them |
| [Verification log](pages/verification.html) | 30 checks: claim → method → official source → verdict |
| [Official sources](pages/sources.html) | Every document relied on, with access dates |
| [Flagged for review](pages/flags.html) | Unverified items and irregularities, with source links |

## The three requested products

`https://link.amazon/B04G1MEwY`, `https://link.amazon/B02NbDxp3`, `https://link.amazon/B00hJ57DV`

Each token is **9 characters** (an ASIN is 10), each `amazon.com/dp/<token>` returns **Page Not Found**, and
each short link redirected to a *different, unrelated* product through `plpRedirect=mhFallback`. Product
identity therefore cannot be established, so title, brand, category, price, availability, rating, review
count, competition and commission band are **blank and flagged** — never guessed. See
[Flagged for review](pages/flags.html) (F-01…F-06).

## Repository layout

```
index.html · app.js · data.js · styles.css   landing dashboard (hash-routed, no build step)
pages/                                       generated subpages: categories, modules, findings, flags
data/                                        source of truth: products, rates, rules, flags, sources, niches
tools/                                       guards, collector, scoring, generator, tracker, optimizer, build, validate
content/templates/                           article / comparison / buying-guide templates
tests/test_pipeline.py                       executable checks for every guard
.github/workflows/pages.yml                  validate -> publish to GitHub Pages
COORDINATION.md                              session board, verification log, conflict notes
```

## Tooling

```bash
python3 tools/build_site.py            # regenerate pages/ from data/*.json (deterministic, network-free)
python3 tools/build_site.py --check     # fail if committed pages/ are stale
python3 tools/validate_data.py          # deploy gate: per-row sourcing, blank-or-flagged, links, disclosure
python3 tests/test_pipeline.py          # 11 guard checks
PYTHONPATH=tools python3 tools/scoring.py
PYTHONPATH=tools python3 tools/amazon_creators_api.py   # prints BLOCKED until credentials exist
PYTHONPATH=tools python3 tools/generate_articles.py     # refuses unverified entries by design
```

`tools/amazon_creators_api.py` targets the **Creators API** (PA-API 5.0 is deprecated and returns
`403 AccessDenied`). Prerequisites per Amazon's docs: an Associates account for the target marketplace and at
least 10 qualifying sales in the past 30 days. With no credentials it exits `BLOCKED` — it does not scrape and
it does not substitute a value.

## Data and verification contract

Rows live in `data/*.json`. A row may only carry a value if it names a `source_ids` entry from
`data/sources.json`, whose host is allowlisted to
`affiliate-program.amazon.com`, `amazon.com`, `webservices.amazon.com`, `ftc.gov`,
`developers.google.com`, `support.google.com`, `docs.github.com`. `tools/validate_data.py` enforces this, plus:
no invented performance metrics, no Amazon mark in our own naming, disclosure wherever a sponsored link
exists, no divergence from the landing page's product rows, and no broken internal links.

All policy and rate data was read from the cited page on **2026-11-13**. Both governing pages carry update
dates (Agreement: Oct 15 2025; Program Policies: Apr 14 2026) and change without notice — re-verify per cycle.

## Affiliate disclosure

> As an Amazon Associate I earn from qualifying purchases.

This sentence is required by the Amazon Associates Program Operating Agreement (§5) and appears in the footer
of every page. Outbound links are qualified with `rel="sponsored"` per Google's guidance, and this project's
own name deliberately contains no Amazon mark, as the Participation Requirements require.

## Notes

The site is a static build (GitHub Pages) with no backend, no cookies, and no visitor identifiers; the click
tracker that ships with it counts static campaign keys only, because associating a sub-tag with a specific end
user is prohibited by the program. Prices and availability are intentionally never displayed as static text.
