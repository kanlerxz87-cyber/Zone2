# Verification Log — Zone2 Amazon Affiliate Platform

Verification date: **2026-11-13**, re-verified line by line against the live official pages on
**2026-11-14** (session `0a3dff48`). Method: each link/value resolved and fetched from the official
source listed.

> **Correction, 2026-11-14.** The note above originally said price, rating, review count, availability
> and the category commission rate "could not be confirmed". That was inaccurate for all five:
>
> * **Price, rating, review count and availability ARE present** on the official Amazon pages. A manual
>   re-fetch on 2026-11-14 read them directly — `B09B7SB46R` shows 4.3 out of 5 from 18,320 ratings,
>   `B08DKYBTPH` shows 4.4 out of 5 from 16,863 ratings, and both show a list price and a stock line.
>   They are blank on this site because they are **Program Content**: Program Policies §6(a) forbids
>   altering Program Content, §6(t) forbids displaying customer reviews or star ratings at all unless
>   they are obtained through Creators API or PA API, and §6(y) bars price-tracking and price-alerting
>   functionality. Under the IP License that content is obtained through the API.
> * **The public category rate card IS readable without signing in.** Amazon's Standard Commission
>   Income Statement publishes Table 1, including "Physical Books, Kitchen, Automotive" at **4.50%**
>   and the "Home" row at **3.00%**. It is the *account* Commission Income Schedule
>   (`/help/operating/schedule`) that redirects to sign-in, so the rate applying to one individual ASIN
>   stays blank.
>
> The cells are still blank. What changed is the stated reason: a policy decision is no longer
> presented as a verification failure.

## 1. Product link resolution (official source: amazon.com)

| Provided link | Resolved destination | Verified title (from official Amazon page) | Brand | Category | Verdict |
|---|---|---|---|---|---|
| https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | CHEFMAN | Home & Kitchen | Resolved & verified |
| https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. | Emeril Lagasse | Home & Kitchen | Resolved & verified |
| https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | Chefman | Home & Kitchen | Resolved & verified |

Irregularity: in all three cases the short-link code differs from the destination ASIN, and a direct
fetch of `amazon.com/dp/<code>` returns Amazon's "Page Not Found" page (verified for B04G1MEwY).
The codes act as opaque short-link tokens, not ASINs. Flagged for review.

## 2. Amazon Associates program facts (official sources)

| Fact | Value as verified | Official source |
|---|---|---|
| Program | Amazon Associates — Amazon's affiliate marketing program | https://affiliate-program.amazon.com/ |
| Commission ceiling | "Earn up to 10% in associate commissions from qualifying purchases and programs" | https://affiliate-program.amazon.com/ |
| Payment timing | ~60 days after end of month earned | https://affiliate-program.amazon.com/help/operating/policies (Commission Income Statement §6) |
| Session definition | Click → 24h / order ends session; cart orders qualify up to 89 days after click-through | https://affiliate-program.amazon.com/help/operating/policies (§1(c)) |
| Qualifying revenue | Amount Amazon receives less shipping, fees, taxes, credits, rebates, bad debt | https://affiliate-program.amazon.com/help/operating/policies (§1) |
| Payment minimums (US) | Deposit $10; gift card $10–$2,000; check $100 + $15 fee | https://affiliate-program.amazon.com/help/operating/policies (§6) |
| Mandatory disclosure | "As an Amazon Associate I earn from qualifying purchases." | https://affiliate-program.amazon.com/help/operating/agreement (§5) |
| Operating Agreement version | Updated October 15, 2025 | https://affiliate-program.amazon.com/help/operating/agreement |
| Program Policies version | Updated April 14, 2026 | https://affiliate-program.amazon.com/help/operating/policies |
| Agent / AI terms | Agents must identify as "Agent/[agent name]" in the user agent; no CAPTCHA circumvention; no model training on Program Content without approval | https://affiliate-program.amazon.com/help/operating/policies (IP License §4, §1, §2(e)) |
| Special Links | Must carry the Associates ID/tag parameter; sub-tags available on request | https://affiliate-program.amazon.com/help/operating/policies (§2(b)) |
| Price/availability display | Only via served link or Creators API / PA API; comparisons must show lowest new (and used, if provided) price | https://affiliate-program.amazon.com/help/operating/policies (§2(b)) |
| Ratings/reviews display | Only via Creators API or PA API | https://affiliate-program.amazon.com/help/operating/policies (§6(t)) |
| Prohibited paid search | No bidding on "amazon"/"kindle" or Amazon marks | https://affiliate-program.amazon.com/help/operating/policies (§2(c), §6(f)) |
| No artificial clicks | No robot/software-generated clicks or sessions | https://affiliate-program.amazon.com/help/operating/policies (§6(s)) |
| No self-purchases | No purchases through own Special Links or by associates' circle | https://affiliate-program.amazon.com/help/operating/policies (§6(u)) |
| No price-tracking features | Site must not have price tracking/alerting unless agreed | https://affiliate-program.amazon.com/help/operating/policies (§6(y)) |

