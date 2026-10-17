 const pageRegistry=window.CRATE_PAGES||{};
 const pageByPath=new Map(Object.values(pageRegistry).map(p=>[p.path,p]));
 const browseKeys=['q','region','era','producer','connection','sound','research','sort','collection','coast'];
 const campaignKeys=['utm_source','utm_medium','utm_campaign','utm_content','utm_term','gclid','dclid','gbraid','wbraid'];
 const initialMetadata=window.CRATE_INITIAL_META;
 const metadataCache=new Map(initialMetadata?[[initialMetadata.route,initialMetadata.jsonld]]:[]);
 let metadataRequest=0;

 function normalizeRoute(value){return value==='#/feature/tribe-production'?'#/feature/tribe':value;}
 function routeFromURL(url){
  if(url.hash.startsWith('#/'))return normalizeRoute(url.hash);
  const path=url.pathname.replace(/\/index\.html$/,'/');
  const page=pageByPath.get(path);
  if(!page)return null;
  if(page.route==='#/'||page.route==='#/songs'){
   const params=new URLSearchParams();for(const key of browseKeys)if(url.searchParams.has(key))params.set(key,url.searchParams.get(key));
   if(params.size)return '#/?'+params.toString();
  }
  return page.route;
 }
 function currentRoute(){return routeFromURL(new URL(location.href))||window.INITIAL_ROUTE||'#/';}
 function routeURL(value){
  value=normalizeRoute(value);
  if(value.startsWith('#/?'))return pageRegistry['#/songs'].path+'?'+value.slice(3);
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
  const key=value.startsWith('#/?')?'#/songs':normalizeRoute(value),p=pageRegistry[key];
  if(!p)return;
  const request=++metadataRequest;
  document.title=p.title;
  const canonical=document.querySelector('link[rel="canonical"]')||document.createElement('link');canonical.rel='canonical';canonical.href=p.url;document.head.append(canonical);
  setMeta('description',p.description);setMeta('author','DJ Naoyaman');setMeta('robots','index,follow,max-image-preview:large');
  for(const [name,text] of Object.entries({'og:title':p.title,'og:description':p.description,'og:url':p.url,'og:type':p.kind,'og:site_name':'Crate Diggin’','og:locale':'ja_JP','og:image':p.image,'og:image:width':'1200','og:image:height':'630','og:image:alt':p.imageAlt||p.title}))setMeta(name,text,true);
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
  if(typeof window.gtag==='function')window.gtag('event',name,params);
 }
 function articleByline(value){
  const p=pageRegistry[value];
  if(!p)return '';
  return '<div class="byline">選曲・編集・文責 <a href="'+routeURL('#/editor')+'">DJ Naoyaman</a>'+
   (p.published?' · 公開 <time datetime="'+esc(p.published)+'">'+esc(p.published.slice(0,10))+'</time>':'')+
   (p.modified?' · 更新 <time datetime="'+esc(p.modified)+'">'+esc(p.modified.slice(0,10))+'</time>':'')+'</div>';
 }
 async function copyPageLink(value,button){
  const p=pageRegistry[value];if(!p)return;
  try{
   await navigator.clipboard.writeText(p.url);button.textContent='コピーしました';
   trackInteraction('share',{method:'copy_link',content_type:value.startsWith('#/song/')?'song':'feature',item_id:value.split('/').pop()});
  }catch(_){
   button.textContent='リンクを選択してコピー';const input=document.createElement('input');input.value=p.url;input.setAttribute('aria-label','共有リンク');button.after(input);input.select();
  }
 }
 function addPageSharing(value){
  if(!value.startsWith('#/song/')&&!value.startsWith('#/feature/'))return;
  const p=pageRegistry[value];if(!p)return;
  let host=view.querySelector('.share');
  if(!host){
   host=document.createElement('div');host.className='share';
   const button=document.createElement('button');button.type='button';button.textContent='特集のリンクをコピー';button.onclick=()=>copyPageLink(value,button);host.append(button);
   view.querySelector('h1')?.after(host);
   const byline=document.createElement('div');byline.innerHTML=articleByline(value);host.after(byline);
  }
  if(navigator.share){
   const button=document.createElement('button');button.type='button';button.textContent='共有する';
   button.onclick=async()=>{try{await navigator.share({title:p.title,text:p.description,url:p.url});trackInteraction('share',{method:'web_share',content_type:value.startsWith('#/song/')?'song':'feature',item_id:value.split('/').pop()});}catch(error){if(error.name!=='AbortError')await copyPageLink(value,button);}};
   host.append(button);
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
