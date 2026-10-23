from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/"scripts/fixtures/approved-guru-note4.json").read_bytes();assert sha(raw)=="ba15fc6533f56b2abc51ca93dc3cfa665152af583ae6246d48525e08eba940e7",'Immutable credit-note fixture drift'
F=json.loads(raw)
def current_guru_note4_file(path,data):
 from approved_guru_note5 import historical_guru_note5_file
 return historical_guru_note5_file(path,data)
def historical_guru_note4_file(path,data):
 data=current_guru_note4_file(path,data)
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
