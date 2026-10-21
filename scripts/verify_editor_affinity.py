from pathlib import Path
import argparse,hashlib,html,json,sys
from approved_halftime import historical_halftime_file
from approved_editor_affinity import F,historical_editor_affinity_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from profile_content import render_profile
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');args=p.parse_args();sha=lambda b:hashlib.sha256(b).hexdigest()
for name,c in F['files'].items():
 raw=(R/name).read_bytes();assert sha(historical_editor_affinity_file(name,raw))==c['beforeSHA256']
 try:historical_editor_affinity_file(name,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted')
for name,digest in F['protected'].items():assert sha(historical_halftime_file(name,(R/name).read_bytes()))==digest,name
before=json.loads(F['files']['editor_profile.json']['before']);after=json.loads((R/'editor_profile.json').read_text());expected=json.loads(json.dumps(before));expected['blocks'].insert(4,F['paragraph']);assert after==expected
assert before['blocks'][3]['text'].startswith('好きな言葉は「MIXWELL」')
assert after['blocks'][5]['text'].startswith('本業は、ブランディングやマーケティング。')
rendered=render_profile(R,'/cratediggin');assert rendered.count(html.escape(F['paragraph']['text']))==1
assert rendered.count('class="editor-photo ')==2
if not args.source_only:
 page=(R/'dist/editor.html').read_text();assert page.count(html.escape(F['paragraph']['text']))==1
 assert page.index(html.escape(before['blocks'][3]['text']))<page.index(html.escape(F['paragraph']['text']))<page.index(html.escape(before['blocks'][4]['text']))
 assert F['paragraph']['text'] in (R/'dist/app.js').read_text()
 assert F['paragraph']['text'] not in (R/'dist/about.html').read_text()
print('One EDITOR preference paragraph after MIXWELL, all prior blocks/photos/catalog exact; static and frontend projection PASS')
