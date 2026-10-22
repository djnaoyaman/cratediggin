from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-chittlins-pepsi-addition.json').read_bytes()
assert sha(raw)=='35b7c8cfdf75f78ca0817f6e1971ef633186cbc1e2b571430a53afee83ba614e','Immutable addition fixture changed'
F=json.loads(raw)
def current_chittlins_pepsi_addition_file(path,data):
 return data
def historical_chittlins_pepsi_addition_file(path,data):
 data=current_chittlins_pepsi_addition_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Chittlins & Pepsi addition drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==527 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
  elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse operation')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original526/base changed: '+path
 return out
