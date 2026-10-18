"""Build-time source gate: strict video identity or validated whole-album playlist."""
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import validate_work
tracks=json.loads((ROOT/'tracks.json').read_text(encoding='utf-8'))
assert tracks, 'Catalog must not be empty'
assert any(t['id']=='dj-shadow-the-number-song' for t in tracks), 'The Number Song missing from source'
assert (ROOT/'dist/tracks/dj-shadow-the-number-song.html').exists(), 'The Number Song page missing from build'
assert 'dj-shadow-the-number-song' in (ROOT/'dist/tracks.js').read_text(encoding='utf-8'), 'The Number Song missing from client catalog'
expected_audio={'dj-shadow-the-number-song':'odlhSQqOXL8','dj-shadow-the-number-song-cut-chemist-remix':'c0CKXOCOX3o'}
for track_id,video_id in expected_audio.items():
 track=next(t for t in tracks if t['id']==track_id)
 assert track['youtube']['id']==video_id, f'Incorrect audio: {track_id}'
 assert (ROOT/f'dist/tracks/{track_id}.html').exists()
for t in tracks:
 validate_work(t);y=t.get('youtube',{})
 if y.get('sourceType','video')=='playlist':
  seq=t.get('playlistSequence',[])
  assert seq and [x['index'] for x in seq]==list(range(1,len(seq)+1)), f'Missing or unordered album sequence: {t["id"]}'
  assert all(re.fullmatch(r'[A-Za-z0-9_-]{11}',x.get('videoId','')) for x in seq), f'Invalid album constituent ID: {t["id"]}'
  assert len({x['videoId'] for x in seq})==len(seq), f'Duplicate album constituent: {t["id"]}'
 else:
  assert re.fullmatch(r'[A-Za-z0-9_-]{11}',y.get('id','')), f'Missing catalog video: {t["id"]}'
print('Both Number Song versions and all strict video/native-album source identities verified')
