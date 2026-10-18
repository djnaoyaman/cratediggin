const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const helpers=fs.readFileSync('src/app/core.js','utf8').split(' const songs=')[0];
const sampleCode=fs.readFileSync('src/app/song-ui.js','utf8').split('\n').filter(l=>/^ function (returnToTrack|createSamplePlayer|disposeSample)\(/.test(l)).join('\n');
const code=helpers+['album-player.js','player.js','inline-player.js'].map(f=>fs.readFileSync('src/app/'+f,'utf8')).join('\n')+'\n'+sampleCode;
const list='OLAK5uy_m8VPjbn9rF3ninCB-n_ToxxHH5U3_TkvE';
function setup(){const els=new Map(),players=[],timers=new Map(),intervals=[],routes=[],loads=[];let seq=0;
 const $=id=>{if(!els.has(id))els.set(id,{checked:true,hidden:false,value:0,textContent:'',style:{},classList:{toggle(){}},listeners:{},addEventListener(k,fn){this.listeners[k]=fn},replaceChildren(...x){this.children=x},setAttribute(){},focus(){},isConnected:true});return els.get(id)};
 const songs=[{id:'video',title:'Video',artist:'A',youtube:{id:'aaaaaaaaaaa',url:'https://www.youtube.com/watch?v=aaaaaaaaaaa'}},{id:'j-dilla-donuts',title:'Donuts',artist:'J Dilla',workType:'album',youtube:{sourceType:'playlist',playlistId:list,url:'https://www.youtube.com/playlist?list='+list,channel:'J Dilla',type:'Official Album'}},{id:'next',title:'Next',artist:'B',youtube:{id:'bbbbbbbbbbb',url:'https://www.youtube.com/watch?v=bbbbbbbbbbb'}}];
 const c={songs,$,window:{},document:{head:{appendChild(){}},createElement:()=>({style:{},setAttribute(){},focus(){},remove(){}}),activeElement:null},location:{origin:'https://example.com'},art:{hidden:true},localStorage:{getItem(){return null},setItem(){}},setInterval:fn=>intervals.push(fn),setTimeout(fn){timers.set(++seq,fn);return seq},clearTimeout:i=>timers.delete(i),cur:0,queue:songs.map(s=>s.id),ready:false,started:false,playing:false,player:null,sourcePlayer:null,sourceId:null,sourceActive:false,returnTime:0,returnPlaying:false,errorCount:0,lastInteraction:0,trackInteraction(){},showArt(){},currentRoute:()=> '#/song/'+songs[c.cur].id,navigate:r=>routes.push(r)};
 c.YT={Player:function(id,o){const p={id,o,loads:[],cues:[],plays:0,pauses:0,destroys:0,loops:[],shuffles:[],index:0,t:0,getDuration:()=>120,getCurrentTime(){return this.t},getPlaylistIndex(){return this.index},getPlaylist:()=>Array.from({length:31},(_,i)=>'member'+i),setLoop:x=>p.loops.push(x),setShuffle:x=>p.shuffles.push(x),loadPlaylist:x=>p.loads.push(x),cuePlaylist:x=>p.cues.push(x),loadVideoById:x=>loads.push(x.videoId),cueVideoById(){},playVideo(){this.plays++},pauseVideo(){this.pauses++},stopVideo(){},destroy(){this.destroys++},seekTo(t){this.t=t},ready(){o.events.onReady({target:p})},state(data){o.events.onStateChange({target:p,data})},error(data=100){o.events.onError({target:p,data})},blocked(){o.events.onAutoplayBlocked({target:p})}};players.push(p);return p}};c.window.YT=c.YT;vm.createContext(c);vm.runInContext(code,c);
 return {c,$,players,loads,routes,intervals,session:()=>vm.runInContext('albumSession',c),locked:()=>vm.runInContext('albumPlaybackLocked',c),timers(){const a=[...timers.values()];timers.clear();a.forEach(fn=>fn())},ready(){c.window.onYouTubeIframeAPIReady();players[0].ready()},album(){c.startSong(1);const p=players.at(-1);p.ready();return p}};
}
{
 const t=setup();t.ready();t.c.loadSong(1,false);assert(t.locked());assert.equal(t.session(),null);assert.equal(t.players.length,1);assert.equal(t.$('#start').hidden,false);t.c.toggle();const p=t.players[1];p.ready();assert.equal(p.loads[0].list,list);assert.equal(p.loads[0].index,0);assert.equal(p.loads[0].listType,'playlist');assert.deepEqual(p.loops,[false]);assert.deepEqual(p.shuffles,[false]);assert.equal(t.loads.length,0);
 for(const auto of [true,false]){t.$('#auto').checked=auto;for(let i=0;i<31;i++){p.index=i;p.state(1);p.state(0)}assert.equal(t.c.cur,1);assert.equal(t.routes.length,0)}
 p.index=29;p.state(1);p.index=30;p.state(1);p.state(0);assert.equal(t.c.cur,1,'Late previous-constituent end cannot advance outer crate');
 p.state(1);p.t=44;t.c.toggle();p.state(2);assert.equal(p.pauses>0,true);const count=p.loads.length;t.c.toggle();p.state(1);assert.equal(p.loads.length,count);assert.equal(p.index,30);assert.equal(p.t,44);t.$('#seek').value=17;t.$('#seek').listeners.input();assert.equal(p.t,17);t.intervals[0]();assert.equal(t.$('#elapsed').textContent,'0:17');
 const old=p;t.c.go(1);assert.equal(t.c.cur,2);assert.equal(old.destroys,1);const before=t.loads.length;for(const n of [1,0,3])old.state(n);old.error();old.blocked();assert.equal(t.c.cur,2);assert.equal(t.loads.length,before);assert.equal(t.$('#now-title').textContent,'Next');
}
{
 const t=setup();t.c.startSong(0);t.c.startSong(1);const album=t.players[0];t.c.window.onYouTubeIframeAPIReady();t.players[1].ready();album.ready();assert.equal(t.loads.length,0,'Late main readiness cannot load a video over album');album.state(1);for(const n of [0,1,3])t.players[1].state(n);t.players[1].error();t.players[1].blocked();assert.equal(t.c.cur,1);assert.equal(t.c.playing,true);assert.equal(t.players[1].pauses>0,true);
}
{
 const t=setup();t.c.window.YT=undefined;t.c.startSong(1);assert.equal(t.players.length,0);t.c.toggle();assert.equal(t.session().wantsPlay,false);t.c.window.YT=t.c.YT;t.c.window.onYouTubeIframeAPIReady();t.players[0].ready();const p=t.players[1];p.ready();assert.equal(p.loads.length,0);assert.equal(p.cues[0].list,list);t.c.toggle();assert.equal(p.plays,1);
}
for(const failure of ['error','blocked','timeout']){const t=setup();t.ready();const p=t.album();if(failure==='timeout')t.timers();else p[failure]();assert(t.session().failed);assert.equal(t.$('#start').hidden,false);for(const n of [0,1,3])p.state(n);assert.equal(t.c.cur,1);t.c.toggle();const retry=t.players.at(-1);assert.notEqual(retry,p);retry.ready();assert.equal(retry.loads[0].list,list);assert.equal(p.destroys,1);}
{
 const t=setup();t.ready();t.c.startSong(0);t.players[0].error();const p=t.album();p.state(1);t.timers();assert.equal(t.c.cur,1,'Old video error timer cannot skip album');
 t.c.disposeAlbumPlayer();t.c.started=false;t.c.toggleUI(false);p.state(1);p.state(0);assert.equal(t.session(),null);assert.equal(t.c.playing,false);t.c.toggle();assert.notEqual(t.session().player,p);
}
{
 const t=setup();t.ready();t.c.currentRoute=()=> '#/song/ini-grown-man-sport';t.c.openInlinePlayer();const p=t.album();p.state(1);assert.equal(vm.runInContext('inlineFrame',t.c),null);t.c.openInlinePlayer();assert.equal(t.session(),null);assert.equal(p.destroys,1);p.state(1);assert.equal(t.c.playing,false);assert(vm.runInContext('inlineFrame',t.c));
}
{
 const t=setup();t.ready();const p=t.album();p.state(1);t.c.pauseActivePlayer();p.state(2);t.c.queue=[];const played=p.plays;t.c.toggle();assert.equal(p.plays,played);assert.equal(t.session().player,p);assert.equal(p.loads.length,1);assert.equal(t.c.cur,1);assert.equal(t.c.playing,false);
}
{const t=setup();t.ready();t.c.createSamplePlayer('ccccccccccc');const sample=t.players.at(-1);sample.ready();const p=t.album();p.state(1);const n=p.plays;sample.state(1);sample.state(0);sample.error();t.c.returnPlaying=true;t.c.sourceActive=true;t.c.disposeSample();assert.equal(p.plays,n);assert.equal(t.c.playing,true);assert.equal(t.c.cur,1);assert.equal(t.players[0].plays,0);}
{const t=setup();t.ready();const p=t.album();p.state(1);p.state(3);t.timers();assert(t.session().failed,'Playing then stalled buffering must expose retry');assert.equal(t.$('#start').hidden,false);assert.equal(t.c.cur,1);}
console.log('Native album ownership, 31 transitions/final stop, late-event isolation, pause/resume/seek, delayed readiness/cancel, error/retry, inline handover and empty-crate safety passed; no real playback claim');
