"""Exact static Premium help copy; no player or account behavior changes."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-premium-notice.json').read_text())
def historical_premium_notice_file(path,data):
 from approved_wutang_feature import historical_wutang_feature_file
 data=historical_wutang_feature_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved Premium notice drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
