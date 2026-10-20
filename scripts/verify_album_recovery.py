from pathlib import Path
import json,hashlib
from approved_album_recovery import F,historical_album_recovery_file
from approved_album_bootstrap import historical_album_bootstrap_file
R=Path(__file__).resolve().parents[1]
assert set(F['files'])=={'src/app/album-player.js','releases.json'}
for p,c in F['files'].items():
 b=(R/p).read_bytes();assert historical_album_recovery_file(p,b).decode()==c['before']
 try:historical_album_recovery_file(p,b+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+p)
assert historical_album_recovery_file('unrelated',b'unchanged')==b'unchanged'
a=json.loads(F['files']['releases.json']['before']);a['version']='22.9';assert json.loads(historical_album_bootstrap_file('releases.json',(R/'releases.json').read_bytes()))==a
old=json.loads((R/'scripts/fixtures/approved-album-navigation.json').read_text())
for p,h in old['contentHashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
assert len(json.loads((R/'tracks.json').read_text()))==501
print('Exact album-only recovery correction, mutation rejection and unchanged501 authored records PASS')
