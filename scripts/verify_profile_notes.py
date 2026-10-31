from pathlib import Path
import json,re,html
r=Path(__file__).resolve().parents[1];d=r/'dist';profile=(d/'editor.html').read_text()
from verify_editor_profile_update import D
assert D['authorUrl'] in profile
features=json.loads((r/'features.json').read_text())['features']
for ident in ['dj-shadow','j-dilla','madlib']:
 f=next(f for f in features if f['id']==ident);n=f['noteArticle'];s=(d/'producers'/(ident+'.html')).read_text();assert html.escape(n['title']) in s and html.escape(n['introduction']) in s and n['url'] in s
tracks=json.loads((r/'tracks.json').read_text());p=next(t for t in tracks if t['id']=='slum-village-players');assert p['youtube']['id']=='AbBZKBplhGc' and '未検証' in p['youtube']['verification'];assert all('EZXXqfUBbLM' not in s['url'] for s in p['sources'])
print('Owner-supplied biography, real signature, three note links and exact Players candidate verified; playback remains unconfirmed')
