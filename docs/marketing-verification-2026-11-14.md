# Marketing set — line-by-line verification log, 2026-11-14

Session `a3faf404` (`arena/a3faf404-zone2`). Scope: `marketing/**`, `tools/build_marketing.py`,
`marketing/scripts/verify_marketing.py`, this file.

Every value published in the marketing set was read off the page named below, on this date, by fetching
that page. Nothing was taken from a search snippet, a review site, another session's ledger, or a model's
memory. Where a page contradicted itself or another official page, the row is published as `CONFLICT` with
both statements quoted and both sources linked, rather than resolved by choice.

## Sources fetched, and what each contributed

| ID | Official page | Fetched | Values taken from it | Quoted text relied on |
|---|---|---|---|---|
| M1 | https://chefman.com/products/turbofry-touch-dual-window-air-fryer | 2026-11-14 | Capacity, power, temperature range, dimensions, weight, model, certification, windows, finish, basket care, Hi-Fry max, Sync Finish | "Capacity: 6 Qt / 5.67 L" · "Power: 1700W/120V" · "200–450°F / 95º-235ºC temperature range" · "Dimensions: 13.38 in x 11.81 in x 10.63 in / 33.98 cm x 30 cm x 27 cm" · "Weight: 13.3 lbs / 6.03 kg" · "Model Number: RJ38-SQPF-3TDB-2W" · "cETL approved with a 1-year Chefman® assurance" · "Sync Function so both baskets finish cooking at the same time" · "Nonstick, dishwasher-safe baskets" · "Interior light" · "Dual viewing windows" · "Matte-black finish" · "Max temp: 450ºF/ 235ºC with Hi-Fry function" |
| M2 | https://www.amazon.com/dp/B0CDY277D3 | 2026-11-14 | Official listing title, breadcrumb category, control type | Title: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black" · breadcrumb "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers" · "Digital touchscreen" |
| M3 | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 | 2026-11-14 | Capacity, dimensions, voltage, door, air circulation, cooking modes, accessories, warranty, model | "26-Quart Capacity preparing food for 4–6 people" · "16.9\"D x 15.8\"W x 14.8\"H Product Dimensions" · "24.6 Liters Capacity" · "120 volts Product Voltage" · "25 Cooking Pre-sets" (spec tile) **and** "Equipped with 24 one-touch cooking presets" (same page's description) · "French doors offer effortless access" · "Engineered with 360° hot air circulation" · "Dual-Speed Fan" · modes list: Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, Roast, Warm · "Included are 7 premium accessories … air fry basket, rotisserie spit, bake pan, and more" · "1-Years Warranty" · model "4-00675-02A-VN" |
| M4 | https://www.amazon.com/dp/B09B7SB46R | 2026-11-14 | Power watts, temperature range, listing title, conflicting model number | "24 cooking functions" in title · product-information block: 1700 W, 75–500 °F, model 4-00675-02X-VN |
| M5 | https://chefman.com/products/turbofry-touch-air-fryer-1 | 2026-11-14 | Capacity (8 Qt), power, temperature range, dimensions, weight, model, presets, certification, finish, basket care, shake reminder, auto shut-off | "Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L" · "200–400°F / 95º-205ºC temperature range" · "Dimensions: (8 Qt Model) 15.4 in x 12.6 in x 13.5 in / 39.11 cm x 32 cm x 34.29 cm" · "Weight: (8 Qt Model) 12.8 lbs / 5.8 kg" · "Model Number: RJ38-SQSS-8T (8 Qt model)" · "1700W/120V" · "4 cooking presets" · "LED shake reminder" · "Auto-shutoff for safety" · "Top-rack dishwasher-safe basket" · "Stainless-steel finish" · "cETL approved with a 1-year Chefman® assurance" |
| M6 | https://www.amazon.com/dp/B08DKYBTPH | 2026-11-14 | Listing title (which claims 450 °F Hi-Fry), breadcrumb category | Title: "Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option …" |
| S-01 | https://affiliate-program.amazon.com/ | 2026-11-14 | Commission ceiling | "up to 10% in associate commissions from qualifying purchases and programs" |
| S-02 | https://affiliate-program.amazon.com/help/operating/agreement | 2026-11-14 | Mandatory disclosure sentence | "As an Amazon Associate I earn from qualifying purchases." |
| S-03 | https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC | 2026-11-14 | ASIN definition (10 characters) | "ASIN is the 10-digit code" |

## Row-by-row disposition

| Product | Rows published | Verified with a source | Conflicts published | Partial | Blank + flagged |
|---|---|---|---|---|---|
| P1 Chefman 6 Qt Dual-Window | 17 | 13 | 0 | 0 | 4 (inner material + UPC unverified; price + rating withheld) |
| P2 Emeril French Door 360 | 15 | 9 | 2 (preset count, model number) | 1 (accessories) | 3 (UPC unverified; price + rating withheld) |
| P3 Chefman 8 Qt | 16 | 12 | 1 (max temperature) | 0 | 3 (UPC unverified; price + rating withheld) |
| **Total** | **48** | **34** | **3** | **1** | **10** |

Counts are produced by `marketing/scripts/verify_marketing.py`, which recomputes them from the data file and
compares against the rendered HTML, so the table above and the site cannot drift apart.

## Irregularities found while building this set

| ID | Product | What is wrong | Evidence | Disposition |
|---|---|---|---|---|
| MK-05 | P2 Emeril | **The manufacturer's own page states two different preset counts.** The specification tile reads "25 Cooking Pre-sets"; the product description on the same page reads "24 one-touch cooking presets", and the Amazon title says "24 cooking functions". | M3 (both statements), M4 (title) | Published as `CONFLICT`, both statements quoted, both sources linked. Not averaged, not resolved. |
| MK-06 | P2 Emeril | **Model number disagrees between official pages.** Manufacturer store: `4-00675-02A-VN`. Amazon product-information block: `4-00675-02X-VN`. | M3, M4 | Published as `CONFLICT` with both. Manufacturer value printed in the article header because it is the brand's own store. |
| MK-11 | P3 Chefman 8 Qt | **The Amazon title advertises a 450 °F Hi-Fry option while Chefman's 8 Qt specification states 200–400 °F.** | M5, M6 | Published as `CONFLICT`; the manufacturer range is shown as the specification, and the Amazon title is quoted verbatim elsewhere rather than silently dropped. |
| MK-07 | P2 Emeril | The manufacturer says "7 premium accessories" but names only three of them in the page text. | M3 | Published as `PARTIAL`; the three named accessories are listed and the remaining four are **not** invented. |
| MK-01 | P1 Chefman 6 Qt | Amazon's product-information block did not render in this session's fetch, so the inner-material row could not be re-confirmed. | M1, M2 | Left blank, `UNVERIFIED`, with the reason printed on the page. |
| MK-02 / 08 / 12 | all three | No UPC is stated on any official page. | M1–M6 | Left blank, `UNVERIFIED`. No aggregator listing was used. |
| MK-03 / 09 / 13 | all three | Prices exist on the pages but **must not be published** — the Associates policy restricts price display, and this project's deploy gate fails on a printed product price. | policy | Row present, value withheld, reason printed. |
| MK-04 / 10 / 14 | all three | Star ratings are storefront-specific and change daily; publishing one as a static "fact" would be a hallucination with a short half-life. | — | Row present, value withheld, reason printed. |

## What this set deliberately does not claim

- **No hands-on testing.** No one in this project has used these appliances. Every performance sentence is
  attributed to the manufacturer and linked.
- **No star ratings, no sales rank, no "best seller" claims.** These are volatile and were not confirmable as
  stable official facts.
- **No prices.** Withheld by policy, not merely missing.
- **No claim that the three supplied `link.amazon` short codes *are* these ASINs.** The codes are 9
  characters, the destinations are 10-character ASINs, and no Amazon document binds a short code to a
  destination. The product pages here are accurate *about those ASINs* — which is exactly what they say.
  The mapping question remains flagged in the repo's main `pages/flags.html` and `revalidation/flagged.html`.
- **No Associates tag.** None has been supplied; inventing one is prohibited. Every product link is a
  labelled, non-earning preview link.

## Reproduce

```bash
python3 tools/build_marketing.py --check        # committed HTML matches a fresh build
python3 marketing/scripts/verify_marketing.py   # 10 gates, per-row sourcing, no prices, links
```

Both run in CI (`.github/workflows/pages.yml`, steps "Rebuild marketing pages…" and "Marketing gate…").
