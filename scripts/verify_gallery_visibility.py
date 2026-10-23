from pathlib import Path
import json,argparse
from approved_gallery_visibility import F,sha,current_gallery_visibility_file as current,historical_gallery_visibility_file as undo
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args();read=lambda path:current(path,(R/path).read_bytes())
for path,h in F['protected'].items():
 allowed={h}
 if path=='audit-reports/maintenance.json' and not a.source_only:allowed.add('fedf57151b58e5bb71899ece7a8f1f7ee3a440b4094f0adde69b25f2ec21d827')
 assert sha(read(path)) in allowed,path
ph=F['previousHelper'];assert sha(read(ph['path']))==ph['afterSHA256']
for path,c in F['files'].items():
 assert sha(undo(path,(R/path).read_bytes()))==c['beforeSHA256']
 try:undo(path,(R/path).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
css=read('src/assets/style.css').decode();before=F['files']['src/assets/style.css']['before'];assert css==before.replace(F['oldSelector'],F['newSelector'],1)
assert F['oldSelector'] not in css and css.count(F['newSelector'])==1
assert len(json.loads(read('tracks.json')))==F['count']==562
assert json.loads(read('releases.json'))==dict(json.loads(F['files']['releases.json']['before']),version=F['afterVersion'])
if not a.source_only:assert (R/'dist/style.css').read_bytes()==read('src/assets/style.css')
print('Exact gallery-only figure selector specificity repair; all562 records, images, runtime, compact/home styles and original test assertions protected PASS')
