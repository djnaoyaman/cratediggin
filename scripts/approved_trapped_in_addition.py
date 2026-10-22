from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-trapped_in-addition.json').read_bytes()
assert sha(raw)=='523de6b2f788ba7495d7ef54bea939dbab00338ec086e724f38e4d48376c434b','Immutable addition fixture changed'
F=json.loads(raw)
def current_trapped_in_addition_file(path,data):
 return data
def historical_trapped_in_addition_file(path,data):
 data=current_trapped_in_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Trapped In addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==536 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='artist_entities.json':assert obj.pop(F['artistEntity']['name'])==F['artistEntity']['record']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original535/base changed: '+path
 return out
