const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.resolve(process.env.TEST_SOURCE||'.'),read=p=>fs.readFileSync(path.join(root,p),'utf8'),source=read('src/app/catalog-ui.js');
assert(!/resultPage|pageSize|makePager|data-page-next|data-page-prev/.test(source));assert(source.includes('queueScope=filtered.map(t=>t.id)'));assert(source.includes('playSelection(filtered,customMode)'));assert(source.includes("$('#count').textContent=filtered.length+' / '+songs.length+' RECORDS'"));assert(read('src/app/router.js').includes('resultLimit=restoredResultLimit(browseRestoring)'));assert(read('src/app/router.js').includes('stopResultsLoading();activeBrowseRoute=null;'));assert(read('src/app/playlist-ui.js').includes("if(link.parentElement?.classList.contains('record-row'))return"));
const snippet=source.slice(source.indexOf(' let stopResultsLoading'),source.indexOf(' function paintResults'));
for(const mode of ['observer','unavailable','throwing']){
 const frames=new Map(),listeners=new Map();let token=0,remembered=0,disconnected=0,observer;
 const host={isConnected:true,ids:Array.from({length:36},(_,i)=>'t'+i),attrs:{},setAttribute(k,v){this.attrs[k]=v},append(e){this.end=e},addEventListener(){},removeEventListener(){}};
 const end={top:10000,setAttribute(k,v){this[k]=v},getBoundingClientRect(){return{top:this.top}},insertAdjacentHTML(where,html){assert.equal(where,'beforebegin');host.ids.push(...html.split('|').filter(Boolean));this.top+=3600}};
 const context={RESULT_CHUNK_SIZE:36,resultLimit:36,innerHeight:900,document:{createElement:()=>end},requestAnimationFrame:fn=>{frames.set(++token,fn);return token},cancelAnimationFrame:id=>frames.delete(id),addEventListener:(name,fn)=>listeners.set(name,fn),removeEventListener:(name,fn)=>{if(listeners.get(name)===fn)listeners.delete(name)},workUnit:()=> '曲',card:x=>x.id+'|',bindPlaylistRows:()=>{},linkRoutes:()=>{},rememberBrowse:()=>remembered++};
 if(mode==='observer')context.IntersectionObserver=class{constructor(fn,opts){observer=this;this.callback=fn;assert.equal(opts.rootMargin,'600px 0px')}observe(e){assert.equal(e,end)}disconnect(){disconnected++}};
 if(mode==='throwing')context.IntersectionObserver=class{constructor(){throw new Error('Unavailable')}};
 const ctx=vm.createContext(context);vm.runInContext(snippet+';globalThis.api={watchResults,stop:()=>stopResultsLoading()}',ctx);const all=Array.from({length:582},(_,i)=>({id:'t'+i}));ctx.api.watchResults(host,all);assert.equal(frames.size,0);assert.match(end.textContent,/全582曲/);assert.equal(end.role,'status');assert.equal(end['aria-live'],'polite');
 const tick=()=>{const jobs=[...frames.values()];frames.clear();jobs.forEach(f=>f())};
 while(context.resultLimit<all.length){end.top=100;listeners.get('scroll')?.();listeners.get('scroll')?.();observer?.callback([{isIntersecting:true}]);assert.equal(frames.size,1,'Duplicate triggers must coalesce');assert.equal(host.attrs['aria-busy'],'true');tick();assert.equal(host.attrs['aria-busy'],'false');assert.deepEqual(host.ids,all.slice(0,context.resultLimit).map(t=>t.id))}
 assert.deepEqual(host.ids,all.map(t=>t.id));assert.equal(new Set(host.ids).size,582);assert.match(end.textContent,/すべての582曲/);assert.equal(listeners.size,0);assert(remembered>0);if(mode==='observer')assert(disconnected>0);
 // Repainting/navigating cancels a pending old append, including late observer events.
 context.resultLimit=36;host.ids=all.slice(0,36).map(t=>t.id);end.top=100;ctx.api.watchResults(host,all);assert.equal(frames.size,1);ctx.api.stop();assert.equal(frames.size,0);observer?.callback([{isIntersecting:true}]);tick();assert.equal(host.ids.length,36);assert.equal(listeners.size,0);
 console.log(mode+': all582 IDs exact/order, one-frame batching, accessible state, fallback and stale-load cleanup PASS');
}
console.log('Continuous scroll source contracts and runtime model PASS (not a browser rendering test)');
