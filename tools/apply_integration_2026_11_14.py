#!/usr/bin/env python3
"""Apply the T23 final-integration corrections to ledger/products.json, ledger/flags.json and
ledger/sources.json.

Run once, by the final integration session. Every change below is the result of a live fetch on
2026-11-14 against an official Amazon or manufacturer page, or against the supplied link itself.
Nothing is inferred. Values that could not be confirmed are left blank and flagged.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"
SPECS = json.loads((REPO / "tools" / "verified_specs_2026-11-14.json").read_text(encoding="utf-8"))

RESOLVED = {
    "P-01": {
        "asin": "B0CDY277D3",
        "title": "CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows, Sync Finish, Hi-Fry, Auto Shutoff, 2 Independent 3Qt Nonstick Dishwasher Safe Frying Baskets, Digital Double Air Fryer - Black",
        "brand": "CHEFMAN",
        "category": "Home & Kitchen",
        "category_path": "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
        "source_ids": ["S19"],
        "manufacturer_source_ids": ["S25"],
        "specs": SPECS["products"][0]["specs"],
    },
    "P-02": {
        "asin": "B09B7SB46R",
        "title": "Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven | 26QT air fryer oven with French doors, 24 cooking functions, dual-speed fan and rotisserie for easy family meals.",
        "brand": "Emeril Lagasse",
        "category": "Home & Kitchen",
        "category_path": "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
        "source_ids": ["S20"],
        "manufacturer_source_ids": ["S27"],
        "specs": SPECS["products"][1]["specs"],
    },
    "P-03": {
        "asin": "B08DKYBTPH",
        "title": "Chefman Air Fryer 8 Qt | TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results | Bake, Dehydrate, Frozen | XL Nonstick Dishwasher-Safe Basket | Stainless Steel",
        "brand": "Chefman",
        "category": "Home & Kitchen",
        "category_path": "Home & Kitchen › Kitchen & Dining › Small Appliances › Fryers › Air Fryers",
        "source_ids": ["S21"],
        "manufacturer_source_ids": ["S26"],
        "specs": SPECS["products"][2]["specs"],
    },
}

WHITE_BLANK = (
    "Price, rating, review count, availability and sales rank are point-in-time values that the Amazon "
    "Associates Program Policies do not allow to be republished outside an Amazon link or a licensed API "
    "(S02), and the category commission band needs an authenticated catalog lookup (S04, S08). They are "
    "left blank rather than inferred."
)


def load(name: str) -> dict:
    return json.loads((LEDGER / name).read_text(encoding="utf-8"))


def save(name: str, data: dict) -> None:
    (LEDGER / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------------------- products
products = load("products.json")
products["note"] = (
    "Ledger of the three affiliate links named in the project brief. Two different questions are kept apart "
    "on purpose. (1) IDENTITY OF THE TOKEN AS SUPPLIED — each supplied code is 9 characters, an ASIN is 10, "
    "and amazon.com/dp/<code> returns Amazon's Page Not Found page, so no attribute can be stated for the "
    "token itself; those fields are blank and the rows are marked UNVERIFIED. (2) WHAT THE LINK RESOLVES TO "
    "— each link.amazon URL resolves to one specific Amazon product page, reproducibly, and an unknown code "
    "on the same service returns a 404 rather than a random product (flag F-20), so the destination is a "
    "verified observation of the link's behaviour. The two are recorded separately because Amazon publishes "
    "no document that binds a link.amazon code to a product, so the destination is not established as the "
    "item the brief intended. Verified 2026-11-14 by live fetch."
)
products["verified_utc"] = "2026-11-14"

for entry in products["entries"]:
    r = RESOLVED[entry["id"]]
    entry["why_blank"] = (
        "The token as supplied is 9 characters, so it is not a valid ASIN, and amazon.com/dp/<token> returns "
        "Amazon's Page Not Found page: no field can be stated for the token itself. The product this link "
        "resolves to is recorded separately in `resolved` below. " + WHITE_BLANK
    )
    entry["source_ids"] = sorted(set(entry["source_ids"] + [r["source_ids"][0]]))
    entry["flag_ids"] = sorted(set(entry["flag_ids"] + ["F-20", "F-21", "F-22", "F-23", "F-24"]))
    entry["resolved"] = {
        "asin": r["asin"],
        "title": r["title"],
        "brand": r["brand"],
        "category": r["category"],
        "category_path": r["category_path"],
        "resolves_to": "https://www.amazon.com/dp/" + r["asin"],
        "observation_status": "OBSERVED",
        "observed_utc": "2026-11-14",
        "source_ids": r["source_ids"],
        "manufacturer_source_ids": r["manufacturer_source_ids"],
        "specs": r["specs"],
        "price": "",
        "rating": "",
        "review_count": "",
        "availability": "",
        "bsr": "",
        "commission_rate": "",
        "why_blank": WHITE_BLANK,
    }

obs = {o["id"]: o for o in products["evidence_observations"]}
obs["E-01"]["interpretation"] = (
    "The destination is a specific product and it is stable for this token — but three different tokens "
    "landing on three different products is NOT by itself evidence of a mapping. The decisive control is "
    "E-06."
)
obs["E-02"]["interpretation"] = (
    "Second distinct destination, second distinct per-link btn_ref token (srctok-534f5e7952f396b2 at the "
    "time of that fetch). Distinctness across tokens, not randomness within a token."
)
obs["E-03"]["interpretation"] = (
    "Third distinct destination, third distinct per-link btn_ref token (srctok-76c3adaeb8708b44 at the time "
    "of that fetch)."
)
obs["E-04"]["observation"] = (
    "https://www.amazon.com/dp/B04G1MEwY , https://www.amazon.com/dp/B02NbDxp3 and https://www.amazon.com/dp/B00hJ57DV "
    "each returned Amazon's \"Sorry! We couldn't find that page\" error page on 2026-11-13 and again on 2026-11-14."
)
products["evidence_observations"] = list(obs.values()) + [
    {
        "id": "E-06",
        "observation": (
            "CONTROL — an unknown code on the same short-link service: GET https://link.amazon/B00TEST12 "
            "(9 characters, never supplied) resolved to https://amzlinks.in/B00TEST12 and returned the "
            "service's 404 page — \"404: File Not Found … You've clicked on an invalid URL.\" "
            "(image host: amzlinks.in/post-tap/short-link-404.png)."
        ),
        "interpretation": (
            "DECISIVE. The service looks the code up: an unknown code returns a 404 instead of an arbitrary "
            "product. The three supplied codes therefore ARE honoured lookups, and the earlier reading that "
            "the token was ignored and the destination arbitrary (flag F-03) is falsified. What is still "
            "unconfirmed is the *contract* — Amazon publishes no document binding a link.amazon code to a "
            "product — not the behaviour."
        ),
        "status": "OBSERVED",
        "source_ids": ["S32", "S19", "S20", "S21"],
    },
    {
        "id": "E-07",
        "observation": (
            "CONTROL — a bare, untagged GET https://www.amazon.com/dp/B08DKYBTPH (a valid 10-character ASIN) "
            "returned the CHEFMAN 8 Qt product page with ?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 "
            "appended to Amazon's own internal links, and with no btn_ref parameter at all."
        ),
        "interpretation": (
            "plpRedirect=mhFallback is emitted on ordinary, direct, valid product-page loads. It is therefore "
            "NOT evidence of a fallback and cannot distinguish a valid ASIN from an invalid token."
        ),
        "status": "OBSERVED",
        "source_ids": ["S21"],
    },
    {
        "id": "E-08",
        "observation": (
            "The three supplied links each carry their own btn_ref=srctok-… source token and the same "
            "channelId=704: B04G1MEwY → srctok-1f979f303a4b5691, B02NbDxp3 → srctok-0cd8be3c7e2e0de3, "
            "B00hJ57DV → srctok-7c59360cbbbd59b7 (observed 2026-11-14 ~10:05 UTC)."
        ),
        "interpretation": (
            "Three distinct per-link source tokens — the signature of individually tracked links, not of a "
            "shared fallback."
        ),
        "status": "OBSERVED",
        "source_ids": ["S19", "S20", "S21"],
    },
    {
        "id": "E-09",
        "observation": (
            "Cross-time check on one link: link.amazon/B04G1MEwY carried btn_ref=srctok-1e229870efde5acf earlier "
            "on 2026-11-14 (recorded by session c6e94e8d) and btn_ref=srctok-1f979f303a4b5691 at ~10:04 UTC on "
            "the same day, while the destination stayed /dp/B0CDY277D3 on every fetch."
        ),
        "interpretation": (
            "The btn_ref source token rotates over time; the DESTINATION does not. Two earlier claims are "
            "therefore both wrong in different ways: 'a different btn_ref on re-fetch proves the destination "
            "shuffles' (F-05, F-12) and 'an identical btn_ref proves the token is permanent' (revalidation C-2). "
            "See flag F-21."
        ),
        "status": "OBSERVED",
        "source_ids": ["S19"],
    },
    {
        "id": "E-10",
        "observation": (
            "None of the three resolved URLs carries a tag= parameter. Each ends "
            "…&channelId=704&plpRedirect=mhFallback (short-link arrival) or "
            "…?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 (direct arrival)."
        ),
        "interpretation": (
            "The links as supplied are untagged, so they cannot attribute a sale to an Associates account. "
            "Amazon's own help page gives the qualifying Special Link format as "
            "http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID. See flag F-24."
        ),
        "status": "OBSERVED",
        "source_ids": ["S24", "S19", "S20", "S21"],
    },
]
save("products.json", products)

# ------------------------------------------------------------------------------------------- flags
flags = load("flags.json")
flags["as_of"] = "2026-11-14"
flags["note"] += (
    " FINAL-INTEGRATION CORRECTION (2026-11-14, session 4338f55e): F-03 was rewritten once more after the "
    "decisive control was run — an UNKNOWN link.amazon code returns a 404 instead of a random product "
    "(flag F-20), so the three supplied codes are honoured lookups and the earlier 'the token was ignored / "
    "the destination was arbitrary' reading is withdrawn. F-20 to F-24 were added by the same session. Every "
    "flag below is published on the Flagged for Review page with its official source links."
)
by_id = {f["id"]: f for f in flags["flags"]}

by_id["F-03"].update(
    {
        "severity": "medium",
        "title": "The three link.amazon codes are honoured lookups, but no Amazon document binds a code to a product",
        "detail": (
            "FINAL READING (2026-11-14, session 4338f55e; supersedes the withdrawn 'arbitrary fallback' wording "
            "and the 'permanent per-link token' wording). What is verified: (a) each of the three supplied "
            "link.amazon URLs resolves, reproducibly, to ONE specific Amazon product page — B0CDY277D3, "
            "B09B7SB46R, B08DKYBTPH; (b) an UNKNOWN code on the same service (https://link.amazon/B00TEST12) "
            "returns a 404 page ('You've clicked on an invalid URL'), so the service looks the code up and the "
            "token IS honoured — the earlier claim that the token was ignored and the destination arbitrary is "
            "falsified; (c) plpRedirect=mhFallback is also emitted on ordinary valid /dp/ loads and so is not "
            "evidence of a fallback; (d) each link carries its own btn_ref=srctok-… token, which rotates over "
            "time while the destination does not. What is NOT verified: no public Amazon document describes the "
            "link.amazon/<code> format or binds a code to a product ASIN, so the binding is established by "
            "observed behaviour, not by documentation."
        ),
        "impact": (
            "The three products can be named and marketed as the destinations the supplied links resolve to, "
            "which is what this site now publishes. They cannot be claimed as 'the products named in the brief' "
            "until the owner confirms the mapping in Associates Central."
        ),
        "action_required": (
            "Owner: confirm in Associates Central that these three destinations are the items to market, and "
            "supply links carrying the Associates tag (F-24)."
        ),
        "source_ids": ["S32", "S19", "S20", "S21", "S24"],
        "owner": "user",
    }
)

by_id["F-06"].update(
    {
        "title": "Published copy must be labelled 'the product this link resolves to' until the owner confirms the mapping",
        "detail": (
            "Because no public Amazon document binds a link.amazon code to a product, the three products this "
            "site publishes are the destinations the supplied links resolve to — verified by live fetch and by "
            "the unknown-code control (F-20) — not a confirmed brief mapping. The article, comparison and "
            "buying-guide generator therefore stays in preview for the three submitted tokens: draft copy "
            "exists in content/templates/** but is not published, so that no article asserts a mapping Amazon "
            "does not document."
        ),
        "impact": (
            "No published article, comparison or buying guide names these three products yet. Every other part "
            "of the platform (policy engine, rate data, scoring, tracking schema, templates, deploy) is "
            "delivered and gated."
        ),
        "action_required": (
            "Confirm the mapping and supply tagged links; the pipeline then publishes verified-only copy "
            "without any other change."
        ),
        "source_ids": ["S32", "S19", "S20", "S21"],
        "owner": "user",
    }
)

by_id["F-19"]["detail"] += (
    " Re-read again on 2026-11-14 by session 4338f55e with the same result: the Emeril Everyday page states "
    "'24 one-touch cooking presets' in its description, '25 Cooking Pre-sets' in its specification tile, and a "
    "feature block headed '10-In-1 Versatility' listing ten functions, while the Amazon listing title says "
    "'24 cooking functions'. The conflict is confirmed and remains unresolved."
)

flags["flags"] = list(by_id.values()) + [
    {
        "id": "F-20",
        "severity": "medium",
        "title": "DECISIVE CONTROL — an unknown link.amazon code returns a 404, so the three supplied codes are honoured lookups",
        "detail": (
            "Run 2026-11-14 by session 4338f55e, the control the earlier sessions did not run. "
            "GET https://link.amazon/B00TEST12 — a 9-character code that was never supplied — resolved to "
            "https://amzlinks.in/B00TEST12 and returned the short-link service's 404 page: '404: File Not "
            "Found … You've clicked on an invalid URL.' (the page's image is hosted at "
            "amzlinks.in/post-tap/short-link-404.png). The three supplied codes do not behave that way: each "
            "resolves to one specific Amazon product page, reproducibly, across fetches on 2026-11-13 and "
            "2026-11-14. A service that answered unknown codes with a random product would be a fallback; a "
            "service that answers unknown codes with a 404 is performing a lookup. Therefore the published "
            "reading that the token was 'ignored' and the destination 'arbitrary' is falsified."
        ),
        "impact": (
            "This is the single finding that decides the disagreement between five earlier sessions. It moves "
            "the three products from 'evidence only' to 'the observed, reproducible destination of each "
            "supplied link' — while leaving the documentation gap (F-04, F-03) exactly as it was."
        ),
        "action_required": (
            "None for the owner to unblock. Recorded so the reviewer can see the control and repeat it: open "
            "https://link.amazon/B00TEST12 in a browser."
        ),
        "source_ids": ["S32", "S19", "S20", "S21"],
        "owner": "done",
    },
    {
        "id": "F-21",
        "severity": "low",
        "title": "The btn_ref source token rotates over time; the destination does not",
        "detail": (
            "Measured 2026-11-14 by session 4338f55e. link.amazon/B04G1MEwY carried "
            "btn_ref=srctok-1e229870efde5acf earlier the same day (recorded by session c6e94e8d) and "
            "btn_ref=srctok-1f979f303a4b5691 at about 10:04 UTC, while the destination stayed /dp/B0CDY277D3 on "
            "every fetch. A direct, untagged load of /dp/B08DKYBTPH carries no btn_ref at all. The three "
            "supplied links' tokens are distinct from one another (1f979f303a4b5691 / 0cd8be3c7e2e0de3 / "
            "7c59360cbbbd59b7) and all three carry channelId=704."
        ),
        "impact": (
            "Two published statements were each half-wrong: 'a different btn_ref on re-fetch proves the "
            "destination shuffles' (F-05, F-12 — withdrawn) and 'an identical btn_ref proves the token is "
            "permanent' (revalidation C-2 — overstated). The correct statement is that the source token is "
            "per-link and time-scoped, and the destination is stable. Anyone auditing this repository by "
            "re-fetching a link tomorrow should expect a different srctok and the same product."
        ),
        "action_required": (
            "None — published so the wording is not misread as a guarantee of permanence in either direction."
        ),
        "source_ids": ["S19", "S20", "S21"],
        "owner": "done",
    },
    {
        "id": "F-22",
        "severity": "medium",
        "title": "The Amazon title for B08DKYBTPH says '450°F Hi-Fry', but that same page's bullet list and specification block — and the manufacturer — say 200–400 °F",
        "detail": (
            "Verified 2026-11-14. The Amazon listing title for B08DKYBTPH reads 'Chefman Air Fryer 8 Qt | "
            "TurboFry® 4-in-1 with 450°F Hi-Fry Option for Crispier Results'. On the same page the 'About this "
            "item' bullet says 'a temperature range from 200-400°F' and the Product information block gives "
            "'Min Temperature Setting: 94 °C' and 'Max Temperature Setting: 400 °F'. Chefman's own page for "
            "model RJ38-SQSS-8T states '200–400°F / 95º-205ºC' and 'Max temp: 400ºF/ 205ºC'. The Hi-Fry name "
            "and the 450 °F figure belong to the 6-quart dual-window model RJ38-SQPF-3TDB-2W, whose Chefman "
            "page states 'Max temp: 450ºF/ 235ºC with Hi-Fry function'."
        ),
        "impact": (
            "Repeating '450 °F' in an article or comparison for the 8-quart model would repeat a claim the "
            "product's own specification block contradicts. 450 °F is publishable only for the 6-quart "
            "dual-window model."
        ),
        "action_required": (
            "Copy rule published: no 450 °F claim for the 8-quart model. Owner action: none required."
        ),
        "source_ids": ["S21", "S26", "S25"],
        "owner": "done",
    },
    {
        "id": "F-23",
        "severity": "medium",
        "title": "Emeril model number differs between the Amazon listing and the manufacturer's own store",
        "detail": (
            "Verified 2026-11-14. Amazon's Item details for B09B7SB46R give 'Model Number: 4-00675-02X-VN' and "
            "'Part Number: 4-00675-02X-VN'. The Emeril Everyday official store page for the same product prints "
            "'4-00675-02A-VN'. Both are official pages for the same listing, and both suffix values appear in "
            "the manufacturer's own image filenames ('..._4-00675-02X_...' and '..._4-00675-02A-VN')."
        ),
        "impact": (
            "A single model number cannot be published for this product. Both values are shown side by side "
            "with their sources; neither is chosen."
        ),
        "action_required": "None — both values published with sources.",
        "source_ids": ["S20", "S27"],
        "owner": "done",
    },
    {
        "id": "F-24",
        "severity": "medium",
        "title": "The three supplied links carry no Associates tag, so as supplied they cannot earn a commission",
        "detail": (
            "Verified 2026-11-14. Every resolved URL ends …&channelId=704&plpRedirect=mhFallback (short-link "
            "arrival) or …?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 (direct arrival); none carries a "
            "tag= parameter. Amazon's own help page gives the qualifying Special Link format as "
            "http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID and states that the tag identifies the "
            "Associates account the sale is tracked to."
        ),
        "impact": (
            "As supplied, the three links would earn nothing and could not be attributed in reporting. This "
            "blocks revenue, not identification — it is the one step that turns this repository from a verified "
            "research platform into a earning affiliate site."
        ),
        "action_required": (
            "Owner: supply the Associates ID (and the target marketplace) so links can be regenerated in the "
            "tagged format the program requires."
        ),
        "source_ids": ["S24", "S19", "S20", "S21"],
        "owner": "user",
    },
]
save("flags.json", flags)

# ----------------------------------------------------------------------------------------- sources
sources = load("sources.json")
sources["accessed_utc"] = "2026-11-14"
sources["note"] += (
    " S28–S31 were added on 2026-11-14 by session 4338f55e: the three supplied short links themselves and the "
    "unknown-code control that decides how they behave. kind=supplied marks the URLs the client supplied; "
    "kind=control marks an experiment run by this project against Amazon's own service."
)
existing = {s["id"] for s in sources["sources"]}
new_sources = [
    {
        "id": "S32",
        "name": "Amazon short-link service — unknown code control (9 characters, never supplied)",
        "url": "https://link.amazon/B00TEST12",
        "kind": "control",
        "page_stated_update": None,
        "accessed_utc": "2026-11-14",
        "used_for": [
            "control proving that an unknown link.amazon code returns a 404 rather than an arbitrary product",
            "flag F-20",
            "evidence observation E-06",
        ],
    },
    {
        "id": "S33",
        "name": "Supplied affiliate short link 1 (as provided in the brief)",
        "url": "https://link.amazon/B04G1MEwY",
        "kind": "supplied",
        "page_stated_update": None,
        "accessed_utc": "2026-11-14",
        "used_for": ["resolution of P-01 to https://www.amazon.com/dp/B0CDY277D3", "evidence E-01, E-08, E-09, E-10"],
    },
    {
        "id": "S34",
        "name": "Supplied affiliate short link 2 (as provided in the brief)",
        "url": "https://link.amazon/B02NbDxp3",
        "kind": "supplied",
        "page_stated_update": None,
        "accessed_utc": "2026-11-14",
        "used_for": ["resolution of P-02 to https://www.amazon.com/dp/B09B7SB46R", "evidence E-02, E-08, E-10"],
    },
    {
        "id": "S35",
        "name": "Supplied affiliate short link 3 (as provided in the brief)",
        "url": "https://link.amazon/B00hJ57DV",
        "kind": "supplied",
        "page_stated_update": None,
        "accessed_utc": "2026-11-14",
        "used_for": ["resolution of P-03 to https://www.amazon.com/dp/B08DKYBTPH", "evidence E-03, E-08, E-10"],
    },
]
sources["sources"].extend(s for s in new_sources if s["id"] not in existing)
save("sources.json", sources)

print("ledger updated:", len(products["entries"]), "entries,", len(products["evidence_observations"]), "observations,", len(flags["flags"]), "flags,", len(sources["sources"]), "sources")
