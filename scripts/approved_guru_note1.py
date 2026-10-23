from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/"scripts/fixtures/approved-guru-note1.json").read_bytes();assert sha(raw)=="e21e82a27e3bcfc4747b3c54f9f87756fa32fad762fed1145506d7921a7deb36",'Immutable credit-note fixture drift'
F=json.loads(raw)
def current_guru_note1_file(path,data):
 return data
def historical_guru_note1_file(path,data):
 data=current_guru_note1_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved credit-note drift: '+path
 if 'before' in c:out=c['before'].encode()
 else:
  obj=json.loads(data)
  if path=='tracks.json':
   assert len(obj)==F['count'];i=next(i for i,t in enumerate(obj) if t['id']==F['id']);assert obj[i]==F['after'];obj[i]=F['before']
  elif path=='releases.json':assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse')
  out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Prior content drift: '+path
 return out
