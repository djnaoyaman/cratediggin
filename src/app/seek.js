 // One timeline for the ordinary player and all ART presentation modes.
 // Native range input supplies touch hit-testing, pointer capture and keyboard semantics.
 // https://developers.google.com/youtube/iframe_api_reference#seekTo
 let seekGesture=null,seekEndGuard=null,seekSegment=null;
 const seekControls=[['#seek','#elapsed','#duration'],['#art-seek','#art-elapsed','#art-duration']];
 const seekTime=n=>{n=Math.max(0,Math.floor(Number(n)||0));return Math.floor(n/60)+':'+String(n%60).padStart(2,'0')};
 function seekContext(){
  if(inlinePlaybackLocked||sourceActive||!songs[cur])return null;
  const album=albumPlaybackLocked,owner=album?albumSession:mainIntent,p=album?owner?.player:player;
  if(album?(!owner||!albumCurrent(owner)||!owner.ready||owner.failed):(!ready||!mainVideoMatches()))return null;
  try{
   const state=p?.getPlayerState?.(),duration=Number(p?.getDuration?.()),current=Number(p?.getCurrentTime?.());
   const video=p?.getVideoData?.()?.video_id||'',index=album?p?.getPlaylistIndex?.():null;
   const start=album?0:Math.max(0,Number(songs[cur].youtube.startSeconds)||0);
   const end=album?duration:Math.min(duration,Number(songs[cur].youtube.endSeconds)||duration);
   if(!Number.isFinite(duration)||!Number.isFinite(current)||end<=start||![1,2].includes(state)||typeof p?.seekTo!=='function')return null;
   return {p,owner,work:songs[cur].id,intent:playbackIntent,video,index,start,end,current,state};
  }catch(_){return null}
 }
 function sameSeekMedia(a,b){return !!a&&!!b&&a.p===b.p&&a.owner===b.owner&&a.work===b.work&&a.video===b.video&&a.index===b.index&&a.start===b.start&&a.end===b.end}
 function sameSeek(a,b){return sameSeekMedia(a,b)&&a.intent===b.intent}
 function paintSeek(c,value){
  const t=c?Math.max(c.start,Math.min(c.end,value??c.current)):0;
  for(const [range,elapsed,duration] of seekControls){const input=$(range);if(!input)continue;
   input.disabled=!c;input.min=c?c.start:0;input.max=c?c.end:100;input.value=t;
   const text=c?seekTime(t-c.start)+' / '+seekTime(c.end-c.start):(sourceActive||inlinePlaybackLocked?'この音源は動画内の再生位置を操作してください':'再生後に位置を変更できます');
   input.setAttribute('aria-valuetext',text);input.title=text;
   input.style.setProperty('--seek-fill',c?((t-c.start)/(c.end-c.start)*100)+'%':'0%');
   $(elapsed).textContent=c?seekTime(t-c.start):'0:00';$(duration).textContent=c?seekTime(c.end-c.start):'—';
  }
 }
 function resetSeek(){seekGesture=null;seekEndGuard=null;seekSegment=null;paintSeek(null)}
 function cancelSeek(){seekGesture=null;paintSeek(seekContext())}
 function refreshSeek(){
  const c=seekContext();
  // seekTo removes YouTube's authored endSeconds limit. Retain that boundary
  // without changing the existing crate auto-advance preference or sequence.
  if(seekSegment&&sameSeekMedia(seekSegment,c)&&c.current>=c.end&&c.state===1){
   const advance=c.owner.reachedPlaying&&c.owner.wantsPlay&&started&&$('#auto').checked;
   seekSegment=null;c.owner.reachedPlaying=false;requestMainPause();if(advance)go(1);return;
  }
  if(seekGesture&&!sameSeek(seekGesture.context,c))seekGesture=null;
  paintSeek(c,seekGesture?.value);
 }
 function beginSeek(input){const c=seekContext();if(!c){cancelSeek();return null}seekGesture={input,context:c,value:c.current};return seekGesture}
 function commitSeek(input){
  const gesture=seekGesture?.input===input?seekGesture:null,c=seekContext();
  if(!gesture||!sameSeek(gesture.context,c)){cancelSeek();return}
  const target=Math.max(c.start,Math.min(c.end,gesture.value));seekGesture=null;
  try{
   // Never turn browsing/cued/ended state into playback. A paused video stays paused.
   // Preview only while dragging; request an unbuffered stream once on release.
   seekEndGuard={...c,target,until:Date.now()+1500};
   if(!albumPlaybackLocked&&songs[cur].youtube.endSeconds)seekSegment=c;
   c.p.seekTo(target,true);
   if(c.state===2)c.p.pauseVideo();
   lastInteraction=Date.now();paintSeek(c,target);
  }catch(_){cancelSeek()}
 }
 function ignoreSeekEnd(p){
  const g=seekEndGuard;if(!g||g.p!==p||g.work!==songs[cur]?.id||g.intent!==playbackIntent||Date.now()>g.until)return false;
  try{return g.target<g.end-1&&Number(p.getCurrentTime())<g.end-1}catch(_){return false}
 }
 for(const [selector] of seekControls){const input=$(selector);if(!input)continue;
  input.addEventListener('pointerdown',()=>beginSeek(input));
  input.addEventListener('input',()=>{const g=seekGesture?.input===input?seekGesture:beginSeek(input);if(!g)return;g.value=Number(input.value);paintSeek(g.context,g.value)});
  input.addEventListener('change',()=>commitSeek(input));
  input.addEventListener('pointerup',()=>{const g=seekGesture;setTimeout(()=>{if(seekGesture===g)cancelSeek()},0)});
  input.addEventListener('pointercancel',cancelSeek);
  input.addEventListener('blur',cancelSeek);
  input.addEventListener('keydown',e=>{if(e.key==='Escape'&&seekGesture){e.preventDefault();e.stopPropagation();cancelSeek()}});
 }
 resetSeek();
