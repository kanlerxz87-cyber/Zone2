# Requirements-to-evidence coverage audit — session `970d11d6` (T51; renumbered from T50)

**Date (UTC):** 2026-11-16 · **Branch:** `arena/970d11d6-zone2` (from `main` @ `004a040`) · **Type:** read-only verification.
**Scope:** maps each explicit requirement of the 2026-11-16 brief to the file or live page that satisfies it, and re-counts the table rows against the "every row has an official source link; blank and flag otherwise" rule.
**Overlap:** the supplied-link, policy-page and gate checks also appear in `docs/review-2026-11-16.md` (T50, session `ebc8a709`, PR #131). This audit does not repeat them as findings; it adds the requirement matrix, row-level counts and N-1…N-7.
**Not edited:** `ledger/**`, `pages/**`, `marketing/**`, `audit/**`, `console/**`, root `*.html`, `assets/**`, `tools/**`, `.github/**`. Every item below that needs a change is logged as an owner request, not made here.

Status vocabulary: **met** (evidence found and checked) · **partial** (met in part; gap stated) · **owner-blocked** (needs the Associates account owner, or a credential this sandbox does not hold) · **not assessed** (not checked in this session).

---

## 1. Requirement coverage

| # | Requirement (from the brief) | Where it is met | Status | Evidence checked this session | Gap / note |
|---|---|---|---|---|---|
| R1 | Executive summary with important details | `EXECUTIVE_SUMMARY.md` (856 lines), `summary.html`, `pages/executive-summary.html`, `docs/executive-summary.md` | **met** | file present, 856 lines | Content not re-read line by line here; prior sessions' verification records cover it. |
| R2 | Polished marketing-style affiliate site, not generic AI-looking | Landing `index.html` (live at <https://kanlerxz87-cyber.github.io/Zone2/>), `marketing/**`, `journal/**`, `design-notes.html` | **partial** | Live landing fetched 2026-11-16: hero, verified product cards, disclosure line, article teasers render | Visual polish **not assessed** (no screenshot review). Copy is evidence-led, not a sales template. |
| R3 | Catchy, trendy articles and topics on the product category | `journal/` (3 articles), `marketing/articles/` (p1–p3), `marketing/topics/` (9 topic pages), `marketing/trending-topics.html` | **partial** | Directory listing and landing teasers | Topic rows are editorial ideas; they carry no sourced data and no official link (see §3). Trend claims are not backed by a trend data source (see R9). |
| R4 | Organic traffic that real people can use to buy, based on the site's information | `audit/traffic.html`, `marketing/**`, product cards with listing links | **partial** | Listing links on the landing point to `amazon.com/dp/...` | Traffic and conversion metrics are **blank** (no analytics, no Associates reports). Organic-ranking claims are not made. |
| R5 | Suggestions section to review and choose before any change is implemented | `pages/suggestions.html` (anchors `SG-01`…`SG-12`), `audit/suggestions.html` (a separate board; its item count is not re-tallied here), `paths.html` (three decision paths), `console/decisions.html` | **met** | Anchors `SG-01`…`SG-12` present in `pages/suggestions.html` (grep, 2026-11-16) | Nothing is implemented from the board; decisions are recorded by the owner. |
| R6 | Clear list of questions, information and answers still needed | `pages/questions.html` (anchors `Q-01`…`Q-18`), `audit/gaps.html` (gap register), `discovery/questions.html` | **met** | Anchors `Q-01`…`Q-18` present in `pages/questions.html` (grep, 2026-11-16) | Q-02 (Creators API), Q-04 (domain ownership), Q-17 (website ownership) and Q-18 (whose account minted the links) need the account owner. |
| R7 | Review the repo line by line against official sources, with links for manual review; flag irregularities | `review-2026-11-15.html` (irregularities R86-01…R86-08), `docs/review-*.md`, `pages/flags.html` (F-01…F-35), `flagged.html`, `docs/coverage-970d11d6.md` (this file, §3–§4) | **met** | Flag register present; F-35 confirmed as the one published flag without an official link (see §3) | — |
| R8 | GitHub Pages live site, clean landing, subpages by category, simple dashboard | Live: `https://kanlerxz87-cyber.github.io/Zone2/`. Category subpages `pages/categories/*` (11 category pages + index), `pages/modules/*` (12 modules), `console/*` (owner dashboard) | **met** | Pages API: `status: built`, source `main` `/`. Latest `main` runs `Build, verify and deploy` = success (PRs #129, #130) | Live fetch of the root returned the landing with no error. |
| R9 | Every table row has a source link to an official site | See §2 (row-level count) | **partial** | Counts re-run this session (§2) | 1 published flag row has no link (F-35); 4 niche rows, 5 tracking rows, 6 editorial topic rows, 41 playbook suggestion rows and 6 verification summary rows have no official link. See §3. |
| R10 | If a value cannot be confirmed from an official source, leave it blank and flag it as unverified | Product attributes `price`, `rating`, `reviewCount`, `availability` are `null` in `assets/js/data.js` and show "— unverified —" on the landing | **met** | Node parse of `assets/js/data.js` (2026-11-16): `PRODUCTS` price/rating/reviewCount/availability all null | Blank is shown for price, rating, review count and availability on every product. |
| R11 | Amazon Associates compliance and disclosure | `compliance.html`, `pages/compliance.html`, disclosure line on every page (checked by `.github/workflows/pages.yml`) | **met** | Landing shows "As an Amazon Associate I earn from qualifying purchases." | Disclosure wording is the site's own; not re-checked against the Operating Agreement in this session. |
| R12 | Automated product research, trend detection, pricing, review and competition analysis | `pages/modules/m-01…m-12` | **owner-blocked** | 6 of the 12 module pages contain the word "scaffolded" (grep, 2026-11-16); the other six were **not** checked for their status wording | The Creators API is not connected (F-05 / Q-02). No live catalog, price, review or competition data is collected. The brief's "automation" is **not** operational. |
| R13 | Track clicks and conversions; optimise campaigns | `pages/tracking.html`, `tracking.html`, `tools/tracking_schema.sql` (schema only) | **owner-blocked** | Measurement register: 5 events defined, **0 live** (`discovery/measurement.html`) | No Associates reports and no live click tracking exist. CTR and conversion rows are blank (no denominator measured). |
| R14 | Publish and manage affiliate links | Supplied links (`link.amazon/…`) listed on `products.html`; `tools/link_builder.py` | **owner-blocked** | Supplied codes are 9 characters; no `tag=` parameter on any of them (F-01, F-24) — confirmed against the Associates help page in §4 S-2 | As supplied the links cannot earn Associates commission. Owner must supply the Associates ID (F-07/F-24). |
| R15 | Identify profitable niches and commission potential | `analysis.html`, `pages/niches.html`, `pages/commissions.html` (74 rows, 0 without official link) | **partial** | Commission rows are sourced to the Associates rate card | Niche demand and competition values are **UNVERIFIED** (4 rows) — no official source states them. |
| R16 | Compliance-first; no invented values | Blank-or-flag rule applied throughout | **met** | §2 counts; §4 spot checks | — |

---

## 2. Row-level source count (re-run 2026-11-16)

**Method.** (a) Root data (`assets/js/data.js`) parsed in Node v22 and every row of each table-backed array checked for an `http(s)` value. (b) Static HTML tables parsed with a regex on `<tr>`/`<td>` and checked for `href="https?://…"`. Header rows are excluded.

| Source | Rows | Rows with an official `http` link | Rows without | Note |
|---|---|---|---|---|
| `PRODUCTS` (root data) | 3 | 3 | 0 | p01–p03 all end in an Amazon listing link |
| `SPECS` | 37 | 37 | 0 | |
| `RESOLUTION_EVIDENCE` | 14 | 14 | 0 | |
| `EXEC_FACTS` | 10 | 10 | 0 | |
| `NICHE_ANALYSIS` | 8 | 8 | 0 | |
| `COMMISSION_ROWS` | 7 | 7 | 0 | |
| `COMPLIANCE_ROWS` | 13 | 13 | 0 | |
| `CONTENT_ROWS` | 6 | 6 | 0 | |
| `TRACKING_ROWS` | 4 | 4 | 0 | |
| `FLAGGED_ROWS` | 40 | 39 | **1** | index 34 = **F-35** (internal `README.md` count drift) — see N-1 |
| `PLATFORM_FEATURES` | 7 | — | — | a feature list with no source field, not a sourced table |
| `verification.html` (root) | 105 | 105 | 0 | |
| `pages/products.html` | 57 | 57 | 0 | |
| `pages/commissions.html` | 74 | 74 | 0 | |
| `pages/sources.html` | 43 | 43 | 0 | |
| `pages/verification.html` | 95 | 89 | 6 | the 6 are status-count summary rows (FLAGGED/OBSERVED/REFUTED …) |
| `pages/flags.html` | 43 | 42 | 1 | F-35 (same row as above) |
| `pages/niches.html` | 14 | 10 | 4 | the 4 are **UNVERIFIED** rows (no official source states the value) |
| `pages/tracking.html` | 11 | 6 | 5 | rows read "not published / not connected / measured here" — no external value |
| `playbook.html` | 82 | 41 | 41 | design-suggestion rows (DP-…), not data rows |
| `marketing/trending-topics.html` | 6 | 0 | 6 | editorial topic ideas, not sourced data |

**Reading.** Every data row of the root dataset that carries a value has an official link, with **one** exception (F-35). The linkless rows elsewhere are blank-by-design, summary, suggestion or editorial rows. The literal wording "every table row must have a source link" is therefore **not** met for those rows, even though the blank-or-flag rule is applied to their values. Owner decision needed (see N-2).

---

## 3. Irregularities raised by this audit (for owner review; non-blocking)

| ID | Finding | Evidence | Proposed owner action |
|---|---|---|---|
| **N-1** | Flag **F-35** (`FLAGGED_ROWS[34]`, `pages/flags.html`) has no official-source link. Its source is the repository's own `README.md` and test count. | Node parse of `assets/js/data.js`; `pages/flags.html` row | Either link the row to the GitHub file (`README.md` / `tests/test_pipeline.py`) and label it *internal, not official*, or accept it as an internal-only flag. **Not edited here** — `ledger/flags.json` is owned by the flags owner. |
| **N-2** | Rows marked UNVERIFIED, editorial topics, playbook suggestions and summary-count rows carry no official link (4 + 5 + 6 + 41 + 6 rows, §2). | §2 | Decide whether "every row" means every *data* row (current practice) or every row including UNVERIFIED ones. If the latter, each UNVERIFIED row should cite the official page where the value was looked for. |
| **N-3** | The model-number binding for the first supplied link is recorded as **verified** in `ledger/products.json` (`Model number: RJ38-SQPF-3TDB-2W`, status `verified`, cited to the Chefman page). This session re-observed the Chefman page (model and "Max temp: 450ºF/235ºC with Hi-Fry" both present) and the Amazon listing title for B0CDY277D3 (matches). **The Amazon part-number field was not re-observed** — chunks 0 and 9 of 17 were read; the item-details block lies in a later chunk. | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer>; <https://www.amazon.com/dp/B0CDY277D3> | Re-read the Amazon item-details block for B0CDY277D3 and confirm the part number. Until then, treat the model binding as **carried, not re-verified this session**. |
| **N-4** | Feature count disagreement between two official sources for the Emeril oven. Amazon title (as displayed on the landing card) says "**24** cooking functions"; the manufacturer page states "**25** Cooking Pre-sets". The landing shows the Amazon title as the product description, so the card repeats a figure the manufacturer contradicts. | Live Emeril page (2026-11-16): "25 Cooking Pre-sets"; Amazon listing title for B09B7SB46R (landing card text) | Owner to decide whether to show the manufacturer's count, the Amazon count, or neither. No spec row in the data uses either figure. |
| **N-5** | The "AI-powered platform" framing is stronger than the operating state: all 12 modules are scaffolded, 0 of 5 measurement events are live, and the Creators API is not connected. | `pages/modules/*`, `discovery/measurement.html`, F-05 | Keep the "scaffolded" label visible wherever the platform is described. This is a presentation risk, not a data error. |
| **N-7** | Question-ID drift on the board. `COORDINATION.md` (T40 row and its record) says Q-17 is "were these links minted under your Associates ID". On the live register that question is **Q-18**; **Q-17** is "do you own the website you will declare". | `pages/questions.html` (`id="Q-17"`, `id="Q-18"`) | Owner of the board to correct the references. Not edited here (`COORDINATION.md` is shared; this session appends only its own record). |
| **N-6** | The coordination board (`COORDINATION.md`) is ~520 KB / ~5,230 lines and several rows still read "in progress" after their owners' closing records (already logged as I-C/I-D by earlier sessions). | `wc -l COORDINATION.md` | Owner to consider archiving closed records. Not changed here. |

---

## 4. Spot checks performed this session (what was actually fetched)

| # | URL (official source) | What was observed on 2026-11-16 | Result |
|---|---|---|---|
| S-1 | <https://kanlerxz87-cyber.github.io/Zone2/> (live landing) | Title "Zone2 — Verified Amazon Affiliate Marketing Platform"; hero; three product cards; disclosure line; article teasers | **Matches** the repo's landing content |
| S-2 | <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC> (Associates Help, simple text link) | "ASIN is the 10-digit code"; link format `…/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID` | **Confirms** the 9-character finding (F-01) and the no-`tag=` finding (F-24) against the official rule |
| S-3 | <https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-68884e8aa630b24a&channelId=704&plpRedirect=mhFallback> (chunks 0 and 9 of 17) | Title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven …"; category path Home & Kitchen › … › Air Fryers | **Matches** the ledger's resolved title and category path. Part-number block not reached (N-3). |
| S-4 | <https://chefman.com/products/turbofry-touch-dual-window-air-fryer> (chunk 0 of 3) | Model `RJ38-SQPF-3TDB-2W`; "Max temp: 450ºF/ 235ºC with Hi-Fry function"; 1307 reviews on the page | **Matches** the ledger's manufacturer rows for model and max temperature |
| S-5 | <https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360> (chunk 0 of 6) | Model `4-00675-02A-VN`; "26-Quart Capacity"; "24.6 Liters"; "25 Cooking Pre-sets"; price shown as $199.99 (manufacturer price — not used on the site) | **Matches** capacity; **differs** from the Amazon title on the preset count (N-4). The price is a manufacturer price and is correctly not displayed as an Amazon price. |
| S-6 | <https://link.amazon/B04G1MEwY> (supplied link) | Resolves to `amazon.com/dp/B0CDY277D3`, carrying a `btn_ref=srctok-…` token (the ledger records that the token changes between fetches; not re-tested here) | **Matches** F-03 / the ledger's "honoured lookup" wording |

**Not re-fetched this session** (cited by earlier verification records, not re-observed here): the Associates Operating Agreement, Program Policies, the FTC *Disclosures 101* page, and Google's Search policy pages. Do not treat their wording as re-verified today.

---

## 5. What this session did **not** do

- No table row, value, price or flag was changed, added or removed.
- No page on the live site was edited; no shared output (`index.html`, navigation, `sitemap.xml`, `ledger/**`) was touched.
- No Amazon Associates ID, Creators API credential or account login was requested or used.
- Visual design was not screenshot-reviewed.

## 6. Owner actions that unblock the brief (unchanged; listed for the decision board)

1. Confirm the intended products for the three supplied codes (F-01, F-03) in Associates Central.
2. Supply the Associates ID and target marketplace; re-issue the links with `tag=` (F-07, F-24).
3. Apply for Creators API access, which is the only route to live price, rating and review data (F-05, Q-02).
4. Decide the "every row" wording for UNVERIFIED and editorial rows (N-2) and the F-35 link (N-1).
5. Correct the board's question references (N-7): the Associates-ID question is **Q-18**, not Q-17.
