# Zone2 — Amazon affiliate research & AI marketing platform

Four complementary, source-first deliverables for the same brief, built by four sessions in parallel and
integrated here. **One rule across all of them: nothing is asserted without an official source, and a value
that cannot be confirmed is left blank and flagged rather than filled in.**

**Live site:** <https://kanlerxz87-cyber.github.io/Zone2/> · start at `start.html`

> As an Amazon Associate I earn from qualifying purchases.

---

## The four views

| Entry point | What it is | Built by |
|---|---|---|
| `index.html` | **Northstar dashboard** — overview, product research, content studio, optimization, compliance, flagged review. Hash navigation, no build step, no dependencies. | `arena/6b8bb130-zone2` |
| `overview.html` (+ `products.html`, `compare.html`, `summary.html`, `requirements.html`, `methodology.html`, `flagged.html`, `product-*.html`) | **Verified Research Hub** — generated per-product attribute rows traced to official Amazon/manufacturer pages, plus the brief-disposition matrix. Guard: `scripts/verify.py`. | `arena/6602723a-zone2` |
| `zone2/` | **Zone2 platform dashboard** — multi-page platform build: dashboard, products, analysis, content, compliance, executive summary, flagged review, sources. | `arena/34836ddd-zone2` |
| `pages/index.html` | **Findings & platform subpages** — 37 generated pages: executive summary, per-product ledger, one page per published Amazon commission band, 12 module pages, compliance control ledger, 32-check verification log, source register, tracking/content/architecture pages, Flagged-for-Review queue. Guard: `tools/validate_data.py`. | `arena/f786c0d7-zone2` |

## The three supplied products — and the disagreement about them

`https://link.amazon/B04G1MEwY` · `https://link.amazon/B02NbDxp3` · `https://link.amazon/B00hJ57DV`

**What every session verified identically:** each embedded code is **9 characters** (Amazon defines an ASIN as a
unique **10-character** alphanumeric identifier), and `https://www.amazon.com/dp/<code>` returns Amazon's *Sorry!
We couldn't find that page* for all three.

**Where the views diverge, and the evidence that settles it:**

| Claim | Basis |
|---|---|
| Hub / `zone2/`: the short links resolve to `B0CDY277D3`, `B09B7SB46R`, `B08DKYBTPH`, which are documented product by product with manufacturer-sourced rows. | the redirect does land on those `/dp/` paths |
| `pages/`: that resolution is **not** an identity — those ASINs are fallback destinations, not the items named in the brief. | every redirect carries `plpRedirect=mhFallback` + `lv=shuf`; the three tokens land on three *different* unrelated products; and a **repeat fetch of the same link on the same day returned the same path with a completely different page body** — a "Best Sellers in Kitchen & Dining" carousel — under a different `btn_ref` shuffle token |

A destination whose content and shuffle token change between requests cannot identify a product. The hub's
product pages are therefore accurate **about those ASINs** (each published row cites the manufacturer's own
page) but are not established as the requested items, and the "one coherent niche: countertop air frying"
reading is an inference from fallbacks. Both interpretations stay visible; the conflict is recorded as
**I-20 / F-12** in [`COORDINATION.md`](COORDINATION.md) and on
[`pages/flags.html`](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html). **Owner action:** confirm the
intended ASINs and everything downstream (identity, pricing, content, tagging) unblocks against them.

## Verification, per view

- **Hub — `scripts/verify.py`:** a `verified`/`conflict` row without a source URL; a non-`https` or
  non-official source; an `unverified` row carrying a published value; a broken internal link; a missing
  disclosure or trademark attribution; any printed price (including bare figures from the audit snapshot).
- **Subpages — `tools/validate_data.py`:** every row must cite an allowlisted official host
  (`affiliate-program.amazon.com`, `amazon.com`, `webservices.amazon.com`, `ftc.gov`, `developers.google.com`,
  `support.google.com`, `docs.github.com`) **or** be blank *and* linked to a flag; no invented performance
  metrics; no Amazon mark in the identifiers this project controls; the §5 disclosure sentence wherever a
  sponsored link exists; no divergence from the dashboard's product rows; no broken internal links (982
  checked).
