from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-rap-city-addition.json').read_bytes()
assert sha(raw)=='18c375597661a70072c2d358f837175e3e1c51cba6fe66ae609fb2ceb8553edd','Immutable addition fixture changed'
F=json.loads(raw)
def current_rap_city_addition_file(path,data):
 from approved_klink_addition import historical_klink_addition_file
 return historical_klink_addition_file(path,data)
def historical_rap_city_addition_file(path,data):
 data=current_rap_city_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Rap City addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==529 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='artist_entities.json':assert obj.pop(F['artistEntity']['name'])==F['artistEntity']['record']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original528/base changed: '+path
 return out
