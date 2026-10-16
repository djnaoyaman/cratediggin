const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');

(async () => {
 const root = path.resolve('dist');
 const server = http.createServer((req, res) => {
  const relative = decodeURIComponent(req.url.split('?')[0]).replace(/^\/cratediggin\/?/, '') || 'index.html';
  const file = path.resolve(root, relative);
  if (!file.startsWith(root + path.sep)) {res.writeHead(403).end(); return;}
  try {
   res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : file.endsWith('.css') ? 'text/css' : file.endsWith('.html') ? 'text/html' : 'application/octet-stream');
   res.end(fs.readFileSync(file));
  } catch {res.writeHead(404).end();}
 });
 await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
 const base = 'http://127.0.0.1:' + server.address().port + '/cratediggin';
 let browser;
 try {
  browser = await chromium.launch({headless:true, channel:process.env.BROWSER_CHANNEL || undefined});
  for (const width of [1280, 390, 320]) {
   const page = await browser.newPage({viewport:{width, height:900}}), errors = [];
   page.on('pageerror', e => errors.push(e.message));
   await page.route('https://www.youtube.com/**', r => r.abort());
   await page.goto(base + '/#/songs');
   await page.waitForSelector('.record-row');
   const ids = () => page.locator('#results .record-card').evaluateAll(xs => xs.map(x => x.getAttribute('href')));
   const selector = () => page.locator('.results-pagination select').first();
   const total = await page.evaluate(() => window.TRACKS.length);
   const first = await ids(); assert.equal(first.length, 12);
   await page.locator('[data-page-next]').first().click();
   const second = await ids(); assert.equal(second.length, 12); assert(!second.some(x => first.includes(x)));
   await page.locator('#results .record-card').nth(5).scrollIntoViewIfNeeded();
   await page.waitForTimeout(100);
   const scroll = await page.evaluate(() => window.scrollY);
   await page.locator('#results .record-card').nth(5).click();
   await page.waitForSelector('.song-heading');
   await page.goBack(); await page.waitForSelector('#results .record-card');
   await page.waitForTimeout(100);
   assert.deepEqual(await ids(), second, 'Back must restore page 2');
   assert(Math.abs(await page.evaluate(() => window.scrollY) - scroll) < 8, 'Back must restore scroll');
   await page.reload(); await page.waitForSelector('#results .record-card');
   assert.deepEqual(await ids(), second, 'Reload must restore page 2');
   await selector().selectOption(String(Math.ceil(total / 12)));
   assert.equal((await ids()).length, total % 12 || 12);
   await page.locator('#search').fill('zzzz-no-such-track'); assert.equal((await ids()).length, 0);
   await page.locator('#clear-browse').click(); assert.deepEqual(await ids(), first);
   await page.locator('#search').fill('jazz');
   await page.waitForURL('**q=jazz');
   const searchUrl = page.url(), searchResults = await ids();
   assert(searchResults.length);
   await page.locator('#results .record-card').first().click(); await page.waitForSelector('.song-heading');
   await page.getByRole('link', {name:'曲一覧', exact:true}).click();
   await page.waitForSelector('#search');
   assert.equal(page.url(), searchUrl); assert.equal(await page.locator('#search').inputValue(), 'jazz');
   assert.deepEqual(await ids(), searchResults, 'Song list link must retain search');
   await page.locator('#clear-browse').click();
   await page.evaluate(() => localStorage.setItem('crate-my-playlist', JSON.stringify({name:'TEST CRATE', ids:window.TRACKS.slice(0, 26).map(t => t.id)})));
   await page.reload(); await page.waitForSelector('#my-crate-tab');
   await page.locator('#my-crate-tab').click();
   await selector().selectOption('2');
   await page.locator('#results .row-menu').first().click();
   await page.locator('#results .crate-move').first().click();
   assert.equal(await selector().inputValue(), '2', 'Reorder must retain current page');
   await page.locator('#results .row-menu').first().click();
   await page.locator('#results .queue-remove').first().click();
   assert.equal(await selector().inputValue(), '2', 'Removal must retain current page');
   await page.locator('#undo-selected').click();
   assert.equal(await selector().inputValue(), '2', 'Undo must retain current page');
   await selector().selectOption('3');
   for(let i=0;i<2;i++){
    await page.locator('#results .row-menu').first().click();
    await page.locator('#results .queue-remove').first().click();
   }
   assert.equal(await selector().inputValue(), '2', 'Deleting final page must clamp to last remaining page');
   assert.equal((await ids()).length, 12);
   assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Overflow at ' + width);
   await page.locator('#results').scrollIntoViewIfNeeded();
   await page.screenshot({path:path.join(process.env.SCREENSHOT_DIR || os.tmpdir(), 'catalog-pagination-' + width + '.png')});
   assert.deepEqual(errors, []); await page.close();
   console.log(width + 'px: pagination, history, scroll, reload, search, MY CRATE reorder/removal/undo/clamp passed');
  }
  assert(fs.readFileSync('dist/features/tribe.html','utf8').includes('rel="canonical" href="https://djnaoyaman.github.io/cratediggin/features/tribe.html"'));
 } finally {await browser?.close(); await new Promise(resolve => server.close(resolve));}
})().catch(e => {console.error(e); process.exitCode = 1;});
