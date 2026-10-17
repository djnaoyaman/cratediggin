const {chromium}=require('playwright'),assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [1280,390]){
  const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
  await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
  await context.route('https://www.youtube.com/iframe_api',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  for(const [old,dest] of [['songs/can-i-kick-it.html','tracks/can-i-kick-it.html'],['features/dj-shadow.html','producers/dj-shadow.html'],['features/tribe-production.html','artists/tribe.html'],['features/','artists/'],['songs/?q=Jazz%20%26%20Soul','tracks/?q=Jazz%20%26%20Soul']]){
   await page.goto('http://127.0.0.1:8765/cratediggin/'+old);await page.waitForURL('**/cratediggin/'+dest);assert(await page.locator('main').count());
  }
  await page.goto('http://127.0.0.1:8765/cratediggin/tracks/can-i-kick-it.html');
  const image=page.locator('.track-artwork img');await image.evaluate(i=>i.decode());assert(await image.isVisible());assert((await image.getAttribute('alt')).includes('DJ Naoyaman'));
  assert(await image.evaluate(i=>i.getBoundingClientRect().width>200&&i.getAttribute('width')&&i.getAttribute('height')));
  await image.screenshot({path:'/tmp/crawl-artwork-'+width+'.png'});
  for(const [label,path] of [['ARTISTS','artists/'],['PRODUCERS','producers/'],['TRACKS','tracks/']]){await page.locator('header nav').getByRole('link',{name:label,exact:true}).click();assert(page.url().endsWith('/'+path));assert.equal(await page.locator('header nav .active').innerText(),label);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));}
  await page.goBack();assert(page.url().endsWith('/producers/'));await page.goForward();assert(page.url().endsWith('/tracks/'));
  await page.locator('header').screenshot({path:'/tmp/migration-navigation-'+width+'.png'});assert.deepEqual(errors,[]);await context.close();
 }
 const context=await browser.newContext({javaScriptEnabled:false}),page=await context.newPage();await page.goto('http://127.0.0.1:8765/cratediggin/tracks/can-i-kick-it.html');assert(await page.locator('.track-artwork img').isVisible());await page.goto('http://127.0.0.1:8765/cratediggin/songs/can-i-kick-it.html');await page.waitForURL('**/tracks/can-i-kick-it.html');assert(await page.locator('h1').count());await context.close();console.log('Legacy direct redirects, query preservation, navigation history, static visible art and mobile layout passed');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
