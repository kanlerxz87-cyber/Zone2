/* Zone2 — verified dataset
 * Every value below was checked against the official source listed in its row's
 * "source" field. Values that could not be confirmed from an official source are
 * left null/empty and flagged as UNVERIFIED (see flagged page). Nothing is
 * inferred, averaged or filled in.

 * HEADLINE VERIFICATION RESULT (re-verified 2026-11-14, corroborates 2026-11-13):
 * the three supplied link.amazon short links do NOT map to identifiable products via a
 * valid Amazon identifier.
 *   - Each code is 9 characters; an Amazon ASIN is a 10-character identifier.
 *   - amazon.com/dp/<code> returns Amazon's "Page Not Found" error page for each.
 *   - Each link.amazon URL redirects (carrying plpRedirect=mhFallback / lv=shuf markers)
 *     to an Amazon air-fryer listing. The destinations are recorded below as OBSERVED
 *     redirect destinations.
 * Whether each redirect is a stable mapping or a shuffled fallback is CONTESTED between
 * sessions and under review: an earlier check (F-12) observed the destination body and
 * shuffle token changing between requests; a later control test (session c6e94e8d, the
 * "Revalidation 2026-11-14" pages) found the destinations stable and individually
 * tracked. This dataset does not assert either side. In all cases the destinations are
 * NOT established as the requested products by any official Amazon source, so product
 * identity is UNVERIFIED for all three supplied links and every product-specific
 * attribute is left blank and flagged.
 */

const VERIFIED_DATE = "2026-11-14";

const ASIN_SOURCE = {
  associatesHome: "https://affiliate-program.amazon.com/",
  policies: "https://affiliate-program.amazon.com/help/operating/policies",
  agreement: "https://affiliate-program.amazon.com/help/operating/agreement",
  asinDef: "https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC",
};

/* ---- Supplied affiliate links (verification status only) ----
 * Product identity could not be established from any official source, so title,
 * brand, category, price, rating, review count and availability are left null and
 * rendered as "— unverified —". The ASIN definition is cited from official Amazon
 * Associates help; the canonical /dp/ result is the observed Amazon error page. */
const PRODUCTS = [
  {
    id: "p1",
    shortLink: "https://link.amazon/B04G1MEwY",
    shortCode: "B04G1MEwY",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B04G1MEwY",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    title: null,
    brand: null,
    category: null,
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    status: "UNVERIFIED",
    source: "https://www.amazon.com/dp/B04G1MEwY",
    sourceLabel: "Amazon.com /dp/ lookup — returns Page Not Found",
    flags: ["F-01", "F-02", "F-03", "F-04", "F-06", "F-12"],
  },
  {
    id: "p2",
    shortLink: "https://link.amazon/B02NbDxp3",
    shortCode: "B02NbDxp3",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B02NbDxp3",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    title: null,
    brand: null,
    category: null,
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    status: "UNVERIFIED",
    source: "https://www.amazon.com/dp/B02NbDxp3",
    sourceLabel: "Amazon.com /dp/ lookup — returns Page Not Found",
    flags: ["F-01", "F-02", "F-03", "F-04", "F-06", "F-12"],
  },
  {
    id: "p3",
    shortLink: "https://link.amazon/B00hJ57DV",
    shortCode: "B00hJ57DV",
    codeLength: 9,
    asinFormatValid: false,
    canonicalDpUrl: "https://www.amazon.com/dp/B00hJ57DV",
    canonicalDpResult: "Page Not Found (Amazon error page)",
    title: null,
    brand: null,
    category: null,
    price: null,
    rating: null,
    reviewCount: null,
    availability: null,
    status: "UNVERIFIED",
    source: "https://www.amazon.com/dp/B00hJ57DV",
    sourceLabel: "Amazon.com /dp/ lookup — returns Page Not Found",
    flags: ["F-01", "F-02", "F-03", "F-04", "F-06", "F-12"],
  },
];

