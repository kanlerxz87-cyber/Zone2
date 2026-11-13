# Zone2 — Amazon affiliate research platform

Three views of the same assignment, built by three sessions working in parallel and integrated here.
**One rule across all of them:** nothing is asserted without an official source, and where a value cannot be
confirmed it is left blank and flagged rather than filled in.

**Live site:** <https://kanlerxz87-cyber.github.io/Zone2/>

> As an Amazon Associate I earn from qualifying purchases.

---

## The three views

| Path | What it is | Built by |
|---|---|---|
| `/index.html` | **Northstar dashboard** — overview, product research, content studio, optimization, compliance, flagged review. Hash navigation, no build step, no dependencies. | `arena/6b8bb130-zone2` |
| `/start.html` → `/overview.html` | **Affiliate Research Hub** — generated hub with per-product attribute rows traced to official Amazon or manufacturer pages, plus the full brief-disposition matrix. | `arena/6602723a-zone2` |
| `/pages/index.html` | **Findings & platform subpages** — 37 generated pages: executive summary, per-product ledger, one subpage per published Amazon commission band, 12 platform-module pages, compliance control ledger, verification log, source register, tracking/content/architecture pages, and the Flagged-for-Review queue. | `arena/f786c0d7-zone2` |

## The three requested products

`link.amazon/B04G1MEwY` · `link.amazon/B02NbDxp3` · `link.amazon/B00hJ57DV`

| Check | Result |
|---|---|
| Token length | **9 characters each** — an ASIN is 10, so none can address a catalog record |
| `amazon.com/dp/<token>` | **Page Not Found** for all three (verified 2026-11-13) |
| Short-link behaviour | each token landed on a **different, unrelated** `dp/` ASIN carrying `plpRedirect=mhFallback` |
| Reproducibility test | re-fetching one link returned the same `dp/` path but a **"Best Sellers in Kitchen & Dining" carousel** instead of a product page, with a different `btn_ref` shuffle token |

**Conclusion:** the destination is a shuffled fallback, not a token→product mapping, so the identity of the three
requested items is unresolved. The `product-B0*.html` pages in the hub document those ASINs accurately (each row
is sourced to the manufacturer's own page) but they are **not established as the items named in the brief** — see
flag **F-12** on `/pages/flags.html`. Fields that no official source states are blank on every view.

## Repository layout

```
index.html, app.js, data.js, styles.css   Northstar dashboard
*.html, assets/, site-manifest.json       generated verified hub (root-level pages)
pages/, pages/assets/site.css             generated subpages (37) - findings, categories, modules, flags

data/                                     the hub's dataset (products, compliance, requirements, sources)
ledger/                                   the subpages' dataset (products, commission table, rules, flags,
                                          verification log, niches, campaigns, sources)
docs/                                     hub executive summary and methodology
scripts/build.py, scripts/verify.py       hub generator + its guard
tools/                                    guard, Creators API client, scoring, content engine, link builder,
                                          click tracker, optimizer, cache, build_site.py, validate_data.py
tests/test_pipeline.py                    executable checks for every guard in tools/
content/templates/                         article / comparison / buying-guide templates
COORDINATION.md                           shared board, merge records, irregularities, verification log
```

Two data namespaces exist because two sessions built in parallel and their schemas differ; `ledger/` rows cite
`ledger/sources.json`, `data/` rows cite `data/sources.json`. Both are enforced by their own gate.

## Build and check locally

Python 3.9+ for the hub; 3.10+ for `tools/` (type-hint syntax). No third-party dependencies.

```bash
python3 scripts/build.py            # regenerate the verified hub (root pages)
python3 scripts/verify.py           # hub guard: unsourced rows, links, prices, disclosure
python3 tools/build_site.py         # regenerate pages/ from ledger/*.json (deterministic)
python3 tools/build_site.py --check # fail if committed pages/ are stale
python3 tools/validate_data.py      # subpage gate: per-row sourcing, blank-or-flagged, links, disclosure
python3 tests/test_pipeline.py      # 11 executable checks for the guards
python3 -m http.server 8080         # preview every view at http://localhost:8080
```

## What the verification enforces

**Hub (`scripts/verify.py`)** — a `verified`/`conflict` row without a source URL; a non-`https` or non-official
source; an `unverified` row carrying a published value; a broken internal link; a missing disclosure or trademark
attribution; any printed price (including bare figures from the audit snapshot).

**Subpages (`tools/validate_data.py`)** — every row must cite an allowlisted official host
(`affiliate-program.amazon.com`, `amazon.com`, `webservices.amazon.com`, `ftc.gov`, `developers.google.com`,
`support.google.com`, `docs.github.com`) or be blank **and** linked to a flag; no invented performance metrics;
no Amazon mark in the identifiers this project controls; the §5 disclosure sentence wherever a sponsored link
exists; no divergence from the dashboard's product rows; no broken internal links (1,164 checked).

## Economics, from Amazon's published statement

`ledger/commission_table.json` transcribes Table 1 row by row
([source](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ)): 10.00% Luxury Beauty /
Luxury Stores Beauty / Amazon Explore; 5.00% music, Handmade, digital video; 4.50% Physical Books, Kitchen,
Automotive; 4.00% devices/fashion/accessories; 3.00% the large home/toys/outdoors/pets cluster; 2.50% PC;
2.00% TVs; 1.00% grocery/health/console; 0.00% nine excluded groups; 4.00% All Other Categories. Attribution
mechanics wired into the model: 24-hour Session, 89-day cart path, 180-day ship-and-pay, ~60-day payment lag,
US minimums 10 / 10 (2,000 cap) / 100 USD (+15 USD check fee)
([Program Policies](https://affiliate-program.amazon.com/help/operating/policies)).

## Automation notes

`tools/amazon_creators_api.py` targets the **Creators API** — PA-API 5.0 is deprecated and returns
`403 AccessDenied` — and exits `BLOCKED` (never scraping) until an eligible Associates account exists
(prerequisite per Amazon: ≥10 qualifying sales in the past 30 days). `tools/scoring.py` returns
`INSUFFICIENT_DATA` rather than a default when an input is missing; `tools/generate_articles.py` refuses to
draft copy for an entry without a resolved identity; `tools/optimize.py` takes no action without ≥30 clicks
**and** a dated report; `tools/redirect_server.py` counts static campaign keys and stores no visitor
identifier, because associating a sub-tag with an end user is prohibited.

Policy pages cited here carry their own update dates (Agreement: 15 Oct 2025; Program Policies: 14 Apr 2026)
and change without notice — re-verify each cycle.
