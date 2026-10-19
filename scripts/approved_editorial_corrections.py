"""Exact source-grounded editorial corrections, not a general preservation exemption."""
from pathlib import Path
import json,hashlib,copy
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-editorial-corrections.json').read_text())
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def historical_editorial_record(record):
 for c in FIXTURE['corrections']:
  if record['id']==c['id']:
   assert digest(c['before'])==c['beforeSHA256'] and digest(c['after'])==c['afterSHA256']
   changed={k for k in set(c['before'])|set(c['after']) if c['before'].get(k)!=c['after'].get(k)}
   assert changed==set(c['allowedFields'])=={'essayTitle','deck','essay','listening','sources','essaySources'}
   assert digest(record)==c['afterSHA256'], 'Unapproved editorial drift: '+record['id']
   return copy.deepcopy(c['before'])
 return record
def historical_editorial_file(path,data):
 c=FIXTURE['fileCorrections'].get(path)
 if c:
  assert hashlib.sha256(data).hexdigest()==c['afterSHA256'], 'Unapproved shelf drift'
  before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
 return data
