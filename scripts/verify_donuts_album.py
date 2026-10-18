"""One aggregate album, not a substitute song or inflated song count."""
import json,re,sys,html as html_parser
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import validate_work,work_count
tracks=json.loads((ROOT/'tracks.json').read_text());by={t['id']:t for t in tracks};t=by['j-dilla-donuts'];y=t['youtube'];validate_work(t)
assert t['workType']=='album' and t['countsTowardDailyNewSongs'] is False
assert y['sourceType']=='playlist' and y['playlistId']=='OLAK5uy_m8VPjbn9rF3ninCB-n_ToxxHH5U3_TkvE' and not y.get('id')
expected=json.loads((ROOT/'scripts/fixtures/donuts-playlist-order.json').read_text());assert y['url']==expected['playlistUrl']
seq=t['playlistSequence'];assert [{k:x[k] for k in ('index','videoId','title')} for x in seq]==expected['items'];assert len(seq)==31 and [x['index'] for x in seq]==list(range(1,32))
assert seq[0]['title']=='Donuts (Outro)' and seq[-1]['title']=='Welcome To The Show' and seq[3]['title']=='Light It'
assert all(re.fullmatch(r'[A-Za-z0-9_-]{11}',x['videoId']) and x['metadataVerified'] for x in seq)
assert len(t['essay'])==6 and len(t['essaySources'])==6 and all(0<=i<len(t['sources']) for ids in t['essaySources'] for i in ids)
assert not any(x.get('youtube') for x in t['samples'])
for id in t['relatedTrackIds']:assert id in by and by[id].get('workType','single')=='single' and by[id]['youtube']['id']
sections=next(x['sections'] for x in json.loads((ROOT/'editorial_deepdives.json').read_text()) if x['artist']=='J Dilla' and x['title']=='Donuts');assert len(sections)==5
for d in sections:assert all(0<=i<len(t['sources']) for i in d['sources'])
html=(ROOT/'dist/tracks/j-dilla-donuts.html').read_text();md=(ROOT/'dist/tracks/j-dilla-donuts.md').read_text()
assert 'アルバム全体' in html and 'ALBUM SEQUENCE' in html and 'ALBUM SEQUENCE' in md
for item in seq:assert item['title'] in html_parser.unescape(html) and item['title'] in md
for d in sections:assert d['heading'] in html
ld=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)[1]);album=next(x for x in ld['@graph'] if x['@type']=='MusicAlbum')
assert album['numTracks']==31 and album['albumProductionType']=='https://schema.org/StudioAlbum' and 'inAlbum' not in album
assert not any(x['@type']=='MusicRecording' for x in ld['@graph'])
a=json.loads((ROOT/'graffiti_artwork.json').read_text());art=next(x for x in a['tracks'] if x['id']==t['id']);im=Image.open(ROOT/art['image']);assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
assert work_count([t])=='0曲・1アルバム'
print('Donuts whole-album identity,31-item order,6 essays/5 sourced sections,existing individual routes,MusicAlbum and true-alpha art passed; playback not certified')
