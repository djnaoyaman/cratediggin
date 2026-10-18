 // Presentation modes never change transport, ownership, queue or playback position.
 let artDisplayMode='hybrid',artPauseBusy=false,artPauseToken=0,artPauseTimer=null;
 function artStoppedInline(){return false}
 function artPlaybackSuppressed(){return false}
 function artModeButtons(){for(const [id,mode] of [['#art-mode-video','video'],['#art-mode-full','full'],['#art-mode-hybrid','hybrid']]){const b=$(id);if(b){b.setAttribute('aria-pressed',String((!art.hidden?document.body.dataset.artMode:artDisplayMode)===mode));b.disabled=false}}}
 function setArtPresentation(mode){if(!['full','video','hybrid'].includes(mode))return false;artDisplayMode=mode;if(!art.hidden)refreshArtProvider();artModeButtons();return true;}
 function restoreVideoWithoutPlay(){return setArtPresentation('hybrid')}
 function prepareArtExplicitPlay(){}
 function revealArtProvider(p){if(p===sourcePlayer&&sourcePlayer){const frame=sourcePlayer.getIframe?.();frame?.scrollIntoView?.({block:'center',behavior:'instant'});frame?.focus?.({preventScroll:true})}else openPlayerPresentation(true)}
 function guardArtPlayback(){return false}
 function requestArtOnly(openAfter=false){artDisplayMode='full';if(openAfter)showArt(true);else if(!art.hidden)refreshArtProvider();artModeButtons();}
 function renderArtOnly(){clearArtDock();document.body.dataset.artOwner='full';document.body.dataset.artMode='full';document.body.style.setProperty('--art-width',innerWidth+'px');document.body.style.setProperty('--art-height',innerHeight+'px');isolateArtPaths(null);const inline=!!inlineFrame?.isConnected;$('#art-toggle').hidden=inline;$('#art-toggle').textContent=sourceActive?'↩':(albumPlaybackLocked?albumSession?.wantsPlay:mainIntent.wantsPlay)?'Ⅱ':'▶';$('#art-toggle').setAttribute('aria-label',sourceActive?'楽曲に戻る':'再生・一時停止');$('#art-provider-help').textContent=inline?'Bandcampの再生操作はVIDEOまたはHYBRIDで行えます。':'表示モードを切り替えても、曲と再生位置は変わりません。';artModeButtons();window.CrateArt?.resize?.();return true;}
