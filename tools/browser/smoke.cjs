/* Exercise the real generated artifact, never Amazon. Test-only service/data are temporary. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium: playwright } = require('playwright');
const packaged = require('@sparticuz/chromium');
const chromium = packaged.default || packaged;
const { default: AxeBuilder } = require('@axe-core/playwright');

let runningBrowser;
(async function () {
  const base = process.env.CN_TEST_ORIGIN;
  assert(base && /^http:\/\/127\.0\.0\.1:\d+$/.test(base), 'Only the isolated loopback test server is permitted');
  const root = path.resolve(__dirname, '../..');
  const shots = path.join(root, '.local/browser-checks');
  fs.mkdirSync(shots, { recursive: true });
  // The npm-distributed browser includes its libraries; no apt or external browser download.
  const bin = path.resolve(path.dirname(require.resolve('@sparticuz/chromium')), '../bin');
  const libs = await packaged.inflate(path.join(bin, 'al2023.tar.br'));
  packaged.setupLambdaEnvironment(path.join(libs, 'lib'));
  const args = chromium.args.filter(a => !['--disable-web-security', '--allow-running-insecure-content', '--single-process'].includes(a));
  const browser = await playwright.launch({ args, executablePath: await chromium.executablePath(), headless: true });
  runningBrowser = browser;
  const errors = [];
  const failures = [];
  const seen = [];
  const a11y = [];
  let externalRequests = 0;
  let browserPosts = 0;
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  // A missing local asset is an error. All external requests are blocked, not merely hoped away.
  await context.route('**/*', async route => {
    const req = route.request();
    const u = new URL(req.url());
    if (u.origin !== base) { externalRequests += 1; return route.abort(); }
    if (req.method() === 'POST') { browserPosts += 1; }
    return route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', e => errors.push(e.message));
  page.on('response', r => { if (r.status() >= 400) { failures.push(r.status() + ' ' + r.url()); } });
  const pages = [
    '/', '/guides/index.html', '/guides/basket-air-fryers.html', '/guides/air-fryer-ovens.html',
    '/guides/thermometers.html', '/guides/basket-or-oven.html', '/guides/air-fryer-capacity.html',
    '/guides/cleanup-and-counter-space.html', '/guides/multi-function-appliances.html',
    '/guides/method.html', '/guides/products/chefman-dual-window.html',
    '/guides/products/emeril-french-door-360.html', '/guides/products/chefman-turbofry-8qt.html',
    '/guides/products/thermomaven-digital.html', '/guides/products/chef-iq-sense.html',
    '/about.html', '/privacy.html', '/suggestions.html', '/questions.html', '/workroom.html',
    '/flagged.html', '/pages/index.html', '/decisions/index.html', '/release/index.html', '/board/index.html'
  ];
  const widths = process.env.CN_TEST_WIDTHS ? process.env.CN_TEST_WIDTHS.split(',').map(Number) : [1440, 390, 320];
  for (const width of widths) {
    await page.setViewportSize({ width, height: 900 });
    for (const rel of pages) {
      const response = await page.goto(base + rel, { waitUntil: 'networkidle' });
      assert.equal(response.status(), 200, rel);
      await page.evaluate(() => document.fonts.ready);
      const layout = await page.evaluate(() => {
        const d = document.querySelector('[data-disclosure-strip]');
        const r = d.getBoundingClientRect();
        const h = document.querySelector('.cn-masthead').getBoundingClientRect();
        return { overflow: document.documentElement.scrollWidth > innerWidth + 1,
          disclosureInView: r.top >= 0 && r.bottom < innerHeight,
          belowMasthead: r.top >= h.bottom - 1,
          height: r.height,
          text: d.textContent,
          shellCount: document.querySelectorAll('[data-cn-shell]').length };
      });
      assert(!layout.overflow, 'Horizontal overflow at ' + width + ' ' + rel);
      assert(layout.disclosureInView && layout.belowMasthead && layout.height > 20, 'Disclosure visibility ' + width + ' ' + rel);
      assert(layout.text.includes('As an Amazon Associate I earn from qualifying purchases.'), rel);
      assert.equal(layout.shellCount, 1, 'Single masthead ' + rel);
      seen.push(width + ' ' + rel);
      if (width === 1440 && ['/', '/suggestions.html', '/workroom.html', '/guides/basket-or-oven.html'].includes(rel)) {
        const scan = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21aa']).analyze();
        a11y.push({ path: rel, violations: scan.violations.map(v => ({ id: v.id, impact: v.impact, nodes: v.nodes.map(n => n.target) })) });
      }
      if (['/', '/suggestions.html', '/guides/basket-or-oven.html'].includes(rel) && width !== 320) {
        await page.screenshot({ path: path.join(shots, (rel === '/' ? 'home' : rel.split('/').pop().replace('.html', '')) + '-' + width + '.png'), fullPage: true });
      }
    }
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(base + '/');
  await page.getByRole('button', { name: 'Thermometers', exact: true }).click();
  assert.equal(await page.locator('[data-product-category]:visible').count(), 2);
  await page.getByRole('button', { name: 'Air fryers', exact: true }).click();
  assert.equal(await page.locator('[data-product-category]:visible').count(), 3);
  await page.getByRole('button', { name: 'The whole edit', exact: true }).click();
  assert.equal(await page.locator('[data-product-category]:visible').count(), 5);
  const workroom = page.locator('.cn-workroom summary');
  const rect = await workroom.boundingBox();
  assert(rect.x >= 0 && rect.x + rect.width <= 390, 'Mobile Workroom control is visible');
  await workroom.click();
  await page.locator('.cn-workroom').getByRole('link', { name: 'Executive summary & all tools' }).click();
  assert(page.url().endsWith('/workroom.html'));
  await page.locator('[data-tool-search]').fill('tracking');
  assert.equal(await page.locator('[data-tool-directory] > a:visible').count(), 1);
  await page.locator('[data-tool-search]').fill('no-matching-tool-zz');
  assert.equal(await page.locator('[data-tool-directory] > a:visible').count(), 0);
  assert((await page.locator('[data-tool-status]').textContent()).includes('No match'));

  await page.goto(base + '/suggestions.html');
  assert.equal(await page.locator('[data-decision-option]:checked').count(), 0);
  await page.locator('[data-decision-option]').first().check();
  assert.equal(await page.evaluate(() => localStorage.length), 0, 'No automatic draft save');
  await page.locator('[data-save-decisions]').click();
  await page.reload();
  assert.equal(await page.locator('[data-decision-option]:checked').count(), 1);
  const downloadPromise = page.waitForEvent('download');
  await page.locator('[data-export-decisions]').click();
  const download = await downloadPromise;
  const content = JSON.parse(fs.readFileSync(await download.path(), 'utf8'));
  assert.equal(content.applied, false);
  assert.equal(content.status, 'review_draft_only');
  assert.equal(Object.keys(content.choices).length, 1);
  await page.locator('[data-reset-decisions]').click();
  assert.equal(await page.locator('[data-decision-option]:checked').count(), 0);
  assert.equal(await page.evaluate(() => localStorage.length), 0);
  assert.equal(await context.cookies().then(c => c.length), 0);
  assert.equal(browserPosts, 0, 'Ordinary automation produces no analytics events');

  const nojs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const fallback = await nojs.newPage();
  await fallback.goto(base + '/');
  assert.equal(await fallback.locator('[data-product-category]:visible').count(), 5);
  assert.equal(await fallback.locator('a[data-product-key][href*="tag=shopnow047c-20"]').count(), 5);
  assert(await fallback.getByRole('link', { name: 'Start with the buying guide' }).isVisible());
  await nojs.close();

  // Deliberately enable only the isolated test-mode client. Do not follow any affiliate link.
  const measurement = await browser.newContext();
  await measurement.route('**/*', route => new URL(route.request().url()).origin === base ? route.continue() : route.abort());
  await measurement.addInitScript(() => { window.CN_MEASUREMENT = { enabled: true, endpoint: '/api/events', mode: 'test' }; });
  await measurement.route('**/assets/js/measurement-config.js', route => route.fulfill({ contentType: 'text/javascript', body: '' }));
  const m = await measurement.newPage();
  await m.goto(base + '/');
  await m.waitForFunction(() => window.CNEvents && CNEvents.status().acknowledged >= 2);
  await m.locator('a[data-product-key]').first().evaluate(a => {
    a.addEventListener('click', e => e.preventDefault(), { once: true });
    a.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
  });
  await m.waitForFunction(() => CNEvents.status().acknowledged >= 3);
  assert.equal(await m.evaluate(() => CNEvents.status().failed), 0);
  assert.equal(await m.evaluate(() => localStorage.length), 0);
  assert.equal((await measurement.cookies()).length, 0);
  await measurement.close();

  for (const preference of ['gpc', 'dnt']) {
    const optedOut = await browser.newContext();
    await optedOut.addInitScript(pref => {
      Object.defineProperty(navigator, pref === 'gpc' ? 'globalPrivacyControl' : 'doNotTrack', { value: pref === 'gpc' ? true : '1' });
      window.CN_MEASUREMENT = { enabled: true, endpoint: '/api/events', mode: 'test' };
    }, preference);
    await optedOut.route('**/assets/js/measurement-config.js', route => route.fulfill({ contentType: 'text/javascript', body: '' }));
    const opt = await optedOut.newPage();
    let optPosts = 0;
    opt.on('request', req => { if (req.method() === 'POST') { optPosts += 1; } });
    await opt.goto(base + '/', { waitUntil: 'networkidle' });
    assert.equal(optPosts, 0, preference + ' opts out');
    assert.equal(await opt.evaluate(() => typeof window.CNEvents), 'undefined');
    await optedOut.close();
  }
  const offline = await browser.newContext();
  await offline.addInitScript(() => { window.CN_MEASUREMENT = { enabled: true, endpoint: '/api/events', mode: 'test' }; });
  await offline.route('**/assets/js/measurement-config.js', route => route.fulfill({ contentType: 'text/javascript', body: '' }));
  await offline.route('**/api/events', route => route.abort());
  const lost = await offline.newPage();
  await lost.goto(base + '/', { waitUntil: 'networkidle' });
  await lost.waitForFunction(() => window.CNEvents && CNEvents.status().failed >= 2);
  assert.equal(await lost.evaluate(() => localStorage.length), 0, 'No offline analytics queue');
  assert.equal(await lost.locator('a[data-product-key][href*="tag=shopnow047c-20"]').count(), 5, 'Collector failure never rewrites or disables shopping links');
  await offline.close();
  assert.equal(errors.length, 0, JSON.stringify(errors));
  assert.equal(failures.length, 0, JSON.stringify(failures));
  assert.equal(externalRequests, 0, 'No external requests, let alone affiliate navigations');
  const report = { layoutsChecked: seen.length, consoleErrors: errors, failedResponses: failures,
    externalRequests, interactions: 'filters, mobile Workroom, tool search, local review save/restore/export/clear, no-JS links, test-mode persistence, GPC/DNT, collector-down direct links',
    accessibility: a11y };
  fs.writeFileSync(path.join(shots, 'report.json'), JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
  const serious = a11y.flatMap(p => p.violations).filter(v => ['serious', 'critical'].includes(v.impact));
  assert.equal(serious.length, 0, 'Resolve serious/critical accessibility findings');
  await browser.close();
})().catch(async error => { console.error(error); if (runningBrowser) { await runningBrowser.close().catch(() => {}); } process.exit(1); });
