from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-the-waters-addition.json').read_bytes()
assert sha(raw)=='8bd86be6f6d7ef1efb46e0105519dec6e89a0457f506acf94445ef70d8ed7ab8','Immutable addition fixture changed'
F=json.loads(raw)
def current_the_waters_addition_file(path,data):
 from approved_rap_city_addition import historical_rap_city_addition_file
 return historical_rap_city_addition_file(path,data)
def historical_the_waters_addition_file(path,data):
 data=current_the_waters_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved The Waters addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==528 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='artist_entities.json':assert obj.pop(F['artistEntity']['name'])==F['artistEntity']['record']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original527/base changed: '+path
 return out
