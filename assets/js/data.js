/* Zone2 — verified dataset
 * Every value below was checked against the official source listed in its row's
 * "source" field on 2026-11-14. Values that could not be confirmed from an official
 * source are left as null/empty and flagged as UNVERIFIED (see flagged page).
 *
 * T23 (final integration): the PRODUCT, SPEC, RESOLUTION_EVIDENCE and FLAGGED_ROWS blocks are
 * GENERATED from ledger/*.json by tools/build_root_data.py — do not hand-edit them; edit the
 * ledger and re-run the generator. The remaining blocks are hand-authored program facts.
 */

const VERIFIED_DATE = "2026-11-14";

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
  // The three links supplied in the brief, and the unknown-code control run against the same
  // short-link service (an unknown code returns a 404, which is what decides how to read them).
  suppliedLink1: "https://link.amazon/B04G1MEwY",
  suppliedLink2: "https://link.amazon/B02NbDxp3",
  suppliedLink3: "https://link.amazon/B00hJ57DV",
  unknownCodeControl: "https://link.amazon/B00TEST12",
};

/* ---- Product catalog (verified from official Amazon product pages) ---- */
/* BEGIN GENERATED: products */
const PRODUCTS = [
  {
    id: "p01",
    shortLink: "https://link.amazon/B04G1MEwY",
    shortCode: "B04G1MEwY",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B04G1MEwY",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    resolvesToAsin: "B0CDY277D3",
    resolvesToUrl: "https://www.amazon.com/dp/B0CDY277D3",
    brand: "CHEFMAN",
    title: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black",
    category: "Home & Kitchen",
    categoryPath: "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    identityStatus: "OBSERVED",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon.com product page for the destination this link resolves to (B0CDY277D3)",
    flags: ["F-01", "F-02", "F-04", "F-06", "F-20", "F-21", "F-22", "F-23", "F-24"],
  },
  {
    id: "p02",
    shortLink: "https://link.amazon/B02NbDxp3",
    shortCode: "B02NbDxp3",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B02NbDxp3",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    resolvesToAsin: "B09B7SB46R",
    resolvesToUrl: "https://www.amazon.com/dp/B09B7SB46R",
    brand: "Emeril Lagasse",
    title: "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.",
    category: "Home & Kitchen",
    categoryPath: "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    identityStatus: "OBSERVED",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon.com product page for the destination this link resolves to (B09B7SB46R)",
    flags: ["F-01", "F-02", "F-04", "F-06", "F-20", "F-21", "F-22", "F-23", "F-24"],
  },
  {
    id: "p03",
    shortLink: "https://link.amazon/B00hJ57DV",
    shortCode: "B00hJ57DV",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B00hJ57DV",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    resolvesToAsin: "B08DKYBTPH",
    resolvesToUrl: "https://www.amazon.com/dp/B08DKYBTPH",
    brand: "Chefman",
    title: "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel",
    category: "Home & Kitchen",
    categoryPath: "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    identityStatus: "OBSERVED",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon.com product page for the destination this link resolves to (B08DKYBTPH)",
    flags: ["F-01", "F-02", "F-04", "F-06", "F-20", "F-21", "F-22", "F-23", "F-24"],
  },
];
/* END GENERATED: products */

/* ---- Verified specification rows (official Amazon + manufacturer pages) ----
 * Integrated from the combined session verification; manufacturer pages
 * re-fetched and confirmed during final integration (2026-11-13). */
