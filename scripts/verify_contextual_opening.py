from approved_brand_identity import historical_brand_social_digest
from approved_requested_two import historical_intake_tracks, historical_intake_file
"""Exact21.12 content/art preservation around a bounded opening-selection change."""
from pathlib import Path
import hashlib,json
from approved_contextual_opening import FIXTURE as F,historical_opening_file
R=Path(__file__).resolve().parents[1];D=R/'dist';sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(F['files'])=={'src/app/order.json','src/app/player.js','src/app/router.js','src/app/catalog-ui.js','src/app/renewal.js','src/assets/style.css','templates/index.html'}
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert historical_opening_file(path,data)==c['before'].encode()
 try:historical_opening_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved source accepted: '+path)
for path,h in F['protected'].items():assert sha(historical_intake_file(path,(R/path).read_bytes()))==h,path
assert len(historical_intake_tracks())==499
assert json.loads(historical_intake_file('releases.json',(R/'releases.json').read_bytes()))['version']=='21.13'
assert len(F['socialImages'])==517
if D.exists():
 for path,h in F['socialImages'].items():assert historical_brand_social_digest(path,(D/path).read_bytes())==h,path
 index=(D/'index.html').read_text();assert 'id="now-title">曲を選んでください' in index
 assert 'window.CrateOpening' not in index
 print('All517 delivered social images byte-identical')
for path in ['src/app/opening.js','src/app/opening-selection.js']:
 s=(R/path).read_text();assert not any(x in s for x in ['fetch(','geolocation','navigator.share','loadSong(','playVideo(','loadVideoById(','Math.random'])
assert 'now(cur);route();' in (R/'src/app/router.js').read_text()
print('Exact499 records/prose/photos/art preserved; seven approved UI/integration deltas and isolated local selection only')
