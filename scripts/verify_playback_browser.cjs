require('./verify_player_readiness.cjs');
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
  const page=await context.newPage(),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await context.route('https://www.googletagmanager.com/**',r=>r.abort());
  await context.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:`
   window.__players=[];window.YT={Player:function(id,options){
    const p={options,loadVideoById(video){(window.__loads??=[]).push(video.videoId);queueMicrotask(()=>options.events?.onStateChange?.({data:1}));},cueVideoById(){},playVideo(){(window.__plays??=[]).push(id);options.events?.onStateChange?.({data:1});},pauseVideo(){(window.__pauses??=[]).push(id);options.events?.onStateChange?.({data:2});},stopVideo(){},getDuration(){return 120;},getCurrentTime(){return 0;},seekTo(){},destroy(){}};
    const play=p.playVideo,pause=p.pauseVideo;
    p.makeReady=()=>{p.playVideo=play;p.pauseVideo=pause;options.events?.onReady?.({target:p});if(id==='yt')window.__ytReady=true;};
    window.__players.push(p);if(id==='sample-yt'&&window.__delaySample){delete p.playVideo;delete p.pauseVideo;}else queueMicrotask(p.makeReady);return p;
   }};window.onYouTubeIframeAPIReady();`}));

  const open=async()=>{await page.goto(base+'/tracks/');await page.waitForFunction(()=>window.__ytReady);};
  await open();
  await page.locator('#results .row-menu').first().click();
  await page.locator('#results .queue-remove').first().click();
  assert(page.url().endsWith('/tracks/'),'Removing a cued song must keep the list open');
  await page.locator('#undo-remove').click();
  await page.evaluate(()=>localStorage.setItem('crate-my-playlist',JSON.stringify({name:'TEST',ids:['can-i-kick-it','runnin']})));
  await open();await page.locator('#my-crate-tab').click();
  await page.locator('#play-filter').click();
  await page.waitForFunction(()=>window.__loads?.length===1);
  assert.equal(await page.locator('#now-title').textContent(),'Can I Kick It?');
  assert.equal(await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event'&&x[1]==='playback_start').length),1);
  const artistPath=await page.evaluate(()=>Object.values(window.CRATE_PAGES).find(p=>p.route.startsWith('#/artist/')).path);
  for(const route of ['/artists/tribe.html',artistPath.replace('/cratediggin',''),'/guides/first-ten.html']){
   await page.evaluate(url=>{const a=document.createElement('a');a.href=url;document.body.append(a);a.click();a.remove();},base+route);
  }
  await page.evaluate(()=>window.__players[0].options.events.onStateChange({data:0}));
  await page.waitForURL('**/tracks/runnin.html');
  assert.equal(await page.locator('#now-title').textContent(),"Runnin’");
  assert.equal(await page.evaluate(()=>window.__loads.length),2,'Browsing must preserve the selected next song');
  // An active song can also be removed without rendering into a detached list.
  await page.evaluate(url=>{const a=document.createElement('a');a.href=url+'/tracks/';document.body.append(a);a.click();a.remove();},base);
  await page.locator('#my-crate-tab').click();
  await page.locator('.record-row').filter({has:page.locator('a[href$="/runnin.html"]')}).locator('.row-menu').click();
  await page.locator('.record-row').filter({has:page.locator('a[href$="/runnin.html"]')}).locator('.queue-remove').click();
  await page.waitForURL('**/tracks/can-i-kick-it.html');
  assert.deepEqual(errors,[]);
  // Two already-open tabs edit the same persistent playlist.
  await page.evaluate(()=>localStorage.removeItem('crate-my-playlist'));await open();
  const other=await page.context().newPage();await other.goto(base+'/tracks/');
  const add=async(p,index)=>{await p.locator('#results .row-menu').nth(index).click();await p.locator('#results .crate-add').nth(index).click();};
  await add(page,0);await add(other,1);
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('crate-my-playlist')));
  assert.equal(saved.ids.length,2,'Both tabs must retain their edits');
  await page.waitForFunction(()=>document.querySelector('#my-crate-tab').textContent.includes('2曲'));
  await other.close();assert.deepEqual(errors,[]);
  // Removing the cued song must also exclude it from both global play controls.
  for(const button of ['#start','#toggle']){
   await page.evaluate(()=>localStorage.clear());await open();
   const excluded=await page.locator('#results .record-card').first().getAttribute('href');
   await page.locator('#results .row-menu').first().click();await page.locator('#results .queue-remove').first().click();
   await page.locator(button).click();await page.waitForFunction(()=>window.__loads?.length===1);
   const result=await page.evaluate(()=>({title:document.querySelector('#now-title').textContent,video:window.__loads[0],tracks:window.TRACKS}));
   const removed=result.tracks.find(t=>excluded.endsWith('/'+t.id+'.html'));
   assert.notEqual(result.video,removed.youtube.id);assert.notEqual(result.title,removed.title);
  }
  // A one-song queue must repeat even while another page is being read.
  await page.evaluate(()=>{localStorage.clear();localStorage.setItem('crate-my-playlist',JSON.stringify({name:'ONE',ids:['can-i-kick-it']}));});
  await open();await page.locator('#my-crate-tab').click();await page.locator('#play-filter').click();
  await page.waitForFunction(()=>window.__loads?.length===1);
  await page.evaluate(url=>{const a=document.createElement('a');a.href=url+'/artists/tribe.html';document.body.append(a);a.click();a.remove();},base);
  await page.evaluate(()=>window.__players[0].options.events.onStateChange({data:0}));
  await page.waitForFunction(()=>window.__loads?.length===2);
  assert.equal(await page.evaluate(()=>window.__loads[0]===window.__loads[1]),true);
  // Delayed sample readiness must not pause the main track or throw; retry after ready works.
  await page.goto(base+'/tracks/can-i-kick-it.html');await page.waitForFunction(()=>window.__ytReady);
  await page.evaluate(()=>window.__delaySample=true);
  await page.evaluate(url=>{const a=document.createElement('a');a.href=url+'/tracks/runnin.html';document.body.append(a);a.click();a.remove();},base);
  await page.locator('#article-play').click();
  const pauses=await page.evaluate(()=>window.__pauses?.filter(id=>id==='yt').length||0);
  await page.locator('#sample-start').click();
  assert.equal(await page.evaluate(()=>window.__pauses?.filter(id=>id==='yt').length||0),pauses);
  assert((await page.locator('#status').textContent()).includes('読み込み中'));
  await page.evaluate(()=>window.__players.at(-1).makeReady());
  await page.locator('#sample-start').click();
  assert.equal(await page.evaluate(()=>window.__plays.at(-1)),'sample-yt');
  await page.locator('#sample-return').click();
  assert.equal(await page.evaluate(()=>window.__plays.at(-1)),'yt');assert.deepEqual(errors,[]);
  for(const [route,button] of [['/tracks/','#play-filter'],['/artists/tribe.html','#feature-play'],['/guides/first-ten.html','#guide-play']]){
   await page.goto(base+route);await page.waitForFunction(()=>window.__ytReady);
   await page.locator(button).click();await page.waitForFunction(()=>window.__loads?.length===1);
   assert.equal(await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event'&&x[1]==='playback_start').length),1);
  }
  console.log('Playback start, exclusion, single-song repeat, delayed sample readiness, queue continuity, removal and cross-tab persistence passed');
 }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=1;});
