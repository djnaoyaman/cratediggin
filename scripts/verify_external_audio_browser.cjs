const {chromium}=require('playwright'),assert=require('node:assert/strict');
const base=process.env.PROFILE_TEST_URL||'http://127.0.0.1:8765/cratediggin';
(async()=>{const browser=await chromium.launch({headless:true});try{
const fixtures=[{id:'erick-sermon-boy-meets-world',title:'Boy Meets World',video:'rIjt0S6hwsY',url:'https://ericksermon.bandcamp.com/album/double-or-nothing',edition:'1995'},{id:'company-flow-vital-nerve',title:'Vital Nerve',video:'105emhbLmg4',url:'https://daily.redbullmusicacademy.com/2012/10/el-p-interview/',edition:'1996'},{id:'artifacts-art-of-facts',title:'Art of Facts',video:'1P90NkYgruI',url:'https://www.subwayhiphop.com/all-sold-out/artifacts-art-of-factsmore-facts',edition:'1996'},{id:'royal-flush-world-wide',title:'World Wide',video:'Rs0ZRP4wrY0',url:'https://music.amazon.com.au/albums/B002U95V26',edition:'1996'},{id:'mos-def-universal-magnetic',title:'Universal Magnetic',video:'TsoCr5KoNoM',url:'https://open.spotify.com/track/4UMsiE4vgpItrO3oMk19t7',edition:'2005'},{id:'siah-yeshua-dapoed-the-visualz',title:'The Visualz',video:'iMAeEkIoBK0',url:'https://open.spotify.com/track/18YIjhu5pIwRrG14lRgIhC',edition:'2008'}];
for(const fixture of fixtures)for(const width of [390,1280]){
 const context=await browser.newContext({viewport:{width,height:1000},reducedMotion:'reduce'});
 await context.route('**/*',async route=>{const url=new URL(route.request().url()),local=new URL(base);if(url.origin===local.origin)return route.continue();if(url.origin==='https://djnaoyaman.github.io'&&url.pathname.startsWith('/cratediggin/assets/')){const response=await route.fetch({url:local.origin+url.pathname+url.search});return route.fulfill({response});}return route.abort();});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base+'/tracks/'+fixture.id+'.html');await page.locator('#article-art').waitFor();
 const artwork=page.locator('.track-artwork img');await artwork.scrollIntoViewIfNeeded();await artwork.evaluate(img=>img.decode());assert(await artwork.evaluate(img=>img.complete&&img.naturalWidth>0),'New artwork must actually decode from local build output');
 await page.locator('#toggle').dispatchEvent('click');
 assert((await page.locator('#now-title').innerText()).includes(fixture.title),'Global play must not select a different song');
 if(fixture.video){assert(!(await page.locator('#status').innerText()).includes('未確定'));assert.equal(await page.evaluate(id=>window.TRACKS.find(t=>t.id===id).youtube.id,fixture.id),fixture.video);}else assert((await page.locator('#status').innerText()).includes('未確定'));
 await page.locator('#article-art').click();
 await page.locator('#art-toggle').click();
 assert((await page.locator('#now-title').innerText()).includes(fixture.title),'ART play must not select a different song');
 if(fixture.video){assert(!(await page.locator('#status').innerText()).includes('未確定'));assert.equal(await page.evaluate(id=>window.TRACKS.find(t=>t.id===id).youtube.id,fixture.id),fixture.video);}else assert((await page.locator('#status').innerText()).includes('未確定'));
 await page.locator('#art-close').click();
 if(fixture.video){assert.equal(await page.locator('#article-play').count(),1);assert.equal(await page.locator('#article-play').isDisabled(),false);assert(await page.locator('#view a[href="https://www.youtube.com/watch?v='+fixture.video+'"]').count()>0);}else assert.equal(await page.locator('#article-play').count(),0,'No fake internal playback button');
 const link=page.locator('#view a[href="'+fixture.url+'"]');
 assert(await link.count()>0);assert((await page.locator('#view').innerText()).includes(fixture.edition));
 if(fixture.video){assert(!(await page.locator('#view').innerText()).includes('サイト内再生は確認中'));}else assert((await page.locator('#view').innerText()).includes('サイト内再生は確認中'));
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 await page.screenshot({path:'/tmp/external-audio-'+fixture.id+'-'+width+'.png',fullPage:true});
 if(fixture.id==='siah-yeshua-dapoed-the-visualz'){await page.goto(base+'/artists/26c15b787b770613.html');await page.locator('.record-card[href$="/tracks/'+fixture.id+'.html"]').waitFor();await page.locator('#toggle').dispatchEvent('click');assert((await page.locator('#now-title').innerText()).includes(fixture.title));assert(!(await page.locator('#status').innerText()).includes('未確定'));await page.locator('.record-card[href$="/tracks/'+fixture.id+'.html"]').click();await page.locator('#article-play').waitFor();assert.equal(await page.locator('#article-play').isDisabled(),false);}
 await page.goto(base+'/tracks/mos-def-ms-fat-booty.html');await page.locator('#article-play').waitFor();
 assert.equal(await page.locator('#article-play').isDisabled(),false,'Existing playable tracks unaffected');
 assert.deepEqual(errors,[]);await context.close();
}console.log('Both owner-selected sources and artist entry controls PASS; actual audio not attempted');
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
