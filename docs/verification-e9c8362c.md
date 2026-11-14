# T28 — Release verification & closing integration

**Session:** `e9c8362c` (`arena/e9c8362c-zone2`) · **Date:** 2026-11-14 (UTC) · **Trees audited:** `main` @ `6a90dfc`
(first pass) and the merged tree after `origin/main` @ `29589f3` (PRs #42–#47) was integrated additively.

This report is the brief's "VERIFICATION" deliverable: every check run in this session, every value
re-read against the official page that states it, and every irregularity — with links for manual
review. Nothing is carried forward from another session's notes without being re-checked; where prior
dated evidence is cited, it says so.

---

## 1. Repository gates — all run on the final merged tree

| Gate | Result |
| --- | --- |
| `tools/validate_data.py` | **exit 0** · 199 rows · 37 sources · 30 canonical flags (F-01…F-30) · 979 internal links · 0 price findings · 0 mark findings · **0 warnings** |
| `tools/build_site.py --check` | 37 built · 0 drifted |
| `tools/build_root_views.py --check` | 2 checked · 0 drifted |
| `tools/build_root_data.py --check` | up to date (`CANONICAL_FLAG_COUNT` derived from the ledger) |
| `tests/test_pipeline.py` | **15/15** (incl. this session's `test_typed_count_labels_cannot_drift_from_the_ledger`, negative-tested) |
| `tools/audit_site.py` | 95 pages audited — fragments / spec_sources / prose_counts / namespaces / disclosure **PASS** |
| `research-hub/scripts/verify.py` | 13 pages · 38 sourced attribute rows · 0 errors (repaired verifier, in CI) |
| `affiliate-lab/scripts/verify_site.py` | 10 pages · 206 rows · 502 links · 0 failures |
| `revalidation/scripts/build.py --check` / `verify.py` | 0 drifted / 73 rows · 168 refs · 0 failures |
| `tools/build_marketing.py --check` / `marketing/scripts/verify_marketing.py` | 9 pages current / 48 spec rows · 0 failures |
| Internal links (deep sweep, all namespaces) | 1,796 references · none broken |
| Disclosure + no-product-price sweep | **95 pages**: disclosure sentence on every page · no price printed in a buying context |
| `node --check` on `assets/js/data.js`, `assets/js/app.js` | OK |

## 2. Official sources re-read live on 2026-11-14 (this session's own fetches)

| # | Claim as published on this site | What the official page says (read today) | Verdict | Source |
| --- | --- | --- | --- | --- |
| V-A | Mandatory disclosure sentence on every page | OA §5: "You must clearly and prominently state … 'As an Amazon Associate I earn from qualifying purchases.'" | **Verified verbatim** | [Operating Agreement §5](https://affiliate-program.amazon.com/help/operating/agreement) |
| V-B | Document currency: OA 15 Oct 2025; Policies 14 Apr 2026 | "Updated: October 15, 2025" / "Updated: April 14, 2026" | **Verified** | OA · [Program Policies](https://affiliate-program.amazon.com/help/operating/policies) |
| V-C | Session ends at 24 h / order / competing click; cart-add ≤ 89 days; ship-pay ≤ 180 days | Commission Income Statement §1, verbatim | **Verified** | [Program Policies §1](https://affiliate-program.amazon.com/help/operating/policies) |
| V-D | Eleven fixed rate bands, 10.00 % → 0.00 %, plus "All Other Categories 4.00 %"; nine category groups at 0.00 % | Table 1 as published (Luxury Beauty 10.00 % … Coach 0.00 %, All Other 4.00 %) | **Verified row by row** | [Table 1](https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) |
| V-E | An ASIN is a 10-digit code; the qualifying link format is `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID` | "ASIN is the 10-digit code that Amazon uses to denote specific products"; the tagged format is shown verbatim | **Verified verbatim** | [ASIN / simple text link help](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| V-F | `amazon.com/dp/B04G1MEwY` (and the other two supplied codes) is Page Not Found | "Sorry! We couldn't find that page." (Page Not Found) | **Reproduced today** | https://www.amazon.com/dp/B04G1MEwY |
| V-G | Each supplied `link.amazon` URL resolves to exactly one listing: B0CDY277D3, B09B7SB46R, B08DKYBTPH | Fetched all three today: titles read "CHEFMAN 6 Quart Dual Basket Air Fryer Oven…", "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…", "Chefman Air Fryer 8 Qt \| TurboFry®…" — matching the ledger rows | **Reproduced today** | https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV |
| V-H | F-21: the per-link `btn_ref` token rotates across days; the destination does not | Today's fetches returned three **new** distinct `srctok-…` values (`704dc575…`, `76d4981d…`, `016f4a53…`) while the `/dp/` paths are unchanged | **Confirmed** | resolved URLs above |
| V-I | F-24: no resolved URL carries an Associates `tag` | Resolved URLs carry `lv`, `btn_type`, `gaOptInStatus`, `btn_ref`, `channelId`, `plpRedirect` — no `tag=` | **Confirmed today** | resolved URLs above |

## 3. Per-row sourcing audit (the brief's hard rule)

Method: every `<tr>` holding data on all **95 published pages** was classified — a row must end in an
official-source link or be an explicit blank/flagged/structural cell. Run before and after the fixes;
final numbers on the merged tree:

| Class | Rows | Disposition |
| --- | --- | --- |
| Rows with an official-source link | **872** | compliant |
| Explicit blank / flagged / explained-unavailable cells | 207 | compliant (blank + reason + flag, never inferred) |
| Repo-internal structural rows (registers, schemas, tallies, lint/template inventories, file inventories, raw evidence URLs) | 51 | not external-world values; each names its file, flag id or raw URL |

**Fixed in this session:** `pages/niches.html`'s "published 0.00% categories" table was block-sourced
only (source chip on the panel, none in the rows). `tools/build_site.py` now emits a Source cell with
the Table 1 source (S04) in each of the nine rows.

**Fixed on `main` during the parallel wave (verified here):** the hub's three product-mapping rows in
`research-hub/summary.html` gained per-row "Official product source" links (manufacturer + Amazon).

**Flagged instead of edited (F-29 / CR-7 partial):** eight external-value rows in
`research-hub/summary.html` remain block-sourced — the four policy-verdict rows (price, star rating,
review count, stock) and the four cross-source conflict rows (I-9, I-10, I-12, I-13). Their values
are sourced on the hub's per-product pages; it is a presentation gap in a preserved companion
namespace owned by another session, so it is published on the Flagged for Review page and logged as
change request CR-7 (partial) in `COORDINATION.md`, per the coordination rules. The remaining
structural rows: `research-hub/flagged.html` (11 register rows), `pages/content-engine.html` (9
lint-code rows), `pages/verification.html` (4 tally rows), `pages/tracking.html` (3 schema rows),
`affiliate-lab/sources.html` (3 failed-lookup register rows), `revalidation/links.html` (3 raw
resolved-URL evidence rows).

## 4. Line-by-line findings in this pass

| # | Finding | Evidence | Disposition |
| --- | --- | --- | --- |
| 1 | **F-30 — README prose counts drifted from the registers three times in one day.** At `6a90dfc` README.md said "14 items / 32 checks / 22 sources / 11 executable guard checks" against registers holding 26 flags / 50 rows / 35 sources / 13 tests; at `29589f3` it read "26 items, F-01…F-26" against 27 flags; at `cefb53a` it read "13 executable guard checks" against a 14-test suite. Same defect class as F-17/F-26, one layer the existing gates did not reach. | README.md at those commits vs `ledger/*.json` and `tests/test_pipeline.py` | **Fixed + gated.** Labels now state the ledger values; `tools/validate_data.py::check_typed_counts` pins every README count label (flags / verification checks / sources / executable guard checks) to the ledgers and asserts the root captions keep their derived markers (`flagCountHeading`, `flagRegisterCount`) instead of typed prose. Negative-tested in `tests/test_pipeline.py::test_typed_count_labels_cannot_drift_from_the_ledger` (a wrong README count turns the gate red; the file is restored afterwards). Published as F-30 (closed). Renumbered twice by ID collisions with parallel sessions (see `COORDINATION.md`). |
| 2 | **F-29 — hub rollup residual** (see §3). | per-row audit on the merged tree | **Flagged for review** (F-29, open) + CR-7 (partial); `research-hub/**` not edited. |
| 3 | `pages/niches.html` exclusions table lacked per-row source links (see §3). | per-row audit | **Fixed** (Source column, S04 per row). |
| 4 | **Merge-conflict reconciliation (two waves, 31 + 30 files).** `origin/main` advanced twice mid-task (PRs #42–#47, then PRs #48/#51/#53). Main's derived count captions (`b38cc982`) superseded this session's typed literals; this session's flags were renumbered twice by ID collisions (finally F-29/F-30); main's own `check_no_typed_flag_counts` gate caught `EXECUTIVE_SUMMARY.md`'s stale "28 flags" phrase when this session's flags landed (the class gate proving itself); and the region-patching generator silently preserved merge markers inside `assets/js/data.js`, caught by `node --check` and fixed by regenerating from a clean base. Full log in `COORDINATION.md`. | git merges of `origin/main` @ `29589f3` and `cefb53a` | **Resolved additively; nothing discarded.** |
| 5 | Carry-forward irregularities re-confirmed today, unchanged: supplied codes are 9 characters (an ASIN is 10, V-E) and `/dp/<code>` is Page Not Found (V-F); no Associates `tag` on any resolved URL (V-I); `btn_ref` rotates across days (V-H). Open items from the parallel wave re-verified as still open: **F-27** (`research-hub/scripts/build.py` deletes its own output before reading inputs — one run wipes the hub pages; never run it in this tree), **CR-1** (`northstar/` badge "03" vs the register). **CR-2** (dead `data/*.json` links in `EXECUTIVE_SUMMARY.md`) verified **already resolved** on `main`. | §2 + file reads | remain published on the Flagged for Review page / coordination log; none block the merge. |

## 5. Live site check (GitHub Pages)

`https://kanlerxz87-cyber.github.io/Zone2/index.html?v=e9c8362c` was fetched during this session with
a cache-buster (per the CDN note in `COORDINATION.md`): the landing renders the corrected state ("0
of 3 brief product mappings confirmed", "3 of 3 supplied links resolve", derived flag KPI), the
disclosure strip is present, and the Verified Platform Facts table matches §2 row for row. The final
post-merge deploy verification is recorded in `COORDINATION.md` (closing entry).

## 6. Links for manual review

- Amazon Associates Program Operating Agreement — https://affiliate-program.amazon.com/help/operating/agreement
- Amazon Associates Program Policies — https://affiliate-program.amazon.com/help/operating/policies
- Standard Commission Income Statement (Table 1) — https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ
- ASIN definition / qualifying link format — https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC
- Supplied links (as given) — https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV
- Canonical lookups of the supplied codes (Page Not Found) — https://www.amazon.com/dp/B04G1MEwY · https://www.amazon.com/dp/B02NbDxp3 · https://www.amazon.com/dp/B00hJ57DV
- Observed destinations (evidence only, F-01…F-03) — https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B09B7SB46R · https://www.amazon.com/dp/B08DKYBTPH
- Site registers — [Flagged for Review](https://kanlerxz87-cyber.github.io/Zone2/flagged.html) · [pages/flags.html](https://kanlerxz87-cyber.github.io/Zone2/pages/flags.html) · [pages/verification.html](https://kanlerxz87-cyber.github.io/Zone2/pages/verification.html) · [pages/sources.html](https://kanlerxz87-cyber.github.io/Zone2/pages/sources.html)

---

*Nothing in this report was inferred: every "Verified" verdict names the page that states the value,
read live on 2026-11-14; every value without such a page is blank and flagged.*
