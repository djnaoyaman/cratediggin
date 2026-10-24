const {chromium}=require('playwright'),fs=require('node:fs'),assert=require('node:assert/strict');
const tracks=JSON.parse(fs.readFileSync('tracks.json','utf8'));
const allIds=tracks.filter(t=>['Slum Village','J-88'].includes(t.artist)||(t.artists||[]).includes('Slum Village')).map(t=>t.id).sort();
const ownIds=tracks.filter(t=>['Slum Village','J-88'].includes(t.artist)).map(t=>t.id).sort();
const guestIds=allIds.filter(id=>!ownIds.includes(id));
assert.equal(allIds.length,18);assert.equal(ownIds.length,15);assert.equal(guestIds.length,3);
const app=fs.readFileSync('dist/app.js','utf8').trimEnd();assert(app.endsWith('})();'));
const instrumented=app.slice(0,-5)+'window.__slumState=()=>({queue:queue.slice(),scope:queueScope.slice()});})();';
const idsFromHrefs=hrefs=>hrefs.map(x=>x.split('/').pop().replace(/\.html$/,'')).sort();
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8779/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true,...(process.env.CHROME_BIN?{executablePath:process.env.CHROME_BIN}:{})});try{
for(const width of [390,1280]){
 const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
 await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
 await context.route('**/app.js*',r=>r.fulfill({contentType:'application/javascript',body:instrumented}));
 await context.route('https://www.youtube.com/**',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/artists/slum-village.html');await page.locator('h1.section-title').filter({hasText:'Slum Village'}).waitFor();
 const photo=page.locator('.person-photo-header .person-photo');await photo.evaluate(i=>i.decode());
 assert.deepEqual(await photo.evaluate(i=>[i.naturalWidth,i.naturalHeight]),[1456,816]);
 assert.equal(await photo.evaluate(i=>getComputedStyle(i).objectFit),'contain');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 const assertScope=async expected=>{const state=await page.evaluate(()=>window.__slumState());assert.deepEqual(state.queue.sort(),expected);assert.deepEqual(state.scope.sort(),expected);assert.deepEqual(idsFromHrefs(await page.locator('#results .record-card').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')))),expected)};
 assert.equal(await page.locator('#feature-count').innerText(),'18曲');await assertScope(allIds);
 assert.equal(await page.locator('#results .record-card').count(),18);
 await page.locator('[data-feature-scope=own]').click();assert.equal(await page.locator('#feature-count').innerText(),'15曲');await assertScope(ownIds);
 await page.locator('[data-feature-scope=related]').click();assert.equal(await page.locator('#feature-count').innerText(),'3曲');await assertScope(guestIds);
 const guests=await page.locator('#results .record-card').evaluateAll(xs=>xs.map(x=>x.getAttribute('href')));
 assert(guests.every(x=>['common-thelonius','dj-jazzy-jeff-are-u-ready','dwele-angel-user-selected'].some(id=>x.includes(id))));
 await page.locator('[data-feature-scope=all]').click();await assertScope(allIds);
 await page.screenshot({path:'/tmp/slum-feature-'+width+'.png',fullPage:false});
 assert.deepEqual(errors,[]);
 await page.goto(base+'/artists/');
 const card=page.locator('.feature-poster').filter({has:page.locator('h3',{hasText:'Slum Village'})});assert.equal(await card.count(),1);assert((await card.innerText()).includes('アーティスト名義 15曲'));
 await card.locator('.feature-photo').evaluate(i=>i.decode());assert.equal(await card.locator('.feature-photo').evaluate(i=>getComputedStyle(i).objectFit),'contain');
 await context.close();
}
for(const width of [390,1280]){const context=await browser.newContext({javaScriptEnabled:false,viewport:{width,height:900}}),page=await context.newPage();await page.goto(base+'/artists/slum-village.html');assert.equal(await page.locator('.person-photo-header').count(),1);assert((await page.locator('main').innerText()).includes('DETROIT / CONANT GARDENS'));const ids=idsFromHrefs(await page.locator('main > ul > li > a').evaluateAll(xs=>xs.map(x=>x.getAttribute('href'))));assert.equal(new Set(ids).size,18);assert.deepEqual(ids,allIds);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await context.close();}
console.log('Slum feature mobile/desktop, image decode/contain, 18/15/3 filters, index discovery, no-JS and no errors PASS');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
