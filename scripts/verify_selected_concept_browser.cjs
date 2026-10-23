'use strict';
const {chromium}=require('playwright'),fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const F=JSON.parse(fs.readFileSync('scripts/fixtures/approved-selected-concept.json','utf8')),BASE='http://127.0.0.1:8765/cratediggin';
const fixture=vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/)[1]);
(async()=>{const browser=await chromium.launch({headless:true});try{for(const width of [390,1280]){
 const c=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});c.setDefaultTimeout(10000);
 await c.addInitScript(()=>{Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}});localStorage.setItem('crate-prefs',JSON.stringify({auto:false,saver:false}));});
 await c.route('**/*',r=>r.request().url()==='https://www.youtube.com/iframe_api'?r.fulfill({contentType:'application/javascript',body:fixture}):new URL(r.request().url()).origin==='http://127.0.0.1:8765'?r.continue():r.abort());
 const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));for(const t of F.tracks){await p.goto(BASE+'/tracks/'+t.id+'.html');await p.waitForFunction(()=>window.__ready);await p.locator('.song-heading').waitFor();
 assert.equal(await p.locator('.song-heading').innerText(),t.title);assert(await p.locator('#article-play').isEnabled());assert.equal(await p.locator('.external-listening').count(),0);
 const tracks=await p.evaluate(()=>window.TRACKS);assert.equal(tracks.length,F.afterCount);assert.equal(tracks.find(x=>x.id===t.id).youtube.id,t.youtube.id);
 assert.equal(await p.locator('#youtube-link').getAttribute('href'),t.youtube.url);if(t.editorialStatus)assert((await p.locator('body').innerText()).includes(t.editorialStatus));
 if(t.editorSelectionMemory)assert((await p.locator('.editor-selection-memory').innerText()).includes(t.editorSelectionMemory.text));
 const art=p.locator('.track-artwork img');await art.evaluate(i=>i.decode());assert(await art.isVisible());assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 assert.equal(await p.evaluate(()=>window.__players.reduce((n,x)=>n+x.loads+x.plays,0)),0);
 await p.locator('#article-play').click();await p.waitForFunction(id=>window.__players.some(x=>x.video===id&&x.loads>0),t.youtube.id);}
 await p.goto(BASE+'/tracks/mass-appeal.html');await p.waitForFunction(()=>window.__ready);await p.locator('.song-heading').waitFor();assert(await p.locator('#article-play').isEnabled());assert.equal(await p.locator('.external-listening').count(),0);assert.deepEqual(errors,[]);await c.close();
}console.log('Selected concept browser PASS390/1280:exact count/newID wiring/disclosure/art/noautoplay/explicitPLAY mock load/priorplayable. Provider blocked; no actual audio,JP or embedverification claimed.');}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
