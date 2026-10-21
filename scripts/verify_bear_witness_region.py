"""One source replacement with explicit metadata-only Japan availability."""
from pathlib import Path
import hashlib,json,sys
R=Path(__file__).resolve().parents[1]
from approved_bear_witness_region import F,historical_bear_witness_region_file
tracks=json.loads((R/'tracks.json').read_text());old=json.loads(historical_bear_witness_region_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(tracks)==len(old)==507
changed=[(a,b) for a,b in zip(old,tracks) if a!=b];assert len(changed)==1
before,after=changed[0];assert before==F['beforeRecord'] and after==F['afterRecord']
assert after['id']=='dr-octagon-bear-witness' and after['year']==1996
assert {k:v for k,v in before.items() if k not in ['youtube','sources','editorialStatus']}=={k:v for k,v in after.items() if k not in ['youtube','sources','editorialStatus']}
y=after['youtube'];assert y['id']=='_dC7jx1iqxY' and y['duration']=='PT3M1S' and y['official'] is False and y['japanRegionStatus']=='included' and y['playableInEmbed'] is True
assert all(y[k] is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
e=json.loads((R/'research/bear-witness-region-repair-20261021.json').read_text());assert e['videos'][0]['availableCountries']==['US'];chosen=e['videos'][1];assert chosen['videoDetails']['videoId']==y['id'] and 'JP' in chosen['availableCountries'] and chosen['playabilityStatus']['playableInEmbed'] is True
for p,h in F['protected'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
for p in F['files']:
 raw=(R/p).read_bytes();historical_bear_witness_region_file(p,raw)
 try:historical_bear_witness_region_file(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted')
if '--source-only' not in sys.argv:
 html=(R/'dist/tracks/dr-octagon-bear-witness.html').read_text();assert y['url'] in html and '非公式' in html and after['editorialStatus'] in html
print('Bear Witness exact source/territory metadata and506-record preservation PASS; no playback certification')
