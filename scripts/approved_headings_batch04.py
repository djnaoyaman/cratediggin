from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-headings-batch04.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_headings_batch04_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved heading correction drift: '+path
 obj=json.loads(data)
 if path=='tracks.json':
  by={t['id']:t for t in obj}
  for row in F['rows']:
   assert by[row['id']]['essayTitle']==row['new'];by[row['id']]['essayTitle']=row['old']
 else:obj['version']=F['beforeVersion']
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Unrelated content changed: '+path
 return before
