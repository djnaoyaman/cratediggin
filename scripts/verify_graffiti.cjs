const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const manifest=JSON.parse(fs.readFileSync('graffiti_artwork.json','utf8'));
const {window}=vm.runInNewContext(fs.readFileSync('dist/tracks.js','utf8')+';({window})',{window:{}});
const path=require('node:path');
function verifyCredits(dir){for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const file=path.join(dir,entry.name);if(entry.isDirectory())verifyCredits(file);else if(file.endsWith('.html')){const html=fs.readFileSync(file,'utf8');if(html.includes('id="art-view"'))assert.match(html,/<span class="art-credit">Designed by DJ Naoyaman<\/span>/,'Missing graffiti credit: '+file)}}}
verifyCredits('dist');
const ready=manifest.tracks.filter(t=>t.status==='ready');assert(ready.length>=3);
for(const t of window.TRACKS)assert.equal(t.art.alt,t.title+' — '+t.artist+'｜CRATE DIGGIN｜DJ Naoyaman');
for(const a of ready){const t=window.TRACKS.find(t=>t.id===a.id);assert(t&&t.art.image===a.image);assert(a.textReviewed&&a.paletteReviewed);assert(fs.statSync(a.image).size>10000);assert(fs.existsSync('dist/'+a.image));assert.deepEqual(a.palette,Array.from(t.art.palette));assert.equal(a.paletteSource,t.art.paletteSource)}
// Actual art API: image URLs, asynchronous loading, late load, resize, song changes,
// image-fit bounds and hide while loading. No remote player is needed here.
const frames=[],listeners={},images=[],drawn=[];let clock=1000;
const gradient={addColorStop(){}};
const ctx=new Proxy({drawImage(...args){drawn.push(args)},measureText(s){return {width:s.length*20}},createLinearGradient(){return gradient},createRadialGradient(){return gradient}},{get:(o,k)=>k in o?o[k]:()=>{}});
const canvas={getContext:()=>ctx,style:{}};
const semantic={alt:'',hidden:true,removeAttribute(){}};
const classes=new Set(),art={classList:{toggle:(name,on)=>on?classes.add(name):classes.delete(name)}};
class FakeImage{constructor(){images.push(this);this.complete=false;this.naturalWidth=1672;this.naturalHeight=941}set src(v){this.url=v}load(){this.complete=true;this.onload()}}
const c={window:{CRATE_SITE_URL:'https://djnaoyaman.github.io/cratediggin'},document:{getElementById:id=>id==='wall'?canvas:id==='artwork-image'?semantic:art,createElement:()=>({...canvas}),addEventListener:(name,fn)=>listeners[name]=fn},Image:FakeImage,URL,matchMedia:()=>({matches:false}),devicePixelRatio:1,innerWidth:390,innerHeight:844,performance:{now:()=>clock},requestAnimationFrame:fn=>{frames.push(fn);return frames.length},cancelAnimationFrame(){},addEventListener:(name,fn)=>listeners[name]=fn,setTimeout:fn=>fn()};
vm.createContext(c);vm.runInContext(fs.readFileSync('src/assets/art.js','utf8'),c);
const song=window.TRACKS.find(t=>t.id==='mass-appeal');c.window.CrateArt.show(song);assert(classes.has('image-art'));assert(images[0].url.endsWith('/cratediggin/'+song.art.image));assert.equal(semantic.alt,'Mass Appeal — Gang Starr｜CRATE DIGGIN｜DJ Naoyaman');
clock=3000;frames.shift()(clock);images[0].load();frames.pop()(clock+50);assert(drawn.length);
let args=drawn.at(-1);assert(args[3]<=390&&args[4]<=844);assert(args[1]>=0&&args[2]>=0);
const before=drawn.length;c.innerWidth=1280;c.innerHeight=720;listeners.resize();assert(drawn.length>before);args=drawn.at(-1);assert(args[3]<=1280&&args[4]<=720);
const switchedAt=drawn.length;
c.window.CrateArt.change(window.TRACKS.find(t=>t.id==='can-i-kick-it'));assert.equal(images.length,2);assert.equal(semantic.alt,'Can I Kick It? — A Tribe Called Quest｜CRATE DIGGIN｜DJ Naoyaman');
assert(drawn.length>switchedAt,'Switch must repaint the wall synchronously');
assert(drawn.slice(switchedAt).every(args=>args[0]!==images[0]),'Previous artwork must not flash while the current image loads');
c.window.CrateArt.hide();const count=frames.length;images[1].load();assert.equal(frames.length,count,'Hidden artwork must not restart rendering');
ctx.fillText=()=>{throw new Error('Configured artwork must not flash legacy lettering')};
c.window.CrateArt.show(song);c.window.CrateArt.change(window.TRACKS.find(t=>t.id==='can-i-kick-it'));
images[1].onerror();frames.pop()(clock+100);
assert(classes.has('image-art'),'Failed image must keep its own wall instead of the legacy artwork');
c.window.CrateArt.hide();
console.log(ready.length+' cover-colored assets, generated-art switching, late loading, contain sizing, resize and hidden-state behavior verified');
