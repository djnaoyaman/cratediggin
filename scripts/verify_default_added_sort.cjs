const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const all=JSON.parse(fs.readFileSync('tracks.json')),window={TRACKS:all};vm.runInNewContext(fs.readFileSync('src/assets/filters.js','utf8'),{window});
const ids=xs=>Array.from(xs,x=>x.id),run=(xs,state={})=>window.CrateFilter(xs,state),before=JSON.stringify(all);
const expected=all.map((t,i)=>({t,i})).sort((a,b)=>b.t.addedOrder-a.t.addedOrder||b.i-a.i).map(x=>x.t.id);
assert.deepEqual(ids(run(all)),expected);assert.deepEqual(ids(run(all.slice().reverse())),expected);assert.deepEqual(ids(run(all,{sort:'selection-desc'})),expected);assert.deepEqual(ids(run(all,{sort:'selection'})),expected.slice().reverse());
assert.deepEqual(expected.slice(0,2),['godfather-don-piece-of-the-action','science-of-sound-who-got-the-funk']);
const subset=all.filter(t=>t.artist.includes('Gang Starr'));assert.deepEqual(ids(run(all,{q:'Gang Starr'})),expected.filter(id=>run(all,{q:'Gang Starr'}).some(t=>t.id===id)));
for(const sort of ['year','year-desc','artist','artist-desc','title','title-desc']){const result=run(all,{sort});assert.equal(result.length,all.length);assert.equal(new Set(ids(result)).size,all.length);}
const chronological=run(all,{sort:'year'});for(let i=1;i<chronological.length;i++)assert((chronological[i-1].year??9999)<=(chronological[i].year??9999));
assert.equal(JSON.stringify(all),before);const ui=fs.readFileSync('src/app/catalog-ui.js','utf8');assert(ui.includes("k==='sort'?'selection-desc'"));assert(ui.includes("k==='sort'&&v==='selection-desc'"));assert(ui.includes("?f.sort:'selection-desc'"));
console.log('Newest-added default, canonical ties independent of input ordering, explicit chronology, all rows and no mutation PASS');
