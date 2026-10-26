"""Guard one DJ-evidenced addition and preserve all 639 preceding works."""
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from artwork_display import assert_normalized, measure

BASE = 'a70ade12b82816da6b23e4018a62ed2b46f82fe8'
ID = 'people-under-the-stairs-montego-slay'
def read(path): return json.loads((ROOT/path).read_text())
def original(path): return json.loads(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT))

rows, old = read('tracks.json'), original('tracks.json')
assert len(old) == 639 and len(rows) == 640 and rows[:-1] == old
t = rows[-1]
assert t['id'] == ID and len({x['id'] for x in rows}) == len(rows)
assert sum(unicodedata.normalize('NFKC', x['title']).casefold() == 'montego slay' for x in rows) == 1
assert t['artist'] == 'People Under the Stairs' and t['primaryArtists'] == [t['artist']]
assert t['year'] == 2002 and t['yearStatus'] == 'verified' and t['yearQualifier'] == '原盤年'
assert t['region'] == t['scene'] == 'Los Angeles' and t['regionSources'] == [0]
assert t['album'] == 'O.S.T.' and t['catalogDuration'] == '4:12'
assert t['producer'] is None and t['producers'] == [] and t['producerBasis']
y = t['youtube']
assert y['id'] == 'e9_xZ4jeyh0' and y['official'] and y['channel'] == 'PEOPLE UNDER THE STAIRS - Topic'
assert y['duration'] == '4:12' and y['versionBasis'] == t['versionBasis']
assert '2003-06-02' in t['versionBasis']
for key in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']:
    assert y[key] is False
assert 'playbackCheckedAt' not in y
assert t['djEvidence']['position'] == '01:21:58' and t['djEvidence']['date'] == '2026-09-23'
assert t['djEvidence']['url'] == 'https://serato.com/playlists/djtbird/lyrics-rhymes-vibes-september-2026'
assert t['sources'][1]['url'] == t['djEvidence']['url']
assert t['essaySources'] == [[1],[0,1]] and len(t['essay']) == 2
assert t['samples'] == [] and t['addedOrder'] == 633

art, old_art = read('graffiti_artwork.json'), original('graffiti_artwork.json')
assert art['tracks'][:-1] == old_art['tracks']
assert {k:v for k,v in art.items() if k != 'tracks'} == {k:v for k,v in old_art.items() if k != 'tracks'}
a = art['tracks'][-1]
assert a['id'] == ID and a['status'] == 'ready'
assert all(a[k] for k in ['transparent','textReviewed','paletteReviewed','noSiteBranding'])
sizing = a['displaySizing']
assert hashlib.sha256((ROOT/a['image']).read_bytes()).hexdigest() == sizing['outputSha256']
assert hashlib.sha256((ROOT/a['originalImage']).read_bytes()).hexdigest() == sizing['sourceSha256']
with Image.open(ROOT/a['image']) as out, Image.open(ROOT/a['originalImage']) as source:
    out.load(); source.load()
    metrics = assert_normalized(measure(out))
    assert metrics['visibleBox'] == sizing['visibleBox'] and out.size == (1809,1021)
    assert out.getchannel('A').getextrema() == (0,255)
    assert source.convert('RGBA').crop((38,48,1593,925)).tobytes() == out.convert('RGBA').crop((127,72,1682,949)).tobytes()
release, prior = read('releases.json'), original('releases.json')
assert release['version'] == '22.227'
assert {k:v for k,v in release.items() if k != 'version'} == {k:v for k,v in prior.items() if k != 'version'}
for p in ['src/app/router.js','src/app/art-modes.js','src/assets/style.css','.github/workflows/pages.yml','artwork_display_legacy.json']:
    assert (ROOT/p).read_bytes() == subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT),p

if '--generated' in sys.argv:
    page = (ROOT/f'dist/tracks/{ID}.html').read_text()
    assert all(x in page for x in ['Montego Slay','People Under the Stairs','Los Angeles','2002','2003年6月2日','e9_xZ4jeyh0','T-Bird','2026年9月23日'])
    assert 'Montego Slay — People Under the Stairs｜CRATE DIGGIN｜DJ Naoyaman' in page
    assert '利用者の環境で再生確認済み' not in page
    assert '/tracks/'+ID+'.html' in (ROOT/f'dist/songs/{ID}.html').read_text()
    assert ID in (ROOT/'dist/sitemap.xml').read_text()
    assert y['url'] in (ROOT/f'dist/songs/{ID}.md').read_text()
print('Montego Slay one-track append; all 639 previous tracks/art and HYBRID preserved; year/region/DJ/edition/alpha8-7%/original-pixel contracts PASS')
