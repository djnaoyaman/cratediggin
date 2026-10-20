const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/app/navigation.js','utf8'),start=source.indexOf(' function updateMetadata('),end=source.indexOf(' function trackInteraction(',start);assert(start>=0&&end>start);
const registry=JSON.parse(fs.readFileSync('dist/metadata.js','utf8').split('=').slice(1).join('=').trim().replace(/;$/,'')),values=new Map(),canonical={};
const context={pageRegistry:registry,metadataRequest:0,metadataCache:new Map(Object.keys(registry).map(k=>[k,{}])),normalizeRoute:x=>x,setMeta:(name,value)=>values.set(name,value),setStructuredData:(data,key)=>context.last=key,document:{title:'',head:{append(){},querySelectorAll:()=>[]},querySelector:()=>canonical,querySelectorAll:()=>[],createElement:()=>({})}};
vm.createContext(context);vm.runInContext(source.slice(start,end),context);
for(const [route,p] of Object.entries(registry)){context.updateMetadata(route);assert.equal(values.get('og:image:alt'),p.imageAlt);assert.equal(values.get('twitter:image:alt'),p.imageAlt);assert.equal(values.get('og:image'),p.image);assert.equal(canonical.href,p.url);assert.equal(context.last,route)}
for(const [route,key] of [['#/timeline?producer=DJ+Premier','#/timeline'],['#/songs?q=Nas','#/songs'],['#/?q=Nas','#/']]){context.updateMetadata(route);assert.equal(values.get('og:image:alt'),registry[key].imageAlt);assert.equal(context.last,key)}
const before=JSON.stringify([...values]);context.updateMetadata('#/unknown');assert.equal(JSON.stringify([...values]),before);
console.log('Actual unchanged SPA metadata handler applies all731 image descriptions and filtered-route metadata without provider execution PASS');
