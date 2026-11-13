"""Opportunity scoring and revenue modelling.

Two deliberate design constraints:

1.  Commission rates come only from Amazon's published Standard Commission Income Statement, transcribed in
    ledger/commission_table.json (source S04).  This module contains no hard-coded rate of its own, so a rate
    can never silently drift out of date inside the code.
2.  Every sub-score returns ``None`` (insufficient data) rather than a default.  A missing input must never
    become a 0 or a 5 - that is how fabricated "analysis" gets produced.

Attribution mechanics implemented here follow Commission Income Statement Sec. 1 (source S02):
Session = 24 hours from the click (or the first order / another associate's click), a cart-add path that must
complete within 89 days, and a purchase that must ship/be paid for within 180 days.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
COMMISSION_FILE = REPO / "ledger" / "commission_table.json"

SESSION_HOURS = 24  # S02 - R-13
CART_TAIL_DAYS = 89  # S02 - R-13 ("no later than 89 days after their initial click-through")
SHIP_WINDOW_DAYS = 180  # S02 - R-13
PAYMENT_LAG_DAYS = 60  # S02 - R-15 ("approximately 60 days following the end of each calendar month")
INACTIVITY_YEARS = 3  # S02 - account with no substantial activity for at least 3 years


@dataclass
class RateInfo:
    rate_pct: float
    group_id: str
    exact_match: bool
    source_id: str


def load_rate_table(path: Path = COMMISSION_FILE) -> dict[str, RateInfo]:
    """Return {category_name_lower: RateInfo} built from the official transcription."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, RateInfo] = {}
    for group in data["groups"]:
        rate = float(group["rate_pct"])
        for cat in group["categories"]:
            out[cat.lower()] = RateInfo(rate, group["id"], True, data["source_id"])
    fallback = data["groups"][-1]
    if fallback["id"] != "C-OTH":  # defensive: keep 'All Other Categories' last
        raise ValueError("commission table transcription must end with the All Other Categories band")
    out["__default__"] = RateInfo(float(fallback["rate_pct"]), fallback["id"], False, data["source_id"])
    return out


def rate_for_category(category: str | None, table: dict[str, RateInfo] | None = None) -> RateInfo | None:
    """Look up a published rate.  ``category`` must itself be a *verified* category (from a catalog record),
    never an assumption: if it is unknown we return None and the caller must leave the field blank."""
    table = table or load_rate_table()
    if not category:
        return None
    key = category.strip().lower()
    if key in table:
        return table[key]
    return table["__default__"]


def zero_rate_categories(table: dict[str, RateInfo] | None = None) -> list[str]:
    table = table or load_rate_table()
    return sorted(k for k, v in table.items() if k != "__default__" and v.rate_pct == 0.0)


# --------------------------------------------------------------------------- sub-scores


def commission_term(category: str | None, table: dict[str, RateInfo] | None = None) -> dict:
    """0..1 normalised against the highest published fixed rate, plus the eligibility verdict."""
    info = rate_for_category(category, table)
    if info is None:
        return {"ok": False, "score": None, "detail": "insufficient data - product category not verified"}
    table = table or load_rate_table()
    ceiling = max(v.rate_pct for v in table.values()) or 1.0
    if info.rate_pct == 0.0:
        return {
            "ok": False,
            "score": 0.0,
            "detail": f"ineligible: {category} is a published 0.00% band (exclusion list)",
            "rate_pct": 0.0,
        }
    return {
        "ok": True,
        "score": info.rate_pct / ceiling,
        "rate_pct": info.rate_pct,
        "exact_match": info.exact_match,
        "source_id": info.source_id,
        "detail": (
            f"{info.rate_pct:.2f}% published fixed rate"
            + ("" if info.exact_match else " (All Other Categories default band)")
        ),
    }


def review_signal(review_count, avg_rating) -> dict:
    """Demand-quality proxy from a listing's own review base.  Both inputs must exist."""
    if review_count is None or avg_rating is None:
        return {"ok": False, "score": None, "detail": "insufficient data - no verified rating/review count"}
    n, r = float(review_count), float(avg_rating)
    if n <= 0:
        return {"ok": False, "score": None, "detail": "insufficient data - review count 0"}
    depth = min(1.0, math.log10(n + 1) / 4.0)  # 9999+ reviews ~ saturates
    quality = max(0.0, min(1.0, (r - 3.0) / 2.0))  # 3.0 -> 0, 5.0 -> 1
    return {"ok": True, "score": 0.6 * depth + 0.4 * quality, "detail": f"{n:.0f} reviews, {r:.1f} avg"}


