# Zone2 — AI-Powered Amazon Affiliate Marketing Platform

A clean, dashboard-style static site that automates the research workflow for Amazon affiliate marketing: product research, pricing / reviews / competition / commission analysis, SEO content planning, affiliate-link management, conversion tracking, and campaign optimization — designed around Amazon Associates compliance and FTC disclosure requirements.

## What's in the repository

- **Primary site (root)** — multi-page dashboard:
  - `index.html` — landing / dashboard with KPIs and platform capabilities
  - `products.html` — product research table (one row per supplied product, each row with official source links)
  - `analysis.html` — pricing / reviews / competition / commission analysis; commission mechanics verified from the official Commission Income Statement
  - `content.html` — SEO articles / comparisons / buying guides status
  - `compliance.html` — Associates Operating Agreement, Program Policies, Participation Requirements, FTC disclosures
  - `executive-summary.html` — executive summary (also `docs/EXECUTIVE_SUMMARY.md`)
  - `flagged.html` — **Flagged for Review**: irregularities and unverified items with source links
  - `sources.html` — every source used, for manual review
  - `assets/styles.css`, `assets/main.js` — styling and table rendering
- **Northstar workspace (`northstar/`)** — alternate source-first research dashboard (Overview, Product research, Content studio, Optimization, Compliance, Flagged for review), preserved intact from a parallel session.
- **Data** — `data/verification.json` (machine-readable verification record).
- **Deploy** — `.github/workflows/pages.yml` validates the site's internal navigation and publishes the repository root to GitHub Pages on pushes to `main`.

## Verification policy (no hallucinations)

Every table row carries a source link to an official site. Values that cannot be confirmed from an official source are **left blank and flagged as unverified** — never inferred or filled in.

## Product status — IMPORTANT

The three supplied product codes (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) are each **9 characters**; Amazon officially defines an ASIN as a **unique 10-character alphanumeric code**. No official source (Amazon product pages, Google, Bing, Wayback Machine, CamelCamelCamel) has any record of these codes, so **all product-specific fields are blank and marked unverified**. See the **Flagged for Review** page (`flagged.html`) for the full irregularity log and source links.

**To activate research:** re-supply each identifier as an exact 10-character ASIN taken directly from the Amazon product page URL (the string after `/dp/`) or from the product's Product Information section.

## Compliance

The site applies Amazon Associates disclosure requirements site-wide: *"As an Amazon Associate I earn from qualifying purchases."* plus clear, conspicuous, link-level FTC disclosure. Official references are linked on the Compliance and Sources pages. No commission income is earned or tracked until products are verified and an Associates account is enrolled.

## Run locally

Open `index.html` in a browser, or serve the repository root with any static file server. No build step or dependencies.

## Coordination

`COORDINATION.md` is the shared task board for parallel sessions (claims, scopes, verification log, merge record).
