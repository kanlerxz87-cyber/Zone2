# Raw verification log

Append-only record of every source consulted and what it actually said.
Capture session: 2026-11-13 (UTC). All timestamps UTC.

This file exists so that any figure on the site can be traced back to the exact page
that produced it. Anything not listed here is not published as a fact.

---

## 1. Affiliate short-link resolution

The three supplied links are opaque. They were resolved by following the redirect and
noting the `Location` target that Amazon's own shortener returns.

| # | Supplied short link | Resolved canonical URL | ASIN |
|---|---|---|---|
| 1 | `https://link.amazon/B04G1MEwY` | `https://www.amazon.com/dp/B0CDY277D3` | B0CDY277D3 |
| 2 | `https://link.amazon/B02NbDxp3` | `https://www.amazon.com/dp/B09B7SB46R` | B09B7SB46R |
| 3 | `https://link.amazon/B00hJ57DV` | `https://www.amazon.com/dp/B08DKYBTPH` | B08DKYBTPH |

**Observation, flagged:** none of the three resolved URLs carried an Amazon Associates
`tag=` parameter. A link without `tag` cannot attribute commission. See irregularity I-4.

---

## 2. Amazon Associates policy sources

| Document | URL | Version observed | Used for |
|---|---|---|---|
| Associates Program Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | Updated 15 October 2025 | Disclosure wording, termination, warranties |
| Associates Program Policies | https://affiliate-program.amazon.com/help/operating/policies | Updated 14 April 2026 | Commission statement, participation rules, IP licence, trademark rules, agent rules |
| Associates Central home | https://affiliate-program.amazon.com/ | — | "Earn up to 10%" headline, payment ~60 days |
| Commission rate card | https://affiliate-program.amazon.com/help/operating/schedule | **login required** | Not readable without an Associates account — flagged |
| Application review help | https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM | — | 3 qualifying sales in 180 days, ≥10 posts rule of thumb |
| Creator University "Top Dos and Don'ts" | https://www.amazon.com/b?node=53643932011 | — | Approved disclosure language, tracking IDs, trademark rules |

### Verbatim quotes relied on

1. **Disclosure (Agreement §5).** "You must clearly and prominently state the following,
   or any substantially similar statement previously allowed under this Agreement, on
   your Site or any other location where Amazon may authorize your display or other use of
   Program Content: 'As an Amazon Associate I earn from qualifying purchases.'"

2. **Session length (Commission Income Statement §1(b)).** A session ends at the first of
   "(x) 24 hours elapse from that click, (y) the customer places an order for a Product,
   other than a digital product ..., or (z) the customer clicks through a Special Link to
   an Amazon Site that is not your Special Link".

3. **Cart window (§1(c)(i)).** A product bought from a cart "no later than 89 days after
   their initial click-through of the Special Link" still qualifies.

4. **Payment timing (§6).** Commission is paid "approximately 60 days following the end of
   each calendar month in which they were earned".

5. **Payment minimums (§6 chart, US).** Deposit minimum 10 USD; gift card minimum 10 USD,
   maximum 2,000 USD; cheque minimum 100 USD with a 15 USD processing fee.

6. **Price display rule (Participation Requirements §2(b)).** "your Site may only show
   prices and availability if: (a) we serve the link in which that price and availability
   data are displayed, or (b) you obtain Product pricing and availability data via Creators
   API or PA API". → This is why no price is printed as a static fact on the site.

7. **Price-comparison rule (same section).** Where prices are shown in a comparison
   format, the associate "must display both the lowest 'new' price and, if we provide it
   to you, the lowest 'used' price".

8. **Timestamps on prices (IP Licence §2(i)).** A date/time stamp is required next to
   pricing or availability data, e.g. "Amazon.com Price: $32.77 (as of 01/07/2008 14:11
   PST-Details)", plus the standard "prices ... are accurate as of the date/time indicated"
   disclaimer.

