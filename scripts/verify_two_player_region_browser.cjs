const {chromium}=require('playwright'),fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('scripts/verify_visible_art_browser.cjs','utf8'),fixture=vm.runInNewContext(source.match(/const fixture=(`[^]*?`);/)[1]);
const deadline=setTimeout(()=>{console.error('Two source browser exceeded60s');process.exit(1)},60000);deadline.unref();
(async()=>{const b=await chromium.launch({headless:true});try{
for(const [route,id,vid,official,old] of [['tracks/grandmaster-flash-the-furious-five-the-message.html','grandmaster-flash-the-furious-five-the-message','4kjeWGQ175g',false,'JfnFkJDuDM0'],['artists/079ffefb92a8ef55.html','sugarhill-gang-rappers-delight','TBMuGCw8hJY',true,'ZjRi-S7J70Y']]){
 const c=await b.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});c.setDefaultTimeout(8000);await c.route('https://www.youtube.com/iframe_api',r=>r.fulfill({contentType:'application/javascript',body:fixture}));await c.route('https://www.googletagmanager.com/**',r=>r.abort());const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto('http://127.0.0.1:8765/cratediggin/'+route);await p.waitForFunction(()=>window.__ready);const t=await p.evaluate(id=>window.TRACKS.find(x=>x.id===id),id);assert.equal(t.youtube.id,vid);assert.equal(t.youtube.official,official);
 if(route.startsWith('artists')){await p.locator('a[href*="sugarhill-gang-rappers-delight"]').first().click();}
 assert((await p.locator('main').innerText()).includes('日本国内での実再生・音声の同一性は未確認'));await p.locator('#article-play').click();await p.waitForFunction(vid=>window.__players.find(x=>x.id==='yt')?.video===vid,vid);assert(!(await p.evaluate(old=>window.__players.some(x=>x.video===old),old)));assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.deepEqual(errors,[]);await c.close();
}
}finally{await b.close();clearTimeout(deadline)}})().catch(e=>{console.error(e);process.exitCode=1});
