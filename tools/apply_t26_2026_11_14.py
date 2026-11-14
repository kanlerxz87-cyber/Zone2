"""T26 (session `arena/d3ce1c29-zone2`, 2026-11-14) — record this session's independent verification.

What this script writes (all additive, nothing deleted):

* `ledger/sources.json`      — adds S36 (Associates program home page), the URL the dashboard cites
                               for the "up to 10%" commission ceiling. It was cited directly in
                               index.html without a register entry.
* `ledger/verification.json` — adds V-51 … V-62, every check this session ran itself by re-reading
                               the official page, plus the three-ASIN replication of the
                               `plpRedirect=mhFallback` control (previously run for one ASIN only, V-45).
* `ledger/flags.json`        — adds F-30 (incomplete bounty/bonus transcription), F-31 (the
                               "nine category groups" caption matched no grouping in the source) and
                               F-32 (validate_data.py skipped rows carrying only `source_id`).

Run:  python3 tools/apply_t26_2026_11_14.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "ledger"

NEW_SOURCE = {
    "id": "S36",
    "publisher": "Amazon (Amazon.com Associates Central)",
    "kind": "official",
    "title": "Amazon Associates home page (program overview and FAQ)",
    "url": "https://affiliate-program.amazon.com/",
    "page_stated_update": None,
    "accessed_utc": "2026-11-14",
    "used_for": [
        "public commission ceiling — 'Earn up to 10% in associate commissions from qualifying purchases and programs.'",
        "payment timing FAQ — 'Commission income is paid approximately 60 days after the end of the month in which it was earned.'",
    ],
}

# id, subject, claim, method, verdict, source_ids, consequence
NEW_VERIFICATION_ROWS = [
    (
        "V-51",
        "OA-05 mandatory disclosure sentence",
        "The Operating Agreement requires the exact sentence 'As an Amazon Associate I earn from qualifying purchases.'",
        "re-read https://affiliate-program.amazon.com/help/operating/agreement §5 on 2026-11-14",
        "VERIFIED",
        ["S01"],
        "verbatim: 'You must clearly and prominently state the following … on your Site …: “As an Amazon Associate I earn from qualifying purchases.”' The sentence rendered at the top of every published page matches character for character.",
    ),
    (
        "V-52",
        "OA document currency",
        "The Operating Agreement states 'Updated: October 15, 2025'",
        "re-read the header of the Operating Agreement on 2026-11-14",
        "VERIFIED",
        ["S01"],
        "the document-currency row on the dashboard is current; no change needed.",
    ),
    (
        "V-53",
        "Table 1 fixed commission bands",
        "Table 1 publishes eleven fixed bands from 10.00% down to 0.00%, plus 'All Other Categories 4.00%'",
        "re-read https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ on 2026-11-14 and compared each band with ledger/commission_table.json",
        "VERIFIED",
        ["S04", "S28"],
        "all eleven bands match the transcription exactly and in order: 10.00 / 5.00 / 4.50 / 4.00 / 3.00 / 2.50 / 2.00 / 1.00 / 0.00 (exclusions) / 0.00 (Coach) / 4.00 (All Other Categories).",
    ),
    (
        "V-54",
        "ASIN length and Special Link format",
        "An ASIN is a 10-character code and a qualifying simple text link has the form http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID",
        "re-read https://affiliate-program.amazon.com/help/node/topic/GP38PJ6EUR6PFBEC on 2026-11-14",
        "VERIFIED",
        ["S24", "S16", "S17", "S18"],
        "verbatim: 'ASIN is the 10-digit code that Amazon uses to denote specific products.' Basis of F-01 stands: the three supplied 9-character codes cannot address a catalog record.",
    ),
    (
        "V-55",
        "Public commission ceiling and payment timing",
        "Amazon publicly states 'up to 10%' commission and payment 'approximately 60 days after the end of the month'",
        "re-read https://affiliate-program.amazon.com/ on 2026-11-14",
        "VERIFIED",
        ["S36"],
        "verbatim: 'Earn up to 10% in associate commissions from qualifying purchases and programs.' and 'Commission income is paid approximately 60 days after the end of the month in which it was earned.' S36 was added to the source register: the dashboard cited this URL without a register entry.",
    ),
    (
        "V-56",
        "CONTROL-02 is plpRedirect=mhFallback specific to the supplied short links? (ASIN B0CDY277D3)",
        "plpRedirect=mhFallback appears only when a link.amazon short link is followed, so it marks a fallback",
        "fetched a bare, untagged https://www.amazon.com/dp/B0CDY277D3 on 2026-11-14 — no short link, no parameters",
        "REFUTED",
        ["S19"],
        "the plain /dp/ URL returned the same product and the final URL carried ?lv=shuf&channelId=500&plpRedirect=mhFallback. Amazon's own redirector emits the marker on an ordinary product load, so it is not evidence of a fallback. Replicates V-45, which ran this control for B08DKYBTPH only.",
    ),
    (
        "V-57",
        "CONTROL-03 same control for ASIN B09B7SB46R",
        "plpRedirect=mhFallback appears only when a link.amazon short link is followed",
        "fetched a bare, untagged https://www.amazon.com/dp/B09B7SB46R on 2026-11-14",
        "REFUTED",
        ["S20"],
        "final URL https://www.amazon.com/dp/B09B7SB46R?lv=shuf&channelId=500&plpRedirect=mhFallback — the marker is emitted without any short link. Control now reproduced on all three destination ASINs.",
    ),
    (
        "V-58",
        "CONTROL-04 same control for ASIN B08DKYBTPH (replication of V-45)",
        "plpRedirect=mhFallback appears only when a link.amazon short link is followed",
        "fetched a bare, untagged https://www.amazon.com/dp/B08DKYBTPH on 2026-11-14",
        "REFUTED",
        ["S21"],
        "final URL https://www.amazon.com/dp/B08DKYBTPH?lv=shuf&channelId=500&plpRedirect=mhFallback&th=1 — identical result to V-45, independently re-run in this session.",
    ),
    (
        "V-59",
        "CONTROL-05 unknown-code control reproduced",
        "An unknown 9-character link.amazon code returns a 404 rather than a random product, proving the supplied codes are looked up",
        "fetched https://link.amazon/B00TEST12 on 2026-11-14",
        "VERIFIED",
        ["S32"],
        "redirects to https://amzlinks.in/B00TEST12 and renders '404: File Not Found … You've clicked on an invalid URL.' Independently reproduced in this session; the control behind F-03 / F-20 holds.",
    ),
    (
        "V-60",
        "SUPPLIED-01 the three supplied links re-resolved in this session",
        "Each supplied short link still resolves to the same single Amazon listing, while its per-link token changes",
        "fetched all three supplied link.amazon URLs on 2026-11-14 and recorded the final URL and page title",
        "VERIFIED",
        ["S33", "S34", "S35", "S19", "S20", "S21"],
        "B04G1MEwY → /dp/B0CDY277D3 (btn_ref=srctok-704dc575b940a94c) 'CHEFMAN 6 Quart Dual Basket Air Fryer Oven with Easy View Windows…'; B02NbDxp3 → /dp/B09B7SB46R (btn_ref=srctok-76d4981d5f44181b) 'Emeril Lagasse 26QT French Door Multi-Function Air Fryer Toaster Oven…'; B00hJ57DV → /dp/B08DKYBTPH (btn_ref=srctok-016f4a534eed3621) 'Chefman Air Fryer 8 Qt | TurboFry 4-in-1…'. Destinations unchanged; all three btn_ref values differ from every value recorded by earlier sessions the same day — F-21 confirmed again, and the three links carry three distinct tokens at one moment.",
    ),
    (
        "V-61",
        "RATE-01 how many bounty and bonus rows does S04 publish?",
        "The site's 'Bounty events' table (9 rows) is the full set of Special Commission Income events",
        "re-read the whole of https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ on 2026-11-14, sections (a) and (b)",
        "REFUTED",
        ["S04", "S28"],
        "S04 publishes 46 rows under '(a) Bounty Events' and 2 further rows under '(b) Bonus Events' (Amazon Fresh Products $1.00; Pet Food & Supplies $3.00). The 9 published rows were the first nine and were individually correct — the defect was omission. Recorded as F-30 and corrected by tools/apply_bounty_completion_2026_11_14.py.",
    ),
    (
        "V-62",
        "RATE-02 special-rate and limitation terms re-read",
        "The Trade-In rates, the $200 fine-art cap and the free-Kindle-book limitation are as published on the site",
        "re-read sections (c) and 'Commission Income Limitations' of S04 on 2026-11-14",
        "VERIFIED",
        ["S04"],
        "Trade-In: Trade Books and Textbooks 4.00%, Consumer Electronics Products 4.00%, Video Games Products 0.00%. Fine art: 'limited to a maximum of $200 per Product'. Free books: no Standard or Special Commission Income for a month with ≥20,000 free Kindle eBook orders and ≥80% free share. All three match the published rows.",
    ),
]

NEW_FLAGS = [
    {
        "id": "F-30",
        "severity": "medium",
        "owner": "done",
        "title": "The bounty table published 9 of the 46 bounty events, and none of the 2 bonus events, under a 'transcribed row-by-row' notice",
        "detail": (
            "Found 2026-11-14 by session d3ce1c29. pages/commissions.html carried a panel headed "
            "'Bounty events (Special Commission Income)' with nine rows, introduced by the notice "
            "'Transcribed row-by-row from Amazon's published Associates Program Standard Commission Income "
            "Statement (S04)'. Re-reading S04 in full shows it publishes 46 rows under '(a) Bounty Events' "
            "(Prime, Prime Video, Audible, Kindle Unlimited, Amazon Music, registries, EBT, Amazon Business, "
            "Amazon Kids+, Prime Gaming, Amazon Haul and six Subscribe & Save rows) and a further 2 rows under "
            "'(b) Bonus Events'. The nine rows that were published were individually correct and correctly "
            "sourced — the defect was omission, not error, but a partial list carrying a completeness claim "
            "reads as the whole set."
        ),
        "impact": (
            "A revenue model that can see only 9 of 48 special-income events systematically under-prices the "
            "non-product revenue a site can earn. Audible ($20.00) and Amazon Business ($15.00) are the two "
            "largest published bounty rates and neither was on the page."
        ),
        "action_required": (
            "None open. ledger/commission_table.json now holds all 46 bounty rows and a new 'bonus_events' "
            "block with the 2 bonus rows; pages/commissions.html renders both and states the counts. Applied "
            "by tools/apply_bounty_completion_2026_11_14.py."
        ),
        "status": "closed",
        "source_ids": ["S04", "S28"],
        "published_on": "pages/commissions.html + pages/flags.html",
    },
    {
        "id": "F-31",
        "severity": "low",
        "owner": "done",
        "title": "The zero-rate caption said 'Nine category groups publish a 0.00% Standard Commission rate', which matches no grouping in the source",
        "detail": (
            "Found 2026-11-14 by session d3ce1c29. Table 1 of S04 publishes eleven bands, of which exactly two "
            "are 0.00%: the exclusion block and Coach, which Amazon lists on its own row. 'Nine' corresponds to "
            "no count in the source — eight semicolon-separated groups in the exclusion block plus Coach is the "
            "closest reading, but that count depends on how the final group "
            "('Amazon Appstore, Prime Now, or Amazon Pay Places') is split."
        ),
        "impact": "A reader checking the claim against Table 1 cannot reconcile it, which undermines trust in the rows that are correct.",
        "action_required": "None open. The caption now names the two 0.00% bands and lists what is in the exclusion block.",
        "status": "closed",
        "source_ids": ["S04"],
        "published_on": "pages/commissions.html + pages/flags.html",
    },
    {
        "id": "F-32",
        "severity": "low",
        "owner": "done",
        "title": "tools/validate_data.py skipped any ledger row whose only source field is 'source_id' (singular)",
        "detail": (
            "Found 2026-11-14 by session d3ce1c29. check_rows() walks the ledger and yields a dict as a row only "
            "if it contains 'source_ids' or 'id'. Every commission-table row (bands, bounty rows, bonus rows, "
            "statement terms) uses the singular 'source_id' and has no 'id', so those rows were never counted and "
            "never held to the 'a row that carries a value must carry a source' rule. Completing the bounty table "
            "would have added 48 unchecked rows."
        ),
        "impact": "The gate could not fail on an unsourced rate row — precisely the failure mode F-30 was.",
        "action_required": (
            "None open. _walk_rows now also yields on 'source_id'; the gate's row count rose from 173 to 228 and "
            "passes. Negative check: reverting the one-line change lowers the count to 173, so the new rows are "
            "really being walked."
        ),
        "status": "closed",
        "source_ids": ["S04"],
        "published_on": "pages/flags.html",
    },
]


def main() -> None:
    # --- sources -------------------------------------------------------------
    src_path = LEDGER / "sources.json"
    doc = json.loads(src_path.read_text(encoding="utf-8"))
    ids = {s["id"] for s in doc["sources"]}
    if NEW_SOURCE["id"] not in ids:
        doc["sources"].append(NEW_SOURCE)
        doc["note"] = doc["note"].rstrip() + (
            " S36 was added 2026-11-14 by session d3ce1c29: the Associates home page was cited directly by the "
            "dashboard for the 'up to 10%' ceiling and the 'approximately 60 days' payment statement but had no "
            "register entry, so the citation was not covered by the source register."
        )
        src_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("sources.json: added S36")

    # --- verification --------------------------------------------------------
    ver_path = LEDGER / "verification.json"
    doc = json.loads(ver_path.read_text(encoding="utf-8"))
    rows = doc.setdefault("rows", [])
    have = {r["id"] for r in rows}
    added = 0
    for vid, subject, claim, method, verdict, sids, consequence in NEW_VERIFICATION_ROWS:
        if vid in have:
            continue
        rows.append(
            {
                "id": vid,
                "subject": subject,
                "claim": claim,
                "method": method,
                "verdict": verdict,
                "source_ids": sids,
                "consequence": consequence,
            }
        )
        added += 1
    doc["note"] = doc["note"].rstrip() + (
        " Rows V-51..V-62 were added 2026-11-14 by session d3ce1c29 (T26): an independent re-read of the "
        "governing Amazon pages, the three-ASIN replication of the plpRedirect=mhFallback control (previously "
        "run for one ASIN only, V-45), a live re-resolution of all three supplied links, and the row count of "
        "S04's bounty and bonus tables."
    )
    ver_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"verification.json: added {added} rows (V-51..V-62)")

    # --- flags ---------------------------------------------------------------
    flg_path = LEDGER / "flags.json"
    doc = json.loads(flg_path.read_text(encoding="utf-8"))
    flags = doc.setdefault("flags", [])
    have = {f["id"] for f in flags}
    added = 0
    for flag in NEW_FLAGS:
        if flag["id"] not in have:
            flags.append(flag)
            added += 1
    doc["note"] = doc["note"].rstrip() + (
        " F-30 to F-32 were added 2026-11-14 by session d3ce1c29 (T26) and are all closed in the same session: "
        "an incomplete bounty/bonus transcription presented as complete, a zero-rate caption whose count matched "
        "no grouping in the source, and a gap in validate_data.py that let every commission-table row escape the "
        "source check."
    )
    flg_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"flags.json: added {added} flags (F-30..F-32)")


if __name__ == "__main__":
    main()
