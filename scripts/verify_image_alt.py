"""Image descriptions only: trusted visual text, static/registry parity, no image changes."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import json,hashlib
from approved_image_alt import F,historical_image_alt_file
from approved_album_recovery import historical_album_recovery_file
R=Path(__file__).resolve().parents[1];D=R/'dist';sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(F['files'])=={'discovery.py','releases.json'}
for p,c in F['files'].items():
 data=(R/p).read_bytes();assert sha(historical_image_alt_file(p,data))==c['beforeSHA256']
 try:historical_image_alt_file(p,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved image-alt source drift accepted')
expected=F['files']['discovery.py']['before']
for old,new in F['replacements']:assert expected.count(old)==1;expected=expected.replace(old,new,1)
assert (R/'discovery.py').read_text()==expected
release=json.loads(F['files']['releases.json']['before']);release['version']='22.8';assert json.loads(historical_album_recovery_file('releases.json',(R/'releases.json').read_bytes()))==release
brand=json.loads((R/'scripts/fixtures/approved-brand-identity.json').read_text())
for p,h in brand['contentHashes'].items():assert sha((R/p).read_bytes())==h,p
class Head(HTMLParser):
 def __init__(self,text):super().__init__();self.meta={};self.feed(text.split('</head>')[0])
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':self.meta.setdefault(a.get('property',a.get('name')),[]).append(a.get('content'))
if D.exists():
 registry=json.loads((D/'metadata.js').read_text().split('=',1)[1].strip().removesuffix(';'));tracks={t['id']:t for t in json.loads((R/'tracks.json').read_text())};features={f['id']:f for f in json.loads((R/'features.json').read_text())['features']}
 ready={a['id'] for a in json.loads((R/'graffiti_artwork.json').read_text())['tracks'] if a.get('status')=='ready'}
 generic='青い背景に白い「CRATE DIGGIN’」のタギングアート';counts={'art':0,'feature':0,'editor':0,'brand':0}
 for route,p in registry.items():
  if route.startswith('#/song/') and route.split('/')[-1] in ready:
   t=tracks[route.split('/')[-1]];expected=t['title']+' — '+t['artist']+'｜CRATE DIGGIN｜DJ Naoyaman';counts['art']+=1
  elif route.startswith('#/feature/'):expected=features[route.split('/')[-1]]['visual']['alt'];counts['feature']+=1
  elif route=='#/editor':expected='DJ NaoyamanのDJパフォーマンス・コラージュ（ユーザー提供）';counts['editor']+=1
  else:expected=generic;counts['brand']+=1
  assert p['imageAlt']==expected,(route,p['imageAlt'])
  rel=p['path'].removeprefix('/cratediggin/');target=D/rel
  if not rel or rel.endswith('/'):target=target/'index.html'
  paths=[target]
  if route.startswith('#/song/'):paths.append(D/'songs'/f"{route.split('/')[-1]}.html")
  for target in paths:
   head=Head(target.read_text());assert head.meta['og:image:alt']==head.meta['twitter:image:alt']==[expected],(route,target)
  full=json.loads((D/p['metadataPath'].removeprefix('/cratediggin/')).read_text());assert full['imageAlt']==expected
 assert counts=={'art':500,'feature':16,'editor':1,'brand':214},counts
 for p,h in brand['unchangedSocialImages'].items():assert sha((D/p).read_bytes())==h,p
 for p,c in brand['socialImages'].items():assert sha((D/p).read_bytes())==c['afterSHA256'],p
 print('731 registry/canonical plus legacy image descriptions match;500 work-art alt and all519 images unchanged')
print('Exact five metadata substitutions, trusted descriptions and source drift rejection PASS')
