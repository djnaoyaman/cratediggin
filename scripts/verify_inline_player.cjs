const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const inlineSource=fs.readFileSync('src/app/inline-player.js','utf8');
const sampleSource=fs.readFileSync('src/app/song-ui.js','utf8').split('\n').filter(l=>/^ function (returnToTrack|createSamplePlayer|disposeSample)\(/.test(l)).join('\n');
const playerSource=fs.readFileSync('src/app/player.js','utf8');
const selectionSource=fs.readFileSync('src/app/editorial.js','utf8').split('\n').find(line=>line.includes('function playSelection('));
function setup(){
 const elements=new Map(),loads=[],cues=[],players=[],storage=new Map(),copied=[],timers=new Map();let timerId=0;
 const $=id=>{if(!elements.has(id))elements.set(id,{checked:true,hidden:false,value:0,textContent:'',isConnected:true,attrs:{},listeners:{},style:{},setAttribute(k,v){this.attrs[k]=v},focus(){},replaceChildren(x){this.child=x},classList:{toggle(){}},addEventListener(k,v){this.listeners[k]=v}});return elements.get(id)};
 const songs=[{id:'first',title:'First',artist:'A',youtube:{id:'aaaaaaaaaaa',url:'https://www.youtube.com/watch?v=aaaaaaaaaaa'}},{id:'chosen',title:'Chosen',artist:'B',youtube:{id:'bbbbbbbbbbb',url:'https://www.youtube.com/watch?v=bbbbbbbbbbb'}}];
 const c={songs,$,window:{},art:{hidden:true},document:{createElement:()=>({style:{},setAttribute(){},focus(){},remove(){this.removed=true}}),head:{appendChild(){}},activeElement:null},location:{origin:'https://example.com'},localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},navigator:{clipboard:{writeText:async text=>copied.push(text)}},setInterval(){},setTimeout(fn){const id=++timerId;timers.set(id,fn);return id},clearTimeout(id){timers.delete(id)},cur:0,queue:['first','chosen'],queueScope:[],queueCustom:false,ready:false,started:false,playing:false,player:null,sourcePlayer:null,sourceId:null,sourceReady:false,sourceActive:false,returnPlaying:false,returnTime:0,errorCount:0,lastInteraction:0,trackInteraction(){},currentRoute:()=> '#/song/ugly-duckling-now-who-s-laughin',navigate(){},playableIds:xs=>xs.map(t=>t.id),YT:{Player:function(id,options){const p={loadVideoById:v=>loads.push(v.videoId),cueVideoById:v=>cues.push(v.videoId),pauses:0,plays:0,pauseVideo(){this.pauses++},playVideo(){this.plays++},stopVideo(){},seekTo(){},getCurrentTime(){return 0},destroy(){},makeReady(){options.events.onReady({target:p})},block(){options.events.onAutoplayBlocked()},fail(code){options.events.onError({data:code})},state(data){options.events.onStateChange({data})}};players.push(p);return p;}}};
 c.window.YT=c.YT;vm.createContext(c);vm.runInContext(playerSource+'\n'+inlineSource+'\n'+sampleSource+'\n'+selectionSource,c);
 return {c,loads,cues,players,$,copied,runTimers(){const pending=[...timers.values()];timers.clear();pending.forEach(fn=>fn())},ready(){c.window.onYouTubeIframeAPIReady();players[0].makeReady()}};
}
function locked(t){return vm.runInContext('inlinePlaybackLocked',t.c)}
function frame(t){return vm.runInContext('inlineFrame',t.c)}
{
 const t=setup();t.c.startSong();t.c.window.onYouTubeIframeAPIReady();t.c.openInlinePlayer();assert(locked(t));assert(frame(t));t.c.disposeInlinePlayer(true);assert.equal(frame(t),null);t.players[0].makeReady();assert.deepEqual(t.loads,[]);assert.equal(t.c.started,false);t.c.startSong();assert(!locked(t));assert.equal(t.loads.length,1);
}
{
 const t=setup();t.ready();t.c.startSong();t.players[0].fail(150);t.c.openInlinePlayer();const n=t.loads.length;for(const state of [0,1,3,2])t.players[0].state(state);t.players[0].fail(150);t.players[0].block();t.runTimers();assert.equal(t.loads.length,n);assert.equal(t.c.cur,0);assert.equal(t.c.started,false);assert.equal(t.c.playing,false);assert.equal(t.$('#status').textContent,'');assert(t.players[0].pauses>0);t.$('#seek').listeners.input();assert(t.$('#status').textContent.includes('再生ボタン'));
 const old=frame(t);t.c.openInlinePlayer();assert(old.removed);assert.notEqual(frame(t),old);t.c.disposeInlinePlayer();assert.equal(frame(t),null);t.players[0].state(0);t.runTimers();assert.equal(t.c.cur,0);t.c.toggle();assert(!locked(t));assert.equal(t.loads.length,n+1);
}
{
 const t=setup();t.c.window.onYouTubeIframeAPIReady();t.c.openInlinePlayer();t.c.disposeInlinePlayer();t.c.sourceId='ccccccccccc';t.players[0].makeReady();assert.equal(t.players.length,2,'sample must initialize after locked delayed readiness');t.players[1].makeReady();assert(t.c.sourceReady);t.players[1].state(1);t.players[1].state(0);t.players[1].fail(150);assert.equal(t.players[0].plays,0);assert.equal(t.c.sourceActive,false);t.c.returnPlaying=true;t.c.sourceActive=true;t.c.disposeSample();assert.equal(t.players[0].plays,0);t.c.startSong();assert(!locked(t));
}
{
 const t=setup();assert.equal(t.c.inlinePlayerMarkup({id:'different'}),'');assert(t.c.inlinePlayerMarkup({id:'ugly-duckling-now-who-s-laughin'}).includes('aria-controls'));assert(!t.c.inlinePlayerMarkup({id:'ugly-duckling-now-who-s-laughin'}).includes('<iframe'));t.ready();t.c.bindInlinePlayer({id:'ugly-duckling-now-who-s-laughin'});t.$('#inline-player-open').onclick();assert(frame(t));let prevented=false;t.$('#inline-player-panel').listeners.keydown({key:'Escape',preventDefault(){prevented=true}});assert(prevented);assert.equal(frame(t),null);assert.equal(t.$('#inline-player-open').attrs['aria-expanded'],'false');
}
console.log('Inline lifecycle: delayed readiness, cancelled pending play, late main/sample callbacks, stale timers, exclusive owner, repeat/close/retry, seek, sample navigation recovery, parent keyboard and track allowlist passed');

