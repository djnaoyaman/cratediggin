const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1280,390]){
   const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
   await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
   await context.route('https://www.youtube.com/iframe_api',r=>r.abort());
   await context.route('https://www.googletagmanager.com/**',r=>r.abort());
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto('http://127.0.0.1:8765/cratediggin/features/');
   const card=page.locator('.feature-poster').filter({has:page.locator('h3',{hasText:'DJ Shadow'})});await card.scrollIntoViewIfNeeded();
   await card.locator('.feature-photo').evaluate(i=>i.decode());await card.locator('.feature-name-tag').evaluate(i=>i.decode());
   assert.equal(await page.locator('.feature-card').count(),15);assert.equal(await page.locator('.feature-poster').count(),15);assert.equal(await page.locator('.feature-photo').count(),12);
   assert((await card.innerText()).includes('Scott Sandars'));
   assert.equal(await card.locator('.feature-photo-credit a').last().getAttribute('href'),'https://creativecommons.org/licenses/by/2.0/');
   assert((await card.locator('.feature-photo').getAttribute('alt')).includes('DJ Shadow'));
   assert.equal(await card.locator('.feature-name-tag').getAttribute('alt'),'');
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await card.screenshot({path:'/tmp/feature-portrait-'+width+'.png'});for(const [i,c] of (await page.locator('.feature-poster').all()).entries()){await c.scrollIntoViewIfNeeded();await page.waitForFunction(()=>[...document.querySelectorAll('.feature-poster img')].filter(i=>i.getBoundingClientRect().top<innerHeight&&i.getBoundingClientRect().bottom>0).every(i=>i.complete&&i.naturalWidth>0));if(await c.locator('.feature-photo').count())assert(await c.locator('.feature-photo').getAttribute('alt'));await c.screenshot({path:'/tmp/feature-portrait-'+width+'-'+i+'.png'});}
   await card.locator('.feature-card').click();await page.locator('h1.section-title').filter({hasText:'DJ Shadow'}).waitFor();
   assert.deepEqual(errors,[]);await context.close();
  }
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}}),page=await context.newPage();
  await page.goto('http://127.0.0.1:8765/cratediggin/features/');assert.equal(await page.locator('.feature-card').count(),15);assert(await page.locator('.feature-photo').count());await context.close();
  console.log('Licensed real-photo feature poster, attribution, accessible names, navigation, no-JS and desktop/mobile layout passed');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
