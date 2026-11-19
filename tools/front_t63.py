#!/usr/bin/env python3
"""Reader-first content for the front of house — T63, session `arena/10727edd-zone2` (2026-11-19).

WHY THIS FILE EXISTS
--------------------
The 2026-11-19 brief: "Lead with the products, not with the verification process", "make it read
like a shop, not an audit", and "publish question-shaped guides". Two of the five supplied links
resolve to meat thermometers (P-04, P-05) and, until this session, neither had a single
reader-facing page — they appeared only in audit and operator registers.

This module holds the data and copy for:
  * the two thermometers, loaded from `ledger/products.json` (P-04 / P-05 `resolved.specs`) and
    `ledger/sources.json` (S61 / S62) — every value is READ, never retyped here;
  * the USDA FSIS safe-minimum-temperature rows (re-read live 2026-11-19, source URL below);
  * four question-shaped guides, one per editorial hypothesis in the brief that did not already
    have a page, plus the thermometer category page.

RULES THIS FILE KEEPS (enforced by tools/verify_front.py)
  * every table row ends in a link to the official page that states it, or a dash with a reason;
  * no price, no rating, no review count, no promotion (the listings show "Early Black Friday
    Deal" banners; the Program Policies require promotion mentions to be removed when the
    promotion ends, so none is ever repeated here);
  * every product link is a tagged Special Link built by tools/link_builder.py, marked
    rel="sponsored nofollow" and labelled "(paid link)";
  * the observed destination of a supplied short link is NOT asserted to be the product the
    owner intended (F-06 / Q-T50-01) — the pages say "the listing the supplied link opens".
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = "2026-11-19"

FSIS_URL = ("https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/"
            "food-safety-basics/safe-temperature-chart")
FSIS_NAME = "USDA FSIS — Safe Minimum Internal Temperature Chart"
# Transcribed verbatim from FSIS_URL on 2026-11-19 (page footer: "Last Updated: Apr 14, 2025").
# Only the rows the guides use are carried; nothing is paraphrased into a different number.
FSIS_ROWS = [
    ("All poultry (breasts, whole bird, legs, thighs, wings, ground poultry, giblets, stuffing)",
     "165 °F (73.9 °C)"),
    ("Ground meats", "160 °F (71.1 °C)"),
    ("Beef, pork, veal and lamb steaks, chops and roasts",
     "145 °F (62.8 °C) and rest at least 3 minutes"),
    ("Fish & shellfish", "145 °F (62.8 °C)"),
    ("Leftovers", "165 °F (73.9 °C)"),
]
FSIS_QUOTE = ("Cook all food to these minimum internal temperatures, as measured with a food "
              "thermometer, before removing food from the heat source.")

# Observed live on the ThermoMaven listing 2026-11-19 (S61): "There is a newer model of this item"
# pointing at B0GL7Z4KP4. Recorded as flag F-44; nothing is inferred about the newer model.
NEWER_MODEL_ASIN = "B0GL7Z4KP4"

THERMO_VOICE = {
    "P4": {
        "ledger_id": "P-04",
        "display": "ThermoMaven 1 Sec Professional Digital Meat Thermometer",
        "short": "ThermoMaven instant-read",
        "brand": "ThermoMaven",
        "headline": "A one-second read you can take anywhere",
        "note": "Stab it in, read it, wipe it off. Runs on one AAA battery, which is in the box.",
        "highlights": ["Response time", "Accuracy", "Upper temperature range", "Power source",
                       "Specification met"],
        "kind": "Instant-read",
    },
    "P5": {
        "ledger_id": "P-05",
        "display": "CHEF iQ Sense Smart Wireless Meat Thermometer (3 probes)",
        "short": "CHEF iQ Sense wireless",
        "brand": "CHEF iQ",
        "headline": "Three probes that stay in while you walk away",
        "note": "Leave-in probes that report to your phone over WiFi, so a long roast does not need you standing at the oven door.",
        "highlights": ["Probes included", "Connectivity", "Heat safety", "Sensors", "Accuracy"],
        "kind": "Leave-in wireless",
    },
}


def e(s: object) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def host_of(url: str) -> str:
    return re.sub(r"^www\.", "", re.sub(r"^https?://", "", url).split("/")[0])


def load_thermometers() -> dict[str, dict]:
    """Return P4/P5 in the same shape marketing/data/facts.json uses for P1..P3.

    Values come from ledger/products.json `resolved.specs`; the source URL from ledger/sources.json.
    A spec whose ledger status is 'conflict' keeps that status, so it renders with a conflict pill.
    """
    products = json.loads((ROOT / "ledger" / "products.json").read_text(encoding="utf-8"))
    sources = {s["id"]: s for s in
               json.loads((ROOT / "ledger" / "sources.json").read_text(encoding="utf-8"))["sources"]}
    by_id = {p["id"]: p for p in products["entries"]}
    out: dict[str, dict] = {}
    for key, voice in THERMO_VOICE.items():
        entry = by_id[voice["ledger_id"]]
        res = entry["resolved"]
        src_ids = res["source_ids"]
        official = [{"id": sid, "name": f"Amazon listing {res['asin']}", "url": sources[sid]["url"]}
                    for sid in src_ids]
        rows = []
        for spec in res["specs"]:
            sid = (spec.get("source_ids") or [None])[0]
            rows.append({
                "attr": spec["attribute"],
                "value": spec["value"],
                "status": spec.get("status", "unverified"),
                "src": sid if sid in sources else None,
                "blank_reason": None if sid else "No official source states this value.",
            })
        # The listing never states these; printed as explicit blanks, never estimated.
        rows.append({"attr": "Price", "value": "", "status": "withheld_by_policy", "src": None,
                     "blank_reason": "Not displayed: the Associates Program Policies limit price display to Amazon-served or API-sourced data."})
        rows.append({"attr": "Star rating / review count", "value": "", "status": "withheld_by_policy",
                     "src": None, "blank_reason": "Not displayed: no first-party data feed is connected."})
        out[key] = {
            "key": key,
            "asin": res["asin"],
            "model": "",
            "title": res["title"],
            "observed_utc": res.get("observed_utc", ""),
            "official_sources": official,
            "rows": rows,
            "intent_status": entry.get("intent_confirmation", {}).get("intent_status", "UNCONFIRMED"),
            "submitted_url": entry["submitted_url"],
        }
    return out


def jsonld_article(rel_path: str, headline: str, description: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "datePublished": TODAY,
        "dateModified": TODAY,
        "mainEntityOfPage": "https://kanlerxz87-cyber.github.io/Zone2/" + rel_path,
        "author": {"@type": "Organization", "name": "Counter Notes"},
        "publisher": {"@type": "Organization", "name": "Counter Notes"},
        "image": "https://kanlerxz87-cyber.github.io/Zone2/assets/img/hero-counter.jpg",
    }
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + "</script>")


# --------------------------------------------------------------------------- #
# The new guides. (slug, kicker, title, dek, category). Bodies are built in build_front.py,
# where the table helpers and the link builder live.
# --------------------------------------------------------------------------- #
NEW_GUIDES = [
    ("instant-read-or-wireless-thermometer", "Thermometers",
     "Instant-read or leave-in wireless: which meat thermometer fits the way you cook?",
     "One is a pocket tool you stab in and read. The other stays in the meat and pings your phone. They solve different problems, and the listings say which.",
     "meat-thermometers"),
    ("thermometer-for-air-fryer", "Food safety",
     "Do you need a meat thermometer for an air fryer? What the USDA chart says",
     "An air fryer's dial sets the temperature of the air, not of the chicken. The federal chart is written in internal temperatures, which only a thermometer can read.",
     "meat-thermometers"),
    ("multi-function-appliance-questions", "Checklist",
     "Seven questions to ask before buying a multi-function kitchen appliance",
     "Ten modes sounds like ten appliances. Before you clear the counter, here is how to tell which of them you will actually use, and which number on the box to trust.",
     "air-fryer-ovens"),
    ("cleanup-and-counter-space", "Fit & cleanup",
     "How to judge cleanup and counter space before you buy",
     "The machine you return is rarely the one that cooked badly. It is the one that did not fit under the cabinet or that nobody wanted to wash. Measure these first.",
     "buying-guides"),
]
