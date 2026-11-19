"""Counter Notes: first-party daily counters and provenance-only report imports.

No browser identifiers, cookies, IP/UA persistence, raw request log or HTTP import API.
Run preview: python3 -m measurement.collector serve --preview --port 8000
Production: gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 4 measurement.collector:application
See measurement/README.md. GitHub Pages cannot run this process.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sqlite3
import sys
import threading
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server
from socketserver import ThreadingMixIn

ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = "/Zone2/"
EVENTS = ("page_view", "product_link_click", "disclosure_view", "conversion_import", "search_query_import")
PUBLIC_EVENTS = frozenset(EVENTS[:3])
PRODUCTS = frozenset(("P1", "P2", "P3", "P4", "P5"))
CHANNELS = frozenset(("direct", "search", "internal", "other"))
MAX_BODY = 8192
RETENTION_DAYS = 90


class Invalid(ValueError):
    """Do not include user-supplied values in error text."""


def utc_now():
    return datetime.now(timezone.utc)


def registered_pages(site: Path):
    return {p.relative_to(site).as_posix() for p in site.rglob("*.html")}


def canonical_page(value, pages):
    if not isinstance(value, str) or value not in pages:
        raise Invalid("page must be a registered static path")
    return value


def exact_fields(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise Invalid("unexpected or missing fields")


def counter_event(raw, pages):
    exact_fields(raw, ("event", "page"), ("product", "position", "channel"))
    event = raw["event"]
    if event not in PUBLIC_EVENTS:
        raise Invalid("event is not accepted from browsers")
    page = canonical_page(raw["page"], pages)
    product, position, channel = raw.get("product", ""), raw.get("position", ""), raw.get("channel", "")
    if event == "page_view":
        if product or position or channel not in CHANNELS:
            raise Invalid("invalid page event dimensions")
    elif event == "product_link_click":
        if product not in PRODUCTS or position or channel:
            raise Invalid("invalid product event dimensions")
    elif product or channel or position != "strip":
        raise Invalid("invalid disclosure event dimensions")
    return event, page, product, position, channel


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS daily_counts (
                    day TEXT NOT NULL, event TEXT NOT NULL, page TEXT NOT NULL,
                    product TEXT NOT NULL, position TEXT NOT NULL, channel TEXT NOT NULL,
                    count INTEGER NOT NULL CHECK(count > 0),
                    PRIMARY KEY(day,event,page,product,position,channel)
                );
                CREATE TABLE IF NOT EXISTS report_imports (
                    source TEXT NOT NULL, sha256 TEXT NOT NULL, imported_at TEXT NOT NULL,
                    period_start TEXT NOT NULL, period_end TEXT NOT NULL,
                    PRIMARY KEY(source,sha256)
                );
                CREATE TABLE IF NOT EXISTS campaign_observations (
                    source TEXT NOT NULL, sha256 TEXT NOT NULL, row_number INTEGER NOT NULL,
                    channel TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL,
                    tracking_id TEXT, page TEXT, query TEXT,
                    eligible_sessions INTEGER, clicks INTEGER, reported_orders INTEGER,
                    impressions INTEGER, average_position REAL,
                    PRIMARY KEY(source,sha256,row_number)
                );
            """)

    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def increment(self, events, *, day=None):
        day = day or utc_now().date()
        cutoff = (day - timedelta(days=RETENTION_DAYS)).isoformat()
        with self.connect() as db:
            db.execute("DELETE FROM daily_counts WHERE day < ?", (cutoff,))
            # Report imports intentionally do not enter this table or vice versa.
            for event, page, product, position, channel in events:
                db.execute("""INSERT INTO daily_counts VALUES (?,?,?,?,?,?,1)
                    ON CONFLICT(day,event,page,product,position,channel)
                    DO UPDATE SET count=count+1""", (day.isoformat(), event, page, product, position, channel))

    def export(self):
        # No public HTTP route exposes this. Operator invokes the CLI on their own server.
        with self.connect() as db:
            db.row_factory = sqlite3.Row
            counts = [dict(r) for r in db.execute("SELECT * FROM daily_counts ORDER BY day,event,page,product")]
            reports = [dict(r) for r in db.execute("SELECT * FROM campaign_observations ORDER BY source,period_start,row_number")]
            imports = [dict(r) for r in db.execute("SELECT * FROM report_imports ORDER BY imported_at")]
        return {"exported_at": utc_now().isoformat(), "notice": "Aggregate event counts, not people, sessions, or purchase attribution.",
                "daily_counts": counts, "campaign_observations": reports, "provenance": imports}

    def prune(self, today=None):
        cutoff = ((today or utc_now().date()) - timedelta(days=RETENTION_DAYS)).isoformat()
        with self.connect() as db:
            db.execute("DELETE FROM daily_counts WHERE day < ?", (cutoff,))
            # Delete whole expired imports atomically so provenance never describes missing rows.
            old = db.execute("SELECT source,sha256 FROM report_imports WHERE period_end < ?", (cutoff,)).fetchall()
            for source, digest in old:
                db.execute("DELETE FROM campaign_observations WHERE source=? AND sha256=?", (source, digest))
                db.execute("DELETE FROM report_imports WHERE source=? AND sha256=?", (source, digest))


