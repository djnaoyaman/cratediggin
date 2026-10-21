from pathlib import Path
import hashlib,json,sys
from approved_two_player_region import F,historical_two_player_region_file
R=Path(__file__).resolve().parents[1]
tracks=json.loads((R/'tracks.json').read_text());old=json.loads(historical_two_player_region_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(tracks)==len(old)==517
assert len([(a,b) for a,b in zip(old,tracks) if a!=b])==2
E=json.loads((R/'research/two-player-region-repair-20261021.json').read_text())
for change,meta,previous in zip(F['changes'],E['replacementSources'],E['previousSources']):
 a,b=change['before'],change['after'];assert {k:v for k,v in a.items() if k not in ['youtube','sources','editorialStatus','versionBasis','audioVerificationStatus']}=={k:v for k,v in b.items() if k not in ['youtube','sources','editorialStatus','versionBasis','audioVerificationStatus']}
 y=b['youtube'];assert y['id']==meta['id'] and 'JP' in meta['availableCountries'] and 'JP' not in previous['availableCountries'];assert meta['playabilityStatus']['playableInEmbed'] is True and y['japanRegionStatus']=='included'
 assert y['id'] in ['4kjeWGQ175g','TBMuGCw8hJY'] and y['duration'] in ['PT7M12S','PT14M37S'];assert y['official']==(y['id']=='TBMuGCw8hJY')
 assert all(y[k] is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
 if '--source-only' not in sys.argv:
  html=(R/('dist/tracks/'+b['id']+'.html')).read_text();assert y['url'] in html and b['editorialStatus'] in html
for p,h in F['protected'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
for p in F['files']:
 raw=(R/p).read_bytes();historical_two_player_region_file(p,raw)
 try:historical_two_player_region_file(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted')
print('Two sources Japan/embed metadata and515 unchanged records PASS; no actual playback certification')
