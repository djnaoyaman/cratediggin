"""Exact approved credit/gallery/signature correction; no general content exemption."""
from pathlib import Path
import hashlib,json,copy
ROOT=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_credit_file(path,data):
 f=json.loads((ROOT/'scripts/fixtures/approved-artifacts-credits.json').read_text())
 c=f['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved credit-correction drift: '+path
 if path=='tracks.json':
  value=json.loads(data)
  for row in f['records']:
   index=row['index'];assert value[index]==row['after'];value[index]=copy.deepcopy(row['before'])
  before=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
 else:before=c['before'].encode()
 assert sha(before)==c['beforeSHA256'],'Original credit baseline mismatch: '+path
 return before
