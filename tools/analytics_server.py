#!/usr/bin/env python3
"""Cookie-free daily counters + authorized, provenance-bearing report imports.

The public endpoint accepts ONLY EV-01..03. EV-04/05 enter through a local CLI,
never a browser assertion. No redirects, cookies, visitor/session IDs, IP/UA logs,
referrers or query strings. Counts are raw events, NOT unique people, eligible
Amazon Sessions, purchases or an attestation that a disclosure was read.

GitHub Pages cannot run this service. The committed client config is disabled.
Run behind an owner-controlled HTTPS reverse proxy, or use --preview locally.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import mimetypes
import os
import re
import sqlite3
import threading
import time
from datetime import date, datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 8192
RETENTION_DAYS = 90
PRODUCTS = {f"P{i}" for i in range(1, 6)}
PUBLIC_EVENTS = {"page_view", "product_link_click", "disclosure_view"}
REPORT_EVENTS = {"conversion_import", "search_query_import"}
SAFE_SUFFIXES = {".html", ".css", ".js", ".svg", ".jpg", ".jpeg", ".png", ".webp", ".woff2", ".xml", ".txt", ".json", ".ico"}
EXCLUDED = {"tools", "tests", "docs", "content", "node_modules", "analytics", "deploy", "_site"}


def today() -> date:
    return datetime.now(timezone.utc).date()


def public_paths(root: Path = ROOT) -> set[str]:
    paths = set()
    for p in root.rglob("*.html"):
        rel = p.relative_to(root)
        if any(part.startswith(".") for part in rel.parts) or rel.parts[0] in EXCLUDED:
            continue
        value = "/" + rel.as_posix()
        paths.add(value)
        if p.name == "index.html":
            paths.add(value[:-10])
    return paths


def strip_prefix(path: str) -> str:
    return path[6:] if path.startswith("/Zone2/") else path


def validate_event(raw: object, allowed_pages: set[str]) -> tuple[str, str, str, str]:
    if not isinstance(raw, dict):
        raise ValueError("event must be an object")
    name, page = raw.get("name"), raw.get("page")
    if name not in PUBLIC_EVENTS:
        raise ValueError("event is not browser-collectable")
    expected = {"name", "page"}
    if name == "product_link_click":
        expected.add("product")
    elif name == "disclosure_view":
        expected.add("position")
    if set(raw) != expected:
        raise ValueError("unexpected or missing fields")
    if not isinstance(page, str) or len(page) > 240 or page not in allowed_pages:
        raise ValueError("page must be a registered static path without query or fragment")
    product, position = raw.get("product", ""), raw.get("position", "")
    if name == "product_link_click" and (not isinstance(product, str) or product not in PRODUCTS):
        raise ValueError("product must be a static catalog key")
    if name == "disclosure_view" and position != "strip":
        raise ValueError("unknown disclosure position")
    return name, page, product, position


class Store:
    """Persist aggregates, never raw request rows. Use one connection per transaction."""
    def __init__(self, path: Path, *, retention_days: int = RETENTION_DAYS):
        self.path = path
        self.retention_days = retention_days
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            # The default location is excluded from Git/static serving. Protect a
            # deliberately configured path from other local users as well.
            os.chmod(path, 0o600)
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS daily_events (
                    day TEXT NOT NULL, name TEXT NOT NULL, page TEXT NOT NULL,
                    product TEXT NOT NULL DEFAULT '', position TEXT NOT NULL DEFAULT '',
                    count INTEGER NOT NULL CHECK(count > 0),
                    PRIMARY KEY(day, name, page, product, position));
                CREATE TABLE IF NOT EXISTS report_imports (
                    sha256 TEXT NOT NULL, event TEXT NOT NULL, imported_utc TEXT NOT NULL,
                    source_url TEXT NOT NULL, channel TEXT NOT NULL, row_count INTEGER NOT NULL,
                    PRIMARY KEY(sha256, event));
                CREATE TABLE IF NOT EXISTS report_rows (
                    sha256 TEXT NOT NULL, event TEXT NOT NULL, row_number INTEGER NOT NULL,
                    period_start TEXT NOT NULL, period_end TEXT NOT NULL,
                    payload TEXT NOT NULL, PRIMARY KEY(sha256, event, row_number));
            """)

    def connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def purge(self, db, day: date):
        cutoff = (day - timedelta(days=self.retention_days - 1)).isoformat()
        db.execute("DELETE FROM daily_events WHERE day < ?", (cutoff,))
        db.execute("DELETE FROM report_rows WHERE period_end < ?", (cutoff,))
        db.execute("DELETE FROM report_imports WHERE substr(imported_utc,1,10) < ?", (cutoff,))

    def add(self, events: list[tuple], *, day: date | None = None):
        day = day or today()
        with self.connect() as db:
            self.purge(db, day)
            for name, page, product, position in events:
                db.execute("""INSERT INTO daily_events VALUES(?,?,?,?,?,1)
                    ON CONFLICT(day,name,page,product,position)
                    DO UPDATE SET count=count+1""", (day.isoformat(), name, page, product, position))

    def export(self) -> dict:
        with self.connect() as db:
            self.purge(db, today())
            db.row_factory = sqlite3.Row
            return {
                "as_of_utc": datetime.now(timezone.utc).isoformat(),
                "warning": "Raw events, not unique people or eligible Amazon Sessions. No inferred conversions.",
                "daily_events": [dict(x) for x in db.execute("SELECT * FROM daily_events ORDER BY day,name,page,product")],
                "report_imports": [dict(x) for x in db.execute("SELECT * FROM report_imports ORDER BY imported_utc")],
                "report_rows": [dict(x) for x in db.execute("SELECT * FROM report_rows ORDER BY sha256,event,row_number")],
            }


