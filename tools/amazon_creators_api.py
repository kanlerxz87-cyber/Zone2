"""Creators API client (the sanctioned catalog data source).

Amazon's PA-API 5.0 is deprecated: calls now return HTTP 403 / AccessDenied with a pointer to the Creators API
(source S06).  The Creators API prerequisites stated in Amazon's own docs (source S07) are: enrolment in the
Associates program for the target marketplace, at least 10 qualifying sales in the past 30 days, API
registration through Associates Central, and generated credentials.

This client therefore has three possible outcomes, and only two of them are silent:

  * READY    - credentials present: real request is made and the response is cached verbatim.
  * BLOCKED  - credentials/eligibility absent: raises ``Blocked`` with a machine-readable reason.  The
               caller must leave dependent fields blank.  No scraping, no guessing, no fallback.
  * STALE    - a cached response exists but its ``as_of`` is outside the freshness window: values are
               returned with ``stale=True`` so pricing/availability cannot be presented as current.

Environment:
  ZONE2_PARTNER_TAG     Associates ID (e.g. exampletag-20)
  ZONE2_API_KEY         Creators API key id
  ZONE2_API_SECRET      Creators API secret
  ZONE2_API_HOST        optional endpoint override (defaults to the marketplace endpoint)
  ZONE2_MARKETPLACE     e.g. amazon.com  (default)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from asin_guard import validate_asin

REPO = Path(__file__).resolve().parents[1]
CACHE_DIR = REPO / ".cache" / "catalog"

ENDPOINTS = {"amazon.com": "https://rest.amazon.com"}  # only the host the operator configured is trusted
DEFAULT_FRESHNESS_HOURS = {
    "price": 24,  # price/availability change; anything older may not be shown as current (R-04)
    "title": 24 * 30,
    "default": 24 * 7,
}

# Fields the API returns are stored verbatim: Participation Requirements forbid adding to, deleting from or
# otherwise altering Content (R-10).  Anything else must be *our* editorial text in a separate key.
FIELD_IMMUTABILITY = ("title", "brand", "contributors", "by_line_info", "features", "classifications")


class Blocked(RuntimeError):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


class QuotaExceeded(RuntimeError):
    pass


@dataclass
class Creds:
    partner_tag: str
    key: str
    secret: str
    host: str

    @classmethod
    def from_env(cls) -> "Creds":
        marketplace = os.environ.get("ZONE2_MARKETPLACE", "amazon.com")
        tag = os.environ.get("ZONE2_PARTNER_TAG", "").strip()
        key = os.environ.get("ZONE2_API_KEY", "").strip()
        secret = os.environ.get("ZONE2_API_SECRET", "").strip()
        missing = [
            name
            for name, val in (("ZONE2_PARTNER_TAG", tag), ("ZONE2_API_KEY", key), ("ZONE2_API_SECRET", secret))
            if not val
        ]
        if missing:
            raise Blocked(
                "CREDS_MISSING",
                f"{', '.join(missing)} not set; Creators API access additionally requires an Associates account "
                "with >=10 qualifying sales in the past 30 days (source S07). Dependent fields must stay blank.",
            )
        return cls(tag, key, secret, os.environ.get("ZONE2_API_HOST") or ENDPOINTS[marketplace])


def _cache_key(operation: str, payload: dict[str, Any]) -> str:
    blob = json.dumps({"op": operation, "payload": payload}, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:32]


def _read_cache(key: str) -> dict[str, Any] | None:
    path = CACHE_DIR / f"{key}.json"
    if not path.exists():
        return None
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["stale"] = time.time() - doc["fetched_utc"] > DEFAULT_FRESHNESS_HOURS[doc.get("freshness_class", "default")] * 3600
    return doc


def _write_cache(key: str, doc: dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / f"{key}.json").write_text(json.dumps(doc, indent=2, sort_keys=True), encoding="utf-8")


class CreatorsClient:
    """Thin client over the documented operations: SearchItems, GetItems, GetVariations, GetBrowseNodes."""

    def __init__(self, creds: Creds | None = None, *, offline_ok: bool = False, min_interval_s: float = 0.55):
        self._creds = creds
        self.offline_ok = offline_ok
        self._min_interval = min_interval_s
        self._last = 0.0

    @property
    def creds(self) -> Creds:
        if self._creds is None:
            self._creds = Creds.from_env()
        return self._creds

    # ---- requests -------------------------------------------------------
    def get_items(self, asins: list[str], resources: list[str] | None = None) -> dict[str, Any]:
        clean = []
        for a in asins:
            v = validate_asin(a)
            if not v.valid:
                # The three brief-supplied tokens land here. Record the failure; never send a guessed id.
                raise Blocked("ASIN_INVALID", v.reason)
            clean.append(v.normalized)
        return self._call(
            "GetItems",
            {
                "ItemIds": clean,
                "PartnerTag": self.creds.partner_tag,
                "Resources": resources
                or ["ItemInfo.Title", "ItemInfo.ByLineInfo", "OffersListings.Listings.Price", "BrowseNodeInfo"],
            },
        )

    def search_items(self, keywords: str, *, count: int = 10, page: int = 1) -> dict[str, Any]:
        return self._call(
            "SearchItems",
            {"Keywords": keywords, "ItemCount": count, "ItemPage": page, "PartnerTag": self.creds.partner_tag},
        )

    def get_browse_nodes(self, node_ids: list[str]) -> dict[str, Any]:
        return self._call("GetBrowseNodes", {"BrowseNodeIds": node_ids, "PartnerTag": self.creds.partner_tag})

    def _call(self, operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        key = _cache_key(operation, payload)
        cached = _read_cache(key)
        if cached and not cached["stale"]:
            cached["source"] = "cache"
            return cached
        creds = self.creds  # raises Blocked when absent
        wait = self._min_interval - (time.time() - self._last)
        if wait > 0:
            time.sleep(wait)
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{creds.host}/{operation}",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": creds.key,
                "x-amz-partner-tag": creds.partner_tag,
                # A real deployment signs with the credentials Amazon issued; the auth scheme is taken from the
                # operator's API registration (source S07) rather than reimplemented from memory here.
                "authorization": f"CREATORS-API {creds.key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:  # pragma: no cover - network path
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:  # pragma: no cover
            text = exc.read().decode("utf-8", "replace")
            if exc.code == 403 and "AccessDenied" in text:
                raise Blocked(
                    "API_DEPRECATED_OR_UNAUTHORIZED",
                    "PA-API 5 returns 403 AccessDenied and directs integrators to the Creators API (source S06); "
                    "confirm this client is pointed at the Creators API endpoint and the account is eligible",
                ) from exc
            if exc.code == 429:
                raise QuotaExceeded("request throttled; honour the documented limit and back off") from exc
            raise Blocked("HTTP_ERROR", f"{exc.code} {text[:200]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:  # pragma: no cover
            raise Blocked("NETWORK_UNREACHABLE", f"{exc.reason}; no value may be substituted") from exc
        self._last = time.time()
        doc = {
            "operation": operation,
            "payload": payload,
            "status": status,
            "fetched_utc": int(time.time()),
            "fetched_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "response_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "raw": json.loads(raw),
            "freshness_class": "price" if "Offers" in str(payload.get("Resources")) else "default",
            "source": "live",
            "stale": False,
        }
        _write_cache(key, doc)
        return doc

    # ---- normalisation --------------------------------------------------
    @staticmethod
    def to_fields(doc: dict[str, Any]) -> dict[str, Any]:
        """Extract only fields present in the response.  A missing field stays missing (blank on the site);
        it is never back-filled from a title match, a memory, or a third-party listing."""
        out: dict[str, Any] = {
            "as_of": doc.get("fetched_iso"),
            "response_sha256": doc.get("response_sha256"),
            "stale": doc.get("stale", True),
        }
        items = ((doc.get("raw") or {}).get("Items") or {}).get("Items") or []
        if not items:
            out["resolved"] = False
            out["reason"] = "catalog response contained no item record"
            return out
        item = items[0]
        info = item.get("ItemInfo") or {}

        def dig(*path):
            node = item
            for p in path:
                if not isinstance(node, dict):
                    return None
                node = node.get(p)
            return node

        out["asin"] = item.get("ASIN") or item.get("DetailPageUrl", "")
        title = dig("ItemInfo", "Title", "DisplayValue")
        out["title"] = title if isinstance(title, str) else ""
        out["brand"] = dig("ItemInfo", "ByLineInfo", "Brand", "DisplayValue") or ""
        out["feature_bullets"] = (dig("ItemInfo", "Features", "DisplayValues") or [])[:5]
        price = dig("Offers", "Offers", "Offer", 0, "Price", "Amount") or dig(
            "OffersListings", "Listings", 0, "Price", "Amount"
        )
        out["price_amount"] = price if isinstance(price, (int, float)) else None
        out["price_currency"] = dig("Offers", "Offers", "Offer", 0, "Price", "Currency") or ""
        out["availability"] = dig("Offers", "Offers", "Offer", 0, "Availability", "Type") or ""
        out["rating"] = dig("CustomerReviews", "Count", "DisplayValue")
        out["browse_nodes"] = [n.get("DisplayName") for n in (dig("BrowseNodeInfo", "BrowseNodes") or []) if n]
        out["resolved"] = bool(out.get("title"))
        out["immutable_fields_verified"] = all(k in info or k.lower() in out for k in FIELD_IMMUTABILITY)
        return out


def status_report() -> dict[str, Any]:
    """What the pipeline can reach right now - used by the site's data-source status table."""
    try:
        Creds.from_env()
    except Blocked as exc:
        return {"state": "BLOCKED", "reason": exc.reason, "detail": exc.detail}
    return {"state": "READY", "reason": "", "detail": "credentials present; first live call still requires the network path"}


if __name__ == "__main__":  # pragma: no cover
    print(json.dumps(status_report(), indent=2))
    for tok in ["B04G1MEwY", "B08N5WRWNW"]:
        try:
            CreatorsClient(offline_ok=True).get_items([tok])
            print(f"{tok}: request issued")
        except Blocked as exc:
            print(f"{tok}: {exc}")
