const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const source = fs.readFileSync('src/app/renewal.js', 'utf8').split(' function readingCard(')[0];

function setup({reduced = false, bodyReduced = false, custom = false} = {}) {
  const nodes = new Map(), timers = new Map(), delays = [], plays = [], saves = [];
  const songs = ['a', 'b', 'c'].map(id => ({id, title: id, artist: 'artist', year: 1993, region: 'NY', art: {image: id + '.webp', alt: id}}));
  const document = {activeElement: null, body: {classList: {contains: () => bodyReduced}}};
  let serial = 0;
  function node(id) {
    let html = '';
    const n = {id, disabled: false, isConnected: true, dataset: {}, offsetWidth: 100, attrs: {},
      classList: {add() {}, remove() {}}, setAttribute(k, v) { this.attrs[k] = v; },
      focus() { document.activeElement = this; }};
    Object.defineProperty(n, 'innerHTML', {
      get: () => html,
      set(value) {
        html = value;
        if (id !== 'shuffle-result') return;
        for (const [selector, old] of nodes) if (!['#shuffle-result', '#shuffle-draw'].includes(selector)) {
          old.isConnected = false;
          nodes.delete(selector);
        }
        for (const match of value.matchAll(/\bid="([^"]+)"/g)) nodes.set('#' + match[1], node(match[1]));
      }
    });
    return n;
  }
  nodes.set('#shuffle-result', node('shuffle-result'));
  nodes.set('#shuffle-draw', node('shuffle-draw'));
  const myCrate = {ids: custom ? songs.map(s => s.id) : [], has(id) { return this.ids.includes(id); }, sync() { saves.push('sync'); },
    add(id) { saves.push('add:' + id); if (!this.has(id)) this.ids.push(id); return true; },
    remove(id) { saves.push('remove:' + id); this.ids = this.ids.filter(x => x !== id); return {saved: true}; }};
  const c = {$: selector => nodes.get(selector) || null, filtered: songs.slice(), customMode: custom, excluded: new Set(), document,
    Math: Object.assign(Object.create(Math), {random: () => .5}),
    setTimeout(fn, delay) { delays.push(delay); timers.set(++serial, fn); return serial; }, clearTimeout: id => timers.delete(id),
    matchMedia: () => ({matches: reduced}), esc: x => x, origin: 'https://example.com', yearLabel: s => s.year,
    hasPlayableSource: () => true, myCrate, linkRoutes() {},
    playSelection(rows, selected) { plays.push({ids: Array.from(rows, s => s.id), selected}); },
    refreshSelection() { if (c.customMode) c.filtered = myCrate.ids.map(id => songs.find(s => s.id === id)); c.checkRenewalDrawScope(); },
    savedSelection() {}};
  vm.createContext(c);
  vm.runInContext(source, c);
  return {c, songs, nodes, timers, delays, plays, saves, $: c.$,
    tick() { const callbacks = [...timers.values()]; timers.clear(); callbacks.forEach(f => f()); },
    finish() { for (let i = 0; i < 6; i++) this.tick(); }};
}
function cleared(t) {
  assert.equal(t.$('#shuffle-result').innerHTML, '');
  assert.equal(t.$('#shuffle-draw').disabled, false);
  assert.equal(t.$('#shuffle-draw').attrs['aria-busy'], 'false');
  assert.equal(t.timers.size, 0);
  assert.equal(t.$('#shuffle-play'), null);
  assert.equal(t.$('#shuffle-save'), null);
  assert.deepEqual(t.plays, []);
  assert.deepEqual(t.saves, []);
}

