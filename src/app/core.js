 function workPlayLabel(s){return ({single:'この曲を聴く',mix:'このミックスを聴く',live_video:'この映像を再生',album:'アルバム全体を聴く'})[workType(s)]}
 function isAlbumSource(s){return s?.youtube?.sourceType==='playlist'}
 function hasPlayableSource(s){return !!(isAlbumSource(s)?s.youtube.playlistId:s?.youtube?.id)}
 function yearLabel(s){return Number.isInteger(s.year)?String(s.year)+(s.yearQualifier?'年〈'+s.yearQualifier+'〉':''):'発表年未確認'}
 function yearSort(s){return Number.isInteger(s.year)?s.year:9999}
 function yearDistance(a,b){return Number.isInteger(a.year)&&Number.isInteger(b.year)?Math.abs(yearSort(a)-yearSort(b)):9999}
 function youtubeLinkLabel(s){return s.youtube.official===true?'公式YouTubeで開く ↗':s.youtube.official===false?'YouTubeの参考投稿で開く ↗':'YouTubeで開く ↗'}
 function workUnit(list){return list.some(s=>workType(s)!=='single')?'作品':'曲'}
 function workType(s){return s.workType||'single'}
 function workLabel(s){return ({single:'楽曲',mix:'DJミックス作品',live_video:'ライブ映像（参考投稿）',album:'アルバム全体'})[workType(s)]}
 function workCount(list){const singles=list.filter(s=>workType(s)==='single').length,mixes=list.filter(s=>workType(s)==='mix').length,videos=list.filter(s=>workType(s)==='live_video').length,albums=list.filter(s=>workType(s)==='album').length;return singles+'曲'+(mixes?'・'+mixes+'ミックス作品':'')+(videos?'・'+videos+'ライブ映像':'')+(albums?'・'+albums+'アルバム':'')}
 const songs=window.TRACKS.slice().sort((a,b)=>yearSort(a)-yearSort(b)||a.artist.localeCompare(b.artist)||a.title.localeCompare(b.title)),$=s=>document.querySelector(s),esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),norm=x=>String(x).normalize('NFKC').toLowerCase();
 const origin=(window.CRATE_SITE_URL||location.origin).replace(/\/$/,''),view=$('#view'),art=$('#art-view');let player=null,ready=false,started=false,playing=false,cur=0,queue=songs.filter(hasPlayableSource).map(s=>s.id),sourcePlayer=null,sourceId=null,returnTime=0,returnPlaying=false,sourceActive=false,errorCount=0,lastInteraction=Date.now(),artFocus=null,artManual=false;
 const excluded=new Set();try{JSON.parse(localStorage.getItem('crate-queue-excluded')||'[]').forEach(id=>excluded.add(id))}catch(_){}
 let playlistStorage;try{playlistStorage=localStorage}catch(_){playlistStorage={getItem:()=>null,setItem:()=>{throw Error('storage')}}}
 const myCrate=window.CratePlaylist(songs,playlistStorage);let customMode=false,lastCustomRemoved=null,applyListFilters=null;
 let queueCustom=false,queueScope=queue.slice();
 const playableIds=(list,selected=customMode)=>list.filter(x=>hasPlayableSource(x)&&(selected||!excluded.has(x.id))).map(x=>x.id);
 function saveExcluded(){try{localStorage.setItem('crate-queue-excluded',JSON.stringify([...excluded]))}catch(_){}}
 queue=playableIds(songs);
 let lastRemoved=null;
