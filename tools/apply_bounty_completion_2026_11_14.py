"""T26 (session d3ce1c29, 2026-11-14) — complete the bounty transcription in ledger/commission_table.json.

Why this script exists
----------------------
`pages/commissions.html` carried a panel headed **"Bounty events (Special Commission Income)"**
containing 9 rows, introduced by the notice *"Transcribed row-by-row from Amazon's published
Associates Program Standard Commission Income Statement (S04)"*.

Re-reading S04 (https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ) on
2026-11-14 shows the page publishes **46** rows under "(a) Bounty Events" and a further **2** rows
under "(b) Bonus Events". The nine published rows were the first nine and were individually correct,
but the panel read as a complete transcription of the statement. That is the irregularity recorded as
flag **F-30**.

This script replaces the partial list with the full transcription and adds the Bonus Events block.
Every row keeps `source_id` **S04**. Nothing is inferred: each program name, action and rate below was
copied from the official page as rendered on 2026-11-14.

Run:  python3 tools/apply_bounty_completion_2026_11_14.py
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TABLE = REPO / "ledger" / "commission_table.json"
SOURCE_ID = "S04"

# (program, bounty action, published rate) — transcribed from S04, section (a) Bounty Events.
BOUNTIES: list[tuple[str, str, str]] = [
    ("Prime Free Trial", "Successful registration of a Free Trial", "$12.00"),
    ("Prime Paid Membership", "Successful purchase of a Membership", "$12.00"),
    ("Prime for Young Adults Trial", "Successful registration of a Trial", "$12.00"),
    ("Prime for Young Adults Paid Membership", "Successful purchase of a Membership", "$12.00"),
    ("Prime Access Free Trial or Paid Membership", "Successful registration of a Free Trial or purchase of a Membership", "$12.00"),
    ("Prime Sign Up at Checkout", "Successful registration or purchase during checkout for a product or Prime exclusive offer", "$12.00"),
    ("Prime Video Free Trial", "Successful registration of a Free Trial", "$2.00"),
    ("Prime Video First Stream", "Successful First Stream", "$5.00"),
    ("Prime Video Stream", "Successful Stream", "$0.25"),
    ("Prime Video Add-on Subscriptions - Free Trial", "Successful registration of a Free Trial", "$2.50"),
    ("Prime Video Add-on Subscriptions - Paid", "Successful purchase of a Subscription", "$3.00"),
    ("Audible Standard Free Trial", "Customer signs up for a free trial of the Audible Standard membership plan on Amazon", "$20.00"),
    ("Audible Premium Plus Free Trial", "Successful registration of a Free Trial on Amazon", "$5.00"),
    ("Audible Standard Monthly Membership", "Customer signs up for a the paid Audible Standard membership plan on Amazon", "$20.00"),
    ("Audible Premium Plus Annual Membership", "Successful purchase of a Membership on Amazon", "$25.00"),
    ("Audible Premium Plus Monthly Membership", "Successful purchase of a Membership on Amazon", "$10.00"),
    ("Audible Audiobook (cash purchase)", "Successful cash purchase of an Audible audiobook on Amazon", "$0.50"),
    ("Audible Gift Membership: 1-month plan", "Successful purchase of a Gift Membership on Amazon", "$5.00"),
    ("Audible Gift Membership: 3-month plan", "Successful purchase of a Gift Membership on Amazon", "$8.00"),
    ("Audible Gift Membership: 6-month plan", "Successful purchase of a Gift Membership on Amazon", "$8.00"),
    ("Audible Gift Membership: 12-month plan", "Successful purchase of a Gift Membership on Amazon", "$10.00"),
    ("Kindle Unlimited Free Trial", "Successful registration of a Free Trial", "$3.00"),
    ("Kindle Unlimited Special Promos", "Successful purchase of a Kindle Unlimited Special Promotion", "$3.00"),
    ("Kindle Unlimited Membership: 6-month plan", "Successful purchase of a Membership", "$3.00"),
    ("Kindle Unlimited Membership: 12-month plan", "Successful purchase of a Membership", "$5.00"),
    ("Kindle Unlimited Membership: 24-month plan", "Successful purchase of a Membership", "$10.00"),
    ("Amazon Music Unlimited Free Trial", "Successful registration of a Free Trial", "$3.00"),
    ("Amazon Music Unlimited Paid Subscription", "Successful purchase of a Subscription", "$3.00"),
    ("Amazon Music Unlimited Special Promotions", "Successful registration of a Free Trial", "$3.00"),
    ("Prime Music Free Trial", "Successful registration of a Free Trial", "$3.00"),
    ("Amazon Baby Registry Create", "Successful creation and addition of at least 1 item to an Amazon Baby Registry", "$3.00"),
    ("Amazon Wedding Registry Create", "Successful creation and addition of at least 1 item to an Amazon Wedding Registry", "$3.00"),
    ("EBT Card Registration", "Successful registration of EBT Card", "$2.00"),
    ("Snap EBT Purchase", "Successful purchase of SNAP/EBT eligible products on Amazon", "$0.50"),
    ("Amazon Business", "Successful registration of an Amazon Business account", "$15.00"),
    ("Amazon Kids+ Free Trial", "Successful registration of a Free Trial", "$3.00"),
    ("Amazon Kids+ Special Promotions", "Successful purchase of a Special Promotion", "$3.00"),
    ("Prime Exclusives", "Successful registration of a Free Trial", "$3.00"),
    ("Prime Gaming", "Successful registration of a Free Trial", "$3.00"),
    ("Amazon Haul", "Amazon Haul First Purchase", "$4.00"),
    ("Subscribe & Save - Beauty & Grooming", "Successful activation and 1st delivery of a Subscribe & Save subscription of a Beauty & Grooming product.", "$0.25"),
    ("Subscribe & Save - Grocery", "Successful activation and 1st delivery of a Subscribe & Save subscription of a Grocery product.", "$0.25"),
    ("Subscribe & Save - Health & Personal Care (HPC) excluding diapers", "Successful activation and 1st delivery of a Subscribe & Save subscription of an HPC excluding diapers product.", "$0.25"),
    ("Subscribe & Save - Pet food and supplies", "Successful activation and 1st delivery of a Subscribe & Save subscription of a pet food and supplies product.", "$0.25"),
    ("Subscribe & Save - Activation & Delivery", "Successful activation and 1st delivery of a Subscribe & Save subscription of an eligible Professional Beauty ASIN", "$0.25"),
    ("Subscribe & Save - Diapers", "Successful activation and 1st delivery of a diapers product.", "$0.25"),
]

# (program, bonus action, published rate) — transcribed from S04, section (b) Bonus Events.
BONUS_EVENTS: list[tuple[str, str, str]] = [
    ("Amazon Fresh Products", "Successful first purchase from the Amazon Fresh store", "$1.00"),
    ("Pet Food & Supplies", "Successful first purchase from the Amazon Pet Food & Supplies store", "$3.00"),
]

NOTE_ADDENDUM = (
    " BOUNTY COMPLETION (2026-11-14, session d3ce1c29, flag F-30): the 'Bounty events' panel originally "
    "published 9 rows under a 'transcribed row-by-row' notice, while S04 publishes 46 rows under "
    "'(a) Bounty Events' and a further 2 under '(b) Bonus Events'. The partial list was replaced with the "
    "full transcription and the Bonus Events block was added. The 9 original rows were individually correct; "
    "the defect was omission, not error."
)


def main() -> None:
    doc = json.loads(TABLE.read_text(encoding="utf-8"))
    doc["bounties"] = [
        {"program": p, "bounty_action": a, "rate": r, "source_id": SOURCE_ID} for p, a, r in BOUNTIES
    ]
    doc["bonus_events"] = [
        {"program": p, "bonus_action": a, "rate": r, "source_id": SOURCE_ID} for p, a, r in BONUS_EVENTS
    ]
    doc["note"] = doc["note"].rstrip() + NOTE_ADDENDUM
    TABLE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ledger/commission_table.json: {len(BOUNTIES)} bounty rows, {len(BONUS_EVENTS)} bonus rows")


if __name__ == "__main__":
    main()
