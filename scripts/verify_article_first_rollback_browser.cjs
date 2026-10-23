'use strict';
// Fixture contract: {removedIds: [20 exact slugs], expectedCount: 562}.
// The writer seals this fixture with the rollback source guard.
const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const F=JSON.parse(fs.readFileSync('scripts/fixtures/approved-article-first-rollback.json','utf8'));
const removed=F.removedIds,expected=F.expectedCount,BASE='http://127.0.0.1:8765/cratediggin';
assert.equal(expected,562);assert.equal(removed.length,20);assert.equal(new Set(removed).size,20);
assert(removed.every(id=>typeof id==='string'&&/^[a-z0-9-]+$/.test(id)));
const fixture=vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/)[1]);
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});
  context.setDefaultTimeout(10000);
  await context.addInitScript(()=>{Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}});localStorage.setItem('crate-prefs',JSON.stringify({auto:false,saver:false}));});
  // No official audio/media is requested. Only the local app and a deterministic player API stub run.
  await context.route('**/*',route=>{
   const url=route.request().url();
   if(url==='https://www.youtube.com/iframe_api')return route.fulfill({contentType:'application/javascript',body:fixture});
   return new URL(url).origin==='http://127.0.0.1:8765'?route.continue():route.abort();
  });
  const page=await context.newPage(),errors=[];page.on('pageerror',error=>errors.push(error.message));
  const checkCatalog=async()=>{
   const ids=await page.evaluate(()=>window.TRACKS.map(t=>t.id));assert.equal(ids.length,expected);assert.equal(new Set(ids).size,expected);
   assert(!ids.some(id=>removed.includes(id)));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  };
  const noAutoplay=async()=>assert.equal(await page.evaluate(()=>window.__players.reduce((n,p)=>n+p.loads+p.plays,0)),0);
  await page.goto(BASE+'/');await page.waitForFunction(()=>window.__ready);await checkCatalog();
  assert(await page.locator('#results .record-card').count()>0);assert.equal(await page.locator('#results img').count(),0,'Published compact homepage retains its no-thumbnail layout');await noAutoplay();
  await page.goto(BASE+'/tracks/');await page.waitForFunction(()=>window.__ready);await checkCatalog();
  const art=page.locator('#results figure.catalog-graffiti img').first();await art.scrollIntoViewIfNeeded();await art.evaluate(img=>img.decode());assert(await art.isVisible());assert(await art.evaluate(img=>img.complete&&img.naturalWidth>0));
  assert.equal(await page.locator('.external-listening').count(),0);await noAutoplay();
  await page.goto(BASE+'/tracks/mass-appeal.html');await page.locator('.song-heading').waitFor();await page.waitForFunction(()=>window.__ready);await checkCatalog();
  assert(await page.locator('#article-play').isEnabled(),'Previously playable track is not disabled');
  assert.equal(await page.locator('.external-listening').count(),0);
  assert(!(await page.locator('body').innerText()).includes('サイト内再生は確認中'));
  assert((await page.locator('#youtube-link').getAttribute('href')).startsWith('https://www.youtube.com/'));
  const articleArt=page.locator('.track-artwork img');await articleArt.evaluate(img=>img.decode());assert(await articleArt.isVisible());await noAutoplay();
  for(const id of removed){const response=await context.request.get(BASE+'/tracks/'+id+'.html');assert.equal(response.status(),404,'Removed static article must not survive the build: '+id);await response.dispose();}
  assert.deepEqual(errors,[]);await context.close();
 }
 console.log('Rollback browser PASS: 562 catalog/no20 revoked IDs, homepage + gallery + playable old article, visible prior art, no pending/external-only UI, all20 removed article HTTP404, no autoplay at390/1280. Official audio blocked; actual playback not claimed.');
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1});
