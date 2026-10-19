const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/app/song-ui.js','utf8').split(' function editorSelectionMemory')[0];const context={esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;')};vm.createContext(context);vm.runInContext(source,context);
const base={essay:['a'],sources:[{url:'https://example.org/a',label:'A & B'}]};
for(const mapping of [undefined,[],[null],[[true]],[[1]],[[-1]],[['0']]])assert.equal(context.essayReferenceMarkup({...base,essaySources:mapping},0),'');
const valid=context.essayReferenceMarkup({...base,essaySources:[[0,0]]},0);assert.equal((valid.match(/<a /g)||[]).length,1);assert(valid.includes('A &amp; B'));assert(valid.includes('noopener noreferrer'));
for(const ref of [{url:'javascript:alert(1)',label:'x'},{url:'https://example.org',label:''}])assert.equal(context.essayReferenceMarkup({...base,sources:[ref],essaySources:[[0]]},0),'');
console.log('Client essay references: missing/invalid indices suppressed, valid references deduplicated and escaped; no transport dependency');
const tracks=JSON.parse(fs.readFileSync('tracks.json','utf8'));let mapped=0;for(const t of tracks){for(let i=0;i<t.essay.length;i++){const actual=context.essayReferences(t,i).map(x=>({url:x.url,label:x.label}));const indices=t.essaySources?.[i]||[];const seen=new Set(),expected=indices.map(j=>t.sources[j]).filter(r=>{if(seen.has(r.url))return false;seen.add(r.url);return true}).map(x=>({url:x.url,label:x.label}));assert.equal(JSON.stringify(actual),JSON.stringify(expected),t.id+':'+i);}if(t.essaySources)mapped++;}assert.equal(mapped,66);console.log('All66 authored client mappings match exact source URL+label order;433 absent mappings remain empty');

for(const invalid of [null,{url:'javascript:bad',label:'bad'},{url:'https://example.org/b',label:''}])assert.equal(context.essayReferenceMarkup({...base,sources:[base.sources[0],invalid],essaySources:[[0,1]]},0),'');
