from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();enc=lambda o:(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
raw=(R/'scripts/fixtures/approved-power-status-correction.json').read_bytes();assert sha(raw)=='830c5dbb03a3c98d4461285aa659bd878b28a72b75f6f1f4c4bab3b3f819adce','Immutable correction fixture drift';F=json.loads(raw)
def current_power_status_correction_file(path,data):
 from approved_ga_events import historical_ga_events_file
 return historical_ga_events_file(path,data)
def historical_power_status_correction_file(path,data):
 data=current_power_status_correction_file(path,data)
 if path=='audit-reports/maintenance.json'and sha(data)==F['generatedAuditSHA256']:
  obj=json.loads(data)
  for row in F['auditChangedRows']:
   assert obj[row['index']]['id']==row['id'];obj[row['index']]=row['before']
  out=enc(obj);assert sha(out)==F['generatedAuditBeforeSHA256'];return out
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved correction drift: '+path
 if c['operation']=='text':out=c['before'].encode()
 else:
  obj=json.loads(data)
  if c['operation']=='replace_track':assert obj[c['index']]['id']==c['id'];obj[c['index']]=c['beforeRow']
  elif c['operation']=='release_version':obj['version']=c['beforeVersion']
  else:raise AssertionError('Unknown correction operation')
  out=enc(obj)
 assert sha(out)==c['beforeSHA256'],'Correction before bytes mismatch: '+path
 return out