// Finite original animation and double-click guard, without the obsolete stale-pool expectation.
{
  const t = setup(); t.c.renewalDraw(); t.c.renewalDraw();
  assert(t.$('#shuffle-draw').disabled); assert.equal(t.timers.size, 1);
  t.finish();
  assert(t.$('#shuffle-result').innerHTML.includes('<h3>b</h3>'));
  assert.equal(t.$('#shuffle-draw').disabled, false); assert.deepEqual(t.plays, []);
  assert.deepEqual(t.delays, [300, 360, 450, 570, 720, 900]);
  assert.equal(t.delays.reduce((a, b) => a + b, 0), 3300);
  t.$('#shuffle-play').onclick();
  assert.deepEqual(t.plays, [{ids: ['b', 'c', 'a'], selected: false}]);
}
{
  const t = setup(); t.c.renewalDraw(); t.tick(); const late = [...t.timers.values()][0];
  t.$('#shuffle-cancel').onclick(); late(); t.finish();
  assert(t.$('#shuffle-result').innerHTML.includes('キャンセル'));
  assert.equal(t.c.document.activeElement.id, 'shuffle-draw');
  assert.equal(t.timers.size, 0); assert.deepEqual(t.plays, []);
}
{
  const t = setup(); t.c.renewalDraw(); t.$('#shuffle-result').isConnected = false; t.tick();
  assert.equal(t.timers.size, 0); assert.deepEqual(t.plays, []); assert.equal(t.$('#shuffle-play'), null);
}
for (const preference of [{reduced: true}, {bodyReduced: true}]) {
  const t = setup(preference); t.c.renewalDraw();
  assert.equal(t.timers.size, 0); assert(t.$('#shuffle-play')); assert.deepEqual(t.plays, []);
}
{
  const t = setup(); t.c.renewalDraw(); t.finish();
  t.$('#shuffle-again').focus(); t.$('#shuffle-again').onclick();
  assert.equal(t.c.document.activeElement.id, 'shuffle-cancel'); t.finish();
  assert(t.$('#shuffle-result').innerHTML.includes('<h3>c</h3>'));
  assert.equal(t.c.document.activeElement.id, 'shuffle-again'); assert.deepEqual(t.plays, []);
}

// A callback which was already queued must also check the live pool without relying on repaint.
{
  const t = setup(); t.c.renewalDraw(); t.c.filtered = []; t.tick(); cleared(t);
}

// Running and completed scopes depend on ordered effective IDs and library/Crate mode.
const changes = [
  ['filtered membership', t => { t.c.filtered = t.songs.slice(0, 1); }],
  ['filtered ordering', t => { t.c.filtered = t.songs.slice().reverse(); }],
  ['empty results', t => { t.c.filtered = []; }],
  ['scope mode', t => { t.c.customMode = true; }],
  ['library exclusion', t => { t.c.excluded.add('b'); }],
  ['Crate ordering', t => { t.c.filtered = [t.songs[2], t.songs[0], t.songs[1]]; }, true]
];
for (const phase of ['running', 'complete']) for (const [name, change, custom] of changes) {
  const t = setup({reduced: phase === 'complete', custom}); t.c.renewalDraw();
  const late = [...t.timers.values()][0]; change(t); t.c.checkRenewalDrawScope();
  if (late) late();
  assert.doesNotThrow(() => cleared(t), phase + ': ' + name);
}
// Semantic filter changes can invalidate even when they happen to produce the same IDs.
{
  const t = setup(); t.c.renewalDraw(); const late = [...t.timers.values()][0];
  t.c.invalidateRenewalDraw(); late(); cleared(t);
}
// Paint-only changes, identical IDs in replacement objects, and library exclusions while in Crate preserve a draw.
for (const phase of ['running', 'complete']) for (const custom of [false, true]) {
  const t = setup({reduced: phase === 'complete', custom}); t.c.renewalDraw();
  const html = t.$('#shuffle-result').innerHTML, timer = [...t.timers.keys()];
  t.c.filtered = t.c.filtered.map(s => ({...s})); if (custom) t.c.excluded.add('b');
  t.c.checkRenewalDrawScope(); t.c.checkRenewalDrawScope();
  assert.equal(t.$('#shuffle-result').innerHTML, html); assert.deepEqual([...t.timers.keys()], timer);
  if (phase === 'running') t.finish(); assert(t.$('#shuffle-play'));
}

