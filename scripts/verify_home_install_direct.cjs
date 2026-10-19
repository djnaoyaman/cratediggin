/*
 * Pure Node regression checks for the production HOME / BOOKMARK helper code.
 * This deliberately uses a small mocked DOM and mocked install events. It does
 * not prove real-browser installation, focus/layout behavior, or playback.
 * Keep the Playwright menu, focus, viewport, storage and player-identity gates.
 *
 * Usage from a checkout: node scripts/verify_home_install_direct.cjs
 * Review-draft usage: node /path/to/this/file.cjs /path/to/checkout
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(process.argv[2] || process.cwd());
const renewal = fs.readFileSync(path.join(root, 'src/app/renewal.js'), 'utf8');
const template = fs.readFileSync(path.join(root, 'templates/index.html'), 'utf8');
const marker = ' // Installation stays a user-owned browser action;';
assert.equal(renewal.split(marker).length, 2, 'Production helper extraction has one stable boundary');
const source = renewal.slice(renewal.indexOf(marker));
assert.match(template, /<span data-home-install-label>HOME GUIDE<\/span>/);
assert.match(template, /aria-label="HOME GUIDE：ホーム画面への追加方法"/);
assert.match(template, /aria-label="BOOKMARK GUIDE：ブラウザのお気に入りへの登録方法"/);
assert.match(template, /☆<\/span> BOOKMARK GUIDE/);
assert.match(template, /このボタンだけで自動登録はされません/);
assert.match(template, /オフライン再生を提供するものではありません/);
for (const prohibited of ['navigator.share', 'window.external', 'serviceWorker.register', 'localStorage', 'sessionStorage']) {
  assert(!source.includes(prohibited), `Helpers do not invoke ${prohibited}`);
}

const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
const settle = () => new Promise(resolve => setImmediate(resolve));

function harness({ standalone = false, displayStandalone = false, dialogSupport = true } = {}) {
  const elements = new Map(), handlers = new Map(), forbidden = [], focusLog = [];
  let activeElement = null, modalShows = 0;
  const location = { href: 'https://example.test/cratediggin/about.html' };
  const fail = action => () => { forbidden.push(action); throw new Error(`Unexpected helper action: ${action}`); };
  class Element {
    constructor(id, { hidden = false, dialog = false } = {}) {
      this.id = id; this.hidden = hidden; this.disabled = false; this.isConnected = true;
      this.open = false; this.textContent = ''; this.title = ''; this.tabIndex = 0;
      this.attributes = {}; this.listeners = new Map(); this.children = []; this.parent = null;
      if (dialog && !dialogSupport) this.showModal = undefined;
      elements.set(id, this);
    }
    setAttribute(key, value) { this.attributes[key] = value; }
    querySelector(selector) { return selector === '[data-home-install-label]' ? elements.get('label') : null; }
    querySelectorAll() { return this.children; }
    addEventListener(type, callback) {
      if (!this.listeners.has(type)) this.listeners.set(type, []);
      this.listeners.get(type).push(callback);
    }
    emit(type, event = {}) { for (const callback of this.listeners.get(type) || []) callback(event); }
    showModal() { this.open = true; modalShows++; }
    close() { if (this.open) { this.open = false; this.emit('close'); } }
    contains(element) { return element === this || this.children.includes(element); }
    getClientRects() { return this.hidden || (this.parent?.id.endsWith('-dialog') && !this.parent.open) ? [] : [{}]; }
    focus() {
      if (this.hidden || this.disabled || !this.isConnected) return;
      activeElement = this; focusLog.push(this.id);
    }
  }
  for (const id of ['#home-install-open', '#home-install-native', '#bookmark-open', '.browser-save-tools']) new Element(id, { hidden: true });
  for (const id of ['#home-install-dialog', '#bookmark-dialog']) new Element(id, { dialog: true });
  for (const id of ['#home-install-state', '#home-install-close', '#bookmark-close', '.brand', 'label', '#new-navigation-focus']) new Element(id);
  const home = elements.get('#home-install-open'), native = elements.get('#home-install-native');
  const homeDialog = elements.get('#home-install-dialog'), bookmarkDialog = elements.get('#bookmark-dialog');
  homeDialog.children = [native, elements.get('#home-install-close')];
  bookmarkDialog.children = [elements.get('#bookmark-close')];
  for (const dialog of [homeDialog, bookmarkDialog]) for (const child of dialog.children) child.parent = dialog;
  elements.get('.browser-save-tools').children = [home, elements.get('#bookmark-open')];
  const context = {
    $: selector => elements.get(selector), location,
    document: { get activeElement() { return activeElement; } },
    matchMedia: query => ({ matches: query === '(display-mode: standalone)' && displayStandalone }),
    navigator: { standalone, share: fail('share'), serviceWorker: { register: fail('service worker') } },
    history: { pushState: fail('pushState'), replaceState: fail('replaceState'), back: fail('history.back') },
    localStorage: { getItem: fail('storage read'), setItem: fail('storage write'), removeItem: fail('storage remove') },
    sessionStorage: { getItem: fail('session read'), setItem: fail('session write') },
    addEventListener(type, callback) {
      if (!handlers.has(type)) handlers.set(type, []);
      handlers.get(type).push(callback);
    },
  };
  context.window = context;
  context.external = { AddFavorite: fail('AddFavorite'), addFavorite: fail('addFavorite') };
  vm.runInNewContext(source, context, { filename: 'production-browser-save-helpers.js' });
  const emit = (type, event = {}) => { for (const callback of handlers.get(type) || []) callback(event); };
  const click = id => { const element = elements.get(id); if (element.hidden || element.disabled) return; element.focus(); return element.onclick?.(); };
  const installEvent = (prompt, userChoice) => {
    const event = { prevented: false, preventDefault() { this.prevented = true; }, prompt, userChoice };
    emit('beforeinstallprompt', event);
    return event;
  };
  const key = (id, shiftKey = false) => {
    const event = { key: 'Tab', shiftKey, prevented: false, preventDefault() { this.prevented = true; } };
    elements.get(id).emit('keydown', event); return event;
  };
  return {
    elements, home, native, homeDialog, bookmarkDialog, emit, click, installEvent, key, location,
    forbidden, focusLog, get active() { return activeElement?.id; }, get modalShows() { return modalShows; },
    get label() { return elements.get('label').textContent; }, get state() { return elements.get('#home-install-state').textContent; },
  };
}

const passed = [];
async function test(name, body) { await body(); passed.push(name); }
(async () => {
  await test('manual guide: visible labels, repeated open/close, focus containment', () => {
    const h = harness();
    assert.equal(h.label, 'HOME GUIDE'); assert.match(h.home.attributes['aria-label'], /^HOME GUIDE：/);
    assert(!h.home.hidden); assert(h.native.hidden);
    for (let index = 0; index < 2; index++) {
      h.click('#home-install-open'); assert(h.homeDialog.open); assert.equal(h.active, '#home-install-close');
      assert(h.key('#home-install-dialog').prevented); assert.equal(h.active, '#home-install-close');
      assert(h.key('#home-install-dialog', true).prevented); assert.equal(h.active, '#home-install-close');
      h.click('#home-install-close'); assert(!h.homeDialog.open); assert.equal(h.active, '#home-install-open');
    }
    assert.deepEqual(h.forbidden, []);
  });
  await test('missing/invalid prompt capability does not turn HOME GUIDE into HOME', () => {
    const h = harness();
    for (const invalid of [undefined, null, true, 'prompt', {}]) h.installEvent(invalid, undefined);
    assert.equal(h.label, 'HOME GUIDE'); assert(h.native.hidden);
  });
  await test('first click invokes the saved prompt synchronously once, before any guide modal', async () => {
    const h = harness(), choice = deferred(); let prompts = 0;
    const event = h.installEvent(() => { prompts++; assert.equal(h.modalShows, 0); }, choice.promise);
    assert(event.prevented); assert.equal(h.label, 'HOME'); assert.match(h.home.attributes['aria-label'], /^HOME：/);
    h.click('#home-install-open');
    assert.equal(prompts, 1); assert.equal(h.modalShows, 0); assert(h.home.disabled); assert(h.native.hidden);
    h.home.onclick(); h.native.onclick(); assert.equal(prompts, 1, 'handler guards also block programmatic repeated activation');
    choice.resolve({ outcome: 'accepted' }); await settle();
    assert.match(h.state, /追加リクエストを送信/); assert.doesNotMatch(h.state, /追加完了|登録済|保存済/);
    assert.equal(h.label, 'HOME GUIDE'); assert(!h.home.disabled); assert(!h.home.hidden); assert(h.native.hidden);
    assert(h.homeDialog.open); h.click('#home-install-close'); h.click('#home-install-open'); assert.equal(prompts, 1);
    assert.deepEqual(h.forbidden, []);
  });
  await test('dismissal, thrown prompt, rejected prompt and rejected choice recover truthfully', async () => {
    for (const mode of ['dismissed', 'throw', 'rejectPrompt', 'rejectChoice']) {
      const h = harness(), choice = deferred(); let prompts = 0;
      const prompt = () => { prompts++; if (mode === 'throw') throw new Error('blocked'); return mode === 'rejectPrompt' ? Promise.reject(new Error('blocked')) : Promise.resolve(); };
      h.installEvent(prompt, choice.promise); h.click('#home-install-open'); await settle();
      if (mode === 'rejectChoice') choice.reject(new Error('choice unavailable')); else choice.resolve({ outcome: 'dismissed' });
      await settle();
      assert.equal(prompts, 1); assert(!h.home.disabled); assert(h.native.hidden); assert.equal(h.label, 'HOME GUIDE');
      assert.match(h.state, mode === 'dismissed' ? /キャンセル/ : /開けませんでした/); assert(h.homeDialog.open);
    }
  });
  await test('installation notification dominates earlier/later choices and errors', async () => {
    for (const order of ['beforePromptResolves', 'beforeChoice', 'afterChoice', 'beforeError']) {
      const h = harness(), prompt = deferred(), choice = deferred();
      h.installEvent(() => prompt.promise, choice.promise); h.click('#home-install-open');
      if (order === 'beforePromptResolves') h.emit('appinstalled');
      prompt.resolve(); await settle();
      if (order === 'beforeChoice' || order === 'beforeError') h.emit('appinstalled');
      if (order === 'beforeError') choice.reject(new Error('late failure')); else choice.resolve({ outcome: 'accepted' });
      await settle(); if (order === 'afterChoice') h.emit('appinstalled');
      assert.match(h.state, /ブラウザから追加完了が通知/); assert(h.home.hidden); assert(h.native.hidden); assert(!h.home.disabled);
      h.installEvent(() => { throw new Error('must not run after appinstalled'); }, Promise.resolve({ outcome: 'accepted' }));
      assert(h.home.hidden); assert(h.native.hidden);
      if (h.homeDialog.open) { h.click('#home-install-close'); assert.equal(h.active, '.brand'); }
      else assert.equal(h.modalShows, 0);
    }
  });
  await test('new saved event survives completion of an older in-flight prompt', async () => {
    const h = harness(), old = deferred(); let first = 0, second = 0;
    h.installEvent(() => { first++; }, old.promise); h.click('#home-install-open');
    h.installEvent(() => { second++; }, Promise.resolve({ outcome: 'dismissed' }));
    assert(h.home.disabled); h.home.onclick(); assert.equal(second, 0);
    old.resolve({ outcome: 'dismissed' }); await settle(); assert.equal(h.label, 'HOME'); assert(!h.native.hidden); assert(!h.native.disabled);
    h.click('#home-install-close'); h.click('#home-install-open'); await settle();
    assert.equal(first, 1); assert.equal(second, 1); assert.equal(h.label, 'HOME GUIDE');
  });
  await test('an event received while the guide is open exposes one usable native action', async () => {
    const h = harness(); let prompts = 0;
    h.click('#home-install-open'); h.installEvent(() => { prompts++; }, Promise.resolve({ outcome: 'dismissed' }));
    assert(!h.native.hidden); h.key('#home-install-dialog'); assert.equal(h.active, '#home-install-native');
    h.key('#home-install-dialog', true); assert.equal(h.active, '#home-install-close');
    await h.click('#home-install-native'); assert.equal(prompts, 1); assert(h.native.hidden); assert.match(h.state, /キャンセル/);
  });
  await test('a pending native action cannot reopen a subsequently closed guide', async () => {
    const h = harness(), choice = deferred();
    h.click('#home-install-open'); h.installEvent(() => {}, choice.promise); const request = h.click('#home-install-native');
    h.click('#home-install-close'); h.elements.get('#new-navigation-focus').focus();
    const focusCount = h.focusLog.length; choice.resolve({ outcome: 'dismissed' }); await request;
    assert(!h.homeDialog.open); assert.equal(h.active, '#new-navigation-focus'); assert.equal(h.focusLog.length, focusCount);
  });
  await test('hash, Back/Forward and URL-only navigation suppress late guide/focus', async () => {
    for (const navigation of ['hashchange', 'popstate', 'pushStateURLOnly', 'roundTripHash', 'roundTripPopstate']) {
      const h = harness(), choice = deferred(), initial = h.location.href;
      h.installEvent(() => {}, choice.promise); h.click('#home-install-open');
      h.location.href = initial + '#/songs';
      if (navigation === 'hashchange' || navigation === 'popstate') h.emit(navigation);
      if (navigation.startsWith('roundTrip')) { h.emit(navigation.endsWith('Hash') ? 'hashchange' : 'popstate'); h.location.href = initial; h.emit(navigation.endsWith('Hash') ? 'hashchange' : 'popstate'); }
      h.elements.get('#new-navigation-focus').focus(); const focusCount = h.focusLog.length;
      choice.resolve({ outcome: 'accepted' }); await settle();
      assert(!h.homeDialog.open, navigation); assert.equal(h.modalShows, 0, navigation); assert.equal(h.active, '#new-navigation-focus', navigation); assert.equal(h.focusLog.length, focusCount, navigation);
      assert(!h.home.disabled); assert.equal(h.label, 'HOME GUIDE');
    }
  });
  await test('BOOKMARK remains a manual guide with no save/share/storage/navigation API', () => {
    const h = harness(), before = h.location.href;
    for (let index = 0; index < 2; index++) {
      h.click('#bookmark-open'); assert(h.bookmarkDialog.open); assert.equal(h.active, '#bookmark-close');
      assert(h.key('#bookmark-dialog').prevented); assert.equal(h.active, '#bookmark-close');
      assert(h.key('#bookmark-dialog', true).prevented); assert.equal(h.active, '#bookmark-close');
      h.click('#bookmark-close'); assert(!h.bookmarkDialog.open); assert.equal(h.active, '#bookmark-open');
    }
    assert.equal(h.location.href, before); assert.deepEqual(h.forbidden, []);
  });
  await test('both standalone signals hide both helpers and their group', () => {
    for (const options of [{ standalone: true }, { displayStandalone: true }]) {
      const h = harness(options);
      for (const id of ['#home-install-open', '#bookmark-open', '.browser-save-tools']) assert(h.elements.get(id).hidden, id);
      h.installEvent(() => { throw new Error('standalone install attempt'); }, Promise.resolve({ outcome: 'accepted' }));
      assert(h.home.hidden); assert(h.native.hidden);
    }
  });
  await test('no dialog support leaves controls inert and hidden', () => {
    const h = harness({ dialogSupport: false });
    for (const id of ['#home-install-open', '#bookmark-open', '.browser-save-tools']) assert(h.elements.get(id).hidden, id);
    assert.equal(h.home.onclick, undefined); assert.equal(h.elements.get('#bookmark-open').onclick, undefined);
  });
  console.log(`PASS: ${passed.length} HOME/BOOKMARK helper state-machine cases (mocked DOM/events; not browser installation or layout evidence)`);
})().catch(error => { console.error(error); process.exitCode = 1; });
