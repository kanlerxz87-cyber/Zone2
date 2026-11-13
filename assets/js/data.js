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
      "Official public statement: associates can earn up to 10% in commissions from qualifying purchases and programs. The category-specific rate card requires Associates sign-in and could not be publicly verified — left blank on the rate table.",
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
    item: "Home & Kitchen category rate",
    value: "",
    note: "Rate schedule (https://affiliate-program.amazon.com/help/operating/schedule) requires Associates sign-in; not publicly verifiable — left blank",
    source: "https://affiliate-program.amazon.com/help/operating/schedule",
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
    item: "Link-code / ASIN mismatch — Product 1",
    detail:
      "Provided link https://link.amazon/B04G1MEwY redirects to amazon.com/dp/B0CDY277D3. The code B04G1MEwY is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Treated as an opaque short-link token; the destination ASIN B0CDY277D3 is the verified product.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Link-code / ASIN mismatch — Product 2",
    detail:
      "Provided link https://link.amazon/B02NbDxp3 redirects to amazon.com/dp/B09B7SB46R. The code B02NbDxp3 is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Destination ASIN B09B7SB46R is the verified product.",
    source: "https://www.amazon.com/dp/B09B7SB46R",
  },
  {
    item: "Link-code / ASIN mismatch — Product 3",
    detail:
      "Provided link https://link.amazon/B00hJ57DV redirects to amazon.com/dp/B08DKYBTPH. The code B00hJ57DV is not a valid Amazon /dp/ ASIN (direct fetch returns “Page Not Found”). Destination ASIN B08DKYBTPH is the verified product.",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
  },
  {
    item: "Price — all three products (UNVERIFIED)",
    detail:
      "List price could not be confirmed from an official source via automated verification (Amazon bot protection; policy restricts price display to served links or Creators API / PA API). Left blank in all tables.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Star rating & review count — all three products (UNVERIFIED)",
    detail:
      "Rating and review-count could not be confirmed from an official source; Program Policy §6(t) also restricts displaying Amazon ratings/reviews outside Creators API / PA API. Left blank in all tables.",
    source: ASIN_SOURCE.policies,
  },
  {
    item: "Home & Kitchen category commission rate (UNVERIFIED)",
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
