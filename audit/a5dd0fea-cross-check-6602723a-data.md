# Cross-check of `arena/6602723a-zone2` data against official sources

- **Checked by:** session `a5dd0fea` (read-only; did not edit the files)
- **Checked:** 2026-11-13 (UTC), against the pages retrieved with the fetch tool.
- **Files checked:** `data/products.json` (captured 2026-11-13T22:40Z), `data/compliance.json`, `data/requirements.json`, `data/sources.json`, `data/raw-verification-log.md`, all at commit `55525d8`.
- **Status key**
  - **Confirmed:** the value appears on the cited page or on a page I retrieved.
  - **Not reproduced:** I could not retrieve the value.
  - **Not confirmed:** the value does not appear on the page the file cites.
  - **Misattributed:** the value belongs to a different ASIN.

---

## 1. Product rows

### P1: B0CDY277D3 (Chefman 6 qt, `link.amazon/B04G1MEwY`)

| Field | Their value | Status | Evidence / source |
|---|---|---|---|
| Resolved ASIN | B0CDY277D3 | Confirmed | Redirect target of the short link (`audit/a5dd0fea-independent-verification.md` §1) |
| Title | CHEFMAN 6 Quart Dual Basket Air Fryer Oven … Black | Confirmed | Amazon US title field, https://www.amazon.com/dp/B0CDY277D3 |
| Brand | Chefman | Confirmed | Amazon title; Chefman site https://chefman.com/products/turbofry-touch-dual-window-air-fryer |
| Model number | RJ38-SQPF-3TDB-2W | Confirmed | Chefman page spec list (`Model Number: RJ38-SQPF-3TDB-2W`) |
| Capacity | 6 qt total (two independent 3-qt baskets) | Confirmed | Chefman: "Capacity: 6 Qt / 5.67 L". The two-basket detail is in the Amazon title. |
| Power | 1700 W / 120 V | Confirmed | Chefman spec list |
| Temperature range | 200–450 °F | Confirmed | Chefman spec list |
| Dimensions | 13.38 × 11.81 × 10.63 in | Confirmed | Chefman spec list |
| Weight | 13.3 lb / 6.03 kg | Confirmed | Chefman spec list |
| Colour / finish | Matte black, dual viewing windows, interior light | Confirmed | Chefman features and spec list |
| Certification, warranty | cETL; 1-year Chefman assurance | Confirmed | Chefman spec list |
| Control type | Digital touchscreen | **Not confirmed** | The 6 qt Chefman page text retrieved does not state touchscreen controls. The 8 qt page does. |
| Inner material | Stainless steel, nonstick baskets | **Not confirmed** | Chefman 6 qt lists "Nonstick, dishwasher-safe baskets" only. The cited source is an Amazon product information block I could not retrieve. |
| Feature: "Automatic shut-off" | listed | **Not confirmed** | Not in the Chefman 6 qt feature list retrieved. Their `features_source` is that page. |
| `category_path` | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | **Not confirmed** | No US breadcrumb retrieved. The UK breadcrumb for the Emeril ASIN is "Home & Kitchen › Kitchen & Home Appliances › Small Kitchen Appliances › Fryers › Air Fryers", which differs. |
| `volatile_snapshot.price_usd` | 69.97 | **Misattributed** | Their own note says this price came from the "customers who viewed" carousel, which shows a sibling listing. It is not this ASIN's price. **Set to null.** |
| `volatile_snapshot.rating` | null | Correct | Left blank. |

### P2: B09B7SB46R (Emeril Lagasse 26 qt, `link.amazon/B02NbDxp3`)

| Field | Their value | Status | Evidence / source |
|---|---|---|---|
| Resolved ASIN | B09B7SB46R | Confirmed | Redirect target |
| Title | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | Confirmed | Amazon US title field |
| Model (manufacturer) | 4-00675-02A-VN | Confirmed | Emeril Everyday product page SKU, https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 |
| Model (Amazon US) | 4-00675-02X-VN | **Not reproduced** | The Amazon US body did not render. The manufacturer's image filenames include "4-00675-02X_AMZ_US". That is a hint, not a confirmation. |
| Capacity | 26 qt / 24.6 L | Confirmed | Emeril spec tile: "26-Quart Capacity" and "24.6 Liters" |
| Cooking presets | 24 (conflict with 25) | Confirmed, both | Emeril: "24 one-touch cooking presets" in the description; "25 Cooking Pre-sets" on the spec tile. Conflict correctly shown. |
| Dimensions | 16.9"D × 15.8"W × 14.8"H | Confirmed | Emeril spec tile. Their note "identical on Amazon" is not verified. |
| Power | 1700 W / 120 V | **Not confirmed** | Emeril shows "120 volts" only. Wattage is not on the page text retrieved. Cited source is Amazon, not retrieved. |
| Temperature | 75–500 °F (Amazon) | **Not reproduced** | Amazon not retrieved. Emeril shows "Temperature Control" with no number, which matches their I-13 note. |
| Colour / material | Silver, stainless steel | Partly confirmed | "stainless steel unit" is in the description. "Silver" appears only in an image alt text. |
| Door style | Dual French doors, single-hand opening | **Not confirmed** | Emeril says "French doors offer effortless access." "Dual" and "single-hand" are not in the text retrieved. |
| Special features | Automatic shut-off, programmable, temperature control, timer | Partly confirmed | Timer and temperature control: Emeril spec tile. Automatic shut-off and programmable: not confirmed. |
| Included accessories | 7, with a list including drip tray, rack, fetch tool | Partly confirmed | Emeril: "7 premium accessories" and names the air fry basket, rotisserie spit, and bake pan. Drip tray, rack, and fetch tool are not in the text retrieved. |
| Warranty | 1 year | Confirmed | Emeril "1-Years Warranty" |
| Item weight | blank | Correct | Left blank. Their file already marks it unverified (conflicting Amazon values). |
| Rating | blank | Correct | Emeril shows 2.6 (25) on its own store. Not published. |
| Rating, storefront .co.uk | "4.5 / 16,128" (their I-7) | **Not reproduced** | Retrieved https://www.amazon.co.uk/dp/B09B7SB46R on 2026-11-13: **4.4 out of 5 stars, (17,838)**. |

