"""Exact targeted-CI workflow/version delta for historical preservation checks."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_ci_policy_file(path,data):
    f=json.loads((ROOT/'scripts/fixtures/approved-ci-policy.json').read_text())
    c=f['files'].get(path)
    if c is None:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved CI-policy drift: '+path
    before=c['before'].encode()
    assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
    return before