def parse_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise Invalid("invalid report date")
    try:
        result = date.fromisoformat(value)
    except ValueError:
        raise Invalid("invalid report date") from None
    if result > utc_now().date():
        raise Invalid("report dates cannot be in the future")
    return result


def nonnegative(value, *, nullable=True):
    if value is None and nullable:
        return None
    if type(value) is not int or not 0 <= value <= 1_000_000_000:
        raise Invalid("count must be a nonnegative integer or null")
    return value


def import_report(store, path, *, authorized_source, pages, allowed_queries):
    """Import normalized FIRST-PARTY aggregate exports, never estimated conversions.

    The operator attests the source via a required CLI flag; code cannot independently
    authenticate an arbitrary export. Nothing is claimed to be Amazon-verified by import.
    Raw filenames and raw report contents are not persisted; only validated fields + hash.
    """
    payload = path.read_bytes()
    if len(payload) > 2_000_000:
        raise Invalid("report exceeds size limit")
    try:
        doc = json.loads(payload)
    except (ValueError, UnicodeError):
        raise Invalid("invalid report JSON") from None
    exact_fields(doc, ("source", "period_start", "period_end", "rows"))
    source = doc["source"]
    if source not in ("amazon_associates", "google_search_console") or source != authorized_source:
        raise Invalid("source does not match operator attestation")
    start, end = parse_date(doc["period_start"]), parse_date(doc["period_end"])
    if start > end or start < utc_now().date() - timedelta(days=RETENTION_DAYS):
        raise Invalid("report period is inverted or outside retention")
    if not isinstance(doc["rows"], list) or not 0 < len(doc["rows"]) <= 10000:
        raise Invalid("report needs a bounded list of rows")
    rows = []
    keys = set()
    for i, raw in enumerate(doc["rows"]):
        if source == "amazon_associates":
            exact_fields(raw, ("tracking_id", "channel", "eligible_sessions", "clicks", "reported_orders"))
            if raw["tracking_id"] != "shopnow047c-20" or raw["channel"] != "amazon_associates":
                raise Invalid("report must use the configured tracking ID and source channel")
            # An account-level report cannot be attributed to a particular page or query.
            key = raw["tracking_id"]
            row = (source, "", i, raw["channel"], start.isoformat(), end.isoformat(), raw["tracking_id"], None, None,
                   nonnegative(raw["eligible_sessions"]), nonnegative(raw["clicks"]), nonnegative(raw["reported_orders"]), None, None)
        else:
            exact_fields(raw, ("page", "query", "impressions", "clicks", "average_position"))
            page = canonical_page(raw["page"], pages)
            query = raw["query"]
            if not isinstance(query, str) or query not in allowed_queries:
                raise Invalid("query is not in the reviewed non-personal topic allowlist")
            pos = raw["average_position"]
            if type(pos) not in (int, float) or not 1 <= pos <= 100000:
                raise Invalid("invalid average position")
            key = (page, query)
            row = (source, "", i, "organic_search", start.isoformat(), end.isoformat(), None, page, query, None,
                   nonnegative(raw["clicks"], nullable=False), None, nonnegative(raw["impressions"], nullable=False), pos)
        if key in keys:
            raise Invalid("duplicate report dimensions")
        keys.add(key)
        rows.append(row)
    digest = hashlib.sha256(payload).hexdigest()
    event = "conversion_import" if source == "amazon_associates" else "search_query_import"
    with store.connect() as db:
        if db.execute("SELECT 1 FROM report_imports WHERE source=? AND sha256=?", (source, digest)).fetchone():
            return {"event": event, "status": "already_imported", "sha256": digest}
        # Overlapping reports cannot be summed. Reject them, including re-exports with a
        # different byte hash, rather than silently doubling orders or impressions.
        if db.execute("SELECT 1 FROM report_imports WHERE source=? AND period_start<=? AND period_end>=?",
                      (source, end.isoformat(), start.isoformat())).fetchone():
            raise Invalid("report overlaps an imported period; review before replacing")
        db.execute("INSERT INTO report_imports VALUES (?,?,?,?,?)", (source, digest, utc_now().isoformat(), start.isoformat(), end.isoformat()))
        db.executemany("INSERT INTO campaign_observations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       [tuple(list(row[:1]) + [digest] + list(row[2:])) for row in rows])
    return {"event": event, "status": "imported", "rows": len(rows), "sha256": digest}


class Budget:
    """Process-wide abuse cap, never an IP/UA-derived identifier. Not bot-proof."""
    def __init__(self, limit=600):
        self.limit, self.tokens, self.last = limit, float(limit), time.monotonic()
        self.lock = threading.Lock()

    def accept(self):
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.limit, self.tokens + (now - self.last) * self.limit / 60)
            self.last = now
            if self.tokens < 1:
                return False
            self.tokens -= 1
            return True


