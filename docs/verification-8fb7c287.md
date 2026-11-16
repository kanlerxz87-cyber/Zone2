# Line-by-line verification — 2026-11-16 — session `arena/8fb7c287-zone2` (`8fb7c287`)

**Task:** T50 — close change requests CR-A…CR-D (filed by session `5d6d2254`, T42, never dispositioned on the
board) and T49's F-20 wording item, with a fresh dated verification pass over the official sources the
published surfaces rest on.

**Method.** Every live check below was run on **2026-11-16 (UTC)** with the workspace page fetcher, because
sandbox shell TLS is blocked (`SSL_ERROR_SYSCALL` on outbound `curl`) — the same channel session `224cc10c`
(T49) used the same day. No value in this record is inferred; anything not observed is marked as such. The
repository gate suite (`python3 tools/ci_replay.py`, all 35 workflow steps) was run on the final tree.

**Files changed by this session** (all others untouched): `ledger/flags.json` (F-20 wording only),
`ledger/products.json` (P-02 accessories row, file note, reverification stamp), `marketing/data/facts.json`
(P2 accessories row, P2 `title_note`, file note), `marketing/data/editorial.json` (guide blocks citing the
accessory count, DS-14 roadmap clause), regenerated outputs via the existing builders only, this document,
and `COORDINATION.md` (append-only records).

---

## 1. The three supplied short links — destination check (4th consecutive date)

| # | Supplied link | Observed destination, 2026-11-16 | Published in `ledger/products.json` | Verdict |
|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | `https://www.amazon.com/dp/B0CDY277D3` — title "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black", Air Fryers breadcrumb, fresh `btn_ref=srctok-68884e8aa630b24a`, no `tag=` | P-01 → `B0CDY277D3` | **MATCHES** |
| 2 | https://link.amazon/B02NbDxp3 | `https://www.amazon.com/dp/B09B7SB46R` — title "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, **Six Cooking Accessories Included**", fresh `btn_ref=srctok-662480f5bd825c83`, no `tag=` | P-02 → `B09B7SB46R` | **MATCHES** |
| 3 | https://link.amazon/B00hJ57DV | `https://www.amazon.com/dp/B08DKYBTPH` — title "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel", fresh `btn_ref=srctok-38bef00eb1e962ef`, no `tag=` | P-03 → `B08DKYBTPH` | **MATCHES** |

All three `btn_ref` values are new relative to every value recorded in E-08/E-09/E-12/E-13 (rotation
re-confirmed, F-21). None of the three resolved URLs carries a `tag=` parameter (F-24 stands).

## 2. The controls — re-run, with status codes stated as observed

