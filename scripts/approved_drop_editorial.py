"""Exact source-grounded Drop editorial delta; media and all other records preserved."""
from pathlib import Path
import json,hashlib,copy
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-drop-editorial.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_drop_file(path,data):
 from approved_organ_editorial import historical_organ_file
 data=historical_organ_file(path,data)
 spec=F['files'].get(path)
 if spec is None:return data
 assert sha(data)==spec['afterSHA256'],'Unapproved Drop editorial drift: '+path
 value=json.loads(data)
 if path=='tracks.json':
  row=next(i for i,t in enumerate(value) if t['id']==F['correction']['id'])
  assert value[row]==F['correction']['after']
  value[row]=copy.deepcopy(F['correction']['before'])
 else:value['version']=F['beforeVersion']
 out=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==spec['beforeSHA256'],'Unrelated content changed: '+path
 return out