// Exercise the real storage listener/refresh path without a browser or an injected mutation API.
const playlistLines = fs.readFileSync('src/app/playlist-ui.js', 'utf8').split('\n');
const refreshSource = playlistLines.find(line => line.trimStart().startsWith('function refreshSelection('));
const storageSource = playlistLines.find(line => line.trimStart().startsWith("addEventListener('storage'"));
const undoSource = fs.readFileSync('src/app/catalog-ui.js', 'utf8').match(/if\(undo\)undo\.onclick=\(\)=>\{([^]*?)\};/)[1];
for (const phase of ['running', 'complete']) {
  const t = setup({reduced: phase === 'complete', custom: true}); let storageListener;
  Object.assign(t.c, {songs: t.songs, art: {hidden: false}, norm: value => String(value).toLowerCase(),
    workUnit: () => '曲', refreshArtCrate() {}, paintResults() { t.c.checkRenewalDrawScope(); },
    addEventListener(name, callback) { assert.equal(name, 'storage'); storageListener = callback; },
    syncSelectionQueue() { throw Error('Storage refresh while preserving playback must not synchronize the queue'); }});
  vm.runInContext(refreshSource + '\n' + storageSource, t.c);
  t.c.renewalDraw(); t.nodes.set('#results', {});
  const html = t.$('#shuffle-result').innerHTML;
  t.c.myCrate.sync = () => { t.c.myCrate.name = 'Renamed'; };
  storageListener({key: 'unrelated'}); storageListener({key: 'crate-my-playlist'});
  assert.equal(t.$('#shuffle-result').innerHTML, html, 'Same ordered IDs after storage/name refresh preserve draw');
  t.c.myCrate.sync = () => { t.c.myCrate.ids = ['c', 'a']; };
  storageListener({key: 'crate-my-playlist'}); cleared(t);

  const u = setup({reduced: phase === 'complete'}); u.c.excluded.add('b'); u.c.renewalDraw();
  Object.assign(u.c, {lastRemoved: 'b', saveExcluded() {}, syncLibraryQueue() {}, paintResults() { u.c.checkRenewalDrawScope(); }});
  vm.runInContext('(function(){' + undoSource + '})()', u.c);
  assert.equal(u.c.excluded.has('b'), false); cleared(u);
}

// An already-queued callback from an old animation cannot invalidate a newer animation.
{
  const t = setup(); t.c.renewalDraw(); const late = [...t.timers.values()][0];
  t.c.invalidateRenewalDraw(); t.c.filtered = [t.songs[2]]; t.c.renewalDraw();
  const html = t.$('#shuffle-result').innerHTML; late();
  assert.equal(t.$('#shuffle-result').innerHTML, html); assert.equal(t.timers.size, 1);
  t.finish(); assert(t.$('#shuffle-result').innerHTML.includes('<h3>c</h3>')); assert.deepEqual(t.plays, []);
}

// Retained handlers cannot play/save old results, either before or after a new generation.
for (const afterNewDraw of [false, true]) {
  const t = setup({reduced: true}); t.c.renewalDraw();
  const oldPlay = t.$('#shuffle-play'), oldSave = t.$('#shuffle-save');
  t.c.invalidateRenewalDraw(); t.c.filtered = [t.songs[2]];
  if (afterNewDraw) t.c.renewalDraw();
  const html = t.$('#shuffle-result').innerHTML;
  oldPlay.onclick(); oldSave.onclick();
  assert.equal(t.$('#shuffle-result').innerHTML, html); assert.deepEqual(t.plays, []); assert.deepEqual(t.saves, []);
  if (afterNewDraw) { t.$('#shuffle-play').onclick(); assert.deepEqual(t.plays, [{ids: ['c'], selected: false}]); }
}
// Test each action's independent live-scope guard, not just invalidation by the first stale action.
for (const action of ['#shuffle-play', '#shuffle-save']) {
  const t = setup({reduced: true}); t.c.renewalDraw(); const stale = t.$(action);
  t.c.filtered = [t.songs[2]]; stale.onclick(); cleared(t);
}
// Fresh Crate PLAY uses its new order; fresh Crate save may remove its own result without a null-node crash.
{
  const t = setup({reduced: true, custom: true}); t.c.renewalDraw(); t.c.invalidateRenewalDraw();
  t.c.filtered = [t.songs[2], t.songs[0]]; t.c.myCrate.ids = ['c', 'a']; t.c.renewalDraw();
  t.$('#shuffle-play').onclick(); assert.deepEqual(t.plays, [{ids: ['a', 'c'], selected: true}]);
  assert.doesNotThrow(() => t.$('#shuffle-save').onclick());
  assert.deepEqual(t.c.myCrate.ids, ['c']); assert.equal(t.$('#shuffle-save'), null);
}
console.log('3300ms shuffle, cancel/repeat/focus/reduced motion, live scope invalidation, stale-handler rejection and fresh explicit PLAY passed.');