9. **Program Content cannot be altered (IP Licence / Participation Requirements §6(a)).**
   You may not "add to, delete from, or otherwise alter any Program Content in any way",
   except resizing images proportionally or truncating text without changing meaning.

10. **No caching of Product Advertising Content (§2(h)).** Images may not be stored; other
    content may be cached for at most 24 hours. ASINs may be stored indefinitely.

11. **Automated access — the "Agent Terms" (IP Licence, section "4. Agents").** An Agent is
    "any software or service that takes autonomous or semi-autonomous action on behalf of,
    or at the instruction of, any person or entity". Agents must identify themselves in the
    user agent as `Agent/[agent name]`, must not conceal that access is automated, must not
    complete or circumvent CAPTCHAs, and must not circumvent blocking measures.

    **This is the single most important constraint on the "automate everything" brief in
    this project.** See `docs/compliance.md` §"Automation limits".

12. **Prohibited paid search (§2(c) of the Commission Income Statement).** Purchases are
    disqualified where a customer arrives via an advertisement bid on "amazon", "kindle",
    or any Amazon Mark, including misspellings such as "ammazon", "amaozn", "kindel".

13. **Search-engine links (§2(d)).** Purchases are disqualified where the customer arrives
    by "a link that is generated or displayed on a search engine". Organic search traffic
    to your own site is fine; put your affiliate link in a search engine and it is not.

14. **Redirecting links (§2(e)).** A link that sends users "indirectly to an Amazon Site
    via an intermediate site, without requiring the customer to click ... on that
    intermediate site" disqualifies the purchase.

15. **Special Links must be direct (Participation Requirements §2(b)).** "All Special
    Links must be accessed directly from your Site" and must carry the Associates ID as a
    URL parameter.

16. **No self-purchases / no incentivised reviews.** Personal orders do not count toward
    the three qualifying sales, and Amazon's Community Guidelines prohibit reviews
    "created, edited, or removed in exchange for compensation".

17. **Application bar.** "at least three [qualified sales] within the first 180 days";
    sites need "robust original content (even when advertising is removed) — a good rule of
    thumb is at least 10 posts", must be public, and must be owned by the applicant.
    Website content must be "recent (generally within the last 60 days)".

18. **Trademark attribution.** Amazon's own guidance: include the statement "Amazon and the
    Amazon logo are trademarks of Amazon.com, Inc. or its affiliates."

19. **Unsuitable sites (§1(a)–(h) of Participation Requirements).** No sexually explicit
    material, violence, false/deceptive/libellous material, hateful or harassing material,
    illegal activity, content directed at children under 13, Amazon marks in the domain
    name, or IP infringement.

20. **Mobile Application Policy.** An app must be in Google Play / Apple / Amazon app
    stores, free to download, original, must not emulate Amazon's shopping app, and must
    not render Amazon pages in WebViews.

21. **One-programme rule (Commission Income Statement §5).** Tags may only be used to earn
    Associates commission; attempting to claim commission from both Associates and another
    programme "using the same traffic (for example, by manipulating or combining
    attribution links)" risks withheld commission and termination.

22. **Inactive accounts (§6).** After 3 years without substantial activity Amazon may
    withhold accrued commission, up to the gift-card minimum.

---

## 3. Product sources

### 3.1 ASIN B08DKYBTPH — Chefman TurboFry Touch 8 Qt

