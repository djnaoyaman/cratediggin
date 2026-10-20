"""Exact optional video bootstrap correction; no unrelated-source exemptions."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
F=json.loads((ROOT/'scripts/fixtures/approved-album-bootstrap.json').read_text())
def historical_album_bootstrap_file(path,data):
 from approved_method_man import historical_method_man_file
 data=historical_method_man_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved album bootstrap drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
