from pathlib import Path
import argparse,json,html,sys
from approved_editor_bathing_byline import F,sha,historical_editor_bathing_byline_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from profile_content import render_profile
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(historical_editor_bathing_byline_file(path,raw))==c['beforeSHA256']
 for bad in [raw+b' ',c['before'].encode()]:
  try:historical_editor_bathing_byline_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unexpected profile drift accepted')
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
old=json.loads(F['files']['editor_profile.json']['before']);now=json.load(open(R/'editor_profile.json'));expected=json.loads(json.dumps(old));expected['blocks'][F['insertIndex']]=F['paragraph'];expected['blocks'][F['patientIndex']]=F['patientParagraph'];assert now==expected
assert F['paragraph']['text']=='湯気文吾名義で、'+old['blocks'][F['insertIndex']]['text'];assert F['patientParagraph']['text']=='「患者の会代表」というペンネームで制作している'+old['blocks'][F['patientIndex']]['text'];assert now['blocks'][:19]==old['blocks'][:19]
markup=render_profile(R,'/cratediggin');assert markup.count(F['url'])==1;assert '＃酸冷交代浴のススメ' in markup and '湯気文吾名義で、' in markup and '「患者の会代表」というペンネームで制作している' in markup;assert markup.count('class="editor-photo ')==2
if not a.source_only:
 page=(R/'dist/editor.html').read_text();assert page.count(F['url'])==1;assert page.index(F['url'])<page.index('https://djnaoyaman.github.io/ppp/about.html');assert F['url'] in (R/'dist/app.js').read_text();assert F['url'] not in (R/'dist/about.html').read_text()
print('Two EDITOR pen-name prefixes, exact all-prior-block/photo/catalog preservation, negative drift and static/SPA projection PASS')