| Attribute | Value | Source |
|---|---|---|
| Title | Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel | Amazon US product page |
| Brand | Chefman | Amazon US; chefman.com |
| Model number | RJ38-SQSS-8T | Amazon US; chefman.com; Chefman user guide |
| Capacity | 8 quarts (7.57 L) | Amazon US; chefman.com |
| Power | 1700 W / 120 V | **Chefman official** (chefman.com), Amazon US bullet says 1000 W — conflict, see I-8 |
| Temperature range | 200–400 °F | chefman.com; Amazon US |
| Presets | 4 (fries, chicken, meat, fish) | chefman.com; Amazon US |
| Dimensions | 12.75"D x 13.5"W x 10"H (Amazon); 15.4 x 12.6 x 13.5 in (chefman.com) — conflict, see I-9 |
| Weight | 12.8 lb / 5.8 kg | chefman.com |
| Material | Plastic, stainless steel | Amazon US |
| Special features | Automatic shut-off, LED shake reminder, programmable | Amazon US |
| Certification | cETL approved | chefman.com; Amazon US |
| Warranty | 1 year (Chefman assurance) | chefman.com; Amazon US |
| Category path | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | Amazon US breadcrumb |
| Amazon badge | Amazon's Choice; "3K+ bought in past month" | Amazon US (point-in-time) |
| Rating at capture | 4.4 / 5 from 16,861 ratings | Amazon US (point-in-time, volatile) |
| Price at capture | $79.91 (list $119.99, −33%) | Amazon US (point-in-time, not published as fact) |

Source URLs:
- https://www.amazon.com/dp/B08DKYBTPH
- https://chefman.com/products/turbofry-touch-air-fryer-1
- https://chefman.com/pages/document-library-air-fryers

### 3.2 ASIN B0CDY277D3 — CHEFMAN 6 Quart Dual Basket Air Fryer