def count_value(value: str, *, optional: bool = False):
    if optional and value == "":
        return None
    if not re.fullmatch(r"\d{1,10}", value):
        raise ValueError("counts must be non-negative integers; unavailable values stay blank")
    return int(value)


def import_report(store: Store, content: bytes, event: str, source_url: str,
                  channel: str, *, authorized: bool, reviewed_for_personal_data: bool = False) -> int:
    """Import a normalized CSV derived from an authorized first-party export.

    This does not authenticate Amazon/Google or prove the operator's assertions.
    The SHA-256 identifies the supplied normalized file; retain the original export
    privately alongside the mapping for a human provenance review. No demo rows ship.
    """
    if not authorized or event not in REPORT_EVENTS:
        raise ValueError("authorized first-party report required")
    source = urlsplit(source_url)
    expected_host = "affiliate-program.amazon.com" if event == "conversion_import" else "search.google.com"
    if source.scheme != "https" or source.netloc != expected_host or source.query or source.fragment:
        raise ValueError("source must be the official report URL, without query or fragment")
    if not re.fullmatch(r"[a-z][a-z0-9_-]{0,31}", channel):
        raise ValueError("channel must be a static label")
    if len(content) > 2_000_000:
        raise ValueError("report too large")
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
    common = {"period_start", "period_end", "clicks"}
    required = common | ({"eligible_sessions", "reported_orders", "tracking_id"} if event == "conversion_import" else {"query", "page", "impressions", "average_position"})
    if reader.fieldnames is None or len(reader.fieldnames) != len(required) or set(reader.fieldnames) != required:
        raise ValueError("report headers do not match the normalized contract")
    if event == "search_query_import" and not reviewed_for_personal_data:
        raise ValueError("query exports require a recorded personal-data review before import")
    rows = []
    allowed = public_paths()
    for raw in reader:
        if None in raw or any(v is None for v in raw.values()):
            raise ValueError("malformed CSV row")
        start, end = date.fromisoformat(raw["period_start"]), date.fromisoformat(raw["period_end"])
        if start > end or end > today() or start < today() - timedelta(days=RETENTION_DAYS - 1):
            raise ValueError("report period is reversed, in the future, or outside retention")
        row = {"clicks": count_value(raw["clicks"], optional=True)}
        if event == "conversion_import":
            if raw["tracking_id"] != "shopnow047c-20":
                raise ValueError("report belongs to a different tracking ID")
            row.update({"tracking_id": raw["tracking_id"],
                        "eligible_sessions": count_value(raw["eligible_sessions"], optional=True),
                        "reported_orders": count_value(raw["reported_orders"], optional=True)})
        else:
            query = raw["query"].strip()
            # A conservative backstop, NOT a claim to reliably detect every name/address.
            if (not query or len(query) > 160 or re.search(r"[@\d\x00-\x1f]|https?://", query)):
                raise ValueError("query rejected by the conservative personal-data backstop")
            if raw["page"] not in allowed:
                raise ValueError("search report page is not in the static registry")
            pos = float(raw["average_position"]) if raw["average_position"] else None
            if pos is not None and (not math.isfinite(pos) or pos < 1):
                raise ValueError("invalid reported average position")
            row.update({"query": query, "page": raw["page"],
                        "impressions": count_value(raw["impressions"], optional=True), "average_position": pos})
        rows.append((start.isoformat(), end.isoformat(), row))
    if not rows:
        raise ValueError("empty report is not evidence of zero orders")
    digest = hashlib.sha256(content).hexdigest()
    with store.connect() as db:
        store.purge(db, today())
        if db.execute("SELECT 1 FROM report_imports WHERE sha256=? AND event=?", (digest, event)).fetchone():
            return 0  # idempotent; no second copy of the same file
        db.execute("INSERT INTO report_imports VALUES(?,?,?,?,?,?)", (
            digest, event, datetime.now(timezone.utc).isoformat(), source_url, channel, len(rows)))
        for number, (start, end, row) in enumerate(rows, 1):
            db.execute("INSERT INTO report_rows VALUES(?,?,?,?,?,?)", (
                digest, event, number, start, end, json.dumps(row, sort_keys=True, allow_nan=False)))
    return len(rows)


