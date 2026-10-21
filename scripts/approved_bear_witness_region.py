"""Exact one-record source repair, with unchanged original work identity."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-bear-witness-region.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_bear_witness_region_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Bear Witness drift: '+path
 obj=json.loads(data)
 if path=='releases.json':obj['version']=F['beforeVersion']
 else:
  hits=[i for i,t in enumerate(obj) if t['id']==F['afterRecord']['id']];assert len(hits)==1 and obj[hits[0]]==F['afterRecord'];obj[hits[0]]=F['beforeRecord']
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode();assert sha(before)==c['beforeSHA256'];return before
