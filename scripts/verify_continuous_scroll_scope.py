"""Exact approved scrolling patch and unchanged catalog/transport/source guard."""
from pathlib import Path
import argparse,json,hashlib
from approved_continuous_scroll import F,current_continuous_scroll_file,historical_continuous_scroll_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
def current(path):return current_continuous_scroll_file(path,(R/path).read_bytes())
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():assert sha(current(path))==h,path
assert len(json.loads(current('tracks.json')))==F['count']==562
assert json.loads(current('releases.json'))['version']==F['afterVersion']=='22.171'
assert sha(current(F['previousHelper']['path']))==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(current_continuous_scroll_file(path,data))==c['afterSHA256'],path
 assert sha(historical_continuous_scroll_file(path,data))==c['beforeSHA256'],path
 for mutated in [data+b' ',data[:-1]]:
  try:historical_continuous_scroll_file(path,mutated)
  except AssertionError:pass
  else:raise AssertionError('Unapproved drift accepted: '+path)
for path,h in F['addedFiles'].items():assert sha(current(path))==h,path
for path,x in F['patch'].items():assert sha(current(path))==x['afterSHA256']
for path in ['tracks.json','graffiti_artwork.json','artist_entities.json','src/app/player.js','src/app/core.js','build.py','audit-reports/maintenance.json']:assert path in F['protected']
assert sha(current('audit-reports/maintenance.json'))==F['generatedAuditSHA256']
# All pre-existing command records remain identical; narrowly add two explicit guards.
old=json.loads(F['files']['scripts/ci/manifest.json']['before']);new=json.loads(current('scripts/ci/manifest.json'))
assert new['commands'][:len(old['commands'])]==old['commands'] and len(new['commands'])==len(old['commands'])+2
assert new['groups']['continuous_scroll']==F['existingRelatedChecks']+['continuous-scroll-model','continuous-scroll-scope']
for k,v in old['groups'].items():assert new['groups'][k]==v
for k in old:
 if k not in ['commands','groups','policy_paths','script_dependencies','scoped_runtime_changes']:assert new[k]==old[k],k
for path,entries in old['scoped_runtime_changes'].items():assert new['scoped_runtime_changes'][path][:len(entries)]==entries
for path in F['runtimeFiles']:
 x=F['patch'][path];assert new['scoped_runtime_changes'][path][-1]=={'before_sha256':x['beforeSHA256'],'after_sha256':x['afterSHA256'],'groups':['continuous_scroll']}
if not a.source_only:
 D=R/'dist';tracks=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(tracks)==len(json.loads((R/'tracks.json').read_text()));assert [t['id']for t in tracks]==[t['id']for t in json.loads((R/'tracks.json').read_text())]
 assert (D/'app.js').is_file()and(D/'style.css').is_file()
 assert 'resultLimit=restoredResultLimit(browseRestoring)'in(D/'app.js').read_text()
print('Continuous scrolling: exact approved patch, prior562 catalog/assets/player/core/build, strict historical inverse/mutation rejection and unchanged CI registrations PASS.')
