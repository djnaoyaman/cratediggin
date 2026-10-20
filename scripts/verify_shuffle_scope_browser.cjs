const {chromium} = require('playwright'), fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const base = 'http://127.0.0.1:8765/cratediggin';
const fixture = vm.runInNewContext(fs.readFileSync('scripts/verify_visible_art_browser.cjs', 'utf8').match(/const fixture=(`[^]*?`);/)[1]);
const app = fs.readFileSync('dist/app.js', 'utf8'), ending = '})();';
assert(app.trimEnd().endsWith(ending));
// Read-only observability in this HTTP response only. No test API is added to the shipped app.
const instrumented = app.trimEnd().slice(0, -ending.length) + `
window.__shuffleState=()=>({
  pool:filtered.filter(s=>customMode||!excluded.has(s.id)).map(s=>({id:s.id,playable:hasPlayableSource(s)})),
  mode:customMode,crate:myCrate.ids,winner:renewalLastDraw,generation:renewalDrawToken,
  playback:{queue:queue.slice(),scope:queueScope.slice(),custom:queueCustom,started,playing,
    current:songs[cur]?.id,sourceActive,sourceId,albumPlaybackLocked,inlinePlaybackLocked,wantsPlay:mainIntent.wantsPlay}
});
` + ending;
const deadline = setTimeout(() => { console.error('Shuffle scope browser exceeded 150s'); process.exit(1); }, 150000);
deadline.unref();

