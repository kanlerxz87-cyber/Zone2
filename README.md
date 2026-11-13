# Zone2 — AI Amazon Affiliate Marketing Platform

An AI-powered Amazon affiliate marketing platform: automated product research,
trending & high-converting product identification, pricing / reviews / competition /
commission analysis, and SEO-optimized product articles, comparisons and buying
guides — with click/conversion tracking and continuous optimization, built to comply
with Amazon Associates policies and disclosure requirements.

## Scope

Three Amazon affiliate products in the **Home & Kitchen — Air Fryers** niche:

| Short link | Resolves to (ASIN) | Product |
| --- | --- | --- |
| https://link.amazon/B04G1MEwY | B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer Oven |
| https://link.amazon/B02NbDxp3 | B09B7SB46R | Emeril Lagasse 26QT French Door Air Fryer Toaster Oven |
| https://link.amazon/B00hJ57DV | B08DKYBTPH | Chefman Air Fryer 8 Qt TurboFry 4-in-1 |

> The ASIN-like token in each `link.amazon` short link is **not** the product ASIN.
> The redirect target is the real identifier (flagged for review).

## What's here

- `site/` — static dashboard site (GitHub Pages). Landing page + category subpages,
  all entries/findings in source-linked tables, plus **Flagged for Review**,
  **Compliance**, **Sources & Verification** and **Executive Summary** pages.
- `site/js/data.js` — the verified dataset (inline, so the site works with no backend).
- `site/js/app.js` — renders the tables from the data.
- `scripts/check_links.py` — verifies no internal link is broken (runs in CI and locally).
- `.github/workflows/deploy.yml` — deploys `site/` to GitHub Pages on push to `main`.
- `COORDINATION.md` — shared task board, verification log and sources.
- `content/executive-summary.md` — executive summary source.

## Verification

Every table row links to the official Amazon listing it was verified against.
Values that could not be confirmed from an official source are left blank and
flagged as unverified — never inferred. Third-party sites are not used as a value
source. Run the link checker with:

```
python3 scripts/check_links.py site
```

## Build & deploy

The site is fully static. Pushing to `main` triggers the GitHub Pages workflow,
which runs the link checker and deploys `site/`.

**As an Amazon Associate I earn from qualifying purchases.**
