'use strict';
// Real Chromium DOM/range/pointer/keyboard behavior; the YouTube provider is mocked.
const {chromium}=require('playwright'),fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const base=process.env.CRATE_PREVIEW_URL||'http://127.0.0.1:8765/cratediggin';
let fixture=vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/)[1]);
fixture=fixture.replace('getDuration(){return 120}','getDuration(){return this.duration??120}').replace('seekTo(t){this.t=t}',"seekTo(t,a){this.seeks=(this.seeks||[]).concat([[t,a]]);this.t=t;if(this.stateValue!==2)this.state(1)}");
const sizes=[[1280,900],[768,900],[390,844],[320,568],[320,420],[667,320],[560,300]];
const disjoint=(a,b)=>a.x+a.width<=b.x+1||b.x+b.width<=a.x+1||a.y+a.height<=b.y+1||b.y+b.height<=a.y+1;
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const [width,height] of sizes){
  const c=await browser.newContext({viewport:{width,height},reducedMotion:'reduce',hasTouch:width<700,serviceWorkers:'block'});
  await c.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin===new URL(base).origin)return r.continue();if(u.href==='https://www.youtube.com/iframe_api')return r.fulfill({contentType:'application/javascript',body:fixture});return r.abort()});
  await c.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
  const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base+'/tracks/mass-appeal.html');await p.waitForFunction(()=>window.__ready);await p.locator('#player-reveal').click();
  assert(await p.locator('#seek').isDisabled());assert(await p.locator('#art-seek').isDisabled());
  await p.locator('#article-art').click();for(const mode of ['full','video','hybrid']){await p.locator('#art-mode-'+mode).click();assert(await p.locator('#art-seek').isDisabled())}
  assert.equal(await p.evaluate(()=>window.__players.reduce((n,x)=>n+x.plays+x.loads,0)),0,'Opening/switching presentation never plays');await p.locator('#art-close').click();
  await p.locator('#article-play').click();await p.waitForFunction(()=>!document.querySelector('#seek').disabled);
  const ordinary=p.locator('#seek');assert.equal((await ordinary.boundingBox()).height,44);await ordinary.focus();await p.keyboard.press('End');await p.keyboard.press('Home');await p.keyboard.press('ArrowRight');assert.equal(await ordinary.inputValue(),'1');
  await p.locator('#toggle').click();await p.waitForFunction(()=>window.__players[0].stateValue===2);await ordinary.focus();await p.keyboard.press('ArrowRight');assert.equal(await p.evaluate(()=>window.__players[0].stateValue),2,'Keyboard seek retains pause');
  await p.locator('#article-art').click();
  const counts=await p.evaluate(()=>window.__players.map(x=>[x.plays,x.loads]));
  for(const mode of ['full','video','hybrid']){
   await p.locator('#art-mode-'+mode).click();const range=p.locator('#art-seek');await range.waitFor({state:'visible'});
   const r=await range.boundingBox(),view=await p.locator('#art-view').boundingBox();assert(r.height>=44&&r.width>=44);assert(r.x>=0&&r.y>=0&&r.x+r.width<=view.width+1&&r.y+r.height<=view.height+1);
   assert(await range.evaluate(e=>{const r=e.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===e}),'Seek hit target is uncovered');
   if(await p.locator('#yt').isVisible())assert(disjoint(await p.locator('.art-progress').boundingBox(),await p.locator('#yt').boundingBox()),'Seek never covers the native provider');
   assert(disjoint(await p.locator('.art-progress').boundingBox(),await p.locator('.art-controls').boundingBox()),'Seek and transport targets stay separate');
   if(await p.locator('.art-info').isVisible())assert(disjoint(await p.locator('.art-progress').boundingBox(),await p.locator('.art-info').boundingBox()),'Seek does not cover track information');
   const before=await p.evaluate(()=>window.__players[0].seeks?.length||0);
   await p.mouse.move(r.x+r.width*.2,r.y+r.height/2);await p.mouse.down();await p.mouse.move(r.x+r.width*.7,r.y+r.height/2,{steps:5});
   assert.equal(await p.evaluate(()=>window.__players[0].seeks?.length||0),before,'Pointer movement only previews');
   await p.mouse.up();assert.equal(await p.evaluate(()=>window.__players[0].seeks.length),before+1);assert.equal(await p.evaluate(()=>window.__players[0].stateValue),2);
   const expected=(r.width*.7-12)/(r.width-24)*120,actual=Number(await range.inputValue());assert(Math.abs(actual-expected)<=2,'Native thumb-center geometry maps to the requested position');
   if(width<700){await p.touchscreen.tap(r.x+r.width*.25,r.y+r.height/2);assert.equal(await p.evaluate(()=>window.__players[0].stateValue),2,'Touch tap retains pause')}
   await range.focus();await p.keyboard.press('Home');assert.equal(await range.inputValue(),'0');await p.keyboard.press('End');assert.equal(await range.inputValue(),'120');await p.keyboard.press('ArrowLeft');assert.equal(await range.inputValue(),'119');
   await range.evaluate(e=>{e.dispatchEvent(new PointerEvent('pointerdown',{pointerId:9,bubbles:true}));e.value='40';e.dispatchEvent(new Event('input',{bubbles:true}));e.dispatchEvent(new PointerEvent('pointercancel',{pointerId:9,bubbles:true}));e.dispatchEvent(new Event('change',{bubbles:true}))});assert.equal(await p.evaluate(()=>window.__players[0].t),119,'Cancelled preview does not seek');
   await p.screenshot({path:`/tmp/seek-${width}x${height}-${mode}.png`});
  }
  assert.deepEqual(await p.evaluate(()=>window.__players.map(x=>[x.plays,x.loads])),counts,'Seek and presentation add no play/load commands');
  await p.locator('#art-seek').focus();await p.keyboard.press('Escape');assert(await p.locator('#art-view').isHidden(),'Escape after a completed seek closes ART');assert.equal(await p.evaluate(()=>document.activeElement.id),'article-art');
  await p.evaluate(()=>{window.__players[0].duration=0});await p.waitForFunction(()=>document.querySelector('#seek').disabled);assert.equal(await p.locator('#duration').textContent(),'—');
  await p.evaluate(()=>{window.__players[0].duration=120});await p.waitForFunction(()=>!document.querySelector('#seek').disabled);
  assert.deepEqual(errors,[]);await c.close();
 }
 // Album uses its own current item; sample/inline owners cannot seek the paused main video.
 const c=await browser.newContext({viewport:{width:390,height:844}});await c.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin===new URL(base).origin)return r.continue();if(u.href==='https://www.youtube.com/iframe_api')return r.fulfill({contentType:'application/javascript',body:fixture});if(u.origin==='https://bandcamp.com')return r.fulfill({contentType:'text/html',body:'Native fixture'});return r.abort()});await c.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
 const p=await c.newPage();await p.goto(base+'/tracks/j-dilla-donuts.html');await p.waitForFunction(()=>window.__ready);await p.locator('#article-play').click();await p.waitForFunction(()=>!document.querySelector('#seek').disabled);await p.locator('#seek').focus();await p.keyboard.press('ArrowRight');assert.equal(await p.evaluate(()=>window.__players.find(x=>x.id.startsWith('album-')).t),1);assert.equal(await p.evaluate(()=>window.__players[0].seeks?.length||0),0);
 await p.goto(base+'/tracks/mass-appeal.html');await p.waitForFunction(()=>window.__ready);await p.locator('#sample-start').click();await p.waitForFunction(()=>document.querySelector('#seek').disabled);assert.equal(await p.evaluate(()=>window.__players[0].seeks?.length||0),0);
 await p.goto(base+'/tracks/ini-grown-man-sport.html');await p.waitForFunction(()=>window.__ready);await p.locator('#inline-player-open').click();assert(await p.locator('#seek').isDisabled());await c.close();
 console.log('Seek browser PASS: normal + ART/VIDEO/HYBRID, seven viewport sizes, native pointer/keyboard, cancel/pause/no-autoplay, owner isolation, elapsed/duration and unobscured provider. Mocked provider, no real iPhone/audio claim.');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
