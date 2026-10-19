from pathlib import Path
from approved_premier_feature import historical_premier_file
import hashlib,json
from approved_browser_tools import FIXTURE as f,historical_browser_tools_file
R=Path(__file__).resolve().parents[1];D=R/'dist';sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(f['files'])=={'templates/index.html','src/app/renewal.js','src/assets/style.css','profile_content.py','features.json'}
for path,c in f['files'].items():
 data=(R/path).read_bytes();assert historical_browser_tools_file(path,data)==c['before'].encode()
 try:historical_browser_tools_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved mutation accepted: '+path)
for path,h in f['protected'].items():assert sha(historical_premier_file(path,(R/path).read_bytes()))==h,path
assert len(json.loads((R/'tracks.json').read_text()))==499
assert json.loads((R/'releases.json').read_text())['version']=='21.11'
s=(R/'src/app/renewal.js').read_text();assert '[300,360,450,570,720,900]' in s and "$('#shuffle-again').onclick=renewalDraw" in s
assert 'window.external' not in s and 'navigator.share' not in s and 'serviceWorker.register' not in s
if D.exists():
 for path,h in f['socialImages'].items():assert sha((D/path).read_bytes())==h,path
 profile=(D/'editor.html').read_text();assert '<span class="editor-name-accessible">DJ Naoyaman</span>' in profile
 assert 'class="editor-signature"' in profile and 'alt="" width="1881" height="628"' in profile
 assert '宮崎直哉' in profile and '約5万曲' in profile and '明治大学' in profile
 assert 'designed by DJ NAOYAMAN' in (D/'index.html').read_text()
print('Exact five scoped UI/visual file corrections;499 records, all supplied photos, biography, ART credit, media and social image bytes preserved')
# The only new content asset is the user-supplied Black Sheep composition.
from PIL import Image
import copy,io
from approved_browser_tools import historical_browser_tools_social
a=f['blackSheepAsset'];asset=R/a['path'];assert sha(asset.read_bytes())==a['sha256']
with Image.open(asset) as im:assert im.size==(1456,816) and sha(im.convert('RGBA').tobytes())==a['pixelSHA256']
before=json.loads(f['files']['features.json']['before']);after=json.loads(historical_premier_file('features.json',(R/'features.json').read_bytes()));normalized=copy.deepcopy(after)
for item in normalized['features']:
 if item['id']=='black-sheep':
  previous=next(x for x in before['features'] if x['id']==item['id']);v=item['visual']
  assert v['tag']==previous['visual']['tag'] and v['photo']==asset.name and v['precomposed'] and v['credit']=='ユーザー提供'
  assert not any(k in v for k in ('license','licenseUrl','author','source'))
  item['visual']=previous['visual']
assert normalized==before,'Only the supplied Black Sheep visual may change'
assert sum(bool(x['visual'].get('photo')) for x in after['features'])==15
if D.exists():
 assert sha((D/asset.name).read_bytes())==a['sha256']
 import sys;sys.path.insert(0,str(R));from brand_assets import SOCIAL_PAPER
 canvas=Image.new('RGB',(1200,630),SOCIAL_PAPER)
 with Image.open(asset) as im:
  art=im.convert('RGBA');art.thumbnail((1200,630),Image.Resampling.LANCZOS);assert art.size==(1124,630);canvas.paste(art,(38,0),art)
 out=io.BytesIO();canvas.save(out,format='JPEG',quality=95,subsampling=0,optimize=True)
 rel='feature-og/black-sheep.jpg';data=(D/rel).read_bytes();assert data==out.getvalue();historical_browser_tools_social(rel,data)
 try:historical_browser_tools_social(rel,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unexpected social image mutation accepted')
 pages=json.loads((D/'metadata.js').read_text().split('=',1)[1].rstrip(';\n'));meta=pages['#/feature/black-sheep']
 assert meta['image'].endswith('/'+rel+'?v=21.11')
 assert meta['image'] in (D/'artists/black-sheep.html').read_text()
 assert 'image/jpeg' in (D/'artists/black-sheep.html').read_text()
 assert '/artists/black-sheep.html' in (D/'features/black-sheep.html').read_text()
 graph=json.loads((D/meta['metadataPath'].removeprefix('/cratediggin/')).read_text());assert meta['image'] in json.dumps(graph)
print('Black Sheep full composition and matching OGP verified; all other feature content and 514 social images unchanged')
