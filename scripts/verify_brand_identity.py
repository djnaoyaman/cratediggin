"""Bounded brand rendering, uniform final heads and exact non-brand preservation."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,parse_qs
import hashlib,json,sys,tempfile
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'dist';sys.path.insert(0,str(R))
from brand_assets import normalize_brand_head,brand_revision,write_icons
from approved_brand_identity import F,historical_brand_identity_file,historical_brand_social_digest
sha=lambda b:hashlib.sha256(b).hexdigest()
class Head(HTMLParser):
 def __init__(self,text):super().__init__();self.items=[];self.feed(text.split('</head>')[0])
 def handle_starttag(self,tag,attrs):
  if tag in ('meta','link'):self.items.append((tag,dict(attrs)))
def contract(text):
 h=Head(text);links=[a for t,a in h.items if t=='link'];themes=[a for t,a in h.items if t=='meta' and a.get('name')=='theme-color'];assert themes==[{'name':'theme-color','content':'#4169e1'}]
 expected={'apple-touch-icon':['apple-touch-icon-tagging.png'],'icon':['favicon.svg','favicon-32.png','favicon-96.png'],'alternate icon':['favicon.ico'],'manifest':['site.webmanifest']}
 for rel,names in expected.items():
  matches=[a for a in links if a.get('rel')==rel];assert len(matches)==len(names),(rel,matches)
  assert [urlsplit(a['href']).path for a in matches]==['/cratediggin/'+n for n in names]
  assert all(parse_qs(urlsplit(a['href']).query)=={'v':[brand_revision()]} for a in matches)
 return links
for p,c in F['files'].items():
 data=(R/p).read_bytes();assert sha(historical_brand_identity_file(p,data))==c['beforeSHA256'],p
 try:historical_brand_identity_file(p,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved source mutation accepted: '+p)
for group in ('assets','contentHashes'):
 for p,h in F[group].items():assert sha((R/p).read_bytes())==h,p
assert len(F['unchangedSocialImages'])==517 and set(F['socialImages'])=={'og-image.jpg','og/a-tribe-called-quest-sucka-nigga.jpg'}
for p,c in F['socialImages'].items():
 data=(R/'brand/identity/social-1200.jpg').read_bytes();assert historical_brand_social_digest(p,data)==c['beforeSHA256']
 try:historical_brand_social_digest(p,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved image mutation accepted')
assert historical_brand_social_digest('unrelated.jpg',b'other')==sha(b'other')
# Existing social/title/canonical/JSON-LD and body remain byte-identical under icon normalization.
raw='<!doctype html><html><head><meta property="og:image" content="keep.jpg"><link rel="canonical" href="keep"><script type="application/ld+json">{"x":1}</script><link REL=\'ICON\' href=\'old\'><link rel="apple-touch-icon" href="old2"><meta name="theme-color" content="old"><link rel="manifest" href="old"></head><body>unchanged</body></html>'
normalized=normalize_brand_head(raw,'/cratediggin');contract(normalized);assert normalize_brand_head(normalized,'/cratediggin')==normalized
for text in ('<meta property="og:image" content="keep.jpg">','<link rel="canonical" href="keep">','<script type="application/ld+json">{"x":1}</script>','<body>unchanged</body>'):assert text in normalized
with tempfile.TemporaryDirectory() as tmp:
 out=Path(tmp);write_icons(out)
 for name,size in [('apple-touch-icon-tagging.png',180),('icon-192.png',192),('icon-512.png',512),('icon-maskable-512.png',512),('favicon-16.png',16),('favicon-32.png',32),('favicon-96.png',96)]:
  with Image.open(out/name) as im:im.load();assert im.size==(size,size) and im.mode=='RGB',name
 with Image.open(out/'favicon.ico') as im:assert im.ico.sizes()=={(16,16),(32,32),(48,48)}
 with Image.open(out/'apple-touch-icon-tagging.png') as actual,Image.open(R/'brand/identity/apple-180.png') as source:assert actual.tobytes()==source.tobytes()
if D.exists():
 for p,h in F['unchangedSocialImages'].items():assert sha((D/p).read_bytes())==h,p
 for p,c in F['socialImages'].items():assert sha((D/p).read_bytes())==c['afterSHA256'],p
 pages=0
 for p in D.rglob('*.html'):
  if p.name=='404.html':continue
  links=contract(p.read_text());pages+=1
  for a in links:
   if a.get('rel') in ('icon','alternate icon','apple-touch-icon','manifest'):assert (D/urlsplit(a['href']).path.removeprefix('/cratediggin/')).is_file(),(p,a)
 assert pages>=731
 m=json.loads((D/'site.webmanifest').read_text());assert m['start_url']==m['scope']=='/cratediggin/' and m['theme_color']=='#4169e1' and m['background_color']=='#ffffff'
 assert [x['purpose'] for x in m['icons']]==['any','any','maskable']
 for x in m['icons']:
  assert parse_qs(urlsplit(x['src']).query)=={'v':[brand_revision()]};assert (D/urlsplit(x['src']).path.removeprefix('/cratediggin/')).exists()
 registry=json.loads((D/'metadata.js').read_text().split('=',1)[1].strip().removesuffix(';'))
 for x in registry.values():
  path=urlsplit(x['image']).path.removeprefix('/cratediggin/')
  if path in F['socialImages']:assert parse_qs(urlsplit(x['image']).query)=={'v':[brand_revision()]}
 print(f'{pages} final static heads consistent; exactly2 brand OGP replacements,517 approved social images byte-preserved')
print('Brand sources, exact scope/negative mutations, icon sizes, ICO and normalizer idempotence PASS')
