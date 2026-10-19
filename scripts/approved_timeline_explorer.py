"""Exact Timeline-only UI ledger, never a catalog/media/artwork exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_explorer_file(path,data):
    fixture=json.loads((ROOT/'scripts/fixtures/approved-timeline-explorer.json').read_text())
    c=fixture['files'].get(path)
    if c is None:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved Timeline drift: '+path
    before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
