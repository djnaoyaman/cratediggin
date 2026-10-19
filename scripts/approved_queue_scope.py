"""Exact queue initialization correction, never a general preservation exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_queue_scope_file(path,data):
    f=json.loads((ROOT/'scripts/fixtures/approved-queue-scope.json').read_text())
    c=f['files'].get(path)
    if c is None:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved queue-scope drift: '+path
    before=c['before'].encode()
    assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
    return before
