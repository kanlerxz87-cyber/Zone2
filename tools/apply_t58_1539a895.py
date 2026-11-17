#!/usr/bin/env python3
"""T58 (session 1539a895) — onboard the two unprocessed supplied affiliate links.

Adds P-04/P-05 (B0c8moW59 -> B0DHZTCNR5, B0f3GKalj -> B0DZFD6R9Z) to the
source-governed ledger, with an explicit product-intent confirmation record whose
fields (intended_asin / official_listing_url / confirmation_date / intent_source)
are kept separate from the observed redirect target. Also adds sources S61/S62,
flags F-42/F-43, verification rows V-105..V-108, questions Q-19/Q-20 and
suggestions SG-13/SG-14.

Every value below was read from the official Amazon listing pages on 2026-11-17.
Nothing is inferred; unconfirmed fields stay blank and flagged.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"


def load(name):
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


def save(name, doc):
    (LEDGER / name).write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote ledger/{name}")


OBS = "2026-11-17"

# ------------------------------------------------------------------ sources S61 / S62
sources_doc = load("sources.json")
existing_ids = {s["id"] for s in sources_doc["sources"]}
assert "S61" not in existing_ids and "S62" not in existing_ids
sources_doc["sources"] += [
    {
        "id": "S61",
        "publisher": "Amazon.com (product catalog page)",
        "kind": "official",
        "title": "Destination listing observed for supplied link 4 — B0DHZTCNR5 (ThermoMaven 1 Sec Professional Digital Meat Thermometer)",
        "url": "https://www.amazon.com/dp/B0DHZTCNR5",
        "page_stated_update": None,
        "accessed_utc": OBS,
        "used_for": [
            "evidence only: link.amazon token B0c8moW59 redirected here; NOT the requested product as an identity",
            "source for the observed destination specifications of the ThermoMaven thermometer",
        ],
        "last_reaccessed_utc": OBS,
    },
    {
        "id": "S62",
        "publisher": "Amazon.com (product catalog page)",
        "kind": "official",
        "title": "Destination listing observed for supplied link 5 — B0DZFD6R9Z (CHEF iQ Sense Smart Wireless Meat Thermometer, Gen3)",
        "url": "https://www.amazon.com/dp/B0DZFD6R9Z",
        "page_stated_update": None,
        "accessed_utc": OBS,
        "used_for": [
            "evidence only: link.amazon token B0f3GKalj redirected here; NOT the requested product as an identity",
            "source for the observed destination specifications of the CHEF iQ thermometer",
        ],
        "last_reaccessed_utc": OBS,
    },
]
save("sources.json", sources_doc)

# --------------------------------------------------------------------------- flags F-42 / F-43
flags_doc = load("flags.json")
existing_flag_ids = {f["id"] for f in flags_doc["flags"]}
assert "F-42" not in existing_flag_ids and "F-43" not in existing_flag_ids
flags_doc["flags"] += [
    {
        "id": "F-42",
        "severity": "medium",
        "owner": "user",
        "status": "open",
        "published_on": OBS,
        "title": "The 4th and 5th supplied links were never processed, and they resolve to a different product category",
        "detail": "The brief names five link.amazon links, but every prior session processed only the first three (B04G1MEwY, B02NbDxp3, B00hJ57DV), which resolve to air fryers. Links 4 (B0c8moW59) and 5 (B0f3GKalj) had zero references anywhere in the repository before this session. Re-resolved live on 2026-11-17, each opens one stable Amazon listing — B0c8moW59 -> B0DHZTCNR5 (ThermoMaven 1-sec digital meat thermometer) and B0f3GKalj -> B0DZFD6R9Z (CHEF iQ Sense smart wireless meat thermometer) — i.e. kitchen thermometers, a second product category the site's air-fryer marketing copy does not cover. The two codes are still 9 characters, not valid ASINs, and /dp/<code> returns Amazon's Page Not Found page, exactly as for the first three (F-01, F-28 control).",
        "impact": "Two of the five requested products had no catalog row, no verification, no marketing content and no decision record. The published shop front under-represents the brief by two items and spans a category (thermometers) with no reader-facing content.",
        "action_required": "Owner: confirm the intended ASINs for links 4 and 5 (Q-19), then decide whether to build a matching thermometer content set (SG-13). No price, rating or commission value is asserted for either.",
        "source_ids": ["S61", "S62", "S16"],
    },
    {
        "id": "F-43",
        "severity": "low",
        "owner": "user",
        "status": "open",
        "published_on": OBS,
        "title": "The commission band for kitchen thermometers is ambiguous in Amazon's published Table 1",
        "detail": "Both new destinations sit in Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat. Amazon's public Standard Commission Income Statement (Table 1) lists 'Kitchen' at 4.50% and 'Home' at 3.00%, but does not name the 'Kitchen Utensils & Gadgets' node, so the band for these two items cannot be assigned from the public table without guessing between the two. The repository's rule is to leave a value blank when no official source states it, so commission_rate stays blank for P-04 and P-05 rather than being inferred from the parent category.",
        "impact": "Commission-potential scoring for the two thermometers is blocked until an authenticated Creators API catalog lookup returns the item's category, or the owner confirms the band.",
        "action_required": "Owner: an authenticated Creators API GetItems lookup for B0DHZTCNR5 and B0DZFD6R9Z returns the authoritative category and therefore the band; until then the field stays blank and flagged.",
        "source_ids": ["S04", "S61", "S62"],
    },
]
save("flags.json", flags_doc)

# ----------------------------------------------------------------------------- products P-04 / P-05
products_doc = load("products.json")
ids = {e["id"] for e in products_doc["entries"]}
assert "P-04" not in ids and "P-05" not in ids

WHY_BLANK_TOKEN = (
    "Token is 9 characters, so it is not a valid ASIN; the canonical /dp/ URL returns Amazon's "
    "Page Not Found page. The supplied short link does open one live listing, and that destination is "
    "stable across re-fetches, but no public Amazon document binds the short code to it (F-03), the "
    "per-link btn_ref token changes between days (F-21), and no resolved URL carries an Associates tag "
    "(F-24). No official record therefore identifies the intended product, so no attribute may be stated."
)
WHY_BLANK_METRICS = (
    "Price, rating, review count, availability and sales rank are point-in-time values that the Amazon "
    "Associates Program Policies do not allow to be republished outside an Amazon link or a licensed API "
    "(S02), and the category commission band needs an authenticated catalog lookup (S04, S08) — for these "
    "thermometer items the public Table 1 does not name the 'Kitchen Utensils & Gadgets' node (F-43). They "
    "are left blank rather than inferred."
)

def intent_record(observed_target):
    """Product-intent confirmation record. The four intent fields are intentionally blank
    until the owner confirms them; the observed redirect target is kept in a separate field
    and the two are never merged."""
    return {
        "intended_asin": "",
        "official_listing_url": "",
        "confirmation_date": "",
        "intent_source": "",
        "observed_redirect_target": observed_target,
        "intent_status": "UNCONFIRMED",
        "note": (
            "Product-intent confirmation record. intended_asin / official_listing_url / "
            "confirmation_date / intent_source are populated only when the owner confirms the item "
            "intended in the brief; they are deliberately blank now. observed_redirect_target records "
            "what the link was observed to resolve to and is kept in a separate field so the two "
            "readings can never be merged (brief rule)."
        ),
    }

p04 = {
    "id": "P-04",
    "label": "Submitted item 4",
    "submitted_url": "https://link.amazon/B0c8moW59",
    "token_as_given": "B0c8moW59",
    "asin_format_valid": False,
    "asin_length_observed": 9,
    "canonical_dp_url": "https://www.amazon.com/dp/B0c8moW59",
    "canonical_dp_result": "Page Not Found (Amazon error page)",
    "title": "",
    "brand": "",
    "category": "",
    "price": "",
    "availability": "",
    "rating": "",
    "review_count": "",
    "bsr": "",
    "commission_rate": "",
    "competition_level": "",
    "conversion": "",
    "clicks": "",
    "status": "UNVERIFIED",
    "source_ids": ["S16", "S61"],
    "why_blank": WHY_BLANK_TOKEN,
    "flag_ids": ["F-01", "F-02", "F-04", "F-06", "F-20", "F-21", "F-22", "F-23", "F-24", "F-42", "F-43"],
    "resolves_to": "https://www.amazon.com/dp/B0DHZTCNR5",
    "intent_confirmation": intent_record("https://www.amazon.com/dp/B0DHZTCNR5"),
    "resolved": {
        "asin": "B0DHZTCNR5",
        "title": "ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified Food Thermometer, Auto-Rotate Bright LED Screen, Highly Waterproof for Grill BBQ Camping, Black",
        "brand": "ThermoMaven",
        "category": "Home & Kitchen",
        "category_path": "Home & Kitchen › Kitchen & Dining › Kitchen Utensils & Gadgets › Thermometers & Timers › Meat",
        "resolves_to": "https://www.amazon.com/dp/B0DHZTCNR5",
        "observation_status": "OBSERVED",
        "observed_utc": OBS,
        "source_ids": ["S61"],
        "manufacturer_source_ids": [],
        "specs": [
            {"attribute": "Response time", "value": "1 second", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Response Time: 1 seconds')"},
            {"attribute": "Accuracy", "value": "±0.5 °F", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing title ('±0.5℉ Accuracy')"},
            {"attribute": "Upper temperature range", "value": "572 °F", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Upper Temperature Range: 572 °F')"},
            {"attribute": "Resolution", "value": "0.1 °", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Resolution: 0.1°')"},
            {"attribute": "Immersion depth", "value": "6.5 in", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Immersion Depth: 6.5 inches')"},
            {"attribute": "Display type", "value": "Digital", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Display Type: Digital')"},
            {"attribute": "Power source", "value": "Battery powered (1 AAA battery, included)", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Power Source: Battery Powered'; 'Number of Batteries: 1 AAA batteries required. (included)')"},
            {"attribute": "Additional features", "value": "Auto off, fast reading system, high accuracy, ultra clear screen, waterproof", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Additional Features')"},
            {"attribute": "Reusability", "value": "Reusable", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Reusability: Reusable')"},
            {"attribute": "Indoor / outdoor use", "value": "Indoor, Outdoor", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Features & Specs ('Indoor Outdoor Usage: Indoor, Outdoor')"},
            {"attribute": "Specification met", "value": "NIST, NSF", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > User guide ('Specification Met: NIST, NSF')"},
            {"attribute": "Material", "value": "Plastic", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Materials & Care ('Outer Material: Plastic'; 'Inner Material: Plastic')"},
            {"attribute": "Care instructions", "value": "Wipe clean", "status": "verified",
             "source_ids": ["S61"], "source_label": "Amazon listing — Product information > Materials & Care ('Product Care Instructions: Wipe Clean')"},
        ],
        "price": "",
        "rating": "",
        "review_count": "",
        "availability": "",
        "bsr": "",
        "commission_rate": "",
        "why_blank": WHY_BLANK_METRICS,
        "title_last_read_utc": OBS,
    },
}

p05 = {
    "id": "P-05",
    "label": "Submitted item 5",
    "submitted_url": "https://link.amazon/B0f3GKalj",
    "token_as_given": "B0f3GKalj",
    "asin_format_valid": False,
    "asin_length_observed": 9,
    "canonical_dp_url": "https://www.amazon.com/dp/B0f3GKalj",
    "canonical_dp_result": "Page Not Found (Amazon error page)",
    "title": "",
    "brand": "",
    "category": "",
    "price": "",
    "availability": "",
    "rating": "",
    "review_count": "",
    "bsr": "",
    "commission_rate": "",
    "competition_level": "",
    "conversion": "",
    "clicks": "",
    "status": "UNVERIFIED",
    "source_ids": ["S16", "S62"],
    "why_blank": WHY_BLANK_TOKEN,
    "flag_ids": ["F-01", "F-02", "F-04", "F-06", "F-20", "F-21", "F-22", "F-23", "F-24", "F-42", "F-43"],
    "resolves_to": "https://www.amazon.com/dp/B0DZFD6R9Z",
    "intent_confirmation": intent_record("https://www.amazon.com/dp/B0DZFD6R9Z"),
    "resolved": {
        "asin": "B0DZFD6R9Z",
        "title": "CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | BBQ, Grill, Oven, Smoker, Air Fryer | Gen3",
        "brand": "CHEF iQ",
        "category": "Home & Kitchen",
        "category_path": "Home & Kitchen › Kitchen & Dining › Kitchen Utensils & Gadgets › Thermometers & Timers › Meat",
        "resolves_to": "https://www.amazon.com/dp/B0DZFD6R9Z",
        "observation_status": "OBSERVED",
        "observed_utc": OBS,
        "source_ids": ["S62"],
        "manufacturer_source_ids": [],
        "specs": [
            {"attribute": "Sensors", "value": "5 (4 internal temperature sensors + 1 ambient sensor)", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — About this Item ('FIVE SENSORS, MAX ACCURACY: ... 4 internal temperature sensors. Additionally, an ambient sensor ...')"},
            {"attribute": "Accuracy", "value": "within 1 °F", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — Product Description ('designed for incredible accuracy within 1°F'; 'Accurate within 1˚F')"},
            {"attribute": "Heat safety", "value": "1000 °F", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing title and About this Item ('1000°F Heat Safe'; 'built to endure 1000°F heat')"},
            {"attribute": "Probes included", "value": "3 ultra-thin probes", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing title and About this Item ('3 Ultra-Thin Probes'; 'THREE PROBES INCLUDED')"},
            {"attribute": "Probe length", "value": "4.75 in", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — Product Description ('equipped with a 4.75\" long design')"},
            {"attribute": "Connectivity", "value": "WiFi (unlimited range) and Bluetooth", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing title and About this Item ('WiFi Unlimited Range'; 'Pair your digital Bluetooth food thermometer with the CHEF iQ App')"},
            {"attribute": "Battery life", "value": "up to 50 hours (About this Item) / 70+ hours (Product Description)", "status": "conflict",
             "source_ids": ["S62"], "source_label": "Amazon listing — About this Item ('running for up to 50 hours on a full charge') contradicts the Product Description ('up to 70 hours of usage on a full charge'). Both figures are published; neither is chosen.",
             "why_blank": "Two values appear on the same official listing and disagree (50 vs 70 hours). The repository publishes both rather than selecting one."},
            {"attribute": "Probe care", "value": "Waterproof and dishwasher-safe probes", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — About this Item ('Waterproof and dishwasher-safe probes')"},
            {"attribute": "Warranty", "value": "Two-year assurance provided by CHEF iQ", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — About this Item ('two-year assurance provided by CHEF iQ')"},
            {"attribute": "Smart hub", "value": "Speaker for audio notifications plus phone push notifications; charges all probes simultaneously", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — About this Item ('Smart Hub features a speaker for audio notifications as well as push notifications'; 'The hub can charge all three probes simultaneously')"},
            {"attribute": "Air-fryer / deep-fryer safe", "value": "Yes", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — Product Description ('Air-fryer and deep-fryer safe')"},
            {"attribute": "Size options", "value": "1, 2, 3 or 4 probes", "status": "verified",
             "source_ids": ["S62"], "source_label": "Amazon listing — Options Available > Size ('1 Probe', '2 Probes', '3 Probes', '4 Probes')"},
        ],
        "price": "",
        "rating": "",
        "review_count": "",
        "availability": "",
        "bsr": "",
        "commission_rate": "",
        "why_blank": WHY_BLANK_METRICS,
        "title_last_read_utc": OBS,
    },
}

products_doc["entries"] += [p04, p05]

# evidence observations E-05 / E-06
obs_ids = {o["id"] for o in products_doc["evidence_observations"]}
new_obs = []
if "E-05" not in obs_ids:
    new_obs.append({
        "id": "E-05",
        "observation": "GET https://link.amazon/B0c8moW59 ended at https://www.amazon.com/dp/B0DHZTCNR5?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-...&channelId=500&plpRedirect=mhFallback (page title observed: ThermoMaven 1 Sec Professional Digital Meat Thermometer, ±0.5℉ Accuracy | NIST&NSF Certified ... Black)",
        "interpretation": "Destination of the supplied link 4: one live ThermoMaven 1-sec digital meat thermometer listing (same ASIN on re-fetch). Stable across re-fetches; not bound to the code by any public Amazon document (F-03, F-20).",
        "status": "OBSERVED",
        "source_ids": ["S61"],
    })
if "E-06" not in obs_ids:
    new_obs.append({
        "id": "E-06",
        "observation": "GET https://link.amazon/B0f3GKalj ended at https://www.amazon.com/dp/B0DZFD6R9Z?lv=shuf&btn_type=ss&gaOptInStatus=true&btn_ref=srctok-...&channelId=500&plpRedirect=mhFallback&th=1 (page title observed: CHEF iQ Sense | Smart Wireless Meat Thermometer | 3 Ultra-Thin Probes | WiFi Unlimited Range | 1000°F Heat Safe | 5 Sensors | ... | Gen3)",
        "interpretation": "Destination of the supplied link 5: one live CHEF iQ Sense smart wireless meat thermometer listing (same ASIN on re-fetch). Stable across re-fetches; not bound to the code by any public Amazon document (F-03, F-20).",
        "status": "OBSERVED",
        "source_ids": ["S62"],
    })
products_doc["evidence_observations"] += new_obs

# update the ledger note + reverification stamp
products_doc["note"] = (
    products_doc["note"]
    + " ADDENDUM 2026-11-17 (session 1539a895, T58): the brief names five link.amazon links, but only the "
    "first three had been processed. This session resolves the 4th (B0c8moW59) and 5th (B0f3GKalj) live and "
    "adds them as P-04 and P-05. Both resolve to kitchen thermometers — B0c8moW59 -> B0DHZTCNR5 (ThermoMaven "
    "1-sec digital meat thermometer) and B0f3GKalj -> B0DZFD6R9Z (CHEF iQ Sense smart wireless meat thermometer) "
    "— a second product category. Each supplied code is still 9 characters (not a valid ASIN) and /dp/<code> "
    "returns Amazon's Page Not Found page, exactly as for the first three. Each entry now carries an explicit "
    "product-intent confirmation record (intended_asin / official_listing_url / confirmation_date / intent_source) "
    "kept separate from the observed redirect target, per the brief's rule that the two must never be merged; the "
    "intent fields are blank until the owner confirms them. Destination specifications are recorded from the two "
    "official Amazon listing pages (S61, S62); the CHEF iQ battery-life row is published as a conflict (50 vs 70 "
    "hours) rather than resolved. No verified value from the first three entries was altered; no price, rating or "
    "commission value was inferred."
)
products_doc["last_reverified_utc"] = OBS
save("products.json", products_doc)

# ------------------------------------------------- verification rows V-105 .. V-108
ver_doc = load("verification.json")
ver_ids = {r["id"] for r in ver_doc["rows"]}
ver_doc["rows"] += [
    {
        "id": "V-105",
        "subject": "Supplied link 4 — https://link.amazon/B0c8moW59",
        "claim": "the short link resolves, reproducibly, to one live Amazon listing, B0DHZTCNR5 (ThermoMaven 1 Sec Professional Digital Meat Thermometer)",
        "method": "live fetch of https://link.amazon/B0c8moW59 on 2026-11-17; the final URL and page title were read from the served page",
        "verdict": "OBSERVED",
        "source_ids": ["S61"],
        "consequence": "P-04 is recorded with its observed destination. The destination is stable across re-fetches but is not bound to the 9-character code by any public Amazon document, so it is an observation, not an established identity (F-03, F-20).",
    },
    {
        "id": "V-106",
        "subject": "Supplied link 5 — https://link.amazon/B0f3GKalj",
        "claim": "the short link resolves, reproducibly, to one live Amazon listing, B0DZFD6R9Z (CHEF iQ Sense Smart Wireless Meat Thermometer, Gen3)",
        "method": "live fetch of https://link.amazon/B0f3GKalj on 2026-11-17; the final URL and page title were read from the served page",
        "verdict": "OBSERVED",
        "source_ids": ["S62"],
        "consequence": "P-05 is recorded with its observed destination. Same standing as V-105: observed behaviour, not an established identity (F-03, F-20).",
    },
    {
        "id": "V-107",
        "subject": "Canonical /dp/ lookups for the two new 9-character codes",
        "claim": "https://www.amazon.com/dp/B0c8moW59 and https://www.amazon.com/dp/B0f3GKalj each return Amazon's Page Not Found page",
        "method": "live fetch of both /dp/ URLs on 2026-11-17; both served Amazon's 'Sorry! We couldn't find that page.' error page",
        "verdict": "OBSERVED",
        "source_ids": ["S61", "S62"],
        "consequence": "Confirms the 9-character codes are not ASINs and cannot address a catalog record as written, matching the control and flag F-01/F-28 already recorded for the first three codes.",
    },
    {
        "id": "V-108",
        "subject": "Thermometer destination specifications (P-04, P-05)",
        "claim": "the published specification rows for the two thermometer destinations were read from their official Amazon listing pages and carry that listing as their source",
        "method": "read the 'Product information' / 'About this Item' / 'Product Description' blocks of https://www.amazon.com/dp/B0DHZTCNR5 (S61) and https://www.amazon.com/dp/B0DZFD6R9Z (S62) on 2026-11-17; each spec row pins the attribute to the listing text that states it",
        "verdict": "OBSERVED",
        "source_ids": ["S61", "S62"],
        "consequence": "P-04 and P-05 carry sourced specification rows. The CHEF iQ battery-life value is published as a conflict (50 vs 70 hours on the same listing) rather than resolved. Price, rating, review count, availability, sales rank and commission band remain blank and flagged (F-43).",
    },
]
save("verification.json", ver_doc)

# ------------------------------------------------------------- questions Q-19 / Q-20
q_doc = load("questions.json")
q_ids = {q["id"] for q in q_doc["questions"]}
q_doc["questions"] += [
    {
        "id": "Q-19",
        "question": "For the 4th and 5th supplied links, what are the intended ASINs, and are the observed thermometer destinations the products the brief meant to promote?",
        "known": "B0c8moW59 resolves reproducibly to B0DHZTCNR5 (ThermoMaven 1-sec digital meat thermometer) and B0f3GKalj to B0DZFD6R9Z (CHEF iQ Sense smart wireless meat thermometer), each to one stable listing (V-105, V-106). Both codes are 9 characters, not valid ASINs, and /dp/<code> returns Page Not Found (V-107, F-01). No public Amazon document binds a link.amazon code to a destination (F-03), and no resolved URL carries an Associates tag (F-24).",
        "missing": "Whether the two thermometer listings are the products the brief intended, or whether the intended items are different ASINs entirely. Only the owner can state intent; nothing public maps a short code back to a requested product.",
        "how_to_find": "Owner: in Associates Central, open the two links (or SiteStripe > Get Link on the intended product pages) and read the Tracking ID and destination each account-issued link points to; or supply the full 10-character ASIN / amazon.<tld>/dp/ URL for each intended item. Until then the intent fields on P-04/P-05 stay blank and the destinations are labelled observed only.",
        "blocks": ["SG-13", "SG-14"],
        "source_ids": ["S61", "S62", "S16", "S02"],
        "owner": "owner",
    },
    {
        "id": "Q-20",
        "question": "Which commission band applies to the two thermometer destinations, and is it confirmed by an authenticated catalog lookup?",
        "known": "Both destinations sit in Home & Kitchen > Kitchen & Dining > Kitchen Utensils & Gadgets > Thermometers & Timers > Meat (S61, S62). Amazon's public Standard Commission Income Statement (Table 1) lists 'Kitchen' at 4.50% and 'Home' at 3.00% but does not name the 'Kitchen Utensils & Gadgets' node (S04).",
        "missing": "The authoritative category for B0DHZTCNR5 and B0DZFD6R9Z, and therefore the commission band. The public table alone does not resolve which of the two bands applies.",
        "how_to_find": "Owner: an authenticated Creators API GetItems lookup for each ASIN returns the item's category and commission rate (S04, S08). Until that lookup runs, commission_rate stays blank and flagged (F-43) rather than inferred from the parent category.",
        "blocks": ["SG-13"],
        "source_ids": ["S04", "S08", "S61", "S62"],
        "owner": "owner",
    },
]
save("questions.json", q_doc)

# -------------------------------------------------------- suggestions SG-13 / SG-14
s_doc = load("suggestions.json")
s_ids = {s["id"] for s in s_doc["suggestions"]}
s_doc["suggestions"] += [
    {
        "id": "SG-13",
        "area": "Shop front / content (thermometer category)",
        "title": "Treat the two newly supplied thermometer links as a second product category and build a matching set of buyer-question articles",
        "suggestion": "Once the intended ASINs are confirmed (Q-19), add a thermometer content set to the shop front parallel to the air-fryer set: a category landing, a comparison of the two thermometers, a buying guide, and question-shaped articles (e.g. 'wireless vs instant-read: which thermometer for your cooking style', 'how many probes do you actually need'). Every article carries the same source discipline: each figure read from the official listing with its link, no hands-on claim, no price, no rating, and the observed-vs-intended label kept visible.",
        "why": "The brief names five products but the shop front only covered three air fryers; the two thermometers had no catalog row, no verification and no reader-facing content (F-42). Google's guidance is that affiliate pages should offer meaningful original content — comparisons and navigation — rather than thin listing copies, and question-shaped titles answer what readers actually type. This is the same publication standard the air-fryer set already meets, applied to the second category.",
        "evidence": ["S61", "S62", "S23", "S40"],
        "options": [
            {"id": "A", "label": "Build the full thermometer set now, labelled observed-only until Q-19 confirms intent",
             "tradeoff": "Fastest to a complete shop front; carries the same observed-vs-intended label the air-fryer set already uses, so nothing is overclaimed."},
            {"id": "B", "label": "Wait for Q-19 before writing any thermometer content",
             "tradeoff": "Cleanest identity, but leaves two of five requested products with no reader-facing page until the owner acts."},
            {"id": "C", "label": "Publish the two thermometer catalog rows and spec tables now, defer the editorial articles to the next cadence",
             "tradeoff": "Middle path: the verified data ships immediately, the editorial expansion waits on the identity decision."},
        ],
        "recommended": "C",
        "needs_answers": ["Q-19", "Q-20"],
        "decision": "",
        "status": "awaiting owner decision",
        "owner": "owner",
    },
    {
        "id": "SG-14",
        "area": "Intake / compliance gate",
        "title": "Adopt the product-intent confirmation record as the standard intake for every submitted affiliate link",
        "suggestion": "For every submitted link, store the intended ASIN, official listing URL, confirmation date and source in dedicated fields, and keep the observed redirect target in a separate field — never merged. The record is populated only when the owner confirms intent; until then the row reads observed-only. This is now the schema on P-04/P-05 and should be the schema for all future intakes.",
        "why": "Amazon's ASIN is a checkable identifier, so a confirmed intended ASIN is the one field that turns an observed redirect into a defensible product identity. Keeping the two readings in separate fields prevents the observed destination from being silently promoted to 'the intended product', which is the exact overclaim this repository has repeatedly corrected (F-03, F-24). It also gives the owner a single, dated place to act.",
        "evidence": ["S16", "S61", "S62", "S02"],
        "options": [
            {"id": "A", "label": "Adopt it as the mandatory intake schema and apply it to all five links retroactively",
             "tradeoff": "One consistent record across the brief; the intent fields stay blank until the owner confirms each, so no value is invented."},
            {"id": "B", "label": "Apply it only to new intakes going forward",
             "tradeoff": "Less retroactive work, but leaves the first three links without the explicit intent fields."},
            {"id": "C", "label": "Adopt it and add a gate that refuses to publish a product row whose intent fields are blank without an observed-only label",
             "tradeoff": "Strongest guard against overclaiming; requires a small validator change (logged, not made without the owner's go-ahead)."},
        ],
        "recommended": "A",
        "needs_answers": ["Q-19"],
        "decision": "",
        "status": "awaiting owner decision",
        "owner": "owner",
    },
]
save("suggestions.json", s_doc)

print("T58 ledger additions complete.")
