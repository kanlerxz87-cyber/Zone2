/* Synthetic browser harness. No Amazon requests or production events are sent. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const code = fs.readFileSync('assets/js/events.js', 'utf8');

async function boot(overrides = {}) {
  const calls = [], listeners = {};
  let intersection;
  const strip = {};
  const document = {
    currentScript: { src: 'https://publication.example/Zone2/assets/js/events.js' },
    referrer: 'https://google.com/search?q=private-query', visibilityState: 'visible',
    querySelector: () => strip,
    addEventListener: (name, fn) => { listeners[name] = fn; }
  };
  const navigator = {};
  const location = { origin: 'https://publication.example', pathname: '/Zone2/index.html', search: '?email=synthetic' };
  const window = {};
  function IntersectionObserver(fn) { intersection = fn; this.observe = () => {}; this.disconnect = () => {}; }
  window.IntersectionObserver = IntersectionObserver;
  const config = overrides.config || { enabled: true, mode: 'self_hosted', endpoint: 'api/events' };
  const fetch = (url, options) => {
    calls.push({ url, options });
    return Promise.resolve({ ok: true, json: () => Promise.resolve(config) });
  };
  Object.assign(navigator, overrides.navigator);
  Object.assign(document, overrides.document);
  const context = { document, navigator, location, window, URL, fetch, IntersectionObserver, console };
  vm.runInNewContext(code, context);
  await new Promise(resolve => setImmediate(resolve));
  await new Promise(resolve => setImmediate(resolve));
  return { calls, listeners, document, intersection: () => intersection };
}
function events(state) { return state.calls.filter(c => c.options?.method === 'POST').flatMap(c => JSON.parse(c.options.body).events); }

(async () => {
  let s = await boot();
  assert.deepEqual(events(s), [{ event: 'page_view', page: 'index.html', channel: 'search' }]);
  s.intersection()([{ isIntersecting: true }]);
  s.intersection()([{ isIntersecting: true }]);
  assert.equal(events(s).filter(e => e.event === 'disclosure_view').length, 1);
  const link = { href: 'https://www.amazon.com/dp/B0CDY277D3?tag=shopnow047c-20', getAttribute: name => name === 'data-product-key' ? 'P1' : null };
  const click = { isTrusted: true, type: 'click', button: 0, target: { closest: () => link } };
  s.listeners.click(click);
  s.listeners.auxclick({ ...click, type: 'auxclick', button: 1 });
  s.listeners.auxclick({ ...click, type: 'auxclick', button: 2 });
  s.listeners.click({ ...click, isTrusted: false });
  assert.equal(events(s).filter(e => e.event === 'product_link_click').length, 2);
  for (const call of s.calls.filter(c => c.options?.method === 'POST')) {
    assert.equal(call.url, 'https://publication.example/Zone2/api/events');
    assert.equal(call.options.credentials, 'omit');
    assert.equal(call.options.keepalive, true);
    assert(!call.options.body.includes('private-query'));
    assert(!call.options.body.includes('synthetic'));
  }
  s.document.visibilityState = 'visible';
  s.listeners.visibilitychange();
  assert.equal(events(s).filter(e => e.event === 'page_view').length, 1);

  for (const navigator of [{ doNotTrack: '1' }, { globalPrivacyControl: true }]) {
    s = await boot({ navigator });
    assert.equal(s.calls.length, 0);
  }
  for (const config of [
    { enabled: false, mode: 'github_pages_static', endpoint: null },
    { enabled: true, mode: 'self_hosted', endpoint: 'https://evil.example/api/events' },
    { enabled: true, mode: 'self_hosted', endpoint: 'api/events?visitor=123' },
    { enabled: true, mode: 'self_hosted', endpoint: 'api/other' }
  ]) {
    s = await boot({ config });
    assert.equal(events(s).length, 0);
  }
  s = await boot({ document: { visibilityState: 'hidden' } });
  assert.equal(events(s).length, 0);
  s.document.visibilityState = 'visible';
  s.listeners.visibilitychange();
  assert.equal(events(s).length, 1);
  assert(!/localStorage|sessionStorage|document\.cookie|sendBeacon/.test(code.replace(/\/\*[\s\S]*?\*\//g, '')));
  console.log('Event client: 12 behavior/privacy cases passed (synthetic; no external requests)');
})().catch(error => { console.error(error); process.exit(1); });
