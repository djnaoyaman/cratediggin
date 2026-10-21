"""Exact requested three-record append; published prefix and unaffected metadata preserved."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-cash-money-three.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_cash_money_three_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Cash Money drift: '+path
 obj=json.loads(data);key=c['arrayKey']
 if key=='version':obj['version']=c['beforeVersion']
 elif key=='entity':assert obj.pop(c['addedEntity'])==c['entityValue']
 elif key is None:
  assert len(obj)==c['beforeCount']+3;obj=obj[:c['beforeCount']]
 else:
  assert len(obj[key])==c['beforeCount']+3;obj[key]=obj[key][:c['beforeCount']]
 before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Published content changed: '+path
 return before