class Budget:
    """Global in-memory request budget: no IP hash, fingerprint or visitor key."""
    def __init__(self):
        self.lock = threading.Lock()
        self.minute = -1
        self.used = 0

    def accept(self):
        with self.lock:
            minute = int(time.monotonic() // 60)
            if minute != self.minute:
                self.minute, self.used = minute, 0
            self.used += 1
            return self.used <= 600


class Handler(BaseHTTPRequestHandler):
    server_version = "CounterNotes/1"

    def log_message(self, *_):
        pass  # stdlib access/error logging would expose addresses and request paths

    def send(self, status: int, body: bytes = b"", content_type: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def origin_allowed(self):
        origin = self.headers.get("Origin", "")
        if origin in self.server.origins:
            return True
        if self.server.preview:
            value = urlsplit(origin)
            return (value.scheme == "https" and value.netloc == self.headers.get("Host")
                    and value.hostname is not None and value.hostname.endswith(".e2b.app"))
        return False

    def do_POST(self):  # noqa: N802
        if urlsplit(self.path).query or strip_prefix(self.path) != "/api/events":
            self.send(404)
            return
        if not self.origin_allowed():
            self.send(403)
            return
        if not self.server.budget.accept():
            self.send(429)
            return
        if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self.send(415)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send(400)
            return
        if self.headers.get("Transfer-Encoding") or length <= 0 or length > MAX_BODY:
            self.send(413)
            return
        try:
            self.connection.settimeout(5)
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict) or set(payload) != {"events"}:
                raise ValueError("events wrapper required")
            events = payload["events"]
            if not isinstance(events, list) or not 1 <= len(events) <= 20:
                raise ValueError("batch size invalid")
            validated = [validate_event(ev, self.server.allowed_pages) for ev in events]
            self.server.store.add(validated)
        except (ValueError, TypeError, KeyError, TimeoutError, UnicodeError):
            self.send(400)
            return
        except sqlite3.Error:
            self.send(503)  # no request/payload logging
            return
        self.send(204)

    def do_HEAD(self):  # noqa: N802
        self.do_GET()

    def do_GET(self):  # noqa: N802
        raw = urlsplit(self.path)
        path = strip_prefix(unquote(raw.path))
        if path == "/api/health":
            self.send(200, json.dumps({"status": "ok", "retention_days": RETENTION_DAYS,
                                     "public_events": sorted(PUBLIC_EVENTS), "mode": "preview" if self.server.preview else "self_hosted"}).encode())
            return
        if path == "/assets/js/measurement-config.js":
            prefix = "/Zone2" if raw.path.startswith("/Zone2/") else ""
            config = {"enabled": True, "endpoint": prefix + "/api/events", "mode": "preview" if self.server.preview else "self_hosted"}
            self.send(200, ("window.CN_MEASUREMENT = Object.freeze(" + json.dumps(config) + ");\n").encode(), "text/javascript")
            return
        if not self.server.serve_static:
            self.send(404)
            return
        rel = Path(path.lstrip("/"))
        if path.endswith("/"):
            rel /= "index.html"
        file = (self.server.root / rel).resolve()
        if (not file.is_relative_to(self.server.root) or any(p.startswith(".") for p in rel.parts)
                or (rel.parts and rel.parts[0] in EXCLUDED) or file.suffix not in SAFE_SUFFIXES or not file.is_file()):
            self.send(404)
            return
        self.send(200, file.read_bytes(), mimetypes.guess_type(file)[0] or "application/octet-stream")


def make_server(host="0.0.0.0", port=8080, *, db_path=None, origins=(), preview=False, serve_static=True, site_root=ROOT):
    if not origins and not preview:
        raise ValueError("an explicit HTTPS site origin is required outside preview mode")
    for origin in origins:
        u = urlsplit(origin)
        if (u.scheme not in {"http", "https"} or u.path or u.query or u.fragment or not u.netloc
                or (u.scheme != "https" and u.hostname not in {"localhost", "127.0.0.1"})):
            raise ValueError("origins must be exact HTTPS origins (HTTP is allowed only for local tests)")
    server = ThreadingHTTPServer((host, port), Handler)
    server.store = Store(Path(db_path or os.environ.get("CN_ANALYTICS_DB", ROOT / ".local" / "analytics.sqlite3")))
    server.origins, server.preview, server.serve_static = set(origins), preview, serve_static
    server.root = Path(site_root).resolve()
    server.allowed_pages, server.budget = public_paths(server.root), Budget()
    return server


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=ROOT / ".local" / "analytics.sqlite3")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve")
    serve.add_argument("--port", type=int, default=8080)
    serve.add_argument("--origin", action="append", default=[])
    serve.add_argument("--preview", action="store_true")
    serve.add_argument("--endpoint-only", action="store_true")
    serve.add_argument("--site-root", type=Path, default=ROOT)
    sub.add_parser("export")
    sub.add_parser("purge")
    imp = sub.add_parser("import-report")
    imp.add_argument("--file", required=True, type=Path)
    imp.add_argument("--event", choices=sorted(REPORT_EVENTS), required=True)
    imp.add_argument("--source-url", required=True)
    imp.add_argument("--channel", required=True)
    imp.add_argument("--authorized", action="store_true")
    imp.add_argument("--reviewed-for-personal-data", action="store_true")
    args = parser.parse_args()
    if args.command == "serve":
        server = make_server(port=args.port, db_path=args.db, origins=args.origin,
                             preview=args.preview, serve_static=not args.endpoint_only, site_root=args.site_root)
        print(f"Counter Notes {'preview' if args.preview else 'self-hosted'} service on 0.0.0.0:{args.port}; access logs disabled", flush=True)
        server.serve_forever()
        return
    store = Store(args.db)
    if args.command == "export":
        print(json.dumps(store.export(), indent=2))
    elif args.command == "purge":
        with store.connect() as db:
            store.purge(db, today())
        print("Retention applied")
    else:
        n = import_report(store, args.file.read_bytes(), args.event, args.source_url, args.channel,
                          authorized=args.authorized, reviewed_for_personal_data=args.reviewed_for_personal_data)
        print(f"Imported {n} rows; duplicate files are not imported twice")


if __name__ == "__main__":
    main()
