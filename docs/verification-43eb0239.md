# Verification record — 2026-11-16 — session `43eb0239` (task **T54** — renumbered twice: T50 was claimed and merged first by `ebc8a709`, T51 by `970d11d6`, and T52/T53 by `7c1511ee`, all while this session was running; renumbered rather than contended, per the board’s precedent. See COORDINATION.md.)

**What this pass is.** A line-by-line re-read, from this session, of the **six official product sources**
that carry every number the published tables print. Session `224cc10c` (T49, merged 2026-11-16) had already
re-audited the *programme* sources — Associates policies, the Operating Agreement, the Google and FTC
pages — and this pass deliberately does not repeat that work. What no session had re-read since 2026-11-14
is the other half: the three Amazon listings the supplied links resolve to, and the three manufacturer
pages. That is the half covered here.

**Method.** Every page below was fetched live on 2026-11-16 and compared against the value this repository
publishes, value by value, in the order the ledger stores them. Nothing was inferred, averaged, filled in or
carried over from another session's notes. Where a published value and the served page disagree, the
disagreement is recorded and — only where the ledger is this session's claimed scope — corrected.

**Channel note.** The sandbox shell cannot make outbound TLS connections (`SSL_ERROR_SYSCALL`), so every
live read below used `fetch_page`, never `curl` and never an assumption. Where a page did not cooperate, the
record says so instead of guessing.

