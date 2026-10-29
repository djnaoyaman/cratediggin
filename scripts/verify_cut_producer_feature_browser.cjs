const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8765/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [320,390,768,1280]){
 const page=await browser.newPage({viewport:{width,height:960},reducedMotion:'reduce'});
 await page.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin===new URL(base).origin)return route.continue();if(u.origin==='https://djnaoyaman.github.io'&&u.pathname.startsWith('/cratediggin/')){let file='dist/'+decodeURIComponent(u.pathname.slice('/cratediggin/'.length));if(fs.existsSync(file)&&fs.statSync(file).isDirectory())file+='/index.html';if(fs.existsSync(file)&&fs.statSync(file).isFile()){const ext=file.split('.').pop(),mime={html:'text/html',js:'text/javascript',css:'text/css',json:'application/json',webp:'image/webp',png:'image/png',jpg:'image/jpeg',jpeg:'image/jpeg',svg:'image/svg+xml',woff2:'font/woff2'};return route.fulfill({status:200,body:fs.readFileSync(file),contentType:mime[ext]||'application/octet-stream'});}}return route.abort();});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/producers/cut-chemist.html');await page.waitForSelector('.feature-listening-route');
 assert.equal(await page.locator('.person-photo-header .person-photo').count(),1);assert.equal(await page.locator('.person-photo-header .person-photo-tag').count(),1);assert.equal(await page.locator('.person-tag-header').count(),0);
 assert.equal(await page.locator('.feature-listening-route li').count(),8);
 await page.waitForFunction(()=>{const im=document.querySelector('.person-photo-header .person-photo');return im&&im.complete&&im.naturalWidth>0});
 const art=await page.locator('.person-photo-header .person-photo').evaluate(im=>({ok:im.complete&&im.naturalWidth>0,r:im.getBoundingClientRect().width}));assert(art.ok&&art.r>width*.4);
 const fit=await page.locator('.person-photo-header .person-photo').evaluate(im=>({fit:getComputedStyle(im).objectFit,ratio:im.getBoundingClientRect().width/im.getBoundingClientRect().height,natural:im.naturalWidth/im.naturalHeight}));assert.equal(fit.fit,'contain');assert(Math.abs(fit.ratio-fit.natural)<0.01,'Full photo aspect ratio retained');
 assert.equal(await page.locator('iframe[src*="youtube"]').count(),0,'Reading must not autoplay or embed on entry');
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
 await page.screenshot({path:`/tmp/cut-producer-feature-${width}.png`,fullPage:true});
 assert.equal(await page.locator('[data-feature-scope=related]').isDisabled(),false);await page.locator('[data-feature-scope=related]').click();
 const relatedIds=['jurassic-5-the-game','jurassic-5-lesson-4-the-radio','jurassic-5-swing-set','dj-shadow-the-number-song-cut-chemist-remix'];
 for(const id of relatedIds)assert(await page.locator('#results a[href*="'+id+'"]').count()>0,'Related work missing: '+id);
 await page.locator('[data-feature-scope=own]').click();assert(await page.locator('#results a[href*="cut-chemist-the-garden"]').count()>0);
 for(const id of relatedIds)assert.equal(await page.locator('#results a[href*="'+id+'"]').count(),0,'Related artist leaked into own scope: '+id);
 await page.locator('[data-feature-scope=all]').click();
 await page.locator('#feature-route-play').click();await page.waitForURL(/lesson-4-the-radio/);assert((await page.locator('#view h1.song-heading').textContent()).includes('Lesson 4: The Radio'));
 await page.goBack();await page.waitForSelector('#feature-route-play');assert.equal(await page.locator('.feature-listening-route li').count(),8);
 await page.goForward();await page.waitForURL(/lesson-4-the-radio/);await page.goBack();await page.waitForSelector('#feature-route-play');
 await page.locator('.feature-listening-route a[href*="the-number-song-cut-chemist-remix"]').click();await page.waitForURL(/the-number-song-cut-chemist-remix/);assert((await page.locator('#view h1.song-heading').textContent()).includes('Remix'));
 await page.goBack();await page.waitForSelector('#feature-route-play');
 await page.goto(base+'/producers/');const card=page.locator('.feature-card:has(img.feature-photo[src*="feature-cut-chemist-provided-collage.webp"])');await card.waitFor();await card.scrollIntoViewIfNeeded();await card.locator('.feature-photo').evaluate(im=>im.decode());
 const bounds=await card.evaluate(el=>{const r=el.getBoundingClientRect(),im=el.querySelector('.feature-photo').getBoundingClientRect();return {w:r.width,inside:im.left>=r.left-1&&im.right<=r.right+1&&im.top>=r.top-1&&im.bottom<=r.bottom+1}});assert(bounds.w>200&&bounds.inside,'Complete card artwork contained');
 await card.locator('..').screenshot({path:`/tmp/cut-producer-feature-card-${width}.png`});await page.screenshot({path:`/tmp/cut-producer-feature-artists-${width}.png`,fullPage:true});
 await card.focus();await page.keyboard.press('Enter');await page.waitForSelector('.person-photo-header');
 await page.goto(base+'/#/feature/cut-chemist');await page.waitForSelector('.feature-listening-route');assert.equal(await page.locator('.feature-listening-route li').count(),8);assert((await page.locator('#view h1').textContent()).includes('Cut Chemist'));
 await page.goto(base+'/producers/');const featureCard=page.locator('.feature-card:has(img.feature-photo[src*="feature-cut-chemist-provided-collage.webp"])');await featureCard.waitFor();await featureCard.scrollIntoViewIfNeeded();await featureCard.locator('.feature-photo').evaluate(im=>im.decode());await featureCard.locator('..').screenshot({path:`/tmp/cut-producer-feature-index-card-${width}.png`});
 assert.equal(errors.length,0,errors.join('\n'));await page.close();
}
const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const plain=await context.newPage();await plain.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());await plain.goto(base+'/producers/cut-chemist.html');await plain.locator('.person-photo-header .person-photo').waitFor();assert((await plain.locator('#view h1').first().innerText()).includes('Cut Chemist'));assert.equal(await plain.locator('.feature-listening-route li').count(),8);await plain.locator('.person-photo-header .person-photo').evaluate(im=>im.decode());assert(await plain.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await plain.screenshot({path:'/tmp/cut-producer-photo-nojs-390.png',fullPage:true});await context.close();
console.log('Cut producer browser PASS: mobile/desktop provided-photo hero and no-JS, selected route, production/remix/mix distinctions, back/forward, direct+SPA navigation, no read autoplay');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
