const {chromium}=require('playwright'),assert=require('node:assert/strict');
const ids=["the-beatnuts-third-of-the-trio", "epmd-scratch-bring-it-back-part-2", "smif-n-wessun-wrektime", "brand-nubian-step-into-da-cipher", "redman-a-day-of-sooperman-lover", "showbiz-a-g-hold-ya-head"];
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [320,390,1280]){
 const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
 await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
 await context.route('https://www.youtube.com/iframe_api',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const id of ids){
  await page.goto('http://127.0.0.1:8765/cratediggin/tracks/'+id+'.html');await page.evaluate(()=>document.fonts.ready);
  const t=await page.evaluate(id=>window.TRACKS.find(t=>t.id===id),id);
  assert.equal(await page.locator('.song-heading').innerText(),t.title);
  const picture=page.locator('.track-artwork img');await picture.scrollIntoViewIfNeeded();await picture.evaluate(i=>i.decode());assert(await picture.isVisible());
  const geometry=await picture.evaluate(i=>{const r=i.getBoundingClientRect(),p=i.parentElement.getBoundingClientRect(),s=getComputedStyle(i.parentElement);return {width:r.width,height:r.height,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight,left:r.left,right:r.right,parentLeft:p.left,parentRight:p.right,bg:s.backgroundColor,bgImage:s.backgroundImage}});
  assert(geometry.naturalWidth>0&&geometry.naturalWidth<=2400&&geometry.naturalHeight>0);assert(geometry.width>0&&geometry.height>0);assert(geometry.left>=geometry.parentLeft-1&&geometry.right<=geometry.parentRight+1);
  assert.equal(geometry.bg,'rgba(0, 0, 0, 0)');assert.equal(geometry.bgImage,'none');assert((await picture.getAttribute('alt')).includes(t.title));
  if(id==='redman-a-day-of-sooperman-lover'){assert.equal(await page.locator('#sample-start').count(),0);assert((await page.locator('main').innerText()).includes('Superman Lover'));}
  assert.equal(await page.locator('.source-list>li').count(),t.sources.length);assert.equal(await page.locator('.editorial-deepdive').count(),2);
  const text=await page.locator('main').innerText();assert(text.includes(t.artist));assert(text.includes(t.deck));assert(!text.includes('Adam Tatar'));assert(!text.includes('HITS資料を追記'));assert(!text.includes('ユーザー指定'));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.locator('.track-artwork').screenshot({path:`/tmp/requested-six-art-${id}-${width}.png`});
  if(width===390){await page.screenshot({path:`/tmp/requested-six-page-${id}-${width}.png`,fullPage:true});}
  await page.locator('#article-art').click();await page.locator('#art-mode-full').click();await page.waitForFunction(()=>document.body.dataset.artOwner==='full');
  await page.waitForFunction(()=>{const c=document.querySelector('#wall'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=4)if(d[i]>30)n++;return n>1000});
  assert.equal(await page.locator('#art-song').innerText(),t.title);assert(await page.locator('#art-mode-video').isVisible());await page.screenshot({path:`/tmp/requested-six-full-${id}-${width}.png`});await page.keyboard.press('Escape');await page.locator('#art-view').waitFor({state:'hidden'});
 }
 assert.deepEqual(errors,[]);await context.close();
}
const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}}),p=await c.newPage();
for(const id of ids){await p.goto('http://127.0.0.1:8765/cratediggin/tracks/'+id+'.html');assert(await p.locator('main').innerText());assert(await p.locator('.track-artwork img').count());assert((await p.locator('main').innerText()).includes('出典'));}
await c.close();console.log('Six new pages: exact title/artist/deck/sources, alpha-art decode/containment,320/390/1280 and no-JS content passed; actual audio not asserted');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