(async () => {
  const browser = await chromium.launch({headless: true});
  try {
    // Both catalog surfaces and both layout sizes without duplicating the whole cross-product.
    for (const [route, width] of [['/', 390], ['/tracks/', 1280]]) {
      const context = await browser.newContext({viewport: {width, height: 844}, reducedMotion: 'reduce'});
      context.setDefaultTimeout(8000); context.setDefaultNavigationTimeout(15000);
      await context.addInitScript(() => {
        if (window !== window.top) return;
        Object.defineProperty(window, 'CRATE_SITE_URL', {get: () => location.origin + '/cratediggin', set() {}});
        localStorage.setItem('crate-my-playlist', JSON.stringify({name: 'Shuffle regression', ids: ['mass-appeal', 'gang-starr-full-clip', 'beastie-boys-brass-monkey']}));
        localStorage.setItem('crate-prefs', JSON.stringify({auto: false, saver: false}));
      });
      await context.route('**/app.js*', r => r.fulfill({contentType: 'application/javascript', body: instrumented}));
      await context.route('https://www.youtube.com/iframe_api', r => r.fulfill({contentType: 'application/javascript', body: fixture}));
      await context.route('https://www.googletagmanager.com/**', r => r.abort());
      const page = await context.newPage(), errors = [];
      page.on('pageerror', e => errors.push(e.message));
      const state = () => page.evaluate(() => window.__shuffleState());
      const playback = () => page.evaluate(() => ({
        ...window.__shuffleState().playback,
        providers: window.__players.map(p => ({id: p.id, video: p.video, state: p.stateValue, t: p.t, index: p.index, commands: p.__shuffleCommands?.slice() || []}))
      }));
      async function preserved(before, label) {
        assert.deepEqual(await playback(), before, label + ': no queue/provider transport changes');
        assert(await page.locator('#yt').evaluate(e => e === window.__shuffleFrame && e.contentWindow === window.__shuffleWindow), label + ': same iframe and contentWindow');
        assert(await page.evaluate(() => window.__shufflePlayers.length === window.__players.length && window.__shufflePlayers.every((p, i) => p === window.__players[i])), label + ': same provider objects');
      }
      async function resetLibrary() {
        await page.locator('#library-tab').click();
        if (await page.locator('#clear-browse').isEnabled()) await page.locator('#clear-browse').click();
      }
      async function draw(phase) {
        await page.emulateMedia({reducedMotion: phase === 'running' ? 'no-preference' : 'reduce'});
        await page.locator('#shuffle-draw').click();
        await page.locator(phase === 'running' ? '#shuffle-cancel' : '#shuffle-play').waitFor();
        await page.evaluate(() => {
          window.__staleShuffle = {play: document.querySelector('#shuffle-play'), save: document.querySelector('#shuffle-save')};
        });
      }
      async function staleNoop(label) {
        const before = await playback(), storage = await page.evaluate(() => localStorage.getItem('crate-my-playlist'));
        const html = await page.locator('#shuffle-result').innerHTML();
        await page.evaluate(() => { window.__staleShuffle.play?.onclick(); window.__staleShuffle.save?.onclick(); });
        assert.equal(await page.locator('#shuffle-result').innerHTML(), html, label + ': stale controls cannot erase a new result');
        assert.equal(await page.evaluate(() => localStorage.getItem('crate-my-playlist')), storage, label + ': stale save cannot write storage');
        await preserved(before, label);
      }
      async function invalidated(before, phase, label) {
        assert.equal(await page.locator('#shuffle-result').innerHTML(), '', label + ': result cleared immediately');
        assert.equal(await page.locator('#shuffle-play, #shuffle-save, #shuffle-cancel').count(), 0);
        assert.equal(await page.locator('#shuffle-draw').isEnabled(), true);
        assert.equal(await page.locator('#shuffle-draw').getAttribute('aria-busy'), 'false');
        await preserved(before, label);
        if (phase === 'complete') {
          await staleNoop(label + ' before new draw');
          // Leave old node references intact, then attempt them again after a new generation exists.
          await page.emulateMedia({reducedMotion: 'reduce'});
          await page.locator('#shuffle-draw').click(); await page.locator('#shuffle-play').waitFor();
          await staleNoop(label + ' after new draw');
        }
      }
      function row(id) { return page.locator('#results .record-row').filter({has: page.locator('.record-card[href*="/' + id + '"]')}); }

      await page.goto(base + route); await page.waitForFunction(() => window.__ready && window.__shuffleState);
      // Establish actual active fixture playback before filtering. Its narrow library queue is independent of the Crate edits below.
      await page.locator('#search').fill('Mass Appeal'); await page.locator('#play-filter').click();
      await page.waitForFunction(() => window.__players.find(p => p.id === 'yt')?.stateValue === 1);
      await page.locator('a[data-nav="' + (route === '/' ? 'home' : 'songs') + '"]').click();
      await page.locator('#results').waitFor(); await resetLibrary();
      await page.evaluate(() => {
        window.__shuffleFrame = document.querySelector('#yt'); window.__shuffleWindow = window.__shuffleFrame.contentWindow;
        window.__shufflePlayers = window.__players.slice();
        // Retain the shared fixture but count cue/seek/destroy too, not only load/play/pause.
        for (const p of window.__players) {
          p.__shuffleCommands = []; p.t = 17;
          for (const key of ['loadVideoById', 'cueVideoById', 'loadPlaylist', 'cuePlaylist', 'playVideo', 'pauseVideo', 'stopVideo', 'seekTo', 'destroy']) {
            const original = p[key]; if (typeof original !== 'function') continue;
            p[key] = function (...args) { this.__shuffleCommands.push(key); return original.apply(this, args); };
          }
        }
      });
      assert.equal((await state()).playback.custom, false); assert.equal((await state()).playback.playing, true);

      for (const phase of ['running', 'complete']) for (const change of ['search', 'shelf', 'sort', 'same-ID search', 'Crate tab']) {
        await resetLibrary(); const before = await playback(), ids = (await state()).pool.map(s => s.id); await draw(phase);
        if (change === 'search') await page.locator('#search').fill('Gang Starr');
        if (change === 'shelf') await page.locator('[data-crate]:not([data-crate="all"]):not(:disabled)').first().click();
        if (change === 'sort') await page.locator('#sort').selectOption('title');
        if (change === 'same-ID search') {
          await page.locator('#search').fill(' ');
          assert.deepEqual((await state()).pool.map(s => s.id), ids, 'Whitespace query deliberately retains ordered IDs');
        }
        if (change === 'Crate tab') await page.locator('#my-crate-tab').click();
        await invalidated(before, phase, route + ' ' + phase + ' ' + change);
      }

      for (const phase of ['running', 'complete']) {
        await resetLibrary(); await page.locator('#my-crate-tab').click();
        let before = await playback(); await draw(phase);
        let ids = (await state()).crate, second = ids[1];
        await row(second).locator('.row-menu').click(); await row(second).locator('.crate-move').first().click();
        assert.deepEqual((await state()).crate.slice(0, 2), [second, ids[0]], 'Real Crate order changed');
        await invalidated(before, phase, phase + ' Crate ordered IDs');

        await page.locator('#my-crate-tab').click(); before = await playback(); await draw(phase);
        const removed = phase === 'complete' ? (await state()).winner : (await state()).crate[1];
        if (phase === 'complete') {
          // refreshSelection(true) repaints and removes the very save button whose handler is running.
          await page.locator('#shuffle-save').click();
        } else {
          await row(removed).locator('.row-menu').click(); await row(removed).locator('.queue-remove').click();
        }
        assert(!(await state()).crate.includes(removed));
        await invalidated(before, phase, phase + ' Crate membership');
        if (phase === 'running') await page.locator('#undo-selected').click();
        else {
          // Restore via the ordinary library add control, not an injected mutation API.
          await resetLibrary();
          const title = await page.evaluate(id => window.TRACKS.find(s => s.id === id).title, removed);
          await page.locator('#search').fill(title); await row(removed).locator('.row-menu').click(); await row(removed).locator('.crate-add').click();
        }

        await resetLibrary(); before = await playback(); await draw(phase);
        const visible = await page.locator('#results .record-card').evaluateAll(nodes => nodes.map(n => new URL(n.href).pathname.split('/').pop().replace(/\.html$/, '')));
        const excluded = visible.find(id => !before.queue.includes(id)); assert(excluded, 'An off-queue library record is available');
        await row(excluded).locator('.row-menu').click(); await row(excluded).locator('.queue-remove').click();
        await invalidated(before, phase, phase + ' library exclusion outside active scope');
        await page.locator('#restore-queue').click();
      }

      for (const phase of ['running', 'complete']) {
        await resetLibrary(); const before = await playback(); await draw(phase);
        const generation = (await state()).generation, original = phase === 'complete' ? await page.locator('#shuffle-play').elementHandle() : null;
        await page.locator('#view-toggle').click(); assert.equal((await state()).generation, generation, 'Density retains draw generation');
        await page.locator('#results [data-page-next]').first().click(); assert.equal((await state()).generation, generation, 'Pagination retains draw generation');
        if (original) assert(await original.evaluate(e => e.isConnected), 'Completed result retains its original controls');
        await page.locator('#shuffle-play').waitFor({timeout: 6000}); await preserved(before, phase + ' density/pagination');
      }

      // Fresh explicit PLAY must replace the old queue with the current rotated pool, never a superseded snapshot.
      for (const custom of [false, true]) {
        await resetLibrary(); if (custom) await page.locator('#my-crate-tab').click();
        await page.locator('#search').fill('Gang Starr'); await draw('complete');
        const fresh = await state(), at = fresh.pool.findIndex(s => s.id === fresh.winner); assert(at >= 0);
        const rotated = [...fresh.pool.slice(at), ...fresh.pool.slice(0, at)];
        await page.locator('#shuffle-play').click();
        await page.waitForFunction(id => window.__shuffleState().playback.current === id && window.__shuffleState().playback.playing, fresh.winner);
        const after = (await state()).playback;
        assert.deepEqual(after.scope, rotated.map(s => s.id)); assert.deepEqual(after.queue, rotated.filter(s => s.playable).map(s => s.id));
        assert.equal(after.custom, custom);
        if (!custom) { await page.locator('a[data-nav="' + (route === '/' ? 'home' : 'songs') + '"]').click(); await page.locator('#results').waitFor(); }
      }
      assert.deepEqual(errors, []); await context.close();
    }
    console.log('Running/completed SHUFFLE invalidation, retained stale controls, Crate order/membership, exclusions, presentation-only retention and fresh explicit PLAY passed; provider mocked, no real audio claim.');
  } finally { await browser.close(); clearTimeout(deadline); }
})().catch(e => { console.error(e); process.exitCode = 1; });
