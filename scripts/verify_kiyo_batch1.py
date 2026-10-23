from pathlib import Path
from PIL import Image
import json,hashlib,html,re,argparse
from approved_kiyo_batch1 import F,current_kiyo_batch1_file,historical_kiyo_batch1_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args();read=lambda path:current_kiyo_batch1_file(path,(R/path).read_bytes())
assert len(F['tracks'])==len(F['artworks'])==len(F['assets'])==6
for path,h in F['protected'].items():assert sha(read(path))==h,path
ph=F['previousHelper'];assert sha(read(ph['path']))==ph['afterSHA256']
for path,c in F['files'].items():
 assert sha(read(path))==c['afterSHA256'];assert sha(historical_kiyo_batch1_file(path,(R/path).read_bytes()))==c['beforeSHA256']
 try:historical_kiyo_batch1_file(path,(R/path).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
tracks=json.loads(read('tracks.json'));assert len(tracks)==544 and len({x['id']for x in tracks})==544 and tracks[-6:]==F['tracks'];assert[x['id']for x in tracks[:-6]]==F['beforeIds']
for t,art,asset in zip(F['tracks'],F['artworks'],F['assets'],strict=True):
 assert art['image']==asset['path'] and art['transparent']is True and t['art']['word']==t['title'] and t['art']['palette']==art['palette']
 assert len(t['essay'])==len(t['essaySources'])>=2 and all(0<=i<len(t['sources'])for refs in t['essaySources']for i in refs)
 assert t['youtube']['channel']and t['youtube']['type']=='Official Audio'and all(t['youtube'][k]is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
 assert sha((R/asset['path']).read_bytes())==asset['sha256']
 with Image.open(R/asset['path'])as im:
  im.load();assert im.mode=='RGBA'and im.size==(asset['width'],asset['height']);al=im.getchannel('A');assert al.getextrema()==tuple(asset['alphaExtrema']) and asset['alphaExtrema'][0]==0 and asset['alphaExtrema'][1]>=250;w,h=im.size;assert max(al.crop(z).getextrema()[1]for z in[(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])==asset['edgeAlphaMax']<=8
  box=al.point(lambda v:255 if v>8 else 0).getbbox();assert box[0]>0 and box[1]>0 and box[2]<w and box[3]<h
if not a.source_only:
 D=R/'dist';projected=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(projected)==544
 readings=html.unescape((D/'readings/index.html').read_text())
 for t in F['tracks']:
  raw=(D/f'tracks/{t["id"]}.html').read_text();page=html.unescape(raw);md=(D/f'songs/{t["id"]}.md').read_text()
  for v in [t['title'],t['artist'],t['essayTitle'],t['deck'],*t['essay'],*(f['text']for f in t['facts']),t['editorialStatus'],t['sampleStatus']]:assert v in page,v
  for s in t['sources']:assert s['url']in page
  for v in [t['essayTitle'],*t['essay']]:assert v in md
  assert next(x['image']for x in F['artworks']if x['id']==t['id'])in page and '## 要調査'not in md
  pt=next(x for x in projected if x['id']==t['id'])
  for k,v in t.items():
   if k!='art':assert pt[k]==v,k
  assert pt['art']['image']==next(x['image']for x in F['artworks']if x['id']==t['id'])and pt['art']['transparent']is True
  assert t['title']in readings and t['essayTitle']in readings and f'/tracks/{t["id"]}.html'in readings
  graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',raw,re.S).group(1))['@graph'];rec=next(x for x in graph if x.get('@type')=='MusicRecording');assert rec['byArtist']['name']==t['artist']
  if F['entities'].get(t['artist'],{}).get('type')=='Person':assert rec['byArtist']['@type']=='Person'
  if t['artist']in F['entities'] and F['entities'][t['artist']]['type']is None:assert '@type'not in rec['byArtist']
print('Six reviewed KIYO additions; old538/credits/UI/security/assets exact, strict inverse and new asset guards PASS. Metadata is not playback verification.')