| Control | URL | Observed 2026-11-16 (this session) | What it reproduces |
|---|---|---|---|
| Unknown-code control (F-20's own) | https://link.amazon/B00TEST12 | Redirects to `https://amzlinks.in/B00TEST12`, serves title "404: File Not Found", body "Uh oh, it looks like something went wrong. You've clicked on an invalid URL.", image `amzlinks.in/post-tap/short-link-404.png` | **F-20 reproduces byte-for-byte** (same response as 2026-11-14) |
| Valid-ASIN control (F-28's own) | https://link.amazon/B0CDY277D3 | Redirects to `https://amzlinks.in/B0CDY277D3`, same 404 page | **F-28 reproduces** |
| Unissued code, `B0…` shape | https://link.amazon/NOTACODE9 | Bare `403 Forbidden` at `link.amazon`, no redirect | The **CR-A observation reproduces** (first seen by `5d6d2254` on 2026-11-15; also recorded by `224cc10c` on 2026-11-16) |
| Unissued code, `Z…` shape | https://link.amazon/ZZZZZZZZZ | Bare `403 Forbidden` at `link.amazon`, no redirect | Matches T49's recorded observation; second shape answering 403 |
| Unissued codes, `A00…` / `C00…` shapes | https://link.amazon/A00TEST12 · https://link.amazon/C00TEST12 | **HTTP 500 through this session's fetcher, both codes, on retry** — no page body returned | **Recorded as observed, not explained.** Session `224cc10c` recorded an amazon.com homepage redirect for these two codes earlier the same day; this session's fetcher saw neither that nor a 403. The discrepancy is logged, not reconciled by inference |

**Verdict on CR-A / T49's wording item:** the *conclusion* F-20 supports is intact — no observed unknown-code
shape ever fell through to an arbitrary product, and the B00TEST12 control reproduces on demand. What was
wrong was the *generalization*: the old title said "an unknown link.amazon code returns a 404", and a reader
reproducing the control with any unissued code today can get a bare 403 instead. Fixed by re-anchoring F-20's
title and detail to the specific control code and stating every observed status code with its date and
observer (see §5).

## 3. Manufacturer pages (CR-B, CR-C evidence)

| Page | Checked | Observed 2026-11-16 | Verdict |
|---|---|---|---|
| https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | Accessories count (CR-B) | Product description reads: "Included are **7 premium accessories** to maximize versatility—air fry basket, rotisserie spit, bake pan, and more." Spec tile still reads "25 Cooking Pre-sets" while the description reads "24 one-touch cooking presets" (existing conflict row reproduces); model line still `4-00675-02A-VN`; dimensions `16.9"D x 15.8"W x 14.8"H`; `120 volts`; `24.6 Liters` | **"7" CONFIRMED live** — session `5d6d2254` could not reach this text on 2026-11-15 (D-1/V-26); this session's fetch returned it, so the conflict can now be stated with both official figures |
| https://chefman.com/products/turbofry-touch-air-fryer-1 | Two-variant page (CR-C) | One URL sells both sizes: Size selector "8 Quart / 5 Quart"; spec bullets "• Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L", "• Dimensions: (5 Qt Model) …", "• Dimensions: (8 Qt Model) …", "• Model Number: RJ38-SQSS-5T (5 Qt model)", "• Model Number: RJ38-SQSS-8T (8 Qt model)"; page title "CHEFMAN® 8 Qt. TurboFry® Touch Air Fryer" | **CONFIRMED** — the 8 Qt line is what every published P3 figure quotes |

## 4. Amazon listing titles — perishability check (CR-B)

| Listing | Title stored in the ledgers (read 2026-11-14) | Title served 2026-11-16 | Verdict |
|---|---|---|---|
| P-01 `B0CDY277D3` | "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, … - Black" | same core text (page `<title>` adds the `Amazon.com:` prefix and ` : Home & Kitchen` suffix) | **Reproduces verbatim** |
| P-02 `B09B7SB46R` | "… \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals." | "… \| Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, **Six Cooking Accessories Included**" | **DIFFERS** — Amazon serves more than one title for this listing over time. Confirms D-1: a quoted listing title is perishable evidence and must carry its read date |
| P-03 `B08DKYBTPH` | "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option … \| Stainless Steel" | same core text | **Reproduces verbatim** |

## 5. Change-request dispositions

| CR | Filed by | Ask | Disposition, 2026-11-16 | Evidence |
|---|---|---|---|---|
| **CR-A** | `5d6d2254` (T42) | Add a flag: "the control behind F-20 answers 403 through the workspace fetcher, where the register quotes a 404 — state the status code as observed, not as the mechanism" | **CLOSED — by wording, not by a new flag.** Two reasons: (1) session `bbcc741f` had already published **F-40** on 2026-11-15, which is the flag CR-A asked for (it records the 403 for `ZZ9QQ7X4LK` and narrows F-20's evidence), so adding "F-4x" would duplicate it; (2) T49's later instruction for this exact defect was to *anchor F-20/F-03's wording to the specific control code*. Done: F-20's title now names `B00TEST12`, its detail states every observed status code with date and observer (including this session's 403s and HTTP-500 anomaly), and its action-required names both controls with expected answers. No flag count changed (still 40), so no typed count anywhere drifted | `ledger/flags.json` F-20 (this commit); F-40; §2 above |
| **CR-B** | `5d6d2254` (T42) | Relabel P2's `Included accessories` row `conflict` with both figures; note that Amazon serves more than one title, so a quoted title is perishable carrying a read date | **CLOSED.** `marketing/data/facts.json`: row is now `conflict`, value "7 (manufacturer) vs 6 (Amazon listing title)", `src` M3 + `src_alt` M4, detail carries both verbatim statements with their 2026-11-16 read dates plus the 2026-11-14 Item-details reading; new `title_note` on P2 records both title observations with read dates. `ledger/products.json`: P-02's spec row is now `conflict` with the same both-figures value and a source label that carries the read dates; the file note's over-general control sentence was anchored to `B00TEST12` (with F-40 cross-referenced) and stamped last-re-verified 2026-11-16. `marketing/data/editorial.json`: the guide sentence that said the count "ships as partial" now says it ships as a conflict, cites both official pages, and both guide blocks that leaned on "seven" attribute the count to the manufacturer and name the listing title's six | §1, §3, §4 above; regenerated `marketing/*.html`, `pages/products.html`, `assets/js/data.js` |
| **CR-C** | `5d6d2254` (T42) | Add one sentence to the P3 article: the manufacturer sells 5 Qt and 8 Qt on one page; every figure quoted is the 8 Qt line | **CLOSED — already satisfied in the current tree; no duplicate edit made.** The sentence exists in `marketing/data/editorial.json` `products/P3/gap` and renders on `marketing/articles/p3.html` ("One manufacturer URL sells both the 5 Qt and the 8 Qt model. Every row in this table is the 8 Qt variant, checked against the size selector on the page."), with a second statement in the Capacity row's note ("…every value on this row set is the manufacturer's stated value for the 8 Qt model, RJ38-SQSS-8T") and a third in the comparison table. It was added by commit `876df57` (publication layer, 2026-11-15 12:12 UTC) — i.e. the current tree already carries what CR-C asked for; the CR was filed against a pre-merge read. Re-verified against the live manufacturer page today (§3) | `marketing/articles/p3.html` lines with the gap sentence; commit `876df57`; §3 above |
| **CR-D** | `5d6d2254` (T42) | Disposition the `docs/*.md` sitemap question: excluded by the generator's rule; intentional or not? | **CLOSED — intentional, no generator change.** `tools/build_sitemap.py` documents "WHAT COUNTS AS PUBLISHED: Every `*.html` file in the repository, minus the exclusions" — a sitemap lists HTML destinations, and `docs/*.md` are Markdown working records, not HTML pages. They remain reachable at their URLs (the Pages artifact is the repository root) but are deliberately not advertised to crawlers. Changing the generator to emit Markdown URLs would break the sitemap's own contract (`--check` derives from `*.html`) for no SEO benefit | `tools/build_sitemap.py` module docstring, lines "WHAT COUNTS AS PUBLISHED"; `sitemap.xml` (139 URLs, regenerated, unchanged) |

**T49's F-20 wording item** (recorded 2026-11-16 by session `224cc10c` for "whoever owns `ledger/flags.json`")
is the same defect as CR-A and is closed by the same edit: F-20's title and detail now anchor to the specific
control code instead of "an unknown code".

## 6. Program sources — spot re-read (load-bearing pages only)

T49 re-audited all 17 discovery-register sources earlier the same day; this session re-read the two
load-bearing Associates pages itself:

| Source | URL | Observed 2026-11-16 | Register expectation | Verdict |
|---|---|---|---|---|
| Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | Page states "**Updated:** April 14, 2026"; Commission Income Statement §1(a)/(b) qualifying-purchase mechanics served verbatim (24-hour session, 89-day cart, 180-day fulfilment) | `page_stated_update` 2026-04-14 (S44–S46, S51–S54) | **MATCHES** |
| Associates Program Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | Page states "**Updated:** October 15, 2025"; §1 (Special Links must use the tagged formats we provide) and §4 Warranties served | `page_stated_update` 2025-10-15 (S58) | **MATCHES** |

Google and FTC pages were re-read by T49 the same day (`eb617be`, all quotes verbatim, S60 drift already
corrected) and were not re-fetched here; their 2026-11-16 audit stands as the record for today.

## 7. Gates — final tree

`python3 tools/ci_replay.py` — **35/35 steps PASSED** on the tree this record describes (run after all
edits and builder regenerations). Highlights: `validate_data` 0 errors, `build_site --check` no drift,
`build_marketing --check` 23 outputs current, `verify_marketing` 0 failures, `audit_site` all checks,
`seo_audit` all checks, `build_readiness --check` + `test_readiness` 13/13, console gate 0 errors,
research-hub guard 0 errors, 39/39 subpages disclose, 11/11 audit negative tests fired.

## 8. Irregularities found, fixed, or left open (non-blocking)

| # | Item | State |
|---|---|---|
| I-1 | F-20's title generalized "an unknown link.amazon code returns a 404" while three unissued codes answer in at least three different ways (404 page / bare 403 / homepage redirect or HTTP 500) | **FIXED this session** — wording re-anchored; status codes stated as observed with dates |
| I-2 | P2 accessories published as `partial` ("7") while the live listing title says "Six" | **FIXED this session** — republished as `conflict` with both figures and read dates on every surface |
| I-3 | P2's stored listing title is not the title the listing serves today | **FIXED as a note** — `title_note` + conflict detail record both observations with read dates; the stored title keeps its 2026-11-14 `observed_utc`, which is the honest stamp for that observation. `resolved.title` in the ledger was deliberately **not** overwritten: it is dated evidence, and today's differing title is recorded alongside it rather than replacing it |
| I-4 | `link.amazon/A00TEST12` and `C00TEST12` returned HTTP 500 through this session's fetcher where T49 recorded a homepage redirect the same day | **OPEN, recorded as observed** — cause unknown, not inferred. Non-blocking: no published claim depends on those two codes |
| I-5 | F-20's old wording also appears verbatim in historical session records (`docs/verification-*.md`, older COORDINATION entries) | **LEFT as-is on purpose** — those are dated records of what was believed when; the live register (`ledger/flags.json`), the dashboard (`assets/js/data.js`) and `pages/flags.html` all carry the corrected wording after regeneration |
| I-6 | `EXECUTIVE_SUMMARY.md` line ~305 says the valid-ASIN control "returns the identical 404 page as an unknown code" | **REVIEWED, acceptable as written** — the sentence documents the F-28 control comparison against the specific `B00TEST12` control recorded in E-06/E-11; it is a historical record of that session's control, not a general claim about the service. Not edited (append-only convention; not in this session's scope) |
| I-7 | Owner blockers unchanged: F-01 (9-character codes), F-03 (identity unconfirmed), F-24 (no Associates `tag=`), F-05/F-07 (no Creators API credentials) | **OPEN — owner action required**, published on the Flagged for Review page as before |

## 9. Sources (all fetched live 2026-11-16 unless noted)

- https://link.amazon/B04G1MEwY · https://link.amazon/B02NbDxp3 · https://link.amazon/B00hJ57DV
- https://link.amazon/B00TEST12 · https://link.amazon/B0CDY277D3 · https://link.amazon/NOTACODE9 ·
  https://link.amazon/ZZZZZZZZZ · https://link.amazon/A00TEST12 · https://link.amazon/C00TEST12
- https://www.amazon.com/dp/B0CDY277D3 · https://www.amazon.com/dp/B09B7SB46R · https://www.amazon.com/dp/B08DKYBTPH
- https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360
- https://chefman.com/products/turbofry-touch-air-fryer-1
- https://affiliate-program.amazon.com/help/operating/policies
- https://affiliate-program.amazon.com/help/operating/agreement
- Prior-day audits referenced, not re-fetched: T49's live source audit (2026-11-16, `eb617be`) for the
  Google/FTC register; `docs/verification-5d6d2254.md` for the CR-A…CR-D evidence base.
