# Independent verification log: session `a5dd0fea`

- **Branch:** `arena/a5dd0fea-zone2` (from `main` @ `f5771676`)
- **Verified:** 2026-11-13 (UTC), by fetching each URL below and reading the page text returned.
- **Rule applied:** a value appears here only if it was present in a retrieved official page. Anything else is **unverified** and left blank.
- **Scope:** read-only cross-check. This session did not build or edit the site, the data tables, or any file owned by another session. See `COORDINATION.md`.

---

## 1. Affiliate short links to product pages

| # | Link as supplied | Final URL after redirect (retrieved) | ASIN | Title on the retrieved page (verbatim) | Source |
|---|---|---|---|---|---|
| 1 | https://link.amazon/B04G1MEwY | https://www.amazon.com/dp/B0CDY277D3 | B0CDY277D3 | "Amazon.com: CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black : Home & Kitchen" | https://www.amazon.com/dp/B0CDY277D3 |
| 2 | https://link.amazon/B02NbDxp3 | https://www.amazon.com/dp/B09B7SB46R | B09B7SB46R | "Amazon.com: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven \| 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals. : Home & Kitchen" | https://www.amazon.com/dp/B09B7SB46R |
| 3 | https://link.amazon/B00hJ57DV | https://www.amazon.com/dp/B08DKYBTPH | B08DKYBTPH | "Amazon.com: Chefman Air Fryer 8 Qt \| TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results \| Bake, Dehydrate, Frozen \| XL Nonstick Dishwasher-Safe Basket \| Stainless Steel : Home & Kitchen" | https://www.amazon.com/dp/B08DKYBTPH |

**Notes**

- Re-fetching the canonical `/dp/` URL returned the same title for #1 and #2. For those two, the body text was only footer and navigation, so no price, rating, availability, or specification text was retrieved.
- For #3, the canonical `/dp/` URL returned a "Continue shopping" interstitial, not product content. The title above comes from the short-link redirect fetch. **Re-check this one manually.**
- The short-link path segments (`B04G1MEwY`, `B02NbDxp3`, `B00hJ57DV`) are 9 characters. ASINs are 10. The ASINs above come from the redirect targets, not from the link text.
- The resolved URLs carry tracking parameters (`lv`, `btn_ref=srctok-…`, `channelId`, `plpRedirect`). None carries an Associates `tag=` parameter, so the owning Associate ID cannot be confirmed from these links. The user should confirm which Associate ID these links belong to.

**Category, from the title suffix ("Home & Kitchen"):** all three are listed under Home & Kitchen. The title also identifies each as an air fryer (or air fryer oven).

## 2. Storefront cross-check (S-6602723A irregularity I-7)

- **Page:** https://www.amazon.co.uk/dp/B09B7SB46R (retrieved 2026-11-13)
- **Title:** "Emeril Lagasse 26 QT Extra Large Air Fryer, Convection Toaster Oven with French Doors, Stainless Steel : Amazon.co.uk: Home & Kitchen"
- **Brand:** EMERIL LAGASSE
- **Rating:** 4.4 out of 5 stars, (17,838)
- **Breadcrumb:** Home & Kitchen › Kitchen & Home Appliances › Small Kitchen Appliances › Fryers › Air Fryers

**Discrepancy.** S-6602723A's board reports "4.5 / 16,128" for this ASIN on `.co.uk`. That value was not reproduced here. The UK title also differs from the US title above, so titles are storefront-specific as well. Ratings and review counts are volatile, so the integration owner should either timestamp them or exclude them, as S-6602723A's I-5 and I-7 already propose.

## 3. Amazon Associates requirements (verified against official page text)

