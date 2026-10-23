"""Strict frozen patch, pre-existing catalog/transport and CI preservation."""
from pathlib import Path
import argparse,json,hashlib
from approved_top_return import F,current_top_return_file,historical_top_return_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
def current(path):return current_top_return_file(path,(R/path).read_bytes())
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():assert sha(current(path))==h,path
assert len(json.loads(current('tracks.json')))==F['count']==562
assert json.loads(current('releases.json'))['version']==F['afterVersion']=='22.172'
assert sha(current(F['previousHelper']['path']))==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(current_top_return_file(path,data))==c['afterSHA256'],path
 assert sha(historical_top_return_file(path,data))==c['beforeSHA256'],path
 for mutated in [data+b' ',data[:-1]]:
  try:historical_top_return_file(path,mutated)
  except AssertionError:pass
  else:raise AssertionError('Unapproved drift accepted: '+path)
for path,h in F['addedFiles'].items():assert sha(current(path))==h,path
for path,x in F['patch'].items():assert sha(current(path))==x['afterSHA256'],path
for path in F['criticalUnchanged']:assert path in F['protected'],path
assert sha(current('audit-reports/maintenance.json'))==F['generatedAuditSHA256']
old=json.loads(F['files']['scripts/ci/manifest.json']['before']);new=json.loads(current('scripts/ci/manifest.json'))
assert new['commands'][:len(old['commands'])]==old['commands']and len(new['commands'])==len(old['commands'])+3
assert new['groups']['top_return']==F['existingRelatedChecks']+F['newChecks']
for k,v in old['groups'].items():assert new['groups'][k]==v
for k in old:
 if k not in ['commands','groups','policy_paths','script_dependencies','scoped_runtime_changes']:assert new[k]==old[k],k
changed=[]
for path,entries in new['scoped_runtime_changes'].items():
 prior=old['scoped_runtime_changes'].get(path,[]);assert entries[:len(prior)]==prior
 for row in entries[len(prior):]:
  x=F['patch'][path];assert row=={'before_sha256':x['beforeSHA256'],'after_sha256':x['afterSHA256'],'groups':['top_return']};changed.append(path)
assert set(changed)==set(F['runtimeFiles'])
if not a.source_only:
 D=R/'dist';tracks=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(tracks)==len(json.loads((R/'tracks.json').read_text()));assert [t['id']for t in tracks]==[t['id']for t in json.loads((R/'tracks.json').read_text())]
 assert(D/'app.js').is_file()and(D/'style.css').is_file()
print('TOP return PASS: frozen patch, unchanged562 catalog/assets/player/core/build, historical inverse/mutation rejection and prior CI registrations preserved.')