## 3. Deliberately left blank + flagged (two distinct reasons)

**3a. Blank because Amazon's program policies require it — the value IS visible on the official pages**

| Value | Reason | Flagged on |
|---|---|---|
| List price (all 3 products) | Visible on the official Amazon pages. Program Content: IP License (obtain via Creators API / PA API) + Policies §6(a); §6(y) also bars price tracking/alerting | flagged.html |
| Star rating & review count | Visible on the official Amazon pages. Policies §6(t) bars displaying customer reviews or star ratings unless obtained through Creators API / PA API | flagged.html |
| Availability | Visible on the official Amazon pages, but Program Content under the IP License and it changes hour to hour | flagged.html |

**3b. Blank because no official source states it — genuinely unverified**

| Value | Reason | Flagged on |
|---|---|---|
| Rate applied to one individual ASIN | The **public** Standard Commission Income Statement publishes the category bands (Kitchen 4.50%, Home 3.00%) without signing in, but the **account** Commission Income Schedule redirects to Amazon sign-in, so the rate Amazon pays on a specific ASIN is left blank rather than inferred from the band | flagged.html |

## 3b. Manufacturer-page verification (integrated during final integration, 2026-11-13)

| Product | Attribute | Verified value | Official source |
|---|---|---|---|
| B0CDY277D3 (CHEFMAN 6 Qt Dual Basket) | Model | RJ38-SQPF-3TDB-2W | https://chefman.com/products/turbofry-touch-dual-window-air-fryer |
| B0CDY277D3 | Capacity | 6 qt total (two independent 3-qt baskets) | same |
| B0CDY277D3 | Power | 1700 W / 120 V | same |
| B0CDY277D3 | Temperature range | 200–450 °F (95–235 °C, as stated by Chefman) | same |
| B0CDY277D3 | Dimensions / weight | 13.38 × 11.81 × 10.63 in · 13.3 lb / 6.03 kg | same |
| B0CDY277D3 | Control / certification / warranty | Digital touchscreen · cETL · 1 year | same |
| B0CDY277D3 | Manufacturer-site price | $108.00 USD (Chefman.com) — verified, deliberately not published on the site (no-price rule) | same |
| B09B7SB46R (Emeril Lagasse 26QT) | Model | 4-00675-02A-VN | https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360 |
| B09B7SB46R | Capacity | 26 qt / 24.6 L | same |
| B09B7SB46R | Dimensions / warranty | 16.9"D × 15.8"W × 14.8"H · 1 year | same |
| B09B7SB46R | Cooking functions | **Conflict:** Amazon title 24 vs manufacturer spec tile 25 — both published | Amazon title + Emeril Everyday spec tile |
| B09B7SB46R | Manufacturer-site price | $199.99 USD (Emeril Everyday) — verified, deliberately not published on the site (no-price rule) | Emeril Everyday |
| B08DKYBTPH (Chefman 8 Qt TurboFry) | Model / capacity | RJ38-SQSS-8T · 8 qt / 7.57 L | https://chefman.com/products/turbofry-touch-air-fryer-1 |
| B08DKYBTPH | Temperature range / presets | 200–400 °F · 4 presets (fries, chicken, fish, meat) | same |
| B08DKYBTPH | Power | **Conflict:** Chefman 1700 W/120 V vs Amazon bullet 1000 W/120 V — both published | Chefman + Amazon |
| B08DKYBTPH | Dimensions | **Conflict:** Chefman 15.4 × 12.6 × 13.5 in vs Amazon 12.75"D × 13.5"W × 10"H — both published | Chefman + Amazon |
| B08DKYBTPH | Manufacturer-site price | $108.00 USD (Chefman.com) — verified, deliberately not published on the site (no-price rule) | Chefman |

