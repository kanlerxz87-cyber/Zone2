# Verification record — session `7264f3c2` (T58) — 2026-11-17

Every claim this session's changes rest on, checked against the official page on the date shown.
Method: live fetch of the official URL (never a cached copy or another session's prose); repository
facts checked by running the command shown. Where something could not be confirmed, the row says so
and the published artifact keeps a blank or an explicit "pending" — nothing was inferred.

## A. Official Amazon pages re-read live on 2026-11-17

| # | Claim this session's work rests on | Official source (fetched live 2026-11-17) | What the page states | Outcome |
|---|---|---|---|---|
| V-1 | The Associates tag format and that the tag identifies the account a sale is tracked to | <https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC> | "ASIN is the 10-digit code that Amazon uses to denote specific products… Every item in our catalog has a unique ASIN." The qualifying text-link format is `http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID`, and "YOURASSOCIATEID is the unique ID that is used to identify your Associates account". The page's own examples are alphanumeric (B000IB9QXI), which is why this repository says 10-**character**. | Confirmed verbatim |
| V-2 | The Program Policies govern Special Links and are incorporated in the Operating Agreement | <https://affiliate-program.amazon.com/help/operating/policies> | Page header states "Associates Program Policies — Updated: April 14, 2026" and "These Associates Program policies … are incorporated by reference in the Associates Program Operating Agreement". Qualifying purchases arise when "a customer clicks through a Special Link on your Site to an Amazon Site", with a session that ends 24 hours after the click. | Confirmed verbatim; matches the date the ledger already records (S02) |
| V-3 | L1 destination | <https://link.amazon/B04G1MEwY> | Serves <https://www.amazon.com/dp/B0CDY277D3?lv=shuf&channelId=500&plpRedirect=mhFallback> — "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black". | Re-confirmed 2026-11-17; unchanged from the ledger's recorded observation |
| V-4 | L2 destination | <https://link.amazon/B02NbDxp3> | Serves <https://www.amazon.com/dp/B09B7SB46R?lv=shuf&channelId=500&plpRedirect=mhFallback> — "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included". | Re-confirmed 2026-11-17 |
| V-5 | L3 destination | <https://link.amazon/B00hJ57DV> | Serves <https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1> — "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel". | Re-confirmed 2026-11-17 |
| V-6 | L4 destination — **first resolution recorded in this repository** | <https://link.amazon/B0c8moW59> | Serves <https://www.amazon.com/dp/B0DHZTCNR5?lv=shuf&btn_type=ss&…&channelId=500&plpRedirect=mhFallback> — "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified … Black". The page's breadcrumb is Meat Thermometers. | New observation: a meat thermometer, outside the air-fryer set. Recorded in `docs/product-intent.json` / `intent.html`; nothing on the site promotes it |
| V-7 | L5 destination — **first resolution recorded in this repository** | <https://link.amazon/B0f3GKalj> | Serves <https://www.amazon.com/dp/B0DZFD6R9Z?lv=shuf&sbo=…&channelId=500&plpRedirect=mhFallback&th=1> — "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3". | New observation: outside the air-fryer set. Recorded in the intent register; disposition question DS-16 |
| V-8 | All five supplied codes are 9 characters, therefore not ASINs | V-1 + the five URLs as supplied in the owner's brief | Each code (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`, `B0c8moW59`, `B0f3GKalj`) is 9 characters; V-1 states an ASIN is 10. | Confirmed; `intent.intended_asin` stays null with the recorded reason on every row |

## B. Repository facts measured in this working tree (commands, not prose)

| # | Claim | How it was checked | Outcome |
|---|---|---|---|
| V-9 | Every reader-facing product Special Link carries the owner's tag | `python3 tools/build_front.py --check` and `python3 tools/build_marketing.py --check`; `python3 tools/verify_front.py` (G4 now fails a product CTA without `tag=shopnow047c-20` and any tag that is not the owner's) and `python3 marketing/scripts/verify_marketing.py` (G5 same, plus citation links must carry no tag) | Front gate OK (8 pages); marketing gate OK (20 pages, 48 spec rows, 0 failures) |
| V-10 | The measurement layer is live and policy-safe | `python3 tools/validate_discovery.py` — LIVE events require the recorded owner decision on DS-11 (present in `docs/discovery-t40.json`); EV-01/02/03 LIVE, EV-04/05 BLOCKED with stated blockers | OK — 6 pages, 17 findings, 12 questions, 17 suggestions, 19 cited sources, 0 failures |
| V-11 | The readiness board states the measured tagged-page count | `python3 tools/build_readiness.py --check` — RR-05 now carries the `{pages_with_tagged_link}` token, measured from the tree (8) | "release/index.html is current — 12 rows, every one sourced"; 13/13 readiness negative tests fire |
| V-12 | The whole workflow passes on the combined tree | `python3 tools/ci_replay.py` — replays all 43 workflow steps in order | CI REPLAY PASSED — 43 steps (after the rebuilds listed below) |
| V-13 | The design brief's counts are re-derived, not typed | `python3 tools/validate_brief.py` measures the tree (151 published pages, 8 tagged, 151 disclosing, 0 price pages) and `python3 tools/test_brief.py` fires 14/14 negative defects | Brief gate clean; summary.json re-measured 2026-11-17 |
| V-14 | The intent register is machine-readable and complete | `docs/product-intent.json` — five links, intent and observation as separate objects, `intended_asin` null with reason everywhere, `associates_workflow_validated` null (pending) everywhere | Published at `intent.html`; sitemap regenerated to include it (161 URLs) |

## C. What this session deliberately did NOT do

