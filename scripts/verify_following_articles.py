from pathlib import Path
import json,hashlib,argparse,html,re,subprocess
from PIL import Image
from approved_following_articles import F,current_following_articles_file,historical_following_articles_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():
 data=(R/path).read_bytes()
 if path=='audit-reports/maintenance.json' and not a.source_only: assert sha(data)==F['generatedAuditSHA256'];continue
 assert sha(data)==h,path
ph=F['previousHelper'];assert sha((R/ph['path']).read_bytes())==ph['afterSHA256']
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(data)==c['afterSHA256'],path
 assert sha(historical_following_articles_file(path,data))==c['beforeSHA256'],path
 try:historical_following_articles_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted: '+path)
T=json.loads((R/'tracks.json').read_text());B=json.loads(F['files']['tracks.json']['before']);assert len(T)==F['afterCount'] and T[:len(B)]==B and T[len(B):]==F['tracks'];assert len({t['id'] for t in T})==len(T)
A=json.loads((R/'graffiti_artwork.json').read_text());old=json.loads(F['files']['graffiti_artwork.json']['before']);assert A['tracks'][:-len(F['tracks'])]==old['tracks'];assert {k:v for k,v in A.items() if k!='tracks'}=={k:v for k,v in old.items() if k!='tracks'}
for t,art in zip(F['tracks'],F['artworks'],strict=True):
 assert t['youtube']['id'] is None and not t['youtube'].get('playlistId')
 assert t['audioVerificationStatus']=='サイト内再生は確認中' and t['externalAudio']['official']is True
 assert all(t['youtube'].get(k)is not True for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
 assert t['externalAudio']['url'].startswith('https://') and t['externalAudio']['url'] in [s['url'] for s in t['sources']]
 assert len(t['essaySources'])==len(t['essay'])>=1 and all(0<=i<len(t['sources'])for r in t['essaySources']for i in r)
 assert t['artists']==list(dict.fromkeys(t['primaryArtists']+t['featuredArtists']))
 assert art['transparent']is True and art['noSiteBranding']is True and art['id']==t['id'] and art['palette']==t['art']['palette']
 asset=next(x for x in F['assets']if x['path']==art['image']);assert sha((R/asset['path']).read_bytes())==asset['sha256']
 with Image.open(R/asset['path'])as im:
  im.load();assert im.mode=='RGBA';alpha=im.getchannel('A');assert alpha.getextrema()[0]==0 and alpha.getextrema()[1]>=250;w,h=im.size;assert max(alpha.crop(z).getextrema()[1]for z in[(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])<=8
# The untouched queue policy excludes every article-first entry and preserves all baseline sources.
core=(R/'src/app/core.js').read_text().split(' const songs=',1)[0]
js=core+'\nconst tracks='+json.dumps(T)+';const added='+json.dumps([t['id']for t in F['tracks']])+';const baseline='+json.dumps(B)+';if(JSON.stringify(tracks.filter(hasPlayableSource).map(t=>t.id))!==JSON.stringify(baseline.filter(hasPlayableSource).map(t=>t.id)))throw Error("queue changed");if(tracks.filter(t=>added.includes(t.id)).some(hasPlayableSource))throw Error("unverified queued");'
subprocess.run(['node','-'],input=js,text=True,check=True,capture_output=True)
if not a.source_only:
 D=R/'dist';P=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(P)==len(T)
 for t in F['tracks']:
  page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
  for val in [t['title'],t['artist'],t['essayTitle'],*t['essay'],'サイト内再生は確認中',t['externalAudio']['url'],t['externalAudio']['label']]:assert val in page,val
  for val in [*t['essay'],'サイト内再生は確認中',t['externalAudio']['url']]:assert val in md,val
  assert next(x for x in P if x['id']==t['id'])['externalAudio']==t['externalAudio']
print('Article-first additions: exact prior catalog/UI inverse, null internal sources, official external links, protected assets and transparent art PASS; actual playback unverified.')
