from pathlib import Path
import hashlib,json
from approved_album_navigation import historical_album_navigation_file
R=Path(__file__).resolve().parents[1];F=json.loads((R/'scripts/fixtures/approved-album-navigation.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
expected={'src/app/'+f+'.js' for f in ['album-player','player','router','playlist-ui','catalog-ui','song-ui','inline-player']}|{'releases.json'}
assert set(F['files'])==expected
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_album_navigation_file(path,data))==c['beforeSHA256']
 try:historical_album_navigation_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted: '+path)
assert historical_album_navigation_file('unrelated.txt',b'unchanged')==b'unchanged'
for path,h in F['contentHashes'].items():assert sha((R/path).read_bytes())==h,path
assert len(json.loads((R/'tracks.json').read_text()))==501
print('Exact album-navigation delta; all501 authored work/media records, features and deep dives unchanged; negative drift cases PASS')
