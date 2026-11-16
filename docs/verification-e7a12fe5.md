# Line-by-line official-source verification — 2026-11-16 (session `arena/e7a12fe5-zone2`, task T40)

**Purpose.** A fresh, dated line-by-line re-verification of the official sources that the published site and registers rest on, plus the three supplied `link.amazon` short links. Nothing here infers a value: anything not confirmable from the official page named beside it is left blank and flagged. All fetches were performed live on 2026-11-16 UTC through the workspace fetch path (sandbox shell TLS to Amazon is blocked; that limitation is noted where it applies).

## 1. Official sources re-checked live

| # | Claim checked | Official source | Result |
|---|---|---|---|
| 1 | Associates Program Operating Agreement — update date and §5 mandatory Site disclosure sentence | https://affiliate-program.amazon.com/help/operating/agreement | Verified. Live page states **Updated: October 15, 2025**. §5 disclosure sentence present. |
| 2 | Associates Program Policies — update date, Commission Income Statement §1 attribution window, Participation Requirements, IP License | https://affiliate-program.amazon.com/help/operating/policies | Verified. Live page states **Updated: April 14, 2026**. §1, §6, IP License sections present as cited by the register. |
| 3 | Standard Commission Income Statement — Table 1 fixed rates and Prime bounty events | https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ | Verified. Table 1 matches `ledger/commission_table.json`; Kitchen 4.50%, Home 3.00%, All Other 4.00%; Prime bounties $12.00. |
| 4 | ASIN definition and tagged Special Link format (ASIN is a 10-digit code) | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | Verified. Page states ASIN is the 10-digit code and documents the tagged link format. Enforced by `tools/asin_guard.py` (9-char tokens rejected, not repaired). |
| 5 | FTC — material connection disclosed clearly and conspicuously | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | Verified. Clear-and-conspicuous disclosure principle confirmed. |
| 6 | Google — qualify paid/affiliate outbound links with `rel="sponsored"` | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | Verified. `rel="sponsored"` documented; page last updated 2025-12-10 UTC. |

## 2. The three supplied `link.amazon` short links — re-confirmed

Each supplied code is **9 characters**; Amazon defines an ASIN as a **10-digit** code (source 4). `https://www.amazon.com/dp/<supplied code>` returns "Page Not Found" for all three. The token is an opaque service identifier, not an ASIN.

Each `link.amazon/<code>` resolves, reproducibly, to exactly one live Amazon listing, and none of the resolved URLs carries an Associates `tag=` parameter, so as supplied none can attribute commission. Amazon publishes no document binding a short code to a destination ASIN, so the mapping is observed behaviour, not documented intent (flag F-03 / F-12; Q-03 / Q-18 remain owner-open).

| # | Supplied link | Resolves to (observed) | `tag=` present? |
|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 — Chefman 6 Qt Dual Basket Air Fryer | No |
| 2 | https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R — Emeril Lagasse 26 QT French Door Air Fryer Toaster Oven | No |
| 3 | https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH — Chefman 8 Qt TurboFry Air Fryer | No |

Product tables publish only manufacturer-sourced specifications for those observed ASINs. Price, rating, review count, stock and commission band are left blank and flagged where no official source confirms them (the category band for each ASIN is not established — Q-08 / SG-08 remain owner-open).

## 3. Decision surfaces — linked and prominent

The root landing page (`index.html`) links the decision-support registers from both the primary navigation and the footer:

- **Suggestions board** — `pages/suggestions.html` (SG-01…SG-12): each row states a decision, options A/B/C, a recommended path, the questions that must be answered first, an owner decision field awaiting record in `ledger/suggestions.json`, and official sources. Nothing is implemented until a choice is recorded there.
- **Open questions register** — `pages/questions.html` (Q-01…Q-18): each row states what is verified, what is missing, how to close the gap, which suggestions it blocks, and the official source.
- Both are linked from the footer "Decisions" column and the landing "Decisions" section, so neither register can be missed by a reviewer.

## 4. Repo gates run locally (2026-11-16), all green

| Gate | Command | Result |
|---|---|---|
| Data/row sourcing gate | `python3 tools/validate_data.py` | 0 errors, 0 warnings; 43 sources, 361 rows, 40 flags, 1176 internal links checked |
| Platform guard tests | `python3 tests/test_pipeline.py` | 15/15 checks passed |
| Generated subpages vs fresh build | `python3 tools/build_site.py --check` | 39 built, 0 drifted/uncommitted |
| Stylesheet `url()` references | `python3 tools/check_css_urls.py` | 16 stylesheets, 9 local url() references, 0 broken |
| Head-metadata contract | `python3 tools/build_head_meta.py --audit` | 87 pages under contract, 0 problems |
| Executive summary vs fresh build | `python3 tools/build_summary.py --check` | summary.html checked, no drift |
| Structural audit | `python3 tools/audit_site.py` | 141 pages; fragments, spec_sources, prose_counts, namespaces, disclosure, debris, board all PASS |

## 5. Flagged irregularities (non-blocking, published for review)

Carried on the Flagged for Review page (`pages/flags.html`) and linked from the root footer; they do **not** block merge:

- **F-01 / F-03:** the three supplied codes are 9 characters (an ASIN is 10); none is established as "the product intended in the brief" by any official Amazon document.
- **F-24:** none of the three resolved `link.amazon` URLs carries an Associates `tag=` parameter; as supplied they cannot earn commission. Owner action: confirm the mapping in Associates Central and regenerate the links with the Associate ID.
- **F-05:** the Creators API account is unregistered (PA-API 5.0 is deprecated and returns `403 AccessDenied`).
- **F-08:** no performance reports exist because there is no traffic to report; no traffic, conversion or revenue figure appears anywhere on the site.

## 6. What is still owner-open (not decided by this session)

- Confirm the product → intended-ASIN mapping with the brief owner (F-01…F-03, Q-03).
- Assign decisions for SG-01…SG-12 in `ledger/suggestions.json` (nothing is implemented until a choice is recorded).
- Close or carry Q-01…Q-18 in `ledger/questions.json` (Q-02 Associate ID, Q-04 domain ownership, Q-17 declared Associates URL unblock monetisation).

---
*Prepared 2026-11-16 UTC by session `arena/e7a12fe5-zone2` (task T40). All official links fetched live this session. Sandbox shell TLS to amazon.com / affiliate-program.amazon.com is blocked; Amazon pages were read through the workspace fetch path; FTC and Google sources read the same way.*
