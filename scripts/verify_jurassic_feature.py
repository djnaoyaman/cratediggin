"""Protect requested J5 editions, tag-led feature, and unrelated catalog assets."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import feature_tracks
from artwork_display import measure,assert_normalized
from PIL import Image
BASE='5db099cfa8a8fb66f0f4a63eb3ff507b02388fda'
def read(f):return json.loads((ROOT/f).read_text())
def prior(f):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{f}'],cwd=ROOT))
s=read('tracks.json');by={t['id']:t for t in s}
assert len(s)==len(by)
preservation='--preservation' in sys.argv
if preservation:
 old=prior('tracks.json')
 assert len(old)==641 and len(s)==646
for t in (old if preservation else []):
 if t['id']=='jurassic-5-jayou':
  now=by[t['id']]
  for k in ['id','title','artist','art','essay','essayTitle','samples','listening','datePublished']:assert now[k]==t[k],k
 else:assert by[t['id']]==t,t['id']
required={'the-game':'n1Q958eWCxA','lausd':'JjyUI40Umg8','contact':'egtB6CzGkHY','canto-de-ossanha':'-dZQgvRMFIA','jayou-remix':'pSUeddnqv6o'}
if preservation:assert {t['id'] for t in s}-{t['id'] for t in old}=={'jurassic-5-'+x for x in required}
for slug,video in required.items():
 t=by['jurassic-5-'+slug];assert t['artist']=='Jurassic 5'
 assert t['youtube']['id']==video and t['youtube']['userSelected'] is True
 assert t['youtube']['official'] is True and 'Topic' in t['youtube']['channel']
 for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']:assert t['youtube'][k] is False
 assert 'playbackCheckedAt' not in t['youtube']
 assert 'DJ' not in t.get('djEvidence',{})
assert by['jurassic-5-jayou']['youtube']['id']=='2ZuN8rc6y7s'
assert by['jurassic-5-lausd']['producers']==['Cut Chemist']
assert by['jurassic-5-contact']['producers']==['Cut Chemist']
assert by['jurassic-5-the-game']['producers']==['Cut Chemist','DJ Nu-Mark']
assert by['jurassic-5-canto-de-ossanha']['producers']==['DJ Nu-Mark']
assert by['jurassic-5-jayou-remix']['yearQualifier']=='選択した収録版の年'
if preservation:
 assert by['jurassic-5-lesson-4-the-radio']['artist']=='Cut Chemist'
 assert by['jurassic-5-lesson-4-the-radio']['youtube']['id']=='uqq6Yg-2XC0'
 for slug,vid in [('schooled-in-the-trade-instrumental','ZqpqMKKrbJs'),('sunroof-instrumental','8TBVH6XRVaI')]:assert by['people-under-the-stairs-'+slug]['youtube']['id']==vid
fdata=read('features.json')
f=next(f for f in fdata['features'] if f['id']=='jurassic-5');assert f['names']==['Jurassic 5']
if preservation:
 fold=prior('features.json');assert [x for x in fdata['features'] if x['id']!='jurassic-5']==fold['features']
selected=feature_tracks(s,f);assert len(selected)>=23
if preservation:assert 'jurassic-5-lesson-4-the-radio' not in {t['id'] for t in selected}
assert set(f['listeningOrder'])<=set(t['id'] for t in selected)
assert len(f['listeningOrder'])==len(set(f['listeningOrder']))==9
assert f['listeningOrder'][0]=='jurassic-5-the-game' and f['listeningOrder'][-1]=='jurassic-5-canto-de-ossanha'
v=f['visual'];assert not v.get('nameOnly') and v['photo']=='feature-jurassic-5-provided-collage.webp'
assert v['precomposed'] and v['fit']=='contain' and v['provenance']=='user-provided'
assert hashlib.sha256((ROOT/'src/assets'/v['photo']).read_bytes()).hexdigest()=='410e447ae4be7ef65eedb94bdeb04a6425a07313dc06a506f19fedb646eeff39'
with Image.open(ROOT/'src/assets'/v['photo']) as photo:
 photo.load();assert photo.size==(1376,864);assert not photo.getexif();assert not any(k in photo.info for k in ['exif','xmp','icc_profile'])
if '--photo-preservation' in sys.argv:
 base=sys.argv[sys.argv.index('--photo-preservation')+1]
 before=lambda file:json.loads(subprocess.check_output(['git','show',base+':'+file],cwd=ROOT))
 assert read('tracks.json')==before('tracks.json') and read('graffiti_artwork.json')==before('graffiti_artwork.json')
 previous=before('features.json')['features'];assert [x for x in fdata['features'] if x['id']!='jurassic-5']==[x for x in previous if x['id']!='jurassic-5']
 oldfeature=next(x for x in previous if x['id']=='jurassic-5');assert {k:v for k,v in f.items() if k!='visual'}=={k:v for k,v in oldfeature.items() if k!='visual'}
for section in f['editorial']['sections']:
 for text in section['paragraphs']:
  for tid in re.findall(r'\(#/song/([a-z0-9-]+)\)',text):assert tid in by,tid
art=read('graffiti_artwork.json')
if preservation:
 original=prior('graffiti_artwork.json');assert art['tracks'][:len(original['tracks'])]==original['tracks']
 assert len(art['tracks'])==len(original['tracks'])+5
for a in (a for a in art['tracks'] if a['id'] in {'jurassic-5-'+x for x in required}):
 assert a['status']=='ready' and all(a[k] for k in ['transparent','textReviewed','paletteReviewed','noSiteBranding'])
 assert a['palette']==by[a['id']]['art']['palette'] and a['paletteSource']==by[a['id']]['art']['paletteSource']
 with Image.open(ROOT/a['image']) as im:im.load();assert_normalized(measure(im));assert im.getchannel('A').getextrema()[0]==0
 assert hashlib.sha256((ROOT/a['image']).read_bytes()).hexdigest()==a['displaySizing']['outputSha256']
with Image.open(ROOT/'src/assets'/f['visual']['tag']) as im:im.load();assert_normalized(measure(im))
# One-shot release audit, deliberately not a permanent CI freeze.
if preservation:
 # No existing image or photo can be altered in this release.
 existing_assets=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'assets','src/assets'],cwd=ROOT,text=True).splitlines()
 for path in existing_assets:
  if Path(path).suffix.lower() not in ['.webp','.png','.jpg','.jpeg']:continue
  before=subprocess.check_output(['git','rev-parse',f'{BASE}:{path}'],cwd=ROOT,text=True).strip()
  assert subprocess.check_output(['git','hash-object',path],cwd=ROOT,text=True).strip()==before,path
 for path in ['src/app/art-modes.js','src/app/player.js','src/app/router.js','artwork_display_legacy.json']:
  assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path
if '--generated' in sys.argv:
 page=(ROOT/'dist/artists/jurassic-5.html').read_text()
 assert 'data-photo-person="jurassic-5"' in page and f['visual']['tag'] in page and v['photo'] in page
 assert 'feature-og/jurassic-5.jpg' in page
 with Image.open(ROOT/'dist/feature-og/jurassic-5.jpg') as og:og.load();assert og.size==(1200,630)
 assert 'feature-listening-route' in page and f'収録作品 {len(selected)}曲' in page
 for sec in f['editorial']['sections']:assert sec['heading'] in page
 assert '写真準備中' not in page and 'placeholder' not in page
 for slug,vid in required.items():
  text=(ROOT/f'dist/tracks/jurassic-5-{slug}.html').read_text();assert vid in text
  assert 'Designed by' in text and 'DJ Naoyaman' in text
 for index in ['dist/artists/index.html','dist/sitemap.xml','dist/llms.txt']:assert 'jurassic-5' in (ROOT/index).read_text()
print(f'J5 feature PASS: {len(s)} works, {len(selected)} J5; requested editions, route, tag and credits' + ('; base-641 preservation audit PASS' if preservation else ''))
