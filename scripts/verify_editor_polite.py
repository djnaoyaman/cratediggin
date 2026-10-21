from pathlib import Path
from approved_editor_polite import F,sha,historical_editor_polite_file
import json,re,sys,html,subprocess
R=Path(__file__).resolve().parents[1];P=R;B=R;sys.path.insert(0,str(R));from profile_content import render_profile,polite_editor_note,EDITOR_NOTE_REPLACEMENTS
packet=json.loads((R/'scripts/fixtures/editor-polite-prose.json').read_text());old=packet['beforeProfile'];new=json.loads((R/'editor_profile.json').read_text());expected=json.loads(json.dumps(old))
for x in packet['replacements']:assert expected['blocks'][x['index']]==x['before'];expected['blocks'][x['index']]=x['after']
assert expected==new and old['blocks'][:19]==new['blocks'][:19]
assert re.findall(r'https://[^)]+',json.dumps(old))==re.findall(r'https://[^)]+',json.dumps(new))
for i,b in enumerate(old['blocks']):
 if b['type'].startswith('h'):assert new['blocks'][i]==b
rendered=render_profile(R,'/cratediggin');assert all(html.escape(b['text']) in rendered for b in new['blocks'] if b['type']=='p' and '[' not in b['text']);assert rendered.count('class="editor-photo ')==2
live=(R/'templates/index.html').read_text();changed=polite_editor_note(live)
pattern=r'<section class="manifesto">.*?</section>';assert re.sub(pattern,'',live,flags=re.S)==re.sub(pattern,'',changed,flags=re.S)
assert polite_editor_note(changed)==changed
for before,after in EDITOR_NOTE_REPLACEMENTS:assert after in changed;assert before not in re.search(pattern,changed,re.S)[0]
assert "if route == '#/editor':\n            content = __import__('profile_content').polite_editor_note(content)" in (R/'discovery.py').read_text()
js=(R/'src/app/editorial.js').read_text();helper=js[js.index(' function refreshEditorNote('):js.index(' function editor(){')];baseps=re.findall(r'<p>(.*?)</p>',re.search(pattern,live,re.S)[0],re.S);vm="const vm=require('vm'),assert=require('node:assert/strict');const originals="+json.dumps(baseps,ensure_ascii=False)+";const nodes=originals.map(innerHTML=>({innerHTML}));const c={editorNoteReplacements:"+json.dumps(EDITOR_NOTE_REPLACEMENTS,ensure_ascii=False)+",document:{querySelectorAll:s=>{assert.equal(s,'.manifesto p');return nodes}}};vm.createContext(c);vm.runInContext("+json.dumps(helper)+",c);for(const route of ['#/editor','#/about','#/editor','#/song/a','#/editor','#/editor','#/']){c.refreshEditorNote(route);const expected=originals.map(s=>route==='#/editor'?c.editorNoteReplacements.reduce((v,[a,b])=>v.split(a).join(b),s):s);assert.deepEqual(nodes.map(n=>n.innerHTML),expected)}console.log('Actual SPA note helper restores original copy on route exit and is idempotent.');";subprocess.run(['node','-e',vm],check=True)
assert 'function refreshRenewalPresentation(hash){refreshEditorNote(hash);' in (R/'src/app/renewal.js').read_text()
from render_editorial import about_html
about=about_html(R,json.loads((R/'tracks.json').read_text()));assert 'SAMPLED MIND.' in about and '{{EDITOR_NOTE_REPLACEMENTS}}' not in about
print('Actual About static renderer excludes EDITOR-only token and executes successfully.')
import hashlib
for path,digest in packet['protected'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==digest,path
print('Exact17 prose blocks, supplied14 paragraphs/headings/links/photos preserved; real profile renderer; actual static full-page note isolation and SPA enter/exit/repeat helpers PASS. Browser not run.')

for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(historical_editor_polite_file(path,raw))==c['beforeSHA256']
 for bad in [raw+b' ',c['before'].encode()]:
  try:historical_editor_polite_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved drift accepted')
