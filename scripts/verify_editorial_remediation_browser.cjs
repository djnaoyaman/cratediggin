const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('fs');
const ids=['j-live-hush-the-crowd','dj-shadow-midnight-in-a-perfect-world','a-tribe-called-quest-electric-relaxation'];
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [320,390,1280]){
const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));await context.route('https://www.youtube.com/iframe_api',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
for(const id of ids){await page.goto('http://127.0.0.1:8765/cratediggin/tracks/'+id+'.html');await page.evaluate(()=>document.fonts.ready);const t=await page.evaluate(id=>TRACKS.find(x=>x.id===id),id);
assert.equal(await page.locator('.song-heading').innerText(),t.title);assert.equal(await page.locator('.deck').innerText(),t.deck);assert.equal(await page.locator('.essay h2').innerText(),t.essayTitle);assert.deepEqual(await page.locator('.essay > p:not(.article-label)').allTextContents(),t.essay);
const rows=page.locator('.essay > .essay-references');assert.equal(await rows.count(),3);
for(let i=0;i<3;i++){const expected=[...new Set(t.essaySources[i].map(j=>t.sources[j].url))];assert.deepEqual(await rows.nth(i).locator('a').evaluateAll(a=>a.map(x=>x.href)),expected);}
const img=page.locator('.track-artwork img');await img.scrollIntoViewIfNeeded();await img.evaluate(i=>i.decode());assert(await img.isVisible());assert(await img.evaluate(i=>i.naturalWidth>0));assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
await page.locator('.essay').scrollIntoViewIfNeeded();await page.locator('.essay').screenshot({path:`/tmp/editorial-remediation-${id}-${width}.png`});assert.equal(await page.locator('.source-list > li').count(),t.sources.length);
}
await page.goto('http://127.0.0.1:8765/cratediggin/readings/');for(const id of ids){const title=await page.evaluate(id=>TRACKS.find(x=>x.id===id).essayTitle,id);assert((await page.locator('main').innerText()).includes(title));}assert.deepEqual(errors,[]);await context.close();}
const context=await browser.newContext({javaScriptEnabled:false}),page=await context.newPage();for(const id of ids){await page.goto('http://127.0.0.1:8765/cratediggin/tracks/'+id+'.html');assert.equal(await page.locator('.essay-references').count(),3);assert((await page.locator('main').innerText()).includes('参考資料'));}await context.close();console.log('Three source-led rewrites: exact paragraph/source mappings, READINGS and no-JS, decoded art,320/390/1280 passed; no audio assertion');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
