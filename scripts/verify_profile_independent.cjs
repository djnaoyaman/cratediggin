const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
const source=JSON.parse(fs.readFileSync('editor_profile.json','utf8'));
const expected=source.blocks.filter(b=>b.type!=='h1').map(b=>b.text.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g,'$1'));
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [320,390,768,1280]){
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/editor.html');await page.locator('.editor-profile').waitFor();
  const paragraphs=await page.locator('.editor-profile .prose > h2,.editor-profile .prose > h3,.editor-profile .prose > p,.editor-profile .prose > ul > li').allTextContents();
  for(const text of expected)assert(paragraphs.some(p=>p===text),'Current author paragraph: '+text.slice(0,50));
  assert.equal(await page.getByRole('heading',{level:1,name:source.name,exact:true}).count(),1);
  assert.equal(await page.locator('.editor-profile a').count(),1);
  assert.equal(await page.getByRole('link',{name:'作者について',exact:true}).getAttribute('href'),source.authorUrl);
  assert.equal(await page.locator('.editor-photo-archive').getAttribute('open'),null);
  const compactText=await page.locator('.editor-profile').innerText();
  for(const removed of ['宮崎直哉','15歳','足立区','32年','約5万曲','学歴','講演'])assert(!compactText.includes(removed));
  assert.equal(await page.locator('.manifesto').count(),0);
  await page.locator('.editor-profile').screenshot({path:'/tmp/editor-profile-compact-'+width+'.png'});
  await page.locator('.editor-photo-archive > summary').click();
  assert.equal(await page.locator('.editor-photo img').count(),2);
  assert.equal(await page.locator('#creator-sites-network').count(),0);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  for(const image of await page.locator('.editor-profile img').all()){await image.scrollIntoViewIfNeeded();await image.evaluate(i=>i.decode());assert(await image.evaluate(i=>i.naturalWidth>0));}
  await page.locator('.editor-profile').screenshot({path:'/tmp/editor-profile-independent-'+width+'.png'});
  await page.goto(base+'/');let requests=0;page.on('request',r=>{if(r.url().includes('/editor-profile.json'))requests++;});
  const metadataPath=await page.evaluate(()=>window.CRATE_PAGES['#/editor'].metadataPath);
  let releaseOldMetadata;
  await page.route(url=>url.pathname===metadataPath,async route=>{await new Promise(resolve=>releaseOldMetadata=resolve);await route.fulfill({json:{jsonld:{'@context':'https://schema.org','@graph':[{'@type':'ProfilePage',mainEntity:{name:'STALE_PROFILE_PROBE'}}]}}});});
  await page.locator('a[data-nav="editor"]').first().click();await page.locator('.editor-profile').waitFor();
  assert(requests>0,'SPA profile must load its independent payload');
  assert((await page.locator('.editor-profile').innerText()).includes(source.description));
  assert.equal(await page.getByRole('link',{name:'作者について',exact:true}).getAttribute('href'),source.authorUrl);
  if(releaseOldMetadata){const response=page.waitForResponse(url=>new URL(url.url()).pathname===metadataPath);releaseOldMetadata();await (await response).finished();await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
  await page.waitForFunction(()=>document.documentElement.dataset.metadataRoute==='#/editor');
  const graph=await page.locator('script[type="application/ld+json"]').last().textContent();
  assert(!graph.includes('宮崎直哉'));assert(graph.includes(source.authorUrl));
  assert(!graph.includes('STALE_PROFILE_PROBE'),'An older shared metadata request must not replace the independent profile');
  await page.locator('a[data-nav="songs"]').first().click();await page.waitForFunction(()=>!document.querySelector('#view .editor-profile'));
  assert.deepEqual(errors,[]);await context.close();
 }
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:900}}),page=await context.newPage();
 await context.route('**/*',r=>new URL(r.request().url()).origin===new URL(base).origin?r.continue():r.abort());
 await page.goto(base+'/editor.html');assert((await page.locator('.editor-profile').innerText()).includes(source.description));
 assert.equal(await page.getByRole('link',{name:'作者について'}).getAttribute('href'),source.authorUrl);
 await page.locator('.editor-profile').screenshot({path:'/tmp/editor-profile-compact-no-js.png'});
 await page.locator('.editor-photo-archive > summary').click();for(const i of await page.locator('.editor-photo img').all()){await i.scrollIntoViewIfNeeded();assert(await i.isVisible());}
 await context.close();
 console.log('Compact SSR/SPA/no-JS profile, author hub, retained photos, four widths and navigation PASS');
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1});
