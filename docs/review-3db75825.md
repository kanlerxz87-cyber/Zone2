# Repo review and live-site audit — session `3db75825` (T40)

Date: 2026-11-15 (UTC) · Branch: `arena/3db75825-zone2` (base `ceaf9a7`, `main`) · Type: **verification only**.
No data, page, or tool file was edited. Findings are recorded here and on the board in `COORDINATION.md`.

Scope of the request, as it applies to this repository:

1. Review the repo and verify line by line against official sources; flag irregularities.
2. Confirm the GitHub Pages site is live and that every table row carries a source link or an explicit blank + flag.
3. Confirm the three supplied Amazon links against the live Amazon pages.
4. Confirm the repository's own gates pass on the tree this session audited.

What this session could **not** do, and why:

- It could not pull product price, rating, review count, availability, or BSR from the Creators API. That
  needs an authenticated Associates account (F-05), which this workspace does not have. Those cells stay blank.
- It did not change any product value. The repo's rule is that a value appears only when an official page states it.

---

## 1. Gates re-run on `arena/3db75825-zone2` (this session, exit codes recorded)

| Command | Exit | What it checks |
|---|---|---|
| `python3 tools/validate_data.py` | 0 | Ledger schema, row→source links, flag counts |
| `python3 tools/audit_site.py` | 0 | Fragments, spec sources, prose counts, namespaces, disclosure (4/4 PASS shown) |
| `python3 tools/build_site.py --check` | 0 | `pages/` generated output has no drift (`drifted_or_uncommitted: []`) |
| `python3 tools/build_root_views.py --check` | 0 | `verification.html` / `sources.html` match the ledger |
| `python3 tools/build_summary.py --check` | 0 | `summary.html` has no drift |
| `python3 tools/build_marketing.py --check` | 0 | 21 marketing outputs current |
| `python3 tools/build_decisions.py --check` | 0 | `decisions/` namespace has no drift |
| `python3 tools/validate_decisions.py` | 0 | Suggestions/questions register validates |
| `python3 tests/test_pipeline.py` | 0 | 15/15 checks |
| `node --check assets/js/app.js` | 0 | JS syntax |
| `node --check assets/js/data.js` | 0 | JS syntax |

Local link check (run by this session across every `*.html` in the tree, excluding `.git`): **116 HTML files,
0 broken local references.**

CI on `main`: latest push run `43714798834` → **success** (`Build, verify and deploy`, commit `ceaf9a7`).
Pages build `43714798538` → **success**. Pages API: `status: built`, source `main` `/`.

Sources for the gate evidence: the repository itself, `https://github.com/kanlerxz87-cyber/Zone2/actions`
(run IDs above), and the live site `https://kanlerxz87-cyber.github.io/Zone2/`.

---

## 2. The three supplied links — re-observed 2026-11-15 from the pages themselves

Each short link was fetched and followed to the Amazon listing. The page title is the value compared.

