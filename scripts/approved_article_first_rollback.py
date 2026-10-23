from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-article-first-rollback.json').read_bytes();assert sha(raw)=='bda8213ae58f4ca4928714adc756e87997ba42aa7b1f0d85c9f11f295f6b2a52';F=json.loads(raw)
def current_article_first_rollback_file(path,data):return data
def historical_article_first_rollback_file(path,data):
 data=current_article_first_rollback_file(path,data)
 if path=='audit-reports/maintenance.json' and sha(data)==F['generatedAuditSHA256']:return F['previousGeneratedAudit'].encode()
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved rollback drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'];return out