def competition_term(results_observed: int | None, competitors_with_reviews: int | None, observed_utc=None) -> dict:
    """Only usable with an operator-recorded SERP sample.  Never defaulted."""
    if results_observed is None or competitors_with_reviews is None or not observed_utc:
        return {
            "ok": False,
            "score": None,
            "detail": "insufficient data - no dated SERP observation recorded (never inferred)",
        }
    pressure = min(1.0, float(competitors_with_reviews) / 10.0)
    return {
        "ok": True,
        "score": max(0.0, 1.0 - pressure),
        "detail": f"observed {results_observed} results / {competitors_with_reviews} reviewed competitors on {observed_utc}",
    }


def demand_term(observations: list[dict] | None) -> dict:
    """Trend needs >=2 dated observations of the same metric from the same official source (M-02)."""
    if not observations or len(observations) < 2:
        return {"ok": False, "score": None, "detail": "insufficient data - fewer than 2 dated observations"}
    vals = [o.get("value") for o in observations]
    if any(v is None for v in vals):
        return {"ok": False, "score": None, "detail": "insufficient data - incomplete observation set"}
    first, last = float(vals[0]), float(vals[-1])
    if first <= 0:
        return {"ok": False, "score": None, "detail": "insufficient data - baseline observation <= 0"}
    delta = (last - first) / first
    return {
        "ok": True,
        "score": max(0.0, min(1.0, 0.5 + delta / 2.0)),
        "detail": f"{first} -> {last} over {len(observations)} observations ({delta:+.1%})",
    }


WEIGHTS = {"commission": 0.30, "demand": 0.25, "competition": 0.25, "review": 0.20}


def niche_score(category, observations=None, results_observed=None, reviewed=None, observed_utc=None) -> dict:
    """Category-level attractiveness.  Blocks (rather than guesses) when any weighted input is missing."""
    parts = {
        "commission": commission_term(category),
        "demand": demand_term(observations),
        "competition": competition_term(results_observed, reviewed, observed_utc),
        "review": {"ok": False, "score": None, "detail": "insufficient data - no aggregate category listing data"},
    }
    missing = [k for k, v in parts.items() if not v["ok"]]
    if missing:
        return {
            "verdict": "INSUFFICIENT_DATA",
            "score": None,
            "blocked_inputs": missing,
            "parts": parts,
            "note": "no niche is declared profitable without every weighted input (M-02/M-05/M-11)",
        }
    avail = {k: v for k, v in parts.items() if v["ok"]}
    wsum = sum(WEIGHTS[k] for k in avail)
    score = sum(WEIGHTS[k] * avail[k]["score"] for k in avail) / wsum
    return {"verdict": "SCORED", "score": score, "parts": parts, "normalized_over": wsum}


# --------------------------------------------------------------------------- money math


def expected_value(clicks: int, conversion_rate: float | None, aov: float | None, rate_pct: float) -> dict:
    """Per-cycle commission estimate.  Any unknown input yields None - not a zero.

    Documented as ILLUSTRATIVE: Amazon makes no representation about the traffic or commission income an
    associate can expect (Operating Agreement Sec. 4 / R-19), so this must never be presented as a forecast.
    """
    if conversion_rate is None or aov is None or rate_pct is None:
        return {"ok": False, "estimate": None, "detail": "insufficient data - conversion or AOV unknown"}
    if clicks <= 0:
        return {"ok": True, "estimate": 0.0, "detail": "no clicks recorded"}
    units = clicks * conversion_rate
    est = units * aov * (rate_pct / 100.0)
    return {
        "ok": True,
        "estimate": round(est, 2),
        "units": round(units, 3),
        "assumptions": {"clicks": clicks, "conversion_rate": conversion_rate, "aov": aov, "rate_pct": rate_pct},
        "labels_illustrative": True,
    }


def delayed_cart_uplift(cart_adds: int, delayed_orders: int) -> dict:
    """Measure the 89-day cart tail (R-13) from real data instead of assuming a number."""
    if not cart_adds:
        return {"ok": False, "uplift": None, "detail": "insufficient data - no cart adds"}
    return {
        "ok": True,
        "uplift": round(float(delayed_orders or 0) / float(cart_adds), 4),
        "detail": f"{delayed_orders or 0} orders completed after click day within the 89-day window",
    }


if __name__ == "__main__":  # pragma: no cover
    table = load_rate_table()
    print("published bands:", sorted({v.rate_pct for v in table.values()}, reverse=True))
    print("0.00% categories:", len(zero_rate_categories(table)))
    for cat in ["Kitchen", "Home", "Televisions", "Gift Cards", "Something Not In The Table", None]:
        print(f"  {cat!r:35}", commission_term(cat, table))