All three manufacturer pages were re-fetched and confirmed during final integration. Manufacturer prices
are labelled as manufacturer-site prices on the site and are not presented as Amazon prices.

## 3c. Third verification pass — 2026-11-14 (session `0a3dff48`)

Every published specification row was re-read against the official page it cites, and the Amazon
product-information and item-details blocks of all three destination ASINs were fetched directly.
Six corrections and two new conflicts came out of it.

| # | Row | What the live page actually says | Change |
|---|---|---|---|
| W-1 | `B0CDY277D3` capacity | Chefman: 6 Qt / 5.67 L. Amazon's title says "2 Independent 3Qt" and its Size field says 6 Quart, but its product-information Capacity field says **6 liters** — 6 qt is 5.67 L, so the one Amazon page disagrees with itself | **New conflict**, published on both values (F-20) |
| W-2 | `B0CDY277D3` UPC | Amazon's item details state UPC **810087845025** | Previously "only in secondary aggregator listings" — now a first-party source; research-hub's blank row is filled |
| W-3 | `B0CDY277D3` power / voltage / dimensions / weight / temperature / model number | Amazon's product-information block states 1700 watts, 120 volts, 13.38"D × 11.81"W × 10.63"H, 13.3 pounds, 93 °C min / 450 °F max, and item details give Model Number RJ38-SQPF-3TDB-2W — **all identical to Chefman** | Rows now cite both official pages |
| W-4 | `B0CDY277D3` rating | Amazon's item details state 4.2 out of 5 from 4,859 ratings for this ASIN itself | The 2026-11-13 capture had not rendered the block (research-hub flag I-6). Value still not published — §6(t) |
| W-5 | `B09B7SB46R` model number | Amazon's item details give **4-00675-02X-VN**; the manufacturer's store gives **4-00675-02A-VN** for the same product | **New conflict**, both published (F-19) |
| W-6 | `B09B7SB46R` power / temperature / capacity / dimensions | Amazon's product-information block states Output Wattage 1700 watts, Wattage 1700 watts, Voltage 120 volts, Min 75 °F / Max 500 °F, Capacity 24.6 liters, Item Dimensions 16.9"D × 15.8"W × 14.8"H | Rows now cite both official pages; dimensions and capacity are corroborated |
| W-7 | `B09B7SB46R` cooking functions | Amazon's title says 24; its Configuration field also says "24 Functions and 7 Accessories"; the manufacturer's spec tile says 25 pre-sets | Conflict row now cites both pages explicitly |
| W-8 | `B08DKYBTPH` power | Amazon's **product-information block** states Output Wattage **1700 watts** — the same as Chefman — while Amazon's marketing **bullet text** says 1000 W | The conflict is inside one Amazon page. Reworded so all three statements are visible |
| W-9 | `B08DKYBTPH` temperature / presets / weight / dimensions / warranty | Amazon's block gives 94 °C min / 400 °F max, its description says 4 Functions, Item Weight 12.8 pounds, Item Dimensions 12.75"D × 13.5"W × 10"H, and item details give a 1-Year Limited Warranty and Part Number RJ38-SQSS-8T | Rows now cite both official pages |
| W-10 | Program Policies §6(t), §6(a), §6(y) | Re-read verbatim from https://affiliate-program.amazon.com/help/operating/policies ("Updated: April 14, 2026") | research-hub rows PG-05 / PG-06 upgraded from `not_rechecked` to `verified` with the clause text; RV-09 closed |

**Nothing published was withdrawn.** Two conflicts were added (F-19 model number, F-20 capacity), the
two "blank because unverified" reasons that were wrong were corrected to "blank by policy", and every
row that draws on two official pages now links both.

## 4. Integration checks

- Static site; no build step; all internal navigation links verified to point to existing files.
- `assets/js/data.js` and `assets/js/app.js` syntax-checked; tables render from the single verified dataset.
- Site deployed via GitHub Pages (source: `main`, path `/`).
