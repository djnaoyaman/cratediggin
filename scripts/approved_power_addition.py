from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-power-addition.json').read_bytes();assert sha(raw)=='7c9ea9ce044f2cd2bcb488130e0bbc4baafefa3e76ff4b2678d11510b73f3e8c','Immutable single-Power fixture drift';F=json.loads(raw)
def current_power_addition_file(path,data):return data
def historical_power_addition_file(path,data):
 data=current_power_addition_file(path,data)
 if path=='audit-reports/maintenance.json'and sha(data)==F['generatedAuditSHA256']:return F['previousGeneratedAudit'].encode()
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved single-Power drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
