'use strict';
const{chromium}=require('playwright'),fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const ORIGIN='http://127.0.0.1:8765',BASE=ORIGIN+'/cratediggin';
const fixture=vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/)[1]);
const app=fs.readFileSync('dist/app.js','utf8').trimEnd();assert(app.endsWith('})();'));
const instrumented=app.slice(0,-5)+`window.__scopeState=()=>({ids:filtered.map(x=>x.id),queue:queue.slice(),scope:queueScope.slice(),custom:customMode,started});})();`;
const savedIds=['mass-appeal','gang-starr-full-clip','beastie-boys-brass-monkey'];
(async()=>{const b=await chromium.launch({headless:true});try{
 for(const width of[390,1280])for(const from of['home','songs']){
  const to=from==='home'?'songs':'home',c=await b.newContext({viewport:{width,height:844},reducedMotion:'reduce',serviceWorkers:'block'});c.setDefaultTimeout(10000);
  await c.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin===ORIGIN){if(u.pathname==='/cratediggin/app.js')return r.fulfill({contentType:'application/javascript',body:instrumented});return r.continue()}if(u.href==='https://www.youtube.com/iframe_api')return r.fulfill({contentType:'application/javascript',body:fixture});return r.abort()});
  await c.addInitScript(ids=>{if(window!==top)return;Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}});localStorage.setItem('crate-my-playlist',JSON.stringify({name:'Manual test crate',ids}));localStorage.setItem('crate-prefs',JSON.stringify({auto:false,saver:false}))},savedIds);
  const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(BASE+(from==='home'?'/':'/tracks/'));await p.waitForFunction(()=>window.__ready&&window.__scopeState);
  const saved=await p.evaluate(()=>localStorage.getItem('crate-my-playlist'));
  assert.equal(await p.locator('#sort option').count(),8);assert.equal((await p.evaluate(()=>window.__scopeState().ids)).length,await p.evaluate(()=>window.TRACKS.length));
  await p.locator('#my-crate-tab').click();assert(await p.locator('.crate-sort').isHidden());assert.deepEqual(await p.evaluate(()=>window.__scopeState().ids),savedIds);
  // Genuine SPA flow: saved manual list -> track article -> previously unvisited catalog.
  await p.locator('.record-card').first().click();await p.locator('.song-heading').waitFor();
  await p.locator('a[data-nav="'+to+'"]').first().click();
  await p.locator('#sort').waitFor({state:'visible'});await p.waitForFunction(()=>!window.__scopeState().custom&&window.__scopeState().ids.length===window.TRACKS.length);
  assert.equal(await p.locator('#library-tab').getAttribute('aria-pressed'),'true');assert.equal(await p.locator('#sort option').count(),8);
  await p.goBack();await p.locator('.song-heading').waitFor();await p.goBack();await p.locator('#my-crate-tab').waitFor();
  await p.waitForFunction(()=>window.__scopeState().custom);assert(await p.locator('.crate-sort').isHidden());assert.deepEqual(await p.evaluate(()=>window.__scopeState().ids),savedIds);
  await p.goForward();await p.locator('.song-heading').waitFor();await p.goForward();await p.locator('#sort').waitFor({state:'visible'});
  for(const sort of['year-desc','title','title-desc','artist','artist-desc','selection','selection-desc','year']){
   await p.locator('#sort').selectOption(sort);assert.equal((await p.evaluate(()=>window.__scopeState().ids)).length,await p.evaluate(()=>window.TRACKS.length));
   assert.deepEqual(await p.evaluate(()=>window.__scopeState().ids),await p.evaluate(sort=>window.CrateFilter(window.TRACKS.slice().sort((a,b)=>(Number.isInteger(a.year)?a.year:9999)-(Number.isInteger(b.year)?b.year:9999)||a.artist.localeCompare(b.artist)||a.title.localeCompare(b.title)),{sort}).map(x=>x.id),sort));
   assert.equal(await p.evaluate(()=>localStorage.getItem('crate-my-playlist')),saved);
  }
  const beforeReveal=await p.locator('#results .record-card').count();await p.locator('.results-status').evaluate(e=>e.scrollIntoView({block:'end'}));await p.waitForFunction(n=>document.querySelectorAll('#results .record-card').length>n,beforeReveal);await p.locator('#sort').selectOption('year-desc');assert.equal(await p.locator('.results-pagination').count(),0);const sortedRows=await p.evaluate(()=>({all:window.__scopeState().ids,shown:[...document.querySelectorAll('#results .record-card')].map(e=>new URL(e.href).pathname.split('/').pop().replace(/\.html$/,''))}));assert(sortedRows.shown.length>0&&sortedRows.shown.length<=sortedRows.all.length);assert.equal(new Set(sortedRows.shown).size,sortedRows.shown.length,'Progressive sort has no duplicate rows');assert.deepEqual(sortedRows.shown,sortedRows.all.slice(0,sortedRows.shown.length),'Progressive sort starts at the exact ordered prefix, regardless of automatic prefetch');
  await p.reload();await p.waitForFunction(()=>window.__ready&&window.__scopeState);assert.equal(await p.locator('#sort').inputValue(),'year-desc');assert.equal((await p.evaluate(()=>window.__scopeState().ids)).length,await p.evaluate(()=>window.TRACKS.length));
  await p.locator('#play-filter').click();await p.waitForFunction(()=>window.__players.find(x=>x.id==='yt')?.stateValue===1);await p.goBack();await p.locator('#sort').waitFor({state:'visible'});
  const playback=()=>p.evaluate(()=>({queue:window.__scopeState().queue,scope:window.__scopeState().scope,providers:window.__players.map(x=>[x.id,x.video,x.loads,x.plays])}));const before=await playback();await p.locator('#sort').selectOption('title-desc');assert.deepEqual(await playback(),before);
  assert.equal(await p.evaluate(()=>localStorage.getItem('crate-my-playlist')),saved);await p.locator('#sort').scrollIntoViewIfNeeded();assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.screenshot({path:'/tmp/producer-collage-catalog-scope-'+from+'-'+width+'.png'});assert.deepEqual(errors,[]);await c.close();
 }
 console.log('HOME/TRACKS cross-route My Crate isolation, Back/Forward restoration, all8 sort directions and full catalog, manual storage and active playback preservation PASS. Mock providers only.');
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
