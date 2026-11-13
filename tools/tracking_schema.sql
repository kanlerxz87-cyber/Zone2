-- Click + earnings ledger for the tracking module.
-- Two tables because the two halves have different owners and different rules:
--   site_clicks  -> measured by us, no visitor identity (Participation Requirements forbid tying a
--                   sub-tag / Associates reporting to a specific end user: rule R-08, source S02)
--   associates_report_rows -> ingested verbatim from Associates Central exports; the ONLY place
--                   conversion and earnings may come from (R-13 / R-15, source S02)
-- Nothing in this schema stores an IP address, user-agent, cookie value, or per-visitor identifier.

PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS campaign_registry (
  key         TEXT PRIMARY KEY,           -- static lowercase label, e.g. "kitchen-hero"
  page        TEXT NOT NULL,             -- site path the block lives on
  entry       TEXT NOT NULL,             -- data/products.json id (P-01..P-03) or a catalog ASIN
  position    TEXT NOT NULL,             -- hero | mid | table | faq | footer
  asin        TEXT NOT NULL CHECK (length(asin) = 10),
  enabled     INTEGER NOT NULL DEFAULT 1,
  created_utc TEXT NOT NULL,
  UNIQUE (page, position, key)
);

CREATE TABLE IF NOT EXISTS site_clicks (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc       TEXT NOT NULL,
  date_local   TEXT NOT NULL,             -- day bucket for reporting only
  campaign_key TEXT NOT NULL REFERENCES campaign_registry(key),
  page         TEXT NOT NULL,
  entry        TEXT NOT NULL,
  outbound_href TEXT NOT NULL,            -- includes the Associates tag; no per-visitor parameter
  http_status  INTEGER
);
CREATE INDEX IF NOT EXISTS idx_clicks_day   ON site_clicks(date_local, campaign_key);
CREATE INDEX IF NOT EXISTS idx_clicks_entry ON site_clicks(entry, date_local);

CREATE TABLE IF NOT EXISTS associates_report_rows (
  id                INTEGER PRIMARY KEY AUTOINCREMENT,
  period_start      TEXT NOT NULL,        -- as reported by Associates Central
  period_end        TEXT NOT NULL,
  marketplace       TEXT NOT NULL,        -- e.g. amazon.com
  tracking_id       TEXT NOT NULL,
  clicks            INTEGER,              -- from the report, not from our own count
  ordered_items     INTEGER,
  shipped_revenue   NUMERIC,
  earned_commission NUMERIC,
  effective_rate_pct AS ROUND(100.0 * earned_commission / NULLIF(shipped_revenue, 0), 2),
  imported_utc      TEXT NOT NULL,
  import_file       TEXT NOT NULL         -- provenance: which export, hashed
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_report_unique ON associates_report_rows(period_start, period_end, marketplace, tracking_id);

CREATE TABLE IF NOT EXISTS catalog_snapshot (
  asin            TEXT NOT NULL,
  fetched_utc     TEXT NOT NULL,
  response_sha256 TEXT NOT NULL,          -- proves the row came from an API response, not a hand edit
  title           TEXT,
  brand           TEXT,
  category        TEXT,
  price_amount    NUMERIC,                -- display only while inside the freshness window (R-04)
  price_currency  TEXT,
  availability    TEXT,
  stale           INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (asin, fetched_utc)
);

CREATE TABLE IF NOT EXISTS compliance_events (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc    TEXT NOT NULL,
  rule_id   TEXT NOT NULL,               -- e.g. R-01, R-08
  severity  TEXT NOT NULL CHECK (severity IN ('info', 'warn', 'block')),
  detail    TEXT NOT NULL,
  page      TEXT
);

-- Reporting views used by the dashboard tables.
CREATE VIEW IF NOT EXISTS v_clicks_by_campaign AS
SELECT campaign_key, page, COUNT(*) AS clicks, MIN(ts_utc) AS first_click, MAX(ts_utc) AS last_click
FROM site_clicks GROUP BY campaign_key, page;

CREATE VIEW IF NOT EXISTS v_conversion_ready AS
SELECT r.period_start, r.period_end, r.tracking_id, r.clicks, r.ordered_items,
       ROUND(100.0 * r.ordered_items / NULLIF(r.clicks, 0), 2) AS conversion_pct,
       r.shipped_revenue, r.earned_commission
FROM associates_report_rows r
WHERE r.clicks IS NOT NULL AND r.ordered_items IS NOT NULL;
-- NOTE: deliberately no view that estimates earnings without report rows, and no column that could hold a
-- visitor identifier. Both would violate the rules cited above.
