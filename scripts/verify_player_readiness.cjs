const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const coreSource=fs.readFileSync('src/app/core.js','utf8');
const playerSource=coreSource.slice(0,coreSource.indexOf(' const songs='))+fs.readFileSync('src/app/album-player.js','utf8')+fs.readFileSync('src/app/player.js','utf8');
const selectionSource=fs.readFileSync('src/app/editorial.js','utf8').split('\n').find(line=>line.includes('function playSelection('));
function setup(){
 const elements=new Map(),loads=[],cues=[],players=[],storage=new Map(),copied=[],timers=new Map();let timerId=0;
 const $=id=>{if(!elements.has(id))elements.set(id,{checked:true,hidden:false,value:0,textContent:'',classList:{toggle(){}},addEventListener(){}});return elements.get(id)};
 const songs=[{id:'first',title:'First',artist:'A',youtube:{id:'aaaaaaaaaaa',url:'https://www.youtube.com/watch?v=aaaaaaaaaaa'}},{id:'chosen',title:'Chosen',artist:'B',youtube:{id:'bbbbbbbbbbb',url:'https://www.youtube.com/watch?v=bbbbbbbbbbb'}}];
 const c={songs,$,window:{},art:{hidden:true},document:{createElement:()=>({}),head:{appendChild(){}},activeElement:null},location:{origin:'https://example.com'},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},navigator:{clipboard:{writeText:async text=>copied.push(text)}},setInterval(){},setTimeout(fn){const id=++timerId;timers.set(id,fn);return id},clearTimeout(id){timers.delete(id)},cur:0,queue:['first','chosen'],queueScope:[],queueCustom:false,ready:false,started:false,playing:false,player:null,sourcePlayer:null,sourceId:null,sourceActive:false,returnPlaying:false,returnTime:0,errorCount:0,lastInteraction:0,trackInteraction(){},currentRoute:()=> '#/',navigate(){},playableIds:xs=>xs.map(t=>t.id),YT:{Player:function(id,options){const p={loadVideoById:v=>loads.push(v.videoId),cueVideoById:v=>cues.push(v.videoId),pauseVideo(){},playVideo(){},stopVideo(){},makeReady(){options.events.onReady({target:p})},block(){options.events.onAutoplayBlocked()},fail(code){options.events.onError({data:code})},state(data){options.events.onStateChange({data})}};players.push(p);return p;}}};
 vm.createContext(c);vm.runInContext(playerSource+'\n'+selectionSource,c);
 return {c,loads,cues,players,$,copied,runTimers(){const pending=[...timers.values()];timers.clear();pending.forEach(fn=>fn())},ready(){c.window.onYouTubeIframeAPIReady();players[0].makeReady()}};
}
{
 const t=setup();t.c.startSong(1);t.ready();assert.deepEqual(t.loads,['bbbbbbbbbbb'],'A play click before readiness must resume the requested song');assert.equal(t.c.cur,1);
}
{
 const t=setup();t.c.window.onYouTubeIframeAPIReady();t.c.loadSong(1,false);t.players[0].makeReady();assert.deepEqual(t.cues,['bbbbbbbbbbb'],'A changed selection must replace the initial iframe video');assert.deepEqual(t.loads,[],'Browsing alone must not autoplay');
}
{
 const t=setup();t.c.queue=['chosen'];t.c.toggle();t.ready();assert.deepEqual(t.loads,['bbbbbbbbbbb'],'Early global playback must honor exclusions');
}
{
 const t=setup();t.c.toggle();t.c.toggle();t.ready();assert.deepEqual(t.loads,[],'A second toggle cancels pending playback');assert.deepEqual(t.cues,['aaaaaaaaaaa']);assert.equal(t.c.started,false);
}
{
 const t=setup();t.c.playSelection([t.c.songs[1]],true);t.ready();assert.deepEqual(t.loads,['bbbbbbbbbbb'],'An early playlist/feature/guide click must preserve its selection');assert.deepEqual(Array.from(t.c.queue),['chosen']);
}
{
 const t=setup();t.ready();t.c.startSong(1);t.players[0].block();assert.equal(t.$('#start').hidden,false,'Blocked autoplay must restore a visible retry button');t.c.startSong();assert.equal(t.loads.at(-1),'bbbbbbbbbbb');
}
console.log('Early song, cued selection, exclusions, cancellation, playlist and blocked-autoplay retry passed');



