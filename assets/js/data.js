/* Zone2 — verified dataset
 * Every value below was checked against the official source listed in its row's
 * "source" field on 2026-11-13. Values that could not be confirmed from an official
 * source are left as null/empty and flagged as UNVERIFIED (see flagged page).
 */

const VERIFIED_DATE = "2026-11-14";

const ASIN_SOURCE = {
  associatesHome: "https://affiliate-program.amazon.com/",
  policies: "https://affiliate-program.amazon.com/help/operating/policies",
  agreement: "https://affiliate-program.amazon.com/help/operating/agreement",
  rateCard: "https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ",
  accountRateCard: "https://affiliate-program.amazon.com/help/operating/schedule",
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

/* ---- Supplied-link resolution evidence (re-verified 2026-11-14) ----
 * Each submitted link was fetched directly and its final URL recorded. A control fetch of a
 * bare, valid ASIN carries the same plpRedirect=mhFallback / lv=shuf markers, so those
 * markers are not evidence of a fallback. What is verifiable: the destination ASIN, its title
 * and its category path. What is NOT verifiable: that these are the items the brief named,
 * because no public Amazon document binds a link.amazon code to a destination ASIN.
 */
const LINK_RESOLUTIONS = [
  {
    submittedLink: "https://link.amazon/B04G1MEwY",
    token: "B04G1MEwY",
    tokenLength: "9 characters (an ASIN is 10)",
    dpResult: "Amazon Page Not Found",
    resolvedAsin: "B0CDY277D3",
    resolvedTitle:
      "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black",
    categoryPath: "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    attribution: "btn_ref=srctok-<16 hex> - identical on same-day re-fetch, rotates between days",
    identity: "Destination verified - link to ASIN mapping not documented by Amazon",
    evidence: [
      "https://link.amazon/B04G1MEwY",
      "https://www.amazon.com/dp/B0CDY277D3",
      "https://www.amazon.com/dp/B04G1MEwY",
    ],
  },
  {
    submittedLink: "https://link.amazon/B02NbDxp3",
    token: "B02NbDxp3",
    tokenLength: "9 characters (an ASIN is 10)",
    dpResult: "Amazon Page Not Found",
    resolvedAsin: "B09B7SB46R",
    resolvedTitle:
      "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.",
    categoryPath: "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    attribution: "btn_ref=srctok-<16 hex> - identical on same-day re-fetch, rotates between days",
    identity: "Destination verified - link to ASIN mapping not documented by Amazon",
    evidence: [
      "https://link.amazon/B02NbDxp3",
      "https://www.amazon.com/dp/B09B7SB46R",
      "https://www.amazon.com/dp/B02NbDxp3",
    ],
  },
  {
    submittedLink: "https://link.amazon/B00hJ57DV",
    token: "B00hJ57DV",
    tokenLength: "9 characters (an ASIN is 10)",
    dpResult: "Amazon Page Not Found",
    resolvedAsin: "B08DKYBTPH",
    resolvedTitle:
      "Chefman Air Fryer 8 Qt | TurboFry 4-in-1 with 450F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel",
    categoryPath: "Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers",
    attribution: "btn_ref=srctok-<16 hex> - identical on same-day re-fetch, rotates between days",
    identity: "Destination verified - link to ASIN mapping not documented by Amazon",
    evidence: [
      "https://link.amazon/B00hJ57DV",
      "https://www.amazon.com/dp/B08DKYBTPH",
      "https://www.amazon.com/dp/B00hJ57DV",
    ],
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
    value: "24 per Amazon listing title; 25 per the manufacturer's spec tile",
    status: "conflict",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Amazon title + Emeril Everyday spec tile (conflict)",
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

/* ---- Category bands (Table 1 of the published Commission Income Statement) ----
 * Transcribed row by row from the official statement on 2026-11-14. Every band row links to
 * the same official source. The "products in band" column is assigned only from a product's
 * own official category path, and is left blank where no verified product falls in the band.
 */
const CATEGORY_BANDS = [
  {
    band: "C-10",
    categories: "Luxury Beauty, Luxury Stores Beauty, Amazon Explore",
    rate: "10.00%",
    products: "",
    productSource: "",
    note: "Highest published fixed rate in Table 1.",
    subpage: "pages/categories/luxury-beauty-exploration.html",
  },
  {
    band: "C-05",
    categories: "Digital Music, Physical Music, Handmade, Digital Videos",
    rate: "5.00%",
    products: "",
    productSource: "",
    note: "Small category set; Handmade is the only broad merchandising group at this rate.",
    subpage: "pages/categories/music-handmade-video.html",
  },
  {
    band: "C-045",
    categories: "Physical Books, Kitchen, Automotive",
    rate: "4.50%",
    products: "B0CDY277D3, B09B7SB46R, B08DKYBTPH",
    productSource: "https://www.amazon.com/dp/B0CDY277D3",
    note: "All three products sit at Kitchen & Dining on their official category path, which names the Kitchen row of this band.",
    subpage: "pages/categories/books-kitchen-automotive.html",
  },
  {
    band: "C-04",
    categories:
      "Amazon Fire Tablet Devices, Amazon Kindle Devices, Luxury Stores Fashion, Apparel, Amazon Cloud Cam Devices, Fire TV Edition Smart TVs, Amazon Fire TV Devices, Amazon Echo Devices, Ring Devices, Watches, Jewelry, Luggage, Shoes, and Handbags & Accessories",
    rate: "4.00%",
    products: "",
    productSource: "",
    note: "Includes Amazon's own device lines; also the value used for All Other Categories (see C-OTH).",
    subpage: "pages/categories/devices-fashion-accessories.html",
  },
  {
    band: "C-03",
    categories:
      "Toys, Furniture, Home, Home Improvement, Lawn & Garden, Pets Products, Headphones, Beauty, Musical Instruments, Business & Industrial Supplies, Outdoors, Tools, Sports, Baby Products, Amazon Coins",
    rate: "3.00%",
    products: "",
    productSource: "",
    note: "Largest cluster of high-volume consumer categories in Table 1. This is the Home row of the Home & Kitchen department.",
    subpage: "pages/categories/home-toys-outdoors-pets.html",
  },
  {
    band: "C-025",
    categories: "PC, PC Components, DVD & Blu-Ray",
    rate: "2.50%",
    products: "",
    productSource: "",
    note: "High-ASP categories with thin rates; revenue math depends on basket, not on rate.",
    subpage: "pages/categories/pc-components-media.html",
  },
  {
    band: "C-02",
    categories: "Televisions, Digital Video Games",
    rate: "2.00%",
    products: "",
    productSource: "",
    note: "Lowest non-zero fixed rate band in Table 1 (before the 1.00% band).",
    subpage: "pages/categories/tv-games.html",
  },
  {
    band: "C-01",
    categories: "Amazon Fresh, Physical Video Games & Video Game Consoles, Grocery, Health & Personal Care",
    rate: "1.00%",
    products: "",
    productSource: "",
    note: "High repeat-purchase categories with the lowest positive fixed rate.",
    subpage: "pages/categories/grocery-health-console.html",
  },
  {
    band: "C-00",
    categories:
      "Gift Cards; Wireless Service Plans; Alcoholic Beverages; Digital Kindle Products purchased as a subscription; Vehicles - Leasing and Sales; Pet Prescription Medications; Food prepared and delivered from a restaurant; Amazon Appstore, Prime Now, or Amazon Pay Places",
    rate: "0.00%",
    products: "",
    productSource: "",
    note: "Pays no Standard Commission Income - excluded from the niche queue before ranking.",
    subpage: "pages/categories/zero-rate-exclusions.html",
  },
  {
    band: "C-00b",
    categories: "Coach",
    rate: "0.00%",
    products: "",
    productSource: "",
    note: "Named single category at 0.00%, listed separately from the exclusion block in Table 1.",
    subpage: "pages/categories/coach-exclusion.html",
  },
  {
    band: "C-OTH",
    categories: "All Other Categories",
    rate: "4.00%",
    products: "",
    productSource: "",
    note: "Default band for a verified ASIN whose category is not in the rows above.",
    subpage: "pages/categories/all-other-categories.html",
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
    finding: "Category rate for this portfolio: 4.50% (the Kitchen row of Table 1)",
    detail:
      "Amazon's Standard Commission Income Statement publishes a fixed rate per category band and is readable without signing in: Physical Books, Kitchen, Automotive - 4.50%. The other row inside the same Home & Kitchen department is Home - 3.00%. The rate applied to an individual ASIN is only visible in the account holder's own Associates Central report, so that cell stays blank.",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
  {
    item: "Program-level commission ceiling",
    finding: "Up to 10%",
    detail:
      "Official public statement: associates can earn up to 10% in commissions from qualifying purchases and programs.",
    source: ASIN_SOURCE.associatesHome,
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
    item: "Standard commission rate - Kitchen category (Table 1)",
    value: "4.50%",
    note:
      "Published fixed rate for the Physical Books, Kitchen, Automotive row of Table 1. All three products sit at Home & Kitchen > Kitchen & Dining > Small Appliances > Fryers > Air Fryers on their official product pages, which names the Kitchen band.",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
  {
    item: "Standard commission rate - Home category (Table 1)",
    value: "3.00%",
    note:
      "Published fixed rate for the Toys, Furniture, Home, Home Improvement row of Table 1 - the other row inside the same Home & Kitchen department. Shown so the full set of applicable bands is visible, not only the one these products match.",
    source: ASIN_SOURCE.rateCard,
    status: "verified",
  },
  {
    item: "Rate applied to one specific ASIN (account rate card)",
    value: "",
    note:
      "The account rate card redirects to Amazon sign-in (customratecard), so the rate Amazon actually applies to an individual ASIN cannot be confirmed from a public page. Left blank - not inferred from the category band.",
    source: ASIN_SOURCE.accountRateCard,
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
const TRACKING_ROWS = [
  {
    campaign: "Launch — air fryer niche",
    product: "All three linked products",
    linkType: "Special Link with Associates tag (tracking required)",
    status: "Configured",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Content — review articles",
    product: "B0CDY277D3, B09B7SB46R, B08DKYBTPH",
    linkType: "Special Link with Associates tag + sub-tag for A/B testing",
    status: "Configured",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Comparison guides",
    product: "Paired ASINs",
    linkType: "Special Link with Associates tag",
    status: "Configured",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Conversion reporting",
    product: "All linked products",
    linkType: "Associates Central reports (clicks, sessions, commission income)",
    status: "Monthly reconciliation",
    source: ASIN_SOURCE.policies,
  },
];

/* ---- Flagged for review ---- */
const FLAGGED_ROWS = [
  {
    item: "Link-code / ASIN mismatch - Product 1",
    detail:
      "Provided link https://link.amazon/B04G1MEwY resolves to amazon.com/dp/B0CDY277D3, and to that same destination on every fetch across 2026-11-13 and 2026-11-14. The code B04G1MEwY is 9 characters and is not a valid Amazon /dp/ ASIN (a direct fetch of https://www.amazon.com/dp/B04G1MEwY returns Page Not Found), and no public Amazon document binds a link.amazon code to a destination ASIN - so the destination is a verified fact about the link, but is not established as the item the brief named.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Link-code / ASIN mismatch - Product 2",
    detail:
      "Provided link https://link.amazon/B02NbDxp3 resolves to amazon.com/dp/B09B7SB46R, and to that same destination on every fetch across 2026-11-13 and 2026-11-14. The code B02NbDxp3 is 9 characters and is not a valid Amazon /dp/ ASIN (a direct fetch of https://www.amazon.com/dp/B02NbDxp3 returns Page Not Found), and no public Amazon document binds a link.amazon code to a destination ASIN - so the destination is a verified fact about the link, but is not established as the item the brief named.",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    item: "Link-code / ASIN mismatch - Product 3",
    detail:
      "Provided link https://link.amazon/B00hJ57DV resolves to amazon.com/dp/B08DKYBTPH, and to that same destination on every fetch across 2026-11-13 and 2026-11-14. The code B00hJ57DV is 9 characters and is not a valid Amazon /dp/ ASIN (a direct fetch of https://www.amazon.com/dp/B00hJ57DV returns Page Not Found), and no public Amazon document binds a link.amazon code to a destination ASIN - so the destination is a verified fact about the link, but is not established as the item the brief named.",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
  {
    item: "Price — all three products (UNVERIFIED / not published)",
    detail:
      "Amazon list prices could not be confirmed from an official source via automated verification (Amazon bot protection; policy restricts Amazon price display to served links or Creators API / PA API). Manufacturer-site prices were verified on the official Chefman and Emeril Everyday pages but are deliberately not published on this site, in line with the program's price-display restrictions. Left blank in all tables.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Star rating & review count — all three products (UNVERIFIED)",
    detail:
      "Rating and review-count could not be confirmed from an official source; Program Policy §6(t) also restricts displaying Amazon ratings/reviews outside Creators API / PA API. Left blank in all tables.",
    source: ASIN_SOURCE.policies,
  },
  {
    item: "Rate applied to one specific ASIN (UNVERIFIED)",
    detail:
      "The published Table 1 category rates are public and are shown on the Analysis page (Kitchen 4.50%, Home 3.00%). The rate Amazon actually applies to an individual ASIN lives in the account rate card, which redirects to Amazon sign-in, so that cell is left blank rather than inferred from the band. Left blank in all tables.",
    source: "https://affiliate-program.amazon.com/help/operating/schedule",
  },
  {
    item: "Link-to-ASIN mapping is not documented by Amazon (UNVERIFIED)",
    detail:
      "Each supplied link resolves to one product and the destination never changes, but no public Amazon help page or program document states what a link.amazon code maps to. The mapping is therefore observed behaviour, not documented intent. Owner action: confirm it in Associates Central.",
    source: "https://affiliate-program.amazon.com/help/operating/policies",
  },
  {
    item: "Per-request attribution token rotates between days",
    detail:
      "Each link returns a per-link token of the form btn_ref=srctok-<16 hex>. The token is identical on same-day re-fetch and differs between 2026-11-13 and 2026-11-14 for the same link, while the destination ASIN never changed. Recorded so token rotation is not later mistaken for destination instability; the token must not be used as a stable identifier.",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
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
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
  },
  {
    item: "Conflict — Chefman 8 Qt power rating",
    detail:
      "Amazon bullet text for B08DKYBTPH states 1000 Watts/120 Volts; Chefman's official product page states 1700 W / 120 V for the same model number. Manufacturer figure published; conflict flagged.",
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
