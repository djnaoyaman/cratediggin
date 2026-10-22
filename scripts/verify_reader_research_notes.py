from pathlib import Path
import json,sys,argparse,html,copy,tempfile
from approved_reader_research_notes import F,sha,historical_reader_research_notes_file as undo
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from article_research import load_notes,render_notice,markdown_notice,CLOSING
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
assert sha((R/'scripts/fixtures/approved-reader-research-notes.json').read_bytes())=='f89ab4e3fdebe9962b9a261f856329efac4284989a2f7e3acd8015a1fbedc309'
tracks=json.loads((R/'tracks.json').read_text());notes=load_notes(R,tracks);assert notes==F['notes'] and len(notes)==11
from approved_lost_in_thought import F as ADDED
def assert_added(rows):
 assert len(rows)==522 and rows[-1]==ADDED['track'] and sum(t['id']==ADDED['track']['id'] for t in rows)==1
assert_added(tracks);assert ADDED['track']['id'] not in notes
for invalid in [tracks[:-1],tracks+[tracks[-1]],json.loads(json.dumps(tracks))]:
 if len(invalid)==522:invalid[-1]['title']+=' changed'
 try:assert_added(invalid)
 except AssertionError:pass
 else:raise AssertionError('Added song mutation accepted')
for p,h in F['preserved'].items():assert sha((R/p).read_bytes())==h,p
for p,c in F['files'].items():
 raw=(R/p).read_bytes();assert undo(p,raw)==(c['before'].encode() if c['before'] is not None else b'')
 try:undo(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Mutation accepted')
assert 'editorialStatus' not in (R/'article_research.py').read_text()
for id,note in notes.items():assert set(note)=={'missingEvidence'} and '新材料' not in note['missingEvidence']
assert render_notice({})==markdown_notice({})==''
x={'articleResearch':{'missingEvidence':'<script>&"'}};assert '<script>' not in render_notice(x) and '&lt;script&gt;' in render_notice(x)
with tempfile.TemporaryDirectory() as temp:
 root=Path(temp)
 for bad in [{'unknown':{'missingEvidence':'x'}},{tracks[0]['id']:{'missingEvidence':''}},{tracks[0]['id']:{'missingEvidence':'x','editorialStatus':'x'}}]:
  (root/'article_research_notes.json').write_text(json.dumps(bad))
  try:load_notes(root,tracks)
  except AssertionError:pass
  else:raise AssertionError('Invalid notice data accepted')
if not a.source_only:
 D=R/'dist';s=(D/'tracks.js').read_text();projected=json.loads(s.split('window.TRACKS = ',1)[1].strip().removesuffix(';'))
 assert {t['id'] for t in projected if 'articleResearch' in t}==set(notes)
 for t in projected:
  note=notes.get(t['id']);page=html.unescape((D/f"tracks/{t['id']}.html").read_text());md=(D/f"songs/{t['id']}.md").read_text()
  assert ('class="article-research-note"' in page)==bool(note)
  if note:
   assert t['articleResearch']==note and note['missingEvidence'] in page and note['missingEvidence'] in md and CLOSING in page and CLOSING in md
  else:assert '\n## 要調査\n' not in md and CLOSING not in md
  source=next(x for x in tracks if x['id']==t['id'])
  for k in ['editorialStatus','essay','essayTitle','deck','context','listening','facts','sources','samples','youtube']:assert t.get(k)==source.get(k)
print('11 bounded missing-evidence notes; 511 absent; authored content/media status unchanged; escaping/schema/negative guards PASS'+(' source-only' if a.source_only else ' static/Markdown/projected data'))
