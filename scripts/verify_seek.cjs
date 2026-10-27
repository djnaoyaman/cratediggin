'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/app/seek.js','utf8');
function setup(){
 const elements=new Map(),calls=[],timers=[];const $=s=>{if(!elements.has(s))elements.set(s,{value:0,listeners:{},style:{setProperty(){}},setAttribute(k,v){this[k]=v},addEventListener(k,v){this.listeners[k]=v}});return elements.get(s)};
 const p={t:30,d:120,state:1,video:'video1',index:0,getPlayerState(){return this.state},getDuration(){return this.d},getCurrentTime(){return this.t},getVideoData(){return {video_id:this.video}},getPlaylistIndex(){return this.index},seekTo(t,a){calls.push(['seek',t,a]);this.t=t;if(this.state!==2)this.state=1},pauseVideo(){calls.push(['pause']);this.state=2}};
 const c={$,songs:[{id:'work1',youtube:{id:'video1'}}],cur:0,player:p,mainIntent:{wantsPlay:true,reachedPlaying:true},albumSession:null,albumPlaybackLocked:false,inlinePlaybackLocked:false,sourceActive:false,ready:true,playbackIntent:1,started:true,lastInteraction:0,mainVideoMatches:()=>p.video===c.songs[c.cur].youtube.id,albumCurrent:o=>o===c.albumSession,requestMainPause(){c.mainIntent.wantsPlay=false;p.pauseVideo()},go(n){calls.push(['next',n])},setTimeout:f=>timers.push(f),Date};
 vm.createContext(c);vm.runInContext(source,c);const range=$('#seek');const fire=(type,value)=>{if(value!==undefined)range.value=value;range.listeners[type]?.({key:value,preventDefault(){},stopPropagation(){}})};return {c,p,$,calls,fire,timers,run:s=>vm.runInContext(s,c)};
}
{
 const t=setup();t.c.refreshSeek();assert(!t.$('#seek').disabled);assert.equal(t.$('#art-elapsed').textContent,'0:30');t.fire('pointerdown');t.fire('input',80);t.c.refreshSeek();assert.equal(t.calls.length,0,'Drag previews without buffering streams');assert.equal(t.$('#art-seek').value,80);t.fire('change');assert.deepEqual(t.calls,[['seek',80,true]]);assert.equal(t.p.state,1);
 t.p.t=84;t.c.refreshSeek();assert.equal(t.$('#seek').value,84,'Focused sliders keep following playback after commit');
}
{
 const t=setup();t.p.state=2;t.c.mainIntent.wantsPlay=false;t.fire('input',70);t.fire('change');assert.deepEqual(t.calls,[['seek',70,true],['pause']]);assert.equal(t.p.state,2);
 for(const state of [-1,0,3,5]){t.p.state=state;t.calls.length=0;t.c.refreshSeek();assert(t.$('#seek').disabled);t.fire('input',45);t.fire('change');assert.equal(t.calls.length,0,'Nonplaying states never start playback via seek')}
}
for(const duration of [0,NaN,Infinity,-5]){const t=setup();t.p.d=duration;t.c.refreshSeek();assert(t.$('#seek').disabled);t.fire('input',45);t.fire('change');assert.equal(t.calls.length,0)}
for(const cancel of ['pointercancel','blur']){const t=setup();t.fire('pointerdown');t.fire('input',70);t.fire(cancel);t.fire('change');assert.equal(t.calls.length,0);assert.equal(t.$('#seek').value,30)}
for(const update of [t=>t.c.playbackIntent++,t=>t.p.video='stale',t=>t.c.sourceActive=true,t=>t.c.inlinePlaybackLocked=true]){const t=setup();t.fire('pointerdown');t.fire('input',70);update(t);t.fire('change');assert.equal(t.calls.length,0,'Stale owner/track gesture rejected')}
{
 const t=setup();t.c.albumPlaybackLocked=true;t.c.albumSession={ready:true,failed:false,player:t.p};t.fire('input',40);t.fire('change');assert.deepEqual(t.calls,[['seek',40,true]]);t.calls.length=0;t.fire('pointerdown');t.fire('input',80);t.p.index++;t.fire('change');assert.equal(t.calls.length,0,'Album item changes cancel drag');t.c.albumSession=null;t.c.refreshSeek();assert(t.$('#seek').disabled);
}
{
 const t=setup();t.fire('input',40);t.fire('change');assert(t.c.ignoreSeekEnd(t.p));t.p.t=120;assert(!t.c.ignoreSeekEnd(t.p));t.c.playbackIntent++;t.p.t=40;assert(!t.c.ignoreSeekEnd(t.p));
}
{
 const t=setup();t.c.songs[0].youtube={id:'video1',startSeconds:20,endSeconds:90};t.c.refreshSeek();assert.equal(t.$('#seek').min,20);assert.equal(t.$('#seek').max,90);assert.equal(t.$('#duration').textContent,'1:10');t.fire('input',10);t.fire('change');assert.equal(t.calls[0][1],20);t.$('#auto').checked=true;t.c.playbackIntent++;t.p.t=91;t.c.refreshSeek();assert.deepEqual(t.calls.slice(-2),[['pause'],['next',1]],'Authored excerpt end remains enforced after seekTo');t.c.refreshSeek();assert.equal(t.calls.filter(x=>x[0]==='next').length,1);
}
assert(fs.readFileSync('templates/index.html','utf8').includes('id="art-seek"'));console.log('Seek PASS: shared preview/commit, paused/no-autoplay, unknown duration, cancellation, stale owners/video, album index, excerpt boundary, post-seek end guard.');