/* ---- Observed redirect destinations — OBSERVED, not the requested products ----
 * Each supplied link.amazon URL redirected (carrying plpRedirect=mhFallback / lv=shuf
 * markers) to an Amazon air-fryer listing. Whether each redirect is a stable mapping
 * or a shuffled fallback is contested and under review (F-12 vs. the Revalidation 2026-11-14
 * control test). Regardless, no official Amazon source establishes these destinations as
 * the requested products, so they are recorded as OBSERVED redirect destinations only.
 * Manufacturer specs for these candidate ASINs are documented, clearly labeled as
 * candidates, in the research-hub companion site (see F-12). */
const REDIRECT_DESTINATIONS = [
  {
    pid: "p1",
    destAsin: "B0CDY277D3",
    destTitle:
      "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry (observed redirect destination — mapping not confirmed)",
    redirectMarkers: "plpRedirect=mhFallback · lv=shuf",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    sourceLabel: "Amazon.com redirect destination (observed)",
  },
  {
    pid: "p2",
    destAsin: "B09B7SB46R",
    destTitle:
      "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven (observed redirect destination — mapping not confirmed)",
    redirectMarkers: "plpRedirect=mhFallback · lv=shuf",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    sourceLabel: "Amazon.com redirect destination (observed)",
  },
  {
    pid: "p3",
    destAsin: "B08DKYBTPH",
    destTitle:
      "Chefman Air Fryer 8 Qt | TurboFry 4-in-1 (observed redirect destination — mapping not confirmed)",
    redirectMarkers: "plpRedirect=mhFallback · lv=shuf · th=1",
    status: "OBSERVED",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    sourceLabel: "Amazon.com redirect destination (observed)",
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
    label: "ASIN identifier definition",
    value: "ASIN is the 10-digit code Amazon uses to denote specific products (Amazon.com Standard Item Number)",
    source: ASIN_SOURCE.asinDef,
  },
  {
    label: "Document currency",
    value: "Operating Agreement updated October 15, 2025; Program Policies updated April 14, 2026",
    source: ASIN_SOURCE.agreement,
  },
];

/* ---- Market & niche analysis ----
 * Reframed after the 2026-11-14 re-verification: the three supplied links did NOT
 * resolve to identifiable products. The air-fryer observations below describe the
 * observed fallback destinations only and are NOT a finding about the requested
 * products. No niche, pricing or competition claim is made for the supplied links. */
