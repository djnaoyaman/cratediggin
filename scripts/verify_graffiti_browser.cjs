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
   const loaded=page.waitForResponse(r=>r.url().endsWith('/assets/graffiti/mass-appeal.webp')&&r.ok());
   await page.locator('#art-open').click();
   await loaded;
   await page.locator('#art-view.image-art').waitFor({state:'visible'});
   await page.waitForFunction(()=>{const c=document.querySelector('#wall'),p=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=0;i<p.length;i+=80)if(p[i]<120)n++;return n>100;});
   assert(await page.locator('#art-view.image-art').isVisible());
   assert(await page.locator('#art-close').isVisible());
   assert(await page.locator('#art-next').isVisible());
   await page.screenshot({path:'/tmp/graffiti-'+width+'.png'});
   await page.locator('#art-close').click();
   await page.locator('#art-view').waitFor({state:'hidden'});
   assert.deepEqual(errors,[]);
   await context.close();
  }
  console.log('Generated graffiti loads and displays with controls on desktop and mobile');
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
