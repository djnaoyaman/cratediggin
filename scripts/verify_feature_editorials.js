// Check real feature selection and rendered routes, including alias grouping.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const songs=JSON.parse(fs.readFileSync('tracks.json','utf8'));
const source=JSON.parse(fs.readFileSync('features.json','utf8'));
const app=fs.readFileSync('dist/app.js','utf8');
const view={innerHTML:'',querySelectorAll:()=>[]},canonical={href:''};
const ctx=vm.createContext({songs,view,document:{title:''},origin:'https://djnaoyaman.github.io/cratediggin',esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;'),top:()=>'',playableIds:s=>s.map(t=>t.id),paintResults:()=>{},$:()=>canonical});
vm.runInContext(app.slice(app.indexOf(' function yearLabel('),app.indexOf(' const songs='))+'let customMode,applyListFilters,filtered,queue,resultPage;const browseRestoring=null;'+app.slice(app.indexOf(' const features=['),app.indexOf(' let lastAnalyticsPage'))+';globalThis.api={features,featureTracks,eligibleFeatures,featurePage};',ctx);
const api=ctx.api,eligible=api.eligibleFeatures();
assert.equal(eligible.length,source.features.length);
assert.equal(new Set(eligible.flatMap(f=>Array.from(f.aliases||[]))).size,eligible.reduce((n,f)=>n+(f.aliases||[]).length,0));
api.featurePage();assert(view.innerHTML.includes('3曲以上'));assert(view.innerHTML.includes('同一人物'));
for(const f of eligible){
 const selected=api.featureTracks(f);assert(selected.length>=3);
 assert.equal(selected.length,new Set(Array.from(selected,t=>t.id)).size,'Duplicate tracks in '+f.id);
 api.featurePage(f.id);
 for(const key of ['context','legacy','listening','connections'])assert(view.innerHTML.includes(f.editorial[key]));
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
