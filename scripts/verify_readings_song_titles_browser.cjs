'use strict';
const{chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const tracks=JSON.parse(fs.readFileSync('tracks.json','utf8')),BASE='http://127.0.0.1:8765/cratediggin',by=Object.fromEntries(tracks.map(t=>[t.id,t]));
// READINGS preserves the established SPA year/artist/title order; static HTML preserves authored order.
const year=t=>Number.isInteger(t.year)?t.year:9999;
const spaTracks=tracks.slice().sort((a,b)=>year(a)-year(b)||a.artist.localeCompare(b.artist)||a.title.localeCompare(b.title));
async function cards(page,selector,expected,staticMode=false){
 const actual=await page.locator(selector).evaluateAll(nodes=>nodes.map(n=>({href:n.getAttribute('href'),rows:[...n.children].map(c=>({tag:c.tagName.toLowerCase(),text:c.textContent,cls:c.className}))})));
 assert.equal(actual.length,expected.length);
 for(let i=0;i<expected.length;i++){const t=expected[i],a=actual[i];assert.deepEqual(a.rows.map(x=>x.tag),['span','p','h2','p','span']);assert.deepEqual(a.rows.map(x=>x.text),[t.artist,t.title,t.essayTitle||t.title,t.deck,'READ ARTICLE ↗'],t.id);assert.equal(a.rows[1].cls,'reading-song-title');assert.equal(new URL(a.href,BASE+'/').pathname,BASE.replace(/^https?:\/\/[^/]+/,'')+'/tracks/'+t.id+'.html');}
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
}
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of[320,390,1280]){
  const staticContext=await browser.newContext({viewport:{width,height:900},javaScriptEnabled:false});await staticContext.route('**/*',r=>new URL(r.request().url()).origin==='http://127.0.0.1:8765'?r.continue():r.abort());const sp=await staticContext.newPage();await sp.goto(BASE+'/readings/');await cards(sp,'.reading-card',tracks,true);await staticContext.close();
  const c=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce',serviceWorkers:'block'});await c.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));await c.route('**/*',r=>new URL(r.request().url()).origin==='http://127.0.0.1:8765'?r.continue():r.abort());const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(BASE+'/readings/');await p.locator('#reading-search').waitFor();await cards(p,'#reading-results .reading-card',spaTracks);
  const input=p.locator('#reading-search');await input.fill('In/Flux');const target=tracks.find(t=>t.title==='In/Flux');assert(target);await cards(p,'#reading-results .reading-card',[target]);await p.screenshot({path:'/tmp/renewal-readings-song-titles-'+width+'.png'});await p.locator('#reading-results .reading-card').click();await p.locator('.song-heading').waitFor();assert.equal(await p.locator('.essay h2').innerText(),target.essayTitle);await p.goBack();await p.locator('#reading-search').waitFor();await cards(p,'#reading-results .reading-card',spaTracks);await p.goForward();await p.locator('.song-heading').waitFor();assert.equal(await p.locator('.essay h2').innerText(),target.essayTitle);
  await p.goto(BASE+'/readings/');await p.locator('#reading-search').waitFor();for(const t of[tracks.reduce((a,b)=>a.title.length>b.title.length?a:b),tracks.find(t=>t.title.includes('(Jay Dee Remix)'))]){assert(t);await p.locator('#reading-search').fill(t.title);const visible=await p.locator('.reading-song-title').allTextContents();assert(visible.includes(t.title));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));}
  await p.locator('#reading-search').fill('');await cards(p,'#reading-results .reading-card',spaTracks);await p.goto(BASE+'/');await p.locator('#home-editorial .reading-card').first().waitFor();await cards(p,'#home-editorial .reading-card',['mass-appeal','dj-shadow-midnight-in-a-perfect-world','nas-rewind'].map(id=>by[id]));assert.deepEqual(errors,[]);await c.close();
 }
 console.log('522 exact reading titles static/SPA; 320/390/1280 wrapping, version suffixes, search reset, Back/Forward,3 shared home cards PASS; no audio playback test');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
