"""Exact person queue correction; no membership or content exemptions."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-person-queue.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_person_queue_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved person queue drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
