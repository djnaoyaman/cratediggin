from pathlib import Path
import json,hashlib
from approved_simple_content_ci import F,sha,historical_simple_content_ci_file as undo,current_simple_content_ci_file as current
R=Path(__file__).resolve().parents[1]
assert sha((R/'scripts/fixtures/approved-simple-content-ci.json').read_bytes())=='e76e0cf8f476adb0dc370e5985e4a8db9488a29ec1f8bdec659610f0adf8803b'
for path,c in F['files'].items():
 data=(R/path).read_bytes()
 assert undo(path,data)==c['before'].encode(),path
 try:undo(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unknown drift accepted: '+path)
for path,h in {**F['protected'],**F['newFiles']}.items():assert sha(current(path,(R/path).read_bytes()))==h,path
assert undo('unrelated.txt',b'unchanged')==b'unchanged'
old=json.loads(F['files']['scripts/ci/manifest.json']['before']);new=json.loads(current('scripts/ci/manifest.json',(R/'scripts/ci/manifest.json').read_bytes()))
assert new['commands'][:-1]==old['commands']
for key,items in old['groups'].items():
 assert new['groups'][key]==items+(['simple-content-ci-preservation'] if key=='policy' else [])
assert len(json.loads(current('tracks.json',(R/'tracks.json').read_bytes())))==522
print('Exact data-only CI classification delta; all522 authored records/UI/Node24 security and historical fixtures unchanged; negative drift guards PASS')
