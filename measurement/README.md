# Counter Notes measurement service

**State on 2026-11-19:** implemented and testable, not a permanent production deployment.
GitHub Pages is [static hosting](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).
It cannot run this writable endpoint. The committed `measurement.json` disables collection on Pages;
no events are queued on a reader's device. A temporary Arena preview is not a production analytics host.
No cloud account, DNS record, enrollment, or report is assumed.

## Run the complete site and collector

```sh
python3 tools/package_site.py
python3 -m measurement.collector serve --preview --port 8000
# open the preview at /Zone2/ (binds 0.0.0.0)
```

`--preview` accepts the Arena preview origin and localhost origins for testing. Its SQLite database
is **test data**, not production traffic. Browser-facing code uses same-origin relative URLs;
it never calls localhost from the reader's browser.

Production (on infrastructure controlled by the site owner, behind an HTTPS reverse proxy):

```sh
python3 tools/package_site.py
pip install -r measurement/requirements.txt
CN_PUBLIC_ORIGIN=https://YOUR-OWN-SITE.example CN_DB=/data/measurement.sqlite3 \
  gunicorn --bind 0.0.0.0:8080 --workers 2 --threads 4 \
  --access-logfile /dev/null measurement.collector:application
```

Keep the publication at `/Zone2/`, or explicitly update the shared base-path/canonical contract
before migration. A custom-domain migration also requires updating canonical URLs and Search Console;
do not publish two competing indexable copies. `CN_SITE` selects the generated `_site` directory.
`measurement/Dockerfile` is an alternative container deployment; build from the repository root after
packaging. Mount a persistent `/data` volume owned by UID 10001. Provisioning a permanent host or
changing DNS is deliberately not pretended to have happened.

### Reverse proxy and retention

* Terminate TLS, limit request bodies to 8 KB and concurrent connections, and require the expected Host.
* Disable access logs and request-body logging on the reverse proxy, CDN and application monitor.
  The application stores no IP/UA, but infrastructure sees network metadata. The claim is **not**
  that the entire internet connection is anonymous. GitHub itself documents IP security logging.
* No cross-origin collector or wildcard CORS. `CN_PUBLIC_ORIGIN` is mandatory for production writes.
* Daily counters retain 90 days. Every write prunes old counter buckets. Run
  `python3 -m measurement.collector prune` daily via cron for expiry during idle periods and
  for imported reports too. Apply the same 90-day maximum to backups; keep the database outside Git.
* DNT and Global Privacy Control stop collection. No cookies, browser storage, fingerprinting,
  user IDs, session IDs, raw referrers, destination parameters, query strings or raw request log.
* A global per-worker request budget reduces abuse without remembering IPs. It is **not bot detection**.
  Counts are events, not unique people or eligible sessions, and are susceptible to bots and retries.
* No public statistics/report route. Import and export are local operator CLI commands only.

## The five defined events

| Event | Input | Persistence and limitation |
|---|---|---|
| EV-01 `page_view` | Visible page load | UTC day, registered page, broad referrer channel, count. Not people/sessions. |
| EV-02 `product_link_click` | Trusted primary or middle click on a tagged direct Amazon link | UTC day, registered page, P1–P5, count. No redirect or purchase inference. |
| EV-03 `disclosure_view` | Actual IntersectionObserver intersection | UTC day, page, strip, count. No observer → unknown, not a fabricated view. Cannot reconstruct per-person order. |
| EV-04 `conversion_import` | Authorized Associates export, local import only | Dated/hash-addressed provenance + report values. Not accepted from browsers. |
| EV-05 `search_query_import` | Authorized Search Console export, local import only | Dated/hash-addressed provenance + reviewed topic queries. Not accepted from browsers. |

No raw event stream is kept. The SQLite primary key aggregates each daily event immediately.
EV-04/05 are represented by completed provenance records, not fake frontend events.

## Authorized report import

There are no reports or example performance rows in the production ledger. Use a normalized JSON
export with top-level `source`, `period_start`, `period_end`, and `rows`. Dates are ISO dates.
Source attestation is an **operator assertion**, not a cryptographic Amazon verification. Never import
a made-up report, customer-level data or an export you are not authorized to use.

* `amazon_associates` row keys: `tracking_id` (only `shopnow047c-20`), `channel`
  (only `amazon_associates`), `eligible_sessions`, `clicks`, `reported_orders`.
  Counts may be null when the report does not supply them. Never derive sessions from page views.
  Page/query attribution is deliberately absent because an account-level report cannot establish it.
* `google_search_console` row keys: `page` (registered relative HTML path), `query`
  (exact member of `measurement/query-allowlist.json`), `impressions`, `clicks`, `average_position`.
  Unknown queries are rejected, not logged. A regex cannot reliably detect names or other personal
  information; only reviewed, static buyer questions are admitted. This limits coverage deliberately.
* Unknown keys, negative counts, other tracking IDs, future/inverted/expired dates, duplicate
  dimensions and overlapping report periods are rejected transactionally. Identical file hashes
  are idempotent. Replacements require deliberate local review rather than silent double counting.

```sh
python3 -m measurement.collector import-report /secure/export.json --authorized-source amazon_associates
python3 -m measurement.collector import-report /secure/search.json --authorized-source google_search_console
python3 -m measurement.collector summary > /secure/aggregate-export.json
```

Exports include timestamp, source, channel, date range, eligible sessions (nullable), clicks,
reported orders (nullable) and SHA-256 provenance. No conversion score, revenue forecast or inferred
page-level sale is calculated. The existing static campaign registry stays empty until identity and
enrollment gates have evidence.

## Tests

```sh
python3 -m unittest discover -s measurement -p 'test_*.py' -v
node tests/test_events.cjs
```

Official references: [Amazon agreement](https://affiliate-program.amazon.com/help/operating/agreement),
[Program Policies](https://affiliate-program.amazon.com/help/operating/policies),
[FTC disclosure guidance](https://www.ftc.gov/business-guidance/resources/disclosures-101-social-media-influencers).
See `docs/verification-37333afd.md` for exact verification scope and external gates.