- **No price, star rating, or traffic/conversion/revenue figure was added anywhere.** No first-party
  report exists; the on-site counter records events into the visitor's own browser only (nothing is
  transmitted) until the owner deploys the endpoint (open items MI-01/MI-02, question DQ-12,
  suggestion DS-17).
- **No product photography.** The social-preview image is a brand card (`assets/img/og.jpg`),
  generated for this site; the product-imagery rights question stays open.
- **No claim that the supplied short links are invalid.** Their compliance status is unresolved;
  what changed is that the site's own published product links now carry the owner's tag, while the
  supplied links remain untagged evidence records.
- **No fabricated per-link "validated" marks.** `associates_workflow_validated` is null on all five
  rows — the enrolled Associates workflow is the owner's session to run; the paste-ready procedure
  is on `intent.html`.
- **No change to any verified specification value.** The spec tables' values and dates are exactly
  as the prior sessions recorded them (last re-read 2026-11-16, session `43eb0239`).

## D. Irregularities found and recorded (none blocking)

| ID | What | Where it is recorded |
|---|---|---|
| IR-1 | Two of the five supplied short links (`B0c8moW59`, `B0f3GKalj`) land on meat-thermometer listings, outside the product set the site describes — the first time this was observed in this repository | `docs/product-intent.json` L4/L5; `intent.html`; ledger F-06 dated note; discovery DS-16/DQ-11 |
| IR-2 | The brief supplied a tag but no evidence of the enrolled account or marketplace; the per-link Associates-workflow validation therefore stays pending | ledger F-07 dated note; `docs/product-intent.json` `special_link.associates_workflow_validated = null`; RR-05 owner_action |
| IR-3 | Two stale hard-coded rules had to be updated because reality changed: the release-readiness negative test R7 mutated RR-05 (now MET) into an empty `blocked_by` without setting BLOCKED, and the design-brief gate hard-coded "0 tagged pages" | `tools/test_readiness.py` (mutation sets state too), `tools/validate_brief.py` (`check_derived_counts` now derives the tag row like its siblings) |
| IR-4 | Eleven published pages that no current generator rebuilds (404, analysis, compliance, content, design-notes, flagged, paths, playbook, products, review-2026-11-15, tracking) still carried the pre-tag disclosure strip text baked in by an older generator build | Fixed in place this session (site chrome only; no historical record text altered). Logged as a forced scope extension in COORDINATION.md — a half-updated site asserting two different realities is the exact defect class the gates exist to prevent |
| IR-5 | `tools/validate_brief.py` hard-coded `GATE_COUNT = 43`; `main` gained the intake namespace's three CI steps during this branch's flight (workflow now runs 46), so the constant was stale the moment the rebase landed | Fixed by deriving the count from the workflow at runtime via `tools/ci_replay.py`'s step parser (never typable again); logged as a scope extension in COORDINATION.md |

## E. Sources carried, not re-fetched

The manufacturer pages (chefman.com, emerileveryday.com) were not re-fetched this session; no
specification value was touched, so nothing in this session's changes rests on them. The
application-review page (FB-06's quote), the Operating Agreement, the FTC pages and Google's
guidance pages are cited from the ledger and brief registers, which record their own read dates;
this session re-read the two Amazon help pages (V-1, V-2) that its own new claims rest on.


## F. Re-verification on the combined tree (2026-11-17, after the rebase onto `main`)

While this branch was in flight, four parallel sessions merged to `main` (`e58dac0` → `6fe5343`):
PR #151 (`0f5673ee`, CR-1 closure — RR-01/RR-05 derived counts, SG-11 dedupe), PRs #153/#155/#156
(`1539a895`, renumbered T59 — onboarded `B0c8moW59`/`B0f3GKalj` as P-04/P-05), PR #154 (`613900e6`,
renumbered T60 — the `intake/` register). This session's claim was renumbered **T58 → T61** per the
board's precedent (merged claim keeps the id). The rebase resolved every conflict by keeping both
sides; nothing from another session was discarded. Checks re-run on the combined tree:

| Check | Result on the combined tree |
|---|---|
| `tools/ci_replay.py` (all workflow steps, in order) | **PASSED — 46/46** (was 43 pre-merge; +3 intake steps from PR #154) |
| `tools/validate_brief.py` + `tools/test_brief.py` | clean; 14/14 negative tests fire |
| `tools/test_readiness.py` | 14/14 negative tests fired (multi-measure row model intact) |
| `tools/test_intake.py` (main's) | OK — baseline clean, 15 injected defects fired |
| `tools/verify_front.py` | OK — 8 pages, all checks pass |
| `marketing/scripts/verify_marketing.py` | OK — 20 pages · 48 spec rows · 0 failures |
| Re-measured summary counts | 159 published pages · 159 disclose · 8 tagged · 0 print a price (intake pages + intent.html added 8 over main's 151) |
| Release-readiness board | 12 rows — 5 MET (RR-01/04/05/08/10), 3 GAP, 2 BLOCKED, 1 UNVERIFIED, 1 OPEN; RR-05 carries both derived tokens |
| Sitemap | 169 URLs, includes `intent.html` and the eight `intake/` pages |
| Cross-register consistency | this register's five observed destinations (L1→B0CDY277D3, L2→B09B7SB46R, L3→B08DKYBTPH, L4→B0DHZTCNR5, L5→B0DZFD6R9Z) agree row-for-row with T59's `ledger/products.json` P-01–P-05 records and T60's `intake/` observations — three independent passes, same destinations; the datasets stay separate as the brief requires |
| Typed brief rows updated to the re-derived tree | workflow steps 46 of 46; requirements 5 met · 7 not met; disclosure prose 159 of 159; clicks note reworded (tag supplied, counter live, no first-party report yet) |
