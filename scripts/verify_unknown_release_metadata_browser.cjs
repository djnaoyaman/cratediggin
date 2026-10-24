const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
const rows=JSON.parse(fs.readFileSync('tracks.json','utf8')).filter(t=>t.id==='dwele-angel-user-selected');
assert.equal(rows.length,1,'Exact Dwele fixture required');assert.equal(rows[0].year,null);assert.equal(rows[0].yearStatus,'unconfirmed');assert.equal(rows[0].album,null);assert.equal(rows[0].producer,null);assert.equal(rows[0].youtube.officialStatus,'unknown');assert.equal(rows[0].youtube.official,null);
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const t of rows){
  const html=fs.readFileSync('dist/tracks/'+t.id+'.html','utf8'),md=fs.readFileSync('dist/songs/'+t.id+'.md','utf8');
  assert(html.includes(t.yearDisplayNote));assert(md.includes(t.yearDisplayNote)||md.includes(t.yearBasis));
  let recordingCount=0;
  for(const match of html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)){
   const data=JSON.parse(match[1]);for(const node of data['@graph']||[data])if(node['@type']==='MusicRecording'){recordingCount++;
    assert(!Object.hasOwn(node,'inAlbum'),'Unknown album must not be asserted in JSON-LD');assert(!Object.hasOwn(node,'datePublished'),'Unknown original year must not be asserted');
   }
  }
  assert(recordingCount>0,'MusicRecording JSON-LD must be present');
  for(const width of [390,1280]){
   const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
   await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(base+'/tracks/'+t.id+'.html');await page.locator('#article-play').waitFor();
   const meta=await page.locator('#view dl.meta').evaluate(dl=>Object.fromEntries([...dl.querySelectorAll('dt')].map(x=>[x.textContent,x.nextElementSibling.textContent])));
   assert.equal(meta['アルバム'],'未確認');assert.equal(meta['制作'],'未確認');assert(meta['発表年'].includes('発表年未確認'));
   const body=await page.locator('#view').innerText();assert(body.includes(t.yearDisplayNote));assert(!body.includes('利用者の環境で再生確認済み'));
   assert(!body.includes('Official Audio'),'Unknown uploader not presented as official');
   assert(await page.locator('#view a[href="'+t.youtube.url+'"]').count()>0);for(const label of await page.locator('#view a[href="'+t.youtube.url+'"]').allTextContents())assert(!label.includes('公式'),'Unknown uploader link must be neutral');assert.equal(await page.locator('#article-play').isDisabled(),false);
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   await page.screenshot({path:'/tmp/unknown-release-'+width+'.png',fullPage:false});assert.deepEqual(errors,[]);await context.close();
  }
 }
 console.log('Explicit unknown-year single: static/Markdown/JSON-LD/SPA metadata and no false official/playback notice PASS; audio not attempted');
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1});
