const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const helpers=fs.readFileSync('src/app/core.js','utf8').split(' const songs=')[0];
const sampleCode=fs.readFileSync('src/app/song-ui.js','utf8').split('\n').filter(l=>/^ function (returnToTrack|createSamplePlayer|disposeSample)\(/.test(l)).join('\n');
const code=helpers+['album-player.js','player.js','inline-player.js'].map(f=>fs.readFileSync('src/app/'+f,'utf8')).join('\n')+'\n'+sampleCode;
const list='OLAK5uy_m8VPjbn9rF3ninCB-n_ToxxHH5U3_TkvE';
function setup(){const storage=new Map(),els=new Map(),players=[],timers=new Map(),intervals=[],routes=[],loads=[];let seq=0;
 const $=id=>{if(!els.has(id))els.set(id,{checked:true,hidden:false,value:0,textContent:'',style:{},classList:{toggle(){}},listeners:{},addEventListener(k,fn){this.listeners[k]=fn},replaceChildren(...x){this.children=x},setAttribute(){},focus(){},isConnected:true});return els.get(id)};
 const songs=[{id:'video',title:'Video',artist:'A',youtube:{id:'aaaaaaaaaaa',url:'https://www.youtube.com/watch?v=aaaaaaaaaaa'}},{id:'j-dilla-donuts',title:'Donuts',artist:'J Dilla',workType:'album',youtube:{sourceType:'playlist',playlistId:list,url:'https://www.youtube.com/playlist?list='+list,channel:'J Dilla',type:'Official Album'}},{id:'next',title:'Next',artist:'B',youtube:{id:'bbbbbbbbbbb',url:'https://www.youtube.com/watch?v=bbbbbbbbbbb'}}];
 const c={songs,$,window:{},document:{head:{appendChild(){}},createElement:()=>({style:{},setAttribute(){},focus(){},remove(){}}),activeElement:null},location:{origin:'https://example.com'},art:{hidden:true},localStorage:{getItem(k){return storage.get(k)||null},setItem(k,v){storage.set(k,v)}},setInterval:fn=>intervals.push(fn),setTimeout(fn){timers.set(++seq,fn);return seq},clearTimeout:i=>timers.delete(i),cur:0,queue:songs.map(s=>s.id),ready:false,started:false,playing:false,player:null,sourcePlayer:null,sourceId:null,sourceActive:false,returnTime:0,returnPlaying:false,errorCount:0,lastInteraction:0,trackInteraction(){},showArt(){},currentRoute:()=> '#/song/'+songs[c.cur].id,navigate:r=>routes.push(r)};
 c.YT={Player:function(id,o){const frame={...$('#'+id),isConnected:true};if(id==='sample-yt')els.set('#'+id,frame);const p={id,o,loads:[],cues:[],plays:0,pauses:0,destroys:0,loops:[],shuffles:[],index:0,t:0,stateValue:-1,video:o.videoId||'',getIframe(){return frame},getPlayerState(){return this.stateValue},getVideoData(){return {video_id:this.video}},getDuration:()=>120,getCurrentTime(){return this.t},getPlaylistIndex(){return this.index},getPlaylist:()=>Array.from({length:31},(_,i)=>'member'+i),setLoop:x=>p.loops.push(x),setShuffle:x=>p.shuffles.push(x),loadPlaylist:x=>p.loads.push(x),cuePlaylist:x=>p.cues.push(x),loadVideoById(x){this.video=x.videoId;loads.push(x.videoId)},cueVideoById(x){this.video=x.videoId},playVideo(){this.plays++},pauseVideo(){this.pauses++},stopVideo(){},destroy(){this.destroys++;frame.isConnected=false},seekTo(t){this.t=t},ready(){o.events.onReady({target:p})},state(data){this.stateValue=data;o.events.onStateChange({target:p,data})},error(data=100){o.events.onError({target:p,data})},blocked(){o.events.onAutoplayBlocked({target:p})}};players.push(p);return p}};c.window.YT=c.YT;vm.createContext(c);vm.runInContext(code,c);
 return {c,$,players,loads,routes,intervals,session:()=>vm.runInContext('albumSession',c),locked:()=>vm.runInContext('albumPlaybackLocked',c),timers(){const a=[...timers.values()];timers.clear();a.forEach(fn=>fn())},ready(){c.window.onYouTubeIframeAPIReady();players[0].ready()},album(){c.startSong(1);const p=players.at(-1);p.ready();return p}};
}

for(const album of [false,true]){
 const t=setup();t.ready();const p=album?t.album():(t.c.startSong(0),t.players[0]);p.state(1);const before=p.pauses;
 t.$('#toggle').onclick();assert.equal(t.$('#toggle').textContent,'▶');t.$('#art-toggle').onclick();assert.equal(t.$('#art-toggle').textContent,'Ⅱ');assert.equal(p.pauses-before,1);assert.equal(p.plays,1);
 p.state(2);assert.equal(t.$('#toggle').textContent,'Ⅱ','Delayed pause must not cancel latest resume');p.state(1);assert.equal(t.c.playing,true);
 t.c.toggle();assert.equal(t.$('#art-toggle').textContent,'▶');p.state(1);assert.equal(t.$('#art-toggle').textContent,'▶','Late playing cannot undo requested pause');p.state(3);assert.equal(t.$('#art-toggle').textContent,'▶');p.state(2);
 p.state(1);assert.equal(t.$('#toggle').textContent,'Ⅱ','Native play works after pause acknowledgement');p.state(2);assert.equal(t.$('#toggle').textContent,'▶','Native pause works');
}
for(const album of [false,true]){
 const t=setup();t.ready();const p=album?t.album():(t.c.startSong(0),t.players[0]);const before=p.pauses;t.c.toggle();assert.equal(p.plays,0);assert.equal(p.pauses-before,1);assert.equal(t.$('#toggle').textContent,'▶');p.state(1);assert.equal(t.$('#toggle').textContent,'▶');p.state(2);p.state(1);assert.equal(t.c.playing,true);
}
for(const album of [false,true]){
 const t=setup();t.ready();const p=album?t.album():(t.c.startSong(0),t.players[0]);t.c.toggle();p.stateValue=2;t.timers();p.state(1);assert.equal(t.c.playing,true,'No-event paused acknowledgement must permit later native play');
}
{
 const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];p.state(1);t.c.toggle();p.state(2);p.state(0);assert.equal(t.c.cur,0,'Ended after pause must not auto advance');t.c.toggle();p.state(1);p.state(0);assert.equal(t.c.cur,1);p.state(0);assert.equal(t.c.cur,1,'Outgoing duplicate end cannot advance album');
 t.c.go(1);assert.equal(t.c.cur,2);p.video='aaaaaaaaaaa';p.state(1);p.state(0);assert.equal(t.c.cur,2,'Mismatched provider video events ignored');
}
for(const wanted of [true,false]){
 const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];p.state(1);t.c.toggle();if(wanted)t.c.toggle();
 t.c.createSamplePlayer('ccccccccccc');const sample=t.players.at(-1);sample.ready();sample.state(1);assert.equal(t.c.returnPlaying,wanted);assert.equal(t.c.sourceActive,true);p.state(1);assert.equal(t.c.playing,false,'Late main play cannot claim sample ownership');
 sample.state(0);assert.equal(t.c.sourceActive,false);assert.equal(t.$('#toggle').textContent,wanted?'Ⅱ':'▶','Sample return restores requested state');
}
{
 const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];p.state(1);t.c.createSamplePlayer('ccccccccccc');const sample=t.players.at(-1);sample.ready();sample.state(1);t.c.disposeSample();assert.equal(t.$('#toggle').textContent,'Ⅱ','Sample disposal restores through intent path');
}
{
 const t=setup();t.ready();t.$('#elapsed').textContent='2:40';t.$('#duration').textContent='4:23';t.c.loadSong(1,false);assert.equal(t.$('#elapsed').textContent,'0:00');assert.equal(t.$('#duration').textContent,'—');t.c.loadSong(2,false);assert.equal(t.$('#duration').textContent,'—');
}
for(const album of [false,true]){
 const t=setup();t.c.window.YT=undefined;t.c.startSong(album?1:0);t.$('#art-toggle').onclick();t.c.window.YT=t.c.YT;t.ready();if(album){const p=t.players[1];p.ready();assert.equal(p.loads.length,0);assert.equal(p.cues.length,1)}else assert.equal(t.loads.length,0);assert.equal(t.c.started,false);
}
console.log('Asynchronous main/album rapid global-ART intent, loading cancel, late callbacks, native recovery, sample return and duration reset passed; no real playback claim');

