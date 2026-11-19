"""Synthetic fixtures only; temporary databases never enter the public site or Git."""
import io
import json
import sqlite3
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from measurement.collector import Application, Invalid, Store, counter_event, import_report, utc_now


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.site = self.root / "site"
        self.site.mkdir()
        (self.site / "index.html").write_text("<html>synthetic test</html>")
        self.db = self.root / "data.sqlite3"
        self.app = Application(self.site, self.db, origin="https://publication.example")
        self.today = utc_now().date()

    def tearDown(self):
        self.temp.cleanup()

    def request(self, path="/Zone2/api/events", *, method="POST", body=None, origin="https://publication.example", **extra):
        raw = json.dumps(body if body is not None else {"events": [{"event": "page_view", "page": "index.html", "channel": "direct"}]}).encode()
        env = {"PATH_INFO": path, "REQUEST_METHOD": method, "HTTP_ORIGIN": origin, "CONTENT_TYPE": "text/plain;charset=UTF-8",
               "CONTENT_LENGTH": str(len(raw)), "wsgi.input": io.BytesIO(raw), **extra}
        result = {}
        def respond(code, headers):
            result.update(status=int(code.split()[0]), headers=dict(headers))
        result["body"] = b"".join(self.app(env, respond))
        return result

    def test_three_browser_events_aggregate(self):
        events = [{"event": "page_view", "page": "index.html", "channel": "search"},
                  {"event": "product_link_click", "page": "index.html", "product": "P5"},
                  {"event": "disclosure_view", "page": "index.html", "position": "strip"}]
        for _ in range(2):
            self.assertEqual(self.request(body={"events": events})["status"], 202)
        counts = self.app.store.export()["daily_counts"]
        self.assertEqual(len(counts), 3)
        self.assertTrue(all(row["count"] == 2 for row in counts))
        self.assertTrue(all(row["day"] == self.today.isoformat() for row in counts))

    def test_unknown_personal_fields_refused_atomically(self):
        for key in ("ip", "user_agent", "email", "session_id", "timestamp", "referrer", "url"):
            with self.subTest(key=key):
                event = {"event": "page_view", "page": "index.html", "channel": "direct", key: "synthetic"}
                self.assertEqual(self.request(body={"events": [event]})["status"], 400)
        self.assertFalse(self.app.store.export()["daily_counts"])

    def test_unregistered_or_query_paths_rejected(self):
        for page in ("unknown.html", "index.html?email=synthetic", "../secret", "/Zone2/index.html"):
            event = {"event": "page_view", "page": page, "channel": "direct"}
            self.assertEqual(self.request(body={"events": [event]})["status"], 400)

    def test_unknown_product_and_dimensions_rejected(self):
        for event in ({"event": "product_link_click", "product": "user-123"},
                      {"event": "page_view", "channel": "private-host.example"},
                      {"event": "disclosure_view", "position": "guessed"}):
            event["page"] = "index.html"
            self.assertEqual(self.request(body={"events": [event]})["status"], 400)

    def test_import_events_cannot_be_forged_in_browser(self):
        for event in ("conversion_import", "search_query_import", "purchase"):
            self.assertEqual(self.request(body={"events": [{"event": event, "page": "index.html"}]})["status"], 400)

    def test_entire_batch_validated_before_any_write(self):
        events = [{"event": "page_view", "page": "index.html", "channel": "direct"}, {"event": "purchase", "page": "index.html"}]
        self.assertEqual(self.request(body={"events": events})["status"], 400)
        self.assertFalse(self.app.store.export()["daily_counts"])

    def test_cross_origin_no_origin_and_lookalike_refused(self):
        for origin in ("", "null", "https://evil.example", "https://publication.example.evil.example"):
            self.assertEqual(self.request(origin=origin)["status"], 403)

    def test_no_production_origin_means_no_writes(self):
        self.app.origin = ""
        self.assertEqual(self.request()["status"], 403)

    def test_privacy_signals_honored(self):
        for header in ("HTTP_DNT", "HTTP_SEC_GPC"):
            result = self.request(**{header: "1"})
            self.assertEqual(json.loads(result["body"])["accepted"], 0)
        self.assertFalse(self.app.store.export()["daily_counts"])

    def test_size_media_method_and_batch_limits(self):
        self.assertEqual(self.request(CONTENT_LENGTH="9000")["status"], 413)
        self.assertEqual(self.request(CONTENT_LENGTH="0")["status"], 413)
        self.assertEqual(self.request(CONTENT_TYPE="application/x-www-form-urlencoded")["status"], 415)
        self.assertEqual(self.request(method="GET")["status"], 405)
        self.assertEqual(self.request(body={"events": []})["status"], 400)
        self.assertEqual(self.request(body={"events": [{}] * 11})["status"], 400)

    def test_bad_json_and_nested_values_safe(self):
        self.assertEqual(self.request(**{"wsgi.input": io.BytesIO(b"not json")})["status"], 400)
        self.assertEqual(self.request(body={"events": [{"event": [], "page": "index.html"}]})["status"], 400)

    def test_api_has_no_cookies_cors_or_public_stats(self):
        headers = self.request()["headers"]
        self.assertNotIn("Set-Cookie", headers)
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(headers["Cache-Control"], "no-store")
        for path in ("/Zone2/api/stats", "/Zone2/api/import", "/Zone2/.git/config", "/Zone2/../data.sqlite3", "/Zone2/%2e%2e/data.sqlite3"):
            self.assertEqual(self.request(path, method="GET")["status"], 404)

    def test_runtime_config_is_same_origin(self):
        config = json.loads(self.request("/Zone2/measurement.json", method="GET")["body"])
        self.assertTrue(config["enabled"])
        self.assertEqual(config["endpoint"], "api/events")
        self.assertEqual(config["mode"], "self_hosted")

    def test_static_site_works_and_head_has_no_body(self):
        self.assertEqual(self.request("/Zone2/", method="GET")["status"], 200)
        self.assertEqual(self.request("/Zone2/", method="HEAD")["body"], b"")
        self.assertNotIn(b"daily_counts", self.request("/healthz", method="GET")["body"])

    def test_budget_is_global_not_ip_keyed(self):
        self.app.budget.tokens = 0
        self.assertEqual(self.request()["status"], 429)
        self.assertFalse(self.app.store.export()["daily_counts"])

    def test_retention_prunes_old_daily_counts(self):
        event = counter_event({"event": "page_view", "page": "index.html", "channel": "direct"}, {"index.html"})
        self.app.store.increment([event], day=self.today - timedelta(days=91))
        self.app.store.increment([event])
        self.assertEqual(len(self.app.store.export()["daily_counts"]), 1)

    def report(self, source="amazon_associates"):
        row = {"tracking_id": "shopnow047c-20", "channel": "amazon_associates", "eligible_sessions": None, "clicks": 7, "reported_orders": 2}
        if source == "google_search_console":
            row = {"page": "index.html", "query": "air fryer capacity comparison", "impressions": 11, "clicks": 2, "average_position": 12.5}
        return {"source": source, "period_start": self.today.isoformat(), "period_end": self.today.isoformat(), "rows": [row]}

    def do_import(self, doc, *, attestation=None):
        path = self.root / "synthetic-report.json"
        path.write_text(json.dumps(doc))
        return import_report(self.app.store, path, authorized_source=attestation or doc["source"], pages={"index.html"},
                             allowed_queries={"air fryer capacity comparison"})

    def test_authorized_conversion_report_records_provenance_not_forecast(self):
        result = self.do_import(self.report())
        self.assertEqual(result["event"], "conversion_import")
        exported = self.app.store.export()
        row = exported["campaign_observations"][0]
        self.assertIsNone(row["eligible_sessions"])
        self.assertIsNone(row["page"])
        self.assertEqual(row["reported_orders"], 2)
        self.assertEqual(len(row["sha256"]), 64)
        self.assertIn("imported_at", exported["provenance"][0])
        self.assertFalse(exported["daily_counts"])

    def test_search_report_preserves_only_allowlisted_queries(self):
        result = self.do_import(self.report("google_search_console"))
        self.assertEqual(result["event"], "search_query_import")
        self.assertIsNone(self.app.store.export()["campaign_observations"][0]["reported_orders"])

    def test_import_hash_is_idempotent_and_overlaps_refused(self):
        doc = self.report()
        self.assertEqual(self.do_import(doc)["status"], "imported")
        self.assertEqual(self.do_import(doc)["status"], "already_imported")
        doc["rows"][0]["clicks"] = 9
        with self.assertRaises(Invalid):
            self.do_import(doc)
        self.assertEqual(len(self.app.store.export()["campaign_observations"]), 1)

    def test_attestation_wrong_tag_and_unknown_fields_fail(self):
        with self.assertRaises(Invalid):
            self.do_import(self.report(), attestation="google_search_console")
        for key, value in (("tracking_id", "other-20"), ("email", "synthetic"), ("clicks", -1), ("reported_orders", True)):
            doc = self.report()
            doc["rows"][0][key] = value
            with self.subTest(key=key), self.assertRaises(Invalid):
                self.do_import(doc)
        self.assertFalse(self.app.store.export()["provenance"])

    def test_unknown_queries_and_duplicate_dimensions_refused(self):
        doc = self.report("google_search_console")
        doc["rows"][0]["query"] = "somebody personal name"
        with self.assertRaises(Invalid):
            self.do_import(doc)
        doc = self.report()
        doc["rows"].append(doc["rows"][0].copy())
        with self.assertRaises(Invalid):
            self.do_import(doc)

    def test_future_inverted_and_expired_periods_refused(self):
        for start, end in ((1, 1), (-5, -6), (-91, -90)):
            doc = self.report()
            doc["period_start"] = (self.today + timedelta(days=start)).isoformat()
            doc["period_end"] = (self.today + timedelta(days=end)).isoformat()
            with self.subTest(start=start), self.assertRaises(Invalid):
                self.do_import(doc)

    def test_prune_import_retention(self):
        self.do_import(self.report())
        self.app.store.prune(today=self.today + timedelta(days=91))
        self.assertFalse(self.app.store.export()["campaign_observations"])
        self.assertFalse(self.app.store.export()["provenance"])

    def test_database_has_no_person_columns(self):
        with self.app.store.connect() as db:
            columns = [r[1] for table in ("daily_counts", "campaign_observations", "report_imports") for r in db.execute(f"PRAGMA table_info({table})")]
        for column in columns:
            self.assertFalse(any(word in column for word in ("visitor", "session_id", "cookie", "ip_address", "user_agent", "email")))


if __name__ == "__main__":
    unittest.main()
