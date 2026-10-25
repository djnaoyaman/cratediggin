const assert=require('node:assert/strict'),fs=require('node:fs'),crypto=require('node:crypto');
const id='jurassic-5-lesson-4-the-radio';
const rows=JSON.parse(fs.readFileSync('tracks.json','utf8')),t=rows.find(x=>x.id===id);
assert(t);assert.equal(t.artist,'Cut Chemist');assert.equal(t.primaryArtist,'Cut Chemist');
for(const key of ['artists','primaryArtists'])assert.deepEqual(t[key],['Cut Chemist']);
assert.equal(t.producer,'Cut Chemist');assert.equal(t.firstReleaseYear,null);
assert.equal(t.earliestDocumentedRelease.year,1995);assert.equal(t.earliestDocumentedRelease.isVerifiedFirstRelease,false);
assert.equal(t.year,2008);assert.equal(t.yearQualifier,'選択版');assert.equal(t.selectedRelease.artist,'Jurassic 5');
assert.equal(t.youtube.id,'uqq6Yg-2XC0');assert(t.yearDisplayNote.includes('初出年は未特定'));
for(const k of ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])assert.equal(t.youtube[k],false);
const ar=JSON.parse(fs.readFileSync('graffiti_artwork.json','utf8')).tracks.find(x=>x.id===id);
assert.equal(ar.artist,'Cut Chemist');
assert.equal(ar.paletteSource,t.art.paletteSource);assert.equal(ar.paletteSourceURL,t.art.paletteSourceUrl);
if(process.argv.includes('--source-only')){console.log('Lesson source attribution/selected edition/flags PASS');process.exit(0);}
const graph=html=>[...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)].flatMap(m=>{const x=JSON.parse(m[1]);return x['@graph']||[x]});
const html=fs.readFileSync('dist/tracks/'+id+'.html','utf8'),md=fs.readFileSync('dist/tracks/'+id+'.md','utf8');
assert(html.includes('Lesson 4: The Radio / Cut Chemist'));assert(md.includes('Cut Chemist'));assert(html.includes(t.yearDisplayNote));
const recordings=graph(html).filter(x=>x['@type']==='MusicRecording');assert(recordings.length>0);
for(const x of recordings){assert.equal(x.byArtist.name,'Cut Chemist');assert(!Object.hasOwn(x,'datePublished'),'Selected edition year must not masquerade as original year');}
assert(html.includes('/tracks/'+id+'.html'),'Legacy published URL stays canonical');assert(html.includes(ar.image));
const slug=n=>crypto.createHash('sha256').update(n).digest('hex').slice(0,16);
for(const [name,expected] of [['Cut Chemist',true],['Jurassic 5',false]]){
 const ahtml=fs.readFileSync('dist/artists/'+slug(name)+'.html','utf8');
 const lists=graph(ahtml).filter(x=>x['@type']==='CollectionPage').map(x=>x.mainEntity);assert(lists.length);
 assert.equal(lists.some(x=>x.itemListElement.some(y=>y.url.includes('/'+id+'.html'))),expected,name+' artist index');
}
console.log('Lesson original credit: source/static/Markdown/SEO/artist indexes and legacy URL PASS');
if(process.argv.includes('--static-only'))process.exit(0);
(async()=>{const {chromium}=require('playwright'),browser=await chromium.launch({headless:true});try{
 const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin',local=new URL(base).origin;
 for(const width of [390,1280]){
  const ctx=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});ctx.setDefaultTimeout(15000);
  await ctx.route('**/*',route=>{const u=new URL(route.request().url());if(u.origin===local)return route.continue();
   if(u.origin==='https://djnaoyaman.github.io'&&u.pathname==='/cratediggin/'+ar.image)return route.fulfill({status:200,contentType:'image/webp',body:fs.readFileSync('dist/'+ar.image)});
   return route.abort();});
  const page=await ctx.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/tracks/'+id+'.html');await page.locator('#article-play').waitFor();
  assert.equal(await page.locator('#view h1.song-heading').innerText(),t.title);
  assert((await page.locator('#view .song-artist').innerText()).includes('Cut Chemist'));assert(!(await page.locator('#view .song-artist').innerText()).includes('Jurassic'));
  assert((await page.title()).includes('Cut Chemist'));assert((await page.locator('#view').innerText()).includes(t.yearDisplayNote));
  assert(await page.locator('#view a[href="'+t.youtube.url+'"]').count()>0);assert.equal(await page.locator('#article-play').isDisabled(),false);
  const img=page.locator('#view .track-artwork img');await img.scrollIntoViewIfNeeded();await page.waitForFunction(()=>{const i=document.querySelector('#view .track-artwork img');return i&&i.complete&&i.naturalWidth>0});
  assert((await img.getAttribute('src')).includes(ar.image));assert((await img.getAttribute('alt')).includes('Cut Chemist'));
  for(const [name,expected] of [['Cut Chemist',true],['Jurassic 5',false]]){
   await page.goto(base+'/artists/'+slug(name)+'.html');await page.locator('#view .artist-directory .record-list').waitFor();assert.equal(await page.locator('#view .artist-directory h1').innerText(),name);
   const count=await page.locator('#view .artist-directory .record-list a[href*="'+id+'"]').count();assert.equal(count>0,expected,name+' SPA index');
  }
  assert.deepEqual(errors,[]);await ctx.close();
 }
 console.log('Lesson original credit mobile/desktop article, artist indexes and corrected art PASS; audio not attempted');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
