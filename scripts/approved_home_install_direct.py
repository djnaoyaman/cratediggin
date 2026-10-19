"""Exact approved direct-install presentation and owner-supplied Premier photo ledger."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-home-install-direct.json').read_text())
def historical_home_install_file(path,data):
 from approved_contextual_opening import historical_opening_file
 data=historical_opening_file(path,data)
 c=FIXTURE['files'].get(path)
 if not c:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved direct-install/photo drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