/* BEGIN GENERATED: specs */
const SPECS = [
  // p01 — CHEFMAN B0CDY277D3 (resolved from B04G1MEwY)
  {
    pid: "p01",
    attribute: "Model number",
    value: "RJ38-SQPF-3TDB-2W",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page — Specifications",
    sourceIds: ["S25"],
  },
  {
    pid: "p01",
    attribute: "Capacity",
    value: "6 Qt / 5.67 L (two independent 3-qt baskets)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page (6 Qt / 5.67 L); Amazon listing ('combined 6-quart large air fryer capacity', 'individual 3-quart large capacity air fryer double baskets')",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Temperature range",
    value: "200–450 °F / 95–235 °C",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page ('200–450°F / 95º-235ºC'); Amazon listing ('Digital air fryer dual basket temperature settings from 200-450°F'; product-information block Max Temperature Setting 450 °F)",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Power",
    value: "1700 W / 120 V",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page ('Power: 1700W/120V'); Amazon listing ('120 Volts/1700 Watts')",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Dimensions",
    value: "13.38 × 11.81 × 10.63 in (33.98 × 30 × 27 cm)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page; Amazon product-information block ('13.38\"D x 11.81\"W x 10.63\"H')",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Weight",
    value: "13.3 lb / 6.03 kg",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page ('Weight: 13.3 lbs / 6.03 kg'); Amazon product-information block ('Item Weight: 13.3 pounds')",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Controls",
    value: "Digital touch control with touchscreen presets",
    status: "verified",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon product-information block ('Control Method: Touch', 'Controller Type: Touch control') and listing bullet ('with touchscreen presets')",
    sourceIds: ["S19"],
  },
  {
    pid: "p01",
    attribute: "Special features",
    value: "+ 2Min button, automatic shut-off, dual-zone features, Hi-Fry, mute; Sync Finish; interior light; dual viewing windows; matte-black finish",
    status: "verified",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon product-information block ('Special Features'); Chefman official product page (Features list)",
    sourceIds: ["S19", "S25"],
  },
  {
    pid: "p01",
    attribute: "Material",
    value: "Metal, plastic; inner material plastic with non-stick coating",
    status: "verified",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon product-information block (Materials & Care)",
    sourceIds: ["S19"],
  },
  {
    pid: "p01",
    attribute: "Certification and warranty",
    value: "cETL approved with a 1-year Chefman assurance",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-dual-window-air-fryer",
    sourceLabel: "Chefman official product page; Amazon listing bullet ('cETL approved … 1-year assurance provided by Chefman')",
    sourceIds: ["S25", "S19"],
  },
  {
    pid: "p01",
    attribute: "Colour",
    value: "Black, gray",
    status: "verified",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon product-information block (Additional details)",
    sourceIds: ["S19"],
  },
  {
    pid: "p01",
    attribute: "UPC",
    value: "",
    status: "unverified",
    source: "",
    sourceLabel: "The Amazon Item details block for this ASIN was not captured in this verification pass; no UPC is stated, so none is published.",
    sourceIds: [],
  },
  // p02 — Emeril Lagasse B09B7SB46R (resolved from B02NbDxp3)
  {
    pid: "p02",
    attribute: "Model number",
    value: "CONFLICT — Amazon listing: 4-00675-02X-VN (Model Number and Part Number); Emeril Everyday store: 4-00675-02A-VN",
    status: "conflict",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon Item details block; Emeril Everyday official store product page",
    sourceIds: ["S20", "S27"],
  },
  {
    pid: "p02",
    attribute: "Capacity",
    value: "26 qt / 24.6 L (sized for 4–6 people)",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store ('26-Quart Capacity', '24.6 Liters Capacity'); Amazon product-information block ('Capacity: 24.6 liters')",
    sourceIds: ["S27", "S20"],
  },
  {
    pid: "p02",
    attribute: "Power",
    value: "1700 watts / 120 volts",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon product-information block ('Output Wattage: 1700 watts', 'Wattage: 1700 watts', 'Voltage: 120 volts')",
    sourceIds: ["S20"],
  },
  {
    pid: "p02",
    attribute: "Temperature settings",
    value: "Minimum 75 °F, maximum 500 °F",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon product-information block ('Min Temperature Setting: 75 °F', 'Max Temperature Setting: 500 °F')",
    sourceIds: ["S20"],
  },
  {
    pid: "p02",
    attribute: "Dimensions",
    value: "16.9\"D × 15.8\"W × 14.8\"H",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store ('16.9\"D x 15.8\"W x 14.8\"H'); Amazon product-information block (Measurements)",
    sourceIds: ["S27", "S20"],
  },
  {
    pid: "p02",
    attribute: "Controls",
    value: "Touch / touchscreen",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon product-information block ('Control Method: Touch', 'Controller Type: Touchscreen')",
    sourceIds: ["S20"],
  },
  {
    pid: "p02",
    attribute: "Cooking functions / presets",
    value: "CONFLICT — Amazon listing title: '24 cooking functions'; Emeril Everyday description: '24 one-touch cooking presets'; Emeril Everyday specification tile: '25 Cooking Pre-sets'; Emeril Everyday feature block headed '10-In-1 Versatility' lists ten functions (Air Fry, Bake, Broil, Defrost, Dehydrate, Grill, Proof, Reheat, Roast, Warm)",
    status: "conflict",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon listing title; Emeril Everyday official store (description, specification tile and '10-In-1 Versatility' feature block) — the manufacturer's own page disagrees with itself (flag F-19)",
    sourceIds: ["S20", "S27"],
  },
  {
    pid: "p02",
    attribute: "Door style",
    value: "Dual French doors",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store ('French doors offer effortless access'); Amazon listing title ('with French doors')",
    sourceIds: ["S27", "S20"],
  },
  {
    pid: "p02",
    attribute: "Included accessories",
    value: "7 premium accessories — air fry basket, rotisserie spit, bake pan and more; Amazon lists Rack, Bake Pan, Drip Tray, Crisper Basket, Rotisserie Spit, Fetch Tool",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store ('Included are 7 premium accessories … air fry basket, rotisserie spit, bake pan, and more'); Amazon Item details ('Configuration: Air Fryer Toaster Oven Combo with 24 Functions and 7 Accessories', 'Included Components')",
    sourceIds: ["S27", "S20"],
  },
  {
    pid: "p02",
    attribute: "Special features",
    value: "Dual-speed fan, rotisserie, 360° hot-air circulation, temperature control",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store (Specifications tiles and Key Features)",
    sourceIds: ["S27"],
  },
  {
    pid: "p02",
    attribute: "Warranty",
    value: "1 year",
    status: "verified",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceLabel: "Emeril Everyday official store ('1-Years Warranty')",
    sourceIds: ["S27"],
  },
  {
    pid: "p02",
    attribute: "UPC",
    value: "752356835682",
    status: "verified",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon Item details block ('UPC: 752356835682')",
    sourceIds: ["S20"],
  },
  {
    pid: "p02",
    attribute: "Item weight",
    value: "",
    status: "unverified",
    source: "",
    sourceLabel: "Neither the Amazon product-information block nor the Emeril Everyday page states an item weight for this product; none is published.",
    sourceIds: [],
  },
  // p03 — Chefman B08DKYBTPH (resolved from B00hJ57DV)
  {
    pid: "p03",
    attribute: "Model number",
    value: "RJ38-SQSS-8T",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('Model Number: RJ38-SQSS-8T (8 Qt model)'); Amazon Item details ('Part Number: RJ38-SQSS-8T')",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Capacity",
    value: "8 Qt / 7.57 L",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('Capacity: 5 Qt or 8 Qt / 4.73 L or 7.57 L'); Amazon product-information block ('Capacity: 8 quarts')",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Temperature range",
    value: "200–400 °F / 95–205 °C (maximum 400 °F)",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('200–400°F / 95º-205ºC', 'Max temp: 400ºF/ 205ºC'); Amazon listing bullet ('a temperature range from 200-400°F') and product-information block ('Max Temperature Setting: 400 °F'). NOTE: the Amazon listing TITLE says '450°F Hi-Fry Option' — contradicted by the same page's own bullet list and specification block and by Chefman. See flag F-22; do not publish 450 °F for this model.",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Power",
    value: "CONFLICT — Amazon listing bullet ('About this item'): '1000 Watts/120 Volts – RJ38-SQSS-8T'; Amazon product-information block: 'Wattage: 1700 watts', 'Voltage: 120 volts'; Chefman official product page: 'Power: 1700W/120V'",
    status: "conflict",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon listing bullet list; Amazon product-information block; Chefman official product page — the disagreement is inside the Amazon listing itself",
    sourceIds: ["S21", "S26"],
  },
  {
    pid: "p03",
    attribute: "Dimensions",
    value: "CONFLICT — Chefman: 15.4 × 12.6 × 13.5 in (39.11 × 32 × 34.29 cm); Amazon product-information block: 12.75\"D × 13.5\"W × 10\"H",
    status: "conflict",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page; Amazon product-information block (Measurements)",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Weight",
    value: "12.8 lb / 5.8 kg",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('Weight: (8 Qt Model) 12.8 lbs / 5.8 kg'); Amazon product-information block ('Item Weight: 12.8 pounds')",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Presets",
    value: "4 — French fries, chicken, meat, fish",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('4 cooking presets'; description lists fries, chicken, fish, meat); Amazon listing bullet ('Four presets … French fries, chicken, meat, and fish')",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "Controls",
    value: "Touch",
    status: "verified",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon product-information block ('Control Method: Touch', 'Controller Type: Touch')",
    sourceIds: ["S21"],
  },
  {
    pid: "p03",
    attribute: "Special features",
    value: "Automatic shut-off, LED shake reminder, programmable",
    status: "verified",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon product-information block ('Special Features')",
    sourceIds: ["S21"],
  },
  {
    pid: "p03",
    attribute: "Material",
    value: "Plastic, stainless steel; inner material stainless steel",
    status: "verified",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon product-information block (Materials & Care)",
    sourceIds: ["S21"],
  },
  {
    pid: "p03",
    attribute: "Certification and warranty",
    value: "cETL approved; 1-year warranty (Amazon: '1-Year Limited Warranty')",
    status: "verified",
    source: "https://chefman.com/products/turbofry-touch-air-fryer-1",
    sourceLabel: "Chefman official product page ('cETL approved with a 1-year Chefman® assurance'); Amazon Item details ('Warranty Description: 1-Year Limited Warranty')",
    sourceIds: ["S26", "S21"],
  },
  {
    pid: "p03",
    attribute: "UPC",
    value: "816458024518",
    status: "verified",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon Item details block ('UPC: 816458024518')",
    sourceIds: ["S21"],
  },
];
/* END GENERATED: specs */

