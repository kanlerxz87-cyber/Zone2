# Verification Log — Zone2 Amazon Affiliate Platform

Verification date: **2026-11-13**. Method: each link/value resolved and fetched from the official source
listed. Automated fetches of Amazon product pages return the official page title (bot-protected bodies
exclude price/rating markup), so title, brand and category are verified from official Amazon pages;
price, rating, review count, availability and the category commission rate could not be confirmed and
were left blank + flagged.

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

## 3. Deliberately unverified (left blank + flagged)

| Value | Reason | Flagged on |
|---|---|---|
| List price (all 3 products) | Not exposed to automated fetch; policy restricts display | flagged.html |
| Star rating & review count | Not exposed; policy restricts display | flagged.html |
| Availability | Not exposed to automated fetch | flagged.html |
| Home & Kitchen category commission rate | Official rate schedule requires Associates sign-in | flagged.html |

## 4. Integration checks

- Static site; no build step; all internal navigation links verified to point to existing files.
- `assets/js/data.js` and `assets/js/app.js` syntax-checked; tables render from the single verified dataset.
- Site deployed via GitHub Pages (source: `main`, path `/`).
