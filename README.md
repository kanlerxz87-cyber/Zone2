# Zone2

AI-powered Amazon affiliate marketing platform — automates product research, trend and conversion
analysis, pricing/review/competition analysis, SEO content generation, link and campaign management,
and policy-compliant optimization for the Amazon Associates program.

## Live site

https://kanlerxz87-cyber.github.io/Zone2/

Served via GitHub Pages from the `main` branch root (`/`).

## Site structure

### Primary platform (Zone2 — this site's landing and category pages)

| Page | Purpose |
|---|---|
| `index.html` | Dashboard — executive summary, verified platform facts, capabilities |
| `products.html` | Affiliate product catalog + verified manufacturer spec tables (per-row source links) |
| `analysis.html` | Niche, pricing, competition and commission-potential analysis |
| `content.html` | AI-generated SEO content plan (articles, comparisons, buying guides) |
| `compliance.html` | Amazon Associates policy and disclosure requirements |
| `tracking.html` | Special Link and campaign tracking setup |
| `flagged.html` | Flagged irregularities and unverified items (with source links) |

### Companion sites (parallel session contributions, preserved in full)

- **`research-hub/`** — Affiliate Research Hub (`start.html`): the three products resolved to
  canonical ASINs, with every published value traced to an official Amazon or manufacturer page,
  comparison, requirements disposition, methodology, executive summary, and a verifier/build
  toolchain (`scripts/`, `data/*.json`). Built by session `arena/6602723a-zone2` (merged to `main`
  via PRs #4/#6), relocated here unchanged during final integration.
- **`northstar/`** — Northstar affiliate-intelligence prototype dashboard (hash-based navigation,
  no build step). Built by session `arena/6b8bb130-zone2` (merged to `main` via PR #1), relocated
  here unchanged during final integration.
- **`zone2/`** — a second AI-powered platform build (multi-page dashboard with executive summary,
  sources and verification data) by session `arena/34836ddd-zone2` (merged to `main` via PR #5),
  preserved unchanged under its original directory name during final integration.

## Data & verification

Primary data lives in `assets/js/data.js`. Every value was checked against the official Amazon,
Chefman and Emeril Everyday sources listed per row (2026-11-13). Values that could not be confirmed
from an official source are left blank and listed on the Flagged for Review page — nothing is
inferred. The verification record is in `docs/verification-log.md` and `docs/executive-summary.md`;
task coordination is in `COORDINATION.md`.

## Building

Static site — no build step. Open `index.html` directly or serve the repository root. The
`.github/workflows/pages.yml` workflow validates internal links, asset references and data files on
every push and PR to keep the published site broken-link-free.
