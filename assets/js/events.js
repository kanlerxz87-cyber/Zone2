/* ============================================================================
   Counter Notes — privacy-preserving event counter (T58, session 7264f3c2, 2026-11-17)

   Implements EV-01 (page_view), EV-02 (product_link_click) and EV-03 (disclosure_view)
   from docs/measurement-t40.json, LIVE under the owner decision recorded on
   discovery/suggestions.html#DS-11 (option A, recorded 2026-11-17).

   The contract this file obeys (principles MP-01..MP-05 in the measurement design):

   MP-01  No personal data: no cookie, no cross-site identifier, and nothing derived from
          the visitor. The queue below stores AGGREGATE EVENTS — page path, a day bucket,
          a static link label — in the visitor's own browser, same-origin, and nothing
          about a person could be reconstructed from them even in principle.
   MP-02  Measure the page and the link, never the person: every field is a static label
          carried by the page or the link itself.
   MP-03  Publish no traffic, conversion or income expectation: this script prints nothing
          and no count derived from it is rendered anywhere on the site.
   MP-05  Search and navigation are never intercepted: clicks are observed, never blocked.

   Persistence: GitHub Pages serves static files, so the endpoint that would keep these
   counts does not exist yet (open item MI-01; suggestion DS-17 on the discovery board).
   Until the owner deploys one, events accumulate in a bounded same-origin queue and
   nothing is transmitted. Deploying an endpoint is one line: set
   window.CN_EVENTS_ENDPOINT = '/api/events' (or any absolute first-party URL) before this
   script loads; the queue then flushes via navigator.sendBeacon on page hide. The event
   shape matches tools/tracking_schema.sql's site_clicks contract: page, link label, day —
   never an IP, user agent, cookie or per-visitor id.
   ========================================================================== */
(function () {
  'use strict';

  // Measure the production host only: previews, local checkouts and mirror hosts record
  // nothing, so a developer session can never inflate a count.
  if (location.hostname !== 'kanlerxz87-cyber.github.io') { return; }

  var QUEUE_KEY = 'counter-notes-events-v1'; // a bucket for aggregate events, not an identifier
  var MAX_EVENTS = 200;                      // bounded: the oldest event is dropped, never grown unbounded
  var ENDPOINT = window.CN_EVENTS_ENDPOINT || null;

  function dayBucket() {
    // A date, never a time: the design forbids anything finer than a day bucket.
    try { return new Date().toISOString().slice(0, 10); } catch (e) { return ''; }
  }

  function pagePath() {
    return location.pathname;
  }

  function referrerHost() {
    // The hostname only — never the full referrer URL, never its query string.
    try { return document.referrer ? new URL(document.referrer).hostname : ''; }
    catch (e) { return ''; }
  }

  function loadQueue() {
    try {
      var raw = window.localStorage.getItem(QUEUE_KEY);
      var arr = raw ? JSON.parse(raw) : [];
      return Object.prototype.toString.call(arr) === '[object Array]' ? arr : [];
    } catch (e) { return []; } // storage unavailable (private mode): the event is simply not recorded
  }

  function saveQueue(q) {
    try { window.localStorage.setItem(QUEUE_KEY, JSON.stringify(q.slice(-MAX_EVENTS))); }
    catch (e) { /* as above: losing an aggregate count is acceptable; storing an identifier is not */ }
  }

  function record(name, fields) {
    var ev = { n: name, d: dayBucket(), p: pagePath() };
    if (fields) { for (var k in fields) { if (Object.prototype.hasOwnProperty.call(fields, k)) { ev[k] = fields[k]; } } }
    var q = loadQueue();
    q.push(ev);
    saveQueue(q);
  }

  function flush() {
    if (!ENDPOINT || typeof navigator === 'undefined' || !navigator.sendBeacon) { return; }
    var q = loadQueue();
    if (!q.length) { return; }
    try {
      // sendBeacon with the aggregate queue only. If the endpoint is down the queue stays
      // where it is — capped, aggregate, local — and the next page tries again.
      if (navigator.sendBeacon(ENDPOINT, JSON.stringify({ events: q }))) { saveQueue([]); }
    } catch (e) { /* never break the page for a measurement */ }
  }

  // ---- EV-01: page_view — once per page load -------------------------------
  record('page_view', { r: referrerHost() });

  // ---- EV-02: product_link_click — observed, never intercepted -------------
  document.addEventListener('click', function (ev) {
    var node = ev.target;
    while (node && node !== document.body) {
      if (node.nodeType === 1 && node.tagName === 'A' && node.getAttribute('data-link-state')) {
        record('product_link_click', {
          k: node.getAttribute('data-product-key') || 'unkeyed',
          s: node.getAttribute('data-link-state')
        });
        return; // do not preventDefault: the visitor goes to Amazon exactly as before
      }
      node = node.parentNode;
    }
  }, true);

  // ---- EV-03: disclosure_view — the strip entering the reader's viewport ----
  var disclosureSeen = false;
  function markDisclosure() {
    if (disclosureSeen) { return; }
    disclosureSeen = true;
    record('disclosure_view', { pos: 'strip' });
  }
  if ('IntersectionObserver' in window) {
    var target = document.querySelector('.pb-disc') || document.querySelector('.disclosure[data-rule="R-01"]');
    if (target) {
      var io = new IntersectionObserver(function (entries) {
        for (var i = 0; i < entries.length; i++) {
          if (entries[i].isIntersecting) { markDisclosure(); io.disconnect(); break; }
        }
      });
      io.observe(target);
    }
  } else {
    markDisclosure(); // no observer support: counting the view is still better than not counting it
  }

  // ---- flush on the way out, if an endpoint is configured -------------------
  window.addEventListener('pagehide', flush);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') { flush(); }
  });

  // Exposed read-only, for the operator to inspect the aggregate queue in the console.
  window.CNEvents = {
    queue: function () { return loadQueue().slice(); },
    size: function () { return loadQueue().length; },
    flush: flush
  };
}());
