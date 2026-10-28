const {chromium}=require('playwright'),assert=require('node:assert/strict');
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [390,1280]){
 const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
 await context.route('**/*',async route=>{const url=new URL(route.request().url()),local=new URL(base);if(url.origin===local.origin)return route.continue();if(url.origin==='https://djnaoyaman.github.io'&&url.pathname.startsWith('/cratediggin/assets/')){const response=await route.fetch({url:local.origin+url.pathname+url.search});return route.fulfill({response});}return route.abort();});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/tracks/mos-def-universal-magnetic.html');await page.locator('#article-art').waitFor();
 const artwork=page.locator('.track-artwork img');await artwork.scrollIntoViewIfNeeded();await artwork.evaluate(img=>img.decode());assert(await artwork.evaluate(img=>img.complete&&img.naturalWidth>0),'New artwork must actually decode from local build output');
 await page.locator('#toggle').dispatchEvent('click');
 assert((await page.locator('#now-title').innerText()).includes('Universal Magnetic'),'Global play must not select a different song');
 assert((await page.locator('#status').innerText()).includes('未確定'));
 await page.locator('#article-art').click();
 await page.locator('#art-toggle').click();
 assert((await page.locator('#now-title').innerText()).includes('Universal Magnetic'),'ART play must not select a different song');
 assert((await page.locator('#status').innerText()).includes('未確定'));
 await page.locator('#art-close').click();
 assert.equal(await page.locator('#article-play').count(),0,'No fake internal playback button');
 const link=page.locator('#view a[href="https://open.spotify.com/track/4UMsiE4vgpItrO3oMk19t7"]');
 assert(await link.count()>0);assert((await link.first().textContent()).includes('2005'));
 assert((await page.locator('#view').innerText()).includes('サイト内再生は確認中'));
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 await page.screenshot({path:'/tmp/external-audio-'+width+'.png',fullPage:true});
 await page.goto(base+'/tracks/mos-def-ms-fat-booty.html');await page.locator('#article-play').waitFor();
 assert.equal(await page.locator('#article-play').isDisabled(),false,'Existing playable tracks unaffected');
 assert.deepEqual(errors,[]);await context.close();
}console.log('External compilation link and unavailable internal audio state PASS; actual audio not attempted');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
