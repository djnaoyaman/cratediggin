// Behavioral checks for the generated catalog, real filters and curated routes.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const window={};vm.runInNewContext(fs.readFileSync('dist/tracks.js','utf8'),{window});
vm.runInNewContext(fs.readFileSync('dist/filters.js','utf8'),{window});
vm.runInNewContext(fs.readFileSync('dist/timeline.js','utf8'),{window});
const songs=window.TRACKS,app=fs.readFileSync('dist/app.js','utf8');
const sourceCatalog=JSON.parse(fs.readFileSync('tracks.json','utf8'));
assert.deepEqual(Array.from(songs,t=>t.id).sort(),sourceCatalog.map(t=>t.id).sort());
for(const t of songs){assert(t.review);assert.equal(t.review.sampleEntries,t.samples.length);assert.equal(t.review.deepDiveSections,t.deepdives.length)}
const shadow=songs.find(t=>t.artist==='DJ Shadow'&&t.title==='Organ Donor');
assert(shadow.samples.some(s=>s.research));
for(const sample of shadow.samples)assert(window.CrateFilter(songs,{q:sample.title}).some(t=>t.id===shadow.id));
assert(window.CrateFilter(songs,{research:'深掘り記事あり'}).every(t=>t.deepdives.length));
assert(window.CrateFilter(songs,{research:'サンプル資料あり'}).every(t=>t.samples.length));
const elements=new Map(),$=selector=>{if(['#back-to-top','#enter-crate'].includes(selector))return null;if(!elements.has(selector))elements.set(selector,{});return elements.get(selector)};
const buttons=['all','own','related'].map(scope=>({dataset:{featureScope:scope},setAttribute(){}}));
const view={innerHTML:'',querySelectorAll:selector=>selector==='[data-feature-scope]'?buttons:[]};
const esc=s=>String(s??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const context=vm.createContext({songs,window,view,$,esc,top:()=>'',paintResults:()=>{},scopePersonQueue:()=>{},playableIds:xs=>xs.map(t=>t.id),origin:'https://djnaoyaman.github.io/cratediggin',document:{title:''}});
vm.runInContext(app.slice(app.indexOf(' function yearLabel('),app.indexOf(' const songs='))+'let customMode,applyListFilters,filtered,queue,resultLimit;const RESULT_CHUNK_SIZE=36,browseRestoring=null;const restoredResultLimit=()=>RESULT_CHUNK_SIZE;'+app.slice(app.indexOf(' const features=['),app.indexOf(' let lastAnalyticsPage'))+';globalThis.api={featurePage,guidePage,featureTracks,featureIdentity,features,listeningGuides,getFiltered:()=>filtered,reviewSummary};',context);
const api=context.api;
api.featurePage('tribe-production');assert(view.innerHTML.includes('知性が、身体を動かす。'));
const all=api.getFiltered().map(t=>t.id);buttons[1].onclick();const own=api.getFiltered().map(t=>t.id);buttons[2].onclick();const related=api.getFiltered().map(t=>t.id);
assert.equal(own.length+related.length,all.length);assert(related.length>0);assert(!own.some(id=>related.includes(id)));
for(const guide of api.listeningGuides){api.guidePage(guide.id);assert.deepEqual(Array.from(api.getFiltered(),t=>t.id),Array.from(guide.ids));assert(view.innerHTML.includes('guide-play'))}
const chronology=window.CrateChronology(songs,esc,{events:window.CRATE_EVENTS});assert(!chronology.includes('MAIN SAMPLE'));assert(!chronology.includes('tc-source'));
const timeline=app.slice(app.indexOf(' function timeline(){'),app.indexOf(' function about()'));assert(!timeline.includes('samples'));assert(!timeline.includes('サンプル'));
assert(!JSON.stringify(songs).includes('90年代を中心にしたこのクレートで'));
const sourceTracks=JSON.parse(fs.readFileSync('tracks.json','utf8'));
for(const source of sourceTracks){const generated=songs.find(t=>t.id===source.id);assert.equal(generated.noteReviewedAt,source.noteReviewedAt,'Review date drift: '+source.id)}
assert(!songs.some(t=>t.review.playbackCheckedAt),'No playback checks should be invented');
const about=app.slice(app.indexOf(' function about()'),app.indexOf(' const editorProfileHTML='));
const mentions=[...about.matchAll(/SUBURBIA CLASSICA/g)];assert(mentions.length>0);
for(const mention of mentions){const before=about.slice(Math.max(0,mention.index-180),mention.index);assert(before.includes('href="https://djnaoyaman.github.io/suburbia-classica/"'))}
console.log('Catalog content states, unified sample search, ATCQ scopes/redirect, guide order, timeline policy, source review dates and sister-site links verified');
