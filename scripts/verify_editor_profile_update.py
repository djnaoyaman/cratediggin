"""Exact owner-supplied paragraphs and unchanged biography tail/photo rendering."""
from pathlib import Path
from approved_editor_polite import historical_editor_polite_file
import argparse,hashlib,json,sys,html
from approved_editor_profile_update import F,historical_editor_profile_file,sha
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for name,spec in F['files'].items():
 raw=(R/name).read_bytes();assert sha(historical_editor_profile_file(name,raw))==spec['beforeSHA256']
 for bad in [raw+b' ',spec['before'].encode()]:
  try:historical_editor_profile_file(name,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved profile drift accepted')
for name,h in F['protected'].items():assert sha(historical_editor_polite_file(name,(R/name).read_bytes()))==h,name
old=json.loads(F['files']['editor_profile.json']['before']);new=json.loads(historical_editor_polite_file('editor_profile.json',(R/'editor_profile.json').read_bytes()));assert {k:v for k,v in new.items() if k!='blocks'}=={k:v for k,v in old.items() if k!='blocks'}
assert new['blocks']==[old['blocks'][0]]+F['requestedBlocks']+F['preservedTail']
assert len(F['requestedBlocks'])==17 and sum(b['type']=='h2' for b in F['requestedBlocks'])==3
assert [b['text'] for b in F['requestedBlocks'] if b['type']=='h2']==['音楽を掘る。記憶を編む。','はじまりは、足立区の15歳','作ることへのこだわり']
sys.path.insert(0,str(R));from profile_content import render_profile
rendered=render_profile(R,'/cratediggin')
for b in F['requestedBlocks']:assert '<'+b['type']+'>'+html.escape(b['text'])+'</'+b['type']+'>' in rendered
assert rendered.count('class="editor-photo ')==2 and 'editor-signature' in rendered and rendered.count('<h1>')==1
assert rendered.index(F['requestedBlocks'][-1]['text'])<rendered.index('editor-photo--event')<rendered.index('約5万曲のクレートから')
if not a.source_only:
 page=(R/'dist/editor.html').read_text()
 for b in F['requestedBlocks']:assert html.escape(b['text']) in page,b['text']
 assert new['signature'] in page and 'editor-provided-collage.webp' in page and 'editor-provided-event.jpg' in page
print('Exact 3 headings/14 paragraphs; later biography, identity, 2 photos and 505 works unchanged; real profile renderer and negative drift checks PASS'+(' (source-only)' if a.source_only else ', generated Editor PASS'))
