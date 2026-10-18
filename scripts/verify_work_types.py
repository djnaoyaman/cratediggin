"""Work labels preserve single-song accounting; native album playlist sources validate exact identity."""
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
album={'workType':'album','youtube':{'sourceType':'playlist','playlistId':'PLabc','url':'https://www.youtube.com/playlist?list=PLabc'}}
validate_work(album)
assert work_count([s,m,album])=='1曲・1ミックス作品・1アルバム'
for url in ['https://www.youtube.com/playlist?list=WRONG','https://evil.example/playlist?list=PLabc','http://www.youtube.com/playlist?list=PLabc','https://www.youtube.com/watch?list=PLabc']:
 try:validate_work(dict(album,youtube=dict(album['youtube'],url=url)))
 except AssertionError:pass
 else:raise AssertionError('Bad playlist URL accepted')
print('Work type validation and separate song/mix accounting passed; native playlist schema validated, no playback claim')
