"""Normalize only the exact reviewed shuffle invalidation delta for historical guards."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_shuffle_scope_file(path,data):
    from approved_ci_policy import historical_ci_policy_file
    data=historical_ci_policy_file(path,data)
    f=json.loads((ROOT/'scripts/fixtures/approved-shuffle-scope.json').read_text())
    c=f['files'].get(path)
    if c is None:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved shuffle-scope drift: '+path
    before=c['before'].encode()
    assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
    return before
