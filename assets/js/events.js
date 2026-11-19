/* Counter Notes — aggregate events only. No cookies, localStorage, identifiers,
   raw referrers, query strings, IP/UA fields, background retries, or link redirects.
   GitHub Pages config is OFF. Self-hosting supplies a same-origin runtime config.
   EV-04/05 are operator imports, NEVER browser purchase/search inference. */
(function () {
  'use strict';
  var script = document.currentScript;
  if (!script || navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl === true) { return; }
  var root = new URL('../../', script.src);
  if (root.origin !== location.origin) { return; }
  var relative = location.pathname.slice(root.pathname.length);
  if (!relative || relative.endsWith('/')) { relative += 'index.html'; }
  // Only static, registered paths; never forward an arbitrary incoming path or query.
  if (!/^(?:[a-z0-9-]+\/)*[a-z0-9-]+\.html$/.test(relative)) { return; }
  var endpoint = null;
  var active = false;
  var pageSeen = false;
  var disclosureSeen = false;
  var observer = null;

  function record(event, fields) {
    if (!active) { return; }
    var data = Object.assign({ event: event, page: relative }, fields || {});
    // A failure loses a count, not the reader. keepalive does not block navigation.
    // fetch completion is NOT treated as an Amazon conversion.
    fetch(endpoint.href, {
      method: 'POST', headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
      body: JSON.stringify({ events: [data] }), credentials: 'omit',
      keepalive: true, cache: 'no-store', redirect: 'error', referrerPolicy: 'no-referrer'
    }).catch(function () { /* do not persist or retry browser events */ });
  }

  function channel() {
    if (!document.referrer) { return 'direct'; }
    try {
      var ref = new URL(document.referrer);
      if (ref.origin === location.origin) { return 'internal'; }
      if (/(^|\.)(google\.[a-z.]+|bing\.com|duckduckgo\.com|search\.yahoo\.com)$/.test(ref.hostname)) { return 'search'; }
    } catch (e) { /* unknown referrer is not stored */ }
    return 'other';
  }

  function observePage() {
    if (document.visibilityState === 'hidden' || pageSeen) { return; }
    pageSeen = true;
    record('page_view', { channel: channel() });
    var strip = document.querySelector('[data-disclosure-strip], .pb-disc, .cn-disclosure');
    if (strip && 'IntersectionObserver' in window) {
      observer = new IntersectionObserver(function (entries) {
        if (!disclosureSeen && entries.some(function (entry) { return entry.isIntersecting; })) {
          disclosureSeen = true;
          record('disclosure_view', { position: 'strip' });
          observer.disconnect();
        }
      }, { threshold: 0.1 });
      observer.observe(strip);
    }
    // No observer support means an unknown disclosure view, not an invented one.
  }

  function click(ev) {
    if (!ev.isTrusted || (ev.type === 'auxclick' && ev.button !== 1)) { return; }
    var link = ev.target && ev.target.closest ? ev.target.closest('a[data-product-key]') : null;
    if (!link || link.getAttribute('aria-disabled') === 'true') { return; }
    var product = link.getAttribute('data-product-key');
    if (!/^P[1-5]$/.test(product)) { return; }
    var dest;
    try { dest = new URL(link.href); } catch (e) { return; }
    if (dest.protocol !== 'https:' || !/^(www\.)?amazon\.com$/.test(dest.hostname) || dest.searchParams.get('tag') !== 'shopnow047c-20') { return; }
    record('product_link_click', { product: product });
    // Never preventDefault, change the href, open Amazon automatically, or cloak it.
  }

  fetch(new URL('measurement.json', root).href, { credentials: 'omit', cache: 'no-store', redirect: 'error', referrerPolicy: 'no-referrer' })
    .then(function (response) { if (!response.ok) { throw new Error('config unavailable'); } return response.json(); })
    .then(function (config) {
      if (config.enabled !== true || config.mode === 'github_pages_static' || typeof config.endpoint !== 'string') { return; }
      endpoint = new URL(config.endpoint, root);
      if (endpoint.origin !== location.origin || endpoint.pathname !== root.pathname + 'api/events' || endpoint.search || endpoint.hash) { return; }
      active = true;
      observePage();
      document.addEventListener('visibilitychange', observePage);
      document.addEventListener('click', click, true);
      document.addEventListener('auxclick', click, true);
    }).catch(function () { /* measurement is fail-closed; shopping still works */ });
}());
