"""Exact single requested work append; no unrelated content or media exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
F=json.loads((ROOT/'scripts/fixtures/approved-something.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_something_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Something drift: '+path
 obj=json.loads(data)
 if path=='releases.json':obj['version']=c['beforeVersion']
 elif c['arrayKey'] is None:
  assert len(obj)==c['beforeCount']+1
  obj=obj[:c['beforeCount']]
 else:
  key=c['arrayKey'];assert len(obj[key])==c['beforeCount']+1
  obj[key]=obj[key][:c['beforeCount']]
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Published data changed: '+path
 return before
