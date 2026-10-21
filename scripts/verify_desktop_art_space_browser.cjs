'use strict';
// Targeted CI only: actual app/renderer, local assets, mocked providers, no live playback.
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const crypto=require('node:crypto'),assert=require('node:assert/strict');
const F=JSON.parse(fs.readFileSync('scripts/fixtures/approved-desktop-art-space.json','utf8'));
const DIST=path.resolve('dist'),ORIGIN='http://127.0.0.1:8765',BASE=ORIGIN+'/cratediggin';
const OUT='/tmp/art-modes-desktop-',REPORT=OUT+'measurements.json';
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const candidateCSS=fs.readFileSync(path.join(DIST,'style.css'),'utf8');
assert.equal(sha(candidateCSS),F.afterStyleSHA256,'Built CSS must equal the approved candidate');
assert.equal(candidateCSS.split(F.patch).length-1,1,'The exact appended patch must occur once');
assert(candidateCSS.endsWith(F.patch),'The approved patch must be the final CSS append');
const baselineCSS=candidateCSS.slice(0,-F.patch.length);
assert.equal(sha(baselineCSS),F.beforeStyleSHA256,'Removing only the exact patch must recover baseline CSS');
const fixtureMatch=fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8').match(/const fixture=(`[^]*?`);/);
assert(fixtureMatch,'Existing local provider fixture must be present');
let providerFixture=vm.runInNewContext(fixtureMatch[1]);
const insert='window.__players.push(p);';
assert.equal(providerFixture.split(insert).length-1,1,'Expected one mock-player registration point');
providerFixture=providerFixture.replace(insert,`p.calls={};for(const key of ['loadVideoById','cueVideoById','loadPlaylist','cuePlaylist','playVideo','pauseVideo','stopVideo','seekTo','destroy','setLoop','setShuffle']){const original=p[key];if(typeof original==='function')p[key]=function(...args){this.calls[key]=(this.calls[key]||0)+1;return original.apply(this,args)}};${insert}`);
const report={base:F.base,evidence:'Actual local app DOM and forwarded native canvas draws/pixels; providers mocked; no live playback evidence.',styles:{baseline:F.beforeStyleSHA256,prototype:F.afterStyleSHA256},cases:[],comparisons:[],status:'running'};
const save=()=>fs.writeFileSync(REPORT,JSON.stringify(report,null,2)+'\n');
const near=(a,b,message,tolerance=1)=>assert(Math.abs(a-b)<=tolerance,`${message}: ${a} vs ${b}`);
const disjoint=(a,b,e=.01)=>!a||!b||a.right<=b.x+e||b.right<=a.x+e||a.bottom<=b.y+e||b.bottom<=a.y+e;
const rectEqual=(a,b,label)=>{assert.equal(!!a,!!b,label+' visibility');if(a&&b)for(const k of ['x','y','width','height'])near(a[k],b[k],label+'.'+k,.1)};
const shotName=(row,suffix)=>OUT+`${row.owner}-${row.width}x${row.height}-${row.variant}-${suffix}.png`;

