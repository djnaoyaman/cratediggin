"""Guard the user's single-video replacement and preserve the other 638 works."""
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'b5fd3e10d5d107ccc12d92ced0bb08519ba9bad1'
ID = 'people-under-the-stairs-sunroof-instrumental'
VIDEO = '8TBVH6XRVaI'
OLD = 'dtddzkG67IE'
def read(p): return json.loads((ROOT/p).read_text())
def old(p): return json.loads(subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT))
rows, before = read('tracks.json'), old('tracks.json')
assert len(rows) == len(before) == 639
assert [x for x in rows if x['id'] != ID] == [x for x in before if x['id'] != ID]
t, b = next(x for x in rows if x['id']==ID), next(x for x in before if x['id']==ID)
assert {k:v for k,v in t.items() if k not in {'youtube','versionBasis','sources'}} == {k:v for k,v in b.items() if k not in {'youtube','versionBasis','sources'}}
assert t['sources'][:5] == b['sources'][:5] and len(t['sources']) == len(b['sources']) == 6
y = t['youtube']
assert y['id']==VIDEO and y['url']=='https://www.youtube.com/watch?v='+VIDEO and y['embedUrl']=='https://www.youtube.com/embed/'+VIDEO
assert y['official'] is False and y['officialStatus']=='unofficial' and y['type']=='一般投稿'
assert y['channel']=='SteveSpliffler' and y['channelUrl']=='https://www.youtube.com/@SteveSpliffler'
assert y['reportedVideoDuration']=='5:29' and t['catalogDuration']=='5:28'
for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']: assert y[k] is False
assert 'playbackCheckedAt' not in y and OLD not in json.dumps(t)
assert t['sources'][5]['url']==y['url'] and t['versionBasis']==y['versionBasis']
release = read('releases.json'); prior = old('releases.json')
assert release['version']=='22.226'
assert {k:v for k,v in release.items() if k!='version'}=={k:v for k,v in prior.items() if k!='version'}
for p in ['graffiti_artwork.json','src/app/router.js','src/app/art-modes.js','src/assets/style.css','.github/workflows/pages.yml']:
    assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT),p
if (ROOT/'dist').exists():
    js=(ROOT/'dist/tracks.js').read_text(); generated=json.loads(js.split('window.TRACKS = ',1)[1].rstrip().removesuffix(';'))
    assert next(x for x in generated if x['id']==ID)['youtube']==y
    for p in [f'dist/tracks/{ID}.html',f'dist/songs/{ID}.md']:
        s=(ROOT/p).read_text(); assert y['url'] in s and OLD not in s and 'SteveSpliffler' in s
        assert '利用者の環境で再生確認済み' not in s
print('Sunroof exact requested video/uploader, edition/art/HYBRID and638other works unchanged; no playback claims PASS')
