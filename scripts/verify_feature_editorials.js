// Check real feature selection and rendered routes, including alias grouping.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const songs=JSON.parse(fs.readFileSync('tracks.json','utf8'));
const source=JSON.parse(fs.readFileSync('features.json','utf8'));
const app=fs.readFileSync('dist/app.js','utf8');
const view={innerHTML:'',querySelectorAll:()=>[]},canonical={href:''};
const ctx=vm.createContext({songs,view,document:{title:''},origin:'https://djnaoyaman.github.io/cratediggin',esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),top:()=>'',playableIds:s=>s.map(t=>t.id),paintResults:()=>{},scopePersonQueue:()=>{},$:selector=>['#back-to-top','#enter-crate'].includes(selector)?null:canonical});
vm.runInContext(app.slice(app.indexOf(' function yearLabel('),app.indexOf(' const songs='))+'let customMode,applyListFilters,filtered,queue,resultLimit;const RESULT_CHUNK_SIZE=36,browseRestoring=null;const restoredResultLimit=()=>RESULT_CHUNK_SIZE;'+app.slice(app.indexOf(' const features=['),app.indexOf(' let lastAnalyticsPage'))+';globalThis.api={features,featureTracks,featureIdentity,publishedFeatures,eligibleFeatures,featurePage};',ctx);
const api=ctx.api,eligible=api.eligibleFeatures();
assert.equal(eligible.length,source.features.length-1);assert.equal(api.publishedFeatures().length,source.features.length);assert(!eligible.some(f=>f.id==='az'));
assert.equal(new Set(eligible.flatMap(f=>Array.from(f.aliases||[]))).size,eligible.reduce((n,f)=>n+(f.aliases||[]).length,0));
api.featurePage();assert(view.innerHTML.includes('5曲以上'));assert(view.innerHTML.includes('8曲以上'));
for(const f of api.publishedFeatures()){
 const selected=api.featureTracks(f);if(f.id==='az')assert.equal(selected.length,4);else assert(Math.max(f.qualification.artistCount,f.qualification.producerCount)>=5);if(f.id==='beastie-boys'){assert.equal(selected.length,10);const included=selected.find(t=>t.id==='beastie-boys-get-it-together');assert(included&&api.featureIdentity(f,included),'Explicit primary billing belongs to own scope');}
 assert.equal(selected.length,new Set(Array.from(selected,t=>t.id)).size,'Duplicate tracks in '+f.id);
 api.featurePage(f.id);assert(!view.innerHTML.includes('掲載3曲以上'));assert(view.innerHTML.includes('音楽性と制作背景を、収録作品からたどる特集。'));
 if(f.editorial.format==='source-led-v1'){for(const sec of f.editorial.sections)assert(view.innerHTML.includes(sec.heading));assert(!view.innerHTML.includes('DJ NAOYAMAN’S VIEW'));}else for(const key of ['context','legacy','listening','connections'])assert(view.innerHTML.includes(f.editorial[key]));
 for(const r of f.editorial.sources)assert(view.innerHTML.includes(r.url));
 const html=fs.readFileSync('dist/'+(f.type==='artist'?'artists':'producers')+'/'+f.id+'.html','utf8');
 const songCount=selected.filter(t=>(t.workType||'single')==='single').length,mixCount=selected.filter(t=>t.workType==='mix').length,videoCount=selected.filter(t=>t.workType==='live_video').length,countLabel=songCount+'曲'+(mixCount?'・'+mixCount+'ミックス作品':'')+(videoCount?'・'+videoCount+'ライブ映像':'');
 assert(html.includes('収録作品 '+countLabel),f.id+': static/client count mismatch');
 assert(view.innerHTML.includes(countLabel),f.id+': client work count mismatch');
 assert(html.includes(f.editorial.title));assert(html.includes('#/feature/'+f.id));
 console.log(f.name+': '+selected.length+' tracks, editorial and static route verified');
}
for(const [id,aliases] of [['j-dilla',['J Dilla','Jay Dee']],['madlib',['Madlib','Quasimoto']]]){
 const f=eligible.find(f=>f.id===id),ids=new Set(Array.from(api.featureTracks(f),t=>t.id));
 for(const t of songs.filter(t=>aliases.includes(t.artist)))assert(ids.has(t.id),'Alias track omitted: '+t.id);
 assert(f.identityNote.includes('共同プロジェクト'));
}
// An under-threshold artist cannot be opened by manually guessing a route.
vm.runInContext("features.push({id:'below-threshold',type:'artist',names:['MF DOOM'],allYears:true,editorial:{}});",ctx);
assert(!api.eligibleFeatures().some(f=>f.id==='below-threshold'));
api.featurePage('below-threshold');assert(view.innerHTML.includes('DEEP IN THE CRATE.'));
console.log('Eligibility, alias coverage, project distinctions and all rendered editorial routes verified');