const NICHE_ANALYSIS = [
  {
    item: "Supplied-product identity",
    finding: "0 of 3 supplied products identified from official sources",
    detail:
      "Each supplied code is 9 characters (an ASIN is 10); amazon.com/dp/<code> returns Page Not Found; and each link.amazon URL redirects via plpRedirect=mhFallback to an unrelated listing. No official source identifies the intended product, so no attribute may be stated.",
    source: ASIN_SOURCE.asinDef,
    status: "unverified",
  },
  {
    item: "Observed redirect destinations (evidence only)",
    finding: "Each link redirected to a different, unrelated air-fryer listing",
    detail:
      "B0CDY277D3 (CHEFMAN 6-quart dual basket), B09B7SB46R (Emeril Lagasse 26QT French door), B08DKYBTPH (Chefman 8-qt TurboFry). These are observed redirect destinations, not confirmed product mappings. Whether each redirect is stable or shuffled is contested and under review (F-12 vs. the Revalidation 2026-11-14 control test).",
    source: "https://www.amazon.com/dp/B0CDY277D3",
    status: "observed",
  },
  {
    item: "Niche inference",
    finding: "Not established for the requested products",
    detail:
      "A 'countertop air frying' niche reading is an inference drawn from the observed fallback destinations, not from the supplied products. It is not published as a verified finding (F-12).",
    source: "https://www.amazon.com/dp/B09B7SB46R",
    status: "unverified",
  },
  {
    item: "Pricing analysis",
    finding: "Unverified",
    detail:
      "Amazon does not expose list price to automated verification; per policy, prices may only be shown if served within the Special Link or obtained via Creators API / PA API. Left blank — not inferred.",
    source: "https://www.amazon.com/dp/B04G1MEwY",
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
    finding: "Unverified for the supplied products",
    detail:
      "Competition can only be assessed among identified products. Because none of the three supplied links maps to an identifiable product, no competition claim is made. Observed fallback destinations compete in the air-fryer space, but that is evidence only.",
    source: "https://www.amazon.com/dp/B08DKYBTPH",
    status: "unverified",
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

/* ---- Marketing content plan (AI-generated content outputs) ----
 * The content generator is intentionally inert for the three supplied links because
 * product identity is unverified (F-06): no product copy is published for them. The
 * plan below records what WILL be produced once valid ASINs are supplied. */
const CONTENT_ROWS = [
  {
    content: "Product review article",
    target: "Product 1 (B04G1MEwY) — identity unverified",
    format: "SEO-optimized long-form review",
    status: "Blocked — identity unverified (F-06)",
    source: "https://www.amazon.com/dp/B04G1MEwY",
  },
  {
    content: "Product review article",
    target: "Product 2 (B02NbDxp3) — identity unverified",
    format: "SEO-optimized long-form review",
    status: "Blocked — identity unverified (F-06)",
    source: "https://www.amazon.com/dp/B02NbDxp3",
  },
  {
    content: "Product review article",
    target: "Product 3 (B00hJ57DV) — identity unverified",
    format: "SEO-optimized long-form review",
    status: "Blocked — identity unverified (F-06)",
    source: "https://www.amazon.com/dp/B00hJ57DV",
  },
  {
    content: "Comparison guide",
    target: "Product 1 vs Product 3 — identity unverified",
    format: "Side-by-side comparison article",
    status: "Blocked — identity unverified (F-06)",
    source: "https://www.amazon.com/dp/B04G1MEwY",
  },
  {
    content: "Comparison guide",
    target: "Compact vs large-capacity air fryer ovens — not established",
    format: "Buying-guide comparison article",
    status: "Blocked — niche inference not verified (F-12)",
    source: "https://www.amazon.com/dp/B02NbDxp3",
  },
  {
    content: "Buying guide",
    target: "“Best air fryer for family meals” — not established",
    format: "SEO buying guide with Special Link integration",
    status: "Blocked — identity unverified (F-06)",
    source: "https://www.amazon.com/dp/B00hJ57DV",
  },
];

/* ---- Campaign & link tracking plan ----
 * No Associates account, marketplace or tag was supplied (F-07), so no live tagged
 * link exists. These rows record the compliant setup that WILL be configured once an
 * account and tag are provided. */
const TRACKING_ROWS = [
  {
    campaign: "Launch — pending product identity",
    product: "All three supplied links (identity unverified)",
    linkType: "Special Link with Associates tag (tracking required)",
    status: "Planned — no tag/account supplied (F-07)",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Content — review articles",
    product: "Supplied links 1, 2, 3 (identity unverified)",
    linkType: "Special Link with Associates tag + sub-tag for A/B testing",
    status: "Planned — no tag/account supplied (F-07)",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Comparison guides",
    product: "Paired supplied links (identity unverified)",
    linkType: "Special Link with Associates tag",
    status: "Planned — no tag/account supplied (F-07)",
    source: ASIN_SOURCE.policies,
  },
  {
    campaign: "Conversion reporting",
    product: "All supplied links",
    linkType: "Associates Central reports (clicks, sessions, commission income)",
    status: "Planned — no account supplied (F-07)",
    source: ASIN_SOURCE.policies,
  },
];

/* ---- Flagged for review ---- */
const FLAGGED_ROWS = [
  {
    item: "Link-code / ASIN mismatch — Product 1",
    detail:
      "Provided link https://link.amazon/B04G1MEwY redirects (plpRedirect=mhFallback) to amazon.com/dp/B0CDY277D3. The code B04G1MEwY is 9 characters (an ASIN is 10) and amazon.com/dp/B04G1MEwY returns Page Not Found. The observed redirect destination is evidence only and is NOT the requested product. Owner must confirm the intended ASIN.",
    source: "https://www.amazon.com/dp/B04G1MEwY",
  },
  {
    item: "Link-code / ASIN mismatch — Product 2",
    detail:
      "Provided link https://link.amazon/B02NbDxp3 redirects (plpRedirect=mhFallback) to amazon.com/dp/B09B7SB46R. The code B02NbDxp3 is 9 characters (an ASIN is 10) and amazon.com/dp/B02NbDxp3 returns Page Not Found. The observed redirect destination is evidence only and is NOT the requested product.",
    source: "https://www.amazon.com/dp/B02NbDxp3",
  },
  {
    item: "Link-code / ASIN mismatch — Product 3",
    detail:
      "Provided link https://link.amazon/B00hJ57DV redirects (plpRedirect=mhFallback) to amazon.com/dp/B08DKYBTPH. The code B00hJ57DV is 9 characters (an ASIN is 10) and amazon.com/dp/B00hJ57DV returns Page Not Found. The observed redirect destination is evidence only and is NOT the requested product.",
    source: "https://www.amazon.com/dp/B00hJ57DV",
  },
  {
    item: "Redirect stability is contested (F-12 vs. Revalidation 2026-11-14)",
    detail:
      "Whether each link.amazon redirect is a stable token→product mapping or a shuffled fallback is under review and not asserted either way. An earlier check (F-12) observed a same-day re-fetch returning the same /dp/ path but a different page body and a different btn_ref token. A later control test (session c6e94e8d, 'Revalidation 2026-11-14') found the destinations stable and individually tracked. Either way, no official Amazon source establishes the destinations as the requested products.",
    source: "https://www.amazon.com/dp/B0CDY277D3",
  },
  {
    item: "Product identity — all three (UNVERIFIED)",
    detail:
      "No official source identifies the intended product for any of the three supplied links. Title, brand, category, price, rating, review count and availability are therefore left blank in all tables and not inferred.",
    source: ASIN_SOURCE.asinDef,
  },
  {
    item: "Price — all three products (UNVERIFIED / not published)",
    detail:
      "Amazon list prices could not be confirmed from an official source via automated verification (Amazon bot protection; policy restricts Amazon price display to served links or Creators API / PA API). Manufacturer-site prices exist for the observed fallback destinations but are deliberately not published on this site, in line with the program's price-display restrictions. Left blank in all tables.",
    source: "https://www.amazon.com/dp/B04G1MEwY",
  },
  {
    item: "Star rating & review count — all three products (UNVERIFIED)",
    detail:
      "Rating and review-count could not be confirmed from an official source for the supplied products; Program Policy §6(t) also restricts displaying Amazon ratings/reviews outside Creators API / PA API. Left blank in all tables.",
    source: ASIN_SOURCE.policies,
  },
  {
    item: "Home & Kitchen category commission rate (UNVERIFIED)",
    detail:
      "The official rate schedule requires Associates sign-in. Only the program-level public ceiling 'up to 10%' is verified; the category-specific rate is left blank.",
    source: "https://affiliate-program.amazon.com/help/operating/schedule",
  },
  {
    item: "Availability / stock status (UNVERIFIED)",
    detail:
      "Current availability could not be confirmed from an official source via automated verification for the supplied products. Left blank in all tables.",
    source: "https://www.amazon.com/dp/B02NbDxp3",
  },
  {
    item: "Content generation inert for the three supplied links (F-06)",
    detail:
      "Because product identity is unresolved, the article/comparison/guide generator is intentionally inert for all three entries. No product marketing copy is published for them. Valid ASINs unblock this step.",
    source: "https://www.amazon.com/dp/B00hJ57DV",
  },
  {
    item: "Associates tag absent on resolved short links (F-07)",
    detail:
      "The resolved link.amazon URLs carry no Associates tag parameter, and no Associates account/tag was supplied. Live click/conversion tracking requires Special Links that include the assigned Associates ID / tag (Participation Requirements §2). Flagged for account configuration before launch.",
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
