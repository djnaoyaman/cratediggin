const http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');

(async()=>{
 const root=path.resolve('dist');
 const server=http.createServer((req,res)=>{
  let relative=decodeURIComponent(req.url.split('?')[0]).replace(/^\/cratediggin\/?/,'');
  if(!relative||relative.endsWith('/'))relative+='index.html';
  const file=path.resolve(root,relative);
  if(!file.startsWith(root+path.sep)){res.writeHead(403).end();return;}
  try{res.setHeader('Content-Type',file.endsWith('.js')?'text/javascript':file.endsWith('.json')?'application/json':file.endsWith('.css')?'text/css':file.endsWith('.html')?'text/html':'application/octet-stream');res.end(fs.readFileSync(file));}catch{res.writeHead(404).end();}
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const base='http://127.0.0.1:'+server.address().port+'/cratediggin';
 let browser;
 try{
  browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||undefined});
  const context=await browser.newContext({viewport:{width:390,height:900}});
  await context.addInitScript(()=>{Element.prototype.requestFullscreen=()=>Promise.resolve();});
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await context.route('https://www.googletagmanager.com/**',r=>r.abort());
  await context.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:`
   window.__players=[];window.YT={Player:function(id,options){
    const p={options,loadVideoById(video){(window.__loads??=[]).push(video.videoId);queueMicrotask(()=>options.events?.onStateChange?.({data:1}));},cueVideoById(video){(window.__cues??=[]).push(video.videoId);},playVideo(){(window.__plays??=[]).push(id);options.events?.onStateChange?.({data:1});},pauseVideo(){(window.__pauses??=[]).push(id);options.events?.onStateChange?.({data:2});},stopVideo(){(window.__stops??=[]).push(id);},getDuration(){return 120;},getCurrentTime(){return 0;},seekTo(){},destroy(){}};
    const play=p.playVideo,pause=p.pauseVideo;
    p.makeReady=()=>{p.playVideo=play;p.pauseVideo=pause;options.events?.onReady?.({target:p});if(id==='yt')window.__ytReady=true;};
    window.__players.push(p);if(id==='sample-yt'&&window.__delaySample){delete p.playVideo;delete p.pauseVideo;}else queueMicrotask(p.makeReady);return p;
   }};window.onYouTubeIframeAPIReady();`}));


  const key='crate-my-playlist',button=page.locator('#art-crate-add');
  const snapshot=()=>page.evaluate(()=>({url:location.href,title:document.querySelector('#now-title').textContent,loads:window.__loads||[],plays:window.__plays||[],pauses:window.__pauses||[],cues:window.__cues||[],stops:window.__stops||[]}));
  const ids=()=>page.evaluate(k=>JSON.parse(localStorage.getItem(k)||'{"ids":[]}').ids,key);
  const open=async(path='/tracks/mass-appeal.html')=>{await page.goto(base+path);await page.waitForFunction(()=>window.__ytReady);if(await page.locator('#player-reveal').isVisible())await page.locator('#player-reveal').click();await page.locator('#art-open').click();await page.locator('#art-view').waitFor({state:'visible'});};
  await open();
  assert.equal(await button.locator('.record-disc').count(),1);
  const iconBox=await button.locator('svg').boundingBox();assert(iconBox.width>=32&&iconBox.height>=32);
  assert.equal(await button.locator('.record-groove').count(),2);
  assert(await button.locator('.record-plus').evaluate(e=>getComputedStyle(e).display!=='none'));
  assert(await button.locator('.record-minus').evaluate(e=>getComputedStyle(e).display!=='none'));
  await page.screenshot({path:'/tmp/art-record-unselected.png'});
  const id=await button.getAttribute('data-song-id'),before=await snapshot();
  await button.click();assert.equal(await button.getAttribute('aria-pressed'),'true');assert.deepEqual(await ids(),[id]);assert.deepEqual(await snapshot(),before);
  assert.equal(await button.locator('.record-plus').evaluate(e=>getComputedStyle(e).display!=='none'),false);assert(await button.locator('.record-minus').evaluate(e=>getComputedStyle(e).display!=='none'));await page.screenshot({path:'/tmp/art-record-selected.png'});
  assert((await button.getAttribute('aria-label')).includes('外す'));assert((await page.locator('#art-crate-status').textContent()).includes('追加'));
  await button.click();assert.equal(await button.getAttribute('aria-pressed'),'false');assert.deepEqual(await ids(),[]);assert.deepEqual(await snapshot(),before);
  await button.focus();await page.keyboard.press('Space');assert.equal(await button.getAttribute('aria-pressed'),'true');await page.keyboard.press('Enter');assert.deepEqual(await ids(),[]);assert.deepEqual(await snapshot(),before);
  await button.click();await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'art-close');await page.keyboard.press('Shift+Tab');assert.equal(await page.evaluate(()=>document.activeElement.id),'art-crate-add');
  await page.keyboard.press('Escape');await page.locator('#art-view').waitFor({state:'hidden'});assert.equal(await page.evaluate(()=>document.activeElement.id),'art-open');
  await open();assert.equal(await button.getAttribute('aria-pressed'),'true');
  const peer=await context.newPage();await peer.goto(base+'/about.html');
  const crossBefore=await snapshot();await peer.evaluate(k=>localStorage.setItem(k,JSON.stringify({name:'TEST',ids:[]})),key);await page.waitForFunction(()=>document.querySelector('#art-crate-add').getAttribute('aria-pressed')==='false');assert.deepEqual(await snapshot(),crossBefore);await peer.close();
  await page.evaluate(()=>{window.__realSetItem=Storage.prototype.setItem;Storage.prototype.setItem=function(){throw Error('quota');};});await button.click();assert((await page.locator('#art-crate-status').textContent()).includes('保存できません'));assert.deepEqual(await snapshot(),crossBefore);assert.equal(await button.getAttribute('aria-pressed'),'true');await button.click();assert.equal(await button.getAttribute('aria-pressed'),'false');assert.deepEqual(await snapshot(),crossBefore);await page.evaluate(()=>Storage.prototype.setItem=window.__realSetItem);
  // A playing custom queue remains the playback snapshot, even after its current track is removed.
  await page.evaluate(k=>localStorage.setItem(k,JSON.stringify({name:'TEST',ids:['can-i-kick-it','runnin']})),key);
  await page.goto(base+'/tracks/');await page.waitForFunction(()=>window.__ytReady);await page.locator('#my-crate-tab').click();await page.locator('#play-filter').click();await page.waitForFunction(()=>window.__loads?.length===1);if(await page.locator('#player-reveal').isVisible())await page.locator('#player-reveal').click();await page.locator('#art-open').click();
  const playing=await snapshot();await button.click();assert.deepEqual(await ids(),['runnin']);assert.deepEqual(await snapshot(),playing);assert.equal(await button.getAttribute('aria-pressed'),'false');
  await page.locator('#art-next').click();await page.waitForFunction(()=>document.querySelector('#art-crate-add').dataset.songId==='runnin');assert.equal(await button.getAttribute('aria-pressed'),'true');
  await page.locator('#art-toggle').click();const pausedStarted=await snapshot();await button.click();assert.deepEqual(await ids(),[]);assert.deepEqual(await snapshot(),pausedStarted);await page.locator('#art-toggle').click();assert.equal(await page.locator('#now-title').textContent(),pausedStarted.title);assert.deepEqual((await snapshot()).loads,pausedStarted.loads);
  // The same removal while merely cued must not load or navigate.
  await page.evaluate(k=>localStorage.setItem(k,JSON.stringify({name:'TEST',ids:['can-i-kick-it','runnin']})),key);
  await page.goto(base+'/tracks/');await page.waitForFunction(()=>window.__ytReady);await page.locator('#my-crate-tab').click();if(await page.locator('#player-reveal').isVisible())await page.locator('#player-reveal').click();await page.locator('#art-open').click();const paused=await snapshot();await button.click();assert.deepEqual(await snapshot(),paused);
  for(const viewport of [{width:320,height:740},{width:390,height:844},{width:1280,height:900},{width:740,height:360}]){
   await page.setViewportSize(viewport);await open();
   await page.evaluate(()=>{document.querySelector('#art-song').textContent='A long track title with its exact original version and extended descriptive subtitle';document.querySelector('#art-artist').textContent='Artist with featured collaborators';});
   const boxes=await page.locator('#art-view button').evaluateAll(bs=>bs.map(b=>{const r=b.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom};}));
   for(const b of boxes){assert(b.w>=44&&b.h>=44);assert(b.x>=0&&b.y>=0&&b.right<=viewport.width+1&&b.bottom<=viewport.height+1);}
   const overlap=await page.evaluate(()=>{const a=document.querySelector('.art-info').getBoundingClientRect(),b=document.querySelector('.art-controls').getBoundingClientRect();return a.left<b.right&&a.right>b.left&&a.top<b.bottom&&a.bottom>b.top;});assert.equal(overlap,false,'Title and controls must not overlap');
   await page.screenshot({path:'/tmp/art-crate-'+viewport.width+'.png'});
   await button.click();await button.click();
  }
  await open('/tracks/a-tribe-called-quest-sucka-nigga.html');assert.equal(await page.locator('#art-view').evaluate(e=>e.classList.contains('image-art')),false);const procedural=await snapshot();await button.click();await button.click();assert.deepEqual(await snapshot(),procedural);await page.screenshot({path:'/tmp/art-crate-procedural.png'});
  assert.deepEqual(errors,[]);console.log('ART VIEW crate toggle, persistence, queue/audio/navigation invariants, cross-tab, save failure, focus and responsive targets passed');
 }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=1;});
