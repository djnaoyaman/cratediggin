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
  await page.route('https://www.googletagmanager.com/**',r=>r.abort());
  await page.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:`
   window.__players=[];window.YT={Player:function(id,options){
    const p={options,loadVideoById(video){(window.__loads??=[]).push(video.videoId);queueMicrotask(()=>options.events?.onStateChange?.({data:1}));},cueVideoById(){},playVideo(){options.events?.onStateChange?.({data:1});},pauseVideo(){options.events?.onStateChange?.({data:2});},stopVideo(){},getDuration(){return 120;},getCurrentTime(){return 0;},seekTo(){},destroy(){}};
    window.__players.push(p);queueMicrotask(()=>{options.events?.onReady?.();window.__ytReady=true;});return p;
   }};window.onYouTubeIframeAPIReady();`}));

  const open=async()=>{await page.goto(base+'/songs/');await page.waitForFunction(()=>window.__ytReady);};
  await open();
  await page.locator('#results .row-menu').first().click();
  await page.locator('#results .queue-remove').first().click();
  assert(page.url().endsWith('/songs/'),'Removing a cued song must keep the list open');
  await page.locator('#undo-remove').click();
  await page.evaluate(()=>localStorage.setItem('crate-my-playlist',JSON.stringify({name:'TEST',ids:['can-i-kick-it','runnin']})));
  await open();await page.locator('#my-crate-tab').click();
  await page.locator('#play-filter').click();
  await page.waitForFunction(()=>window.__loads?.length===1);
  assert.equal(await page.locator('#now-title').textContent(),'Can I Kick It?');
  assert.equal(await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event'&&x[1]==='playback_start').length),1);
  const artistPath=await page.evaluate(()=>Object.values(window.CRATE_PAGES).find(p=>p.route.startsWith('#/artist/')).path);
  for(const route of ['/features/tribe.html',artistPath.replace('/cratediggin',''),'/guides/first-ten.html']){
   await page.evaluate(url=>{const a=document.createElement('a');a.href=url;document.body.append(a);a.click();a.remove();},base+route);
  }
  await page.evaluate(()=>window.__players[0].options.events.onStateChange({data:0}));
  await page.waitForURL('**/songs/runnin.html');
  assert.equal(await page.locator('#now-title').textContent(),"Runnin’");
  assert.equal(await page.evaluate(()=>window.__loads.length),2,'Browsing must preserve the selected next song');
  // An active song can also be removed without rendering into a detached list.
  await page.evaluate(url=>{const a=document.createElement('a');a.href=url+'/songs/';document.body.append(a);a.click();a.remove();},base);
  await page.locator('#my-crate-tab').click();
  await page.locator('.record-row').filter({has:page.locator('a[href$="/runnin.html"]')}).locator('.row-menu').click();
  await page.locator('.record-row').filter({has:page.locator('a[href$="/runnin.html"]')}).locator('.queue-remove').click();
  await page.waitForURL('**/songs/can-i-kick-it.html');
  assert.deepEqual(errors,[]);
  // Two already-open tabs edit the same persistent playlist.
  await page.evaluate(()=>localStorage.removeItem('crate-my-playlist'));await open();
  const other=await page.context().newPage();await other.goto(base+'/songs/');
  const add=async(p,index)=>{await p.locator('#results .row-menu').nth(index).click();await p.locator('#results .crate-add').nth(index).click();};
  await add(page,0);await add(other,1);
  const saved=await page.evaluate(()=>JSON.parse(localStorage.getItem('crate-my-playlist')));
  assert.equal(saved.ids.length,2,'Both tabs must retain their edits');
  await page.waitForFunction(()=>document.querySelector('#my-crate-tab').textContent.includes('2曲'));
  await other.close();assert.deepEqual(errors,[]);
  for(const [route,button] of [['/songs/','#play-filter'],['/features/tribe.html','#feature-play'],['/guides/first-ten.html','#guide-play']]){
   await page.goto(base+route);await page.waitForFunction(()=>window.__ytReady);
   await page.locator(button).click();await page.waitForFunction(()=>window.__loads?.length===1);
   assert.equal(await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event'&&x[1]==='playback_start').length),1);
  }
  console.log('Playback start, queue continuity, active/cued removal and cross-tab persistence passed');
 }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=1;});
