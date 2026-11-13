# Northstar — affiliate intelligence dashboard

A static, source-first research dashboard for the three Amazon short links supplied in the project request. Product identities and listing data are intentionally blank: none was independently confirmed from an official product detail page. The site does not claim to publish affiliate content, track conversions, or provide AI automation; it presents a transparent prototype and flags the inputs needed to build those capabilities safely.

## Run locally
Open `index.html` in a browser or serve this directory with any static file server. Navigation is hash-based and requires no build step or dependencies.

## Site sections
- **Overview:** executive summary, research snapshot, and unresolved product queue.
- **Product research:** submitted links and blank, unverified product fields.
- **Content studio:** recommended workflow, with content generation blocked until facts are verified.
- **Optimization:** reports that no click/conversion data has been supplied.
- **Compliance:** links to official Amazon Associates guidance.
- **Flagged for review:** unresolved product and operational flags.

## Research and compliance
Official references are linked in the dashboard and `data.js`: Amazon Associates Policies, Participation Requirements, Amazon disclosure guidance, and Amazon's Associates tools overview. Current terms and marketplace-specific requirements must be checked before use. The public Amazon disclosure language shown in the dashboard is transcribed from Amazon's official disclosure guidance. No prices, ratings, product titles, commission rates, trends, or performance results have been inferred. Amazon's policies impose conditions on display of product prices, availability, reviews/ratings, and API content; use authorized Associates tools and follow their current license.

## GitHub Pages
`.github/workflows/pages.yml` validates the static assets and publishes the repository root when changes reach `main` (or via workflow dispatch). Enable GitHub Pages with **GitHub Actions** as the source in repository settings if it is not already configured.
