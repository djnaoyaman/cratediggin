from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();enc=lambda o:(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
raw=(R/'scripts/fixtures/approved-selected-concept.json').read_bytes();assert sha(raw)=='1f440f5ce41dff8945b0cd11fa0060b536eb2879121aa781e4f481ec0b9ccf1a','Immutable selected-concept fixture drift';F=json.loads(raw)
def current_selected_concept_file(path,data):return data
def historical_selected_concept_file(path,data):
 data=current_selected_concept_file(path,data)
 if path=='audit-reports/maintenance.json'and sha(data)==F['generatedAuditSHA256']:
  out=enc(json.loads(data)[:-len(F['tracks'])]);assert sha(out)==F['generatedAuditBeforeSHA256'];return out
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved selected-concept drift: '+path
 op=c['operation']
 if op=='text':out=c['before'].encode()
 else:
  obj=json.loads(data)
  if op=='append_tracks':obj=obj[:-c['count']]
  elif op=='append_artworks':obj['tracks']=obj['tracks'][:-c['count']]
  elif op=='add_entities':
   for key in c['keys']:del obj[key]
  elif op=='release_version':obj['version']=c['beforeVersion']
  else:raise AssertionError('Unknown operation '+op)
  out=enc(obj)
 assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
