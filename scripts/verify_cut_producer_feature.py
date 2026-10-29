"""Producer-role/edition/tag contracts without freezing unrelated future changes."""
import argparse,json,re,subprocess,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import feature_tracks,work_count
from artwork_display import measure,assert_normalized
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--generated',action='store_true');ap.add_argument('--preservation');args=ap.parse_args()
read=lambda p:json.loads((ROOT/p).read_text());s=read('tracks.json');by={t['id']:t for t in s};assert len(by)==len(s)
f=next(f for f in read('features.json')['features'] if f['id']=='cut-chemist');assert f['type']=='producer' and f['names']==['Cut Chemist']
route=['jurassic-5-lesson-4-the-radio','jurassic-5-lesson-6-the-lecture','jurassic-5-quality-control','jurassic-5-swing-set','dj-shadow-the-number-song-cut-chemist-remix','cut-chemist-bunkys-pick','cut-chemist-storm','cut-chemist-the-garden'];assert f['listeningOrder']==route
videos=['uqq6Yg-2XC0','bcOv_eBmaSk','PgpDN-bARwc','LA0jouPMb9s','c0CKXOCOX3o','U5Kj6P-fMt0','1N1RkAebVwo','tmxf-qHAtyE']
for id,video in zip(route,videos):
 t=by[id];assert t['youtube']['id']==video and t['youtube']['official'];assert 'Cut Chemist' in t['producers']
assert by[route[0]]['artist']=='Jurassic 5' and by[route[0]]['originalArtist']=='Cut Chemist'
assert by[route[0]]['selectedRelease']['year']==2008 and by[route[0]]['earliestDocumentedRelease']['year']==1995
assert by[route[1]]['producers']==['Cut Chemist'] and '2016' in by[route[1]]['producerBasis']
assert by[route[3]]['producers']==['Cut Chemist','DJ Nu-Mark']
assert by[route[4]]['yearQualifier']=='原曲の年'
assert by[route[5]]['workType']=='mix'
assert by[route[2]]['youtube']['channel']=='Jurassic5VEVO' and by[route[7]]['youtube']['channel']=='Cut Chemist - Topic'
selected=feature_tracks(s,f);assert set(route)<=set(t['id'] for t in selected)
v=f['visual'];assert not v.get('nameOnly') and v['photo']=='feature-cut-chemist-provided-collage.webp'
assert v['precomposed'] and v['fit']=='contain' and v['provenance']=='user-provided'
assert hashlib.sha256((ROOT/'src/assets'/v['photo']).read_bytes()).hexdigest()=='fa1455d6449eb1fd33d0e73f018be9ffb3b66c2eed32b380b478bd293f2a185f'
with Image.open(ROOT/'src/assets'/v['photo']) as photo:
 photo.load();assert photo.size==(1376,864);assert not photo.getexif();assert not any(k in photo.info for k in ['exif','xmp','icc_profile'])
for section in f['editorial']['sections']:
 for paragraph in section['paragraphs']:
  for id in re.findall(r'\(#/song/([a-z0-9-]+)\)',paragraph):assert id in by,id
with Image.open(ROOT/'src/assets'/f['visual']['tag']) as im:im.load();assert_normalized(measure(im));assert im.getchannel('A').getextrema()[0]==0
if args.preservation:
 prior=lambda p:json.loads(subprocess.check_output(['git','show',args.preservation+':'+p],cwd=ROOT))
 old=prior('tracks.json');assert len(old)==len(s);assert set(by)=={t['id'] for t in old}
 changed={'jurassic-5-swing-set','jurassic-5-lesson-6-the-lecture','dj-shadow-the-number-song-cut-chemist-remix','jurassic-5-quality-control','cut-chemist-the-garden'}
 for t in old:
  now=by[t['id']];assert now['art']==t['art'] and now.get('youtube',{}).get('id')==t.get('youtube',{}).get('id')
  if t['id'] not in changed:assert now==t,t['id']
 assert [x for x in read('features.json')['features'] if x['id']!=f['id']]==[x for x in prior('features.json')['features'] if x['id']!=f['id']]
 old_feature=next(x for x in prior('features.json')['features'] if x['id']==f['id']);assert {k:v for k,v in f.items() if k!='visual'}=={k:v for k,v in old_feature.items() if k!='visual'}
 assert old==s, 'Photo update must preserve all track data'
 assert read('graffiti_artwork.json')==prior('graffiti_artwork.json')
 for p in subprocess.check_output(['git','ls-tree','-r','--name-only',args.preservation,'assets','src/assets'],cwd=ROOT,text=True).splitlines():
  if Path(p).suffix.lower() in ['.webp','.png','.jpg','.jpeg']:assert subprocess.check_output(['git','hash-object',p],cwd=ROOT)==subprocess.check_output(['git','rev-parse',args.preservation+':'+p],cwd=ROOT),p
if args.generated:
 page=(ROOT/'dist/producers/cut-chemist.html').read_text();assert v['photo'] in page and 'person-photo-header' in page;assert f['visual']['tag'] in page and 'feature-listening-route' in page and '収録作品 '+work_count(selected) in page
 assert 'feature-og/cut-chemist.jpg' in page
 with Image.open(ROOT/'dist/feature-og/cut-chemist.jpg') as og:og.load();assert og.size==(1200,630)
 for section in f['editorial']['sections']:assert section['heading'] in page
 for p in ['dist/producers/index.html','dist/sitemap.xml','dist/llms.txt']:assert f['id'] in (ROOT/p).read_text()
print(f'Cut producer PASS: {work_count(selected)}, eight role-verified route works, original/selected editions distinguished')
