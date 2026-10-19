"""Exact source-led Premier addition and role-policy rendering ledger, never a generic exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-premier-feature.json').read_text())
def historical_premier_file(path,data):
    from approved_home_install_direct import historical_home_install_file
    data=historical_home_install_file(path,data)
    c=FIXTURE['files'].get(path)
    if not c:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved Premier scope drift: '+path
    before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
