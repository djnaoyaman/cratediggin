const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8765/cratediggin';
const expected=JSON.parse(fs.readFileSync('dist/site-updated.json','utf8'));
const day=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Tokyo',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date(expected.site.dateModified));
(async()=>{const browser=await chromium.launch({headless:true});const report=[];try{
 for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:960},reducedMotion:'reduce'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/');await page.locator('.site-update').waitFor();
  assert.equal(await page.locator('.site-update').count(),1);
  assert.equal(await page.locator('.site-update time').getAttribute('datetime'),expected.site.dateModified);
  assert.equal(await page.locator('.site-update time').textContent(),day);
  await page.waitForFunction(()=>document.documentElement.dataset.metadataRoute==='#/');
  const home=await page.locator('script[type="application/ld+json"]').last().textContent();
  assert.equal(JSON.parse(home)['@graph'][0].dateModified,expected.site.dateModified);
  await page.evaluate(async()=>{await document.fonts.ready;document.querySelector('.site-update').scrollIntoView({behavior:'instant',block:'center'});await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));});
  await page.waitForFunction(()=>{const r=document.querySelector('.site-update').getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight;});
  assert(await page.locator('.site-update').isVisible());
  await page.locator('footer').screenshot({path:`/tmp/site-update-home-${width}.png`,animations:'disabled'});
  await page.locator('a[data-nav="editor"]').first().click();await page.locator('#view .page-update').waitFor();
  assert.equal(await page.locator('#view .page-update time').getAttribute('datetime'),expected.profile.dateModified);
  await page.waitForFunction(()=>document.documentElement.dataset.metadataRoute==='#/editor');
  assert.equal(JSON.parse(await page.locator('script[type="application/ld+json"]').last().textContent())['@graph'][0].dateModified,expected.profile.dateModified);
  await page.locator('#view .page-update').scrollIntoViewIfNeeded();await page.screenshot({path:`/tmp/site-update-editor-${width}.png`});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'No horizontal overflow');
  await page.goBack();await page.waitForFunction(()=>document.documentElement.dataset.metadataRoute==='#/');
  assert.equal(await page.locator('.site-update').count(),1);
  assert.deepEqual(errors,[]);report.push({width,staticFooter:true,spaProfile:true,backNavigation:true});await context.close();
 }
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:960}});
 await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
 const page=await context.newPage();await page.goto(base+'/editor.html');assert.equal(await page.locator('.page-update time').getAttribute('datetime'),expected.profile.dateModified);
 await page.locator('.page-update').scrollIntoViewIfNeeded();await page.screenshot({path:'/tmp/site-update-editor-no-js-390.png'});await context.close();
 const xml=fs.readFileSync('dist/sitemap.xml','utf8');assert(xml.includes('<lastmod>'+expected.site.dateModified+'</lastmod>'));assert(xml.includes('<lastmod>'+expected.profile.dateModified+'</lastmod>'));
 fs.writeFileSync('/tmp/site-update-report.json',JSON.stringify({expected,report,noJS:true},null,2));
 console.log('Truthful site/profile dates: 390/1280 static/SPA/back/no-JS and metadata PASS');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