{const t=setup();t.ready();const p=t.album();p.index=0;p.state(1);p.state(0);assert.equal(t.session().wantsPlay,true);p.state(3);t.timers();assert.equal(t.session().failed,true,'Intermediate member stall must retain watchdog');}
{const t=setup();t.ready();const p=t.album();p.index=30;p.state(1);p.state(0);assert.equal(t.session().wantsPlay,false);assert.equal(t.c.cur,1);assert.equal(t.$('#toggle').textContent,'▶');}
{const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];p.video='';p.error(100);assert.equal(t.c.playbackErrors().length,1,'Unknown provider metadata must not discard errors');}
{const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];for(const state of [-1,5,3]){p.state(state);assert.equal(t.$('#toggle').textContent,'Ⅱ');}t.c.toggle();for(const state of [-1,5,3]){p.state(state);assert.equal(t.$('#toggle').textContent,'▶');}}

{const t=setup();t.ready();t.c.startSong(0);const p=t.players[0];t.timers();assert.equal(t.$('#toggle').textContent,'▶');assert(t.$('#status').textContent.includes('時間がかかっています'));const plays=p.plays;t.c.toggle();assert.equal(p.plays,plays+1,'Timeout next toggle retries rather than pausing again');assert.equal(t.$('#toggle').textContent,'Ⅱ');}

{const t=setup();t.ready();const p=t.players[0];p.state(1);assert.equal(t.c.playing,true,'Native play immediately after cue is accepted');}
{const t=setup();t.c.window.YT=undefined;t.c.startSong(1);t.c.toggle();t.c.window.YT=t.c.YT;t.ready();const p=t.players[1];p.ready();assert.equal(p.cues.length,1);p.state(1);assert.equal(t.c.playing,true,'Native album play immediately after cue is accepted');}

{const t=setup();t.ready();t.c.startSong(0);const main=t.players[0];main.state(1);t.c.createSamplePlayer('ccccccccccc');const sample=t.players.at(-1);sample.ready();assert.equal(vm.runInContext('sourceReady',t.c),true,'Replacement iframe is accepted as ready');sample.state(1);assert.equal(t.c.sourceActive,true);assert(main.pauses>0);t.c.disposeSample();const before={status:t.$('#status').textContent,pauses:main.pauses};sample.ready();sample.state(1);sample.state(0);sample.error();assert.equal(vm.runInContext('sourceReady',t.c),false);assert.equal(t.c.sourceActive,false);assert.equal(t.$('#status').textContent,before.status);assert.equal(main.pauses,before.pauses,'Disposed sample callbacks cannot affect current owner');}
