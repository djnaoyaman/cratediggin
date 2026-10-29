const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8765/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [320,390,768,1280]){
 const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce'});
 await page.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin===new URL(base).origin)return route.continue();if(u.origin==='https://djnaoyaman.github.io'&&u.pathname.startsWith('/cratediggin/')){let file='dist/'+decodeURIComponent(u.pathname.slice('/cratediggin/'.length));if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file+='/index.html';if(fs.existsSync(file)&&fs.statSync(file).isFile()){const ext=file.split('.').pop(),mime={html:'text/html',js:'text/javascript',css:'text/css',json:'application/json',webp:'image/webp',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',svg:'image/svg+xml',woff2:'font/woff2'};return route.fulfill({status:200,body:fs.readFileSync(file),contentType:mime[ext]||'application/octet-stream'});}}return route.abort();});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/artists/jurassic-5.html');await page.waitForSelector('.feature-listening-route');
 assert.equal(await page.locator('.person-photo-header .person-photo').count(),1);assert.equal(await page.locator('.person-photo-header .person-photo-tag').count(),1);assert.equal(await page.locator('.person-tag-header').count(),0);
 assert.equal(await page.locator('.feature-listening-route li').count(),9);
 await page.waitForFunction(()=>{const im=document.querySelector('.person-photo-header .person-photo');return im&&im.complete&&im.naturalWidth>0});
 const art=await page.locator('.person-photo-header .person-photo').evaluate(im=>({ok:im.complete&&im.naturalWidth>0,r:im.getBoundingClientRect().width}));assert(art.ok&&art.r>width*.4);
 const fit=await page.locator('.person-photo-header .person-photo').evaluate(im=>({fit:getComputedStyle(im).objectFit,ratio:im.getBoundingClientRect().width/im.getBoundingClientRect().height,natural:im.naturalWidth/im.naturalHeight}));assert.equal(fit.fit,'contain');assert(Math.abs(fit.ratio-fit.natural)<0.01,'Full photo aspect ratio retained');
 assert.equal(await page.locator('iframe[src*="youtube"]').count(),0,'Reading must not autoplay or embed on entry');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
 await page.screenshot({path:`/tmp/jurassic-feature-${width}.png`,fullPage:true});
 await page.locator('#feature-route-play').click();await page.waitForURL(/the-game/);assert((await page.locator('#view h1.song-heading').textContent()).includes('The Game'));
 await page.goBack();await page.waitForSelector('#feature-route-play');assert.equal(await page.locator('.feature-listening-route li').count(),9);
 await page.goForward();await page.waitForURL(/the-game/);await page.goBack();await page.waitForSelector('#feature-route-play');
 await page.locator('.feature-listening-route a[href*="jayou-remix"]').click();await page.waitForURL(/jayou-remix/);assert((await page.locator('#view h1.song-heading').textContent()).includes('Remix'));
 await page.goBack();await page.waitForSelector('#feature-route-play');
 await page.goto(base+'/artists/');const card=page.locator('.feature-card:has(img.feature-photo[src*="feature-jurassic-5-provided-collage.webp"])');await card.waitFor();await card.scrollIntoViewIfNeeded();await card.locator('.feature-photo').evaluate(im=>im.decode());
 const bounds=await card.evaluate(el=>{const r=el.getBoundingClientRect(),im=el.querySelector('.feature-photo').getBoundingClientRect();return {w:r.width,inside:im.left>=r.left-1&&im.right<=r.right+1&&im.top>=r.top-1&&im.bottom<=r.bottom+1}});assert(bounds.w>200&&bounds.inside,'Complete card artwork contained');
 await card.locator('..').screenshot({path:`/tmp/jurassic-feature-card-${width}.png`});await page.screenshot({path:`/tmp/jurassic-feature-artists-${width}.png`,fullPage:true});
 await card.focus();await page.keyboard.press('Enter');await page.waitForSelector('.person-photo-header');
 await page.goto(base+'/features/');const featureCard=page.locator('.feature-card:has(img.feature-photo[src*="feature-jurassic-5-provided-collage.webp"])');await featureCard.waitFor();await featureCard.scrollIntoViewIfNeeded();await featureCard.locator('.feature-photo').evaluate(im=>im.decode());await featureCard.locator('..').screenshot({path:`/tmp/jurassic-feature-index-card-${width}.png`});
 assert.equal(errors.length,0,errors.join('\n'));await page.close();
}
const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const plain=await context.newPage();await plain.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());await plain.goto(base+'/artists/jurassic-5.html');await plain.locator('.person-photo-header .person-photo').waitFor();assert((await plain.locator('#view h1').first().innerText()).includes('Jurassic 5'));assert.equal(await plain.locator('.feature-listening-route li').count(),9);await plain.locator('.person-photo-header .person-photo').evaluate(im=>im.decode());assert(await plain.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await plain.screenshot({path:'/tmp/jurassic-photo-nojs-390.png',fullPage:true});await context.close();
console.log('J5 browser PASS: mobile/desktop provided-photo hero and no-JS, selected route, distinct remix, back/forward, direct+SPA navigation, no read autoplay');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
