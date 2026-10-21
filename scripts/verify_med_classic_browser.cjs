const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const records=JSON.parse(fs.readFileSync('scripts/fixtures/approved-med-classic.json')).records,base='http://127.0.0.1:8765/cratediggin';
const fixture=fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=`([\s\S]*?)`;/)[1];
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [390,1280])for(const expected of records){
  const c=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
  await c.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
  await c.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:fixture}));await c.route('https://www.googletagmanager.com/**',r=>r.abort());
  const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(base+'/tracks/'+expected.id+'.html');await p.waitForFunction(()=>window.__ready);
  assert.equal(await p.locator('.song-heading').innerText(),expected.title);const t=await p.evaluate(id=>window.TRACKS.find(t=>t.id===id),expected.id);assert.equal(t.youtube.id,expected.youtube.id);
  assert.deepEqual(await p.locator('.essay > p:not(.article-label)').allTextContents(),t.essay);const refs=p.locator('.essay > .essay-references');assert.equal(await refs.count(),4);
  for(let i=0;i<4;i++)assert.deepEqual(await refs.nth(i).locator('a').evaluateAll(xs=>xs.map(x=>x.href)),t.essaySources[i].map(n=>t.sources[n].url));
  assert.equal(await p.locator('.editorial-deepdive').count(),2);assert((await p.locator('main').innerText()).includes('未確認'));
  const img=p.locator('.track-artwork img');await img.scrollIntoViewIfNeeded();await img.evaluate(i=>Promise.race([i.decode(),new Promise((_,r)=>setTimeout(()=>r(Error('decode timeout')),10000))]));assert(await img.isVisible());assert.equal(await img.getAttribute('alt'),t.title+' — '+t.artist+'｜CRATE DIGGIN｜DJ Naoyaman');const box=await img.boundingBox();assert(box&&box.x>=0&&box.x+box.width<=width+1);assert.equal(await img.evaluate(e=>getComputedStyle(e).objectFit),'contain');assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert(await p.evaluate(()=>window.__players.every(x=>x.loads===0&&x.plays===0)));
  await p.locator('article:not(.editorial-deepdive)').screenshot({path:'/tmp/producer-collage-med-'+expected.id+'-'+width+'.png'});
  await p.locator('#article-play').click();await p.waitForFunction(()=>window.__players.find(x=>x.id==='yt')?.stateValue===1);assert.equal(await p.evaluate(()=>window.__players.find(x=>x.id==='yt').video),t.youtube.id);assert.deepEqual(errors,[]);await c.close();
 }
 const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}});for(const t of records){const p=await c.newPage();await p.goto(base+'/tracks/'+t.id+'.html');assert.equal(await p.locator('#view > article > h1').innerText(),t.title);assert((await p.locator('main').innerText()).includes(t.essayTitle));assert((await p.locator('main').innerText()).includes('未確認'));await p.close();}await c.close();
 console.log('MED articles/credits/transparent-art and exact media selection at390/1280, static routes PASS; mock provider, no actual playback certification');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
