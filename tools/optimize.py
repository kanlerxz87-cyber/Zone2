"""Campaign optimizer: evidence-gated rule engine.

Reads site-side click aggregates plus (when available) dated Associates report rows, and proposes actions.
The whole point of this module is what it refuses to do: with thin data it emits NO_ACTION with the reason,
rather than concluding that a niche "converts".  It can change placement, internal linking, coverage and
headline testing.  It can never edit product facts - those come from verified sources only (R-10).
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]

MIN_CLICKS_FOR_DECISION = 30  # operator-chosen floor; recorded so the threshold itself is auditable
PAYMENT_LAG_DAYS = 60  # S02 - commission income paid ~60 days after month end
SESSION_HOURS = 24  # S02 - attribution window


@dataclass
class Action:
    target: str
    kind: str
    rationale: str
    evidence: list[str]
    reversible: bool = True


def load_state() -> dict[str, Any]:
    clicks_path = REPO / ".local" / "clicks.agg.json"
    earnings_path = REPO / "data" / "associates_report.json"
    return {
        "clicks": json.loads(clicks_path.read_text()) if clicks_path.exists() else {},
        "earnings": json.loads(earnings_path.read_text()) if earnings_path.exists() else None,
    }


def ctr(clicks: int, impressions: int | None) -> float | None:
    if not impressions:
        return None  # never assume an impression denominator
    return round(clicks / impressions, 4)


def propose_actions(state: dict[str, Any], *, pages: dict[str, dict] | None = None) -> dict[str, Any]:
    clicks = state.get("clicks") or {}
    earnings = state.get("earnings")
    actions: list[Action] = []
    skipped: list[dict[str, str]] = []

    if not clicks:
        skipped.append(
            {
                "code": "NO_CLICK_DATA",
                "detail": (
                    "no click events recorded, so no page may be judged; the optimizer stays inert rather than "
                    "optimizing on assumptions"
                ),
            }
        )
    else:
        counts = [c.get("clicks", 0) for c in clicks.values()]
        median = statistics.median(counts) if counts else 0
        for key, row in clicks.items():
            n = row.get("clicks", 0)
            if n < MIN_CLICKS_FOR_DECISION:
                skipped.append(
                    {"code": "SAMPLE_TOO_SMALL", "detail": f"{key}: {n} clicks < {MIN_CLICKS_FOR_DECISION} required"}
                )
                continue
            if n >= max(MIN_CLICKS_FOR_DECISION, median * 2):
                actions.append(
                    Action(
                        target=row.get("page", key),
                        kind="duplicate_winning_position",
                        rationale=(
                            f"{n} clicks is >=2x the median ({median:.0f}) across tracked positions; replicate the "
                            "placement pattern on sibling pages and add an internal link to it"
                        ),
                        evidence=[f"clicks:{key}={n}", f"median={median:.0f}"],
                    )
                )
            elif n <= max(1, median / 4):
                actions.append(
                    Action(
                        target=row.get("page", key),
                        kind="retest_position",
                        rationale=f"{n} clicks vs median {median:.0f}; move the block above the fold and re-measure",
                        evidence=[f"clicks:{key}={n}", f"median={median:.0f}"],
                    )
                )

    if earnings is None:
        skipped.append(
            {
                "code": "NO_EARNINGS_REPORT",
                "detail": (
                    "conversion/earnings actions require a dated Associates report export; revenue-side decisions "
                    "are withheld until then (payments arrive ~60 days after month end, source S02)"
                ),
            }
        )
    else:
        for row in earnings.get("rows", []):
            if row.get("orders") and row.get("clicks") and row["clicks"] >= MIN_CLICKS_FOR_DECISION:
                conv = row["orders"] / row["clicks"]
                if conv < 0.005:
                    actions.append(
                        Action(
                            target=row.get("page", row.get("campaign", "?")),
                            kind="rewrite_intent",
                            rationale=f"conversion {conv:.2%} over {row['clicks']} clicks; re-align the page to the buying query",
                            evidence=[f"report:{row.get('period', 'unknown')}"],
                        )
                    )

    coverage = []
    for page, meta in (pages or {}).items():
        if meta.get("identity_verified") and not meta.get("has_comparison"):
            coverage.append(Action(target=page, kind="add_comparison", rationale="verified product without a comparison asset", evidence=["ledger:identity_verified"]))

    return {
        "generated_utc": _now(),
        "policy": {
            "min_clicks_for_decision": MIN_CLICKS_FOR_DECISION,
            "decision_scope": "placement, internal linking, coverage, headline tests - never product facts",
            "payment_lag_days": PAYMENT_LAG_DAYS,
            "session_hours": SESSION_HOURS,
        },
        "actions": [a.__dict__ for a in actions],
        "no_action_reasons": skipped,
        "counts": {"actions": len(actions), "skipped": len(skipped)},
    }


def _now() -> str:
    import time

    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_report(state_path: Path | None = None) -> Path:
    state = load_state() if state_path is None else json.loads(Path(state_path).read_text())
    out = REPO / ".local" / "optimizer_report.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(propose_actions(state), indent=2, sort_keys=True), encoding="utf-8")
    return out


if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(propose_actions(load_state()), indent=2, sort_keys=True))
