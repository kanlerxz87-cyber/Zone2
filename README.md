# Zone2 — Amazon affiliate research

Two views of the same three Amazon affiliate products, built by two sessions working in
parallel and merged here.

**Live site:** <https://kanlerxz87-cyber.github.io/Zone2/>

> As an Amazon Associate I earn from qualifying purchases.

---

## The two sites

| Path | What it is | Built by |
|---|---|---|
| `/index.html` | **Northstar** — a research workspace dashboard: overview, product research, content studio, optimization, compliance, flagged review. Hash-based navigation, no build step, no dependencies. Product facts are held blank because that session did not resolve the short links. | session `arena/6b8bb130-zone2` |
| `/start.html` → `/overview.html` | **Affiliate Research Hub** — the three products resolved to canonical ASINs, with every published value traced to an official Amazon or manufacturer page, plus the full compliance position and a line-by-line disposition of the brief. | session `arena/6602723a-zone2` |

**Both apply the same rule:** nothing is asserted without an official source, and where sources
disagree the disagreement is published rather than smoothed over.

`/start.html` is the landing page that links to both. It is generated, not hand-written.

## The three products

All three supplied `link.amazon/*` short links were resolved by following the redirect; the ASIN
is not readable from the short link itself.

| Supplied link | ASIN | Product | Brand |
|---|---|---|---|
| `link.amazon/B04G1MEwY` | B0CDY277D3 | 6 Qt Dual Basket Air Fryer, dual windows, Sync Finish | Chefman |
| `link.amazon/B02NbDxp3` | B09B7SB46R | 26QT French Door Multi-Function Air Fryer Toaster Oven | Emeril Lagasse |
| `link.amazon/B00hJ57DV` | B08DKYBTPH | 8 Qt TurboFry Touch air fryer, stainless steel | Chefman |

One coherent niche: countertop air frying, compact → mid → large.

## Repository layout

```
index.html, app.js, data.js, styles.css   Northstar dashboard (session 6b8bb130)
*.html, assets/, start.html               generated verified hub (session 6602723a)
site-manifest.json                        the exact list of files the generator owns

data/                                     the dataset — the single source of truth
  products.json            per-product specs; every row has a status and a source URL
  compliance.json          Amazon's rules, quoted with section references
  requirements.json        every requirement in the brief and its honest disposition
  sources.json             source registry, 3-tier trust model, rejected sources
  raw-verification-log.md  raw capture log: what each page actually said
docs/
  executive-summary.md     the short version
scripts/
  build.py                 generates the verified hub from data/
  verify.py                the guard: fails on unsourced rows, broken links, printed prices
COORDINATION.md            shared task board, merge record, irregularities log
```

## Build and check locally

Requires Python 3.9+. No third-party dependencies.

```bash
python3 scripts/build.py     # regenerate the verified hub
python3 scripts/verify.py    # exits non-zero on any broken rule
python3 -m http.server 8080  # preview both sites at http://localhost:8080
```

The dashboard needs no build step: open `index.html`.

## What the verification enforces

`scripts/verify.py` fails the build when:

- a fact row claimed as `verified` or `conflict` has no source URL;
- a source URL is not `https` or is not an official host;
- a row marked `unverified` still carries a published value;
- an internal link points at a file that is neither generated nor owned by the dashboard;
- a page is missing the affiliate disclosure or the trademark attribution;
- a page prints a currency amount — this project does not publish prices.

CI additionally runs a **negative test**: it injects an unsourced row and asserts the verifier
rejects it, so the guard is proven to guard.

## What is deliberately *not* published

| Data | Why |
|---|---|
| Price | Amazon permits price display only where Amazon serves it or it comes from the official API, and requires a timestamp plus a disclaimer. |
| Star rating / review count | Storefront-specific for the same ASIN; a single figure would mislead. |
| Stock status | Changes by the minute. |
| Commission rate | The official rate card requires an Associates login. |
| Conversion rate, sales volume, "trending" score | Not published by Amazon; no official source exists. |

## Known issues

The one thing blocking commercial value: **the three supplied links carry no Amazon Associates
tracking tag**, so clicks cannot be attributed. See `/flagged.html`, or `COORDINATION.md` item O-1.

## GitHub Pages

`.github/workflows/pages.yml` validates both sites, rebuilds the hub, confirms the committed
output matches a fresh build, runs the verifier, runs the negative test, stages only publishable
files into `_site/`, asserts the bundle is complete and that `data/` and `scripts/` have not
leaked, and deploys from `main` on push.

## Licence

Not yet chosen — see `COORDINATION.md` item O-3.
