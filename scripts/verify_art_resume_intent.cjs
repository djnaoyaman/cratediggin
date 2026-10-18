const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const suite=fs.readFileSync('scripts/verify_player_intent.cjs','utf8').split('\nfor(const album of [false,true]){')[0];
assert(suite.includes('function setup()'));
const outer={require,console};vm.createContext(outer);vm.runInContext(suite+';this.setup=setup',outer);
function setup(){const t=outer.setup(),c=t.c;c.document.body={dataset:{},style:{setProperty(){}}};c.sourceReady=false;c.innerWidth=390;c.innerHeight=844;c.clearArtDock=()=>{};c.isolateArtPaths=()=>{};c.artDockGeometry=()=>({});c.refreshArtProvider=()=>{};c.artInfo=()=>{};c.window.CrateArt={resize(){},change(){}};vm.runInContext(fs.readFileSync('src/app/art-modes.js','utf8'),c);return t;}
for(const initialReady of [false,true])for(const began of [false,true]){
 const t=setup(),c=t.c;c.window.onYouTubeIframeAPIReady();const p=t.players[0];if(initialReady)p.ready();if(began){c.startSong(0);if(initialReady)p.state(1)}p.t=43;c.art.hidden=false;
 const before={plays:p.plays,pauses:p.pauses,loads:t.loads.length,intent:vm.runInContext('JSON.stringify(mainIntent)',c),pending:vm.runInContext('JSON.stringify(pendingLoad)',c)};
 for(const mode of ['full','video','hybrid','full'])c.setArtPresentation(mode);
 assert.equal(p.plays,before.plays);assert.equal(p.pauses,before.pauses);assert.equal(t.loads.length,before.loads);assert.equal(vm.runInContext('JSON.stringify(mainIntent)',c),before.intent);assert.equal(vm.runInContext('JSON.stringify(pendingLoad)',c),before.pending);assert.equal(p.t,43);assert.equal(c.cur,0);assert.deepEqual(Array.from(c.queue),['video','j-dilla-donuts','next']);
 if(initialReady&&began){const pauses=p.pauses;c.$('#art-toggle').onclick();assert.equal(p.pauses,pauses+1);assert.equal(vm.runInContext('artDisplayMode',c),'full','Explicit transport does not change presentation');}
}
console.log('Real player plus three presentation modes: transport/pending intent/time/queue invariant, explicit user pause remains operative.');
