"""Exact two-record append ledger; never a general catalog or product exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/requested-two.json').read_text())
sha=lambda data:hashlib.sha256(data).hexdigest()
def historical_intake_file(path,data):
 from approved_timeline_explorer import historical_explorer_file
 data=historical_explorer_file(path,data)
 if path=='releases.json':
  c=FIXTURE['release'];assert sha(data)==c['afterSHA256'],'Unapproved release drift'
  value=json.loads(data);assert value['version']==c['version'];value['version']=c['before']['version'];assert value==c['before']
  before=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode();assert sha(before)==c['beforeSHA256'];return before
 c=FIXTURE['appendedFiles'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved requested-intake drift: '+path
 value=json.loads(data)
 if c['arrayKey'] is None:
  assert isinstance(value,list) and len(value)==c['afterCount'];value=value[:c['beforeCount']]
 else:
  assert isinstance(value,dict) and isinstance(value[c['arrayKey']],list) and len(value[c['arrayKey']])==c['afterCount']
  value[c['arrayKey']]=value[c['arrayKey']][:c['beforeCount']]
 before=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(before)==c['beforeSHA256'],'Published ordered prefix changed: '+path
 return before
def historical_intake_tracks():
 return json.loads(historical_intake_file('tracks.json',(ROOT/'tracks.json').read_bytes()))
