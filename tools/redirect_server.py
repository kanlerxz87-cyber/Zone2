"""First-party click measurement endpoint.

Scope is narrow on purpose.  Amazon's Program Policies (source S02) forbid associating a sub-tag - or any
Associates reporting - with a specific end user, so this tracker cannot and does not identify visitors.
Conversion and earnings are not measured here at all: they come from Associates reporting under the Session
definition (R-13/R-15).  This service only counts which page and which static campaign sent a click.

Design:
  * no cookies, no fingerprints, no IP persisted (only a salted /24 prefix for optional abuse limits)
  * campaign keys come from a static registry file, never from request data (R-08)
  * the outbound href is built by tools/link_builder.py, so the tag/rel guarantees always hold
  * writes one JSON line per click to the event log (append-only), aggregated by tools/optimize.py
"""

from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parents[1]
CAMPAIGN_REGISTRY = REPO / "ledger" / "campaigns.json"
EVENT_LOG = Path(os.environ.get("ZONE2_EVENT_LOG", REPO / ".local" / "clicks.jsonl"))

SUBTAG_STATIC_RULE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,47}$")
PER_VISITOR_TOKENS = ("user", "uid", "uuid", "session", "sid", "ip", "visitor", "client", "device", "email")


class TrackingPolicyError(ValueError):
    pass


@dataclass(frozen=True)
class Campaign:
    key: str
    page: str
    entry: str
    position: str
    asin: str
    enabled: bool

    @property
    def href_path(self) -> str:
        return f"/c/{self.key}"


def load_campaigns(path: Path = CAMPAIGN_REGISTRY) -> dict[str, Campaign]:
    if not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    out = {}
    for raw in doc.get("campaigns", []):
        c = Campaign(**raw)
        if not SUBTAG_STATIC_RULE.match(c.key):
            raise TrackingPolicyError(f"campaign key {c.key!r} is not a static lowercase label (R-08)")
        if any(tok in c.key.lower() for tok in PER_VISITOR_TOKENS):
            raise TrackingPolicyError(f"campaign key {c.key!r} looks per-visitor, which is prohibited (R-08)")
        out[c.key] = c
    return out


def resolve(key: str, campaigns: dict[str, Campaign]) -> Campaign:
    if key not in campaigns:
        raise TrackingPolicyError(
            f"unknown campaign {key!r}: only registered static campaigns may be tracked; "
            "an ad-hoc key would let a caller smuggle a per-visitor identifier (R-08)"
        )
    c = campaigns[key]
    if not c.enabled:
        raise TrackingPolicyError(f"campaign {key!r} is disabled")
    return c


def record_click(key: str, campaigns: dict[str, Campaign], *, dest_builder) -> dict:
    """Count a click and return the redirect target.  The event line contains no visitor data."""
    c = resolve(key, campaigns)
    target = dest_builder(c.asin, c)
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "ts": int(time.time()),
        "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "campaign": c.key,
        "page": c.page,
        "entry": c.entry,
        "position": c.position,
        "asin": c.asin,
    }
    with EVENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, sort_keys=True) + "\n")
    return {"location": target, "event": event}


def aggregate(events: list[dict]) -> dict[str, dict]:
    """Per-campaign click totals.  Deliberately stops at clicks: it cannot invent CTR, conversion or EPC."""
    totals: dict[str, dict] = {}
    for e in events:
        row = totals.setdefault(
            e["campaign"], {"campaign": e["campaign"], "page": e.get("page", ""), "clicks": 0, "first_ts": e["ts"], "last_ts": e["ts"]}
        )
        row["clicks"] += 1
        row["first_ts"] = min(row["first_ts"], e["ts"])
        row["last_ts"] = max(row["last_ts"], e["ts"])
    return totals


class Handler(BaseHTTPRequestHandler):
    server_version = "zone2-clicks/1.0"

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/healthz":
            self._send(200, {"ok": True, "campaigns": len(self.server.campaigns)})  # type: ignore[attr-defined]
            return
        m = re.match(r"^/c/([A-Za-z0-9_-]+)/?$", path)
        if not m:
            self._send(404, {"error": "not found"})
            return
        try:
            result = record_click(m.group(1), self.server.campaigns, dest_builder=self.server.dest_builder)  # type: ignore[attr-defined]
        except TrackingPolicyError as exc:
            # Never redirect on a policy failure - a wrong or per-user tag is worse than no click.
            self._send(400, {"error": str(exc)})
            return
        self.send_response(302)
        self.send_header("Location", result["location"])
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer-when-downgrade")
        self.end_headers()

    def log_message(self, fmt: str, *args) -> None:  # suppress default access log (would persist IPs)
        return

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(host: str = "0.0.0.0", port: int = 8080):
    campaigns = load_campaigns()

    def dest_builder(asin: str, campaign: Campaign) -> str:
        import link_builder as lb  # local import so module can be used without a configured tag

        try:
            link = lb.build_product_link(
                asin,
                os.environ.get("ZONE2_PARTNER_TAG", ""),
                link_text="View on Amazon",
                subtag=campaign.position,
            )
            return link.href
        except lb.LinkPolicyError as exc:
            raise TrackingPolicyError(f"destination refused by link policy: {exc}") from exc

    srv = ThreadingHTTPServer((host, port), Handler)
    srv.campaigns = campaigns  # type: ignore[attr-defined]
    srv.dest_builder = dest_builder  # type: ignore[attr-defined]
    return srv


if __name__ == "__main__":  # pragma: no cover
    import http.server  # noqa: F401  (documents the stdlib dependency)

    srv = make_server()
    print(f"serving {len(srv.campaigns)} campaigns on http://0.0.0.0:8080/c/<key>")  # type: ignore[attr-defined]
    srv.serve_forever()
