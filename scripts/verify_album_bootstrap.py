from pathlib import Path
import hashlib,json
from approved_album_bootstrap import F,historical_album_bootstrap_file
R=Path(__file__).resolve().parents[1]
assert hashlib.sha256((R/'scripts/fixtures/youtube-video-id-validation.json').read_bytes()).hexdigest()==F['providerContractSHA256']
assert set(F['files'])=={'src/app/player.js','releases.json'}
for p,c in F['files'].items():
 b=(R/p).read_bytes();assert historical_album_bootstrap_file(p,b).decode()==c['before']
 try:historical_album_bootstrap_file(p,b+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+p)
old="videoId:songs[cur]?.youtube?.id||undefined,"
new="...(songs[cur]?.youtube?.id?{videoId:songs[cur].youtube.id}:{}),"
a=F['files']['src/app/player.js']['before'];assert a.count(old)==1;assert a.replace(old,new)==(R/'src/app/player.js').read_text()
a=json.loads(F['files']['releases.json']['before']);a['version']='22.10';assert json.loads((R/'releases.json').read_text())==a
print('Exact optional videoId omission only, source mutation rejection and release bookkeeping PASS')
