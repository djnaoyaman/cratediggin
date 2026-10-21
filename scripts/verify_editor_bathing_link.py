from pathlib import Path
import argparse,json,html,sys
from approved_editor_bathing_link import F,sha,historical_editor_bathing_link_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from profile_content import render_profile
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(historical_editor_bathing_link_file(path,raw))==c['beforeSHA256']
 for bad in [raw+b' ',c['before'].encode()]:
  try:historical_editor_bathing_link_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unexpected profile drift accepted')
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
old=json.loads(F['files']['editor_profile.json']['before']);now=json.load(open(R/'editor_profile.json'));expected=json.loads(json.dumps(old));expected['blocks'].insert(F['insertIndex'],F['paragraph']);assert now==expected
assert old['blocks'][F['insertIndex']]['text'].startswith('[掌蹠膿疱症.com]');assert now['blocks'][:19]==old['blocks'][:19]
markup=render_profile(R,'/cratediggin');assert markup.count(F['url'])==1;assert '＃酸冷交代浴のススメ' in markup;assert markup.count('class="editor-photo ')==2
if not a.source_only:
 page=(R/'dist/editor.html').read_text();assert page.count(F['url'])==1;assert page.index(F['url'])<page.index('https://djnaoyaman.github.io/ppp/about.html');assert F['url'] in (R/'dist/app.js').read_text();assert F['url'] not in (R/'dist/about.html').read_text()
print('One EDITOR site paragraph/link, exact all-prior-block/photo/catalog preservation, negative drift and static/SPA projection PASS')