async function setupContext(browser,row){
 const c=await browser.newContext({viewport:{width:row.width,height:row.height},deviceScaleFactor:1,reducedMotion:'reduce',serviceWorkers:'block'});
 c.setDefaultTimeout(10000);c.setDefaultNavigationTimeout(15000);
 const net={localRequests:0,localCSS:0,htmlHintsRemoved:0,mockApi:0,mockBandcamp:0,blocked:{},blockedWebSockets:[],errors:[]};row.network=net;
 assert.equal(typeof c.routeWebSocket,'function','Targeted CI requires Playwright WebSocket interception support');
 await c.routeWebSocket('**/*',socket=>{net.blockedWebSockets.push(socket.url());socket.close()});
 // A single pre-navigation route is fail-closed. Never fetch or continue an external URL.
 await c.route('**/*',async route=>{
  try{
   const request=route.request(),u=new URL(request.url());
   if(u.origin===ORIGIN){
    net.localRequests++;
    if(u.pathname==='/cratediggin/style.css'){
     net.localCSS++;
     return await route.fulfill({status:200,contentType:'text/css',body:row.variant==='baseline'?baselineCSS:candidateCSS});
    }
    if(request.isNavigationRequest()&&u.pathname.startsWith('/cratediggin/')&&u.pathname.endsWith('.html')){
     const filename=path.resolve(DIST,decodeURIComponent(u.pathname.slice('/cratediggin/'.length)));
     assert(filename.startsWith(DIST+path.sep),'Local HTML must remain inside dist');
     let body=fs.readFileSync(filename,'utf8');
     body=body.replace(/<link\b(?=[^>]*\brel\s*=\s*["'](?:preconnect|dns-prefetch)["'])[^>]*>/gi,()=>{net.htmlHintsRemoved++;return ''});
     return await route.fulfill({status:200,contentType:'text/html',headers:{'x-dns-prefetch-control':'off'},body});
    }
    return await route.continue();
   }
   if(u.href==='https://www.youtube.com/iframe_api'){
    net.mockApi++;return await route.fulfill({status:200,contentType:'application/javascript',body:providerFixture});
   }
   if(u.origin==='https://bandcamp.com'&&u.pathname.startsWith('/EmbeddedPlayer/')){
    net.mockBandcamp++;return await route.fulfill({status:200,contentType:'text/html',headers:{'content-security-policy':"default-src 'none'; style-src 'unsafe-inline'"},body:'<!doctype html><title>Mock Bandcamp</title><button style="min-height:40px">Native Bandcamp fixture</button>'});
   }
   net.blocked[u.hostname]=(net.blocked[u.hostname]||0)+1;
   return await route.abort('blockedbyclient');
  }catch(e){net.errors.push(String(e.stack||e));try{await route.abort('failed')}catch{}}
 });
 await c.addInitScript(()=>{
  Object.defineProperty(window,'CRATE_SITE_URL',{get:()=>location.origin+'/cratediggin',set(){}});
  window.__desktopArtDraw=null;
  const native=CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage=function(...args){
   const result=Reflect.apply(native,this,args); // Always perform the actual browser canvas operation.
   if(this.canvas.id==='wall'&&args.length===5&&args[0] instanceof HTMLImageElement){
    const source=args[0],m=this.getTransform();
    window.__desktopArtDraw={src:source.currentSrc||source.src,natural:[source.naturalWidth,source.naturalHeight],x:args[1],y:args[2],width:args[3],height:args[4],canvasWidth:this.canvas.width,canvasHeight:this.canvas.height,transform:[m.a,m.b,m.c,m.d,m.e,m.f]};
   }
   return result;
  };
 });
 return c;
}
async function settled(p){
 await p.evaluate(()=>document.fonts.ready);
 await p.waitForFunction(()=>{
  const im=document.querySelector('#artwork-image'),cv=document.querySelector('#wall'),d=window.__desktopArtDraw;
  return im?.complete&&im.naturalWidth>0&&d&&d.src===im.src&&d.canvasWidth===cv.width&&d.canvasHeight===cv.height;
 });
 await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
}
async function snapshot(p){
 return p.evaluate(()=>({
  players:window.__players.map(x=>({id:x.id,video:x.video,loads:x.loads,plays:x.plays,pauses:x.pauses,state:x.stateValue,t:x.t,index:x.index,destroyed:!!x.destroyed,calls:{...x.calls}})),
  now:document.querySelector('#now-title')?.textContent,
  storage:Object.fromEntries(Object.keys(localStorage).sort().map(k=>[k,localStorage.getItem(k)]))
 }));
}
async function unchanged(p,before,selector){
 assert.deepEqual(await snapshot(p),before,'Presentation/metadata operations must not alter observed provider state, commands or stored preferences');
 assert(await p.locator(selector).evaluate(e=>e===window.__desktopSavedFrame&&e.contentWindow===window.__desktopSavedWindow),'Same provider iframe and contentWindow');
}
async function measure(p,selector,mode){
 const result=await p.evaluate(({selector,mode})=>{
  function box(e){if(!e)return null;const r=e.getBoundingClientRect(),s=getComputedStyle(e);if(s.display==='none'||s.visibility==='hidden'||r.width===0||r.height===0)return null;return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom}}
  const ids={canvas:'#wall',brand:'.art-brand',credit:'.art-credit',signature:'.art-signature',close:'#art-close',info:'.art-info',title:'#art-song',artist:'#art-artist',controls:'.art-controls',help:'#art-provider-help',status:'#art-crate-status'};
  const boxes=Object.fromEntries(Object.entries(ids).map(([k,s])=>[k,box(document.querySelector(s))]));
  const buttons=[...document.querySelectorAll('.art-mode-controls button,.art-controls button,#art-close')].map(e=>{
   const r=box(e);if(!r)return null;const samples=[[.1,.1],[.5,.5],[.9,.9]].map(([x,y])=>{const t=document.elementFromPoint(r.x+r.width*x,r.y+r.height*y);return{hit:e.contains(t),tag:t?.tagName,id:t?.id,className:typeof t?.className==='string'?t.className:null}});return{id:e.id,rect:r,hit:samples.every(x=>x.hit),samples};
  }).filter(Boolean);
  const provider=document.querySelector(selector),pr=box(provider);
  const providerClear=pr?[[.1,.1],[.5,.5],[.9,.9]].every(([x,y])=>document.elementFromPoint(pr.x+pr.width*x,pr.y+pr.height*y)===provider):null;
  let alpha=null;
  if(mode!=='video'){
   const cv=document.querySelector('#wall'),r=cv.getBoundingClientRect(),data=cv.getContext('2d').getImageData(0,0,cv.width,cv.height).data;
   let minX=cv.width,minY=cv.height,maxX=-1,maxY=-1,count=0,sum=0;
   for(let y=0;y<cv.height;y++)for(let x=0;x<cv.width;x++){
    const a=data[(y*cv.width+x)*4+3];sum+=a;
    if(a>32){count++;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y)}
   }
   const sx=cv.width/r.width,sy=cv.height/r.height;
   alpha={threshold:32,count,sum,backing:[cv.width,cv.height],bounds:count?{x:minX/sx,y:minY/sy,width:(maxX-minX+1)/sx,height:(maxY-minY+1)/sy,absoluteX:r.x+minX/sx,absoluteY:r.y+minY/sy}:null};
  }
  const credit=document.querySelector('.art-credit'),sig=document.querySelector('.art-signature');
  return{mode,owner:document.body.dataset.artOwner,boxes,buttons,provider:pr,providerClear,providerVisibility:provider?getComputedStyle(provider).visibility:null,alpha,draw:mode!=='video'&&window.__desktopArtDraw?{...window.__desktopArtDraw}:null,creditName:credit?.getAttribute('aria-label'),signatureNatural:[sig?.naturalWidth,sig?.naturalHeight],scrollWidth:document.documentElement.scrollWidth,viewport:[innerWidth,innerHeight]};
 },{selector,mode});
 return result;
}
function assertLayout(m,row){
 const {boxes:b,buttons}=m,w=row.width,h=row.height;
 assert(m.scrollWidth<=w+1,'No horizontal document overflow');
 for(const q of buttons){const r=q.rect;assert(r.width>=44&&r.height>=44,`44px target ${q.id}`);assert(r.x>=0&&r.y>=0&&r.right<=w+1&&r.bottom<=h+1,`Contained target ${q.id}`);if(m.mode==='video'&&w>=1024&&q.id==='art-close'){
   // Existing VIDEO container intercepts only the lower edge. Keep this visible,
   // require the center usable, and compare the exact baseline mask below.
   assert(q.samples[0].hit&&q.samples[1].hit,'VIDEO CLOSE top and center remain usable');
   assert(!q.samples[2].hit&&q.samples[2].className==='art-mode-controls','Known baseline VIDEO close-edge interception only');
  }else assert(q.hit,`Unobstructed target ${q.id}`)}
 for(let i=0;i<buttons.length;i++)for(let j=i+1;j<buttons.length;j++)assert(disjoint(buttons[i].rect,buttons[j].rect),`Buttons overlap: ${buttons[i].id}, ${buttons[j].id}`);
 assert(b.credit&&b.signature,'Design credit and signature stay visible');
 assert.equal(m.creditName,'Designed by DJ Naoyaman');
 assert(m.signatureNatural[0]>0&&m.signatureNatural[1]>0,'Original signature decoded');
 near(b.signature.width,72,'Signature width',.1);near(b.signature.height,24,'Signature height',.1);
 for(const k of ['credit','signature','info','controls','help','status'])if(b[k])assert(b[k].x>=0&&b[k].y>=0&&b[k].right<=w+1&&b[k].bottom<=h+1,`Contained ${k}`);
 for(const key of ['brand','close','info','controls','help','status','canvas'])assert(disjoint(b.credit,b[key]),`Credit overlaps ${key}`);
 for(const q of buttons)if(q.id.startsWith('art-mode-'))for(const key of ['brand','credit','canvas','info','controls','help','status'])assert(disjoint(q.rect,b[key]),`${q.id} overlaps ${key}`);
 for(const a of ['info','controls','help','status'])for(const z of ['info','controls','help','status'])if(a<z)assert(disjoint(b[a],b[z]),`Footer overlap: ${a}/${z}`);
 if(m.mode!=='video'){
  assert(b.canvas&&m.alpha?.count>1000&&m.alpha.bounds,'Actual canvas contains painted artwork');
  for(const key of ['brand','credit','close','info','controls','help','status'])assert(disjoint(b.canvas,b[key]),`Canvas overlaps ${key}`);
  const d=m.draw;assert(d&&d.natural[0]>0&&d.natural[1]>0,'Recorded forwarded real image draw');
  assert(d.x>=-.1&&d.y>=-.1&&d.x+d.width<=b.canvas.width+.1&&d.y+d.height<=b.canvas.height+.1,'Actual renderer draw remains contained');
 }
 if(m.mode==='full')assert.equal(m.providerVisibility,'hidden','ART hides, not destroys, provider');
 else{
  assert(m.provider&&m.providerClear,'Provider rectangle remains uncovered');
  const pr=m.provider;assert(pr.width>=200&&pr.height>=(row.owner==='inline'?42:200),'Provider minimum dimensions');
  assert(pr.x>=0&&pr.y>=0&&pr.right<=w+1&&pr.bottom<=h+1,'Provider stays in viewport');
  for(const key of ['canvas','brand','credit','close','info','controls','help','status'])assert(disjoint(pr,b[key]),`Provider overlaps ${key}`);
  for(const q of buttons)assert(disjoint(pr,q.rect),`Provider overlaps button ${q.id}`);
 }
}
function sameStaticGeometry(a,b,label){
 for(const k of Object.keys(a.boxes))rectEqual(a.boxes[k],b.boxes[k],label+'.'+k);
 rectEqual(a.provider,b.provider,label+'.provider');
 assert.deepEqual(a.buttons,b.buttons,label+' hit-target boxes');
 assert.deepEqual(a.alpha,b.alpha,label+' actual alpha pixels/bounds');
 if(a.mode==='video'){assert.equal(a.draw,null);assert.equal(b.draw,null);assert.equal(a.alpha,null);assert.equal(b.alpha,null)}
 else for(const k of ['x','y','width','height','canvasWidth','canvasHeight'])near(a.draw[k],b.draw[k],label+'.draw.'+k,.01);
}
async function runCase(browser,{width,height,variant,owner}){
 const row={width,height,variant,owner,measurements:{},status:'running'};report.cases.push(row);
 const c=await setupContext(browser,row);let p;
 try{
  p=await c.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const slug=owner==='main'?'dr-octagon-bear-witness':owner==='album'?'j-dilla-donuts':owner==='inline'?'ini-grown-man-sport':'mass-appeal';
  const selector=owner==='sample'?'#sample-yt':owner==='album'?'#album-player-host iframe':owner==='inline'?'#inline-player-host iframe':'#yt';
  await p.goto(BASE+'/tracks/'+slug+'.html');await p.waitForFunction(()=>window.__ready===true);
  if(owner==='sample')await p.locator('#sample-start').click();
  if(owner==='album')await p.locator('#article-play').click();
  if(owner==='inline')await p.locator('#inline-player-open').click();
  await p.locator(selector).waitFor({state:'attached'});
  await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await p.locator(selector).evaluate(e=>{window.__desktopSavedFrame=e;window.__desktopSavedWindow=e.contentWindow});
  // A deterministic mock position, set before the no-new-commands baseline.
  await p.evaluate(()=>window.__players.forEach(x=>x.t=43));
  const before=await snapshot(p);row.before=before;
  await p.locator('#article-art').click();await settled(p);
  for(const mode of ['hybrid','full','video','hybrid','full','full']){
   await p.locator('#art-mode-'+mode).click();
   await p.waitForFunction(m=>document.body.dataset.artMode===m,mode);
   if(mode!=='video')await settled(p);
   else await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
   await p.locator('.art-signature').evaluate(i=>i.decode());
   await unchanged(p,before,selector);
   const m=await measure(p,selector,mode),first=!row.measurements[mode];
   if(first)row.measurements[mode]=m; // Keep evidence even when an assertion below fails.
   assert.equal(m.owner,mode==='full'?'full':owner==='album'?'main':owner);
   assertLayout(m,row);
   for(const id of ['full','video','hybrid'])assert.equal(await p.locator('#art-mode-'+id).getAttribute('aria-pressed'),String(id===mode));
   if(first)await p.screenshot({path:shotName(row,mode)})
   else if(mode!=='video')sameStaticGeometry(row.measurements[mode],m,mode+' roundtrip');
  }
  if(width>=1024){
   const expected=variant==='prototype'?96:150,canvas=row.measurements.full.boxes.canvas;
   near(canvas.y,expected,'ART canvas top');near(canvas.height,height-(variant==='prototype'?296:350),'ART canvas height');near(canvas.bottom,height-200,'ART footer reserve');
   const modes=row.measurements.full.buttons.filter(x=>x.id.startsWith('art-mode-'));
   near(modes[0].rect.x,variant==='prototype'?200:16,'First mode button x');
   for(const q of modes)near(q.rect.y,variant==='prototype'?14:94,'Mode button header row');
   const pr=row.measurements.hybrid.provider;
   near(pr.x,width-372,'Desktop HYBRID provider x');near(pr.width,360,'Desktop provider width');near(pr.height,owner==='inline'?42:200,'Desktop provider height');near(pr.y,(height-pr.height)/2,'Desktop provider y');
  }
  // A real long title is repeated only to force two-line metadata stress. No layout,
  // song data, queue, preferences or provider objects are changed by this probe.
  if(owner==='main'&&width===1280){
   const saved=await p.evaluate(()=>({title:document.querySelector('#art-song').textContent,artist:document.querySelector('#art-artist').textContent,status:document.querySelector('#art-crate-status').textContent}));
   try{
    await p.evaluate(()=>{
     const real=window.TRACKS.find(x=>x.id==='handsome-boy-modeling-school-if-it-wasnt-for-you');
     if(!real)throw Error('Required real long-title record missing');
     document.querySelector('#art-song').textContent=Array(5).fill(real.title).join(' / ');
     document.querySelector('#art-artist').textContent=real.artist;
     document.querySelector('#art-crate-status').textContent='Synthetic metadata test only';
    });
    await unchanged(p,before,selector);
    row.syntheticLongMetadata={label:'Synthetic two-line stress: five repetitions of a real catalog title; no playback or track change',measurement:await measure(p,selector,'full')};
    await p.screenshot({path:shotName(row,'synthetic-long-metadata')});
    assertLayout(row.syntheticLongMetadata.measurement,row);
    assert(await p.locator('#art-song').evaluate(e=>e.scrollHeight>e.clientHeight&&e.clientHeight>22*1.15+1&&e.clientHeight<=2.3*22+1),'Long title retains bounded scroll region');
   }finally{await p.evaluate(s=>{document.querySelector('#art-song').textContent=s.title;document.querySelector('#art-artist').textContent=s.artist;document.querySelector('#art-crate-status').textContent=s.status},saved)}
  }
  await p.locator('#art-close').focus();await p.keyboard.press('Escape');
  assert(await p.locator('#art-view').isHidden());assert.equal(await p.evaluate(()=>document.activeElement.id),'article-art');
  assert.equal(await p.locator('[inert]').count(),0);await unchanged(p,before,selector);
  await p.locator('#article-art').click();await settled(p);await unchanged(p,before,selector);
  assert.equal(await p.evaluate(()=>document.body.dataset.artMode),'full','Reopen retains presentation mode');
  await p.locator('#art-mode-hybrid').click();await settled(p);await unchanged(p,before,selector);
  sameStaticGeometry(row.measurements.hybrid,await measure(p,selector,'hybrid'),'HYBRID after close/reopen');
  await p.locator('#art-mode-video').click();
  await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await p.locator('#art-close').click();await unchanged(p,before,selector);
  assert(await p.locator('#art-view').isHidden(),'VIDEO CLOSE center click closes the presentation');
  assert.deepEqual(errors,[],'No page JavaScript errors');assert.deepEqual(row.network.errors,[],'No route errors');assert.deepEqual(row.network.blockedWebSockets,[],'No unexpected WebSocket attempts');
  assert(row.network.localCSS>0&&row.network.mockApi>0,'Candidate stylesheet and mocked API were actually used');
  if(owner==='inline')assert(row.network.mockBandcamp>0,'Bandcamp was fulfilled locally');
  row.status='passed';
 }catch(e){row.status='failed';row.error=String(e.stack||e);if(p)try{await p.screenshot({path:shotName(row,'failure')})}catch{};throw e}
 finally{save();await c.close()}
}
function comparePairs(){
 for(const [width,height] of [[1280,800],[1440,900],[390,844]]){
  const a=report.cases.find(x=>x.owner==='main'&&x.width===width&&x.variant==='baseline');
  const b=report.cases.find(x=>x.owner==='main'&&x.width===width&&x.variant==='prototype');
  sameStaticGeometry(a.measurements.hybrid,b.measurements.hybrid,'A/B HYBRID '+width);
  sameStaticGeometry(a.measurements.video,b.measurements.video,'A/B unchanged VIDEO including known close-edge hit mask '+width);
  if(width===390){sameStaticGeometry(a.measurements.full,b.measurements.full,'A/B unchanged mobile ART');report.comparisons.push({viewport:[width,height],full:'unchanged measured geometry and alpha pixels',hybrid:'unchanged measured geometry and alpha pixels'});continue}
  const x=a.measurements.full,y=b.measurements.full;
  near(y.boxes.canvas.y,x.boxes.canvas.y-54,'Measured top reclaim');near(y.boxes.canvas.height,x.boxes.canvas.height+54,'Measured height reclaim');near(y.boxes.canvas.bottom,x.boxes.canvas.bottom,'Unchanged canvas bottom');
  for(const key of ['brand','credit','signature','close','info','title','artist','controls','help','status'])rectEqual(x.boxes[key],y.boxes[key],'A/B unchanged chrome '+key);
  const expected=width===1280?[868,434,976,488]:[1068,534,1176,588];
  [x.draw.width,x.draw.height,y.draw.width,y.draw.height].forEach((n,i)=>near(n,expected[i],'Forwarded actual draw dimension '+i,.1));
  const ratio=y.draw.height/x.draw.height;
  near(y.alpha.bounds.width,x.alpha.bounds.width*ratio,'Measured painted alpha width gain',3);
  near(y.alpha.bounds.height,x.alpha.bounds.height*ratio,'Measured painted alpha height gain',3);
  assert(y.alpha.count>x.alpha.count,'Actual painted pixels must increase');
  report.comparisons.push({viewport:[width,height],drawBefore:[x.draw.width,x.draw.height],drawAfter:[y.draw.width,y.draw.height],measuredLinearGain:ratio-1,alphaBefore:x.alpha,alphaAfter:y.alpha,hybrid:'unchanged measured geometry and alpha pixels'});
 }
}
(async()=>{
 const browser=await chromium.launch({headless:true,args:['--disable-background-networking']});
 try{
  for(const [width,height] of [[1280,800],[1440,900],[390,844]])for(const variant of ['baseline','prototype'])await runCase(browser,{width,height,variant,owner:'main'});
  comparePairs();
  for(const owner of ['sample','album','inline'])await runCase(browser,{width:1280,height:800,variant:'prototype',owner});
  report.status='passed';
  console.log('Desktop ART actual renderer A/B: six Bear contexts and three provider-owner contexts passed. Local origin plus fulfilled mocks only; native media/playback not certified.');
 }catch(e){report.status='failed';report.error=String(e.stack||e);throw e}
 finally{
  save();
  console.log('DESKTOP_ART_COMPARISONS '+JSON.stringify(report.comparisons));
  console.log('DESKTOP_ART_CASES '+JSON.stringify(report.cases.map(r=>({owner:r.owner,viewport:[r.width,r.height],variant:r.variant,status:r.status,network:r.network,fullCanvas:r.measurements.full?.boxes.canvas,fullPaint:r.measurements.full?.alpha?.bounds,modes:r.measurements,error:r.error?.split('\n')[0]}))));
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1});
