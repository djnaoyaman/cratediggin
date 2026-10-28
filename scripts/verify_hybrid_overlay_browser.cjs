'use strict';
// CI browser QA: real site DOM/canvas, mocked provider. Never certifies audio playback.
const {chromium}=require('playwright'),fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const BASE='http://127.0.0.1:8765/cratediggin',BASE_SHA='8c5b2f6fc0abfd88d2422dc5673d8e162570a019';
const router=fs.readFileSync('src/app/router.js','utf8'),css=fs.readFileSync('dist/style.css','utf8'),app=fs.readFileSync('dist/app.js','utf8');
const geometryContext={};vm.createContext(geometryContext);vm.runInContext(router.slice(router.indexOf(' function legacyArtDockGeometry'),router.indexOf(' function artVideoGeometry'))+';globalThis.geometry=artDockGeometry;',geometryContext);
const oldRouter=cp.execFileSync('git',['show',BASE_SHA+':src/app/router.js'],{encoding:'utf8'}),oldCSS=cp.execFileSync('git',['show',BASE_SHA+':src/assets/style.css'],{encoding:'utf8'});
assert(app.includes(router));const oldApp=app.replace(router,oldRouter);
let fixture=vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/)[1]);
fixture=fixture.replace("frame.title='Native provider fixture'","frame.allowFullscreen=true;frame.title='Native provider fixture'");
const sizes=[[1440,900],[1180,757],[1024,768],[768,900],[390,844],[320,568],[390,600],[320,420],[390,500],[320,486],[844,390],[667,320],[568,320],[560,300]];
const report={evidence:'Mocked providers, real browser geometry/controls; no real audio or physical-device verification',cases:[],preservedModes:0};
const disjoint=(a,b)=>a.x+a.width<=b.x+.5||b.x+b.width<=a.x+.5||a.y+a.height<=b.y+.5||b.y+b.height<=a.y+.5;
const rect=async(p,s)=>p.locator(s).boundingBox();
const snapshot=p=>p.evaluate(()=>window.__players.map(x=>[x.loads,x.plays,x.pauses,x.t,x.index,x.stateValue]));
async function setup(browser,owner,variant){
 const c=await browser.newContext({viewport:{width:1180,height:757},reducedMotion:'reduce',serviceWorkers:'block'});
 await c.route('**/*',async r=>{const u=new URL(r.request().url());if(u.origin==='http://127.0.0.1:8765'){if(u.pathname.endsWith('/style.css'))return r.fulfill({contentType:'text/css',body:variant==='baseline'?oldCSS:css});if(u.pathname.endsWith('/app.js'))return r.fulfill({contentType:'application/javascript',body:variant==='baseline'?oldApp:app});return r.continue()}if(u.href==='https://www.youtube.com/iframe_api')return r.fulfill({contentType:'application/javascript',body:fixture});if(u.origin==='https://bandcamp.com')return r.fulfill({contentType:'text/html',body:'<button>Native Bandcamp fixture</button>'});return r.abort()});
 await c.addInitScript(()=>Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}}));
 const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(BASE+'/tracks/'+(owner==='album'?'j-dilla-donuts':owner==='inline'?'ini-grown-man-sport':'mass-appeal')+'.html');await p.waitForFunction(()=>window.__ready);await p.evaluate(()=>document.fonts.ready);
 await p.locator(owner==='sample'?'#sample-start':owner==='inline'?'#inline-player-open':'#article-play').click();await p.evaluate(()=>window.__players.forEach(x=>x.t=43));
 const provider=owner==='sample'?'#sample-yt':owner==='album'?'#album-player-host iframe':owner==='inline'?'#inline-player-host iframe':'#yt';
 await p.locator(provider).evaluate(e=>{window.__keptFrame=e;window.__keptWindow=e.contentWindow});const before=await snapshot(p);await p.locator('#article-art').click();return {c,p,provider,before,errors};
}
async function boxes(p,provider){return p.evaluate(sel=>Object.fromEntries(['#wall','.art-credit','.art-mode-controls','#art-close',sel].map(s=>{const e=document.querySelector(s),r=e.getBoundingClientRect(),v=getComputedStyle(e);return [s,{x:r.x,y:r.y,width:r.width,height:r.height,visibility:v.visibility,display:v.display}]})),provider)}
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const owner of ['main','sample','album','inline']){
  const baseline=await setup(browser,owner,'baseline'),old=new Map();
  for(const [width,height] of sizes){await baseline.p.setViewportSize({width,height});for(const mode of ['full','video']){await baseline.p.locator('#art-mode-'+mode).click();old.set(`${width}x${height}/${mode}`,await boxes(baseline.p,baseline.provider))}}await baseline.c.close();
  const {c,p,provider,before,errors}=await setup(browser,owner,'candidate');
  for(const [width,height] of sizes){await p.setViewportSize({width,height});for(const mode of ['hybrid','full','video','hybrid']){
   await p.locator('#art-mode-'+mode).click();const actual=await p.evaluate(()=>document.body.dataset.artMode);if(mode==='hybrid')assert.equal(actual,geometryContext.geometry(width,height,owner==='inline',{})?'hybrid':'full');
   assert(await p.locator(provider).evaluate(e=>e===window.__keptFrame&&e.contentWindow===window.__keptWindow));assert.deepEqual(await snapshot(p),before,'Presentation cannot send transport commands');
   if(mode!=='hybrid'){assert.deepEqual(await boxes(p,provider),old.get(`${width}x${height}/${mode}`),'ART/VIDEO artwork, provider, credit and header geometry unchanged (transport footer now includes seek)');report.preservedModes++;continue}
   if(actual!=='hybrid')continue;
   const room=await rect(p,'#art-view'),video=await rect(p,provider),canvas=await rect(p,'#wall');assert.equal(room.width,width);assert.equal(room.height,height);assert(canvas.width>=width-25,'No side column reserved for video');if(owner!=='inline')assert(!disjoint(canvas,video),'HYBRID native video overlays full artwork stage');
   assert(video.width>=200&&video.height>=(owner==='inline'?42:200));if(owner!=='inline'&&(width<700||height<=500)){assert(video.x>=canvas.x+7&&video.y>=canvas.y+7&&video.x+video.width<=canvas.x+canvas.width-7&&video.y+video.height<=canvas.y+canvas.height-7,'Native player lies inside artwork with inset');assert.equal(Math.round(video.width),Math.max(200,Math.round(canvas.width*.35)));}assert(video.x>=0&&video.y>=0&&video.x+video.width<=width+1&&video.y+video.height<=height+1);assert(width-(video.x+video.width)<=25,'Right corner anchor');assert(video.y+video.height>height*.6,'Lower corner anchor');
   for(const s of ['.art-controls','.art-progress','#art-close','.art-mode-controls','.art-info','.art-credit','#art-provider-help']){const b=await rect(p,s);assert(disjoint(video,b),`${owner} ${width}x${height}: provider covers ${s}`)}
   for(const s of ['#art-close','#art-mode-full','#art-mode-video','#art-mode-hybrid','#art-prev','#art-next','#art-crate-add']){assert(await p.locator(s).evaluate(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44&&e.contains(document.elementFromPoint(r.x+r.width/2,r.y+r.height/2))}),s+' hit target')}
   assert(await p.locator(provider).evaluate(e=>{const r=e.getBoundingClientRect();return [[.05,.05],[.5,.5],[.95,.95]].every(([x,y])=>document.elementFromPoint(r.x+r.width*x,r.y+r.height*y)===e)}),'Native provider uncovered');
   await p.waitForFunction(()=>document.querySelector('#artwork-image')?.naturalWidth>0);await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   if(owner==='main')await p.screenshot({path:`/tmp/hybrid-overlay-${width}x${height}.png`});report.cases.push({owner,width,height,room,video,canvas});
  }}
  for(const width of [568,667]){await p.setViewportSize({width,height:320});await p.addStyleTag({content:':root{--art-safe-left:44px;--art-safe-right:44px;--art-safe-bottom:21px;--art-safe-top:0px}'});await p.locator('#art-mode-full').click();await p.locator('#art-mode-hybrid').click();if(!geometryContext.geometry(width,320,owner==='inline',{left:44,right:44,bottom:21,top:0})){assert.equal(await p.evaluate(()=>document.body.dataset.artMode),'full');continue}const r=await rect(p,provider);assert(r.x>=44&&r.x+r.width<=width-44+1&&r.y>=52&&r.y+r.height<=299);for(const s of ['.art-controls','.art-progress','#art-close','.art-mode-controls','.art-info','.art-credit','#art-provider-help'])assert(disjoint(r,await rect(p,s)),`Notch ${width}: ${s}`)}
  await p.setViewportSize({width:1180,height:757});await p.locator('#art-mode-full').click();await p.locator('#art-mode-hybrid').click();await p.keyboard.press('Escape');assert(await p.locator('#art-view').isHidden());assert(await p.locator('#article-art').evaluate(e=>e===document.activeElement),'Close restores invoking focus');assert.deepEqual(await snapshot(p),before);assert.equal(await p.locator('[inert]').count(),0);assert.deepEqual(errors,[]);await c.close();
 }
 fs.writeFileSync('/tmp/hybrid-overlay-report.json',JSON.stringify(report,null,2));console.log(`HYBRID overlay PASS: ${report.cases.length} owner/viewport cases, ${report.preservedModes} unchanged ART/VIDEO comparisons, notch-safe controls and frame/transport preservation. Mocked providers only.`);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
