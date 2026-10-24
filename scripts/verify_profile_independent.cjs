const {chromium}=require('playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
const source=JSON.parse(fs.readFileSync('editor_profile.json','utf8'));
const expected=source.blocks.filter(b=>b.type!=='h1').map(b=>b.text.replace(/\[([^\]]+)\]\(https:\/\/[^)]+\)/g,'$1'));
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===new URL(base).origin?route.continue():route.abort());
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/editor.html');await page.locator('.editor-profile').waitFor();
  const paragraphs=await page.locator('.editor-profile .prose > h2,.editor-profile .prose > h3,.editor-profile .prose > p,.editor-profile .prose > ul > li').allTextContents();
  for(const text of expected)assert(paragraphs.some(p=>p===text),'Current author paragraph: '+text.slice(0,50));
  assert.equal(await page.getByRole('heading',{level:1,name:source.name,exact:true}).count(),1);
  assert.equal(await page.locator('.editor-profile a[data-creator-site]').count(),9);
  assert.equal(await page.locator('#creator-sites-network').count(),0);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  for(const image of await page.locator('.editor-profile img').all()){await image.scrollIntoViewIfNeeded();await image.evaluate(i=>i.decode());assert(await image.evaluate(i=>i.naturalWidth>0));}
  await page.locator('.editor-profile').screenshot({path:'/tmp/editor-profile-independent-'+width+'.png'});
  await page.goto(base+'/');let requests=0;page.on('request',r=>{if(r.url().includes('/editor-profile.json'))requests++;});
  await page.locator('a[data-nav="editor"]').first().click();await page.locator('.editor-profile').waitFor();
  assert(requests>0,'SPA profile must load its independent payload');
  assert((await page.locator('.editor-profile').innerText()).includes(source.realName));
  await page.locator('a[data-nav="songs"]').first().click();await page.waitForFunction(()=>!document.querySelector('#view .editor-profile'));
  assert.deepEqual(errors,[]);await context.close();
 }
 console.log('Independent SSR/SPA profile, current authored text, nine links, images, navigation and responsive layout PASS');
}finally{await browser.close();}})().catch(error=>{console.error(error);process.exitCode=1});
