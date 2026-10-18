"""Protect all493 previously published works and validate the six requested additions."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[1]
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
f=json.loads((R/'scripts/fixtures/requested-six.json').read_text());baseline=f['published493'];t=json.loads((R/'tracks.json').read_text());ids=[x['id'] for x in t];by={x['id']:x for x in t}
assert len(t)==499 and len(set(ids))==499 and ids[:493]==baseline['orderedIds']
for id,h in baseline['records'].items():assert digest(by[id])==h, 'Published record changed: '+id
for name,p in baseline['sourcePrefixes'].items():
 d=json.loads((R/name).read_text());key=p['kind'];n=p['count']
 if key=='object':d=dict(list(d.items())[:n])
 elif key is None:d=d[:n]
 else:d[key]=d[key][:n]
 assert digest(d)==p['sha256'],'Published prefix changed: '+name
for name,h in baseline['assets'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h
assert ids[493:]==f['ids']
art={x['id']:x for x in json.loads((R/'graffiti_artwork.json').read_text())['tracks']};deep={(x['artist'],x['title']):x['sections'] for x in json.loads((R/'editorial_deepdives.json').read_text())}
for id in f['ids']:
 x=by[id];expected=f['records'][id];assert (x['title'],x['artist'],x['year'],x['producer'],x['youtube']['id'])==tuple(expected)
 assert x['youtube']['official'] and x['youtube']['playbackVerified'] is False and x['youtube']['embeddedPlaybackVerified'] is False
 assert len(x['essay'])==len(x['essaySources'])==3 and len(deep[(x['artist'],x['title'])])==2
 for refs in x['essaySources']:assert refs and all(isinstance(i,int) and 0<=i<len(x['sources']) for i in refs)
 for d in deep[(x['artist'],x['title'])]:assert d['sources'] and all(0<=i<len(x['sources']) for i in d['sources'])
 a=art[id];assert a['transparent'] and a['palette']==x['art']['palette'];p=R/a['image'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['art'][id]['sha256']
 with Image.open(p) as im:assert im.width<=2400 and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
 for forbidden in ['統合時','依頼名','本文取得未','検索抜粋のみ','追記予定','source budget','production-ready']:
  assert forbidden not in json.dumps([x['essay'],x['sources'],deep[(x['artist'],x['title'])]],ensure_ascii=False)
 if not id.startswith('redman-'):assert x['samples']==[] and '未確認' in x['sampleStatus']
r=by['redman-a-day-of-sooperman-lover'];assert len(r['samples'])==1;s=r['samples'][0];assert s.get('main') is not True and s['title']=='Superman Lover' and s['youtube']['id']=='fQrAQU9c3wY' and s['sources']
assert not set(f['held'])&set(ids)
print('Six exact requested records; all493 original values/order and new4 assets protected; sources, non-dominant sample, alpha/white paint passed; no audio certification')
