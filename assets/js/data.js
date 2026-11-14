/* Zone2 — verified dataset
 * Every value below was checked against the official source listed in its row's
 * "source" field on 2026-11-13. Values that could not be confirmed from an official
 * source are left as null/empty and flagged as UNVERIFIED (see flagged page).
 */

const VERIFIED_DATE = "2026-11-13";

const ASIN_SOURCE = {
  associatesHome: "https://affiliate-program.amazon.com/",
  policies: "https://affiliate-program.amazon.com/help/operating/policies",
  agreement: "https://affiliate-program.amazon.com/help/operating/agreement",
  // Publicly readable rate card (Table 1 + bounty tables + commission income limitations).
  rateCard: "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ",
  // Creators API reference: the sanctioned lookup path for ASIN -> catalog record.
  creatorsGetItems: "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/operations/get-items",
  // Public help pages re-read on 2026-11-14.
  linkFormat: "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC",
  disclosureHelp: "https://affiliate-program.amazon.com/help/node/topic/GHQNZAU6669EZS98",
  applicationReview: "https://affiliate-program.amazon.com/help/node/topic/G8TW5AE9XL2VX9VM",
  ftcDisclosures101:
    "https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers",
  googleOutboundLinks: "https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links",
};

/* ---- Product catalog (verified from official Amazon product pages) ---- */
const PRODUCTS = [
  {
    id: "p1",
    shortLink: "https://link.amazon/B04G1MEwY",
    shortCode: "B04G1MEwY",
    asin: "B0CDY277D3",
    brand: "CHEFMAN",
    title:
      "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black",
    category: "Home & Kitchen",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon.com product page (B0CDY277D3)",
  },
  {
    id: "p2",
    shortLink: "https://link.amazon/B02NbDxp3",
    shortCode: "B02NbDxp3",
    asin: "B09B7SB46R",
    brand: "Emeril Lagasse",
    title:
      "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.",
    category: "Home & Kitchen",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon.com product page (B09B7SB46R)",
  },
  {
    id: "p3",
    shortLink: "https://link.amazon/B00hJ57DV",
    shortCode: "B00hJ57DV",
    asin: "B08DKYBTPH",
    brand: "Chefman",
    title:
      "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel",
    category: "Home & Kitchen",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon.com product page (B08DKYBTPH)",
  },
];

/* ---- Verified specification rows (official Amazon + manufacturer pages) ----
 * Integrated from the combined session verification; manufacturer pages
 * re-fetched and confirmed during final integration (2026-11-13). */
