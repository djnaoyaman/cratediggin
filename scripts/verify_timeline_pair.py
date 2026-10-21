"""Requested two-record append and directly generated output only."""
from pathlib import Path
import hashlib,json,sys
from html import escape
from PIL import Image
from approved_timeline_pair import F,historical_timeline_pair_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for name,c in F['files'].items():
 raw=(R/name).read_bytes();before=historical_timeline_pair_file(name,raw);assert sha(before)==c['beforeSHA256']
 for bad in (raw+b' ',before):
  try:historical_timeline_pair_file(name,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved bundle accepted: '+name)
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
tracks=json.loads((R/'tracks.json').read_text());old=json.loads(historical_timeline_pair_file('tracks.json',(R/'tracks.json').read_bytes()))
assert len(tracks)==516 and len(old)==514 and tracks[:-2]==old and tracks[-2:]==F['records']
assert len({t['id'] for t in tracks})==516
assert sum(t.get('workType','single')=='single' for t in tracks)==511
entities=json.loads((R/'artist_entities.json').read_text());assert {t['artist'] for t in tracks}<=entities.keys()
assert [t['youtube']['id'] for t in tracks[-2:]]==['I4P5RR4jPGg','a0ZhDbZIbiM']
assert [t['year'] for t in tracks[-2:]]==[2004,1989]
assert tracks[-2]['producers']==['Madlib']
assert tracks[-1]['producers']==['Prince Paul','De La Soul']
assert '2023' in tracks[-1]['versionBasis'] and '2002' in tracks[-2]['yearBasis']
dives=json.loads((R/'editorial_deepdives.json').read_text());assert dives[-2:]==F['deepdives']
art=json.loads((R/'graffiti_artwork.json').read_text());assert art['tracks'][-2:]==F['artEntries'] and len(art['tracks'])==516
for t,d,a,img in zip(F['records'],F['deepdives'],F['artEntries'],F['assets']):
 assert len(t['essay'])==len(t['essaySources'])==4 and len(d['sections'])==2
 assert all('（' not in p for p in t['producers'])
 assert t['versionBasis']==t['youtube']['versionBasis']
 assert isinstance(t['youtube']['channel'],str) and t['youtube']['channel'].strip()
 assert t['youtube']['playbackVerified'] is False and t['youtube']['embeddedPlaybackVerified'] is False
 assert 'japanAvailableMetadata' not in t['youtube'] and 'embeddableMetadata' not in t['youtube'] and 'duration' not in t['youtube']
 assert '未確認' in t['youtube']['notice']
 assert set(t['connections'])<={x['id'] for x in tracks} and t['id'] not in t['connections']
 for indices in t['essaySources']+[s['sources'] for s in d['sections']]:assert all(type(i)is int and 0<=i<len(t['sources']) for i in indices)
 assert a['palette']==t['art']['palette'] and a['transparent'] and a['textReviewed']
 p=R/img['path'];assert sha(p.read_bytes())==img['sha256']
 with Image.open(p) as im:
  im.load();assert im.mode=='RGBA' and list(im.size)==img['dimensions'] and max(im.size)<=2400
  assert sha(im.tobytes())==img['rgbaSHA256'] and im.getchannel('A').getextrema()[0]==0
  assert sum(1 for r,g,b,alpha in im.getdata() if min(r,g,b)>225 and alpha>240)>1000
sys.path.insert(0,str(R/'scripts'))
from editorial_uniqueness import authored,duplicates,new_violations
baseline=json.loads((R/'scripts/fixtures/editorial-legacy-debt.json').read_text());assert not new_violations(duplicates(authored(R)),baseline['groups']),'New editorial duplication'
if '--source-only' not in sys.argv:
 for t,d,a in zip(F['records'],F['deepdives'],F['artEntries']):
  D=R/'dist';p=(D/'tracks'/(t['id']+'.html')).read_text();md=(D/'songs'/(t['id']+'.md')).read_text()
  assert escape(t['essayTitle']) in p and t['essayTitle'] in md and escape(t['essayTitle']) in (D/'readings/index.html').read_text()
  assert all(escape(x) in p for x in t['essay']) and all(escape(s['heading']) in p for s in d['sections'])
  assert '未確認' in p and a['image'] in p and 'DJ Naoyaman' in p
  assert all(escape(f['text']) in p for f in t['facts'])
  assert '/tracks/'+t['id']+'.html' in (D/'sitemap.xml').read_text()
  with Image.open(D/'og'/(t['id']+'.jpg')) as im:assert im.size==(1200,630)
print('Two requested Timeline recordings, exact514 prefix, version/source distinctions, transparent art and honest unknown playback status PASS')
