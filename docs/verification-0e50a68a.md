# Verification record — session `0e50a68a` (T40), 2026-11-15 UTC

**Session:** `arena/0e50a68a-zone2` · **Task:** T40 — final integration + independent verification pass for the
2026-11-15 request. **Base at claim:** `main` = `ceaf9a79` (PR #88); integrated onto `main` = `23c7fd2` (PR #96).
**Scope:** `COORDINATION.md` (append-only records + the F-42 dedup repair) and this file. No other session's
file was edited. All facts below were checked live on 2026-11-15 against the official sources listed; nothing
is carried forward from another session's notes without being re-observed here.

## 1. Supplied links — independent live re-verification (2026-11-15)

Each supplied short link was fetched live and its redirect destination read from the response itself.

| # | Supplied link | Final URL observed | Listing title (as observed) | Verdict |
|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | **Reproduced** — matches ledger S19 |
| 2 | https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included | **Reproduced** — matches ledger S20 |
| 3 | https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | **Reproduced** — matches ledger S21 |

Observations reproduced on all three:
- The resolved URLs carry `plpRedirect=mhFallback`, `lv=shuf`, `channelId=704` and a per-fetch `btn_ref=srctok-…`
  token (three distinct tokens today, different from 2026-11-14 — consistent with flag **F-21**, the
  `btn_ref` rotation between windows).
- None of the resolved URLs carries an Associates `tag` parameter — **F-24 stands**: as supplied the links
  cannot attribute a commission.
- All three destination breadcrumbs: *Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers*
  (shared category, "1 category" KPI on the landing page).
- The codes as supplied are 9 characters; Amazon's own help defines an ASIN as "the 10-digit code"
  (https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC). **F-01/F-02/F-03 stand**: the
  destinations are real listings, but no official Amazon document confirms the codes as the intended products.
- Prices and ratings are visible on the destination pages; per the program's price-display rules
  (Participation Requirements §2(b)) and this project's no-inference rule, **none is copied anywhere**.

## 2. Repository gates — replayed on the combined tree (2026-11-15)

Every gate below was executed locally on the integrated tree; results are the actual outputs.

| Gate | Result |
|---|---|
| `tools/validate_data.py` | exit 0 · 0 errors · 0 warnings · 38 flags · 42 sources · 340 rows · 1,153 internal links checked |
| `tools/build_site.py --check` | 39 built · 0 drifted |
| `tools/build_root_views.py --check` | sources.html + verification.html · 0 drifted |
| `tools/build_root_data.py --check` | `assets/js/data.js` up to date |
| `tools/build_summary.py --check` | summary.html · 0 drifted |
| `tools/build_marketing.py --check` | 21 marketing outputs (18 pages + 3 machine-readable) · committed output current |
| `marketing/scripts/verify_marketing.py` | OK · 18 pages · 48 spec rows · 0 failures (disclosure, preview labels, no prices, per-row sources, links) |
| `tools/build_decisions.py --check` | 8 built · 0 drifted · summary not stale |
| `tools/validate_decisions.py` | exit 0 · 10 suggestions awaiting decision · 16 questions open · 24 requirements · 14 cross-references checked · 0 errors |
| `tools/audit_site.py` | **116 published pages** — fragments / spec_sources / prose_counts / namespaces / disclosure: **all PASS** |
| `tests/test_pipeline.py` | **15/15** passed |
| `affiliate-lab/scripts/verify_site.py` | 206 table rows · 502 links · **0 failures** |
| `revalidation/scripts/build.py --check` + `verify.py` | 6 built · 0 drift · 73 rows · 168 refs · **0 failures** |
| `research-hub/scripts/build.py` + `verify.py` | 12 pages · 38 sourced attribute rows · **0 errors** |
| `node --check assets/js/data.js` + `app.js` | syntax OK |
| Workflow step "Internal links and asset references resolve (all sites)" (replayed verbatim from `.github/workflows/pages.yml`) | **All internal links and assets resolve** |
| Workflow step "No page prints a price and every page discloses" (replayed verbatim) | **90 pages: disclosure present, no prices printed** |
| Workflow step "Subpages disclose and never print a product price" (replayed verbatim) | **39 subpages: disclosure present, sponsored links qualified** |

## 3. Published deliverables — line-by-line review against the brief

| Brief requirement | Where it lives | Review result |
|---|---|---|
| Polished marketing affiliate site (not "AI slop") | `marketing/` (publication *Counter Notes*: articles, comparison, buying guide, topics, trending-topics, improvements board) + `journal/` | Articles carry verdict standfirsts, "who this fits"/"if that's not you" sections, honest fine-print paragraphs, per-row source links, §5 disclosure on every page; no prices, no invented ratings, no first-hand claims. **Meets the brief.** |
| Suggestions section a reviewer can use to choose the best path before implementing | `pages/suggestions.html` (SG-01…SG-10, options A/B/C, trade-off, recommendation, blocking question, status) + `marketing/improvements.html` + `decisions/requirements.html` | Decision board is linked from the landing page and dashboard callout; nothing is implemented until the owner records a decision in `ledger/suggestions.json`. **Meets the brief.** |
| Clear list of questions, information and answers to address before decisions | `pages/questions.html` (Q-01…Q-16, each with verified-now / still-missing / how-to-find / blocks) | 16 questions, each with an official-source link and a discovery action; linked from the landing page. **Meets the brief.** |
| Executive summary of important details | `EXECUTIVE_SUMMARY.md`, `summary.html`, `pages/executive-summary.html` | Covers the job, the verification discipline, what is settled, what waits on the owner, with sourced program facts. **Meets the brief.** |
| GitHub Pages live site: clean landing + subpages by category, dashboard-like, tables with entries/findings/analysis | Root dashboard (`index.html`) + `products.html`, `analysis.html`, `compliance.html`, `tracking.html`, `content.html`, `pages/` (39 generated pages incl. categories, niches, modules, commissions, flags) | Landing fetched live (cache-busted): renders KPIs, product cards with blank-or-unverified fields, decision-board callout, sourced program table. **Meets the brief.** |
| Every table row sourced to an official site; unverifiable values blank + flagged | `ledger/` dataset, all table generators, `tools/validate_data.py`, `tools/audit_site.py` | Per-row source links enforced by gates; price/rating/availability/commission band published as blanks with flags F-01…F-38. **Meets the brief.** |
| Suggestions feeding the design prompt for a polished site | `docs/design-prompt-suggestions.md`, `docs/methodology.md`, `playbook.html` | Present and linked. **Meets the brief.** |

## 4. F-42 repair — completed this session (COORDINATION.md)

The shared task board carried the deferred F-42 duplication (byte-identical session-record fragments committed
across the 2026-11-15 merge waves). This session removed **only** byte-identical duplicates, verified by
assertion before every deletion; no session's unique text was discarded.

| Duplicate removed | Identical to (kept) |
|---|---|
| `## T26 — closing record (d3ce1c29)` duplicated table rows | first copy's table rows |
| Four duplicated `###` sub-sections ("What shipped", "Verification rows added by this session", "What is still open for the owner", "Process note for whoever comes next") | first T26 copy |
| `## Session claim — 42fa4918` + `## Session record — 42fa4918 (T31)` header (second occurrence) | first occurrence (3303…3319) |
| 42fa4918 T31 record body: "Verification performed", "Findings", "T29 closing record", "T31 closing record" + "Still open for the owner" note | first occurrence |
| `8c4236ad` record body: "T32 — work record", "T32 — closing record" | first occurrence |
| Stray duplicated fragment ("in` line, and a duplicated fragment…") | substring of the canonical Scope-amendment paragraph |

Kept deliberately: the unique consolidated task-disposition rows (T28/T29/T30/T34–T37/T31/T39/T41/T38) inside
the second T26 record, and the unique T39 (`e8b071cd`) record that had been sandwiched inside the duplicated
region. Post-repair checks: **0 duplicate sections** at both `##` and `###` level, all session records
present, **0** conflict markers (the five `>>>>>>>` string matches are quoted prose inside records, not
markers). File size 4322 → 4081 lines.

## 5. Live deployment confirmation (2026-11-15, cache-busted)

- GitHub Pages API: `status: built`, source `main` `/`, https://kanlerxz87-cyber.github.io/Zone2/
- Landing fetched live with cache-buster (`?v=0e50a68a`): renders the current dashboard — KPIs "3 of 3 / 0 of 3 /
  1 category / 4.00% / 38", the Suggestions + Questions callout, three product cards with blank
  price/rating/availability, and the sourced program-facts table.
- `marketing/index.html` committed copy reviewed: publication title, disclosure, and editorial sections present.

## 6. Irregularities and open items (carried forward, non-blocking, published with sources)

1. **F-01/F-02/F-03 — product identity unconfirmed.** The three supplied codes are 9 characters (an ASIN is a
   "10-digit code", per the official Associates help page); the `link.amazon` destinations are real listings but
   no official Amazon document binds the codes to them. Owner action: confirm the intended ASINs in Associates
   Central. Source: https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC
2. **F-24 — no Associates tag.** The supplied links carry no `tag` parameter; regenerated tagged links are
   required before any sale can be attributed. Source: https://affiliate-program.amazon.com/help/operating/policies
3. **F-05 — Creators API registration.** PA-API 5 is deprecated (403); the Creators API requires an eligible
   Associates account. Source: https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction
4. **P2 listing-title drift (carried from T32).** The `B09B7SB46R` listing title observed today matches the
   2026-11-15 ledger variant; the 2026-11-14 variant differs (Amazon rotates listing copy between fetches).
   The ledger keeps its dated source; re-read next cycle. Not corrected here — `ledger/**` is out of scope.
5. **Owner questions Q-01…Q-16 remain open by design** on `pages/questions.html`; suggestions SG-01…SG-10 remain
   awaiting a recorded decision in `ledger/suggestions.json`.

## 7. Sources used (all official, all read live 2026-11-15)

| Source | URL | Used for |
|---|---|---|
| Supplied short link 1 | https://link.amazon/B04G1MEwY | link → destination re-verification |
| Supplied short link 2 | https://link.amazon/B02NbDxp3 | link → destination re-verification |
| Supplied short link 3 | https://link.amazon/B00hJ57DV | link → destination re-verification |
| Amazon listing B0CDY277D3 | https://www.amazon.com/dp/B0CDY277D3 | destination title/breadcrumb |
| Amazon listing B09B7SB46R | https://www.amazon.com/dp/B09B7SB46R | destination title/breadcrumb |
| Amazon listing B08DKYBTPH | https://www.amazon.com/dp/B08DKYBTPH | destination title/breadcrumb |
| Associates — ASIN definition / link format | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | ASIN = "10-digit code" |
| Associates Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | §5 disclosure sentence, document currency |
| Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | participation/price-display rules, F-24 basis |
| Creators API introduction | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction | API prerequisites, PA-API 5 deprecation |
| GitHub Pages API | https://api.github.com/repos/kanlerxz87-cyber/Zone2/pages | deploy status confirmation |
