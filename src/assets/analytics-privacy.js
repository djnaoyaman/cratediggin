/* Public route attribution only. Never send search text, hashes, names or unknown parameters. */
window.CrateAnalyticsURL=function(value,campaigns=false){try{const u=new URL(value,location.origin);const clean=new URL(u.origin+u.pathname);if(campaigns)for(const key of ['utm_source','utm_medium','utm_campaign','gclid','dclid','gbraid','wbraid']){const v=u.searchParams.get(key);if(v&&/^[A-Za-z0-9_-]{1,160}$/.test(v))clean.searchParams.set(key,v)}return clean.href}catch(_){return location.origin+location.pathname}};
window.CrateAnalyticsReferrer=function(value){if(!value)return '';try{const u=new URL(value);return u.origin===location.origin?window.CrateAnalyticsURL(value):u.origin+'/'}catch(_){return ''}};

/* Additive events: keep transport, queues, player ownership and existing analytics intact. */
(()=>{
 if(window.CrateInteractionEvents)return;
 const schemas={sample_playback_start:['song_id'],select_filter:['filter_key'],select_listening_shelf:['shelf_id'],art_open:[]};
 function track(name,values={}){try{if(location.hostname!=='djnaoyaman.github.io'||!schemas[name]||typeof window.gtag!=='function')return;const p={send_to:'G-71ENPHWEJH',transport_type:'beacon'};for(const k of schemas[name]){const v=values[k];if(typeof v==='string'&&/^[a-zA-Z0-9_-]{1,100}$/.test(v))p[k]=v;}window.gtag('event',name,p);}catch{}}
 window.CrateInteractionEvents={track};
 document.addEventListener('change',e=>{const el=e.target;if(e.isTrusted&&el?.tagName==='SELECT'&&['region','era','producer','connection','sound','research','sort'].includes(el.id))track('select_filter',{filter_key:el.id});});
 document.addEventListener('click',e=>{if(!e.isTrusted||e.button!==0)return;const b=e.target.closest?.('[data-crate],#art-open');if(!b)return;if(b.hasAttribute('data-crate'))track('select_listening_shelf',{shelf_id:b.dataset.crate});else if(document.getElementById('art-view')?.hidden===false)track('art_open');});
 const states=new WeakMap();
 window.addEventListener('message',e=>{
  if(!['https://www.youtube.com','https://www.youtube-nocookie.com'].includes(e.origin))return;
  const frame=document.getElementById('sample-yt');if(!frame?.contentWindow||e.source!==frame.contentWindow)return;
  let data;try{data=typeof e.data==='string'?JSON.parse(e.data):e.data;}catch{return;}
  const state=data?.event==='onStateChange'?data.info:data?.event==='infoDelivery'?data.info?.playerState:undefined;
  if(![0,1,2,3,5,-1].includes(state))return;
  const prior=states.get(frame);states.set(frame,state);if(state!==1||prior===1)return;
  const id=location.pathname.match(/\/tracks\/([a-zA-Z0-9_-]+)\.html$/)?.[1];track('sample_playback_start',{song_id:id});
 });
})();
