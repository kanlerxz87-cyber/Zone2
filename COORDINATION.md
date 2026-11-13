# COORDINATION.md — Shared Task Board

Repository: `kanlerxz87-cyber/Zone2`
Sessions: `arena/34836ddd-zone2`, `arena/6b8bb130-zone2`
Date: 2026-11-13

## Protocol notes

- This is the shared task board. Each task lists status, owning session, and file scope.
- Statuses: `unclaimed`, `in progress`, `done`, `needs review`.
- `needs review` = item is published on the "Flagged for Review" page and does not block anything.
- Shared outputs (site index/navigation, combined table data) are changed only by the final integration session once all other tasks are done.

## Tasks

| # | Task | Status | Session | File scope | Notes |
|---|------|--------|---------|------------|-------|
| 1 | Repo review | done | arena/34836ddd-zone2 | none | Repo contained only `README.md` (# Zone2) and an initial commit `f577167`. No existing site, data, or code to preserve. |
| 2 | Product verification (3 ASINs) | done | arena/34836ddd-zone2 | `data/verification.json` | **Irregularity flagged:** codes B04G1MEwY, B02NbDxp3, B00hJ57DV are each 9 characters; Amazon officially requires a unique 10-character ASIN. No official source could confirm any product identity. All product-specific values left blank + unverified. Sources below. |
| 3 | Executive summary | done | arena/34836ddd-zone2 | `docs/EXECUTIVE_SUMMARY.md`, `executive-summary.html` | Platform scope, products, verification findings, compliance posture, flagged irregularities. |
| 4 | Site build — primary multi-page dashboard | done | arena/34836ddd-zone2 | `index.html`, `products.html`, `analysis.html`, `content.html`, `compliance.html`, `executive-summary.html`, `flagged.html`, `sources.html`, `assets/styles.css`, `assets/main.js` | Clean dashboard-style static site. Tables carry per-row source links; unverified cells blank + flagged. Root landing page. |
| 5 | Site build — source-first research dashboard (Northstar workspace) | done | arena/6b8bb130-zone2 | `northstar/index.html`, `northstar/styles.css`, `northstar/app.js`, `northstar/data.js` | Hash-based single-page dashboard (Overview, Product research, Content studio, Optimization, Compliance, Flagged for review). Same no-inference policy. Preserved verbatim under `northstar/` by the integration session. |
| 6 | GitHub Pages workflow | done | arena/6b8bb130-zone2 | `.github/workflows/pages.yml` | Validates static assets and internal navigation, then publishes repo root to GitHub Pages on pushes to `main`. Updated by integration session to validate the combined site. |
| 7 | Final integration & verification | done | arena/34836ddd-zone2 (integration) | all site files | Merged both sessions' work; re-verified combined data line by line; confirmed site builds with no broken links. Conflict resolution logged below. |
| 8 | PR, merge, GitHub Pages deploy | done | arena/34836ddd-zone2 | none | PR #5 created and merged into `main`; GitHub Pages deploys via the workflow. See record below. |

## Merge conflict log (task 7)

- `git merge origin/main` into `arena/34836ddd-zone2` produced add/add conflicts in `COORDINATION.md` and `index.html` (both sessions created these files at the same paths).
- **Resolution (without discarding either session's work):**
  - The other session's dashboard (`index.html`, `styles.css`, `app.js`, `data.js`) was moved intact into the `northstar/` subfolder; its relative asset references still resolve, and it is linked from the primary dashboard navigation.
  - The root `index.html` is the primary multi-page dashboard (session `arena/34836ddd-zone2`), now with a nav link to the preserved Northstar workspace.
  - `COORDINATION.md` was rewritten as the single shared board above, recording both claims.
  - `README.md` and `.github/workflows/pages.yml` were updated by the integration session to describe/validate the combined site.

## Verification log (task 2 — line by line)

Sources checked for each identifier `B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`:

1. **Amazon product page** — `https://www.amazon.com/dp/<code>` returns Amazon's "Page Not Found" (Dogs of Amazon) for all three. Links: [https://www.amazon.com/dp/B04G1MEwY](https://www.amazon.com/dp/B04G1MEwY), [https://www.amazon.com/dp/B02NbDxp3](https://www.amazon.com/dp/B02NbDxp3), [https://www.amazon.com/dp/B00hJ57DV](https://www.amazon.com/dp/B00hJ57DV)
2. **Google exact-match search** for `"B04G1MEwY"` — approx. **0 results**; Google states the string matches no known result. [https://www.google.com/search?q=%22B04G1MEwY%22](https://www.google.com/search?q=%22B04G1MEwY%22)
3. **Bing exact-match search** for each code — no results referencing the codes (only unrelated pages returned). [https://www.bing.com/search?q=%22B04G1MEwY%22](https://www.bing.com/search?q=%22B04G1MEwY%22)
4. **Wayback Machine CDX index** — no captures of `amazon.com/dp/B04G1MEwY` (or `www.` form). [http://web.archive.org/cdx/search/cdx?url=amazon.com/dp/B04G1MEwY&output=json](http://web.archive.org/cdx/search/cdx?url=amazon.com/dp/B04G1MEwY&output=json)
5. **CamelCamelCamel (Amazon US price tracker)** — all three "not yet in our database" / invalid identifier. [B04G1MEwY](https://camelcamelcamel.com/product/B04G1MEwY), [B02NbDxp3](https://camelcamelcamel.com/product/B02NbDxp3), [B00hJ57DV](https://camelcamelcamel.com/product/B00hJ57DV)
6. **ASIN format (official)** — Amazon: ASIN is a "unique 10-character alphanumeric code" assigned to every product; examples `B07FZ8S74R`, `0451524934`. [https://sell.amazon.com/blog/what-is-an-asin](https://sell.amazon.com/blog/what-is-an-asin)
7. **Character-count check** — all three provided codes measure **9 characters**; valid ASIN examples measure 10.

### Irregularities flagged for review

- **I-1:** `B04G1MEwY` is 9 characters — not a valid 10-character ASIN. Product identity unverified.
- **I-2:** `B02NbDxp3` is 9 characters — not a valid 10-character ASIN. Product identity unverified.
- **I-3:** `B00hJ57DV` is 9 characters — not a valid 10-character ASIN. Product identity unverified.
- **I-4:** `https://link.amazon/B04G1MEwY` did not resolve to a stable product page when fetched; it redirected to an unrelated product listing (ASIN `B0CDY277D3`, a CHEFMAN air fryer) via Amazon's fallback behavior — the short link is not a reliable identifier for the intended product.
- **I-5:** No official source (Amazon, Google, Bing, Wayback Machine, CamelCamelCamel) has any record of the three codes; all product-specific fields (title, brand, category, price, rating, reviews, BSR, commission) are therefore **blank and marked unverified** in the site tables.

## Compliance sources (tasks 4, 5)

- Associates Program Operating Agreement (updated Oct 15, 2025): [https://affiliate-program.amazon.com/help/operating/agreement](https://affiliate-program.amazon.com/help/operating/agreement)
- Associates Program Policies (updated Apr 14, 2026, incl. Commission Income Statement): [https://affiliate-program.amazon.com/help/operating/policies](https://affiliate-program.amazon.com/help/operating/policies)
- Participation Requirements: [https://affiliate-program.amazon.com/help/operating/participation/](https://affiliate-program.amazon.com/help/operating/participation/)
- Disclosure requirements ("As an Amazon Associate I earn from qualifying purchases." + FTC clear & conspicuous): [https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98)
- FTC Endorsement Guides (referenced by Amazon): [https://www.ftc.gov/tips-advice/business-center/guidance/ftcs-endorsement-guides-what-people-are-asking#affiliate](https://www.ftc.gov/tips-advice/business-center/guidance/ftcs-endorsement-guides-what-people-are-asking#affiliate)

## PR / merge record (task 8)

- PR: [https://github.com/kanlerxz87-cyber/Zone2/pull/5](https://github.com/kanlerxz87-cyber/Zone2/pull/5)
- Merge result: merged into `main` via `gh pr merge 5 --merge` on 2026-11-13 (after integration conflict resolution; first attempt failed with a non-clean merge commit, resolved via the merge in task 7).
- GitHub Pages: deployed from `main` via `.github/workflows/pages.yml` (GitHub Actions source). Site URL recorded in the Actions run once the workflow completes.
