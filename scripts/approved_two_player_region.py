"""Exact two-record Japan source repair; no unrelated drift."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-two-player-region.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_two_player_region_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved source repair drift: '+path
 obj=json.loads(data)
 if path=='releases.json':obj['version']=F['beforeVersion']
 else:
  for change in F['changes']:
   hits=[i for i,t in enumerate(obj) if t['id']==change['after']['id']]
   assert len(hits)==1 and obj[hits[0]]==change['after'];obj[hits[0]]=change['before']
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode();assert sha(before)==c['beforeSHA256'];return before
