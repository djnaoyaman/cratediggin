const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const context={window:{}};vm.createContext(context);
for(const file of ['tracks.js','filters.js'])vm.runInContext(fs.readFileSync('dist/'+file,'utf8'),context);
const {TRACKS:songs,CRATE_SHELVES:shelves,CrateFilter:filter}=context.window;
assert.equal(shelves.length,6);assert.equal(filter(songs,{}).length,songs.length);
const tagged=songs.filter(s=>s.listeningTags.length);assert(tagged.length<songs.length,'Do not auto-classify all tracks');
for(const shelf of shelves){
 const actual=filter(songs,{collection:shelf.id});assert(actual.length>0);
 assert.deepEqual(actual.map(s=>s.id).sort(),songs.filter(s=>s.listeningTags.includes(shelf.id)).map(s=>s.id).sort());
 for(const coast of ['east','west','other'])assert(filter(songs,{collection:shelf.id,coast}).every(s=>s.listeningTags.includes(shelf.id)));
 const term=actual[0].title;assert(filter(songs,{collection:shelf.id,q:term}).some(s=>s.id===actual[0].id));
 assert.equal(filter(songs,{collection:shelf.id,q:'zzzz-no-such-track-zzzz'}).length,0);
 console.log(shelf.label+': '+actual.length+' tracks');
}
assert(songs.some(s=>s.listeningTags.length>1));
assert(filter(songs,{q:'Quasimoto'}).some(s=>s.artist==='Quasimoto'));
console.log('All '+songs.length+' records remain discoverable; '+tagged.length+' have reviewed listening tags.');