class Application:
    def __init__(self, site, db, *, origin="", preview=False):
        self.site = site.resolve()
        self.pages = registered_pages(self.site)
        self.store = Store(db)
        self.origin, self.preview = origin.rstrip("/"), preview
        self.budget = Budget()

    def __call__(self, env, respond):
        headers = [("X-Content-Type-Options", "nosniff"), ("Referrer-Policy", "strict-origin-when-cross-origin")]

        def send(code, value, content_type="application/json; charset=utf-8", *, cache="no-store"):
            body = json.dumps(value, separators=(",", ":")).encode() if isinstance(value, (dict, list)) else value
            respond(code, headers + [("Content-Type", content_type), ("Content-Length", str(len(body))), ("Cache-Control", cache)])
            return [b"" if env.get("REQUEST_METHOD") == "HEAD" else body]

        path = env.get("PATH_INFO", "")
        method = env.get("REQUEST_METHOD", "GET")
        if path in ("/healthz", BASE_PATH + "api/healthz") and method in ("GET", "HEAD"):
            return send("200 OK", {"ok": True, "mode": "preview" if self.preview else "self_hosted", "retention_days": RETENTION_DAYS})
        if path == BASE_PATH + "measurement.json" and method in ("GET", "HEAD"):
            return send("200 OK", {"enabled": bool(self.origin or self.preview), "endpoint": "api/events", "mode": "preview" if self.preview else "self_hosted"})
        if path == BASE_PATH + "api/events":
            if method != "POST":
                return send("405 Method Not Allowed", {"error": "POST required"})
            origin = env.get("HTTP_ORIGIN", "")
            preview_ok = self.preview and bool(re.fullmatch(r"https://[a-z0-9-]+\.e2b\.app|http://(?:localhost|127\.0\.0\.1):\d+", origin))
            if not (self.origin and origin == self.origin or preview_ok):
                return send("403 Forbidden", {"error": "origin not allowed"})
            if env.get("HTTP_DNT") == "1" or env.get("HTTP_SEC_GPC") == "1":
                return send("202 Accepted", {"accepted": 0, "privacy_signal": True})
            if not self.budget.accept():
                return send("429 Too Many Requests", {"error": "aggregate request budget reached"})
            if env.get("CONTENT_TYPE", "").split(";")[0] not in ("application/json", "text/plain"):
                return send("415 Unsupported Media Type", {"error": "JSON required"})
            try:
                length = int(env.get("CONTENT_LENGTH") or "0")
                if not 0 < length <= MAX_BODY:
                    return send("413 Content Too Large", {"error": "body size refused"})
                doc = json.loads(env["wsgi.input"].read(length))
                exact_fields(doc, ("events",))
                if not isinstance(doc["events"], list) or not 0 < len(doc["events"]) <= 10:
                    raise Invalid("events must contain one to ten entries")
                events = [counter_event(raw, self.pages) for raw in doc["events"]]
                self.store.increment(events)
            except (ValueError, UnicodeError, TypeError, KeyError):
                return send("400 Bad Request", {"error": "event schema refused"})
            except sqlite3.Error:
                return send("503 Service Unavailable", {"error": "counter unavailable"})
            return send("202 Accepted", {"accepted": len(events)})
        if method not in ("GET", "HEAD"):
            return send("405 Method Not Allowed", {"error": "method not allowed"})
        if path in ("/", BASE_PATH.rstrip("/")):
            # Keep relative page/assets/API URLs under the same project prefix,
            # including when a preview UI opens the bare port URL.
            headers.append(("Location", BASE_PATH))
            return send("302 Found", b"", "text/plain; charset=utf-8")
        if not path.startswith(BASE_PATH):
            return send("404 Not Found", {"error": "not found"})
        rel = unquote(path[len(BASE_PATH):])
        parts = Path(rel).parts
        if any(part.startswith(".") or part == ".." for part in parts) or "\\" in rel:
            return send("404 Not Found", {"error": "not found"})
        target = (self.site / rel).resolve()
        if not target.is_relative_to(self.site):
            return send("404 Not Found", {"error": "not found"})
        if target.is_dir():
            target /= "index.html"
        if not target.is_file():
            return send("404 Not Found", {"error": "not found"})
        content_type = mimetypes.guess_type(target)[0] or "application/octet-stream"
        return send("200 OK", target.read_bytes(), content_type, cache="public, max-age=300")


