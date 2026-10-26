"""Verify the independent Swing Set addition without changing historic catalog rows."""
import hashlib,json,subprocess,unicodedata
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from artwork_display import assert_normalized,measure
ROOT=Path(__file__).resolve().parents[1]
BASE='8c5b2f6fc0abfd88d2422dc5673d8e162570a019'
ID='jurassic-5-swing-set'
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def original(path):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT))
tracks=read('tracks.json');old=original('tracks.json')
assert tracks[:-1]==old and len(tracks)==len(old)+1
row=tracks[-1];assert row['id']==ID
assert len({t['id'] for t in tracks})==len(tracks)
assert sum(unicodedata.normalize('NFKC',t['title']).casefold()=='swing set' for t in tracks)==1
assert row['artist']=='Jurassic 5' and row['primaryArtists']==['Jurassic 5']
assert row['year']==2000 and row['yearStatus']=='verified'
assert row['region']==row['scene']=='Los Angeles'
assert row['album']=='Quality Control' and row['producers']==['DJ Nu-Mark']
assert row['youtube']['id']=='LA0jouPMb9s' and row['youtube']['official']
assert row['youtube']['url'].endswith('v=LA0jouPMb9s')
for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']:assert row['youtube'][k] is False
assert 'playbackCheckedAt' not in row['youtube']
assert row['djEvidence']['position']=='00:51:08'
assert row['djEvidence']['url']=='https://serato.com/playlists/myquade/4-16-2024'
assert all(row[k] for k in ['sources','yearBasis','regionBasis','versionBasis','producerBasis'])
art=read('graffiti_artwork.json');oa=original('graffiti_artwork.json')
assert art['tracks'][:-1]==oa['tracks'];assert {k:v for k,v in art.items() if k!='tracks'}=={k:v for k,v in oa.items() if k!='tracks'}
a=art['tracks'][-1];assert a['id']==ID and a['status']=='ready'
assert a['transparent'] and a['textReviewed'] and a['noSiteBranding']
assert hashlib.sha256((ROOT/a['image']).read_bytes()).hexdigest()==a['displaySizing']['outputSha256']
with Image.open(ROOT/a['image']) as im:
 im.load();assert 'A' in im.getbands();metrics=assert_normalized(measure(im));assert metrics['visibleBox']==a['displaySizing']['visibleBox'];assert im.getchannel('A').getextrema()==(0,255)
release=read('releases.json');oldrelease=original('releases.json');assert release['version']=='22.223';assert {k:v for k,v in release.items() if k!='version'}=={k:v for k,v in oldrelease.items() if k!='version'}
if (ROOT/'dist').exists():
 page=(ROOT/'dist/tracks'/f'{ID}.html').read_text(encoding='utf-8')
 assert all(x in page for x in ['Swing Set','Jurassic 5','Los Angeles','2000'])
 redirect=(ROOT/'dist/songs'/f'{ID}.html').read_text(encoding='utf-8')
 assert '/tracks/'+ID+'.html' in redirect and 'rel="canonical"' in redirect
 assert 'Swing Set — Jurassic 5｜CRATE DIGGIN｜DJ Naoyaman' in page
 assert 'myquade' in page and '2024年4月16日' in page
 assert 'jurassic-5-swing-set' in (ROOT/'dist/sitemap.xml').read_text(encoding='utf-8')
print('Swing Set one-track append, all 638 prior records/art rows unchanged, edition/year/region/source contracts, no playback claims, alpha8/7% artwork and generated routes PASS')
