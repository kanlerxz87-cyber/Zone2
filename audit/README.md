# Independent verification audit: session `5ba0cb60`

**Branch:** `arena/5ba0cb60-zone2` (base: `main` @ `cfc04b1`)
**Snapshot date:** 2026-11-13 (UTC). Every value below was read on that date.
**Claimed scope:** `audit/**` only. This audit does not edit the shared outputs (site pages, `data/**`, `docs/**`, `scripts/**`, `index.html`, `styles.css`, `app.js`, `data.js`, README, or the workflow). Those belong to the integration session. See `COORDINATION.md`.

## What this audit contains

| File | Purpose |
|---|---|
| [product-verification.md](product-verification.md) | Line-by-line field verification for the three products, with a source link on every row |
| [products-verified.json](products-verified.json) | The same facts in machine-readable form, for the integration session to ingest |
| [associates-compliance.md](associates-compliance.md) | Official Amazon Associates and FTC requirements that apply to this project, each with a source link and an action |
| [irregularities.md](irregularities.md) | Every irregularity found in the repo, the board, and the supplied inputs, with evidence |

## Method

1. Each supplied `link.amazon/<code>` URL was followed to its final destination with the page-retrieval tool. The destination was recorded.
2. Each Amazon product detail page was read in full. Values were copied from the page's own "Product information" and "About this item" sections, and the page section is cited on each row.
3. Amazon Associates policy text was read from the official `affiliate-program.amazon.com` pages (Operating Agreement, Program Policies, and the Associates Help topic on disclosure). Quotations are verbatim.
4. FTC guidance was read from `ftc.gov`.
5. The GitHub Pages configuration and workflow runs were read through the GitHub API with `gh`.

## Status key

| Status | Meaning |
|---|---|
| `verified` | Read directly from the cited official page on 2026-11-13. |
| `withheld` | Known, but intentionally not published, because an official policy restricts display. The policy is cited. |
| `unverified` | Not confirmed from an official source. Left blank. Never inferred. |
| `conflict` | Two official values on the same page disagree. Both are recorded and the row is flagged. |

## Limitations (stated plainly)

- Amazon pages are dynamic. Values were read from the page text the retrieval tool returned. A reviewer should re-check each value on the live page before publication.
- The Associates "Standard Commission Income" rate card is behind a sign-in wall (`/help/operating/schedule` redirects to sign-in). Commission rates are therefore **unverified** and left blank.
- No Associates account, Associate ID, PA-API credentials, or click/conversion reports were available. Nothing in this audit measures performance.
- Pricing and availability are **withheld** from every published artifact. The Associates Participation Requirements (§2, "Links on Your Site") restrict where prices and availability may be shown. The observed snapshot prices are not written into this repo. They are recorded in the chat report to the user.
