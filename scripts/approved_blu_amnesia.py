"""Exact one requested Blu track; published content preserved."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-blu-amnesia.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_blu_amnesia_file(path,data):
 from approved_four_mix import historical_four_mix_file
 data=historical_four_mix_file(path,data)
 from approved_two_player_region import historical_two_player_region_file
 data=historical_two_player_region_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Blu-track drift: '+path
 obj=json.loads(data);key=c['arrayKey']
 if key=='version':obj['version']=c['beforeVersion']
 elif key=='entities':
  for k,v in c['addedEntities'].items():assert obj.pop(k)==v
 elif key is None:
  assert len(obj)==c['beforeCount']+1;obj=obj[:c['beforeCount']]
 else:
  assert len(obj[key])==c['beforeCount']+1;obj[key]=obj[key][:c['beforeCount']]
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Published content changed: '+path
 return before
