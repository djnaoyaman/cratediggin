const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/app/playlist-ui.js','utf8');
const click=source.match(/link\.onclick=e=>\{([^\n]+?)\};/)[1];
const sync=source.match(/ function syncSelectionQueue\(\)\{[^\n]+/)[0];
for(const customMode of [false,true])for(const started of [false,true])for(const albumOwned of [false,true]){
 const preserve=started||albumOwned;const songs=['a','b','outside'].map(id=>({id})),c={songs,filtered:songs.slice(0,2),customMode,started,albumOwnsPlayback:()=>albumOwned,queueCustom:!customMode,queueScope:['outside'],queue:['outside'],suppressClick:false,actions:{hidden:true},close(){throw Error('unexpected close')},e:{preventDefault(){throw Error('unexpected preventDefault')}},playableIds:rows=>rows.map(t=>t.id),hasPlayableSource:()=>true,myCrate:{ids:['outside','b','a']}};
 vm.createContext(c);vm.runInContext('(function(){'+click+'})()',c);
 assert.deepEqual(Array.from(c.queueScope),preserve?['outside']:['a','b']);assert.deepEqual(Array.from(c.queue),preserve?['outside']:['a','b']);assert.equal(c.queueCustom,preserve?!customMode:customMode);
 if(!preserve&&customMode){vm.runInContext(sync,c);c.syncSelectionQueue();assert.deepEqual(Array.from(c.queue),['b','a']);c.myCrate.ids=['outside','a'];c.syncSelectionQueue();assert.deepEqual(Array.from(c.queue),['a']);c.myCrate.ids=['outside','b','a'];c.syncSelectionQueue();assert.deepEqual(Array.from(c.queue),['b','a']);assert.deepEqual(Array.from(c.queueScope),['a','b']);}
}
console.log('Actual card handler initializes queue/scope/custom atomically only before playback; reorder/remove/restore never admit outside IDs.');
