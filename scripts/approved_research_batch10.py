from pathlib import Path
import json,hashlib,copy
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-research-batch10.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_research_batch10_file(path,data):
 from approved_research_batch11 import historical_research_batch11_file
 data=historical_research_batch11_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved research pilot drift: '+path
 obj=json.loads(data)
 if path=='tracks.json':
  by={t['id']:i for i,t in enumerate(obj)}
  for row in F['rows']:
   assert obj[by[row['id']]]==row['after'];obj[by[row['id']]]=copy.deepcopy(row['before'])
 elif path=='editorial_deepdives.json':assert obj==F['afterDeepDives'];obj=copy.deepcopy(F['beforeDeepDives'])
 elif path=='listening_shelves.json':assert obj==F['afterShelves'];obj=copy.deepcopy(F['beforeShelves'])
 else:obj['version']=F['beforeVersion']
 out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Unrelated content changed: '+path
 return out
