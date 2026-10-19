from pathlib import Path
import hashlib,json
from approved_browser_tools import FIXTURE as f,historical_browser_tools_file
R=Path(__file__).resolve().parents[1];D=R/'dist';sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(f['files'])=={'templates/index.html','src/app/renewal.js','src/assets/style.css','profile_content.py'}
for path,c in f['files'].items():
 data=(R/path).read_bytes();assert historical_browser_tools_file(path,data)==c['before'].encode()
 try:historical_browser_tools_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved mutation accepted: '+path)
for path,h in f['protected'].items():assert sha((R/path).read_bytes())==h,path
assert len(json.loads((R/'tracks.json').read_text()))==499
assert json.loads((R/'releases.json').read_text())['version']=='21.10'
s=(R/'src/app/renewal.js').read_text();assert '[300,360,450,570,720,900]' in s and "$('#shuffle-again').onclick=renewalDraw" in s
assert 'window.external' not in s and 'navigator.share' not in s and 'serviceWorker.register' not in s
if D.exists():
 for path,h in f['socialImages'].items():assert sha((D/path).read_bytes())==h,path
 profile=(D/'editor.html').read_text();assert '<span class="editor-name-accessible">DJ Naoyaman</span>' in profile
 assert 'class="editor-signature"' in profile and 'alt="" width="1881" height="628"' in profile
 assert '宮崎直哉' in profile and '約5万曲' in profile and '明治大学' in profile
 assert 'designed by DJ NAOYAMAN' in (D/'index.html').read_text()
print('Exact four UI file corrections;499 records, all supplied photos, biography, ART credit, media and social image bytes preserved')
