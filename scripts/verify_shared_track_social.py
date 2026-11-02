"""All track previews share the homepage image; recordings and on-site art do not."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
import json,re,sys
from PIL import Image
R=Path(__file__).resolve().parents[1];D=R/'dist'
sys.path.insert(0,str(R))
class Tags(HTMLParser):
 def __init__(self,text):
  super().__init__();self.meta={};self.counts={};self.links={};self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='meta':
   k=a.get('property',a.get('name',''));self.meta[k]=a.get('content');self.counts[k]=self.counts.get(k,0)+1
  if tag=='link':self.links[a.get('rel')]=a.get('href')
registry=json.loads((D/'metadata.js').read_text().split('=',1)[1].strip().removesuffix(';'))
home=registry['#/']; shared=home['image']; alt=home['imageAlt']
assert urlparse(shared).path.endswith('/og-image.jpg')
assert urlparse(shared).scheme=='https' and urlparse(shared).netloc=='djnaoyaman.github.io' and '?v=' in shared
assert (D/'og-image.jpg').read_bytes()==(R/'brand/identity/social-1200.jpg').read_bytes()
with Image.open(D/'og-image.jpg') as im:
 im.load();assert im.size==(1200,630) and im.format=='JPEG'
tracks=json.loads((R/'tracks.json').read_text())
for t in tracks:
 p=registry['#/song/'+t['id']]
 assert p['image']==shared and p['imageAlt']==alt,t['id']
 assert t['title'] in p['title'] and t['artist'] in p['title']
 assert t['deck'] in p['description']
 assert urlparse(p['url']).netloc==urlparse(shared).netloc
 canonical_tags=Tags((D/'tracks'/(t['id']+'.html')).read_text())
 social={k:v for k,v in canonical_tags.meta.items() if k.startswith(('og:','twitter:'))}
 assert social
 for directory in ['tracks','songs']:
  text=(D/directory/(t['id']+'.html')).read_text();tags=Tags(text)
  assert tags.links['canonical']==p['url']
  assert all(tags.meta.get(k)==v and tags.counts[k]==canonical_tags.counts[k]==1 for k,v in social.items())
  assert tags.meta['og:image:width']=='1200' and tags.meta['og:image:height']=='630'
  for key in ['og:image','twitter:image']:
   assert tags.meta[key]==shared and tags.counts[key]==1,(t['id'],key)
  for key in ['og:image:alt','twitter:image:alt']:assert tags.meta[key]==alt
  assert tags.meta['og:title']==p['title'] and tags.meta['og:description']==p['description']
  assert tags.meta['og:url']==p['url'] and tags.meta['og:image:type']=='image/jpeg'
  if directory == 'tracks':  # Legacy /songs redirects retain metadata, not a duplicate graph.
   graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S)[1])['@graph']
   article=next(x for x in graph if x.get('@type')=='Article')
   assert article['image']==[shared]
 assert not (D/'og'/(t['id']+'.jpg')).exists()
 assert not (D/'og'/(t['id']+'.png')).exists()
assert not list((D/'og').glob('*.jpg')) and not list((D/'og').glob('*.png'))
# No generated metadata, JSON-LD, sitemap or UI keeps a dangling per-song preview.
for path in D.rglob('*'):
 if path.suffix in {'.html','.js','.json','.xml','.txt','.md'}:
  assert not re.search(r'/og/[^\s\"<>?]+\.(?:jpg|png)',path.read_text()),path
for p in registry.values():
 target=D/urlparse(p['image']).path.removeprefix('/cratediggin/')
 assert target.is_file(),target
print(f'Shared homepage OGP PASS: {len(tracks)} canonical+legacy pages, SPA registry, JSON-LD; unique titles/descriptions/canonicals; no dangling social images.')
