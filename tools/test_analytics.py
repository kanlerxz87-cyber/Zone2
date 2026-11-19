#!/usr/bin/env python3
"""Isolated synthetic tests; no test traffic reaches Amazon or a production database."""
from __future__ import annotations

import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from datetime import timedelta
from pathlib import Path

from analytics_server import MAX_BODY, Store, import_report, make_server, today, validate_event


class CounterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'test.sqlite3'
        self.store = Store(self.db)
        self.pages = {'/', '/index.html'}

    def tearDown(self):
        self.temp.cleanup()

    def test_page_view(self):
        self.assertEqual(validate_event({'name': 'page_view', 'page': '/'}, self.pages), ('page_view', '/', '', ''))

    def test_all_five_products(self):
        for n in range(1, 6):
            validate_event({'name': 'product_link_click', 'page': '/', 'product': f'P{n}'}, self.pages)

    def test_disclosure(self):
        validate_event({'name': 'disclosure_view', 'page': '/', 'position': 'strip'}, self.pages)

    def test_personal_data_and_unknown_fields_refused(self):
        for field in ['ip', 'user_agent', 'email', 'session', 'referrer', 'r', 'day', 'timestamp', 'count']:
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_event({'name': 'page_view', 'page': '/', field: 'x'}, self.pages)

    def test_query_or_arbitrary_path_refused(self):
        for page in ['/?email=x', '/#fragment', '/visitor/name', 9, None, ['unhashable']]:
            with self.subTest(page=page), self.assertRaises(ValueError):
                validate_event({'name': 'page_view', 'page': page}, self.pages)

    def test_browser_cannot_claim_conversions_or_queries(self):
        for name in ['conversion_import', 'search_query_import', 'purchase', None]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                validate_event({'name': name, 'page': '/'}, self.pages)

    def test_bad_product_or_position_refused(self):
        for raw in [{'name': 'product_link_click', 'page': '/', 'product': 'user-123'},
                    {'name': 'disclosure_view', 'page': '/', 'position': 'guessed'}]:
            with self.assertRaises(ValueError):
                validate_event(raw, self.pages)

    def test_aggregates_not_raw_events(self):
        self.store.add([('page_view', '/', '', '')] * 3)
        rows = self.store.export()['daily_events']
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['count'], 3)
        self.assertEqual(set(rows[0]), {'day', 'name', 'page', 'product', 'position', 'count'})

    def test_retention(self):
        self.store.add([('page_view', '/', '', '')], day=today() - timedelta(days=91))
        self.store.add([('page_view', '/', '', '')])
        self.assertEqual(len(self.store.export()['daily_events']), 1)

    def csv(self, event='conversion_import', **changes):
        d = today().isoformat()
        if event == 'conversion_import':
            row = dict(period_start=d, period_end=d, clicks='2', eligible_sessions='', reported_orders='0', tracking_id='shopnow047c-20')
        else:
            row = dict(period_start=d, period_end=d, clicks='2', query='basket or oven air fryer', page='/', impressions='4', average_position='3.5')
        row.update(changes)
        return (','.join(row) + '\n' + ','.join(row.values()) + '\n').encode()

    def imp(self, content=None, **kwargs):
        return import_report(self.store, content or self.csv(), 'conversion_import',
                             'https://affiliate-program.amazon.com/home/reports', 'organic', **kwargs)

    def test_authorization_required(self):
        with self.assertRaises(ValueError):
            self.imp(authorized=False)

    def test_import_provenance_and_missing_sessions_stay_null(self):
        self.assertEqual(self.imp(authorized=True), 1)
        result = self.store.export()
        self.assertEqual(len(result['report_imports'][0]['sha256']), 64)
        row = json.loads(result['report_rows'][0]['payload'])
        self.assertIsNone(row['eligible_sessions'])
        self.assertEqual(row['reported_orders'], 0)
        self.assertEqual(result['daily_events'], [])

    def test_identical_import_idempotent(self):
        self.assertEqual(self.imp(authorized=True), 1)
        self.assertEqual(self.imp(authorized=True), 0)

    def test_wrong_tag_refused(self):
        with self.assertRaises(ValueError):
            self.imp(self.csv(tracking_id='someone-20'), authorized=True)

    def test_invalid_or_future_or_stale_period_refused(self):
        for value in [(today()+timedelta(days=1)).isoformat(), (today()-timedelta(days=91)).isoformat()]:
            with self.assertRaises(ValueError):
                self.imp(self.csv(period_start=value, period_end=value), authorized=True)

    def test_negative_or_inferred_counts_refused(self):
        for value in ['-1', 'estimated 2', '3.1', 'NaN']:
            with self.assertRaises(ValueError):
                self.imp(self.csv(clicks=value), authorized=True)

    def test_no_arbitrary_source_or_extra_fields(self):
        with self.assertRaises(ValueError):
            import_report(self.store, self.csv(), 'conversion_import', 'https://example.com/report', 'organic', authorized=True)
        with self.assertRaises(ValueError):
            self.imp(self.csv(email='someone@example.com'), authorized=True)

    def test_search_requires_personal_data_review(self):
        with self.assertRaises(ValueError):
            import_report(self.store, self.csv('search_query_import'), 'search_query_import',
                          'https://search.google.com/search-console', 'organic', authorized=True)

    def test_search_import_and_personal_data_backstop(self):
        kw = dict(authorized=True, reviewed_for_personal_data=True)
        self.assertEqual(import_report(self.store, self.csv('search_query_import'), 'search_query_import',
                                      'https://search.google.com/search-console', 'organic', **kw), 1)
        with self.assertRaises(ValueError):
            import_report(self.store, self.csv('search_query_import', query='name@example.com'), 'search_query_import',
                          'https://search.google.com/search-console', 'organic', **kw)


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.server = make_server(host='127.0.0.1', port=0, db_path=Path(cls.temp.name)/'http.sqlite3',
                                 origins=['http://localhost'], preview=True)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp.cleanup()

    def req(self, method, path, data=None, **headers):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=10)
        body = json.dumps(data) if isinstance(data, (dict, list)) else data
        h = {'Origin': 'http://localhost', 'Content-Type': 'application/json'}
        h.update(headers)
        conn.request(method, path, body=body, headers=h)
        response = conn.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        conn.close()
        return result

    def test_valid_and_acknowledged(self):
        status, headers, _ = self.req('POST', '/api/events', {'events': [{'name': 'page_view', 'page': '/'}]})
        self.assertEqual(status, 204)
        self.assertNotIn('Set-Cookie', headers)

    def test_project_subpath(self):
        self.assertEqual(self.req('POST', '/Zone2/api/events', {'events': [{'name': 'page_view', 'page': '/'}]})[0], 204)

    def test_cross_origin_and_missing_origin_refused(self):
        for origin in ['', 'https://attacker.example']:
            self.assertEqual(self.req('POST', '/api/events', {'events': []}, Origin=origin)[0], 403)

    def test_wrong_content_type_and_oversize(self):
        self.assertEqual(self.req('POST', '/api/events', '{}', **{'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.req('POST', '/api/events', 'x' * (MAX_BODY + 1))[0], 413)

    def test_atomic_batch_rejects_bad_event(self):
        before = self.server.store.export()['daily_events']
        self.assertEqual(self.req('POST', '/api/events', {'events': [{'name': 'page_view', 'page': '/'}, {'name': 'purchase', 'page': '/'}]})[0], 400)
        self.assertEqual(before, self.server.store.export()['daily_events'])

    def test_private_files_not_served(self):
        for path in ['/.git/config', '/.local/analytics.sqlite3', '/tools/analytics_server.py', '/../COORDINATION.md', '/api/metrics']:
            self.assertEqual(self.req('GET', path)[0], 404, path)

    def test_live_config_only_when_service_exists(self):
        status, _, body = self.req('GET', '/Zone2/assets/js/measurement-config.js')
        self.assertEqual(status, 200)
        self.assertIn(b'"enabled": true', body)
        self.assertIn(b'/Zone2/api/events', body)

    def test_health_is_not_a_public_metrics_export(self):
        _, _, body = self.req('GET', '/api/health')
        data = json.loads(body)
        self.assertEqual(data['status'], 'ok')
        self.assertNotIn('daily_events', data)

    def test_production_origin_required(self):
        with self.assertRaises(ValueError):
            make_server(port=0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
