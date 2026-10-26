const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8765/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [390,1280]){
 const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/artists/jurassic-5.html');await page.waitForSelector('.feature-listening-route');
 assert.equal(await page.locator('.person-tag-header img').count(),1);assert.equal(await page.locator('.person-tag-header .person-photo').count(),0);
 assert.equal(await page.locator('.feature-listening-route li').count(),9);
 const art=await page.locator('.person-tag-header img').evaluate(im=>({ok:im.complete&&im.naturalWidth>0,r:im.getBoundingClientRect().width}));assert(art.ok&&art.r>width*.4);
 assert.equal(await page.locator('iframe[src*="youtube"]').count(),0,'Reading must not autoplay or embed on entry');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
 await page.screenshot({path:`/tmp/jurassic-feature-${width}.png`,fullPage:true});
 await page.locator('#feature-route-play').click();await page.waitForURL(/the-game/);assert((await page.locator('h1').textContent()).includes('The Game'));
 await page.goBack();await page.waitForSelector('#feature-route-play');assert.equal(await page.locator('.feature-listening-route li').count(),9);
 await page.locator('.feature-listening-route a[href*="jayou-remix"]').click();await page.waitForURL(/jayou-remix/);assert((await page.locator('h1').textContent()).includes('Remix'));
 await page.goBack();await page.waitForSelector('#feature-route-play');
 await page.goto(base+'/artists/');await page.locator('a[href*="feature/jurassic-5"],a[href*="artists/jurassic-5.html"],a[href*="features/jurassic-5.html"]').first().click();await page.waitForSelector('.person-tag-header');
 assert.equal(errors.length,0,errors.join('\n'));await page.close();
}
console.log('J5 browser PASS: mobile/desktop tag hero, selected route, distinct remix, back/forward, direct+SPA navigation, no read autoplay');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