{
 const t=setup();t.c.currentRoute=()=> '#/song/ini-grown-man-sport';t.c.songs[0].id='ini-grown-man-sport';t.c.queue[0]='ini-grown-man-sport';t.ready();t.c.startSong();const n=t.loads.length;t.players[0].fail(100);t.runTimers();assert.equal(t.c.cur,0);assert.equal(t.loads.length,n);assert.equal(t.$('#auto').checked,true);assert(t.$('#status').textContent.includes('別プレイヤー'));for(const state of [0,1,3])t.players[0].state(state);t.players[0].block();t.players[0].fail(150);t.runTimers();assert.equal(t.c.cur,0);assert.equal(t.loads.length,n);assert.equal(t.c.started,false);assert.equal(t.c.playing,false);assert.equal(t.$('#auto').checked,true);t.c.startSong();assert(!locked(t));assert.equal(t.loads.length,n+1);t.players[0].fail(100);assert(locked(t));assert(t.c.inlinePlayerMarkup(t.c.songs[0]).includes('aria-controls'));t.c.openInlinePlayer();assert(frame(t).src.includes('track=2828430171'));assert(locked(t));t.players[0].state(0);t.players[0].fail(150);t.runTimers();assert.equal(t.c.cur,0);assert.equal(t.loads.length,n+1);t.c.disposeInlinePlayer();t.c.startSong();assert(!locked(t));assert.equal(t.$('#auto').checked,true);
}
{
 const t=setup();t.ready();t.c.startSong();t.players[0].fail(100);t.runTimers();assert.equal(t.c.cur,1,'Other tracks retain error auto-next');
}
console.log('Grown Man Sport exact official inline URL, unavailable-source retention, preserved auto preference and other-track auto-next passed');
