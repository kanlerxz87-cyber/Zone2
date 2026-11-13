# COORDINATION.md — Shared task board

This file is the shared task board for all agent sessions working on this repository.
Read it before starting work. Claim a task by writing your session ID and file scope here,
then commit and push the claim immediately. Never start a task another session has claimed.

**Last updated:** 2026-11-13 (UTC)

---

## Session registry

| Session ID | Branch | Role | Status |
|---|---|---|---|
| `arena/6b8bb130-zone2` | merged to `main` via PR #1 | Dashboard prototype (Northstar) | merged |
| `S-6602723A` | `arena/6602723a-zone2` | Verified dataset, generated hub, integration | in progress (PR #4) |

---

## Task board

Legend: `unclaimed` · `in progress` · `done` · `needs review`
A status of `needs review` means the item is published on the *Flagged for Review* page and
does not block anything.

| ID | Task | Status | Owner | File scope |
|---|---|---|---|---|
| T1 | Task board + session registry | done | S-6602723A | `COORDINATION.md` |
| T2 | Resolve the three affiliate short links to canonical ASINs | done | S-6602723A | `data/raw-verification-log.md` |
| T3 | Verify product facts against official sources | done | S-6602723A | `data/products.json`, `data/sources.json` |
| T4 | Amazon Associates compliance requirements | done | S-6602723A | `data/compliance.json` |
| T5 | Executive summary | done | S-6602723A | `docs/executive-summary.md` |
| T6 | Automated platform requirements matrix | done | S-6602723A | `data/requirements.json` |
| T7 | Verified hub site (landing + category subpages) | done | S-6602723A | `*.html` (generated), `assets/**` |
| T8 | Link + data integrity check in CI | done | S-6602723A | `scripts/verify.py`, `.github/workflows/**` |
| T9 | Dashboard prototype (Northstar) | done | `arena/6b8bb130-zone2` | `index.html`, `app.js`, `data.js`, `styles.css` |
| T10 | Final integration: merge, re-verify, PR, deploy | in progress | S-6602723A | `COORDINATION.md`, `README.md`, `.github/workflows/**` |

---

## File ownership (non-overlapping scopes)

| Scope | Owner | Notes |
|---|---|---|
| `index.html`, `app.js`, `data.js`, `styles.css` | `arena/6b8bb130-zone2` | Dashboard. **Preserved unchanged** by the integration session. |
| `COORDINATION.md` | final integration session | task board |
| `README.md` | final integration session | both sites documented |
| `.github/workflows/**` | final integration session | merged from both sessions |
| `data/**`, `docs/**`, `scripts/**` | S-6602723A | verified dataset and tooling |
| `start.html`, `overview.html`, `products.html`, `compare.html`, `compliance.html`, `requirements.html`, `methodology.html`, `flagged.html`, `summary.html`, `product-*.html`, `404.html`, `assets/**` | S-6602723A | generated; listed in `site-manifest.json` |

`site-manifest.json` records exactly which files `scripts/build.py` owns. The generator cleans up
only files on that list, so it can never delete the dashboard's hand-written files or anything in
`data/`, `docs/` or `scripts/`.

---

## Change log

### 2026-11-13 — `arena/6b8bb130-zone2` (merged via PR #1)

- Claimed the dashboard task with scope `COORDINATION.md, README.md, index.html, styles.css,
  app.js, data.js, .github/workflows/pages.yml`.
- Built Northstar, a static source-first dashboard. Product fields were left **blank and marked
  Unverified** because that session could not resolve the three short links to product pages.
- Added an Actions-based Pages workflow with asset and navigation validation.
- Research policy recorded: "do not assert product titles, features, prices, ratings,
  commissions, or performance for the three submitted short URLs unless an official source can be
  verified."

### 2026-11-13 — S-6602723A

- **Claimed:** T1–T8, T10; scope `data/**`, `docs/**`, `scripts/**`, `COORDINATION.md`,
  `README.md`, `.github/workflows/**`, and generated HTML at the repo root.
- Repo state at claim: `main` = `f577167`, containing only a 7-byte `README.md`. Nothing to
  conflict with at that time.
- Resolved all three short links to canonical ASINs and verified specifications against Amazon
  product pages and the manufacturers' own product pages.
- Built the verified hub and the verifier guard.
- **Merge conflict encountered** when opening PR #4: session `arena/6b8bb130-zone2` had merged
  PR #1 into `main` in the meantime. See the merge record below.

---

## Merge conflict and resolution

**What happened.** While S-6602723A was building on `arena/6602723a-zone2`, session
`arena/6b8bb130-zone2` merged PR #1 into `main` (`cfc04b1`), adding a complete dashboard at
`index.html`, `app.js`, `data.js` and `styles.css`, plus its own `README.md`,
`COORDINATION.md` and `.github/workflows/pages.yml`. PR #4 then reported
`mergeable: CONFLICTING`.

**Files conflicted:** `index.html`, `README.md`, `COORDINATION.md`,
`.github/workflows/pages.yml`.

**Resolution — nothing either session built was discarded:**

| File | Resolution |
|---|---|
| `index.html` | **Kept the dashboard's version verbatim.** The verified hub's overview moved to `overview.html`, and `start.html` became a landing page linking to both. The generator asserts it does not write `index.html`. |
| `README.md` | Rewritten to document **both** sites, with per-session attribution. |
| `COORDINATION.md` | This file — both sessions' records retained, plus this resolution log. |
| `.github/workflows/pages.yml` | Merged. The dashboard session's Actions-based deployment is kept as the deployment mechanism; the dashboard's original asset/navigation validation is preserved as a step; the verified-hub build, verifier and negative test were added. The bundle is staged into `_site/` instead of uploading the repo root, so `data/` and `scripts/` are not published. |
| `app.js`, `data.js`, `styles.css` | Untouched. |

**Deviation, recorded deliberately:** the dashboard's original workflow published with
`path: .`, which would have exposed `data/`, `docs/`, `scripts/` and this file as browsable
static assets. The merged workflow stages only publishable files and asserts that no `data/` or
`scripts/` file leaks into the bundle. This changes the previous behaviour and is recorded here
rather than done silently.

---

## Irregularities log

| # | Irregularity | Where | Disposition |
|---|---|---|---|
| I-1 | `README.md` in the initial commit contains only `# Zone2` (7 bytes) — no description, licence, or usage documentation. | `README.md` @ `f577167` | Resolved. |
| I-2 | No `LICENSE`, no `.gitignore`, no CI, no tests in the initial commit. | repo root @ `f577167` | `.gitignore` and CI added; licence is owner decision O-3. |
| I-3 | The three `link.amazon/*` short links are opaque redirects; their target ASINs cannot be read from the link text. | affiliate inputs | Resolved by following the redirect; recorded in `data/raw-verification-log.md`. |
| I-4 | No Amazon Associates tracking tag (Store ID) on any of the three links, so commission attribution is impossible. | affiliate inputs | **Flagged for review — owner action O-1.** |
| I-5 | Prices, ratings, review counts and stock status are volatile and Amazon restricts their display. | product data | Captured for the audit trail, withheld from publication. |
| I-6 | Amazon.com product pages are bot-gated and render inconsistently to automated fetches. | product data | Disclosed in `docs/methodology.md`; corroborated against regional storefronts and the manufacturer. |
| I-7 | Star ratings differ by storefront for the same ASIN (`B09B7SB46R`: 4.5/16,128 on `.co.uk` vs 4.6/8,361 on `.sa`). | product data | No rating published. |
| I-8 | Chefman 8 Qt: Amazon's bullet text says 1000 W; Chefman says 1700 W for the same model number `RJ38-SQSS-8T`. | `B08DKYBTPH` | Manufacturer figure published; discrepancy flagged. |
| I-9 | Chefman 8 Qt dimensions differ between the Amazon spec table and the manufacturer page. | `B08DKYBTPH` | Both published as separate sourced rows. |
| I-10 | Emeril model number suffix: `-02X-VN` on Amazon US vs `-02A-VN` on the manufacturer store. | `B09B7SB46R` | Both published with sources. |
| I-11 | Emeril wattage: 1700 W is the rated figure; a customer review reports a lower measured draw. | `B09B7SB46R` | Rated figure published. Measured draw is not a specification and is not published. |
| I-12 | Emeril preset count: 24 in the title and description, 25 in the manufacturer's own spec tile. | `B09B7SB46R` | Both shown side by side. |
| I-13 | Emeril 500 °F maximum is single-sourced to Amazon's product-information block. | `B09B7SB46R` | Published as single-source and labelled. |
| I-14 | The Chefman 6 Qt listing's own rating block did not render; the figure visible on the page belongs to a sibling ASIN (`B0B7C327LK`). | `B0CDY277D3` | Rating left blank; not attributed. |
| I-15 | Amazon's Agent Terms require automated clients to self-identify and forbid bypassing blocks, which makes "fully automated scraping" non-compliant. | brief vs policy | Documented on the compliance page; the automation that *is* compliant was built. |
| I-16 | **Two sessions built overlapping front pages.** PR #1 merged a dashboard at `index.html` while PR #4 was in progress. | `index.html` | Resolved without discarding either: dashboard kept at `index.html`, hub at `overview.html`, `start.html` as landing. See the merge section. |
| I-17 | The dashboard's workflow published `path: .`, exposing `data/`, `docs/` and `scripts/` as static files. | `.github/workflows/pages.yml` | Fixed in the merged workflow: only `_site/` is uploaded, with an assertion that nothing leaks. |

---

## Verification protocol used this session

1. Every table row carries a `source` link to an official page (Amazon product page, the
   Amazon Associates Operating Agreement, or the manufacturer's own site).
2. A value that could not be confirmed from an official source is left **blank** and marked
   `unverified` in `data/products.json`, and it appears on the *Flagged for Review* page.
3. No value is inferred, interpolated, or carried over from a similar product.
4. `scripts/verify.py` re-checks every row at build time and fails the build on an unsourced
   row, a non-`https` source, a published unverified value, a broken internal link, a missing
   disclosure, or a printed price.
5. Capture timestamps are recorded in UTC in `data/products.json`.

---

## PR and merge record

| Item | Value |
|---|---|
| Integration branch | `arena/6602723a-zone2` (branched from `main` @ `f577167`) |
| PR #1 (dashboard) | merged before integration — <https://github.com/kanlerxz87-cyber/Zone2/pull/1> |
| PR #4 (verified hub + integration) | <https://github.com/kanlerxz87-cyber/Zone2/pull/4> |
| Merge conflict | resolved as described above; no work discarded |
| Merge result | _recorded after merge_ |
| Pages deploy | _recorded after deploy_ |
