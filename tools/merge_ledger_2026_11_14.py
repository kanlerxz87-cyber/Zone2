#!/usr/bin/env python3
"""Reconcile session 4338f55e's ledger with session a133aa61's live re-verification.

Both sessions did a "final integration" pass and both extended the same ledger, so two
identifier spaces collided:

  * flag ids  — 4338f55e used F-20 for the decisive unknown-code control and F-21 for the
    btn_ref rotation; a133aa61 used F-20 for the btn_ref rotation and F-21 for the R-09
    compliance correction.
  * source ids — 4338f55e used S28-S31 for the unknown-code control and the three supplied
    short links; a133aa61 used S28-S31 for four Associates-program pages it re-read live.

This script resolves both collisions in favour of the ids already published in this
repository's generated pages (the ledger is the source of truth, and the pages are built
from it), while preserving every finding from both sessions:

  * a133aa61's F-20 (btn_ref rotation) is MERGED into 4338f55e's F-21, with a133aa61's
    live-observed srctok values added to the detail.
  * a133aa61's F-21 (R-09 compliance correction) becomes F-25.
  * a133aa61's S28-S31 (four Associates program pages) keep those ids, because
    ledger/verification.json rows V-33..V-50 already cite them; 4338f55e's S28-S31 move to
    S32-S35 and every reference to them is rewritten.

Run from the repository root after a merge that touches ledger/*.json:

    python3 tools/merge_ledger_2026_11_14.py
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "ledger"

MINE_SOURCE_REMAP = {"S28": "S32", "S29": "S33", "S30": "S34", "S31": "S35"}


def git_show(ref: str, path: str) -> dict:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=REPO)
    return json.loads(raw.decode("utf-8"))


def write(name: str, payload: dict) -> None:
    path = LEDGER / name
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote ledger/{name}")


def remap_sources(node):
    """Rewrite the source ids 4338f55e added, wherever they are referenced."""
    if isinstance(node, dict):
        return {k: (MINE_SOURCE_REMAP.get(v, v) if k == "source_id" or k == "source_ids" and isinstance(v, str)
                    else remap_sources(v)) for k, v in node.items()}
    if isinstance(node, list):
        if node and all(isinstance(x, str) for x in node):
            return [MINE_SOURCE_REMAP.get(x, x) for x in node]
        return [remap_sources(x) for x in node]
    return node


def merge_sources() -> None:
    mine = git_show("HEAD", "ledger/sources.json")
    theirs = git_show("MERGE_HEAD", "ledger/sources.json")

    mine_by_id = {s["id"]: s for s in mine["sources"]}
    theirs_by_id = {s["id"]: s for s in theirs["sources"]}

    merged = []
    for sid in sorted(set(mine_by_id) | set(theirs_by_id), key=lambda s: int(s[1:])):
        if sid in mine_by_id and sid in theirs_by_id and sid in MINE_SOURCE_REMAP:
            # A true collision: both sessions used S28-S31. a133aa61's four Associates-program
            # pages keep the ids (verification rows V-33..V-50 already cite them); 4338f55e's
            # control and supplied links are renumbered.
            merged.append(theirs_by_id[sid])
            src = dict(mine_by_id[sid])
            src["id"] = MINE_SOURCE_REMAP[sid]
            merged.append(src)
        elif sid in mine_by_id:
            merged.append(mine_by_id[sid])
        else:
            merged.append(theirs_by_id[sid])

    # The three destination listings are not "fallback" pages: the unknown-code control
    # (F-20) shows the service honours the code, so the old wording is corrected here.
    titles = {
        "S19": "Destination listing observed for supplied link 1 — B0CDY277D3 (CHEFMAN 6 Quart Dual Basket)",
        "S20": "Destination listing observed for supplied link 2 — B09B7SB46R (Emeril Lagasse 26QT French Door)",
        "S21": "Destination listing observed for supplied link 3 — B08DKYBTPH (Chefman 8 Qt TurboFry)",
    }
    for src in merged:
        if src["id"] in titles:
            src["title"] = titles[src["id"]]
        if src["id"] == "S32":
            src["publisher"] = "Amazon.com (short-link service link.amazon)"
            src["title"] = "Amazon short-link service — unknown code control (9 characters, never published)"

    merged.sort(key=lambda s: int(s["id"][1:]))
    payload = {
        "note": (
            mine["note"].split(" S28-S31 were added")[0].rstrip()
            + " S28-S31 were added 2026-11-14 by session a133aa61 during the final integration, when the"
            " governing Associates pages were re-read live; S32-S35 were added 2026-11-14 by session"
            " 4338f55e for the unknown-code control and the three supplied short links. The two sessions"
            " initially reused the same ids; tools/merge_ledger_2026_11_14.py resolved the collision so no"
            " id points at two different pages."
        ),
        "accessed_utc": "2026-11-14",
        "sources": merged,
    }
    write("sources.json", payload)


def merge_flags() -> None:
    mine = git_show("HEAD", "ledger/flags.json")
    theirs = git_show("MERGE_HEAD", "ledger/flags.json")
    theirs_by_id = {f["id"]: f for f in theirs["flags"]}

    flags = remap_sources(json.loads(json.dumps(mine["flags"])))
    by_id = {f["id"]: f for f in flags}

    # a133aa61's F-20 (btn_ref rotates across days) becomes evidence inside F-21, which is
    # the same finding: the destination is stable, the per-link token is not.
    f21 = by_id["F-21"]
    btn = theirs_by_id["F-20"]
    f21["title"] = (
        "The link-rewrite token (btn_ref) rotates between days while the destination ASIN does not — "
        "so the token is not a usable identity marker"
    )
    f21["detail"] = f21["detail"].rstrip() + (
        " Independent live re-fetch on 2026-11-14 by session a133aa61 recorded the same three"
        " destinations with different per-link tokens: link.amazon/B04G1MEwY carried"
        " btn_ref=srctok-1f979f303a4b5691 (earlier sessions recorded srctok-1e229870efde5acf),"
        " B02NbDxp3 carried srctok-0cd8be3c7e2e0de3 (earlier srctok-534f5e7952f396b2), and"
        " B00hJ57DV carried srctok-7c59360cbbbd59b7 (earlier srctok-76c3adaeb8708b44). Within a"
        " single day the token is stable; across days it is not."
    )
    f21["impact"] = f21["impact"].rstrip() + (
        " The ASIN, the page body and the channelId=704 parameter all reproduce across sessions"
        " and across days, so the destination findings stand; only the token's stability claim"
        " does not. Read btn_ref as evidence of a live redirect, never as an identifier."
    )
    f21["action_required"] = f21["action_required"].rstrip() + (
        " Do not use the btn_ref value as a stable identifier for anything. Confirm the three"
        " destinations in Associates Central and regenerate the links with the Associates tag."
    )
    f21["source_ids"] = sorted(set(f21.get("source_ids", [])) | {"S16", "S19", "S20", "S21"})

    # a133aa61's F-21 (the R-09 compliance correction) becomes F-25.
    r09 = dict(theirs_by_id["F-21"])
    r09["id"] = "F-25"
    r09["source_ids"] = ["S03", "S29"]  # S29 is the Participation Requirements page (a133aa61's id)
    flags.append(r09)

    payload = {
        "note": mine["note"].rstrip()
        + " MERGED 2026-11-14 (session 4338f55e): the live re-verification by session a133aa61 was"
        " adopted in full — its btn_ref finding is folded into F-21 with the observed token values, and"
        " its R-09 compliance correction is published as F-25. The two sessions had reused the flag ids"
        " F-20 and F-21 for different findings; the ids already published here were kept and the"
        " incoming flags were renumbered, so no id points at two different findings.",
        "as_of": "2026-11-14",
        "flags": flags,
    }
    write("flags.json", payload)


def merge_products() -> None:
    mine = git_show("HEAD", "ledger/products.json")
    theirs = git_show("MERGE_HEAD", "ledger/products.json")
    theirs_entry = {e["id"]: e for e in theirs["entries"]}
    theirs_obs = {o["id"]: o for o in theirs["evidence_observations"]}

    payload = remap_sources(json.loads(json.dumps(mine)))
    payload["verified_utc"] = "2026-11-14"

    why_blank = (
        "Token is 9 characters, so it is not a valid ASIN; the canonical /dp/ URL returns Amazon's"
        " Page Not Found page. The supplied short link does open one live listing, and that"
        " destination is stable across re-fetches, but no public Amazon document binds the short"
        " code to it (F-03), the per-link btn_ref token changes between days (F-21), and no"
        " resolved URL carries an Associates tag (F-24). No official record therefore identifies"
        " the intended product, so no attribute may be stated."
    )
    for entry in payload["entries"]:
        entry["why_blank"] = why_blank
        other = theirs_entry.get(entry["id"])
        if other:
            entry["flag_ids"] = sorted(set(entry.get("flag_ids", [])) | set(other.get("flag_ids", [])))

    for obs in payload["evidence_observations"]:
        other = theirs_obs.get(obs["id"])
        if other and other.get("interpretation"):
            obs["interpretation"] = other["interpretation"]

    payload["last_reverified_utc"] = "2026-11-14"
    payload["reverification_note"] = (
        "Session 4338f55e re-read the three supplied links and the three manufacturer pages on"
        " 2026-11-14; session a133aa61 re-read them independently with live outbound access on the"
        " same day. Both record the same three destinations. The unknown-code control (S32) shows the"
        " short-link service honours the code; the per-link btn_ref token rotates between days (F-21)."
    )
    write("products.json", payload)


def merge_compliance() -> None:
    path = LEDGER / "compliance.json"
    text = path.read_text(encoding="utf-8")
    # a133aa61's R-09 note cites its own F-21; in the merged register that finding is F-25.
    text = text.replace("(F-21).", "(F-25).")
    path.write_text(text, encoding="utf-8")
    print("wrote ledger/compliance.json")


def merge_verification() -> None:
    path = LEDGER / "verification.json"
    text = path.read_text(encoding="utf-8")
    # a133aa61's V-41..V-43 cite its F-20 (btn_ref rotation); in the merged register that is F-21.
    text = text.replace("(F-01, F-20).", "(F-01, F-21).")
    text = text.replace("(F-20)", "(F-21)")
    path.write_text(text, encoding="utf-8")
    print("wrote ledger/verification.json")


def main() -> int:
    merge_sources()
    merge_flags()
    merge_products()
    merge_compliance()
    merge_verification()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
