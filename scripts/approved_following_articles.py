from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-following-articles.json').read_bytes();assert sha(raw)=='d6b02d47aba396ebbcedb641be9330f2609aea30121f960f459dcd23374fb750','Immutable article-first fixture drift';F=json.loads(raw)
def current_following_articles_file(path,data):return data
def historical_following_articles_file(path,data):
 data=current_following_articles_file(path,data)
 if path=='audit-reports/maintenance.json' and sha(data)==F['generatedAuditSHA256']:return F['previousGeneratedAudit'].encode()
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved article-first drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
