"""Exact recoverable album failure correction; no unrelated-source exemptions."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
F=json.loads((ROOT/'scripts/fixtures/approved-album-recovery.json').read_text())
def historical_album_recovery_file(path,data):
 from approved_album_bootstrap import historical_album_bootstrap_file
 data=historical_album_bootstrap_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved album recovery drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
