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
  const page=await browser.newPage({viewport:{width:390,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.route('https://www.googletagmanager.com/**',r=>r.abort());
  await page.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:`
   window.__players=[];window.YT={Player:function(id,options){
    const p={options,loadVideoById(){queueMicrotask(()=>options.events?.onStateChange?.({data:1}));},cueVideoById(){},playVideo(){options.events?.onStateChange?.({data:1});},pauseVideo(){options.events?.onStateChange?.({data:2});},stopVideo(){},getDuration(){return 120;},getCurrentTime(){return 0;},seekTo(){},destroy(){}};
    window.__players.push(p);queueMicrotask(()=>{options.events?.onReady?.();window.__ytReady=true;});return p;
   }};window.onYouTubeIframeAPIReady();`}));
  await page.addInitScript(()=>{Object.defineProperty(navigator,'clipboard',{value:{writeText:async value=>{window.__copied=value;}}});});
  const check=async(route)=>{
   await page.waitForFunction(key=>document.documentElement.dataset.metadataRoute===key,route);
   const result=await page.evaluate(key=>{
    const p=window.CRATE_PAGES[key],ld=JSON.parse(document.querySelector('script[type="application/ld+json"]').textContent);
    return {expected:p,title:document.title,description:document.querySelector('meta[name="description"]').content,
     og:document.querySelector('meta[property="og:title"]').content,canonical:document.querySelector('link[rel="canonical"]').href,
     ogURL:document.querySelector('meta[property="og:url"]').content,ld,hash:location.hash,path:location.pathname};
   },route);
   assert.equal(result.title,result.expected.title);assert.equal(result.description,result.expected.description);
   assert.equal(result.og,result.expected.title);assert.equal(result.canonical,result.expected.url);assert.equal(result.ogURL,result.expected.url);
   assert.equal(result.path,result.expected.path);assert.equal(result.hash,'');
   assert(result.ld['@graph'].some(x=>x.url===result.expected.url||x.itemListElement?.some(y=>y.item===result.expected.url)));
  };
  await page.goto(base+'/songs/can-i-kick-it.html?utm_source=regression&utm_medium=test');
  await check('#/song/can-i-kick-it');
  await page.waitForFunction(()=>window.__ytReady);
  await page.evaluate(()=>window.__navigationMarker=42);
  await page.locator('#article-play').click();
  await page.waitForFunction(()=>window.dataLayer.some(x=>x[0]==='event'&&x[1]==='playback_start'));
  await page.evaluate(()=>window.__players[0].options.events.onStateChange({data:1}));
  assert.equal(await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event'&&x[1]==='playback_start').length),1,'Repeated playing state must not double count');
  await page.locator('#copy').click();
  assert.equal(await page.evaluate(()=>window.__copied),'https://djnaoyaman.github.io/cratediggin/songs/can-i-kick-it.html');
  assert(await page.evaluate(()=>window.dataLayer.some(x=>x[0]==='event'&&x[1]==='share'&&x[2].item_id==='can-i-kick-it')));
  const nextRoute=await page.locator('.article-nav a').last().evaluate(a=>Object.values(window.CRATE_PAGES).find(p=>p.path===new URL(a.href).pathname).route);
  await page.locator('.article-nav a').last().click();
  await check(nextRoute);
  assert.equal(await page.evaluate(()=>window.__navigationMarker),42,'Real URLs must retain the player session');
  await page.goBack();await check('#/song/can-i-kick-it');
  assert(page.url().includes('utm_source=regression'),'History must retain acquisition parameters');
  // A slower response for an earlier navigation must never overwrite the final page schema.
  const rapid=await page.evaluate(()=>Object.values(window.CRATE_PAGES).filter(p=>p.route.startsWith('#/song/')).slice(-2).map(p=>({route:p.route,path:p.path,metadataPath:p.metadataPath})));
  await page.route('**/metadata/**',async request=>{if(new URL(request.request().url()).pathname===rapid[0].metadataPath)await new Promise(resolve=>setTimeout(resolve,200));await request.continue();});
  await page.evaluate(items=>{for(const item of items){const a=document.createElement('a');a.href=item.path;document.body.append(a);a.click();a.remove();}},rapid);
  await check(rapid[1].route);await page.waitForTimeout(300);await check(rapid[1].route);
  // Legacy links remain accepted and become shareable physical URLs.
  await page.goto(base+'/#/feature/tribe-production');await check('#/feature/tribe');
  await page.getByRole('button',{name:'特集のリンクをコピー'}).click();
  assert.equal(await page.evaluate(()=>window.__copied),'https://djnaoyaman.github.io/cratediggin/features/tribe.html');
  await page.goto(base+'/songs/');await check('#/songs');
  assert.equal(await page.locator('a[href^="#/"]').count(),0,'Rendered links must be crawlable URLs');
  await page.locator('#results .row-menu').first().click();
  await page.locator('#results .crate-add').first().click();
  const events=await page.evaluate(()=>window.dataLayer.filter(x=>x[0]==='event').map(x=>({name:x[1],params:x[2]})));
  assert(events.some(x=>x.name==='add_to_playlist'&&x.params.song_id));
  assert(!events.some(x=>'playlist_name' in (x.params||{})||'search_term' in (x.params||{})));
  await page.goto(base+'/features/tribe.html');await check('#/feature/tribe');
  await page.reload();await check('#/feature/tribe');
  assert.deepEqual(errors,[]);
  const noJS=await browser.newPage({javaScriptEnabled:false});
  await noJS.goto(base+'/features/tribe.html');
  assert((await noJS.title()).includes('A Tribe Called Quest'));
  assert(await noJS.locator('main h1').count());
  assert((await noJS.locator('main a[href*="/songs/"]').count())>3);
  await noJS.close();await page.close();
  console.log('Direct/legacy URLs, metadata/schema navigation, history, no-JS HTML, player continuity, attribution and action events passed');
 }finally{await browser?.close();await new Promise(resolve=>server.close(resolve));}
})().catch(error=>{console.error(error);process.exitCode=1;});
