"""Exact approved opening-selection UI ledger, never a content or artwork exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-contextual-opening.json').read_text())
def historical_opening_file(path,data):
 c=FIXTURE['files'].get(path)
 if not c:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved opening-selection drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
