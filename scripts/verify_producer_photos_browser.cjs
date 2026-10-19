const{chromium}=require('playwright');const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true});try{
const ids=['dj-shadow','j-dilla','madlib','pete-rock','erick-sermon','tribe','gang-starr','public-enemy','nas','az','de-la-soul','beastie-boys','main-source','epmd'];
for(const width of[320,390,1280]){
 const seen=new Set();
 const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
 await context.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
 await context.route('https://www.youtube.com/iframe_api',r=>r.abort());await context.route('https://www.googletagmanager.com/**',r=>r.abort());
 const p=await context.newPage();
 for(const route of['artists/','producers/']){
  await p.goto('http://127.0.0.1:8765/cratediggin/'+route);await p.locator('.feature-poster').first().waitFor();await p.evaluate(()=>document.fonts.ready);
  for(const id of ids){
   const card=p.locator('.feature-poster').filter({has:p.locator('a.feature-card[href$="/'+id+'.html"]')});if(!await card.count())continue;assert.equal(await card.count(),1);assert(!seen.has(id));seen.add(id);
   await card.scrollIntoViewIfNeeded();const photo=card.locator('.feature-photo');await photo.evaluate(i=>i.decode());await card.locator('.feature-name-tag').evaluate(i=>i.decode());
   const g=await card.evaluate(c=>{const i=c.querySelector('.feature-photo'),t=c.querySelector('.feature-name-tag'),r=c.querySelector('.feature-portrait'),b=i.getBoundingClientRect(),tb=t.getBoundingClientRect(),rb=r.getBoundingClientRect(),s=getComputedStyle(i);const scale=Math.min(b.width/i.naturalWidth,b.height/i.naturalHeight),pw=i.naturalWidth*scale,ph=i.naturalHeight*scale;return{paint:{x:b.x+(b.width-pw)/2,y:b.y+(b.height-ph)/2,right:b.x+(b.width+pw)/2,bottom:b.y+(b.height+ph)/2,height:ph},dims:[i.naturalWidth,i.naturalHeight],fit:s.objectFit,filter:s.filter,blend:s.mixBlendMode,photo:{x:b.x,y:b.y,right:b.right,bottom:b.bottom,width:b.width,height:b.height},tag:{y:tb.y,bottom:tb.bottom},region:{x:rb.x,right:rb.right,bottom:rb.bottom},after:getComputedStyle(r,':after').display,decor:[...c.querySelectorAll('.feature-tape,.feature-paper-grain')].map(e=>getComputedStyle(e).display)}});
   assert.deepEqual(g.dims,[1456,816]);assert.equal(g.fit,'contain');assert.equal(g.filter,'none');assert.equal(g.blend,'normal');assert.equal(g.after,'none');assert(g.decor.every(x=>x==='none'));assert(g.photo.height>100&&g.photo.width>200);assert(g.paint.height>100,JSON.stringify(g));assert(g.paint.x>=g.region.x-.5&&g.paint.right<=g.region.right+.5&&g.paint.y>=g.photo.y-.5&&g.paint.bottom<=g.photo.bottom+.5,JSON.stringify(g));assert(g.photo.bottom<=g.tag.y+.5,JSON.stringify(g));assert(g.tag.bottom<=g.region.bottom+.5);assert(g.photo.x>=g.region.x-.5&&g.photo.right<=g.region.right+.5);
   await card.locator('summary').click();assert((await card.innerText()).includes('ユーザー提供'));assert.equal(await card.locator('.feature-photo-credit a').count(),0);await card.locator('summary').click();
   await card.screenshot({path:'/tmp/producer-collage-'+id+'-'+width+'.png'});
  }
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 }
 assert.deepEqual([...seen].sort(),[...ids].sort());await context.close();
}
const c=await browser.newContext({javaScriptEnabled:false}),p=await c.newPage();for(const route of['artists/','producers/']){await p.goto('http://127.0.0.1:8765/cratediggin/'+route);for(const im of await p.locator('.feature-portrait--provided .feature-photo').all()){await im.evaluate(i=>i.decode());assert.deepEqual(await im.evaluate(i=>[i.naturalWidth,i.naturalHeight]),[1456,816]);}}await c.close();
console.log('Fourteen full-composition supplied collages, separate original tags, truthful credits,320/390/1280 containment and no-JS PASS');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
