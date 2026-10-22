from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-knicks-addition.json').read_bytes()
assert sha(raw)=='11a26427055bb8e66349523c648292e8379f02b2f4850fd4f4003c3b98b0ec75','Immutable addition fixture changed'
F=json.loads(raw)
def current_knicks_addition_file(path,data):
 from approved_no_sleep_addition import historical_no_sleep_addition_file
 return historical_no_sleep_addition_file(path,data)
def historical_knicks_addition_file(path,data):
 data=current_knicks_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Knicks addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==524 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original523/base changed: '+path
 return out