for(const intervention of ['disable-auto','sample','same-track-retry']){const t=setup();t.ready();t.c.startSong(1);t.players[0].fail(150);if(intervention==='disable-auto')t.$('#auto').checked=false;if(intervention==='sample')t.c.sourceActive=true;if(intervention==='same-track-retry')t.c.startSong(1);t.runTimers();assert(t.loads.every(id=>id==='bbbbbbbbbbb'),intervention+' must cancel a stale auto-skip');assert.equal(t.c.cur,1)}
console.log('Provider-error auto-skip respects auto preference, sample playback and manual retry');

{const t=setup();t.ready();t.c.startSong(1);t.players[0].fail(150);assert(t.$('#status').textContent.includes('YouTube'));assert.equal(t.c.playbackErrors().length,1);assert.equal(t.copied.length,0);assert(!playerSource.includes('playback-report'));assert(!fs.readFileSync('templates/index.html','utf8').includes('playback-report'));}
{const t=setup();t.ready();t.c.startSong(1);t.runTimers();assert.equal(t.$('#start').hidden,false);assert(t.$('#status').textContent.includes('読み込みに時間'));assert.equal(t.c.playbackErrors()[0].code,'LOAD_TIMEOUT');const ok=setup();ok.ready();ok.c.startSong(1);ok.players[0].state(1);ok.runTimers();assert.equal(ok.c.playbackErrors().length,0);}
console.log('Failed-track copy control absent; retry, external link and internal error handling preserved');

for(const readyFirst of [false,true]){
 const t=setup();if(readyFirst)t.ready();t.c.startSong(1);
 t.c.songs.push({id:'external',title:'External',artist:'C',youtube:{id:null,url:'https://example.com/search'},externalAudio:{url:'https://example.com/audio'}});
 t.c.loadSong(2,true);assert.equal(t.c.cur,2);assert.equal(t.c.started,false);
 assert.equal(vm.runInContext('mainIntent.wantsPlay',t.c),false,'Unavailable source clears old play intent');
 assert.equal(vm.runInContext('pendingLoad',t.c),null,'Unavailable source clears pending old track');
 if(!readyFirst){t.ready();assert.equal(t.loads.length,0);assert.equal(t.cues.length,0);assert(t.$('#status').textContent.includes('サイト内再生は確認中'),'Late readiness must preserve unavailable status');}
 const before=t.loads.length;t.c.toggle();t.c.startSong();assert.equal(t.loads.length,before);assert.equal(t.c.cur,2);
 assert(t.$('#status').textContent.includes('未確定'));
}
console.log('Switching from pending/active audio to external-only track clears playback and prevents fallback');

for(const [id,video] of Object.entries({"mos-def-universal-magnetic":"TsoCr5KoNoM","siah-yeshua-dapoed-the-visualz":"iMAeEkIoBK0"})){
 const selected=JSON.parse(fs.readFileSync("tracks.json","utf8")).find(x=>x.id===id);assert.equal(selected.youtube.id,video);assert(!selected.externalAudio);
 const t=setup();t.c.songs[1]=selected;t.c.queue=["first",id];t.c.startSong(1);t.ready();assert.deepEqual(t.loads,[video],"Owner-selected source must reach loadVideoById exactly");assert.equal(t.c.cur,1);
}
console.log("Both owner-selected KIYO sources route to their exact IDs; mock only, no actual playback claim");
