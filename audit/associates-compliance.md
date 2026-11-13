# Amazon Associates and FTC requirements that apply to this project

Snapshot: 2026-11-13 (UTC). Every row cites an official page. Quotations are verbatim unless marked *paraphrase*.

**Document versions read:** Associates Program Operating Agreement, updated October 15, 2025; Associates Program Policies, updated April 14, 2026. Both are listed on the Associates Central pages below.

**Blocking items** (a human or account action is required before commission can be tracked): C-04, C-18, C-19.

---

## A. Disclosure

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-01 | Associates must "identify yourself on your Site as an Amazon Associate with the language required by the Operating Agreement". The required statement is: **"As an Amazon Associate I earn from qualifying purchases."** It must appear "clearly and conspicuously" on the site. | [Associates Help: Why do I have to identify myself as an Associate?](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Yes | Show this exact sentence on every page that contains an affiliate link (footer and near the product tables). |
| C-02 | Link-level disclosure must be "Clear" and "Conspicuous", placed "near any affiliate link or product review". Examples given: "(paid link)", "#ad", "#CommissionsEarned". | [Associates Help (same page)](https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98) | Yes | Add a short "(affiliate link)" marker beside each product link. |
| C-03 | FTC: disclose a "material connection" clearly and where it will be seen. Disclosures "are likely to be missed if they appear only on an ABOUT ME or profile page". | [FTC, Disclosures 101 for Social Media Influencers](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers) | Yes | Place the disclosure near the product content, not only on a disclosure subpage. |

## B. Links and tracking

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-04 | "Special Links must use the Associates ID we have assigned to you." Also: "you must include your Associates ID or 'tag' (appearing as XXXXX-##...) as a parameter in the URL of each link you place on your Site to an Amazon Site." | [Program Policies, Participation Requirements §2(a)–(b)](https://affiliate-program.amazon.com/help/operating/policies) | Yes | **BLOCKING.** The supplied links carry no tag (see I-03). The Associate ID must come from the account owner. The agent cannot create or infer it. |
| C-11 | Each use of Program Content must be linked "solely to the related Product detail page or other relevant page of an Amazon Site and not to any other page." | [Program Policies, IP License §1](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Every product link must point to a product detail page (`/dp/ASIN`). |
| C-08 | "Special Links must link to Products." And: "When linking to pages with Product lists you must have additional original content on your Site that is relevant to the Special Link." | [Program Policies, Participation Requirements §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Category pages must carry original analysis, not just a list of links. |
| C-15 | Commission is disqualified for "any Product purchase that is not correctly tracked or reported because the links from your site to the relevant Amazon Site are not properly formatted" (CIS §2(g)). Also disqualified: a purchase "referred to an Amazon Site by a link that sends users indirectly to an Amazon Site via an intermediate site" (CIS §2(e), "Redirecting Link"). | [Program Policies, Commission Income Statement §2](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Use canonical `/dp/ASIN` links with the tag. Do not route links through third-party shorteners or redirect pages. The supplied `link.amazon` codes redirect; see I-01. |
| C-13 | Purchases referred through paid ads that use Amazon marks or keywords are disqualified (CIS §2(c), "Prohibited Paid Search Placement"). | [Program Policies, CIS §2(c)](https://affiliate-program.amazon.com/help/operating/policies) | Only if paid ads are used | Do not run paid search or social ads that use Amazon keywords. |

## C. Price, availability, and product content

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-05 | "Product prices and availability may vary... your Site may only show prices and availability if: (a) we serve the link in which that price and availability data are displayed, or (b) you obtain Product pricing and availability data via Creators API or PA API." | [Program Policies, Participation Requirements §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | Yes | **Prices and availability are withheld** from every artifact. The page uses "View price on Amazon" links only. The owner must decide whether to set up PA-API access. |
| C-06 | Comparison-format price display must show "the lowest 'new' price and, if we provide it..., the lowest 'used' price". | [Program Policies, Participation Requirements §2(b)](https://affiliate-program.amazon.com/help/operating/policies) | Only if prices are shown | Not applicable while prices are withheld. |
| C-07 | "Original content utilizing third-party materials must contain significant commentary, analysis, or transformation to any materials you include." | [Program Policies, Participation Requirements §1](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Do not paste Amazon bullet points or descriptions. Analysis must be the site's own. |
| C-10 | "You will not add to, delete from, or otherwise alter any Program Content in any way" (except resizing images and truncating text that does not change its meaning). | [Program Policies, Participation Requirements §6(a)](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Quote product titles and specs exactly, and do not edit them. |
| C-09 | The IP License grants rights to "Program Content", which includes "Creators API, PA API, Data Feeds and Product Advertising Content", and it "does not include... any use of data mining, robots, or similar data gathering and extraction tools". Ratings, review counts, and BSR were collected from product pages, not from PA-API. | [Program Policies, IP License §1](https://affiliate-program.amazon.com/help/operating/policies) | **Flag for owner decision** | This audit records ratings and BSR with a review flag. The owner must decide whether to publish them and whether to replace page reads with PA-API data. |
| C-22 | *Paraphrase:* Associates may not use Special Links or Program Content to develop machine-learning models without prior written approval. | [Program Policies, Participation Requirements §5](https://affiliate-program.amazon.com/help/operating/policies) | Yes, for any "AI-powered" design | No model is trained on Amazon data. Any AI feature that uses Program Content needs prior written approval. |

## D. Trademarks and naming

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-12 | Amazon Marks may be used "ONLY BY DISPLAY ON YOUR SITE WITH THE PURPOSE OF ADVERTISING AVAILABILITY OF PRODUCTS ON AN AMAZON SITE, WITH A CORRESPONDING SPECIAL LINK". Amazon marks may not appear in any domain name, subdomain, or username (Participation §1(g); Trademark Guidelines §8). | [Program Policies, Trademark Guidelines §1 and §8](https://affiliate-program.amazon.com/help/operating/policies) | Yes | The site URL `kanlerxz87-cyber.github.io/Zone2` contains no Amazon mark. Do not add "amazon" to the domain or repo name. |

## E. Program rules that affect content and promotion

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-20 | Operating Agreement preamble: content posted on Amazon.com must follow Amazon's Community Guidelines, "including the prohibition of customer reviews that are created, edited, or removed in exchange for compensation." | [Operating Agreement, preamble](https://affiliate-program.amazon.com/help/operating/agreement) | Informational. The clause governs Amazon.com content, not this site. | Good practice: do not solicit or create reviews for compensation. |
| C-21 | Participation §3(e): disclose cookies, pixels, and other tracking on the site. | [Program Policies, Participation Requirements §3(e)](https://affiliate-program.amazon.com/help/operating/policies) | Only if analytics or tracking is added | The current design uses no trackers. Add a disclosure before adding any analytics. |

## F. Eligibility and payment (informational)

| ID | Requirement (quoted or paraphrased) | Source | Applies? | Action for this project |
|---|---|---|---|---|
| C-18 | Participation §1: "If you are a non-US person participating in the Associates Program, you agree that unless you have otherwise notified us in your tax information you will perform all services under the Agreement outside the United States." The Associates Central country selector on the page header does **not** list Norway. The selector contains: United States, United Kingdom, Germany, France, Japan, Canada, Italy, Spain, India, Brazil, Mexico, Australia, UAE, Singapore, Netherlands, Saudi Arabia, Sweden, Poland, Belgium, Ireland, Turkey, Egypt. | [Program Policies §1](https://affiliate-program.amazon.com/help/operating/policies) and [Associates Central country list](https://affiliate-program.amazon.com/help/operating/compensation) | **Flag** | **BLOCKING until confirmed.** The owner (Oslo, NO) must confirm in Associates Central that a Norway-based account is eligible. This audit does not conclude eligibility. |
| C-19 | Participation §1: the Site "must contain original content and be publicly available via the website address provided in the application." Sites must be applied for and approved. | [Program Policies, Participation Requirements §1](https://affiliate-program.amazon.com/help/operating/policies) | Yes | **BLOCKING.** The owner must apply with this site URL. |
| C-14 | Standard commission rates by category. **Unverified.** The official rate card at `/help/operating/schedule` redirects to a sign-in page, so no rate could be read from an official source. The policy document refers to it as the "Standard Commission Income" appendix. | [Program Policies, Appendix link](https://affiliate-program.amazon.com/help/operating/policies) | Yes | Commission rate fields are **left blank**. Secondary sites report figures, but those are not official and are not used. See [irregularities.md](irregularities.md), I-09. |
| C-16 | Qualifying purchase window: a 24-hour session from click, extended to 89 days when the item is added to the cart; purchase counts only if shipped within 180 days. | [Program Policies, CIS §1(b)](https://affiliate-program.amazon.com/help/operating/policies) | Informational | Useful context for the analysis page. No performance is estimated. |
| C-17 | Payment minimums (U.S.): direct deposit $10; gift card $10 to $2,000; check $100 with a $15 processing fee. | [Program Policies, Commission Income Reporting and Payment §6](https://affiliate-program.amazon.com/help/operating/policies) | Informational | Context only. |

---

## Source register (all official, read 2026-11-13)

| Source | URL | Used for |
|---|---|---|
| Associates Program Operating Agreement | https://affiliate-program.amazon.com/help/operating/agreement | C-20, preamble |
| Associates Program Policies (Commission Income Statement, Participation Requirements, IP License, Trademark Guidelines, Payment) | https://affiliate-program.amazon.com/help/operating/policies | C-02 to C-19, C-21, C-22 |
| Associates Help: disclosure requirements | https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98 | C-01, C-02 |
| Associates Central compensation page (country list) | https://affiliate-program.amazon.com/help/operating/compensation | C-18 |
| Associates rate schedule (login required; not readable) | https://affiliate-program.amazon.com/help/operating/schedule | C-14 (unverified) |
| FTC, Disclosures 101 for Social Media Influencers | https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers | C-03 |
| GitHub Pages configuration (API) | https://api.github.com/repos/kanlerxz87-cyber/Zone2/pages | Pages source: `main` `/`, public, status `built` |