**Ledger rows this pass produced:** `V-90` … `V-104` in
[`ledger/verification.json`](../ledger/verification.json) · rendered on
[pages/verification.html](https://kanlerxz87-cyber.github.io/Zone2/pages/verification.html).

---

## 1. The three supplied links, re-resolved today

| # | Supplied link | Resolved to today | `btn_ref` token on this fetch | Verdict | Source |
|---|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | `https://www.amazon.com/dp/B0CDY277D3` | `srctok-68884e8aa630b24a` | **VERIFIED** — destination unchanged | [S33](https://link.amazon/B04G1MEwY) · [S19](https://www.amazon.com/dp/B0CDY277D3) |
| 2 | https://link.amazon/B02NbDxp3 | `https://www.amazon.com/dp/B09B7SB46R` | `srctok-662480f5bd825c83` | **VERIFIED** — destination unchanged | [S34](https://link.amazon/B02NbDxp3) · [S20](https://www.amazon.com/dp/B09B7SB46R) |
| 3 | https://link.amazon/B00hJ57DV | `https://www.amazon.com/dp/B08DKYBTPH` | `srctok-38bef00eb1e962ef` | **VERIFIED** — destination unchanged | [S35](https://link.amazon/B00hJ57DV) · [S21](https://www.amazon.com/dp/B08DKYBTPH) |

All three destinations are identical to the ones recorded on 2026-11-13/14 and re-confirmed by four
earlier sessions. All three `btn_ref` tokens are new again, which is flag **F-21** reproducing for the
sixth time: **the tracking token rotates between days, the destination does not.**

### Control, re-run today

| Probe | Served response | Verdict |
|---|---|---|
| https://link.amazon/B00TEST12 (the exact code F-20 names) | `amzlinks.in/B00TEST12` → *"404: File Not Found … You've clicked on an invalid URL."* | **Reproduces.** An unissued code does not fall through to a product page. |

This is the positive evidence that lets the site say the three supplied codes are **honoured lookups**
rather than ignored tokens. **F-40's caveat still stands and is not weakened or strengthened by this run:**
the control is anchored to *this specific code*. Other unissued shapes have answered differently on other
days (403 at the edge, homepage redirect), and the cause is unknown. No generalisation is claimed.

---

## 2. Identity rows — listing title, brand, category path

| Product | Published before this pass | Live page, 2026-11-16 | Verdict |
|---|---|---|---|
| P-01 `B0CDY277D3` | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | identical | **VERIFIED verbatim** |
| P-02 `B09B7SB46R` | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| **26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.** | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| **Countertop Convection Cooker, 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included** | **REFUTED** — see §4 |
| P-03 `B08DKYBTPH` | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | identical | **VERIFIED verbatim** |

Brand (`CHEFMAN`, `Emeril Lagasse`, `Chefman`) and the browse path
`Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers` reproduce for all three.

---

## 3. Specification values, compared line by line against the manufacturer pages

Every row below is a value this site publishes with a source link. "Live page says" is transcribed from the
page as served on 2026-11-16.

### 3.1 P-01 — Chefman TurboFry® Touch 6 Qt Dual-Window — [S25](https://chefman.com/products/turbofry-touch-dual-window-air-fryer)

| Attribute | Published value | Live page says | Verdict |
|---|---|---|---|
| Model number | RJ38-SQPF-3TDB-2W | `Model Number: RJ38-SQPF-3TDB-2W` | VERIFIED |
| Capacity | 6 Qt / 5.67 L (two independent 3-qt baskets) | `Capacity: 6 Qt / 5.67 L` | VERIFIED |
| Temperature range | 200–450 °F / 95–235 °C | `200–450°F / 95º-235ºC temperature range` | VERIFIED |
| Power | 1700 W / 120 V | `Power: 1700W/120V` | VERIFIED |
| Dimensions | 13.38 × 11.81 × 10.63 in (33.98 × 30 × 27 cm) | `Dimensions: 13.38 in x 11.81 in x 10.63 in / 33.98 cm x 30 cm x 27 cm` | VERIFIED |
| Weight | 13.3 lb / 6.03 kg | `Weight: 13.3 lbs / 6.03 kg` | VERIFIED |
| Certification and warranty | cETL approved with a 1-year Chefman assurance | `cETL approved with a 1-year Chefman® assurance` | VERIFIED |

**7 of 7 — zero drift.**

### 3.2 P-03 — Chefman 8 Qt TurboFry® Touch — [S26](https://chefman.com/products/turbofry-touch-air-fryer-1)

| Attribute | Published value | Live page says | Verdict |
|---|---|---|---|
| Model number | RJ38-SQSS-8T | `Model Number: RJ38-SQSS-8T (8 Qt model)` | VERIFIED |
| Capacity | 8 Qt / 7.57 L | `Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L` — 8 Qt model row | VERIFIED |
| Temperature range | 200–400 °F / 95–205 °C | `200–400°F / 95º-205ºC temperature range` | VERIFIED |
| Power | **CONFLICT** — Amazon bullet 1000 W vs Amazon info block and Chefman 1700 W | `Power: 1700W/120V` | VERIFIED — conflict side intact |
| Dimensions | **CONFLICT** — Chefman 15.4 × 12.6 × 13.5 in vs Amazon 12.75 × 13.5 × 10 in | `Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 cm x 32 cm x 34.29 cm` | VERIFIED — conflict side intact |
| Weight | 12.8 lb / 5.8 kg | `Weight: (8 Qt Model) 12.8 lbs / 5.8 kg` | VERIFIED |
| Presets | 4 — French fries, chicken, meat, fish | `4 cooking presets`; description "presets for fries, chicken, fish, and meat" | VERIFIED |
| Certification and warranty | cETL approved; 1-year warranty | `cETL approved with a 1-year Chefman® assurance` | VERIFIED |

**Zero drift.** Both published conflicts are still conflicts; neither side was dropped and no choice was
made between them.

### 3.3 P-02 — Emeril Lagasse French Door AirFryer 360, 26 QT — [S27](https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360)

| Attribute | Published value | Live page says | Verdict |
|---|---|---|---|
| Title | EMERIL LAGASSE FRENCH DOOR AIRFRYER 360™ TOASTER OVEN COMBO, 26 QT | identical | VERIFIED |
| Model number | **CONFLICT** — Amazon `4-00675-02X-VN` vs manufacturer `4-00675-02A-VN` | `4-00675-02A-VN` | VERIFIED — conflict stands (F-23) |
| Capacity | 26 qt / 24.6 L (sized for 4–6 people) | tile `26-Quart Capacity / preparing food for 4–6 people`; tile `24.6 Liters` | VERIFIED |
| Cooking functions / presets | **CONFLICT** — 24 (Amazon, manufacturer description) vs 25 (tile) vs 10 (feature block) | description `24 one-touch cooking presets`; tile `25 Cooking Pre-sets`; block `10-In-1 Versatility` listing Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, Roast, Warm | VERIFIED — conflict stands (F-19) |
| Dimensions | 16.9"D × 15.8"W × 14.8"H | tile `16.9"D x 15.8"W x 14.8"H` | VERIFIED |
| Special features | Dual-speed fan, rotisserie, 360° hot-air circulation, temperature control | tiles `Dual-Speed Fan`, `Temperature Control`; feature blocks `Rotisserie`, `360 Air Technology` | VERIFIED |
| Warranty | 1 year | `1-Years Warranty` | VERIFIED |
| Included accessories | 7 premium accessories (manufacturer); Amazon lists six | `Included are 7 premium accessories`; Amazon title states **Six** Cooking Accessories Included | VERIFIED — both figures present, row labelled accordingly |
| Voltage | 120 volts (tile) | `120 volts` | VERIFIED |

**Zero drift on every value sourced to this page.**

---

## 4. The one defect this pass found — and what was done about it

**D-1 (confirmed, corrected): P-02's published Amazon listing title had drifted from the live listing.**

The repository was publishing, as the title of `B09B7SB46R`, a string read on 2026-11-14:

> Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | *26QT air fryer oven with French
> doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.*

The page served on 2026-11-16 says:

> Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | *Countertop Convection Cooker,
> 24 One-Touch Preset Options, Extra Large Interior, Six Cooking Accessories Included*

This is not new: session `5d6d2254` found exactly this on 2026-11-15 (its defect D-1) and deliberately left
it, because `ledger/products.json` was another session's claimed scope at the time. Two independent
sessions, two days apart, have now read the same current string, and P-01 and P-03 titles reproduced
verbatim in the same run — so it is not a formatting artefact in how this site reads titles. **Amazon serves
different title text for this listing at different times.**

What was done, all inside this session's claimed scope:

1. `ledger/products.json` — the stored title is now what the page serves, stamped
   `title_last_read_utc: 2026-11-16` and `title_previously_read_utc: 2026-11-14`. P-01 and P-03 were
   re-stamped only; their titles matched.
2. `ledger/products.json` — the *Cooking functions / presets* conflict row quoted `"'24 cooking functions'"`
   from the stale title. It now quotes the live clause. The substance of the conflict — 24 against 25
   against 10 — is untouched.
3. `ledger/flags.json` — new flag **F-41** records the drift, the correction, and the structural lesson:
   **a listing title is perishable evidence**, and it is only defensible while it carries the date it was read.
4. `ledger/verification.json` — **V-95** is recorded `REFUTED`, not `VERIFIED`. (It was first written as
   `VERIFIED` and corrected in the same session, before any commit, once the comparison was finished. The
   note in the ledger says so.) **V-104** lists the copies that remain outside this scope.

**Deliberately not done — logged instead as change request CR-13 in `COORDINATION.md`:** the superseded
title is still present in `revalidation/data/links.json`, `revalidation/data/specs.json`,
`revalidation/products.html`, `marketing/data/facts.json`, `marketing/articles/p2.html` and
`research-hub/data/raw-verification-log.md`. Those are other namespaces' own datasets and a dated raw log.
Editing them across a claimed scope is precisely what the coordination rules forbid, so they are a logged
request rather than a silent edit. Historical verification docs (`docs/verification-*.md`,
`docs/verification-log.md`, `docs/revalidation-2026-11-14.md`) quote the old string **as evidence** of what
was true when they were written; rewriting them would falsify the record, so they stay exactly as they are.

---

## 5. What this pass could **not** verify — stated, not glossed

**V-103.** The rows this repository sources *only* to the Amazon product-information table — controls,
special features, material, colour and UPC for P-01; wattage, temperature settings, controls, model number
and UPC for P-02; wattage, dimensions, controls, special features, material, certification and UPC for
P-03 — **were not re-read today.** The listing body is request-dependent: two consecutive fetches of the
same URL (`…/dp/B09B7SB46R`) returned different page lengths and different section ordering, so the
product-information table could not be located with confidence, and a value read from the wrong section is
worse than a value not read at all.

Nothing was changed, filled in or inferred as a result. Every one of those rows keeps its published official
source link and its 2026-11-14 observation. What today's run *does* establish for all three products is
the identity layer (destination ASIN, listing title, brand, category path — §1 and §2) and every
manufacturer-sourced specification value (§3), which together are the majority of the published table.

---

## 6. Gates

All 35 workflow steps replayed locally (`tools/ci_replay.py`) plus `tools/validate_data.py`,
`tools/audit_site.py`, `tools/seo_audit.py`, the marketing, console, audit, discovery, readiness,
revalidation, affiliate-lab and research-hub verifiers, and `tests/test_pipeline.py` — all green on the
final tree, after the correction and after every generator was re-run. The `check_published_counts` gate
caught the two count strings that the new flag and the new verification rows invalidated
(`README.md`, `EXECUTIVE_SUMMARY.md`); both were updated to the ledger values and the gate is green.

---

## 7. Irregularities still open for owner review (unchanged by this pass)

| Id | Item | Source |
|---|---|---|
| F-01 (high) | The three supplied codes are 9 characters; an ASIN is 10. Identity rests on the observed link destinations until Associates Central confirms them. | [S16](https://www.amazon.com/dp/B04G1MEwY) · [S24](https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC) |
| F-24 (medium) | The supplied links carry no Associates `tag=` parameter — as supplied they cannot earn a commission. | [S33](https://link.amazon/B04G1MEwY) |
| F-40 (low) | The negative control behind F-20 does not behave identically for every token shape. Published reading unchanged. | [S43](https://link.amazon/ZZ9QQ7X4LK) |
| **F-41 (medium, new)** | P-02's title drift — corrected in the ledger, three downstream copies outstanding (CR-13). | [S20](https://www.amazon.com/dp/B09B7SB46R) |
| — | Measurement: 5 events defined, **0 live**. The site is static; disclosed on `discovery/measurement.html`. | [discovery/measurement.html](https://kanlerxz87-cyber.github.io/Zone2/discovery/measurement.html) |

**Owner actions, unchanged:** supply the Associates ID and target marketplace (F-24 / Q-01 / Q-02); confirm
the three destinations are the products intended (F-03 / Q-03); re-supply full ASINs if the brief's tokens
were meant as ASINs (F-01); decide CR-13.
