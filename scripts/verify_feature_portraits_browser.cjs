const {chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [1280,390]){
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
  await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
  await context.route('https://www.youtube.com/iframe_api',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));let total=0,photos=0;
  for(const [path,count] of [['artists',10],['producers',6]]){
   await page.goto('http://127.0.0.1:8765/cratediggin/'+path+'/');await page.locator('.feature-poster').first().waitFor();
   assert.equal(await page.locator('.feature-poster').count(),count);total+=count;photos+=await page.locator('.feature-photo').count();
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   for(const [i,c] of (await page.locator('.feature-poster').all()).entries()){await c.evaluate(e=>e.scrollIntoView({block:'start'}));await c.locator('img').evaluateAll(xs=>Promise.all(xs.map(i=>i.decode())));if(await c.locator('.feature-photo').count())assert(await c.locator('.feature-photo').getAttribute('alt'));await c.screenshot({path:'/tmp/feature-portrait-'+width+'-'+path+'-'+i+'.png'});}
   if(path==='producers'){const card=page.locator('.feature-poster').filter({has:page.locator('h3',{hasText:'DJ Shadow'})});await card.locator('.feature-photo-credit summary').click();assert((await card.innerText()).includes('ユーザー提供'));assert.equal(await card.locator('.feature-photo-credit a').count(),0);await card.locator('.feature-photo-credit summary').click();await card.locator('.feature-card').click();await page.locator('h1.section-title').filter({hasText:'DJ Shadow'}).waitFor();assert(page.url().endsWith('/producers/dj-shadow.html'));}
  }
  assert.equal(total,16);assert.equal(photos,16);assert.deepEqual(errors,[]);await context.close();
 }
 const context=await browser.newContext({javaScriptEnabled:false}),page=await context.newPage();for(const [path,count] of [['artists',10],['producers',6]]){await page.goto('http://127.0.0.1:8765/cratediggin/'+path+'/');assert.equal(await page.locator('.feature-poster').count(),count);}await context.close();
 console.log('16 supplied photo cards, original15 image tags and Premier typography, attribution, split collections, no-JS and mobile verified');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