### P3: B08DKYBTPH (Chefman 8 qt, `link.amazon/B00hJ57DV`)

| Field | Their value | Status | Evidence / source |
|---|---|---|---|
| Resolved ASIN | B08DKYBTPH | Confirmed | Redirect target |
| Title | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 … | Confirmed | Amazon US title field (from the redirect fetch; the canonical page returned an interstitial) |
| Model number | RJ38-SQSS-8T | Confirmed | Chefman 8 qt page; the 8 Qt model is RJ38-SQSS-8T |
| Capacity | 8 qt / 7.57 L | Confirmed | Chefman spec list |
| Power | 1700 W / 120 V (conflict with Amazon's 1000 W) | Confirmed (manufacturer side) | Chefman spec list. Amazon's "1000 Watts" bullet not retrieved, so the conflict cannot be checked. |
| Temperature | 200–400 °F | Confirmed | Chefman description and spec list |
| Presets | 4 (fries, chicken, fish, meat) | Confirmed | Chefman description and spec list |
| Dimensions (manufacturer) | 15.4 × 12.6 × 13.5 in | Confirmed | Chefman 8 Qt Model spec |
| Dimensions (Amazon) | 12.75"D × 13.5"W × 10"H | **Not reproduced** | Amazon not retrieved |
| Weight | 12.8 lb / 5.8 kg | Confirmed | Chefman 8 Qt Model spec |
| Material | Plastic, stainless steel | **Not confirmed** | Chefman says "Stainless-steel finish". "Plastic" is not in the text retrieved. Cited source is Amazon. |
| Special features | Automatic shut-off, LED shake reminder, programmable | Partly confirmed | Auto-shutoff and LED shake reminder: Chefman. "Programmable": not confirmed. |
| Feature: "flat frying tray" | listed | **Not confirmed** | Chefman says "Top-rack dishwasher-safe basket" only |
| Certification, warranty | cETL; 1-year Chefman assurance | Confirmed | Chefman spec list |
| `volatile_snapshot` rating 4.4 / 16,861; price 79.91; list 119.99; "Amazon's Choice" | recorded | **Not reproduced** | Canonical Amazon page returned an interstitial. The Chefman page shows $119.99 as a list-style price, but no Amazon figure. These are point-in-time and should stay off the site. |

---

## 2. Compliance and requirements files

| Claim in their file | Status | Evidence |
|---|---|---|
| Operating Agreement and Program Policies are verified | Confirmed | Both pages retrieved (`audit/a5dd0fea-independent-verification.md` §3) |
| Commission rate schedule is unverified and no rate is published | Confirmed | Schedule URL redirects to sign-in. Consistent with my check. |
| Application review: "at least three qualified sales within the first 180 days" | Confirmed | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM |
| "10 posts" and "content recent (generally within the last 60 days)" | Confirmed | Same page. Relevant to a new site, since the review checks content recency. |
| Disclosure wording, including "#paidlink", "#ad", "CommissionsEarned" | Confirmed | https://www.amazon.com/b?node=53643932011 (Amazon Operating Agreement Dos and Don'ts) |
| Trademark statement: "Amazon and the Amazon logo are trademarks of Amazon.com, Inc. or its affiliates." | Confirmed, and present in `compliance.json` | Same page |
| Tracking ID in every affiliate link | Confirmed, and present in their file | Same page. **The resolved short-link URLs do not carry a Tracking ID** (see audit §1). |
| **No screenshots or video recordings of Amazon on the site** | **Missing from their file** | Same page: "Use screenshots or video recordings of Amazon on your site(s)" is listed under Don'ts. **Recommend adding.** |

---

## 3. Summary of what must change before publication

1. **P1 price 69.97 is misattributed** to B0CDY277D3. Set it to null. (Same rule that applies to the P3 snapshot values.)
2. **Remove or flag unconfirmed features and specs** listed above: P1 "Automatic shut-off" and "Digital touchscreen"; P1 "Inner material: stainless steel"; P2 wattage, dual doors, single-hand opening, drip tray, rack, fetch tool; P3 "Plastic", "programmable", "flat frying tray", and the Amazon dimensions.
3. **Correct the .co.uk rating** for B09B7SB46R, or remove it. Observed: 4.4 / 17,838 on 2026-11-13.
4. **Correct the category path** for P1, P2, and P3 to a US source, or leave it blank. The only breadcrumb I retrieved is from the UK site.
5. **Add the no-screenshots rule** to `compliance.json`.
6. Where Amazon's own page could not be read, keep the value blank and flagged, as S-6602723A's I-6 already proposes. Do not replace it with the manufacturer's figure for an Amazon-specific field.

**Items confirmed and suitable to publish now, with the source URL on each row:** the three ASINs; the three titles; brands; the model numbers for P1 and P3; the manufacturer capacities for all three; the manufacturer dimensions and weight for P1 and P3; the Emeril capacity and dimensions; the 24 vs 25 preset conflict; and the compliance quotes above.