| Supplied link | Code as supplied (chars) | Redirects to (ASIN in the URL) | Page title observed 2026-11-15 | Ledger entry | Matches ledger? | Source link |
|---|---|---|---|---|---|---|
| `https://link.amazon/B04G1MEwY` | `B04G1MEwY` (9) | `amazon.com/dp/B0CDY277D3` | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | P-01 → B0CDY277D3 | **Yes** | [short link](https://link.amazon/B04G1MEwY) · [destination](https://www.amazon.com/dp/B0CDY277D3) |
| `https://link.amazon/B02NbDxp3` | `B02NbDxp3` (9) | `amazon.com/dp/B09B7SB46R` | "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included : Home & Kitchen" | P-02 → B09B7SB46R | **Yes** | [short link](https://link.amazon/B02NbDxp3) · [destination](https://www.amazon.com/dp/B09B7SB46R) |
| `https://link.amazon/B00hJ57DV` | `B00hJ57DV` (9) | `amazon.com/dp/B08DKYBTPH` | "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel : Home & Kitchen" | P-03 → B08DKYBTPH | **Yes** | [short link](https://link.amazon/B00hJ57DV) · [destination](https://www.amazon.com/dp/B08DKYBTPH) |

What this shows, and what it does not:

- **Shows:** each supplied short link resolves to one specific Amazon listing, and the ledger's destination
  titles match what was observed today.
- **Does not show:** that the listing is the product the brief intended. The codes are 9 characters, and the
  ledger records that the canonical `/dp/<code>` form returns Amazon's Page Not Found page (P-01…P-03,
  `canonical_dp_result`). The ledger's 10-character ASIN convention was taken from the repo; it was **not
  re-confirmed from an Amazon help page in this session**, so it is listed under Irregularities (§5).
- **Shows:** none of the three observed destination URLs carries an Associates `tag=` parameter (F-24). As
  supplied, these links cannot attribute a commission.
- **Shows:** each destination URL carries per-click tracking parameters (`lv=shuf`, `btn_ref=srctok-…`,
  `plpRedirect=mhFallback`). The `btn_ref` token differs between fetches (F-21), so it must not be treated as
  a stable identifier. The `plpRedirect=mhFallback` parameter is the reason earlier sessions raised F-03/F-12.
  Those flags stand and are not closed by this review.

Note on the observed page text: the fetched pages also show prices and ratings, which the repo does not publish
(its rule is that price is not inferred or copied). None was recorded here.

---

## 3. Official source — Associates Program Policies

| Item | Observed 2026-11-15 | Source link |
|---|---|---|
| Policy page "Updated" date | **April 14, 2026** (matches the ledger's "updated 2026-04-14") | [affiliate-program.amazon.com/help/operating/policies](https://affiliate-program.amazon.com/help/operating/policies) |
| Commission Income Statement, Qualifying Purchases window | 24-hour session; 89-day add-to-cart completion; 180-day ship/pay window (text read in this session) | same page, §1 "Qualifying Purchases and Qualifying Revenue" |
| Document structure | Commission Income Statement, Participation Requirements, Products Statement, Mobile App Policy, Trademark Guidelines, IP License, Influencer Program Policy, Creator Ads Boost policy | same page |

The ledger's per-row checks for the commission bands and the disclosure sentence were **not** re-read line by
line in this session. They remain as recorded in `ledger/compliance.json` and `ledger/commission_table.json`,
with their own source links. This review does not re-verify them.

---

## 4. Live site entry point

- `https://kanlerxz87-cyber.github.io/Zone2/` — fetched 2026-11-15: title "Zone2 — Verified Amazon Affiliate
  Marketing Platform"; the three product cards show "— unverified —" for price, rating, and availability, and
  show the observed destinations, consistent with `ledger/products.json`.
- Landing-page KPIs as published: 3 of 3 supplied links resolve (re-observed 2026-11-15); 0 of 3 brief product
  mappings confirmed by an official Amazon document (F-03); 4.00% "All Other Categories" program rate; 38 flags
  on the Flagged for Review register.

---

## 5. Irregularities flagged for review (non-blocking)

| # | Irregularity | Evidence / source | Disposition |
|---|---|---|---|
| I-A | **The three supplied codes are 9 characters.** The repo says an ASIN is 10 characters, but this session did not re-read that rule from an Amazon help page. | `ledger/products.json` P-01…P-03 `asin_length_observed: 9`; Amazon's ASIN definition page not fetched this session | Needs an Amazon help-page link before it is stated as fact on the site. **Not fixed here.** |
| I-B | **Open PR #70 (`arena/cffe745a-zone2`, "trendy marketing articles") is CONFLICTING and has no check runs.** Its head edits generated marketing output. | `gh pr view 70` → `mergeable: CONFLICTING`, `statusCheckRollup: []` | Another session's claim. Left as-is; owner should rebase or close. |
| I-C | **Board rows that read "in progress" have closing records.** T28 (closed by `e9c8362c` and `0a697d4a`), T32 (closed by `8c4236ad`, merged), and T38 (closed by `bfed39e0`, merged as PR #85). | `COORDINATION.md` rows at lines 79, 2911, 2922 vs. the closing records at the end of the file | Hygiene. Recorded; no row edited by this session. |
| I-D | **`COORDINATION.md` is 401 KB / ~4,160 lines** with repeated renumbering (T29→T30→…→T39). Hard to audit by hand. | `wc -l COORDINATION.md` | Recommend archiving closed sections into a separate log. Not done here. |
| I-E | **Only owner-level blockers remain.** No Associates tag on any supplied link (F-24); no Associates ID or Creators API access (F-05, F-07); no performance data exists (F-08). These block revenue, not the build. | Landing page + `ledger/flags.json` | Owner decision. Listed on the suggestions board. |
| I-F | **Carried forward, not re-verified here:** the `@font-face` path issue in `assets/css/style.css` (recorded in T38's closing record), and the "verified 2026-11-14" eyebrow on some pages checked on 2026-11-15. | `COORDINATION.md` T38 closing record; earlier T29 note | Not re-checked this session. Left as recorded. |

---

## 6. Summary

- Gates: **11 of 11 exit 0**. Local link check: **0 broken** across 116 HTML files. Latest CI on `main` and the Pages build: **success**.
- Three supplied links: **re-observed today; each resolves to one listing that matches the ledger**; none is confirmed as the intended product; none carries an Associates tag.
- No values were added, changed, or inferred. Unverified cells remain blank and flagged.
- Open items are owner decisions and hygiene, not build defects.
