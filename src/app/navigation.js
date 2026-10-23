 const pageRegistry=window.CRATE_PAGES||{};
 const pageByPath=new Map(Object.values(pageRegistry).map(p=>[p.path,p]));
 const browseKeys=['q','region','era','producer','connection','sound','research','sort','collection','coast'];
 const campaignKeys=['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','dclid','gbraid','wbraid'];
 const initialMetadata=window.CRATE_INITIAL_META;
 const metadataCache=new Map(initialMetadata?[[initialMetadata.route,initialMetadata.jsonld]]:[]);
 let metadataRequest=0;

 function normalizeRoute(value){return value==='#/features'?'#/artists':value==='#/feature/tribe-production'?'#/feature/tribe':value;}
 function routeFromURL(url){
  if(url.hash.startsWith('#/'))return normalizeRoute(url.hash);
  const path=url.pathname.replace(/\/index\.html$/,'/');
  const page=pageByPath.get(path);
  if(!page)return null;
  if(page.route==='#/timeline'){const params=new URLSearchParams();for(const key of window.CrateExplorer.keys)if(url.searchParams.has(key))params.set(key,url.searchParams.get(key));return page.route+(params.size?'?'+params.toString():'')}
  if(page.route==='#/'||page.route==='#/songs'){
   const params=new URLSearchParams();for(const key of browseKeys)if(url.searchParams.has(key))params.set(key,url.searchParams.get(key));
   if(params.size)return page.route+'?'+params.toString();
  }
  return page.route;
 }
 function currentRoute(){return routeFromURL(new URL(location.href))||window.INITIAL_ROUTE||'#/';}
 function routeURL(value){
  value=normalizeRoute(value);
  if(value.startsWith('#/timeline?'))return pageRegistry['#/timeline'].path+'?'+value.slice(11);
  if(value.startsWith('#/?'))return pageRegistry['#/'].path+'?'+value.slice(3);
  if(value.startsWith('#/songs?'))return pageRegistry['#/songs'].path+'?'+value.slice(8);
  return pageRegistry[value]?.path||pageRegistry['#/'].path;
 }
 function replaceBrowseRoute(value){
  const url=new URL(routeURL(value),location.origin),old=new URL(location.href);
  for(const key of campaignKeys)if(old.searchParams.has(key))url.searchParams.set(key,old.searchParams.get(key));
  history.replaceState({...history.state,crateRoute:value},'',url.pathname+url.search);
 }
 function navigate(value,{replace=false}={}){
  rememberBrowse();
  history[replace?'replaceState':'pushState'](replace?{...history.state,crateRoute:value}:{crateRoute:value},'',routeURL(value));
  route();
 }
 function linkRoutes(root=document){
  root.querySelectorAll('a[href^="#/"]').forEach(a=>a.setAttribute('href',routeURL(a.getAttribute('href'))));
 }
 function setMeta(name,value,property=false){
  const attribute=property?'property':'name';
  const matches=[...document.head.querySelectorAll('meta['+attribute+'="'+name+'"]')];
  const element=matches.shift()||document.createElement('meta');
  for(const duplicate of matches)duplicate.remove();
  element.setAttribute(attribute,name);element.content=value;document.head.append(element);
 }
 function setStructuredData(data,key){
  document.querySelectorAll('script[type="application/ld+json"]').forEach(x=>x.remove());
  const script=document.createElement('script');script.type='application/ld+json';script.textContent=JSON.stringify(data);document.head.append(script);
  document.documentElement.dataset.metadataRoute=key;
 }
 function updateMetadata(value){
  const key=value.startsWith('#/timeline?')?'#/timeline':value.startsWith('#/songs?')?'#/songs':value.startsWith('#/?')?'#/':normalizeRoute(value),p=pageRegistry[key];
  if(!p)return;
  const request=++metadataRequest;
  document.title=p.title;
  const canonical=document.querySelector('link[rel="canonical"]')||document.createElement('link');canonical.rel='canonical';canonical.href=p.url;document.head.append(canonical);
  setMeta('description',p.description);setMeta('author','DJ Naoyaman');setMeta('robots','index,follow,max-image-preview:large');
  for(const [name,text] of Object.entries({'og:title':p.title,'og:description':p.description,'og:url':p.url,'og:type':p.kind,'og:site_name':'CRATEDIGGIN\'','og:locale':'ja_JP','og:image':p.image,'og:image:type':'image/jpeg','og:image:width':'1200','og:image:height':'630','og:image:alt':p.imageAlt||p.title}))setMeta(name,text,true);
  document.head.querySelectorAll('meta[property^="article:"]').forEach(x=>x.remove());
  if(p.kind==='article'){
   setMeta('article:author',pageRegistry['#/editor'].url,true);
   if(p.published)setMeta('article:published_time',p.published,true);
   if(p.modified)setMeta('article:modified_time',p.modified,true);
  }
  for(const [name,text] of Object.entries({'twitter:card':'summary_large_image','twitter:title':p.title,'twitter:description':p.description,'twitter:image':p.image,'twitter:image:alt':p.imageAlt||p.title}))setMeta(name,text);
  document.querySelectorAll('link[rel="alternate"][type="text/markdown"]').forEach(x=>x.remove());
  if(key.startsWith('#/song/')){const alternate=document.createElement('link');alternate.rel='alternate';alternate.type='text/markdown';alternate.href=p.url.replace(/\.html$/,'.md');document.head.append(alternate);}
  if(metadataCache.has(key)){setStructuredData(metadataCache.get(key),key);return;}
  document.querySelectorAll('script[type="application/ld+json"]').forEach(x=>x.remove());
  delete document.documentElement.dataset.metadataRoute;
  fetch(p.metadataPath+'?v='+encodeURIComponent(window.CRATE_RELEASE?.version||''))
   .then(response=>{if(!response.ok)throw Error('Metadata unavailable');return response.json();})
   .then(data=>{metadataCache.set(key,data.jsonld);if(request===metadataRequest)setStructuredData(data.jsonld,key);})
   .catch(()=>{});
 }
 function trackInteraction(name,params={}){
  // Only public catalog IDs and fixed action values; never names typed into MY CRATE or search text.
  try{if(typeof window.gtag==='function')window.gtag('event',name,params);}catch(_){}
 }
 function articleByline(value){
  const p=pageRegistry[value];
  if(!p)return '';
  return '<div class="byline">選曲・編集・文責 <a href="'+routeURL('#/editor')+'">DJ Naoyaman</a>'+
   (p.published?' · 公開 <time datetime="'+esc(p.published)+'">'+esc(p.published.slice(0,10))+'</time>':'')+
   (p.modified?' · 更新 <time datetime="'+esc(p.modified)+'">'+esc(p.modified.slice(0,10))+'</time>':'')+'</div>';
 }
 function sharingPage(value){const p=pageRegistry[value.startsWith('#/timeline?')?'#/timeline':value.startsWith('#/songs?')?'#/songs':value.startsWith('#/?')?'#/':normalizeRoute(value)];return p&&value.startsWith('#/timeline?')?{...p,url:new URL(routeURL(value),location.origin).href}:p;}
 function shareLinks(p){
  const u=encodeURIComponent(p.url),t=encodeURIComponent(p.title),line=encodeURIComponent(p.title+'\n'+p.url);
  return [['X','https://x.com/intent/tweet?text='+t+'&url='+u],['Facebook','https://www.facebook.com/sharer/sharer.php?u='+u],['LINE','https://line.me/R/share?text='+line]];
 }
 async function copyPageLink(value,button){
  const p=sharingPage(value);if(!p)return;
  const host=button.closest('.page-sharing')||button.parentElement,status=host.querySelector('[role="status"]');
  try{await navigator.clipboard.writeText(p.url);trackInteraction('share',{method:'copy_link',content_type:value.startsWith('#/song/')?'song':'page',item_id:value.startsWith('#/timeline')?'timeline':value.split('/').pop()});if(status)status.textContent='リンクをコピーしました';else button.textContent='コピーしました';}
  catch(_){let input=host.querySelector('.share-fallback-url');if(!input){input=document.createElement('input');input.className='share-fallback-url';input.readOnly=true;input.setAttribute('aria-label','コピーする共有リンク');host.append(input);}input.value=p.url;input.focus();input.select();if(status)status.textContent='リンクを選択してコピーしてください';}
 }
 function sharingControls(value){
  const p=sharingPage(value);if(!p)return null;
  const host=document.createElement('nav');host.className='page-sharing';host.setAttribute('aria-label','このページをシェア');
  const label=document.createElement('span');label.className='share-label';label.textContent='SHARE THIS PAGE';host.append(label);
  for(const [name,url] of shareLinks(p)){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=name;a.setAttribute('aria-label',name+'でこのページをシェア（新しいタブ）');host.append(a);}
  const copy=document.createElement('button');copy.type='button';copy.textContent='リンクをコピー';copy.onclick=()=>copyPageLink(value,copy);host.append(copy);
  if(typeof navigator.share==='function'){const native=document.createElement('button');native.type='button';native.textContent='その他に共有';native.onclick=async()=>{try{await navigator.share({title:p.title,url:p.url});}catch(e){if(e.name!=='AbortError')await copyPageLink(value,copy);}};host.append(native);}
  const status=document.createElement('span');status.className='share-status';status.setAttribute('role','status');status.setAttribute('aria-live','polite');host.append(status);return host;
 }
 function addPageSharing(value){
  if(!sharingPage(value))return;
  document.querySelectorAll('.page-sharing').forEach(n=>n.remove());
  document.querySelector('footer')?.append(sharingControls(value));
  if(value.startsWith('#/song/')||value.startsWith('#/feature/')){
   const article=view.querySelector('article')||view;article.append(sharingControls(value));
   if(value.startsWith('#/feature/')&&!view.querySelector('.byline')){const b=document.createElement('div');b.innerHTML=articleByline(value);view.querySelector('h1')?.after(b);}
  }
 }
 document.addEventListener('click',event=>{
  if(event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
  const anchor=event.target.closest('a[href]');
  if(!anchor||anchor.target||anchor.hasAttribute('download'))return;
  const url=new URL(anchor.href,location.href);
  if(url.origin!==location.origin||(url.hash&&!url.hash.startsWith('#/')))return;
  const next=routeFromURL(url);if(!next)return;
  event.preventDefault();navigate(next);
 });
 addEventListener('popstate',route);

