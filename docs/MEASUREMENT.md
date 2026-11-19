# Measurement: implemented is not deployed

Checked **2026-11-19**. Production GitHub Pages has **no connected collector**. The committed
`assets/js/measurement-config.js` is deliberately disabled. A static host cannot run POST handlers:
[GitHub's official Pages description](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
The previous browser-local event queue has been removed; it never provided sitewide analytics.

## Five defined events

| ID | Event | Ingestion / evidence boundary | Production status | Official criterion (not proof of implementation) |
|---|---|---|---|---|
| EV-01 | `page_view` | Public POST; allowlisted page, server UTC day | Implemented; not deployed | [Amazon policies](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-02 | `product_link_click` | Public POST; page + static P1–P5 key | Implemented; not deployed | [Amazon policies](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-03 | `disclosure_view` | Public POST; at least half the strip intersects viewport | Implemented; not deployed | [Amazon policies](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-04 | `conversion_import` | Local CLI; authorized Associates export, period/source/channel/hash | Implemented; no real export available | [Amazon policies](https://affiliate-program.amazon.com/help/operating/policies) |
| EV-05 | `search_query_import` | Local CLI; authorized, personal-data-reviewed Search Console export | Implemented; no real export available | [Search Console](https://support.google.com/webmasters/answer/7576553?hl=en) |

Raw loads and clicks are **not unique people or eligible Amazon Sessions**. A visibility event does
not establish reading or individual sequencing. No browser purchase/conversion event is accepted.
No conversion score, inferred order, expected revenue or profitable niche is computed.
[Amazon's policies](https://affiliate-program.amazon.com/help/operating/policies) define attribution
and prohibit artificial clicks. [Google describes query performance reporting](https://support.google.com/webmasters/answer/7576553?hl=en).

## Run the real service locally

```sh
python3 tools/test_analytics.py
python3 tools/analytics_server.py --db .local/preview.sqlite3 serve --preview --port 8080
```

It binds to `0.0.0.0`. The service itself serves an enabled, same-origin config only while it runs.
Preview allows the proxied `*.e2b.app` origin matching the Host header; this is explicitly preview
mode, not a production-domain authorization. Browser automation is excluded from collection.
For the exact deployed projection add `--site-root _site` after building it.

For production, use an **owner-controlled HTTPS reverse proxy** and exact origin:

```sh
python3 tools/analytics_server.py --db /private/analytics.sqlite3 serve \
  --origin https://YOUR-OWN-HOST --port 8080
```

The placeholder is documentation, not a provisioned host. No cloud account, domain or hosting
credential exists here. Do not expose the Python service without TLS, access-log controls,
process supervision, backup/retention configuration and a jurisdiction-appropriate privacy review.
If the static site remains on GitHub Pages, a controlled same-origin proxy/custom-domain deployment
is necessary; changing a config string alone does not create a working endpoint.

### Contract

- `POST /api/events` (also `/Zone2/api/events`): JSON `{ "events": [...] }`, max 20 events / 8 KiB.
- Exact allowed origin required; no wildcard CORS; no redirect.
- Each event has `name` and an exact registered `page`, without query/fragment.
- Click additionally has `product: "P1"` through `"P5"`; disclosure has `position: "strip"`.
- Unknown fields, client timestamps/counts/IDs, unknown paths, browser report events, and oversized
  requests are rejected. An invalid batch writes nothing. Successful persistence returns HTTP 204.
- `GET /api/health` publishes service status, not counts or a database path.
- No public report-import, metrics-export, raw-database or admin endpoint.
- Client uses credentialless same-origin fetch, no referrer, no cookie or analytics browser storage.
  It honors GPC/DNT. No persistent retry queue or implied exactly-once guarantee.
- Basic automation exclusion and global request budget do not prove events came from humans.

## Import reports only when authorized evidence exists

Keep original exports **private**. Normalize only relevant aggregate columns; retain the mapping
and original alongside the normalized file for a human provenance review. A CLI flag asserts the
operator's authorization; it is not an authentication of Amazon/Google or proof of file origin.
No report sample is checked into production data and no real data has been imported this session.

EV-04 CSV headers (exact, any order):

```text
period_start,period_end,clicks,eligible_sessions,reported_orders,tracking_id
```

`tracking_id` must be `shopnow047c-20`. Dates are ISO dates. Counts must be explicitly reported
non-negative integers or blank. **Do not derive eligible_sessions from clicks or page views.** A
missing count is stored as null, not zero. Zero orders must be explicitly reported, not assumed.

```sh
python3 tools/analytics_server.py --db .local/analytics.sqlite3 import-report \
  --file /private/normalized-associates.csv --event conversion_import \
  --source-url https://affiliate-program.amazon.com/home/reports --channel organic --authorized
```

EV-05 CSV headers:

```text
period_start,period_end,clicks,query,page,impressions,average_position
```

Use only a personal-data-reviewed first-party export; the conservative automatic backstop refuses
queries with digits, email-like text, URLs or controls but **cannot reliably recognize every name or
address**. The review gate is necessary; do not call it an automatic privacy guarantee.

```sh
python3 tools/analytics_server.py --db .local/analytics.sqlite3 import-report \
  --file /private/normalized-search.csv --event search_query_import \
  --source-url https://search.google.com/search-console --channel organic \
  --authorized --reviewed-for-personal-data
```

Every import records timestamp, source, static channel, period and normalized-file SHA-256.
Identical file imports are idempotent. Different files can overlap periods; the export intentionally
does not sum overlapping reports or infer a conversion rate. Review superseded/overlapping exports
before analysis. Browser events and imported report counts remain different tables.

```sh
python3 tools/analytics_server.py --db .local/analytics.sqlite3 export
python3 tools/analytics_server.py --db .local/analytics.sqlite3 purge
```

Default retention is **90 days**; ingestion/export purge old values. Schedule `purge` daily so an idle
service also expires data. Keep runtime databases and original reports out of Git and the web root.
Disable application/proxy request-body and access logs; the application suppresses stdlib logs, but
upstream hosting logs remain the operator's responsibility. GitHub independently logs IPs for security
as its [official Pages documentation explains](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Production acceptance gate

1. An owner-controlled HTTPS route actually answers health and a persisted test batch in an isolated DB.
2. Invalid origins/fields/browser conversions are rejected; private files and exports are not served.
3. Host logging, retention, legal basis/consent and the operator notice have been reviewed.
4. Remove test data; activate same-origin production config only on the running service.
5. Do not fabricate events or click affiliate links to test attribution. Account destination/report
   confirmation must follow the enrolled Associates workflow without artificial traffic or purchases.
6. Until this gate passes, report **not connected**, not LIVE.
