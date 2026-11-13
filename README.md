# Zone2 — Amazon Affiliate Intelligence Dashboard

AI-powered Amazon affiliate marketing platform: product research, commission &amp; competition analysis, SEO content plan, affiliate-link management design, and compliance tracking — every value verified against official sources.

## Live site

**https://kanlerxz87-cyber.github.io/Zone2/** (GitHub Pages, serves from `main` branch root)

| Page | Contents |
|------|----------|
| [Dashboard](index.html) | KPIs, headline findings, program facts |
| [Products](products.html) | 3 supplied links, per-marketplace 404 evidence, blank-unverified attributes |
| [Analysis](analysis.html) | Official rate card, attribution rules, niche/competition assessment, automation roadmap |
| [Comparisons](comparisons.html) | Head-to-head framework (values blank until products verify) |
| [Buying Guides](buying-guides.html) | SEO content plan per Google's official starter guide |
| [Compliance](compliance.html) | 12 Amazon/FTC requirements with sources + status |
| [Executive Summary](executive-summary.html) | One-page summary of goal, method, findings, risks, next steps |
| [Flagged for Review](flagged-for-review.html) | 13 irregularities (F-01…F-13), all non-blocking, with source links |
| [Verification Log](verification.html) | Line-by-line check log (every URL + result, 2026-11-13) |
| [Sources](sources.html) | 25 official sources used |

## Headline finding

**0 of 3 supplied products could be verified.** Codes `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV` are 9 characters (valid ASIN = 10); all 18 official `/dp/` URLs return 404 across six marketplaces; Amazon search returns "No results". All product data cells are **blank and flagged** — never inferred. See [Flagged for Review](flagged-for-review.html).

## Verification rule

> Every table row links to an official source. If a value cannot be confirmed from an official source, it is left blank and flagged as unverified. Nothing is inferred.

Run the automated check:

```bash
python3 scripts/verify_site.py
```

## Repository layout

```
index.html … sources.html   # static site (GitHub Pages root)
assets/style.css, app.js    # UI
data/products.json          # product research (nulls + flags for unverified)
data/compliance.json        # compliance matrix with sources
docs/repo-review.md         # line-by-line repo review
scripts/verify_site.py      # link / row-source / disclosure verifier
COORDINATION.md             # shared multi-session task board
```

## Disclosure

**As an Amazon Associate I earn from qualifying purchases.**
