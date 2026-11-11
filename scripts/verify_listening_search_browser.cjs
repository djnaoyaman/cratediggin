const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const totalRecords=JSON.parse(fs.readFileSync('tracks.json','utf8')).length;
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
const source=fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8'),fixture=vm.runInNewContext(source.match(/const fixture=(`[^]*?`);/)[1]);
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [320,390,1280]){
  const c=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
  await c.addInitScript(()=>localStorage.setItem('crate-prefs',JSON.stringify({auto:false,saver:false})));
  await c.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:fixture}));
  await c.route('https://www.googletagmanager.com/**',r=>r.abort());
  const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  await p.goto(base+'/tracks/epmd-scratch-bring-it-back-part-2.html');
  await p.waitForFunction(()=>window.__ready);
  assert.equal(await p.locator('.listening-search a').count(),2);
  for(const link of await p.locator('.listening-search a').all()){const box=await link.boundingBox();assert(box.height>=44&&box.width>=44);assert.equal(await link.evaluate(e=>e.getClientRects().length),1,'Keep each label together');}
  assert.equal(await p.locator('[data-crate],.crate-choices').count(),0);
  await p.locator('.listening-search').scrollIntoViewIfNeeded();
  await p.screenshot({path:require('node:path').join(require('node:os').tmpdir(),'listening-search-'+width+'.png')});
  assert(await p.evaluate(()=>window.__players.every(x=>!x.plays)),'Reading does not start playback');
  const transport=()=>p.evaluate(()=>window.__players.filter(x=>x.id==='yt').map(x=>({video:x.video,loads:x.loads,plays:x.plays,state:x.stateValue})));
  await p.locator('#article-play').click();await p.waitForFunction(()=>window.__players.find(x=>x.id==='yt')?.stateValue===1);
  const playing=await transport();
  await p.locator('.listening-search a').filter({hasText:'スクラッチの技'}).click();
  await p.locator('#search').waitFor();
  assert.equal(await p.locator('#search').inputValue(),'スクラッチの技');
  assert.equal(new URL(p.url()).pathname,'/cratediggin/tracks/');
  assert.equal(new URL(p.url()).searchParams.get('q'),'スクラッチの技');
  assert.equal(await p.locator('#count').innerText(),`4 / ${totalRecords} RECORDS`);
  assert.deepEqual(await transport(),playing,'Search navigation preserves active playback');
  await p.goBack();await p.locator('.listening-search a').first().waitFor();
  assert.deepEqual(await transport(),playing,'Back preserves active playback');
  await p.goForward();await p.locator('#search').waitFor();
  await p.locator('#search').fill('スクラッチの技 EPMD');
  assert.equal(await p.locator('#count').innerText(),`1 / ${totalRecords} RECORDS`);
  await p.reload();await p.locator('#search').waitFor();
  assert.equal(await p.locator('#search').inputValue(),'スクラッチの技 EPMD');
  assert.equal(await p.locator('#count').innerText(),`1 / ${totalRecords} RECORDS`);
  await p.locator('#search').fill('スクラッチの技 zzzz-no-such-track-zzzz');
  assert.equal(await p.locator('#count').innerText(),`0 / ${totalRecords} RECORDS`);
  assert(await p.locator('#play-filter').isDisabled());
  await p.locator('#clear-browse').click();assert.equal(await p.locator('#count').innerText(),`${totalRecords} / ${totalRecords} RECORDS`);
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  assert.deepEqual(errors,[]);await c.close();
  console.log(width+'px: listening search, real URL, Back/Forward, reload, empty/reset, mocked playback preservation PASS');
 }
 const c=await browser.newContext({javaScriptEnabled:false});const p=await c.newPage();
 await p.goto(base+'/tracks/epmd-scratch-bring-it-back-part-2.html');
 assert.equal(await p.locator('.listening-search a').count(),2);await c.close();
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
