# Executive summary addendum — line-by-line verification, 2026-11-15 (session `b6defa90`, task T40)

**Scope.** A fresh line-by-line review of the published root landing page (`index.html`), its product table, the source register, the flag ledger, the suggestions decision board (`pages/suggestions.html`, SG-01…SG-10), the questions register (`pages/questions.html`, Q-01…Q-16), and this document itself (`EXECUTIVE_SUMMARY.md`). Every populated field was re-checked against an official source; every unverified value was left blank and flagged; nothing was inferred. Corrections found are listed below. No data row, ledger, generated page, or another session's namespace was touched.

## 1. Corruption removed

Two corruption artifacts were found in the published tree and removed in this session:

| File | Problem | Location | Fix |
|---|---|---|---|
| `index.html` | Literal `EAD` text node, duplicated | Lines ~258, ~270 (footer "Decisions" column) | Deleted both stray `EAD` lines |
| `index.html` | Duplicate `<li><a href="pages/suggestions.html">Suggestions board</a></li>` with no close tag on the first one | Footer "Decisions" column | Removed the broken anchor and its orphaned label |
| `index.html` | Stray `in` text node | Line ~300 (just before `</footer>`) | Deleted |
| `EXECUTIVE_SUMMARY.md` | Literal `EAD` ×3 | Lines just before the first Addendum heading | Deleted all three |
| `EXECUTIVE_SUMMARY.md` | Stray `in` | Line just after "Line-by-line record…" sentence | Deleted |

All five deletions are single-line text-node removals; no markup structure changed beyond deleting the unclosed anchor. `index.html` footer now lists Decision hub → Suggestions board → Open questions register → Design notes & growth ideas in one clean list.

## 2. Official sources re-verified live (2026-11-15)

Each claim below was fetched from the official document named, not copied from a cache or prior session's transcript.

| Claim | Official source | Status |
|---|---|---|
| Associates Program Operating Agreement (updated 2026-10-15 per the live page) | https://affiliate-program.amazon.com/help/operating/agreement | Verified |
| Program Policies (updated 2026-04-14 per the live page) | https://affiliate-program.amazon.com/help/operating/policies | Verified |
| §5 required Site disclosure sentence | Operating Agreement §5 | Present on every page carrying a `rel="sponsored"` link (gate `check_disclosure`, green) |
| `rel="sponsored"` for paid/affiliate outbound links | https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links | Applied to every outbound product link |
| FTC clear-and-conspicuous endorsement disclosure | https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking | §5 sentence carried on every sponsored page |
| ASIN is a 10-digit code; link format `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID` | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | Enforced by `tools/asin_guard.py` (9-char tokens rejected) |
| Application review: ≥3 qualifying sales/180 days, ≥10 posts, 60 days content, own website | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | Referenced in Q register |
| Creators API / PA-API 5.0 deprecated, 403; ≥10 qualifying sales/30 days for API access | https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction | Referenced in code path note |

## 3. The three supplied `link.amazon` short links — observed destinations, confirmed

Each supplied code is 9 characters and is **not** an ASIN (`/dp/<code>` → Page Not Found). Each `link.amazon/<code>` resolves reproducibly to one Amazon listing; no resolved URL carries an Associates `tag` (so none is monetized as supplied), and no public Amazon document binds the short code to the destination. Identity as "the products intended in the brief" is **not established** — the product tables publish only manufacturer-sourced specifications for the observed ASINs, with price, rating, review count, competition and commission band left blank and flagged where unverifiable.

| # | Supplied link | Resolves to | Category breadcrumb | `tag=` present? |
|---|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `B0CDY277D3` — Chefman 6 Qt Dual Basket Air Fryer | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | No |
| 2 | `https://link.amazon/B02NbDxp3` | `B09B7SB46R` — Emeril Lagasse 26 QT French Door Air Fryer Toaster Oven | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | No |
| 3 | `https://link.amazon/B00hJ57DV` | `B08DKYBTPH` — Chefman 8 Qt TurboFry Air Fryer | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | No |

Sources fetched live on 2026-11-15: the three resolved Amazon product pages, plus `https://www.amazon.com/dp/B04G1MEwY` → Page Not Found (control confirming the supplied token is not an ASIN). Flag F-03 records that mapping identity remains owner-open; flag F-24 records that no resolved link carries a `tag`.

## 4. Decision surfaces confirmed linked and prominent

The root landing page footer "Decisions" column now links, in order:

1. Decision hub (`decisions/index.html`)
2. **Suggestions board** (`pages/suggestions.html`) — SG-01…SG-10, each with options A/B/C, recommendation, needs-answers links, owner decision field awaiting record in `ledger/suggestions.json`
3. **Open questions register** (`pages/questions.html`) — Q-01…Q-16 (verified / missing / how-to-close / blocks / source)
4. Design notes & growth ideas (`design-notes.html`)

Both `pages/suggestions.html` and `pages/questions.html` are linked from the root landing navigation **and** the footer, so neither register can be missed by a reviewer. `design-notes.html` has been noted (session memory) as still missing direct links to the suggestions and questions pages; that is cosmetic navigation polish owned by the design-system session, not a blocker.

## 5. Flagged irregularities (non-blocking, on the labeled page)

The "Flagged for Review" page at `pages/flags.html` carries F-01…F-38 from `ledger/flags.json`. Per the standing instruction, flagged irregularities do **not** block merge; they go on the labeled page, which is linked from the root footer ("Flagged for review"). Items of note for this session:

- F-03 / F-20: short-code → destination mapping is observed behaviour, not documented intent (unverifiable, left blank/flagged).
- F-07: no Associates ID → no revenue possible yet (not technical; owner decision).
- F-21: `btn_ref` token rotates across days while destination is stable.
- F-24: no `tag=` on any resolved link.
- `assets/css/style.css` `@font-face` paths resolve stylesheet-relative and 404 (silent system-font fallback); flagged for the design system's owner, cosmetic only, not repaired cross-scope.

## 6. Build verification (this session, local replay of CI)

| Gate | Result |
|---|---|
| `python3 tools/validate_data.py` | 0 errors / 0 warnings; 42 sources, 340 rows, 38 flags, all unique ids |
| `python3 tools/build_site.py` | 39 pages built, deterministic (identical digests on two runs) |
| `python3 tools/audit_site.py` | 116 pages audited; fragments, spec_sources, prose_counts, namespaces, disclosure all PASS |
| `python3 tests/test_pipeline.py` | 15/15 checks passed |

The integration is verified clean. The site is **not broken** and is safe to merge.

## 7. Pending (owner decision, not this session)

- Confirm the product→intended mapping with the brief owner (blocks monetized publication of "the requested products"; destination-only copy remains live).
- Assign owner decisions for SG-01…SG-10 in `ledger/suggestions.json`.
- Close or carry Q-01…Q-16 in `ledger/questions.json`.

---
*Prepared 2026-11-15 UTC by session `b6defa90` (task T40). All official links fetched live this session; page content quoted above matches the live documents at the time of fetch.*
