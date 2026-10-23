from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-external-articles.json').read_bytes();assert sha(raw)=='398ad9ed0d263e1ff831e64da88e71c2d7ed90ed2ea55e829ae3f45500628ad7','Immutable article-first fixture drift';F=json.loads(raw)
def current_external_articles_file(path,data):return data
def historical_external_articles_file(path,data):
 data=current_external_articles_file(path,data)
 if path=='audit-reports/maintenance.json' and sha(data)==F['generatedAuditSHA256']:return F['previousGeneratedAudit'].encode()
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved article-first drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
