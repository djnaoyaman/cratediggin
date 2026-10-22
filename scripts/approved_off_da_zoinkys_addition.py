from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-off_da_zoinkys-addition.json').read_bytes()
assert sha(raw)=='344f1f08d8b5b48f39142c1aa5eba7c105eadfc819c1d864835d51fec9c93198','Immutable addition fixture changed'
F=json.loads(raw)
def current_off_da_zoinkys_addition_file(path,data):
 from approved_a_lot_addition import historical_a_lot_addition_file
 return historical_a_lot_addition_file(path,data)
def historical_off_da_zoinkys_addition_file(path,data):
 data=current_off_da_zoinkys_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Off Da Zoinkys addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==534 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='artist_entities.json':assert obj.pop(F['artistEntity']['name'])==F['artistEntity']['record']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original533/base changed: '+path
 return out
