"""Fourteen exact supplied collages, no editorial/media drift or silent licensing claims."""
from pathlib import Path
import json,hashlib,copy,io
from PIL import Image
from approved_browser_tools import historical_browser_tools_file
from approved_photo_replacement import FIXTURE as f,historical_photo_file
R=Path(__file__).resolve().parents[1];D=R/'dist';sha=lambda b:hashlib.sha256(b).hexdigest()
ids={'dj-shadow','j-dilla','madlib','pete-rock','erick-sermon','tribe','gang-starr','public-enemy','nas','az','de-la-soul','beastie-boys','main-source','epmd'}
assert {a['id'] for a in f['assets']}==ids
for p,c in f['files'].items():assert historical_photo_file(p,(R/p).read_bytes())==c['before'].encode()
for p,h in f['protected'].items():assert sha(historical_browser_tools_file(p,(R/p).read_bytes()))==h,p
old=json.loads(f['files']['features.json']['before']);new=json.loads((R/'features.json').read_text());norm=copy.deepcopy(new)
assert len(new['features'])==15
for item in norm['features']:
 previous=next(x for x in old['features'] if x['id']==item['id'])
 if item['id'] in ids:
  v=item['visual'];assert v['precomposed'] and v['fit']=='contain' and v['provenance']=='user-provided' and v['credit']=='ユーザー提供'
  assert v['tag']==previous['visual']['tag'];assert not any(k in v for k in ['license','licenseUrl','author','source'])
  item['visual']=previous['visual']
assert norm==old,'Feature prose, roles, personal photos or tags changed'
retired=json.loads((R/'retired_feature_photos.json').read_text())['paths'];assert set(retired)=={a['retiredPublicPath'] for a in f['assets'] if a['retiredPublicPath']}
for a in f['assets']:
 p=R/a['path'];assert sha(p.read_bytes())==a['sha256']
 if a['retiredPublicPath']:assert sha((R/'src/assets'/a['retiredPublicPath']).read_bytes())==a['retiredSourceSHA256']
 with Image.open(p) as im:assert im.size==(1456,816) and sha(im.convert('RGBA').tobytes())==a['pixelSHA256']
 if D.exists():
  if a['retiredPublicPath']:assert not (D/a['retiredPublicPath']).exists()
  with Image.open(D/p.name) as im:assert im.size==(1456,816) and sha(im.convert('RGBA').tobytes())==a['pixelSHA256']
  with Image.open(D/'feature-og'/f"{a['id']}.jpg") as im:assert im.size==(1200,630) and im.format=='JPEG' and im.mode=='RGB'
  import sys;sys.path.insert(0,str(R));from brand_assets import SOCIAL_PAPER
  canvas=Image.new('RGB',(1200,630),SOCIAL_PAPER)
  with Image.open(p) as original:
   art=original.convert('RGBA');art.thumbnail((1200,630),Image.Resampling.LANCZOS)
   assert art.size==(1124,630),'Unexpected crop/scale'
   canvas.paste(art,(38,0),art)
  expected=io.BytesIO();canvas.save(expected,format='JPEG',quality=95,subsampling=0,optimize=True)
  assert (D/'feature-og'/f"{a['id']}.jpg").read_bytes()==expected.getvalue(),'Full-containment OGP composition mismatch'
  for group in ['features','producers','artists']:
   page=D/group/(a['id']+'.html')
   if page.exists():
    text=page.read_text()
    if group=='features':assert 'rel="canonical"' in text and ('/producers/'+a['id']+'.html' in text or '/artists/'+a['id']+'.html' in text)
    else:assert 'feature-og/'+a['id']+'.jpg' in text and 'image/jpeg' in text
  pages=json.loads((D/'metadata.js').read_text().split('=',1)[1].rstrip(';\n'))
  meta=pages['#/feature/'+a['id']];assert meta['image'].endswith('/feature-og/'+a['id']+'.jpg?v='+json.loads((R/'releases.json').read_text())['version'])
  canonical=D/meta['path'].removeprefix('/cratediggin/')
  text=canonical.read_text();assert meta['image'] in text and 'image/jpeg' in text
  graph=json.loads((D/meta['metadataPath'].removeprefix('/cratediggin/')).read_text())
  assert meta['image'] in json.dumps(graph)
assert len(f['unchangedSocialImages'])==500
for path,h in f['unchangedSocialImages'].items():assert sha((D/path).read_bytes())==h,path
# No public file may point to a retired producer photo.
for p in D.rglob('*'):
 if p.is_file() and p.suffix in {'.html','.js','.json','.md','.xml'}:
  text=p.read_text()
  assert not any(name in text for name in retired),'Retired reference: '+str(p)
# A changed approved renderer must not be normalized silently.
for p,c in f['files'].items():
 try:historical_photo_file(p,(R/p).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Mutation accepted: '+p)
print('Fourteen exact full-composition collages; original source backups,499 catalog/media and all15 feature prose/tags preserved; exact OGP encoding and retirement gates PASS')
