from approved_requested_two import historical_intake_tracks, historical_intake_file
"""Preserve published21.11 exactly except the approved helper UI, gallery restoration and supplied photos."""
from pathlib import Path
import json,hashlib,sys,io
R=Path(__file__).resolve().parents[1];D=R/'dist';sys.path.insert(0,str(R))
from approved_home_install_direct import FIXTURE as F,historical_home_install_file
from PIL import Image
from approved_contextual_opening import historical_opening_file
sha=lambda b:hashlib.sha256(b).hexdigest()
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert historical_home_install_file(path,data)==c['before'].encode()
 try:historical_home_install_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved mutation accepted: '+path)
for path,h in F['protected'].items():assert sha(historical_opening_file(path,(R/path).read_bytes()))==h,path
before=json.loads(F['files']['features.json']['before']);current=json.loads(__import__('approved_artifacts_credits').historical_credit_file('features.json',(R/'features.json').read_bytes()));assert current['policy']==before['policy'];assert len(current['features'])==16
for old,new in zip(before['features'],current['features']):
 if old['id']=='dj-premier':
  normalized=dict(new);v=normalized.pop('visual');assert normalized==old;assert v['photo']=='feature-dj-premier-provided-collage.webp' and v['precomposed'] and v['credit']=='ユーザー提供' and v['typographicName']=='DJ PREMIER' and not v.get('tag')
 else:assert new==old,new['id']
assert len(historical_intake_tracks())==499
assert json.loads(historical_intake_file('releases.json',(R/'releases.json').read_bytes()))['version']=='21.13'
asset=R/F['photo']['path'];assert sha(asset.read_bytes())==F['photo']['encodedSHA256']
with Image.open(asset) as im:assert list(im.size)==[1456,816];assert sha(im.convert('RGBA').tobytes())==F['photo']['rgbaSHA256']
for a in F['editorPhotos']:
 asset_path=R/a['path'];assert sha(asset_path.read_bytes())==a['encodedSHA256']
 with Image.open(asset_path) as im:assert list(im.size)==a['dimensions'] and sha(im.convert('RGBA').tobytes())==a['rgbaSHA256']
 if a['source'].endswith('.jpg'):assert a['encodedSHA256']==a['sourceSHA256']
if (D/'metadata.js').exists():
 assert len(F['socialImages'])==516
 for path,h in F['socialImages'].items():
  if path!='feature-og/dj-premier.jpg':assert sha((D/path).read_bytes())==h,path
 from brand_assets import save_feature_social_image
 import tempfile
 with tempfile.TemporaryDirectory() as temp:
  reference=Path(temp)/'premier.jpg';save_feature_social_image(reference,asset);assert reference.read_bytes()==(D/'feature-og/dj-premier.jpg').read_bytes()
 with tempfile.TemporaryDirectory() as temp:
  reference=Path(temp)/'editor.jpg';save_feature_social_image(reference,R/'src/assets/editor-provided-collage.webp');assert reference.read_bytes()==(D/'editor-og.jpg').read_bytes()
 with Image.open(D/'feature-og/dj-premier.jpg') as im:assert im.size==(1200,630)
 meta=json.loads((D/'metadata.js').read_text().split('=',1)[1].rstrip(';\n'));m=meta['#/feature/dj-premier'];assert m['image'].endswith('/feature-og/dj-premier.jpg?v='+json.loads((R/'releases.json').read_text())['version'])
 assert meta['#/editor']['image'].endswith('/editor-og.jpg?v='+json.loads((R/'releases.json').read_text())['version'])
 editor=(D/'editor.html').read_text();assert editor.count('class="editor-photo editor-photo--')==2
 from profile_content import inline
 for block in json.loads((R/'editor_profile.json').read_text())['blocks']:
  assert inline(block['text']) in editor,block['text']
 assert meta['#/editor']['image'] in editor
 for a in F['editorPhotos']:assert (D/Path(a['path']).name).read_bytes()==(R/a['path']).read_bytes()
 gallery=(D/'tracks/index.html').read_text();assert 'static-graffiti-gallery' in gallery and gallery.count('class="catalog-graffiti"')==500
 index=(D/'producers/index.html').read_text();assert 'feature-dj-premier-provided-collage.webp' in index and 'feature-dj-premier-tag.webp' in index
 assert 'undefined' not in index and '/None' not in index
 assert (D/asset.name).read_bytes()==asset.read_bytes()
print('Direct native-install capability/guide scope and exact supplied Premier pixels;499 records, old15 features/photos,515 other OGP and all published prose preserved')