| # | Requirement | What the official text says | Source (section, page) |
|---|---|---|---|
| R1 | Required Associate disclosure | "You must clearly and prominently state the following, or any substantially similar statement previously allowed under this Agreement, on your Site … : 'As an Amazon Associate I earn from qualifying purchases.'" | Operating Agreement §5, https://affiliate-program.amazon.com/help/operating/agreement (page "Updated: October 15, 2025") |
| R2 | Prices and availability may only be shown in limited cases | "your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API and you comply with the requirements regarding use of Creators API or PA API…" | Program Policies, Participation Requirements §2(b), https://affiliate-program.amazon.com/help/operating/policies (page "Updated: April 14, 2026") |
| R3 | No inaccurate or misleading product claims | "You must not make inaccurate, overbroad, deceptive or otherwise misleading claims about any Product…" | Participation Requirements §2(b), same page |
| R4 | Site owner is responsible for content accuracy and disclosures | §3(b) refers to disclosure rules "for example, if applicable, the U.S. FTC Guides Concerning the Use of Endorsement and Testimonials in Advertising". §3(c) makes you responsible for "the accuracy, completeness, and appropriateness of, materials posted on your Site (including all Product descriptions…)" | Participation Requirements §3(b)–(c), same page |
| R5 | Domain and identifiers must not use Amazon marks | Unsuitable sites include those that "include any trademark of Amazon or its affiliates … in any domain name, subdomain name, in any 'tag' or Associates ID…" | Participation Requirements §1(g), same page |
| R6 | Redirect-style links lose commission | Purchases are disqualified where the customer is referred "by a link that sends users indirectly to an Amazon Site via an intermediate site, without requiring the customer to click…" | Commission Income Statement §2(e), same page |
| R7 | Payment minimums (US) | Deposit $10; gift card $10 to $2,000; check $100 with a $15 processing fee | Commission Income Statement §6 (Payment Minimum Chart), same page |
| R8 | FTC disclosure standard | Disclose any financial, employment, personal, or family relationship. The disclosure should be "hard to miss", placed "with the endorsement message itself", and should not be "mixed into a group of hashtags or links". | FTC, *Disclosures 101 for Social Media Influencers* (Nov 2019), https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers |

**Not verified**

- **Commission rates (by category):** The official schedule at https://affiliate-program.amazon.com/help/operating/schedule redirected to an Amazon sign-in page. The compensation page https://affiliate-program.amazon.com/help/operating/compensation returned navigation only, with no rate table. Third-party pages disagree (for example, Kitchen at 4.5%, 5%, or 8%). **No rate is used in this audit.** Commission potential therefore cannot be calculated.
- **Trademark Guidelines and IP License (full text):** Not reviewed line by line. Manual review needed before any publication that names Amazon.
- **Program Policies, sections not read:** The Products Statement, the Mobile Application Policy, and the Influencer Program Policy were not read.

## 4. Coordination and repository findings

| # | Finding | Evidence |
|---|---|---|
| C1 | S-6602723A's board marks T2–T8 as "done", but its branch contains no artifacts for those tasks. | Commit `4a262c0` (2026-11-13 22:35:58 UTC) lists T1 done and T2–T8 done. `git ls-tree -r origin/arena/6602723a-zone2` shows only `.gitignore`, `COORDINATION.md`, and `README.md`. The `data/`, `docs/`, `site/`, `scripts/`, and `.github/` paths it claims do not exist on the remote. |
| C2 | Three other sessions claim overlapping scope with no shared artifacts. | `arena/1767c9d6-zone2` (`dcd4ee0`), `arena/6602723a-zone2` (`4a262c0`), and `arena/6b8bb130-zone2` (`d9d93a2`). Each has one or two commits, and only `COORDINATION.md` / `.gitignore` / `README.md` changed. 1767c9d6 and 6b8bb130 both claim `index.html`, `styles.css`, `app.js`, and `README.md`. |
| C3 | Branch naming conflicts with the session rule. | The shared protocol asks for `session-<id>/<task>` branches. This session's rule requires working on the single assigned branch, `arena/a5dd0fea-zone2`, so that is what this session uses. |
| C4 | GitHub Pages is enabled, but there is nothing to serve yet. | `gh api repos/kanlerxz87-cyber/Zone2/pages` reports `build_type: legacy`, `source: main /`, status `built`, URL https://kanlerxz87-cyber.github.io/Zone2/. `main` contains only `README.md` (`# Zone2`). |
| C5 | Repository baseline has no licence, no build, and no content. | `main` @ `f5771676`: one file, `README.md`, 7 bytes. |
| C6 | Price data cannot be shown without PA-API or Creators API. | See R2. Any price on the site must come from one of those APIs, or be left blank. |

## 5. Summary for the integration owner

- **Confirmed:** the three short links resolve to ASINs B0CDY277D3, B09B7SB46R, and B08DKYBTPH. The titles and the Home & Kitchen category are shown above. The disclosure wording, the price-display limit, the FTC standard, and the redirect-link exclusion are confirmed from official text.
- **Blocked:** commission rates, prices, ratings, review counts, and stock. These are left blank and flagged.
- **Irregular:** the claimed-done artifacts (C1), the storefront rating mismatch (§2), and the un-tagged resolved URLs (§1 notes).