def configured_app():
    return Application(Path(os.getenv("CN_SITE", ROOT / "_site")), Path(os.getenv("CN_DB", ROOT / ".local" / "measurement.sqlite3")),
                       origin=os.getenv("CN_PUBLIC_ORIGIN", ""), preview=os.getenv("CN_PREVIEW") == "1")


# Lazy WSGI initialization: importing this module for tests never creates a data file.
_app = None
_app_lock = threading.Lock()
def application(env, respond):
    global _app
    with _app_lock:
        if _app is None:
            _app = configured_app()
    return _app(env, respond)


class PreviewServer(ThreadingMixIn, WSGIServer):
    """Preview only: concurrent static fetches must not starve a counter POST.

    Use the documented bounded Gunicorn workers behind TLS for production.
    """
    daemon_threads = True


class QuietHandler(WSGIRequestHandler):
    def log_message(self, *args):
        pass  # Default access logs contain IPs. No raw access logging here.


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=Path(os.getenv("CN_DB", ROOT / ".local" / "measurement.sqlite3")))
    ap.add_argument("--site", type=Path, default=ROOT / "_site")
    sub = ap.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--preview", action="store_true")
    sub.add_parser("summary")
    sub.add_parser("prune")
    imp = sub.add_parser("import-report")
    imp.add_argument("file", type=Path)
    imp.add_argument("--authorized-source", required=True, choices=("amazon_associates", "google_search_console"))
    args = ap.parse_args()
    if args.command == "serve":
        app = Application(args.site, args.db, origin=os.getenv("CN_PUBLIC_ORIGIN", ""), preview=args.preview)
        print(f"Counter Notes ({'preview, not production data' if args.preview else 'self-hosted'}) on 0.0.0.0:{args.port}{BASE_PATH}", flush=True)
        with make_server("0.0.0.0", args.port, app, server_class=PreviewServer, handler_class=QuietHandler) as server:
            server.serve_forever()
        return
    store = Store(args.db)
    if args.command == "summary":
        store.prune()
        print(json.dumps(store.export(), indent=2))
    elif args.command == "prune":
        store.prune()
    else:
        try:
            queries = set(json.loads((ROOT / "measurement" / "query-allowlist.json").read_text()))
            result = import_report(store, args.file, authorized_source=args.authorized_source,
                                   pages=registered_pages(args.site), allowed_queries=queries)
        except (Invalid, OSError) as exc:
            raise SystemExit(str(exc)) from None
        print(json.dumps(result))


if __name__ == "__main__":
    main()
