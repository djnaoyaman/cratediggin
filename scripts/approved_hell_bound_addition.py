from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-hell_bound-addition.json').read_bytes()
assert sha(raw)=='53714ebff13c33443f443e45c71ca0cfa6e94f48d6d9a4b89576cc421d7af38b','Immutable addition fixture changed'
F=json.loads(raw)
def current_hell_bound_addition_file(path,data):
 return data
def historical_hell_bound_addition_file(path,data):
 data=current_hell_bound_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Hell Bound (Ad 01) addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==537 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='artist_entities.json':assert obj.pop(F['artistEntity']['name'])==F['artistEntity']['record']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original536/base changed: '+path
 return out
