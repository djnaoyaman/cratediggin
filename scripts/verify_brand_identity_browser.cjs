const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const watchdog=setTimeout(()=>{console.error('Brand browser check exceeded60s');process.exit(1)},60000);
(async()=>{const browser=await chromium.launch({headless:true});try{for(const width of [390,1280]){
 const context=await browser.newContext({viewport:{width,height:844},javaScriptEnabled:false});const page=await context.newPage();page.setDefaultTimeout(10000);
 // Static scraper/head verification deliberately does not initialize any playback provider.
 for(const path of ['','tracks/a-tribe-called-quest-sucka-nigga.html','tracks/mass-appeal.html','timeline.html','producers/dj-premier.html','editor.html']){
  const response=await page.goto('http://127.0.0.1:8765/cratediggin/'+path);assert.equal(response.status(),200,path);
  const result=await page.evaluate(()=>({apple:[...document.querySelectorAll('link[rel="apple-touch-icon"]')].map(x=>x.href),manifest:[...document.querySelectorAll('link[rel="manifest"]')].map(x=>x.href),themes:[...document.querySelectorAll('meta[name="theme-color"]')].map(x=>x.content),social:document.querySelector('meta[property="og:image"]')?.content,canonical:document.querySelector('link[rel="canonical"]')?.href,frames:document.querySelectorAll('iframe').length}));
  assert.equal(result.apple.length,1);assert(result.apple[0].includes('/cratediggin/apple-touch-icon-tagging.png?v='));assert.equal(result.manifest.length,1);assert.deepEqual(result.themes,['#4169e1']);assert(result.social&&result.canonical);assert.equal(result.frames,0);
  const icon=await page.request.get(result.apple[0]);assert.equal(icon.status(),200);assert.equal(icon.headers()['content-type'].split(';')[0],'image/png');
  const manifest=await (await page.request.get(result.manifest[0])).json();assert.equal(manifest.theme_color,'#4169e1');assert.equal(manifest.icons.at(-1).purpose,'maskable');
 }
 await context.close();
}console.log('Brand heads/icons/manifest on six directly affected static routes at390/1280; no playback initialized PASS');}finally{clearTimeout(watchdog);await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
