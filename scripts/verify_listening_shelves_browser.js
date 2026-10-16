const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH,headless:true,args:['--no-sandbox']});
 const base=process.env.TEST_URL||'http://127.0.0.1:8765/cratediggin';
 for(const width of [1280,390,320]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/#/songs');await page.waitForSelector('[data-crate="loop"]');
  assert.equal(await page.locator('[data-crate]').count(),7);
  assert.equal(await page.locator('.advanced-filters').getAttribute('open'),null);
  assert(await page.locator('.advanced-filters [data-coast="east"]').count());
  const total=await page.evaluate(()=>window.TRACKS.length);
  for(const id of ['loop','drums','bass','voice','scratch','arrangement']){
   await page.locator('[data-crate="'+id+'"]').click();
   assert.equal(await page.locator('[data-crate="'+id+'"]').getAttribute('aria-pressed'),'true');
   const expected=await page.evaluate(id=>window.TRACKS.filter(s=>s.listeningTags.includes(id)).length,id);
   assert.equal(await page.locator('#count').textContent(),expected+' / '+total+' RECORDS');
   assert((await page.locator('#crate-caption').textContent()).length>10);
   assert(page.url().includes('collection='+id));
  }
  await page.reload();await page.waitForSelector('[data-crate="arrangement"][aria-pressed="true"]');
  await page.locator('#search').fill('zzzz-no-such-track-zzzz');
  assert.equal(await page.locator('#count').textContent(),'0 / '+total+' RECORDS');
  assert(await page.locator('[data-crate="scratch"]').isDisabled());
  assert(await page.locator('#play-filter').isDisabled());
  await page.locator('#clear-browse').click();
  assert.equal(await page.locator('#count').textContent(),total+' / '+total+' RECORDS');
  await page.locator('.advanced-filters summary').click();
  await page.locator('[data-coast="east"]').click();
  assert((await page.locator('#crate-caption').textContent()).includes('East Coast'));
  await page.reload();await page.waitForSelector('[data-coast="east"][aria-pressed="true"]');
  assert.notEqual(await page.locator('.advanced-filters').getAttribute('open'),null);
  await page.locator('#reset').click();
  assert.equal(await page.locator('#count').textContent(),total+' / '+total+' RECORDS');
  await page.locator('#my-crate-tab').click();assert(!(await page.locator('.crate-choices').isVisible()));
  await page.locator('#library-tab').click();assert(await page.locator('.crate-choices').isVisible());
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow at '+width);
  for(const b of await page.locator('[data-crate]').all()){const box=await b.boundingBox();assert(box.height>=44,'Touch target too small')}
  await page.screenshot({path:'/tmp/listening-shelf-'+width+'.png',fullPage:false});
  await page.goto(base+'/#/song/can-i-kick-it');await page.waitForSelector('.listening-links a');
  await page.locator('.listening-links a').first().click();await page.waitForSelector('[data-crate][aria-pressed="true"]');
  assert(page.url().includes('collection='));
  assert.deepEqual(errors,[]);console.log(width+'px: shelves, counts, deep link, search, reset, region, MY CRATE, layout passed');await page.close();
 }
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