const SPECS = [
  // Product 1 — CHEFMAN 6 Qt Dual Basket (B0CDY277D3)
  {
    pid: "p1",
    attribute: "Model number",
    value: "RJ38-SQPF-3TDB-2W",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Capacity",
    value: "6 qt total (two independent 3-qt baskets)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Power",
    value: "1700 W / 120 V",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Temperature range",
    value: "200–450 °F (95–235 °C, as stated by Chefman)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Dimensions",
    value: "13.38 × 11.81 × 10.63 in (33.98 × 30 × 27 cm)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Weight",
    value: "13.3 lb / 6.03 kg",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Control type",
    value: "Digital touchscreen",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Certification",
    value: "cETL approved",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p1",
    attribute: "Warranty",
    value: "1 year (Chefman assurance)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page",
  },
  // Product 2 — Emeril Lagasse 26QT French Door (B09B7SB46R)
  {
    pid: "p2",
    attribute: "Model number",
    value: "4-00675-02A-VN",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  {
    pid: "p2",
    attribute: "Capacity",
    value: "26 qt / 24.6 L",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  {
    pid: "p2",
    attribute: "Power",
    value: "1700 W / 120 V (single source: Amazon product-information block)",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon product page",
  },
  {
    pid: "p2",
    attribute: "Temperature range",
    value: "75–500 °F (single source: Amazon product-information block)",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon product page",
  },
  {
    pid: "p2",
    attribute: "Cooking functions / presets",
    value:
      "Unresolved - the manufacturer page disagrees with itself: Amazon listing title 24; Emeril description text 24; Emeril spec tile 25; Emeril feature block headed '10-In-1 Versatility' lists 10",
    status: "conflict",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Amazon listing title + three blocks of the Emeril Everyday page (flag F-19)",
  },
  {
    pid: "p2",
    attribute: "Dimensions",
    value: "16.9\"D × 15.8\"W × 14.8\"H",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  {
    pid: "p2",
    attribute: "Door style",
    value: "Dual French doors",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  {
    pid: "p2",
    attribute: "Included accessories",
    value:
      "Manufacturer states 7 premium accessories (basket, rotisserie spit, bake pan among them); Amazon's list differs in detail — itemised count not asserted",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  {
    pid: "p2",
    attribute: "Warranty",
    value: "1 year",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store",
  },
  // Product 3 — Chefman 8 Qt TurboFry (B08DKYBTPH)
  {
    pid: "p3",
    attribute: "Model number",
    value: "RJ38-SQSS-8T",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Capacity",
    value: "8 qt / 7.57 L",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Power",
    value: "1700 W / 120 V (Chefman) vs 1000 W / 120 V (Amazon bullet text)",
    status: "conflict",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official page vs Amazon listing (conflict)",
  },
  {
    pid: "p3",
    attribute: "Temperature range",
    value: "200–400 °F (95–205 °C, as stated by Chefman)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Presets",
    value: "4 (fries, chicken, fish, meat)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Dimensions",
    value:
      "Manufacturer: 15.4 × 12.6 × 13.5 in (39.11 × 32 × 34.29 cm) · Amazon spec table: 12.75\"D × 13.5\"W × 10\"H",
    status: "conflict",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official page vs Amazon listing (conflict)",
  },
  {
    pid: "p3",
    attribute: "Weight",
    value: "12.8 lb / 5.8 kg",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Certification",
    value: "cETL approved",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
  {
    pid: "p3",
    attribute: "Warranty",
    value: "1 year (Chefman assurance)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page",
  },
];

/* ---- Executive summary facts (all official Amazon Associates sources) ---- */
const EXEC_FACTS = [
  {
    label: "Platform program",
    value: "Amazon Associates — Amazon's affiliate marketing program",
    source: ASIN_SOURCE.associatesHome,
  },
  {
    label: "Commission ceiling (public, official)",
    value: "Up to 10% in associate commissions from qualifying purchases and programs",
    source: ASIN_SOURCE.associatesHome,
  },
  {
    label: "Payment timing",
    value: "Commission income is paid approximately 60 days after the end of the month in which it was earned",
    source: ASIN_SOURCE.policies,
  },
  {
    label: "Session / attribution window",
    value:
      "Session begins at Special Link click; purchases qualify if made within the session, via 1-Click, or added to cart and ordered no later than 89 days after the initial click-through",
    source: ASIN_SOURCE.policies,
  },
  {
    label: "Mandatory disclosure",
    value:
      "“As an Amazon Associate I earn from qualifying purchases.” — must be clearly and prominently stated on the site",
    source: ASIN_SOURCE.agreement,
  },
  {
    label: "Agent / AI transparency rule",
    value:
      "Any Agent accessing Program Content must identify itself in the user agent string as “Agent/[agent name]” and must not circumvent CAPTCHAs or human-check measures",
    source: ASIN_SOURCE.policies,
  },
  {
    label: "Document currency",
    value:
      "Operating Agreement updated October 15, 2025; Program Policies updated April 14, 2026",
    source: ASIN_SOURCE.agreement,
  },
];

/* ---- Market & niche analysis ---- */
const NICHE_ANALYSIS = [
  {
    item: "Primary niche",
    finding: "All three affiliate links resolve to air fryers / air fryer ovens",
    detail:
      "Products span a 6-quart dual-basket air fryer oven (Chefman), a 26-quart French-door air fryer toaster oven (Emeril Lagasse), and an 8-quart TurboFry air fryer (Chefman)",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    status: "verified",
  },
  {
    item: "Category",
    finding: "Amazon category: Home & Kitchen (all three listings)",
    detail: "Confirmed from the official Amazon product page titles for each ASIN",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    status: "verified",
  },
  {
    item: "Portfolio concentration",
    finding: "Single-category portfolio (100% Home & Kitchen)",
    detail:
      "No cross-category diversification in the current link set; scalable expansion would require new official product links from the user",
    source: ASIN_SOURCE.associatesHome,
    status: "verified",
  },
  {
    item: "Pricing analysis",
    finding: "Unverified",
    detail:
      "Amazon does not expose list price to automated verification; per policy, prices may only be shown if served within the Special Link or obtained via Creators API / PA API. Left blank — not inferred.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    status: "unverified",
  },
  {
    item: "Review / rating analysis",
    finding: "Unverified",
    detail:
      "Star ratings and review counts are not exposed to automated fetches, and Program Policy §6(t) restricts displaying Amazon customer reviews/star ratings unless obtained via Creators API or PA API. Left blank — not inferred.",
    source: ASIN_SOURCE.policies,
    status: "unverified",
  },
  {
    item: "Competition analysis",
    finding: "Within-niche competition among the three linked products",
    detail:
      "Two Chefman listings and one Emeril Lagasse listing compete in the same air-fryer niche; differentiation by capacity (6 Qt vs 8 Qt vs 26 QT) and feature set (dual baskets, French doors, 4-in-1 functions)",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    status: "verified",
  },
  {
    item: "Commission potential",
    finding: "Program-level ceiling: up to 10%",
    detail:
      "Official public statement: associates can earn up to 10% in commissions from qualifying purchases and programs. The fixed rate table (Standard Commission Income Statement, Table 1) is publicly readable and is transcribed on the Commissions view; which band a specific ASIN falls into still requires a catalog lookup, so the per-product rate stays unverified.",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
];

/* ---- Commission rate card (official program facts) ---- */
const COMMISSION_ROWS = [
  {
    item: "Program-level commission ceiling",
    value: "Up to 10%",
    note: "Official statement on Amazon Associates Central homepage",
    source: ASIN_SOURCE.associatesHome,
    status: "verified",
  },
  {
    item: "Published fixed rate — “Kitchen” band",
    value: "4.50%",
    note: "Table 1 verbatim: “Physical Books, Kitchen, Automotive — 4.50%”. Amazon publishes both “Kitchen” (4.50%) and “Home” (3.00%) as separate bands.",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
  {
    item: "Published fixed rate — “Home” band",
    value: "3.00%",
    note: "Table 1 verbatim: “Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins — 3.00%”",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
  {
    item: "Applicable rate for the three candidate ASINs",
    value: "",
    note: "Unresolved: neither the listing's browse path (Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers) nor the public rate table states which of the Kitchen / Home / All Other bands Amazon applies to a specific ASIN. A catalog lookup via Creators API GetItems is required, and it is not available in this workspace. Left blank — not inferred.",
    source: ASIN_SOURCE.creatorsGetItems,
    status: "unverified",
  },
  {
    item: "Qualifying revenue basis",
    value: "Amount Amazon actually receives, less shipping, gift-wrapping, handling, taxes, service charges, credits, rebates, credit card fees and bad debt",
    note: "Commission Income Statement §1",
    source: ASIN_SOURCE.policies,
    status: "verified",
  },
  {
    item: "Payment timing",
    value: "Approximately 60 days after end of the month earned",
    note: "Commission Income Statement §6",
    source: ASIN_SOURCE.policies,
    status: "verified",
  },
  {
    item: "Payment minimums (US)",
    value: "Direct deposit $10 · Gift card $10–$2,000 · Check $100 (+$15 processing fee)",
    note: "Payment Minimum Chart, Commission Income Statement §6",
    source: ASIN_SOURCE.policies,
    status: "verified",
  },
];

/* ---- Compliance requirements (verified from official program documents) ---- */
const COMPLIANCE_ROWS = [
  {
    requirement: "Mandatory disclosure",
    detail:
      "Site must clearly and prominently state: “As an Amazon Associate I earn from qualifying purchases.”",
    source: ASIN_SOURCE.agreement,
    ref: "Operating Agreement §5",
  },
  {
    requirement: "Original content",
    detail:
      "Site(s) must contain original content and be publicly available; third-party materials require significant commentary, analysis, or transformation",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §1",
  },
  {
    requirement: "Special Links with Associates tag",
    detail:
      "Every link must include the assigned Associates ID / tag parameter so referrals are tracked; sub-tags may be requested for performance monitoring",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §2",
  },
  {
    requirement: "Price & availability display",
    detail:
      "Prices/availability may only be shown if served within the link, or obtained via Creators API / PA API in compliance with the License; comparisons must show the lowest new price (and lowest used price if provided)",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §2(b)",
  },
  {
    requirement: "Agent / AI transparency",
    detail:
      "Agents accessing Program Content must identify themselves in the user agent string as “Agent/[agent name]”, not mimic human behavior, respond truthfully to human-verification prompts, and not circumvent blocking measures",
    source: ASIN_SOURCE.policies,
    ref: "IP License §4 (Agent Terms)",
  },
  {
    requirement: "No machine-learning training on Program Content",
    detail:
      "Program Content may not be used, without express prior written approval, to develop or improve large language / multimodal / machine learning models, or in direct training or fine-tuning of a model",
    source: ASIN_SOURCE.policies,
    ref: "IP License §1 / §2(e)",
  },
  {
    requirement: "No purchased search on Amazon marks",
    detail:
      "Must not bid on or purchase keywords including “amazon”, “kindle” or any Amazon trademark (Prohibited Paid Search Placement)",
    source: ASIN_SOURCE.policies,
    ref: "Commission Income Statement §2(c); Participation §6(f)",
  },
  {
    requirement: "No artificial traffic",
    detail:
      "Must not artificially generate clicks or impressions, or create Sessions via robots or software",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §6(s)",
  },
  {
    requirement: "No self-purchases through Special Links",
    detail:
      "Must not purchase products through one's own Special Links, nor permit friends, family, employees or contractors to do so",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §6(u)",
  },
  {
    requirement: "No price-tracking / price-alert functionality",
    detail: "Site must not have price tracking and/or price alerting functionality unless otherwise agreed by Amazon",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §6(y)",
  },
  {
    requirement: "Review & rating display restriction",
    detail:
      "Amazon customer reviews or star ratings may only be displayed if obtained via Creators API or PA API in compliance with the License",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §6(t)",
  },
  {
    requirement: "Promotion-removal duty",
    detail:
      "References to limited-time promotions (e.g. discounts) must be removed as soon as the promotion ends on the relevant Amazon site",
    source: ASIN_SOURCE.policies,
    ref: "Participation Requirements §2(b)",
  },
];

/* ---- Marketing content plan (AI-generated content outputs) ---- */
const CONTENT_ROWS = [
  {
    content: "Product review article",
    target: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven (B0CDY277D3)",
    format: "SEO-optimized long-form review",
    status: "Ready",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    content: "Product review article",
    target: "Emeril Lagasse 26QT French Door Air Fryer Toaster Oven (B09B7SB46R)",
    format: "SEO-optimized long-form review",
    status: "Ready",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    content: "Product review article",
    target: "Chefman Air Fryer 8 Qt TurboFry 4-in-1 (B08DKYBTPH)",
    format: "SEO-optimized long-form review",
    status: "Ready",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
  {
    content: "Comparison guide",
    target: "Chefman 6 Qt Dual Basket vs Chefman 8 Qt TurboFry",
    format: "Side-by-side comparison article",
    status: "Ready",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    content: "Comparison guide",
    target: "Compact vs large-capacity air fryer ovens (6 Qt vs 26 QT)",
    format: "Buying-guide comparison article",
    status: "Ready",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    content: "Buying guide",
    target: "“Best air fryer for family meals” buying guide",
    format: "SEO buying guide with Special Link integration",
    status: "Ready",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
];

/* ---- Campaign & link tracking plan ---- */
/* Status semantics: a campaign is only "Published" when ledger/campaigns.json holds an enabled entry whose
   ASIN came from a verified catalog record. That file is EMPTY_BY_DESIGN (F-06/F-07), so every row below is
   correctly reported as not live. Editing these strings to "Configured" would assert links that do not exist. */
const TRACKING_ROWS = [
  {
    campaign: "Launch — air fryer niche",
    product: "All three linked products",
    linkType: "Special Link with Associates tag (tracking required)",
    status: "Not live — blocked",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Content — review articles",
    product: "B0CDY277D3, B09B7SB46R, B08DKYBTPH",
    linkType: "Special Link with Associates tag + sub-tag for A/B testing",
    status: "Not live — blocked",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Comparison guides",
    product: "Paired ASINs",
    linkType: "Special Link with Associates tag",
    status: "Not live — blocked",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Conversion reporting",
    product: "All linked products",
    linkType: "Associates Central reports (clicks, sessions, commission income)",
    status: "Not live — no reports connected",
    source: ASIN_SOURCE.policies,
  },
];

/* ---- Flagged for review ----
 * These are the dashboard's reader-facing flags. The canonical register is ledger/flags.json (F-01..F-19);
 * every row below that has a canonical counterpart names it in `ledger_flag` and links to its entry on the
 * Flagged for Review page in the findings namespace, so a reader can always reach the full text + sources.
 * Rows without a canonical counterpart are dashboard-specific (e.g. a per-product UNVERIFIED cell).
 */
const LEDGER_FLAGS_URL = "pages/flags.html";
const FLAGGED_ROWS = [
  {
    item: "Link-code / ASIN mismatch — Product 1",
    detail:
      "Provided link https://link.amazon/B04G1MEwY redirects to amazon.com/dp/B0CDY277D3. The code B04G1MEwY is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Treated as an opaque short-link token; the destination ASIN B0CDY277D3 is the verified product.",
    ledger_flag: "F-01",
    ledger_url: LEDGER_FLAGS_URL + "#F-01",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Link-code / ASIN mismatch — Product 2",
    detail:
      "Provided link https://link.amazon/B02NbDxp3 redirects to amazon.com/dp/B09B7SB46R. The code B02NbDxp3 is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Destination ASIN B09B7SB46R is the verified product.",
    ledger_flag: "F-01",
    ledger_url: LEDGER_FLAGS_URL + "#F-01",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    item: "Link-code / ASIN mismatch — Product 3",
    detail:
      "Provided link https://link.amazon/B00hJ57DV redirects to amazon.com/dp/B08DKYBTPH. The code B00hJ57DV is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Destination ASIN B08DKYBTPH is the verified product.",
    ledger_flag: "F-01",
    ledger_url: LEDGER_FLAGS_URL + "#F-01",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
  {
    item: "Price — all three products (UNVERIFIED / not published)",
    detail:
      "Amazon list prices could not be confirmed from an official source via automated verification (Amazon bot protection; policy restricts Amazon price display to served links or Creators API / PA API). Manufacturer-site prices were verified on the official Chefman and Emeril Everyday pages but are deliberately not published on this site, in line with the program's price-display restrictions. Left blank in all tables.",
    ledger_flag: "F-04",
    ledger_url: LEDGER_FLAGS_URL + "#F-04",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Star rating & review count — all three products (UNVERIFIED)",
    detail:
      "Rating and review-count could not be confirmed from an official source; Program Policy §6(t) also restricts displaying Amazon ratings/reviews outside Creators API / PA API. Left blank in all tables.",
    ledger_flag: "F-06",
    ledger_url: LEDGER_FLAGS_URL + "#F-06",
    source: ASIN_SOURCE.policies,
  },
  {
    item: "Applicable commission band per ASIN (UNVERIFIED)",
    detail:
      "The official rate schedule requires Associates sign-in. Only the program-level public ceiling “up to 10%” is verified; the category-specific rate is left blank.",
    source: "https://affiliate-program.amazon.com/help/operating/schedule",
  },
  {
    item: "Availability / stock status (UNVERIFIED)",
    detail:
      "Current availability could not be confirmed from an official source via automated verification. Left blank in all tables.",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    item: "Conflict — Emeril Lagasse cooking functions / presets",
    detail:
      "The Amazon listing title states 24 cooking functions; the manufacturer's spec tile states 25 cooking pre-sets. Both values are published; neither is presented as definitive.",
    ledger_flag: "F-19",
    ledger_url: LEDGER_FLAGS_URL + "#F-19",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
  },
  {
    item: "Conflict — Chefman 8 Qt power rating",
    detail:
      "Amazon bullet text for B08DKYBTPH states 1000 Watts/120 Volts; Chefman's official product page states 1700 W / 120 V for the same model number. Manufacturer figure published; conflict flagged.",
    ledger_flag: "F-19",
    ledger_url: LEDGER_FLAGS_URL + "#F-19",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
  },
  {
    item: "Conflict — Chefman 8 Qt dimensions",
    detail:
      "Chefman's official page states 15.4 × 12.6 × 13.5 in (39.11 × 32 × 34.29 cm); Amazon's spec table states 12.75\"D × 13.5\"W × 10\"H. Both published as separate conflicting rows.",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
  },
  {
    item: "Associates tag absent on resolved short links",
    detail:
      "The resolved link.amazon URLs carry no Associates tag parameter. Live click/conversion tracking requires Special Links that include the assigned Associates ID / tag (Participation Requirements §2). Flagged for account configuration before launch.",
    ledger_flag: "F-07",
    ledger_url: LEDGER_FLAGS_URL + "#F-07",
    source: "https://affiliate-program.amazon.com/help/operating/policies",
  },
];

const PLATFORM_FEATURES = [
  { name: "Automated product research", desc: "Collects and organizes the full requirement list for affiliate products with verified official sources." },
  { name: "Trend & conversion analysis", desc: "Identifies trending and high-converting products; scores competition and commission potential." },
  { name: "Pricing, review & competition analysis", desc: "Analyzes pricing, reviews and competitive positioning — only from official sources; unverifiable values are flagged, never inferred." },
  { name: "SEO content generation", desc: "Generates SEO-optimized product articles, comparisons and buying guides from verified product data." },
  { name: "Link & campaign management", desc: "Creates and manages Special Links with Associates tags and sub-tags; tracks clicks and conversions." },
  { name: "Continuous optimization", desc: "Reconciles campaign performance monthly and continuously optimizes for affiliate revenue within program policies." },
  { name: "Policy compliance", desc: "Enforces Amazon Associates disclosure requirements and operating policies, including AI/agent transparency rules." },
];
