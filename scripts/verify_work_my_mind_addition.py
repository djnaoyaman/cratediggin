"""Guard one DJ-evidenced addition and preserve all 640 preceding works."""
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from artwork_display import assert_normalized,measure
BASE='884100e5ef6009ba408f00e35696d198ba3d3687'
ID='cut-chemist-work-my-mind'
def read(path):return json.loads((ROOT/path).read_text())
def original(path):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT))
rows,old=read('tracks.json'),original('tracks.json')
assert len(old)==640 and len(rows)==641 and rows[:-1]==old
assert len({x['id'] for x in rows})==641
assert sum('work my mind' in unicodedata.normalize('NFKC',x['title']).casefold() for x in rows)==1
t=rows[-1];assert t['id']==ID
assert t['artist']=='Cut Chemist' and t['primaryArtists']==['Cut Chemist']
assert t['featuredArtists']==['Chali 2na','Hymnal']
assert t['artists']==['Cut Chemist','Chali 2na','Hymnal']
assert t['year']==2017 and t['yearStatus']=='verified' and t['yearQualifier']=='シングル初出年'
assert '2018年3月2日' in t['yearDisplayNote']
assert t['region']==t['scene']=='Los Angeles' and t['regionSources']==[1]
assert t['album']=='Die Cut' and t['catalogDuration']=='3:38'
assert t['producer'] is None and t['producers']==[] and t['producerBasis']
y=t['youtube'];assert y['id']=='zmYXYlCeUYE' and y['official'] and y['channel']=='Cut Chemist'
assert y['channelUrl']=='https://www.youtube.com/@OfficialCutChemist'
assert y['duration']=='3:38' and y['versionBasis']==t['versionBasis']
for key in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']:assert y[key] is False
assert 'playbackCheckedAt' not in y
assert t['djEvidence']['position']=='00:51:57' and t['djEvidence']['date']=='2022-07-06'
assert t['djEvidence']['url']=='https://serato.com/playlists/Sim_Ca/warm-up-1'
assert t['sources'][3]['url']==t['djEvidence']['url']
assert t['essaySources']==[[3],[0,1,2]] and len(t['essay'])==2
assert t['samples'][0]['title']=='Alternative Fresh' and t['samples'][0]['artist']=='Vox Populi!'
assert t['samples'][0]['year'] is None and 'youtube' not in t['samples'][0]
assert t['addedOrder']==634
art,prior_art=read('graffiti_artwork.json'),original('graffiti_artwork.json')
assert art['tracks'][:-1]==prior_art['tracks']
assert {k:v for k,v in art.items() if k!='tracks'}=={k:v for k,v in prior_art.items() if k!='tracks'}
a=art['tracks'][-1];assert a['id']==ID and a['status']=='ready'
assert all(a[k] for k in ['transparent','textReviewed','paletteReviewed','noSiteBranding'])
s=a['displaySizing']
assert hashlib.sha256((ROOT/a['image']).read_bytes()).hexdigest()==s['outputSha256']
assert hashlib.sha256((ROOT/a['originalImage']).read_bytes()).hexdigest()==s['sourceSha256']
with Image.open(ROOT/a['image']) as out,Image.open(ROOT/a['originalImage']) as source:
 out.load();source.load();metrics=assert_normalized(measure(out))
 assert metrics['visibleBox']==s['visibleBox'] and out.size==(1860,978)
 assert out.getchannel('A').getextrema()==(0,255)
 assert source.convert('RGBA').crop((41,57,1639,897)).tobytes()==out.convert('RGBA').crop((131,69,1729,909)).tobytes()
release,prior=read('releases.json'),original('releases.json')
assert release['version']=='22.228'
assert {k:v for k,v in release.items() if k!='version'}=={k:v for k,v in prior.items() if k!='version'}
for p in ['src/app/router.js','src/app/art-modes.js','src/assets/style.css','.github/workflows/pages.yml','artwork_display_legacy.json']:
 assert (ROOT/p).read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=ROOT),p
# No existing asset may change; source blobs are compared without decoding.
for p in subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'assets'],cwd=ROOT,text=True).splitlines():
 assert subprocess.check_output(['git','hash-object',p],cwd=ROOT,text=True).strip()==subprocess.check_output(['git','rev-parse',f'{BASE}:{p}'],cwd=ROOT,text=True).strip(),p
if '--generated' in sys.argv:
 page=(ROOT/f'dist/tracks/{ID}.html').read_text()
 for text in ['Work My Mind','Cut Chemist','Chali 2na','Hymnal','Los Angeles','2017','2018年3月2日','zmYXYlCeUYE','Sim Ca','2022年7月6日','Alternative Fresh']:
  assert text in page,text
 assert 'Work My Mind (feat. Chali 2na &amp; Hymnal) — Cut Chemist｜CRATE DIGGIN｜DJ Naoyaman' in page
 assert '利用者の環境で再生確認済み' not in page
 assert ID in (ROOT/'dist/sitemap.xml').read_text()
 assert y['url'] in (ROOT/f'dist/songs/{ID}.md').read_text()
print('Work My Mind: 641-track append; all prior 640 records/art/assets, audio fixes and HYBRID preserved; metadata/alpha8-7%/original pixels PASS')
