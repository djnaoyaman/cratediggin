"""Exact four requested mix tracks; published content preserved."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-four-mix.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_four_mix_file(path,data):
 from approved_named_art_first import historical_named_art_first_file
 data=historical_named_art_first_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved four-track drift: '+path
 obj=json.loads(data);key=c['arrayKey']
 if key=='version':obj['version']=c['beforeVersion']
 elif key=='entities':
  for k,v in c['addedEntities'].items():assert obj.pop(k)==v
 elif key is None:
  assert len(obj)==c['beforeCount']+4;obj=obj[:c['beforeCount']]
 else:
  assert len(obj[key])==c['beforeCount']+4;obj[key]=obj[key][:c['beforeCount']]
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Published content changed: '+path
 return before
