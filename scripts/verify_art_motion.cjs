const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/assets/art.js','utf8');
function harness(reduced=false){
 const calls=[],frames=new Map();let frameId=0;
 const gradient={addColorStop(){}};
 const context=record=>new Proxy({measureText:t=>({width:t.length*20}),createLinearGradient:()=>gradient,createRadialGradient:()=>gradient},{get:(o,k)=>k in o?o[k]:(...args)=>{if(record)calls.push([k,...args])},set:(o,k,v)=>{o[k]=v;if(record&&k==='globalAlpha')calls.push([k,v]);return true}});
 const ctx=context(true),canvas={style:{},getContext:()=>ctx,getBoundingClientRect:()=>({width:884,height:464})};
 const room={dataset:{},classList:{toggle(){}}},semantic={removeAttribute(){}};
 class Photo{constructor(){this.complete=true;this.naturalWidth=1200;this.naturalHeight=600;this.photo=true}set src(v){this.url=v}}
 const c={window:{CRATE_SITE_URL:'https://example.com/cratediggin'},document:{getElementById:id=>id==='wall'?canvas:id==='artwork-image'?semantic:room,createElement:()=>({getContext:()=>context(false)}),addEventListener(){}},Image:Photo,URL,matchMedia:()=>({matches:reduced}),devicePixelRatio:1,innerWidth:1200,innerHeight:800,performance:{now:()=>1000},requestAnimationFrame:fn=>{frames.set(++frameId,fn);return frameId},cancelAnimationFrame:id=>frames.delete(id),addEventListener(){}};
 vm.runInNewContext(source,c);
 return {api:c.window.CrateArt,calls,frames,room,step(ts){const current=[...frames.values()];frames.clear();calls.length=0;current.forEach(fn=>fn(ts))}};
}
const durations={drift:6200,groove:3900,stomp:2600,burst:1500};
function song(mode,variant=0){return {id:mode,title:mode,artist:'Artist',art:{image:'assets/graffiti/test.webp',transparent:true,palette:['#b55a40','#f0e0b0','#292929'],seed:37,motion:{mode,duration:durations[mode],variant}}}}
const signatures=[];
for(const mode of Object.keys(durations)){
 const t=harness();t.api.show(song(mode));assert.equal(t.room.dataset.motion,mode);t.step(1000+durations[mode]/2);
 const names=t.calls.map(c=>c[0]);signatures.push(JSON.stringify(names));
 assert(t.calls.some(c=>c[0]==='drawImage'&&c[1]?.photo),'The actual configured artwork must be drawn');
 if(mode==='drift')assert(t.calls.some(c=>c[0]==='globalAlpha'&&c[1]>0&&c[1]<1));
 if(mode==='groove')assert.equal(names.filter(n=>n==='rect').length,8);
 if(mode==='stomp')assert.equal(names.filter(n=>n==='rect').length,5);
 if(mode==='burst')assert(names.includes('arc'));
 t.step(1000+durations[mode]+10);assert.equal(t.frames.size,0,'Completed entrances must settle');t.api.hide();
}
assert.equal(new Set(signatures).size,4,'All tension families need different rendering paths');
const groove=[];
for(let v=0;v<4;v++){const t=harness();t.api.show(song('groove',v));t.step(2950);groove.push(JSON.stringify(t.calls.filter(c=>['rect','moveTo','lineTo'].includes(c[0]))));}
assert.equal(new Set(groove).size,4,'Neutral groove still needs four distinct gestures');
for(const mode of Object.keys(durations)){const t=harness(true);t.api.show(song(mode));assert.equal(t.frames.size,0);assert(!t.calls.some(c=>c[0]==='clip'),'Reduced motion must show completed art immediately');}
const t=harness();assert.equal(t.api.motionFor(song('drift')).duration,6200);assert.equal(t.api.motionFor({art:{motion:{mode:'unknown',duration:-50}}}).mode,'groove');assert.equal(t.api.motionFor({art:{motion:{mode:'burst',duration:99999}}}).duration,8000);
console.log('Four tension reveals, four groove gestures, completion and reduced-motion behavior passed');

if(fs.existsSync('dist/tracks.js')){const window={};vm.runInNewContext(fs.readFileSync('dist/tracks.js','utf8'),{window});const bounds={drift:[5600,7000],groove:[3200,4600],stomp:[2200,3000],burst:[1200,1800]},modes=new Set();for(const track of window.TRACKS){const m=track.art.motion;assert(m&&bounds[m.mode],track.id+' missing editorial motion');assert.equal(m.basis,'editorial-cues');assert(m.duration>=bounds[m.mode][0]&&m.duration<=bounds[m.mode][1]);assert(m.variant>=0&&m.variant<=3);modes.add(m.mode)}assert.equal(modes.size,4);console.log(window.TRACKS.length+' generated tracks have bounded editorial motion plans');}
