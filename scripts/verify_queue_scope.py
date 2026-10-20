from approved_brand_identity import historical_brand_social_digest
from pathlib import Path
import json,hashlib
from approved_album_navigation import historical_album_navigation_file
from approved_queue_scope import historical_queue_scope_file
from approved_shuffle_scope import historical_shuffle_scope_file
R=Path(__file__).resolve().parents[1];F=json.loads((R/'scripts/fixtures/approved-queue-scope.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert len(json.loads((R/'tracks.json').read_text()))==501
assert [t['id'] for t in json.loads((R/'tracks.json').read_text())]==F['orderedIds']
for path,h in F['protected'].items():assert sha(historical_shuffle_scope_file(path,(R/path).read_bytes()))==h,path
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_queue_scope_file(path,data))==c['beforeSHA256']
 try:historical_queue_scope_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted: '+path)
old=F['files']['src/app/playlist-ui.js']['before'];new=historical_album_navigation_file('src/app/playlist-ui.js',(R/'src/app/playlist-ui.js').read_bytes()).decode()
assert new==old.replace('queueCustom=customMode;queue=playableIds(filtered)','queueCustom=customMode;queueScope=filtered.map(t=>t.id);queue=playableIds(filtered)',1)
release=json.loads(historical_shuffle_scope_file('releases.json',(R/'releases.json').read_bytes()));assert release==dict(json.loads(F['files']['releases.json']['before']),version='22.2')
assert historical_queue_scope_file('unrelated.txt',b'unchanged')==b'unchanged'
if (R/'dist').exists():
 for path,h in F['socialImages'].items():assert historical_brand_social_digest(path,(R/'dist'/path).read_bytes())==h,path
 assert len(F['socialImages'])==519
print('Exact one-branch queue scope correction;501 content/media/art and519 OGP preserved; drift rejection PASS')
