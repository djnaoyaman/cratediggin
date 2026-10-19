"""Exact one-record correction; protect every other published value and product byte."""
import json, hashlib, copy
from pathlib import Path
from approved_media_correction import FIXTURE as f, historical_record, digest
R=Path(__file__).resolve().parents[1]
t=json.loads((R/'tracks.json').read_text()); assert [x['id'] for x in t]==f['orderedIds'] and len(t)==499
for x in t:assert digest(historical_record(x))==f['publishedRecords'][x['id']],x['id']
for name,h in f['protectedFiles'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
c=f['corrections'];assert len(c)==1 and c[0]['id']=='ini-grown-man-sport'
x=next(x for x in t if x['id']==c[0]['id']);y=x['youtube'];assert y['id']=='pXu0g1gFjDM' and y['url']=='https://www.youtube.com/watch?v=pXu0g1gFjDM'
assert y['official'] and y['japanAvailableMetadata'] and y['embeddableMetadata']
assert y['playbackVerified'] is False and y['embeddedPlaybackVerified'] is False
assert x['artist']=='InI' and x['album']=='Center of Attention' and y['duration']=='PT4M36S'
e=f['evidence'];assert e['videoId']==y['id'] and e['channelId']==y['channelId'] and e['lengthSeconds']=='276'
assert 'JP' in e['availableCountries'] and e['playableInEmbed'] is True and e['status']=='OK'
assert 'center of attention' in e['keywords'] and 'ini' in e['keywords'] and e['actualJapanPlaybackTested'] is False
assert any(s['url']=='https://www.youtube.com/watch?v=S-sTcEQHvkY' for s in x['sources']),'Historical credit citation must remain'
inline=(R/'src/app/inline-player.js').read_text();assert 'track=2828430171' in inline and 'track=4005860905' in inline
for field,value in [('title','Changed title'),('artist','Changed artist'),('essay',[]),('editorialStatus','Changed notice'),('youtube',dict(y,id='wrong'))]:
 changed=copy.deepcopy(x);changed[field]=value
 try:historical_record(changed)
 except AssertionError:pass
 else:raise AssertionError('Mutation accepted: '+field)
print('One exact official JP/embed-qualified media correction; all499 ordered records and original product/assets protected; mutation guard rejects other changes; no real audio certification')
