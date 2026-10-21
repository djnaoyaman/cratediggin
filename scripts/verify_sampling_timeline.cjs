const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),F=JSON.parse(fs.readFileSync('scripts/fixtures/approved-sampling-timeline.json'));
for(const [p,c]of Object.entries(F.files)){assert.equal(hash(fs.readFileSync(p)),c.afterSHA256);assert.equal(hash(c.before),c.beforeSHA256)}
for(const[p,h]of Object.entries(F.protected))assert.equal(hash(fs.readFileSync(p)),h,p);
const tracks=JSON.parse(fs.readFileSync('tracks.json')),window={TRACKS:tracks};vm.runInNewContext(fs.readFileSync('src/assets/timeline.js','utf8'),{window});
const events=JSON.parse(JSON.stringify(window.CRATE_EVENTS));assert.equal(events.length,25);assert.deepEqual(events.filter(e=>!e.id),F.oldEvents);assert.deepEqual(events.filter(e=>e.id).sort((a,b)=>a.id.localeCompare(b.id)),F.newEvents.slice().sort((a,b)=>a.id.localeCompare(b.id)));
assert.equal(new Set(F.newEvents.map(e=>e.id)).size,14);assert.equal(tracks.length,507);
for(const e of events){assert(/^\d{4}(-\d{2}(-\d{2})?)?$/.test(e.date));assert.equal(Number(e.date.slice(0,4)),e.year);assert(e.url.startsWith('https://'));for(const s of e.sources||[])assert(s.url.startsWith('https://'));for(const id of e.relatedTrackIds||[])assert(tracks.some(t=>t.id===id));assert((e.relatedTrackIds||[]).length<=2)}
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const render=(songs,events)=>window.CrateChronology(songs,esc,{events});let html=render(tracks,events);assert.equal((html.match(/class="tc-event"/g)||[]).length,25);
for(const e of F.newEvents){assert(html.includes(esc(e.title)));assert(html.includes('datetime="'+e.date+'"'));for(const id of e.relatedTrackIds||[])assert(html.includes('href="#/song/'+id+'"'))}
const years=[...html.matchAll(/id="timeline-year-(\d+)"/g)].map(m=>+m[1]);assert.deepEqual(years,years.slice().sort((a,b)=>a-b));assert(html.includes('timeline-year-2026'));
assert(render([],[]).includes('この条件の曲はまだありません'));
const decade=events.filter(e=>e.year>=1990&&e.year<2000);assert.equal((render(tracks.filter(t=>t.year>=1990&&t.year<2000),decade).match(/class="tc-event"/g)||[]).length,decade.length);
const test={year:2000,date:'2000',category:'<tag>',title:'<script>bad</script>',text:'<b>bad</b>',source:'<source>',url:'https://example.com/?a="b',relatedTrackIds:['missing']};const safe=render([], [test]);assert(!safe.includes('<script>'));assert(safe.includes('&lt;script&gt;'));assert(!safe.includes('href="#/song/missing"'));
const app=fs.readFileSync('src/app/editorial.js','utf8');assert(app.includes("!restricted||selected.some(s=>s.year===e.year)"),'Existing filter semantics unchanged');
console.log('14 sourced Timeline events, old11 exact,507 works unchanged, date precision, citations, related links, ordering, escaping and empty/decade behavior PASS');