/* ---- Resolution evidence & controls (generated from ledger/products.json) ---- */
/* BEGIN GENERATED: resolution-evidence */
const RESOLUTION_EVIDENCE = [
  {
    id: "E-01",
    observation: "GET https://link.amazon/B04G1MEwY ended at https://www.amazon.com/dp/B0CDY277D3?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-...&channelId=704&plpRedirect=mhFallback (page title observed: CHEFMAN 6 Quart Dual Basket Air Fryer Oven ...)",
    interpretation: "The destination is a specific product and it is stable for this token — but three different tokens landing on three different products is NOT by itself evidence of a mapping. The decisive control is E-06.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceIds: ["S19"],
  },
  {
    id: "E-02",
    observation: "GET https://link.amazon/B02NbDxp3 ended at https://www.amazon.com/dp/B09B7SB46R?...plpRedirect=mhFallback (page title observed: Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven ...)",
    interpretation: "Second distinct destination, second distinct per-link btn_ref token (srctok-534f5e7952f396b2 at the time of that fetch). Distinctness across tokens, not randomness within a token.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceIds: ["S20"],
  },
  {
    id: "E-03",
    observation: "GET https://link.amazon/B00hJ57DV ended at https://www.amazon.com/dp/B08DKYBTPH?...plpRedirect=mhFallback (page title observed: Chefman Air Fryer 8 Qt | TurboFry 4-in-1 ...)",
    interpretation: "Third distinct destination, third distinct per-link btn_ref token (srctok-76c3adaeb8708b44 at the time of that fetch).",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceIds: ["S21"],
  },
  {
    id: "E-04",
    observation: "https://www.amazon.com/dp/B04G1MEwY , https://www.amazon.com/dp/B02NbDxp3 and https://www.amazon.com/dp/B00hJ57DV each returned Amazon's \"Sorry! We couldn't find that page\" error page on 2026-11-13 and again on 2026-11-14.",
    interpretation: "No catalog record exists for any of the three tokens as given.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S17", "S18"],
  },
  {
    id: "E-05",
    observation: "Each token was measured against the ASIN identifier definition (10 characters): B04G1MEwY=9, B02NbDxp3=9, B00hJ57DV=9. Each is alphanumeric, so only the length fails.",
    interpretation: "Pattern is consistent with a one-character truncation, but the missing character is not recoverable and was NOT guessed.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S17", "S18"],
  },
  {
    id: "E-06",
    observation: "CONTROL — an unknown code on the same short-link service: GET https://link.amazon/B00TEST12 (9 characters, never supplied) resolved to https://amzlinks.in/B00TEST12 and returned the service's 404 page — \"404: File Not Found … You've clicked on an invalid URL.\" (image host: amzlinks.in/post-tap/short-link-404.png).",
    interpretation: "DECISIVE. The service looks the code up: an unknown code returns a 404 instead of an arbitrary product. The three supplied codes therefore ARE honoured lookups, and the earlier reading that the token was ignored and the destination arbitrary (flag F-03) is falsified. What is still unconfirmed is the *contract* — Amazon publishes no document binding a link.amazon code to a product — not the behaviour.",
    status: "OBSERVED",
    source: "https://link.amazon/B00TEST12",
    sourceIds: ["S28", "S19", "S20", "S21"],
  },
  {
    id: "E-07",
    observation: "CONTROL — a bare, untagged GET https://www.amazon.com/dp/B08DKYBTPH (a valid 10-character ASIN) returned the CHEFMAN 8 Qt product page with ?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 appended to Amazon's own internal links, and with no btn_ref parameter at all.",
    interpretation: "plpRedirect=mhFallback is emitted on ordinary, direct, valid product-page loads. It is therefore NOT evidence of a fallback and cannot distinguish a valid ASIN from an invalid token.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceIds: ["S21"],
  },
  {
    id: "E-08",
    observation: "The three supplied links each carry their own btn_ref=srctok-… source token and the same channelId=704: B04G1MEwY → srctok-1f979f303a4b5691, B02NbDxp3 → srctok-0cd8be3c7e2e0de3, B00hJ57DV → srctok-7c59360cbbbd59b7 (observed 2026-11-14 ~10:05 UTC).",
    interpretation: "Three distinct per-link source tokens — the signature of individually tracked links, not of a shared fallback.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceIds: ["S19", "S20", "S21"],
  },
  {
    id: "E-09",
    observation: "Cross-time check on one link: link.amazon/B04G1MEwY carried btn_ref=srctok-1e229870efde5acf earlier on 2026-11-14 (recorded by session c6e94e8d) and btn_ref=srctok-1f979f303a4b5691 at ~10:04 UTC on the same day, while the destination stayed /dp/B0CDY277D3 on every fetch.",
    interpretation: "The btn_ref source token rotates over time; the DESTINATION does not. Two earlier claims are therefore both wrong in different ways: 'a different btn_ref on re-fetch proves the destination shuffles' (F-05, F-12) and 'an identical btn_ref proves the token is permanent' (revalidation C-2). See flag F-21.",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceIds: ["S19"],
  },
  {
    id: "E-10",
    observation: "None of the three resolved URLs carries a tag= parameter. Each ends …&channelId=704&plpRedirect=mhFallback (short-link arrival) or …?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 (direct arrival).",
    interpretation: "The links as supplied are untagged, so they cannot attribute a sale to an Associates account. Amazon's own help page gives the qualifying Special Link format as http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID. See flag F-24.",
    status: "OBSERVED",
    source: "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC",
    sourceIds: ["S24", "S19", "S20", "S21"],
  },
];
/* END GENERATED: resolution-evidence */

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
    label: "What each supplied link resolves to (observed 2026-11-14)",
    value:
      "Each of the three supplied link.amazon URLs resolves to exactly one Amazon product page — B0CDY277D3, B09B7SB46R and B08DKYBTPH — reproducibly. An unknown 9-character code on the same service returns a 404 instead of a product, so the codes are honoured lookups, not ignored tokens.",
    source: ASIN_SOURCE.unknownCodeControl,
  },
  {
    label: "Identity of the supplied codes",
    value:
      "Each supplied code is 9 characters. Amazon's own help page states that an ASIN is the 10-digit code Amazon uses to denote specific products, so the codes are valid short-link tokens but not ASINs.",
    source: ASIN_SOURCE.linkFormat,
  },
  {
    label: "Qualifying Special Link format (official)",
    value:
      "http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID — the tag identifies the Associates account the sale is tracked to. None of the three supplied links carries a tag.",
    source: ASIN_SOURCE.linkFormat,
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
    finding: "All three supplied links resolve to air fryers / air fryer ovens",
    detail:
      "The destinations span a 6-quart dual-basket air fryer oven (Chefman), a 26-quart French-door air fryer toaster oven (Emeril Lagasse) and an 8-quart TurboFry air fryer (Chefman). This is a statement about the destinations the links resolve to, which are verified; it is not a claim that these are the items the brief intended (see F-03).",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    status: "verified",
  },
  {
    item: "Supplied-code identity",
    finding: "Unverified — the codes are not ASINs and Amazon documents no code-to-product contract",
    detail:
      "Each supplied code is 9 characters (an ASIN is 10) and amazon.com/dp/<code> is Amazon's Page Not Found page. The destination of each link is an observation (F-20); the code-to-product binding is not documented by any public Amazon source, so the brief mapping stays unconfirmed (F-03).",
    source: ASIN_SOURCE.linkFormat,
    status: "unverified",
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

/* ---- Marketing content plan (AI-generated content outputs) ----
 * Status semantics (T23): a draft may only be published for an entry whose identity is
 * established. The three supplied codes resolve to known products (F-20), but no public Amazon
 * document binds a code to a product (F-03), so the generator is held for these entries and the
 * rows below are marked Blocked rather than Ready. */
const CONTENT_ROWS = [
  {
    content: "Product review article",
    target: "CHEFMAN 6 Quart Dual Basket Air Fryer Oven (B0CDY277D3)",
    format: "SEO-optimized long-form review",
    status: "Blocked",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    content: "Product review article",
    target: "Emeril Lagasse 26QT French Door Air Fryer Toaster Oven (B09B7SB46R)",
    format: "SEO-optimized long-form review",
    status: "Blocked",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    content: "Product review article",
    target: "Chefman Air Fryer 8 Qt TurboFry 4-in-1 (B08DKYBTPH)",
    format: "SEO-optimized long-form review",
    status: "Blocked",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
  {
    content: "Comparison guide",
    target: "Chefman 6 Qt Dual Basket vs Chefman 8 Qt TurboFry",
    format: "Side-by-side comparison article",
    status: "Blocked",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    content: "Comparison guide",
    target: "Compact vs large-capacity air fryer ovens (6 Qt vs 26 QT)",
    format: "Buying-guide comparison article",
    status: "Blocked",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    content: "Buying guide",
    target: "“Best air fryer for family meals” buying guide",
    format: "SEO buying guide with Special Link integration",
    status: "Blocked",
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
/* BEGIN GENERATED: flags */
const FLAGGED_ROWS = [
  {
    item: "F-01 — Submitted tokens are not valid ASINs",
    detail: "B04G1MEwY, B02NbDxp3 and B00hJ57DV are each 9 characters. The ASIN identifier is 10 characters, so none of the three can address a catalog record as written. Each is alphanumeric, so only the length fails - consistent with a truncation, but the missing character is not recoverable and was not guessed.",
    severity: "high",
    impact: "Product identity, and every dependent field (title, brand, category, price, rating, commission band, competition), is unavailable.",
    actionRequired: "Re-supply the full 10-character ASIN or the complete amazon.<tld>/dp/<ASIN> URL for each item.",
    ledgerFlag: "F-01",
    ledgerUrl: "pages/flags.html#F-01",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S17", "S18"],
  },
  {
    item: "F-02 — Canonical product pages return Page Not Found",
    detail: "https://www.amazon.com/dp/B04G1MEwY , /dp/B02NbDxp3 and /dp/B00hJ57DV each returned Amazon's \"Sorry! We couldn't find that page\" error page when fetched on 2026-11-13.",
    severity: "high",
    impact: "Confirms the tokens do not exist in the catalog rather than merely being unresolvable from this network.",
    actionRequired: "None - evidence record. Re-verify if the ASINs are ever corrected.",
    ledgerFlag: "F-02",
    ledgerUrl: "pages/flags.html#F-02",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S17", "S18"],
  },
  {
    item: "F-03 — The three link.amazon codes are honoured lookups, but no Amazon document binds a code to a product",
    detail: "FINAL READING (2026-11-14, session 4338f55e; supersedes the withdrawn 'arbitrary fallback' wording and the 'permanent per-link token' wording). What is verified: (a) each of the three supplied link.amazon URLs resolves, reproducibly, to ONE specific Amazon product page — B0CDY277D3, B09B7SB46R, B08DKYBTPH; (b) an UNKNOWN code on the same service (https://link.amazon/B00TEST12) returns a 404 page ('You've clicked on an invalid URL'), so the service looks the code up and the token IS honoured — the earlier claim that the token was ignored and the destination arbitrary is falsified; (c) plpRedirect=mhFallback is also emitted on ordinary valid /dp/ loads and so is not evidence of a fallback; (d) each link carries its own btn_ref=srctok-… token, which rotates over time while the destination does not. What is NOT verified: no public Amazon document describes the link.amazon/<code> format or binds a code to a product ASIN, so the binding is established by observed behaviour, not by documentation.",
    severity: "medium",
    impact: "The three products can be named and marketed as the destinations the supplied links resolve to, which is what this site now publishes. They cannot be claimed as 'the products named in the brief' until the owner confirms the mapping in Associates Central.",
    actionRequired: "Owner: confirm in Associates Central that these three destinations are the items to market, and supply links carrying the Associates tag (F-24).",
    ledgerFlag: "F-03",
    ledgerUrl: "pages/flags.html#F-03",
    source: "https://link.amazon/B00TEST12",
    sourceIds: ["S28", "S19", "S20", "S21", "S24"],
  },
  {
    item: "F-04 — link.amazon is not the documented public Associates short-link domain",
    detail: "The domain does resolve (it is served from Amazon CloudFront ranges), but it is not the public program's documented short-link domain used for Associates links; the public canonical product form is amazon.<tld>/dp/<ASIN> and program tooling provides its own link formats (S09). No Amazon help page surfaced in this review documents `link.amazon/<token>` as a publisher-facing link format.",
    severity: "medium",
    impact: "Links of this shape cannot be relied on for tagging or attribution, and an untagged link earns nothing.",
    actionRequired: "Generate links from SiteStripe or the API in the tagged format required by the Participation Requirements (R-07).",
    ledgerFlag: "F-04",
    ledgerUrl: "pages/flags.html#F-04",
    source: "https://affiliate-program.amazon.com/help/operating/policies",
    sourceIds: ["S02", "S09"],
  },
  {
    item: "F-05 — PA-API 5.0 is deprecated - the plan and most public tooling write-ups are stale",
    detail: "Amazon's legacy PA-API documentation URL now serves a deprecation notice: PA-API 5 calls return HTTP 403 with AccessDenied and instruct integrators to migrate to the Creators API. Amazon's own public Associates tools page (referenced in the site's source list) still describes the Product Advertising API as the programmatic option.",
    severity: "medium",
    impact: "Any collector, tutorial, or dependency built against PA-API 5 will fail at runtime, not at build time. Architecture here targets the Creators API and degrades to a BLOCKED status rather than scraping.",
    actionRequired: "Register for Creators API access in Associates Central when the account exists (prerequisite: >=10 qualifying sales in the past 30 days, per Amazon's docs).",
    ledgerFlag: "F-05",
    ledgerUrl: "pages/flags.html#F-05",
    source: "https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation",
    sourceIds: ["S06", "S07", "S09"],
  },
  {
    item: "F-06 — Published copy must be labelled 'the product this link resolves to' until the owner confirms the mapping",
    detail: "Because no public Amazon document binds a link.amazon code to a product, the three products this site publishes are the destinations the supplied links resolve to — verified by live fetch and by the unknown-code control (F-20) — not a confirmed brief mapping. The article, comparison and buying-guide generator therefore stays in preview for the three submitted tokens: draft copy exists in content/templates/** but is not published, so that no article asserts a mapping Amazon does not document.",
    severity: "high",
    impact: "No published article, comparison or buying guide names these three products yet. Every other part of the platform (policy engine, rate data, scoring, tracking schema, templates, deploy) is delivered and gated.",
    actionRequired: "Confirm the mapping and supply tagged links; the pipeline then publishes verified-only copy without any other change.",
    ledgerFlag: "F-06",
    ledgerUrl: "pages/flags.html#F-06",
    source: "https://link.amazon/B00TEST12",
    sourceIds: ["S28", "S19", "S20", "S21"],
  },
  {
    item: "F-07 — No Associates account, marketplace, tracking ID, or tag supplied",
    detail: "The brief did not include an Associates ID/tag, target marketplace, or category access. Commission eligibility and reporting are account- and marketplace-specific, so no account-level figure can be verified or attributed.",
    severity: "medium",
    impact: "Link builder runs in inert preview mode; earnings/conversion columns stay blank; the disclosure statement is still shown because it is required of every participant.",
    actionRequired: "Provide Associates ID + marketplace if live linking is wanted.",
    ledgerFlag: "F-07",
    ledgerUrl: "pages/flags.html#F-07",
    source: "https://affiliate-program.amazon.com/help/operating/agreement",
    sourceIds: ["S01", "S02"],
  },
  {
    item: "F-08 — No click, conversion, or earnings history exists",
    detail: "Nothing in the brief supplied a report export. Clicks are site-side and measurable after launch; conversion and earnings must come from Associates reporting under the Session definition (R-13).",
    severity: "medium",
    impact: "All performance tables render as empty states with the ingestion contract documented, rather than illustrative numbers.",
    actionRequired: "Ingest a dated Associates report (or wire the earnings export) to activate the optimizer.",
    ledgerFlag: "F-08",
    ledgerUrl: "pages/flags.html#F-08",
    source: "https://affiliate-program.amazon.com/help/operating/policies",
    sourceIds: ["S02"],
  },
  {
    item: "F-09 — Sandbox network allowlist limits live verification",
    detail: "The build environment may reach github.com, api.github.com, codeload.github.com, registry.npmjs.org and files.pythonhosted.org. Direct HTTPS to Amazon from that sandbox fails at TLS (curl SSL_ERROR_SYSCALL), so page evidence in this review was captured through the agent's fetch path and recorded with the final URL observed. Reproducing by hand needs only a browser.",
    severity: "low",
    impact: "Documented for auditability; does not change any conclusion.",
    actionRequired: "None.",
    ledgerFlag: "F-09",
    ledgerUrl: "pages/flags.html#F-09",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S19"],
  },
  {
    item: "F-10 — Repo review: prior merged site is honest but incomplete, and its citations predate these checks",
    detail: "Reviewed commit cfc04b1 (from arena/6b8bb130-zone2, merged via PR #1). Its three product rows are correctly blank/\"Unverified\" and all four of its cited reference URLs were re-fetched here and confirmed live and on-topic. Gaps: it links the deprecated PA-API overview without the deprecation notice, cites no commission rate table, no attribution window, no per-row official source, and has no category subpages.",
    severity: "low",
    impact: "Nothing published by that commit is wrong; the expansion here supplies what was missing. Its landing page, data.js rows and Pages workflow are preserved.",
    actionRequired: "Review the added pages; nothing from the merged commit was deleted.",
    ledgerFlag: "F-10",
    ledgerUrl: "pages/flags.html#F-10",
    source: "https://affiliate-program.amazon.com/help/operating/agreement",
    sourceIds: ["S01", "S02", "S04", "S06"],
  },
  {
    item: "F-11 — Policy pages carry different update dates and can change without notice",
    detail: "The Operating Agreement page states \"Updated: October 15, 2025\"; the Program Policies page states \"Updated: April 14, 2026\". Rates, Session mechanics and disclosure wording are all governed by pages Amazon may revise at any time, and the Agreement requires compliance with the most up-to-date version of the Program Policies.",
    severity: "low",
    impact: "Compliance data in this repository is timestamped and re-checked by the build; treat as a snapshot, not a subscription.",
    actionRequired: "Re-run tools/build_site.py --refresh before each publishing cycle.",
    ledgerFlag: "F-11",
    ledgerUrl: "pages/flags.html#F-11",
    source: "https://affiliate-program.amazon.com/help/operating/agreement",
    sourceIds: ["S01", "S02"],
  },
  {
    item: "F-12 — WITHDRAWN - the 'shuffled fallback' reproducibility claim did not reproduce",
    detail: "This row asserted that a same-day re-fetch of link.amazon/B04G1MEwY returned a different page body (a 'Best Sellers in Kitchen & Dining' carousel) and a different btn_ref token, and concluded the destination could not identify a product. On re-test (session c6e94e8d, reproduced by this session on 2026-11-14) repeated fetches returned the SAME ASIN path, the SAME btn_ref=srctok-1e229870efde5acf and the same product detail page. The observation did not reproduce and the inference drawn from it did not hold. Kept in the register rather than deleted, because deleting a published correction would hide that the site carried an unsupported claim between 2026-11-13 and 2026-11-14.",
    severity: "low",
    impact: "No live harm: the value affected nothing that was published as fact. The withdrawal matters because the claim was used to justify calling the destinations 'arbitrary'.",
    actionRequired: "None - withdrawn. The stable-destination finding in F-03 replaces it.",
    ledgerFlag: "F-12",
    ledgerUrl: "pages/flags.html#F-12",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceIds: ["S16", "S19"],
  },
  {
    item: "F-13 — Review note: one merged page title leads with an Amazon mark",
    detail: "compliance.html is titled 'Amazon rules this site complies with'. The Participation Requirements prohibit an Amazon mark in a domain name, subdomain, tag/Associates ID, or social identifier - a page title is none of those, and descriptive reference plus the mandated disclosure sentence are permitted. Flagged only because a title that opens with the mark can read as an official Amazon property, and Section 5 forbids implying endorsement or affiliation. Recorded as a build warning, not a failure.",
    severity: "low",
    impact: "No functional impact; low-risk naming judgement call for the owner.",
    actionRequired: "Optional: reword the title (e.g. 'Program rules this site complies with').",
    ledgerFlag: "F-13",
    ledgerUrl: "pages/flags.html#F-13",
    source: "https://affiliate-program.amazon.com/help/operating/agreement",
    sourceIds: ["S01", "S02"],
  },
  {
    item: "F-14 — Duplicate of the prototype dashboard at northstar/ (disclosure gap since closed)",
    detail: "Commit 4bea98e added northstar/index.html, app.js, data.js and styles.css - a near-copy of the original Northstar dashboard - and the root files it was copied from were later removed, so the copy is now the only instance of that view. When measured against 9b8830d its served HTML carried no disclosure sentence (grep -c 'As an Amazon Associate' northstar/index.html -> 0). Re-measured on the merged tree after PR #3: the copy now carries the disclosure strip (count 1), so that gap is closed. Remaining point is structural: the primary site's footer links to northstar/index.html, so the duplicate is a live companion view rather than dead weight, and its content now drifts from the primary site's.",
    severity: "low",
    impact: "No compliance issue at measurement time on the merged tree. Two dashboard implementations now evolve independently; a reader following the footer link sees the older prototype with blank product rows.",
    actionRequired: "Optional: fold the prototype into the primary site, or label it explicitly as the earlier prototype in its own page heading so the difference is obvious to a reader.",
    ledgerFlag: "F-14",
    ledgerUrl: "pages/flags.html#F-14",
    source: "https://docs.github.com/en/rest/pages/pages",
    sourceIds: ["S22"],
  },
  {
    item: "F-15 — The hub's own verifier is stale after the namespace move, so its per-row sourcing guard is not running",
    detail: "`python3 research-hub/scripts/verify.py` prints 7 failures on the current tree: it computes its repository root as the script's parent directory (research-hub/), so it looks for research-hub/index.html, app.js, data.js and styles.css - files that now live elsewhere or not at all - and it flags research-hub/start.html's own ../zone2/index.html link as 'escaping the repository'. Its expected-file list also still names the pre-move root layout. The workflow does not invoke this script any more (it runs its own link/asset/data checks), so nothing is blocked and CI is green; but the hub's rows are no longer policed by the guard that was written for them.",
    severity: "medium",
    impact: "No published error. Risk: a future edit to research-hub/data/products.json could add an unsourced 'verified' row and no check would catch it, because the only guard for that namespace is currently mis-pointed.",
    actionRequired: "Owner/reviewer: re-point the verifier's ROOT at the repo root (parents[2]) and update its required-file list to the post-move layout, or fold its per-row rules into the workflow's data checks. Not done here: research-hub/** is another session's scope, so this is recorded as a change request.",
    ledgerFlag: "F-15",
    ledgerUrl: "pages/flags.html#F-15",
    source: "https://docs.github.com/en/rest/pages/pages",
    sourceIds: ["S22"],
  },
  {
    item: "F-16 — Three compliance-control rows cited controls and files that do not exist; one misquoted current policy",
    detail: "Found in a line-by-line re-verification of the repository on 2026-11-14. (1) R-01 cited `site/compliance-inject.js` as the mechanism that renders the required disclosure - no such file exists anywhere in the repository; the disclosure is in fact emitted by the page renderers and enforced by tools/validate_data.py::check_disclosure plus the workflow's disclosure step. (2) R-11 cited `tools/validate_data.py::assert_no_amazon_marks` - no such function exists; the implemented function is `check_marks`. (3) R-02 cited `tools/generate_articles.py::lint_disclosure_proximity` and R-06 cited `::lint_claims` - neither function exists; both rules are enforced inside the single `lint()` function, and R-06's inline evidence marker is `<!--evidence:` (the data.js summary said 'inline evidence reference', which is right in substance but the function name was invented). (4) R-09 stated that email/SMS channels are 'absent from the schema' so a scheduler cannot target them - the current Program Policies expressly PERMIT Special Links in solicited (opt-in) email, SMS and direct messaging, so the rule text was stale against the policy page updated April 14, 2026.",
    severity: "high",
    impact: "The published compliance table claimed control coverage that did not exist for four rows. No fabricated product or price data was involved - this is a control-accuracy defect, not a data-invention defect - but a reader auditing 'is this enforced?' would have been given a wrong file or function name, and R-09 misstated a permission as a prohibition.",
    actionRequired: "Corrected in this session: R-01, R-02, R-06 and R-11 now cite the real functions and files; R-01 and R-11 carry an explicit 'Corrected 2026-11-14' sentence; R-09's requirement text was rewritten to the policy as published (solicited/opt-in only, certification on request) while keeping the repository's stricter no-email/no-SMS channel default as a self-imposed control, labelled as such. Reviewer may still wish to re-read each control against the code.",
    ledgerFlag: "F-16",
    ledgerUrl: "pages/flags.html#F-16",
    source: "https://affiliate-program.amazon.com/help/operating/agreement",
    sourceIds: ["S01", "S02", "S05"],
  },
  {
    item: "F-17 — Root dashboard stated '3 Verified affiliate products' and '11 items flagged' while the ledger states 0 identified",
    detail: "The primary dashboard's KPI strip said '3 / Verified affiliate products' and '11 / Items flagged for review'. The root product page's own heading was 'Product Catalog - verified from official Amazon pages', and the executive-summary paragraph said the products 'are identified and verified'. Meanwhile ledger/products.json marks all three submitted items status=UNVERIFIED with null title/brand/category, ledger/flags.json contains 15 flags (not 11), and F-03/F-12 record that the three destinations are fallback pages, not a mapping of the submitted tokens. Both readings are defensible - the dashboard describes the three *fallback destinations* it verified, the ledger describes the three *submitted tokens* it could not identify - but published side by side without that distinction, they contradict each other.",
    severity: "medium",
    impact: "A reader could conclude the three supplied links had been identified and verified, which the project's own ledger explicitly denies. That is the exact class of overstatement the brief forbids.",
    actionRequired: "Corrected: the KPI now reads '3 / Fallback landing pages verified (0 of 3 submitted codes identified)' with the count computed from FLAGGED_ROWS, and the product page heading and summary paragraph now state the distinction in place. Reviewer action: confirm which of the two readings should be the primary framing.",
    ledgerFlag: "F-17",
    ledgerUrl: "pages/flags.html#F-17",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceIds: ["S19", "S20", "S21"],
  },
  {
    item: "F-18 — CI link check omitted the generated pages/ namespace (fixed in this session)",
    detail: "The workflow step 'Internal links and asset references resolve (all sites)' walks the root pages, research-hub/, northstar/, zone2/ and affiliate-lab/ but never pages/ - the 37 generated findings pages, which are the largest HTML surface in the repository. A broken href there would have reached main. Re-run by hand on 2026-11-14 the pages/ namespace has 0 broken file references and 0 unresolvable anchors, so no live defect was present; the gap was in the gate, not the output.",
    severity: "low",
    impact: "No broken link was published. The risk was that a future edit to pages/ could ship a dead link with all CI green.",
    actionRequired: "Fixed in this session: pages/ added to the link check, and pages/ + affiliate-lab/ added to the disclosure/price gate so both rules now cover every namespace.",
    ledgerFlag: "F-18",
    ledgerUrl: "pages/flags.html#F-18",
    source: "https://docs.github.com/en/rest/pages/pages",
    sourceIds: ["S22"],
  },
  {
    item: "F-19 — Emeril manufacturer page contradicts itself on functions/presets, so the published 'conflict' row named the wrong second source",
    detail: "The published spec row for the Emeril Lagasse 26QT (P-02, 'Cooking functions / presets') reads '24 per Amazon listing title; 25 per the manufacturer's spec tile'. Re-read on 2026-11-14, the manufacturer's own page carries THREE different numbers: the description text says '24 one-touch cooking presets', a specification tile says '25 Cooking Pre-sets', and a feature block headed '10-In-1 Versatility' lists ten functions. The Amazon listing title observed on the same day likewise says '24 cooking functions'. So the disagreement is not Amazon-vs-manufacturer - it is the manufacturer page disagreeing with itself, and no official source fixes the right number. Re-read again on 2026-11-14 by session 4338f55e with the same result: the Emeril Everyday page states '24 one-touch cooking presets' in its description, '25 Cooking Pre-sets' in its specification tile, and a feature block headed '10-In-1 Versatility' listing ten functions, while the Amazon listing title says '24 cooking functions'. The conflict is confirmed and remains unresolved.",
    severity: "medium",
    impact: "The row was not wrong about a conflict existing, but it attributed the conflict to the wrong party, which would mislead a reader trying to resolve it. The value is unconfirmable, so it must stay blank-or-both-values and flagged rather than resolved by inference.",
    actionRequired: "Corrected: the row now shows all four observations with their exact source wording and status=conflict; flag F-19 published. Reviewer action: treat the preset count as unresolved; do not publish a single number in any article.",
    ledgerFlag: "F-19",
    ledgerUrl: "pages/flags.html#F-19",
    source: "https://www.emerileveryday.com/products/emeril_lagasse_french_door_airfryer_360",
    sourceIds: ["S27"],
  },
  {
    item: "F-20 — DECISIVE CONTROL — an unknown link.amazon code returns a 404, so the three supplied codes are honoured lookups",
    detail: "Run 2026-11-14 by session 4338f55e, the control the earlier sessions did not run. GET https://link.amazon/B00TEST12 — a 9-character code that was never supplied — resolved to https://amzlinks.in/B00TEST12 and returned the short-link service's 404 page: '404: File Not Found … You've clicked on an invalid URL.' (the page's image is hosted at amzlinks.in/post-tap/short-link-404.png). The three supplied codes do not behave that way: each resolves to one specific Amazon product page, reproducibly, across fetches on 2026-11-13 and 2026-11-14. A service that answered unknown codes with a random product would be a fallback; a service that answers unknown codes with a 404 is performing a lookup. Therefore the published reading that the token was 'ignored' and the destination 'arbitrary' is falsified.",
    severity: "medium",
    impact: "This is the single finding that decides the disagreement between five earlier sessions. It moves the three products from 'evidence only' to 'the observed, reproducible destination of each supplied link' — while leaving the documentation gap (F-04, F-03) exactly as it was.",
    actionRequired: "None for the owner to unblock. Recorded so the reviewer can see the control and repeat it: open https://link.amazon/B00TEST12 in a browser.",
    ledgerFlag: "F-20",
    ledgerUrl: "pages/flags.html#F-20",
    source: "https://link.amazon/B00TEST12",
    sourceIds: ["S28", "S19", "S20", "S21"],
  },
  {
    item: "F-21 — The btn_ref source token rotates over time; the destination does not",
    detail: "Measured 2026-11-14 by session 4338f55e. link.amazon/B04G1MEwY carried btn_ref=srctok-1e229870efde5acf earlier the same day (recorded by session c6e94e8d) and btn_ref=srctok-1f979f303a4b5691 at about 10:04 UTC, while the destination stayed /dp/B0CDY277D3 on every fetch. A direct, untagged load of /dp/B08DKYBTPH carries no btn_ref at all. The three supplied links' tokens are distinct from one another (1f979f303a4b5691 / 0cd8be3c7e2e0de3 / 7c59360cbbbd59b7) and all three carry channelId=704.",
    severity: "low",
    impact: "Two published statements were each half-wrong: 'a different btn_ref on re-fetch proves the destination shuffles' (F-05, F-12 — withdrawn) and 'an identical btn_ref proves the token is permanent' (revalidation C-2 — overstated). The correct statement is that the source token is per-link and time-scoped, and the destination is stable. Anyone auditing this repository by re-fetching a link tomorrow should expect a different srctok and the same product.",
    actionRequired: "None — published so the wording is not misread as a guarantee of permanence in either direction.",
    ledgerFlag: "F-21",
    ledgerUrl: "pages/flags.html#F-21",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceIds: ["S19", "S20", "S21"],
  },
  {
    item: "F-22 — The Amazon title for B08DKYBTPH says '450°F Hi-Fry', but that same page's bullet list and specification block — and the manufacturer — say 200–400 °F",
    detail: "Verified 2026-11-14. The Amazon listing title for B08DKYBTPH reads 'Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results'. On the same page the 'About this item' bullet says 'a temperature range from 200-400°F' and the Product information block gives 'Min Temperature Setting: 94 °C' and 'Max Temperature Setting: 400 °F'. Chefman's own page for model RJ38-SQSS-8T states '200–400°F / 95º-205ºC' and 'Max temp: 400ºF/ 205ºC'. The Hi-Fry name and the 450 °F figure belong to the 6-quart dual-window model RJ38-SQPF-3TDB-2W, whose Chefman page states 'Max temp: 450ºF/ 235ºC with Hi-Fry function'.",
    severity: "medium",
    impact: "Repeating '450 °F' in an article or comparison for the 8-quart model would repeat a claim the product's own specification block contradicts. 450 °F is publishable only for the 6-quart dual-window model.",
    actionRequired: "Copy rule published: no 450 °F claim for the 8-quart model. Owner action: none required.",
    ledgerFlag: "F-22",
    ledgerUrl: "pages/flags.html#F-22",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceIds: ["S21", "S26", "S25"],
  },
  {
    item: "F-23 — Emeril model number differs between the Amazon listing and the manufacturer's own store",
    detail: "Verified 2026-11-14. Amazon's Item details for B09B7SB46R give 'Model Number: 4-00675-02X-VN' and 'Part Number: 4-00675-02X-VN'. The Emeril Everyday official store page for the same product prints '4-00675-02A-VN'. Both are official pages for the same listing, and both suffix values appear in the manufacturer's own image filenames ('..._4-00675-02X_...' and '..._4-00675-02A-VN').",
    severity: "medium",
    impact: "A single model number cannot be published for this product. Both values are shown side by side with their sources; neither is chosen.",
    actionRequired: "None — both values published with sources.",
    ledgerFlag: "F-23",
    ledgerUrl: "pages/flags.html#F-23",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceIds: ["S20", "S27"],
  },
  {
    item: "F-24 — The three supplied links carry no Associates tag, so as supplied they cannot earn a commission",
    detail: "Verified 2026-11-14. Every resolved URL ends …&channelId=704&plpRedirect=mhFallback (short-link arrival) or …?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 (direct arrival); none carries a tag= parameter. Amazon's own help page gives the qualifying Special Link format as http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID and states that the tag identifies the Associates account the sale is tracked to.",
    severity: "medium",
    impact: "As supplied, the three links would earn nothing and could not be attributed in reporting. This blocks revenue, not identification — it is the one step that turns this repository from a verified research platform into a earning affiliate site.",
    actionRequired: "Owner: supply the Associates ID (and the target marketplace) so links can be regenerated in the tagged format the program requires.",
    ledgerFlag: "F-24",
    ledgerUrl: "pages/flags.html#F-24",
    source: "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC",
    sourceIds: ["S24", "S19", "S20", "S21"],
  },
];
/* END GENERATED: flags */

const PLATFORM_FEATURES = [
  { name: "Automated product research", desc: "Collects and organizes the full requirement list for affiliate products with verified official sources." },
  { name: "Trend & conversion analysis", desc: "Identifies trending and high-converting products; scores competition and commission potential." },
  { name: "Pricing, review & competition analysis", desc: "Analyzes pricing, reviews and competitive positioning — only from official sources; unverifiable values are flagged, never inferred." },
  { name: "SEO content generation", desc: "Generates SEO-optimized product articles, comparisons and buying guides from verified product data." },
  { name: "Link & campaign management", desc: "Creates and manages Special Links with Associates tags and sub-tags; tracks clicks and conversions." },
  { name: "Continuous optimization", desc: "Reconciles campaign performance monthly and continuously optimizes for affiliate revenue within program policies." },
  { name: "Policy compliance", desc: "Enforces Amazon Associates disclosure requirements and operating policies, including AI/agent transparency rules." },
];
