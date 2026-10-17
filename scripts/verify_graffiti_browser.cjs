const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  for(const width of [1280,390]){
   const context=await browser.newContext({viewport:{width,height:width===390?844:720},reducedMotion:'reduce'});
   await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
   const page=await context.newPage(),errors=[];
   page.on('pageerror',e=>errors.push(e.message));
   await context.route('https://www.googletagmanager.com/**',r=>r.abort());
   await context.route('https://www.youtube.com/iframe_api',r=>r.abort());
   await page.goto('http://127.0.0.1:8765/cratediggin/songs/mass-appeal.html');
   await page.locator('#art-open').click();
   await page.waitForFunction(()=>{const i=document.querySelector('#artwork-image');return i.complete&&i.naturalWidth>0;});
   assert.equal(await page.locator('#artwork-image').getAttribute('alt'),'Mass Appeal — Gang Starr｜CRATE DIGGIN｜DJ Naoyaman');
   await page.locator('#art-view.image-art').waitFor({state:'visible'});
   await page.waitForFunction(()=>{const c=document.querySelector('#wall'),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<p.length;i+=80)if(p[i]<120)n++;return n>100;});
   assert(await page.locator('#art-view.image-art').isVisible());
   assert.equal(await page.locator('#art-view .art-credit').getAttribute('aria-label'),'Designed by DJ Naoyaman');
   assert(await page.locator('#art-view .art-credit').isVisible());
   await page.waitForFunction(()=>{const i=document.querySelector('#art-view .art-signature');return i.complete&&i.naturalWidth>0});
   assert(await page.locator('#art-view .art-signature').isVisible());
   assert(await page.locator('#art-close').isVisible());
   assert(await page.locator('#art-next').isVisible());
   await page.screenshot({path:'/tmp/graffiti-'+width+'.png'});
   await page.locator('#art-close').click();
   await page.locator('#art-view').waitFor({state:'hidden'});
   assert.deepEqual(errors,[]);
   await context.close();
  }
  const animated=await browser.newContext({viewport:{width:1280,height:720},reducedMotion:'no-preference'});
  await animated.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
  await animated.route('https://www.googletagmanager.com/**',r=>r.abort());await animated.route('https://www.youtube.com/iframe_api',r=>r.abort());
  const moving=await animated.newPage(),motionErrors=[];moving.on('pageerror',e=>motionErrors.push(e.message));
  const ink=()=>moving.evaluate(()=>{const c=document.querySelector('#wall'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<d.length;i+=1013)n=(Math.imul(n,31)+d[i])>>>0;return n});
  for(const [id,mode] of [['93-til-infinity','drift'],['mass-appeal','groove'],['bucktown','stomp'],['dj-shadow-the-number-song','burst']]){
   await moving.goto('http://127.0.0.1:8765/cratediggin/songs/'+id+'.html');await moving.locator('#art-open').click();
   await moving.locator('#art-view[data-motion="'+mode+'"]').waitFor({state:'visible'});
   const duration=await moving.evaluate(id=>window.TRACKS.find(t=>t.id===id).art.motion.duration,id);
   if(await moving.locator('#artwork-image').isVisible())await moving.waitForFunction(()=>{const i=document.querySelector('#artwork-image');return i.complete&&i.naturalWidth>0});
   await moving.waitForTimeout(80);const first=await ink();await moving.waitForTimeout(Math.round(duration*.4));const middle=await ink();assert.notEqual(first,middle,mode+' must visibly animate');
   await moving.screenshot({path:'/tmp/graffiti-motion-'+mode+'.png'});await moving.waitForTimeout(duration+100);const done=await ink();await moving.waitForTimeout(120);assert.equal(await ink(),done,mode+' should settle without an endless loop');
  }
  assert.deepEqual(motionErrors,[]);await animated.close();
  console.log('Generated graffiti loads and displays with controls on desktop and mobile; four tension entrances animate and settle');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
