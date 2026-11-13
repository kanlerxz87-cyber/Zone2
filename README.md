# Zone2

AI-powered Amazon affiliate marketing platform — automates product research, trend and conversion
analysis, pricing/review/competition analysis, SEO content generation, link and campaign management,
and policy-compliant optimization for the Amazon Associates program.

## Live site

https://kanlerxz87-cyber.github.io/Zone2/

Served via GitHub Pages from the `main` branch root (`/`).

## Site structure

| Page | Purpose |
|---|---|
| `index.html` | Dashboard — executive summary, verified platform facts, capabilities |
| `products.html` | Affiliate product catalog (verified Amazon data, per-row source links) |
| `analysis.html` | Niche, pricing, competition and commission-potential analysis |
| `content.html` | AI-generated SEO content plan (articles, comparisons, buying guides) |
| `compliance.html` | Amazon Associates policy and disclosure requirements |
| `tracking.html` | Special Link and campaign tracking setup |
| `flagged.html` | Flagged irregularities and unverified items (with source links) |

## Data & verification

All data lives in `assets/js/data.js`. Every value was checked against the official Amazon sources
listed per row (2026-11-13). Values that could not be confirmed from an official source are left blank
and listed on the Flagged for Review page — nothing is inferred. The verification record is in
`docs/verification-log.md`; task coordination is in `COORDINATION.md`.

## Building

Static site — no build step. Open `index.html` directly or serve the repository root.
