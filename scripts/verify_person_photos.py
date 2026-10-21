"""Exact provided-photo identity, static/SPA parity and untouched catalog proof."""
from pathlib import Path
import argparse,hashlib,html,json,re,subprocess,sys
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from person_photos import photo_feature,photo_header
from approved_person_photos import F,historical_person_photos_file
sha=lambda b:hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--source-only',action='store_true');args=parser.parse_args()
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(historical_person_photos_file(path,raw))==c['beforeSHA256']
 try:historical_person_photos_file(path,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
features=json.loads((R/'features.json').read_text())['features'];features=[f for f in features if f.get('editorial') and f.get('visual',{}).get('precomposed')]
assert len(features)==17
for f in features:
 assert photo_feature(features,f['name'])['id']==f['id'];markup=photo_header(f,'/cratediggin')
 assert markup.count('<figure')==1 and f['visual']['photo'] in markup and f['visual']['tag'] in markup
 assert html.escape(f['visual']['alt'],quote=True) in markup and 'alt="" aria-hidden="true"' in markup
 assert 'loading="lazy"' not in markup and f['visual']['provenance']=='user-provided'
for name,expected in [('J Dilla','j-dilla'),('Jay Dee','j-dilla'),('Quasimoto','madlib'),('The Ummah',None),('Unknown',None),('J Dilla & Madlib',None)]:
 f=photo_feature(features,name);assert (f['id'] if f else None)==expected
# Execute real browser helper in isolation to compare every identity and emitted HTML.
source=(R/'src/app/editorial.js').read_text();helpers=source[source.index(' function personPhotoFeature('):source.index(' function featurePage(')]
names=list(dict.fromkeys([n for f in features for n in [f['name'],*f.get('aliases',[]),*f.get('names',[])]]+['Unknown','J Dilla & Madlib']))
script="const vm=require('node:vm');const d=JSON.parse(require('node:fs').readFileSync(0,'utf8'));const c={publishedFeatures:()=>d.features,origin:'/cratediggin',esc:s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\\"','&quot;').replaceAll(\"'\",'&#x27;')};vm.createContext(c);vm.runInContext(d.helpers,c);console.log(JSON.stringify(d.names.map(n=>({id:c.personPhotoFeature(n)?.id||null,html:c.personPhotoHeader(c.personPhotoFeature(n))}))));"
result=json.loads(subprocess.check_output(['node','-e',script],input=json.dumps(dict(features=features,helpers=helpers,names=names)).encode()))
for name,value in zip(names,result):
 f=photo_feature(features,name);assert value=={'id':f['id'] if f else None,'html':photo_header(f,'/cratediggin')},name
# Preserve all selection/queue code byte for byte: only exact markup insertions and isolated helpers.
player=(R/'src/app/player.js').read_text();before=F['files']['src/app/player.js']['before']
assert player.replace("'+personPhotoHeader(personPhotoFeature(selected))+'","")==before
before=F['files']['src/app/editorial.js']['before']
assert source.replace(helpers,'').replace("'+personPhotoHeader(f)+'","")==before
if not args.source_only:
 from PIL import Image
 class Document(HTMLParser):
  def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
  def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
 D=R/'dist';pages=json.loads((D/'metadata.js').read_text().removeprefix('window.CRATE_PAGES=').strip().removesuffix(';'))
 tracks=json.loads((R/'tracks.json').read_text());assert len(tracks)==506
 for f in features:
  with Image.open(R/'src/assets'/f['visual']['photo']) as im:assert max(im.size)<=2400
  with Image.open(D/'feature-og'/(f['id']+'.jpg')) as im:assert im.size==(1200,630)
  route=pages['#/feature/'+f['id']];text=(D/route['path'].removeprefix('/cratediggin/')).read_text();doc=Document(text)
  assert text.count('class="person-photo-header"')==1 and photo_header(f,'/cratediggin') in text
  assert any(t=='link' and a.get('rel')=='canonical' and a.get('href')==route['url'] for t,a in doc.tags)
  assert '/feature-og/'+f['id']+'.jpg?v=22.24' in route['image']
 for name in sorted({t['artist'] for t in tracks}):
  f=photo_feature(features,name);slug=hashlib.sha256(name.encode()).hexdigest()[:16];text=(D/'artists'/(slug+'.html')).read_text();doc=Document(text)
  assert text.count('class="person-photo-header"')==(1 if f else 0),name
  meta=dict((a.get('property',a.get('name')),a.get('content')) for t,a in doc.tags if t=='meta')
  if f:
   assert photo_header(f,'/cratediggin') in text
   expected='https://djnaoyaman.github.io/cratediggin/feature-og/'+f['id']+'.jpg?v=22.24'
   assert meta['og:image']==meta['twitter:image']==expected
   assert meta['og:image:alt']==meta['twitter:image:alt']==f['visual']['alt']
   graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text).group(1));assert graph['@graph'][0]['image']==expected
  else:assert '/og-image.jpg?' in meta['og:image'],name
  assert 'href="/cratediggin/tracks/' in text,name
 print('Generated17 feature headers, exact-person artist headers/OG/Twitter/JSON-LD, canonical links and untouched unknown identities PASS')
print('Person photo source/identity parity, exact rendering-only delta, catalog/art/queue preservation PASS')
