/* Counter Notes · EV-01 page_view, EV-02 product_link_click, EV-03 disclosure_view.
   EV-04/05 are authorized report imports, NEVER browser events.
   No cookies, localStorage, visitor/session ID, fingerprint, referrer or query.
   Direct Amazon links are observed, never blocked or routed through a redirect.
   Raw best-effort event counts are not unique readers or eligible Amazon Sessions.
   See privacy.html and docs/MEASUREMENT.md for retention/deployment limitations. */
(function () {
  'use strict';
  var config = window.CN_MEASUREMENT || {};
  if (!config.enabled || !config.endpoint || !window.fetch) { return; }
  if (navigator.globalPrivacyControl || navigator.doNotTrack === '1' || window.doNotTrack === '1') { return; }
  if (navigator.webdriver && config.mode !== 'test') { return; }
  var endpoint;
  try {
    endpoint = new URL(config.endpoint, location.href);
    if (endpoint.origin !== location.origin || endpoint.search || endpoint.hash) { return; }
    if (endpoint.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') { return; }
  } catch (error) { return; }
  var page = location.pathname.replace(/^\/Zone2(?=\/)/, '');
  var pending = [];
  var sent = 0;
  var failed = 0;
  var scheduled = false;
  function flush() {
    scheduled = false;
    if (!pending.length) { return; }
    var batch = pending.splice(0, 20);
    // At-most-once attempt: no retry after an ambiguous network result, no persistent queue.
    // An unavailable collector loses events rather than inventing exact delivery guarantees.
    try {
      window.fetch(endpoint.href, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ events: batch }),
        credentials: 'omit',
        referrerPolicy: 'no-referrer',
        keepalive: true
      }).then(function (response) {
        if (response.ok) { sent += batch.length; } else { failed += batch.length; }
      }).catch(function () { failed += batch.length; });
    } catch (error) { failed += batch.length; }
  }
  function record(name, fields) {
    var event = { name: name, page: page };
    Object.keys(fields || {}).forEach(function (key) { event[key] = fields[key]; });
    pending.push(event);
    if (!scheduled) {
      scheduled = true;
      window.setTimeout(flush, 0);
    }
  }
  record('page_view');
  document.addEventListener('click', function (event) {
    var anchor = event.target && event.target.closest ? event.target.closest('a[data-product-key]') : null;
    if (!anchor || anchor.getAttribute('data-link-state') !== 'TAGGED') { return; }
    var key = anchor.getAttribute('data-product-key') || '';
    if (/^P-[0-9]{2}$/.test(key)) { key = 'P' + Number(key.slice(2)); }
    if (!/^P[1-5]$/.test(key)) { return; }
    record('product_link_click', { product: key });
    flush(); // Do not preventDefault or wait: shopping works even if this request fails.
  }, true);
  var strip = document.querySelector('[data-disclosure-strip], .pb-disc, .disclosure[data-rule="R-01"]');
  if (strip && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      if (entries.some(function (entry) { return entry.isIntersecting && entry.intersectionRatio >= 0.5; })) {
        record('disclosure_view', { position: 'strip' });
        observer.disconnect();
      }
    }, { threshold: 0.5 });
    observer.observe(strip);
  }
  // No fallback event: if visibility cannot be observed, it must not be invented.
  window.addEventListener('pagehide', flush);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') { flush(); }
  });
  window.CNEvents = Object.freeze({
    status: function () { return { mode: config.mode, acknowledged: sent, failed: failed, pending: pending.length }; },
    flush: flush
  });
}());
