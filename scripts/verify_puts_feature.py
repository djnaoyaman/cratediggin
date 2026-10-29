"""Requested PUTS route/edition contracts; optional one-shot preservation audit."""
import argparse,json,re,subprocess,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import feature_tracks
from artwork_display import measure,assert_normalized
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--generated',action='store_true');ap.add_argument('--preservation');args=ap.parse_args()
read=lambda p:json.loads((ROOT/p).read_text());s=read('tracks.json');by={t['id']:t for t in s};assert len(by)==len(s)
f=next(f for f in read('features.json')['features'] if f['id']=='people-under-the-stairs')
expected={'san-francisco-knights':'xqgJfFbOKnU','the-next-step-ii':'p4IUayilTf4','youth-explosion':'hpdbY2CVH20','code-check':'4tfdcJRpDZo','montego-slay':'e9_xZ4jeyh0','the-la-song':'p4H1S4J852Y','acid-raindrops':'UcKDx4cmvio','the-break-down':'gnGqlvvsgbg'}
assert f['listeningOrder']==['people-under-the-stairs-'+x for x in expected]
for slug,video in expected.items():
 t=by['people-under-the-stairs-'+slug];assert t['youtube']['id']==video and t['youtube']['official'] and 'Topic' in t['youtube']['channel']
assert by['people-under-the-stairs-san-francisco-knights']['year']==1998
assert by['people-under-the-stairs-youth-explosion']['year']==2000
acid=by['people-under-the-stairs-acid-raindrops'];assert acid['year']==2002 and acid['selectedRelease']['year']==2003
assert 'duration' not in acid['youtube'] and '4分56秒' not in ''.join(acid['essay'])
for key in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified','exactMixMasterVerified']:assert acid['youtube'][key] is False
for slug,video in [('schooled-in-the-trade-instrumental','ZqpqMKKrbJs'),('sunroof-instrumental','8TBVH6XRVaI')]:
 id='people-under-the-stairs-'+slug;assert by[id]['youtube']['id']==video and id not in f['listeningOrder']
selected=feature_tracks(s,f);assert len(selected)>=16 and f['type']=='artist';v=f['visual'];assert not v.get('nameOnly') and v['photo']=='feature-people-under-the-stairs-provided-collage.webp'
assert v['precomposed'] and v['fit']=='contain' and v['provenance']=='user-provided'
assert hashlib.sha256((ROOT/'src/assets'/v['photo']).read_bytes()).hexdigest()=='998eedce796b3b878b268beafc0e28bd8f97a53d94cedd14a0c88a205d3cbc95'
with Image.open(ROOT/'src/assets'/v['photo']) as photo:
 photo.load();assert photo.size==(1376,864);assert not photo.getexif();assert not any(k in photo.info for k in ['exif','xmp','icc_profile'])
for section in f['editorial']['sections']:
 for paragraph in section['paragraphs']:
  for id in re.findall(r'\(#/song/([a-z0-9-]+)\)',paragraph):assert id in by,id
with Image.open(ROOT/'src/assets'/f['visual']['tag']) as im:im.load();assert_normalized(measure(im));assert im.getchannel('A').getextrema()[0]==0
assert hashlib.sha256((ROOT/'src/assets'/f['visual']['tag']).read_bytes()).hexdigest()=='60c0b1ecaec1baa045d89535aeb0e74b6177ac46132e493d8980af750499cbe9'
if args.preservation:
 prior=lambda p:json.loads(subprocess.check_output(['git','show',args.preservation+':'+p],cwd=ROOT))
 old=prior('tracks.json');assert len(old)==len(s);assert set(by)=={t['id'] for t in old}
 for t in old:
  if t['id']==acid['id']:assert t['art']==acid['art'] and t['year']==acid['year']
  else:assert by[t['id']]==t,t['id']
 assert [x for x in read('features.json')['features'] if x['id']!=f['id']]==[x for x in prior('features.json')['features'] if x['id']!=f['id']]
 old_feature=next(x for x in prior('features.json')['features'] if x['id']==f['id']);assert {k:v for k,v in f.items() if k!='visual'}=={k:v for k,v in old_feature.items() if k!='visual'}
 assert old==s, 'Photo update must preserve all track data'
 assert read('graffiti_artwork.json')==prior('graffiti_artwork.json')
 for p in subprocess.check_output(['git','ls-tree','-r','--name-only',args.preservation,'assets','src/assets'],cwd=ROOT,text=True).splitlines():
  if Path(p).suffix.lower() in ['.webp','.png','.jpg','.jpeg']:assert subprocess.check_output(['git','hash-object',p],cwd=ROOT)==subprocess.check_output(['git','rev-parse',args.preservation+':'+p],cwd=ROOT),p
if args.generated:
 page=(ROOT/'dist/artists/people-under-the-stairs.html').read_text();assert v['photo'] in page and 'person-photo-header' in page;assert f['visual']['tag'] in page and 'feature-listening-route' in page and f'収録作品 {len(selected)}曲' in page
 assert 'UcKDx4cmvio' in (ROOT/'dist/tracks/people-under-the-stairs-acid-raindrops.html').read_text()
 assert 'feature-og/people-under-the-stairs.jpg' in page
 with Image.open(ROOT/'dist/feature-og/people-under-the-stairs.jpg') as og:og.load();assert og.size==(1200,630)
 for section in f['editorial']['sections']:assert section['heading'] in page
 for p in ['dist/artists/index.html','dist/sitemap.xml','dist/llms.txt']:assert f['id'] in (ROOT/p).read_text()
print(f'PUTS PASS: {len(selected)} works, eight licensed Topic route selections, original years, protected selections and tag')
