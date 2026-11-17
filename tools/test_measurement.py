#!/usr/bin/env python3
"""Gate the measurement layer — tools/test_measurement.py.

The defect class this exists to prevent: a page claims "we measure clicks" while
nothing measures clicks, or a collector quietly starts keeping per-visitor data.
Each check below is a negative test with a comment naming the claim it protects.

Run: python3 tools/test_measurement.py
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import analytics_server  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, cond: bool, note: str = "") -> None:
    RESULTS.append((name, bool(cond), note))


def rejects(store, event, fields) -> bool:
    try:
        store.validate(event, dict(fields))
    except analytics_server.Rejected:
        return True
    return False


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="zone2-analytics-"))
    try:
        store = analytics_server.EventStore(tmp)

        # 1. The only recordable events are EV-01..EV-03. EV-04 (conversion) is
        #    BLOCKED on Amazon's reporting: the endpoint must not accept it, or
        #    the site could fabricate conversion data.
        check("EV-04 conversion cannot be recorded",
              rejects(store, "conversion", {"day": "2026-11-17"}),
              "endpoint accepts only " + str(sorted(analytics_server.EVENT_FIELDS)))
        check("EV-05 earnings cannot be recorded",
              rejects(store, "earnings", {"day": "2026-11-17"}))

        # 2. MP-01: no per-visitor data, spelled as code. Every identifier key
        #    in the design's 'deliberately not collected' lists must be refused.
        for key in ("user_id", "session_id", "fingerprint", "email", "ip", "device_id", "resolution", "user_agent"):
            if not rejects(store, "page_view", {"day": "2026-11-17", key: "x"}):
                check(f"per-visitor key refused: {key}", False, "accepted a per-visitor field")
                break
        else:
            check("per-visitor keys all refused (MP-01)", True)

        # 3. Unknown fields are rejected, not silently dropped — an undeclared
        #    field is how scope creep enters a schema.
        check("undeclared field refused", rejects(store, "page_view", {"day": "2026-11-17", "mood": "happy"}))

        # 4. A declared field with a non-string value is rejected.
        check("non-string field refused", rejects(store, "page_view", {"day": "2026-11-17", "viewport_class": 5}))

        # 5. day must be a calendar day — the design keeps a day, not a
        #    timestamp, because a timestamp narrows a visit to a person.
        check("timestamp refused as day", rejects(store, "page_view", {"day": "2026-11-17T10:22:33Z"}))

        # 6. Valid events record and aggregate per product.
        p = store.validate("product_link_click", {
            "day": "2026-11-17", "page_path": "/Zone2/", "product_key": "B0CDY277D3",
            "link_state": "TAGGED", "placement": "spec-table"})
        store.record(p)
        store.record(store.validate("page_view", {"day": "2026-11-17", "page_path": "/Zone2/"}))
        agg = store.aggregates()
        check("EV-02 aggregates by product_key",
              agg["products"].get("B0CDY277D3") == 1 and agg["total"] == 2, json.dumps(agg))

        # 7. /subscribe stores exactly email + page_path + day — reader capture
        #    with nothing else attached.
        row = store.record_reader({"email": "reader@example.org", "page_path": "/Zone2/"})
        check("subscribe stores only the opt-in fields", set(row) == {"email", "page_path", "day"}, str(row))
        check("subscribe refuses extra fields", _rejects_reader(store, {"email": "a@b.co", "ip": "1.2.3.4"}))
        check("subscribe refuses malformed email", _rejects_reader(store, {"email": "not-an-address"}))

        # 8. Retention: --prune folds expiring lines into daily.json and the
        #    aggregates survive (MI-02's default policy).
        store.record(store.validate("page_view", {"day": "2020-01-01", "page_path": "/Zone2/old"}))
        removed = store.prune(retention_days=30)
        check("prune expires old raw rows", removed == 1, f"removed={removed}")
        check("prune preserves aggregates", store.aggregates()["total"] == 3, json.dumps(store.aggregates()))

        # 9. Bot filter: crawler user-agents are dropped (MI-03's minimal
        #    filter — explicitly not a bot policy).
        check("crawler user-agent dropped",
              analytics_server.is_bot("Mozilla/5.0 (compatible; Googlebot/2.1)")
              and analytics_server.is_bot("") and analytics_server.is_bot("curl/8.0")
              and not analytics_server.is_bot("Mozilla/5.0 (Macintosh) Safari/605"))

        # 10. End-to-end over HTTP: /healthz and /events must return aggregates
        #     and nothing personal; /collect must reject a conversion attempt.
        server = ThreadingHTTPServer(("127.0.0.1", 0), analytics_server.make_handler(store))
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()

        def post(path, payload, ua="Mozilla/5.0"):
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}{path}", data=json.dumps(payload).encode(),
                headers={"Content-Type": "application/json", "User-Agent": ua}, method="POST")
            try:
                with urllib.request.urlopen(req) as resp:
                    return resp.status, json.loads(resp.read().decode())
            except urllib.error.HTTPError as err:
                return err.code, json.loads(err.read().decode())

        code, body = post("/collect", {"event": "disclosure_view", "day": "2026-11-17",
                                       "page_path": "/Zone2/", "disclosure_position": "under-masthead"})
        check("HTTP /collect records EV-03", code == 202 and body.get("status") == "recorded", str(body))
        code, body = post("/collect", {"event": "conversion", "day": "2026-11-17"})
        check("HTTP /collect refuses conversion", code == 422, str(body))
        code, body = post("/collect", {"event": "page_view", "day": "2026-11-17", "page_path": "/x"},
                          ua="Mozilla/5.0 (compatible; bingbot/2.0)")
        check("HTTP bot dropped", code == 202 and body.get("status") == "dropped", str(body))
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/events") as resp:
            events = json.loads(resp.read().decode())
        raw_text = json.dumps(events)
        check("HTTP /events is aggregates only",
              "@" not in raw_text and "email" not in raw_text and events.get("total") == 4, raw_text[:120])
        server.shutdown()

        # 11. The client collector: source-level privacy checks and the exact
        #     event set. This is the "no cookies, no identifiers" claim tested
        #     against the code that makes it.
        js = (REPO / "assets" / "js" / "analytics.js").read_text(encoding="utf-8")
        banned_snippets = ["document.cookie", "localStorage", "sessionStorage", "indexedDB",
                           "toDataURL", "getUserMedia", "userAgentData", "hardwareConcurrency",
                           "visitor_id", "user_id", "session_id", "device_id"]
        present = [s for s in banned_snippets if s in js]
        check("client keeps no identifier APIs or keys", not present, f"found {present}")
        check("client fires exactly EV-01..EV-03",
              all(f'record("{ev}"' in js or f"record('{ev}'" in js
                  for ev in ("page_view", "product_link_click", "disclosure_view"))
              and "conversion" not in js.split("*/")[-1], "event set drifted")
        check("client sends host-only referrer", "hostname" in js and "document.referrer" in js)

        # 12. Status discipline: SHIPPED requires the shipped files to exist;
        #     LIVE is forbidden while MI-01 (the sink) is unresolved — the page
        #     may not read LIVE while nothing can collect.
        design = json.loads((REPO / "docs" / "measurement-t40.json").read_text(encoding="utf-8"))
        files_exist = all((REPO / f).is_file() for f in (
            "assets/js/analytics.js", "tools/analytics_server.py", "tools/test_measurement.py"))
        shipped = [e for e in design["events"] if e["status"] == "SHIPPED"]
        live = [e for e in design["events"] if e["status"] == "LIVE"]
        check("SHIPPED rows have shipping files", bool(shipped) and files_exist)
        mi01 = next((g for g in design["open_items"] if g["id"] == "MI-01"), {})
        mi01_open = "unresolved" in str(mi01.get("status", "")).lower()
        check("no row reads LIVE while MI-01 is unresolved",
              not live or not mi01_open, f"live={[e['id'] for e in live]} mi01={mi01.get('status')}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    failed = [r for r in RESULTS if not r[1]]
    for name, ok, note in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" — {note}" if note and not ok else ""))
    print(f"test_measurement: {len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    return 1 if failed else 0


def _rejects_reader(store, fields) -> bool:
    try:
        store.record_reader(dict(fields))
    except analytics_server.Rejected:
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
