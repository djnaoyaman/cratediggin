"""Current compact profile contract; historical biography requirements are superseded."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from profile_content import render_profile
D=json.loads((R/'editor_profile.json').read_text());s=render_profile(R,'/cratediggin')
assert D['name']=='DJ Naoyaman' and 'realName' not in D
assert len(D['blocks'])==4 and len(D['description'])<150
assert D['authorUrl']=='https://djnaoyaman.github.io/profile.html'
for bad in ['宮崎直哉','15歳','足立区','叔父','学歴','講演','約5万曲','32年','模試','ブランドと地域','creator-site']:
 assert bad not in s,bad
assert s.count('<a ')==1 and D['authorUrl'] in s
assert s.count('class="editor-photo ')==2 and 'editor-signature' in s
assert '<details class="editor-photo-archive">' in s
if '--source-only' not in sys.argv and (R/'dist/editor.html').exists():
 from validate_site import validate_profile
 validate_profile(R)
print('Current compact profile source, one author link and preserved photos PASS')
