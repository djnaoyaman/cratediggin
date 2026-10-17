// Exercise the actual feature selection code without requiring a browser.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const songs = JSON.parse(fs.readFileSync(path.join(root, 'tracks.json'), 'utf8'));
const app = fs.readFileSync(path.join(root, 'dist/app.js'), 'utf8');
const start = app.indexOf(' const features=[');
const end = app.indexOf(' function featurePage', start);
assert(start >= 0 && end > start, 'Feature code not found');
const context = vm.createContext({songs});
vm.runInContext(app.slice(start, end) + '; globalThis.catalogFeatures = features; globalThis.selectFeature = featureTracks;', context);
const expected = {
  'dj-shadow': ['dj-shadow-organ-donor-extended-overhaul','dj-shadow-in-flux','dj-shadow-building-steam-with-a-grain-of-salt','dj-shadow-organ-donor','dj-shadow-midnight-in-a-perfect-world','dj-shadow-stem-long-stem','dj-shadow-what-does-your-soul-look-like','dj-shadow-high-noon','unkle-rabbit-in-your-headlights','unkle-lonely-soul','dj-shadow-six-days','dj-shadow-mashin-on-the-motorway','dj-shadow-scale-it-back','dj-shadow-the-mountain-will-fall','dj-shadow-nobody-speak','dj-shadow-rocket-fuel','dj-shadow-ozone-scraper','dj-shadow-the-number-song','dj-shadow-the-number-song-cut-chemist-remix'],
  'j-dilla': ['slum-village-fall-in-love','slum-village-players','slum-village-get-dis-money','j-dilla-fuck-the-police','jaylib-the-red','j-dilla-workinonit','j-dilla-time-the-donut-of-the-heart','j-dilla-last-donut-of-the-night','j-dilla-so-far-to-go','runnin','the-pharcyde-drop','de-la-soul-stakes-is-high','janet-jackson-got-til-its-gone-jay-dees-revenge-mix','a-tribe-called-quest-find-a-way','common-the-light','erykah-badu-didnt-cha-know'],
  'madlib': ['lootpack-whenimondamic','quasimoto-microphone-mathematics','quasimoto-low-class-conspiracy','madlib-slims-return','madvillain-americas-most-blunted','madvillain-accordion','madvillain-all-caps','madvillain-meat-grinder','freddie-gibbs-madlib-thuggin','freddie-gibbs-madlib-crime-pays','madlib-road-of-the-lonely-ones','mf-doom-one-beer','de-la-soul-shopping-bags','mos-def-auditorium','kanye-west-no-more-parties-in-la','jaylib-the-red']
};
for (const [id, required] of Object.entries(expected)) {
  const feature = context.catalogFeatures.find(f => f.id === id);
  assert(feature && feature.type === 'producer' && feature.allYears, id + ': missing all-years producer feature');
  const selected = context.selectFeature(feature);
  assert(selected.every((t, i) => i === 0 || selected[i - 1].year <= t.year), id + ': chronological order');
  for (const tid of required) {
    const track = selected.find(t => t.id === tid);
    assert(track && track.youtube.id, id + ': missing song/audio ' + tid);
    assert(fs.existsSync(path.join(root, 'dist/tracks', tid + '.html')), 'Missing generated page ' + tid);
  }
  console.log(id + ': ' + selected.length + ' tracks; requested songs and audio present');
}
const dilla = context.selectFeature(context.catalogFeatures.find(f => f.id === 'j-dilla'));
assert(!dilla.some(t => t.id === 'janet-jackson-got-til-its-gone'), 'Original Janet production must not be attributed to Dilla');
assert.deepEqual(songs.find(t => t.id === 'jaylib-the-red').producers, ['J Dilla']);
assert.equal(songs.find(t => t.id === 'mos-def-auditorium').youtube.official, false);
assert(songs.length >= 262 && songs.every(t => t.youtube.id), 'Catalog has missing audio');
console.log('Credits, reference-audio labeling and all catalog audio IDs verified');

assert.equal(songs.find(t => t.id === 'dj-shadow-organ-donor-extended-overhaul').youtube.id, 'C2MmSXrfK9s');