- **`pages/` engine guards — `tests/test_pipeline.py`:** 11 executable checks (identifier refusal without
  repair, untagged-link refusal, per-visitor sub-tag refusal, competing-attribution refusal, banned disclosure
  wording, rate-table fidelity, "scoring never guesses", no fabricated metrics in data, build determinism).
- **`zone2/`** states its own checks on its methodology page; its product fields are blank, consistent with the
  above.

## Repository layout

| Path | Contents |
|---|---|
| `start.html` | Landing page linking to all four views (generated). |
| `index.html`, `app.js`, `data.js`, `styles.css` | Northstar dashboard (+ sidebar links into `pages/`). |
| `overview.html`, `products.html`, `compare.html`, … , `assets/` | Verified hub (generated; owned by `site-manifest.json`). |
| `zone2/` | Zone2 platform dashboard. |
| `pages/` | 37 generated subpages + `pages/manifest.json` (owned by `tools/build_site.py` — never hand-edit). |
| `data/` | Hub dataset. |
| `ledger/` | Subpage dataset: `products.json`, `commission_table.json`, `compliance.json`, `modules.json`, `flags.json`, `verification.json`, `sources.json`, `niches.json`, `campaigns.json`. |
| `docs/`, `content/templates/` | Hub summary/methodology; article, comparison and buying-guide templates. |
| `scripts/` | `build.py` + `verify.py` (hub). |
| `tools/` | `build_site.py`, `validate_data.py`, `asin_guard.py`, `amazon_creators_api.py`, `scoring.py`, `generate_articles.py`, `link_builder.py`, `redirect_server.py`, `optimize.py`, `cache.py`, `tracking_schema.sql`. |
| `tests/` | `test_pipeline.py`. |
| `EXECUTIVE_SUMMARY.md` | The brief's deliverable (a): what was verified, built, and blocked. |
| `COORDINATION.md` | Shared task board, merge/conflict records, irregularities, CI repair note. |
| `.github/workflows/pages.yml` | CI: validate all views → rebuild → verify → gate → stage `_site/` → deploy. |

## Run locally

Python 3.9+ (hub), 3.10+ (`tools/`). No third-party dependencies.

```bash
python3 scripts/build.py && python3 scripts/verify.py    # verified hub
python3 tools/build_site.py && python3 tools/validate_data.py   # subpages + gate
python3 tests/test_pipeline.py                            # guard checks
python3 -m http.server 8080                               # preview every view
```

The dashboard needs no build step: open `index.html`.

## Automation status

`tools/amazon_creators_api.py` targets the **Creators API** — PA-API 5.0 is deprecated and returns
`403 AccessDenied` — and exits `BLOCKED` rather than scraping until an eligible Associates account exists
(Amazon's stated prerequisite: ≥10 qualifying sales in the past 30 days). `tools/scoring.py` returns
`INSUFFICIENT_DATA` instead of a default when an input is missing; `tools/generate_articles.py` refuses to
draft copy for an entry without a resolved identity; `tools/optimize.py` takes no action without ≥30 clicks
**and** a dated report; `tools/redirect_server.py` counts static campaign keys and stores no visitor
identifier, because associating a sub-tag with a specific end user is prohibited.

Published economics used by the model (`ledger/commission_table.json`): fixed bands 10.00 / 5.00 / 4.50 /
4.00 / 3.00 / 2.50 / 2.00 / 1.00 / 0.00 % with a 4.00% default, Prime bounties $12.00, 24-hour Session,
89-day cart path, 180-day ship-and-pay, ~60-day payment lag
([rates](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) ·
[policies](https://affiliate-program.amazon.com/help/operating/policies)). Policy pages carry their own update
dates and change without notice — re-verify each cycle.

## GitHub Pages

`.github/workflows/pages.yml` validates all four views, re-runs both generators and both guards, then stages
a curated `_site/` bundle (dashboard, hub, `zone2/`, `pages/`) and deploys it on pushes to `main`. Internal
namespaces (`data/`, `scripts/`, `tools/`, `tests/`, `ledger/`, `content/`) are asserted absent from the bundle.
Source of truth for Pages is **GitHub Actions** in repository settings.
