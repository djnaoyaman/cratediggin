from pathlib import Path
import hashlib,json
from approved_shuffle_scope import historical_shuffle_scope_file
R=Path(__file__).resolve().parents[1];F=json.loads((R/'scripts/fixtures/approved-shuffle-scope.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(F['files'])=={'src/app/renewal.js','src/app/catalog-ui.js','releases.json','.github/workflows/pages.yml'}
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_shuffle_scope_file(path,data))==c['beforeSHA256']
 try:historical_shuffle_scope_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unexpected drift accepted: '+path)
for name,key in [('tracks.json','tracksSHA256'),('features.json','featuresSHA256'),('editorial_deepdives.json','deepdivesSHA256')]:assert sha((R/name).read_bytes())==F[key],name
assert len(json.loads((R/'tracks.json').read_text()))==501
release=json.loads((R/'releases.json').read_text());assert release==dict(json.loads(F['files']['releases.json']['before']),version='22.3')
assert historical_shuffle_scope_file('unrelated.txt',b'unchanged')==b'unchanged'
print('Exact shuffle invalidation delta; all501 records, feature/deep prose unchanged; historical asset/OGP gates retained')
