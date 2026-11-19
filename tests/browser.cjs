/* Actual Chromium tests. All activity is local fixture traffic; Amazon is NEVER visited. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawn, spawnSync} = require('node:child_process');
const {pathToFileURL} = require('node:url');
const root = path.resolve(__dirname, '..');
const {chromium: playwright} = require('playwright');
const axeSource = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
const scratch = path.join(root, '.local', 'browser-checks');
fs.mkdirSync(scratch, {recursive:true});
const base = process.env.CN_TEST_URL || 'http://127.0.0.1:8765/Zone2/';
const db = path.join(scratch, 'fixture-'+process.pid+'.sqlite3');
let service, browser;
const summary = {kind:'synthetic_local_verification_not_campaign_data', viewport_checks:0, accessibility_pages:0, behavior_checks:[]};

function python(code) {
  const p=spawnSync('python3',['-c',code],{cwd:root,encoding:'utf8'});
  if(p.status!==0)throw new Error(p.stderr);
  return p.stdout.trim();
}
function ready(child) {
  return new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(new Error('Test collector startup timed out')),20000);
    child.stdout.on('data',data=>{if(String(data).includes('on 0.0.0.0:')){clearTimeout(timer);resolve();}});
    child.once('exit',code=>{clearTimeout(timer);reject(new Error('Test collector exited: '+code));});
    child.stderr.on('data',data=>process.stderr.write(data));
  });
}
async function context(options={}) {
  const c=await browser.newContext(options);
  // A local DOM interaction may be tested. No artificial Amazon traffic or live affiliate click.
  await c.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  return c;
}
async function run() {
  const entry=require.resolve('@sparticuz/chromium');
  const imported=await import(pathToFileURL(entry).href);
  const chromium=imported.default;
  const executablePath=await chromium.executablePath();
  // Serverless package ships NSS/NSPR separately; unpack for minimal sandbox Linux.
  const pkg=path.resolve(path.dirname(entry),'..');
  const {inflate}=await import(pathToFileURL(path.join(path.dirname(entry),'lambdafs.js')).href);
  const lib=await inflate(path.join(pkg,'bin/al2023.tar.br'));
  if(!process.env.CN_TEST_URL){
    service=spawn('python3',['-m','measurement.collector','--db',db,'serve','--preview','--port','8765'],{cwd:root,env:process.env,stdio:['ignore','pipe','pipe']});
    await ready(service);
  }
  const launchOptions={executablePath,headless:true,args:chromium.args.filter(a=>!a.includes('disable-web-security')&&!a.includes('allow-running-insecure-content')&&a!=='--single-process'),env:{...process.env,LD_LIBRARY_PATH:path.join(lib,'lib')+(process.env.LD_LIBRARY_PATH?':'+process.env.LD_LIBRARY_PATH:'')}};
  for(let attempt=1;attempt<=3;attempt++){
    try{browser=await playwright.launch(launchOptions);break;}
    catch(err){
      // The packaged headless binary can sporadically SIGSEGV before Chromium starts in this
      // minimal sandbox. Retry startup only; once the browser is up, every test failure is fatal.
      if(!/SIGSEGV/.test(String(err))||attempt===3)throw err;
      process.stderr.write('Chromium startup SIGSEGV; retrying launch ('+attempt+'/2)\n');
    }
  }
  summary.browser_version=browser.version();
  const c=await context({viewport:{width:1440,height:1000}});
  const page=await c.newPage();
  const errors=[],missing=[],posts=[],accessibility=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('response',r=>{if(r.status()>=400 && new URL(r.url()).origin===new URL(base).origin)missing.push([r.status(),r.url()]);});
  page.on('request',r=>{if(r.url().endsWith('/api/events'))posts.push(JSON.parse(r.postData()));});
  await page.goto(new URL('/',base).href,{waitUntil:'load'});
  assert.equal(new URL(page.url()).pathname,'/Zone2/');
  summary.behavior_checks.push('bare preview URL redirects to the correct relative-asset base');
  const current=JSON.parse(python("import sys,json;sys.path.insert(0,'tools');import publication as p;print(json.dumps(sorted(p.indexable_paths()|set(p.extra_pages())|{'suggestions.html','questions.html'})))"));
  for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
    await page.setViewportSize(viewport);
    for(const rel of current){
      await page.goto(new URL(rel,base).href,{waitUntil:'load'});
      await page.evaluate(()=>document.fonts.ready);
      const result=await page.evaluate(()=>{
        const d=document.querySelector('[data-disclosure-strip]');
        const box=d.getBoundingClientRect();
        const point=document.elementFromPoint(Math.min(100,innerWidth/2),box.y+box.height/2);
        return {width:document.documentElement.scrollWidth,view:innerWidth,bottom:box.bottom,top:box.top,visible:box.height>0&&d.contains(point),h1:document.querySelectorAll('h1').length};
      });
      assert(result.width<=result.view+1,rel+' horizontal overflow at '+viewport.width);
      assert(result.top>=0&&result.bottom<=viewport.height,rel+' disclosure not above fold');
      assert(result.visible,rel+' disclosure covered by other content');
      assert.equal(result.h1,1,rel+' H1 count');
      summary.viewport_checks++;
      if(viewport.width===390){
        await page.addScriptTag({content:axeSource});
        const axe=await page.evaluate(async()=>await axe.run({exclude:[]},{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa']}}));
        if(axe.violations.length){
          fs.writeFileSync(path.join(scratch,'axe-'+rel.replaceAll('/','-')+'.json'),JSON.stringify(axe.violations,null,2));
          accessibility.push(rel+' axe violations: '+axe.violations.map(v=>v.id+': '+v.nodes.map(n=>n.target.join(' ')).join(',')).join('; '));
        }
        summary.accessibility_pages++;
        const retailerTargets=await page.locator('a.cn-retailer-link').evaluateAll(as=>as.map(a=>{
          const r=a.getBoundingClientRect();
          return {w:r.width,h:r.height,minHeight:getComputedStyle(a).minHeight,sponsored:a.relList.contains('sponsored')};
        }));
        assert(retailerTargets.every(x=>x.w>=44&&x.h>=44&&x.minHeight==='44px'&&x.sponsored),rel+' paid-link target below the T76 44px rule');
        const tableLabels=await page.locator('.cn-table tbody th').evaluateAll(xs=>xs.map(x=>{
          const s=getComputedStyle(x);
          return {clipped:x.scrollWidth>x.clientWidth+1||x.scrollHeight>x.clientHeight+1,upper:s.textTransform==='uppercase',nowrap:s.whiteSpace==='nowrap'};
        }));
        assert(tableLabels.every(x=>!x.clipped&&!x.upper&&!x.nowrap),rel+' publication table body row label is clipped or incorrectly transformed');
      }
      if(rel==='index.html')await page.screenshot({path:path.join(scratch,'home-'+viewport.width+'.png'),fullPage:true});
    }
  }
  assert.deepEqual(accessibility,[],'WCAG A/AA automated findings (see .local/browser-checks/axe-*.json)');
  // Archives have diverse layouts; test the disclosure visually on EVERY packaged HTML page.
  const all=JSON.parse(python("from pathlib import Path;import json;print(json.dumps([p.relative_to('_site').as_posix() for p in Path('_site').rglob('*.html')]))"));
  for(const rel of all.filter(p=>!current.includes(p))){
    await page.goto(new URL(rel,base).href,{waitUntil:'load'});
    const visible=await page.evaluate(()=>{
      const d=document.querySelector('[data-disclosure-strip]');
      if(!d)return false;const r=d.getBoundingClientRect();
      return r.top>=0&&r.bottom<=innerHeight&&r.height>0&&d.contains(document.elementFromPoint(Math.min(100,innerWidth/2),r.y+r.height/2));
    });
    if(!visible)await page.screenshot({path:path.join(scratch,'archive-failure.png'),fullPage:false});
    assert(visible,rel+' archive disclosure not above-fold/visible');
    const unqualified=await page.evaluate(()=>Array.from(document.querySelectorAll('a[href]')).filter(a=>/^(?:www\.)?amazon\.com$|^link\.amazon$|^amzn\.to$/.test(new URL(a.href).hostname)&&!a.relList.contains('sponsored')).map(a=>a.href));
    assert.deepEqual(unqualified,[],rel+' runtime product links not sponsored');
    const tableLabels=await page.locator('.cn-table tbody th').evaluateAll(xs=>xs.map(x=>{
      const s=getComputedStyle(x);
      return {clipped:x.scrollWidth>x.clientWidth+1||x.scrollHeight>x.clientHeight+1,upper:s.textTransform==='uppercase',nowrap:s.whiteSpace==='nowrap'};
    }));
    assert(tableLabels.every(x=>!x.clipped&&!x.upper&&!x.nowrap),rel+' archived publication table body row label is clipped or incorrectly transformed');
    summary.viewport_checks++;
  }
  await page.setViewportSize({width:390,height:844});
  await page.goto(base,{waitUntil:'load'});
  const homeMeasurements=await page.evaluate(()=>{
    const hrefs=s=>Array.from(document.querySelectorAll(s+' a[href]')).map(a=>a.getAttribute('href'));
    const menu=hrefs('.cn-menu-links'),footer=hrefs('.cn-footer-tool-grid');
    const menuSet=new Set(menu),footerSet=new Set(footer);
    const intersection=[...menuSet].filter(h=>footerSet.has(h)).length;
    const links=Array.from(document.querySelectorAll('a.cn-retailer-link')).map(a=>{
      const r=a.getBoundingClientRect();
      return {w:r.width,h:r.height,minHeight:getComputedStyle(a).minHeight,sponsored:a.relList.contains('sponsored')};
    });
    return {menu:menu.length,menuUnique:menuSet.size,footer:footer.length,footerUnique:footerSet.size,intersection,anchors:document.querySelectorAll('a[href]').length,links};
  });
  assert.deepEqual({menu:homeMeasurements.menu,menuUnique:homeMeasurements.menuUnique,footer:homeMeasurements.footer,footerUnique:homeMeasurements.footerUnique,intersection:homeMeasurements.intersection,anchors:homeMeasurements.anchors},{menu:70,menuUnique:70,footer:70,footerUnique:70,intersection:70,anchors:200},'T76 packaged navigation counts at 390px');
  assert(homeMeasurements.links.every(x=>x.w>=44&&x.h>=44&&x.minHeight==='44px'&&x.sponsored),'T76 mobile retailer controls retain 44px targets and sponsored rel');
  summary.behavior_checks.push('Workspace links and mobile paid-link targets match the packaged T76 measurements');
  await page.keyboard.press('Tab');
  assert.equal(await page.locator(':focus').textContent(),'Skip to content');
  await page.keyboard.press('Enter');
  assert.equal(await page.locator(':focus').getAttribute('id'),'main');
  await page.locator('.cn-workspace-menu summary').click();
  await page.keyboard.press('Escape');
  assert.equal(await page.locator('.cn-workspace-menu').getAttribute('open'),null);
  summary.behavior_checks.push('skip link and keyboard menu Escape');
  await page.locator('#kitchen-priority').selectOption('temperature');
  await page.locator('#kitchen-finder button').click();
  assert.match(await page.locator('#finder-result a').getAttribute('href'),/instant-read-or-wireless/);
  summary.behavior_checks.push('progressive format finder');
  await page.goto(new URL('shop.html',base).href,{waitUntil:'load'});
  await page.locator('[data-filter="thermometers"]').click();
  assert.equal(await page.locator('.cn-product:visible').count(),2);
  await page.locator('[data-filter="air-fryers"]').click();
  assert.equal(await page.locator('.cn-product:visible').count(),3);
  await page.locator('[data-filter="all"]').click();
  assert.equal(await page.locator('.cn-product:visible').count(),5);
  summary.behavior_checks.push('accessible product filters');
  const before=posts.filter(p=>p.events[0].event==='product_link_click').length;
  const cta=page.locator('a[data-product-key="P1"]').first();
  await cta.evaluate(a=>a.addEventListener('click',ev=>ev.preventDefault()));
  const clickResponse=page.waitForResponse(r=>r.url().endsWith('/api/events')&&r.status()===202);
  await cta.click();
  await clickResponse;
  assert.equal(posts.filter(p=>p.events[0].event==='product_link_click').length,before+1);
  assert(posts.some(p=>p.events[0].event==='page_view'));
  assert(posts.some(p=>p.events[0].event==='disclosure_view'));
  assert.equal(await page.evaluate(()=>localStorage.length),0);
  assert.equal((await c.cookies()).length,0);
  assert(posts.every(p=>JSON.stringify(p).length<200));
  summary.behavior_checks.push('real local POST persistence; no counter cookies/storage; outbound blocked');
  await page.goto(new URL('suggestions.html',base).href,{waitUntil:'load'});
  await page.locator('#S63-02 input[value="B"]').check();
  await page.reload({waitUntil:'load'});
  assert(await page.locator('#S63-02 input[value="B"]').isChecked());
  const downloadPromise=page.waitForEvent('download');
  await page.locator('#export-choices').click();
  const download=await downloadPromise;
  await download.saveAs(path.join(scratch,'review-fixture.json'));
  const review=JSON.parse(fs.readFileSync(path.join(scratch,'review-fixture.json')));
  assert.equal(review.scope,'review_preferences_only');
  assert(review.choices.some(v=>v.suggestion_id==='S63-02'&&v.preferred_option==='B'));
  await page.locator('#clear-choices').click();
  assert.equal(await page.evaluate(()=>localStorage.length),0);
  summary.behavior_checks.push('operator preference restore/export/clear; no implementation');
  for(const signal of ['doNotTrack','globalPrivacyControl']){
    const quiet=await context();
    await quiet.addInitScript(({signal})=>Object.defineProperty(navigator,signal,{value:signal==='doNotTrack'?'1':true}),{signal});
    const tab=await quiet.newPage();let writes=0;
    tab.on('request',r=>{if(r.method()==='POST')writes++;});
    await tab.goto(base,{waitUntil:'load'});
    assert.equal(writes,0,signal+' must disable events');
    await quiet.close();
    summary.behavior_checks.push(signal+' disables collection');
  }
  const off=await context();
  await off.route('**/measurement.json',r=>r.fulfill({contentType:'application/json',body:JSON.stringify({enabled:false,endpoint:null,mode:'github_pages_static'})}));
  const tab=await off.newPage();let offPosts=0;
  tab.on('request',r=>{if(r.method()==='POST')offPosts++;});
  await tab.goto(base,{waitUntil:'load'});
  assert.equal(offPosts,0);
  assert.equal(await tab.evaluate(()=>localStorage.length),0);
  summary.behavior_checks.push('static Pages config sends no events');
  await off.close();
  const noJS=await context({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const plain=await noJS.newPage();
  await plain.goto(new URL('shop.html',base).href,{waitUntil:'load'});
  assert.equal(await plain.locator('.cn-product:visible').count(),5);
  assert.equal(await plain.locator('a[data-product-key]').count(),5);
  summary.behavior_checks.push('all products/direct links work without JavaScript');
  await noJS.close();
  assert.deepEqual(errors,[],'browser runtime errors');
  assert.deepEqual(missing,[],'missing local assets/pages');
  if(service){
    const dump=JSON.parse(python("import sqlite3,json;d=sqlite3.connect("+JSON.stringify(db)+");print(json.dumps(d.execute('SELECT event,sum(count) FROM daily_counts GROUP BY event').fetchall()))"));
    assert(dump.some(([event,count])=>event==='product_link_click'&&count>=1));
    assert(dump.some(([event,count])=>event==='page_view'&&count>=1));
    summary.persisted_fixture_events=Object.fromEntries(dump);
  }
  await c.close();
  summary.ok=true;
  fs.writeFileSync(path.join(scratch,'result.json'),JSON.stringify(summary,null,2)+'\n');
  console.log(JSON.stringify(summary,null,2));
}
run().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{
  if(browser)await browser.close();
  if(service)service.kill('SIGTERM');
  for(const suffix of ['', '-wal','-shm'])try{fs.unlinkSync(db+suffix);}catch(e){if(e.code!=='ENOENT')console.error(e.message);}
});
