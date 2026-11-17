#!/usr/bin/env python3
"""Zone2 self-hosted analytics endpoint — tools/analytics_server.py.

The server half of the measurement layer (docs/measurement-t40.json). It accepts
only the events that design defines and only the fields each event declares, and
it refuses everything that could single out a person:

  * POST /collect   — record EV-01 page_view, EV-02 product_link_click or
                      EV-03 disclosure_view. Unknown events (including
                      "conversion" and "earnings" — EV-04 is BLOCKED and cannot
                      be recorded here) are rejected. Unknown fields are
                      rejected. Per-visitor keys (user_id, session, fingerprint,
                      email, ip, …) are rejected — the collector never sees them.
  * POST /subscribe — reader capture (SG-28): stores exactly {email, page_path,
                      day} and nothing else. It sends no email and claims no
                      mailing capability; confirmation before any email is the
                      owner's list-provider step (MI-02 family).
  * GET  /healthz   — liveness + counts. No personal data.
  * GET  /events    — daily aggregates only: event counts by day and, for
                      product_link_click, by product_key. No rows, no paths of
                      individual visits, no per-visitor anything.

Storage is append-only JSONL under --data-dir plus daily.json aggregates.
Retention: raw event lines expire after 30 days (MI-02's default, awaiting the
owner's recorded policy); `--prune` folds expiring lines into the daily
aggregates and deletes them. Bot user-agents are dropped (MI-03's minimal
filter — explicitly not a bot policy).

Deployment (owner): run this anywhere you control, then point the site at it by
setting <meta name="zone2-analytics-endpoint" content="https://your-host/collect">
in the page templates. Until that tag is set, the client ships as a no-op and
nothing is collected.

Usage:
    python3 tools/analytics_server.py --host 0.0.0.0 --port 8787 --data-dir .analytics
    python3 tools/analytics_server.py --data-dir .analytics --prune
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RETENTION_DAYS = 30
RAW_FILE = "events.jsonl"
READERS_FILE = "readers.jsonl"
AGG_FILE = "daily.json"

# EV-01/02/03 field allowlists — exactly the fields docs/measurement-t40.json
# declares for each event. Anything else is a rejection, not a silent drop.
EVENT_FIELDS = {
    "page_view": {"page_path", "referrer_host", "viewport_class", "day"},
    "product_link_click": {"page_path", "product_key", "link_state", "placement", "day"},
    "disclosure_view": {"page_path", "disclosure_position", "day"},
}

# Keys that must never appear in any payload. This list is the no-per-visitor
# rule (MP-01) spelled as code, and tools/test_measurement.py asserts it.
BANNED_KEYS = {
    "user_id", "user", "uid", "visitor_id", "visitor", "session_id", "session",
    "fingerprint", "device_id", "device", "client_id", "gid", "email", "name",
    "phone", "address", "ip", "ip_address", "cookie", "id", "url", "referrer",
    "resolution", "screen", "user_agent", "ua", "query", "utm_id", "click_id",
}

SUBSCRIBE_FIELDS = {"email", "page_path", "day"}

# Substring tokens, not prefixes: real crawler UAs bury the token mid-string
# ("Mozilla/5.0 (compatible; Googlebot/2.1)"). Deliberately minimal (MI-03):
# this is a courtesy filter, not a bot policy.
BOT_UA_TOKENS = (
    "bot", "crawl", "spider", "slurp", "headless", "phantom",
    "curl", "wget", "python-requests", "go-http", "preview", "monitor",
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Rejected(Exception):
    """A payload that violates the schema or the privacy rule."""


class EventStore:
    """Append-only JSONL events with daily aggregates and a retention rule."""

    def __init__(self, data_dir: Path):
        self.dir = Path(data_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.raw = self.dir / RAW_FILE
        self.readers = self.dir / READERS_FILE
        self.agg_path = self.dir / AGG_FILE

    # -- validation ----------------------------------------------------
    @staticmethod
    def validate(event: str, fields: dict) -> dict:
        if event not in EVENT_FIELDS:
            raise Rejected(f"unknown event {event!r} — this endpoint records only {sorted(EVENT_FIELDS)}")
        allowed = EVENT_FIELDS[event]
        for key in fields:
            if key in BANNED_KEYS:
                raise Rejected(f"field {key!r} is a per-visitor identifier — never collected (MP-01)")
            if key not in allowed:
                raise Rejected(f"field {key!r} is not declared for {event}")
        out = {"event": event}
        for key in sorted(allowed):
            if key in fields:
                value = fields[key]
                if not isinstance(value, str):
                    raise Rejected(f"field {key!r} must be a string")
                out[key] = value
        if "day" not in out:
            out["day"] = date.today().isoformat()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", out["day"]):
            raise Rejected("day must be a UTC calendar date (YYYY-MM-DD), not a timestamp")
        return out

    # -- storage -------------------------------------------------------
    def record(self, payload: dict) -> None:
        with self.raw.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")

    def record_reader(self, fields: dict) -> dict:
        for key in fields:
            if key in BANNED_KEYS and key != "email":
                raise Rejected(f"field {key!r} is never collected (MP-01)")
            if key not in SUBSCRIBE_FIELDS:
                raise Rejected(f"field {key!r} is not accepted by /subscribe")
        email = str(fields.get("email") or "")
        if not EMAIL_RE.match(email):
            raise Rejected("email must be a plain address")
        row = {
            "email": email,
            "page_path": str(fields.get("page_path") or ""),
            "day": date.today().isoformat(),
        }
        with self.readers.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
        return row

    def raw_rows(self) -> list:
        if not self.raw.exists():
            return []
        rows = []
        for line in self.raw.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows

    def aggregates(self) -> dict:
        if self.agg_path.exists():
            stored = json.loads(self.agg_path.read_text(encoding="utf-8"))
        else:
            stored = {"by_day": {}, "products": {}, "pruned": 0}
        by_day = {day: dict(events) for day, events in stored.get("by_day", {}).items()}
        products = dict(stored.get("products", {}))
        rows = self.raw_rows()
        for row in rows:
            day = row.get("day", "?")
            event = row.get("event", "?")
            by_day.setdefault(day, {})
            by_day[day][event] = by_day[day].get(event, 0) + 1
            if event == "product_link_click":
                key = row.get("product_key", "?")
                products[key] = products.get(key, 0) + 1
        # "pruned" counts lines already folded into by_day by prune().
        total = int(stored.get("pruned", 0)) + len(rows)
        return {"by_day": by_day, "products": products, "total": total}

    def reader_count(self) -> int:
        if not self.readers.exists():
            return 0
        return sum(1 for line in self.readers.read_text(encoding="utf-8").splitlines() if line.strip())

    def prune(self, retention_days: int = RETENTION_DAYS) -> int:
        """Fold expiring raw lines into daily.json, then delete them."""
        cutoff = (date.today() - timedelta(days=retention_days)).isoformat()
        kept, expiring = [], []
        for row in self.raw_rows():
            (expiring if row.get("day", "9999") < cutoff else kept).append(row)
        if not expiring:
            return 0
        agg = json.loads(self.agg_path.read_text(encoding="utf-8")) if self.agg_path.exists() else {"by_day": {}, "products": {}, "pruned": 0}
        for row in expiring:
            day = row.get("day", "?")
            event = row.get("event", "?")
            agg["by_day"].setdefault(day, {})
            agg["by_day"][day][event] = agg["by_day"][day].get(event, 0) + 1
            if event == "product_link_click":
                key = row.get("product_key", "?")
                agg["products"][key] = agg.get("products", {}).get(key, 0) + 1
        agg["pruned"] = int(agg.get("pruned", 0)) + len(expiring)
        self.agg_path.write_text(json.dumps(agg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.raw.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in kept), encoding="utf-8")
        return len(expiring)


def is_bot(user_agent: str) -> bool:
    ua = (user_agent or "").strip().lower()
    if not ua:
        return True
    return any(token in ua for token in BOT_UA_TOKENS)


def make_handler(store: EventStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "Zone2Analytics/1.0"

        def _json(self, code: int, payload: dict) -> None:
            body = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            self.wfile.write(body)

        def do_OPTIONS(self):  # noqa: N802
            self._json(204, {})

        def do_GET(self):  # noqa: N802
            if self.path == "/healthz":
                self._json(200, {
                    "ok": True,
                    "events_total": store.aggregates()["total"],
                    "readers": store.reader_count(),
                    "retention_days": RETENTION_DAYS,
                })
            elif self.path == "/events":
                self._json(200, store.aggregates())
            else:
                self._json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            try:
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length) if length else b"{}"
                fields = json.loads(raw.decode("utf-8") or "{}")
                if not isinstance(fields, dict):
                    raise Rejected("payload must be a JSON object")
            except (ValueError, json.JSONDecodeError):
                self._json(400, {"error": "body must be a JSON object"})
                return

            if self.path == "/collect":
                if is_bot(self.headers.get("User-Agent")):
                    self._json(202, {"status": "dropped", "reason": "bot user-agent"})
                    return
                try:
                    event = fields.pop("event", None)
                    payload = store.validate(event, fields)
                except Rejected as err:
                    self._json(422, {"error": str(err)})
                    return
                store.record(payload)
                self._json(202, {"status": "recorded"})
            elif self.path == "/subscribe":
                try:
                    row = store.record_reader(fields)
                except Rejected as err:
                    self._json(422, {"error": str(err)})
                    return
                self._json(202, {"status": "recorded", "note": "stored only; no email is sent by this endpoint"})
            else:
                self._json(404, {"error": "not found"})

        def log_message(self, fmt, *args):  # quiet by default
            pass

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Zone2 self-hosted analytics endpoint (no per-visitor data)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--data-dir", default=".analytics")
    ap.add_argument("--prune", action="store_true", help="fold raw events older than the retention window into daily.json and exit")
    args = ap.parse_args(argv)

    store = EventStore(Path(args.data_dir))
    if args.prune:
        removed = store.prune(RETENTION_DAYS)
        print(json.dumps({"pruned": removed, "retention_days": RETENTION_DAYS}, indent=2))
        return 0

    server = ThreadingHTTPServer((args.host, args.port), make_handler(store))
    print(f"Zone2 analytics endpoint on http://{args.host}:{args.port} (data: {store.dir}, retention {RETENTION_DAYS}d)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
