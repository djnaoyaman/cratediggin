"""Work labels preserve single-song accounting; unsupported playlist sources fail closed."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import work_type,work_label,work_count,validate_work
tracks=json.loads((ROOT/'tracks.json').read_text())
for t in tracks:validate_work(t)
s={'youtube':{'id':'abcdefghijk','url':'https://www.youtube.com/watch?v=abcdefghijk'}}
m=dict(s,workType='mix')
assert work_type(s)=='single' and work_label(m)=='DJミックス作品'
assert work_count([s,m])=='1曲・1ミックス作品'
assert work_count([s])=='1曲'
for invalid in [dict(s,workType='bogus'),dict(s,workType='album'),{'youtube':dict(s['youtube'],sourceType='playlist',playlistId='PLabc')},{'youtube':dict(s['youtube'],playlistId='PLabc')},{'youtube':dict(s['youtube'],url='https://www.youtube.com/watch?v=wrongwrong1')}]:
 try:validate_work(invalid)
 except AssertionError:pass
 else:raise AssertionError('Invalid or unsupported source was accepted')
print('Work type validation and separate song/mix accounting passed; no playlist or playback claim')
