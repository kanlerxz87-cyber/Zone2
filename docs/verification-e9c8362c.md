# T26 — Release verification & closing integration

**Session:** `e9c8362c` (`arena/e9c8362c-zone2`) · **Date:** 2026-11-14 (UTC) · **Tree audited:** `main` @ `6a90dfc`
(merge of PR #41) plus this branch's changes.

This report is the brief's "VERIFICATION" deliverable: every check run in this session, every value
re-read against the official page that states it, and every irregularity — with links for manual
review. Nothing here is carried forward from another session's notes without being re-checked; where
prior dated evidence is cited, it says so.

---

## 1. Repository gates — all run on this branch after the fixes

| Gate | Result |
| --- | --- |
| `tools/validate_data.py` | **exit 0** · 175 rows · 35 sources · 28 canonical flags · 976 internal links · 0 price findings · 0 mark findings · 1 known warning (F-13 title, `research-hub/compliance.html`) |
| `tools/build_site.py --check` | 37 built · 0 drifted |
| `tools/build_root_views.py --check` | 2 checked · 0 drifted |
| `tools/build_root_data.py --check` | up to date (`CANONICAL_FLAG_COUNT` derived from the ledger) |
| `tests/test_pipeline.py` | **14/14** (incl. new `test_typed_count_labels_cannot_drift_from_the_ledger`, negative-tested) |
| `affiliate-lab/scripts/verify_site.py` | 10 pages · 206 rows · 502 links · 0 failures |
| `revalidation/scripts/build.py --check` / `verify.py` | 6 built · 0 drifted / 73 rows · 168 refs · 0 failures |
| `tools/build_marketing.py --check` / `marketing/scripts/verify_marketing.py` | 9 pages current / 48 spec rows · 0 failures |
| Internal-link check (all 8 namespaces, incl. `marketing/`) | all resolve (deep sweep: 1,796 internal links/assets, none broken) |
| Disclosure + no-product-price sweep | **94 pages**: disclosure sentence present on every page · no price printed in a buying context |
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
| V-G | Each supplied `link.amazon` URL resolves to exactly one listing: B0CDY277D3, B09B7SB46R, B08DKYBTPH | Fetched all three today: titles read "CHEFMAN 6 Quart Dual Basket Air Fryer Oven…", "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…", "Chefman Air Fryer 8 Qt \| TurboFry®…" | **Reproduced today** | https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV |
| V-H | F-21: the per-link `btn_ref` token rotates across days; the destination does not | Today's fetches returned `btn_ref=srctok-704dc575…`, `…76d4981d…`, `…016f4a53…` — all different from the 2026-11-13/14 values recorded by earlier sessions, while the `/dp/` paths are unchanged | **Confirmed (new distinct values)** | resolved URLs above |
| V-I | F-24: no resolved URL carries an Associates `tag` | Resolved URLs carry `lv`, `btn_type`, `gaOptInStatus`, `btn_ref`, `channelId`, `plpRedirect` — no `tag=` | **Confirmed today** | resolved URLs above |

## 3. Per-row sourcing audit (the brief's hard rule)

Method: every `<tr>` holding data on all **94 published pages** was classified — a row must end in an
official-source link or be an explicit blank/flagged/structural cell. Run before and after the fixes
below.

| Class | Rows (after) | Disposition |
| --- | --- | --- |
| Rows with an official-source link | **867** | compliant |
| Explicit blank / flagged / explained-unavailable cells | 207 | compliant (blank + reason + flag, never inferred) |
| Repo-internal structural rows (registers, schemas, tallies, template/lint inventories, raw evidence URLs) | 54 | not external-world values; each names its file, flag id or raw URL — listed in §5 |

**Fix applied (per-row gap closed):** `pages/niches.html`'s "published 0.00% categories" table was
block-sourced (source chip on the panel, none in the rows). `tools/build_site.py` now emits a Source
column with the Table 1 source (S04) in every one of the nine rows; `pages/` regenerated.

**Flagged instead of fixed (F-28 / CR-7):** `research-hub/summary.html` rollup tables (21 rows) state
product and policy values without per-row links. The values are sourced one level down (the hub's
per-product pages carry per-row Amazon/manufacturer links) — it is a presentation gap in a preserved
companion namespace owned by another session, so it is published on the Flagged for Review page and
logged as change request CR-7 in `COORDINATION.md`, per the coordination rules. The other 33
structural rows live in `research-hub/flagged.html` (11 register rows), `pages/content-engine.html`
(9 lint-code rows), `pages/verification.html` (4 tally rows), `pages/tracking.html` (3 schema rows),
`affiliate-lab/sources.html` (3 failed-lookup register rows) and `revalidation/links.html` (3 raw
resolved-URL evidence rows).

## 4. Line-by-line findings in this pass

| # | Finding | Evidence | Disposition |
| --- | --- | --- | --- |
| 1 | **F-27 — typed counts drifted from the registers.** `README.md` said "flagged for review (14 items)", "verification log (32 checks)", "source register (22 sources)", "11 executable guard checks" while the ledgers hold 28 flags / 50 verification rows / 35 sources / 14 tests. `index.html` and `flagged.html` typed the flag count too. Same defect class as F-17 and F-26: a typed number with no gate behind it. | `README.md` @ `6a90dfc` lines 45–50, 144 vs `ledger/flags.json`, `ledger/verification.json`, `ledger/sources.json`, `tests/test_pipeline.py` | **Fixed.** Labels corrected; new gate `tools/validate_data.py::check_typed_counts` pins every typed count label to the ledgers; negative-tested in `tests/test_pipeline.py`. Published as F-27 (closed). |
| 2 | **F-28 — hub rollup rows lack per-row source links** (see §3). | per-row audit; `research-hub/summary.html` rows 1–3, 5–8 | **Flagged for review** (F-28, open) + CR-7; `research-hub/**` not edited. |
| 3 | `pages/niches.html` exclusions table lacked per-row source links (see §3). | per-row audit | **Fixed** (Source column, S04 per row). |
| 4 | Carry-forward irregularities re-confirmed today, unchanged: supplied codes are 9 characters (an ASIN is 10, V-E) and `/dp/<code>` is Page Not Found (V-F); no Associates `tag` on any resolved URL (V-I); `btn_ref` rotates across days (V-H); F-13 title warning on `research-hub/compliance.html`; I-27 (`research-hub/scripts/verify.py` stale after the namespace move). | §2 | remain published on the Flagged for Review page; none block the merge. |

## 5. Live site check (GitHub Pages)

`https://kanlerxz87-cyber.github.io/Zone2/index.html?v=e9c8362c` was fetched after the last deploy
(cache-buster used, per the CDN note in `COORDINATION.md`): the landing renders the corrected state
("0 of 3 Brief product mappings confirmed by an official Amazon document", "3 of 3 supplied links
resolve", 26→28 flags after this merge), the disclosure strip is present, and the Verified Platform
Facts table matches §2 row for row. Final deploy verification after the merge is recorded in
`COORDINATION.md` (closing entry).

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
