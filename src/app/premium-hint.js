 // Optional playback guidance only: never detects membership or changes provider/privacy settings.
 const premiumHintKey='crate-premium-hint-v1';let premiumHintSeen=false,premiumHintTimer=0,premiumHintNode=null;
 try{premiumHintSeen=sessionStorage.getItem(premiumHintKey)==='1'}catch(_){}
 function hidePremiumHint(){clearTimeout(premiumHintTimer);premiumHintTimer=0;if(premiumHintNode)premiumHintNode.hidden=true;}
 function armPremiumHint(){clearTimeout(premiumHintTimer);premiumHintTimer=setTimeout(()=>{if(!premiumHintNode?.contains(document.activeElement))hidePremiumHint();},8000);}
 function showPremiumHint(){
  if(premiumHintSeen||!art.hidden||(typeof inlineFrame!=='undefined'&&inlineFrame?.isConnected))return;
  const anchor=$('#status');if(!anchor)return;
  premiumHintSeen=true;try{sessionStorage.setItem(premiumHintKey,'1')}catch(_){}
  const note=document.createElement('aside');note.className='premium-playback-hint';note.id='premium-playback-hint';note.setAttribute('aria-label','YouTube Premiumのご案内');
  note.innerHTML='<div role="status" aria-live="polite"><p>YouTube Premiumなら広告なしで再生できます。</p><small>加入アカウントへのログイン・ブラウザ設定によります。 <a href="https://support.google.com/youtube/answer/7437519?hl=ja" target="_blank" rel="noopener noreferrer">詳細 ↗</a></small></div><button type="button" aria-label="YouTube Premiumの案内を閉じる">×</button>';
  anchor.insertAdjacentElement('afterend',note);premiumHintNode=note;
  const close=note.querySelector('button');close.onclick=()=>{const focused=document.activeElement===close;hidePremiumHint();if(focused)$('#toggle')?.focus?.({preventScroll:true});};
  note.addEventListener('focusin',()=>clearTimeout(premiumHintTimer));note.addEventListener('focusout',armPremiumHint);armPremiumHint();
 }