| Attribute | Value | Source |
|---|---|---|
| Title | CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black | Amazon US product page |
| Brand | Chefman | Amazon; chefman.com |
| Model number | RJ38-SQPF-3TDB-2W | Amazon (product information block); chefman.com |
| Capacity | 6 quarts total, two independent 3-quart baskets | Amazon; chefman.com |
| Power | 1700 W / 120 V | Amazon (product information); chefman.com |
| Temperature range | 200–450 °F (Hi-Fry to 450 °F) | chefman.com; Amazon |
| Presets / modes | Touchscreen presets; Sync Finish; +2 min; shake reminder; Hi-Fry | Amazon; chefman.com |
| Dimensions | 13.38 x 11.81 x 10.63 in / 33.98 x 30 x 27 cm | chefman.com (matches Amazon metric listing 34 x 30 x 27 cm) |
| Weight | 13.3 lb / 6.03 kg | chefman.com |
| Colour | Black, matte finish, dual viewing windows, interior light | chefman.com; Amazon |
| Material | Metal / plastic, stainless-steel inner, nonstick baskets | Amazon |
| Certification | cETL approved | Amazon; chefman.com |
| Warranty | 1 year (Chefman assurance) | Amazon; chefman.com |
| Category path | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | Amazon breadcrumb |
| Rating at capture | 4.4 / 5 from 1,392 ratings (seen in "also viewed" card for sibling ASIN B0B7C327LK; the parent ASIN's own block did not render) | Amazon US (partial — see I-6) |

Source URLs:
- https://www.amazon.com/dp/B0CDY277D3
- https://chefman.com/products/turbofry-touch-dual-window-air-fryer

**Note.** The Amazon page for this ASIN did not render its own rating block during
capture. The 4.4/1,392 figure belongs to the sibling listing B0B7C327LK shown in the
"customers who viewed this item also viewed" carousel and is therefore **not** published
for B0CDY277D3. Rating left blank on the site.

### 3.3 ASIN B09B7SB46R — Emeril Lagasse 26QT French Door Air Fryer Toaster Oven

| Attribute | Value | Source |
|---|---|---|
| Title | Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. | Amazon US product page |
| Brand | Emeril Lagasse | Amazon; emerileveryday.com |
| Model number | 4-00675-02X-VN (Amazon US); 4-00675-02A-VN (emerileveryday.com listing); 4-00675-02 (Amazon SE) | conflict, see I-10 |
| Capacity | 26 quarts / 24.6 L | Amazon; emerileveryday.com |
| Power | 1700 W / 120 V | Amazon (product information); see I-11 for the 1000 W conflict |
| Temperature range | 75–500 °F (Amazon product information) | Amazon |
| Cooking presets | 24 (Amazon title, manufacturer description); manufacturer spec block says "25 Cooking Pre-sets" | conflict, see I-12 |
| Dimensions | 16.9"D x 15.8"W x 14.8"H | Amazon; emerileveryday.com (identical) |
| Colour / material | Silver / stainless steel | Amazon; emerileveryday.com |
| Included accessories | Rack, bake pan, drip tray, crisper basket, rotisserie spit, fetch tool (7 accessories per manufacturer copy) | Amazon; emerileveryday.com |
| Special features | Automatic shut-off, programmable, temperature control, timer; interior light; French doors | Amazon; emerileveryday.com |
| Warranty | 1 year | emerileveryday.com |
| Manufacturer | Emeril Lagasse | Amazon |
| Country of origin | China | Amazon product information |
| Category path | Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers | Amazon breadcrumb |
| Best Sellers Rank at capture | #28,731 in Home; #49 in Air Fryers | Amazon (point-in-time) |
| Rating at capture | 4.5 / 5 from 16,128 ratings (Amazon.co.uk) vs 4.6 / 5 from 8,361 (Amazon.sa) | **storefront-specific** — see I-7 |

Source URLs:
- https://www.amazon.com/dp/B09B7SB46R
- https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360

---

## 4. Conflicts found and how they are handled

| ID | Conflict | Sources | Handling |
|---|---|---|---|
| I-8 | Chefman 8 Qt wattage: 1000 W vs 1700 W | Amazon US bullet text says "1000 Watts/120 Volts – RJ38-SQSS-8T"; chefman.com says "Power: 1700W/120V" for RJ38-SQSS-8T; independent manual index also says 1700 W | Publish **1700 W** citing the manufacturer, and record the Amazon discrepancy on the Flagged for Review page. Not silently resolved. |
| I-9 | Chefman 8 Qt dimensions | Amazon table: 12.75"D x 13.5"W x 10"H. chefman.com: 15.4 x 12.6 x 13.5 in (8 Qt variant), while the UK variant page says H 25.4 x W 32.4 x D 34.3 cm | Both published as separate rows with their own source; neither is presented as "the" dimension. |
| I-10 | Emeril model number suffix | -02X-VN (Amazon US), -02A-VN (manufacturer store), -02 (Amazon SE) | Publish the Amazon US string as the ASIN's model number, list the manufacturer string separately, flag the mismatch. |
| I-11 | Emeril wattage | Amazon product information: 1700 W. Some regional listings describe a 1700 W unit but a review notes 1,300–1,500 W draw in bake mode | Publish 1700 W (rated) from Amazon's product information; note that measured draw differs from rated power, which is normal. |
| I-12 | Emeril preset count: 24 vs 25 | Amazon title and manufacturer description say 24; manufacturer's own spec tile says "25 Cooking Pre-sets"; the Amazon.co.uk listing text also says "25 cooking presets" | Both published side by side with sources; flagged. |
| I-13 | Emeril maximum temperature | Amazon product information: 500 °F. Manufacturer spec block does not state a maximum; it states temperature control only | Publish 500 °F citing Amazon product information and mark it single-source. |

---

## 5. Sources consulted and rejected

Listed so the rejection is auditable.

| Source | Why not used |
|---|---|
| `homeproductcatalog.com` | Affiliate content farm; no editorial policy; not official |
| `kitchenwink.com`, `kitchendyno.com`, `ontheroadeatss.com`, `airfryerguidance.com` | Review blogs, not official; several contain contradictory specs |
| `manualsfile.com`, `manua.ls` | Third-party manual indexes; useful corroboration only, never cited as authority |
| `kohls.com`, `macys.com` | Retailer listings for near-identical but not identical SKUs |
| `modernspacegallery.com`, `shoppurilite.ca` | Reseller storefronts re-publishing Amazon copy |
| Any Amazon regional page as a *primary* source | Used only as corroboration where the US page body did not render; the regional ASIN page is the same catalogue record but the storefront's own numbers (reviews, stock) differ |
