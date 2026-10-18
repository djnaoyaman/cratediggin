"""Validate generated social images and non-JS legacy scraper metadata."""
import json, re
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
from PIL import Image
root=Path(__file__).resolve().parents[1]; dist=root/'dist'
registry=json.loads((dist/'metadata.js').read_text().split('=',1)[1].strip().removesuffix(';'))
class Tags(HTMLParser):
    def __init__(self,text):
        super().__init__(); self.meta={}; self.counts={}; self.links={}; self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='meta':
            key=a.get('property',a.get('name','')); self.meta[key]=a.get('content'); self.counts[key]=self.counts.get(key,0)+1
        if tag=='link': self.links[a.get('rel')]=a.get('href')
art_by_id={a['id']:a for a in json.loads((root/'graffiti_artwork.json').read_text())['tracks']}
count=0; artwork_count=0; fallback_count=0
for route,p in registry.items():
    if not route.startswith('#/song/'):continue
    tid=route.split('/')[-1]
    ct=Tags((dist/'tracks'/f'{tid}.html').read_text()); lt=Tags((dist/'songs'/f'{tid}.html').read_text())
    canonical=ct.meta; legacy=lt.meta
    assert ct.links['canonical']==lt.links['canonical']==p['url'],tid
    expected={k:v for k,v in canonical.items() if k.startswith(('og:','twitter:'))}
    assert expected and all(legacy.get(k)==v and ct.counts[k]==lt.counts[k]==1 for k,v in expected.items()),tid
    assert canonical['og:image']==canonical['twitter:image']==p['image']
    assert canonical['og:image:type']=='image/png'
    assert canonical['og:image:width']=='1200' and canonical['og:image:height']=='630'
    assert canonical['og:image:alt']==canonical['twitter:image:alt']==p['imageAlt']
    assert urlparse(p['image']).scheme=='https' and urlparse(p['image']).netloc==urlparse(p['url']).netloc=='djnaoyaman.github.io' and '?v=' in p['image']
    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',(dist/'tracks'/f'{tid}.html').read_text(),re.S)[1])
    article=next(x for x in schema['@graph'] if x.get('@type')=='Article')
    assert article['image']==[p['image']],tid
    with Image.open(dist/'og'/f'{tid}.png') as im:
        im.load(); assert im.size==(1200,630) and im.mode=='RGB',tid
        piece=art_by_id.get(tid,{})
        if piece.get('status')=='ready':
            assert im.getpixel((1,1))==(85,83,78),tid
            with Image.open(root/piece['image']) as source:
                rgba=source.convert('RGBA'); assert rgba.getchannel('A').getextrema()[0]==0,tid
                rgba.thumbnail((1080,382),Image.Resampling.LANCZOS)
                xoff=(1200-rgba.width)//2; yoff=82+(382-rgba.height)//2
                checked=0
                for y in range(0,rgba.height,11):
                    for x in range(0,rgba.width,11):
                        pixel=rgba.getpixel((x,y))
                        if pixel[3]>=200:
                            xx,yy=xoff+x,yoff+y
                            background=(81,79,74) if xx%7==0 else (89,87,82) if yy%4==0 else (85,83,78)
                            expected=tuple((pixel[i]*pixel[3]+background[i]*(255-pixel[3])+127)//255 for i in range(3))
                            assert im.getpixel((xx,yy))==expected,tid
                            checked+=1
                assert checked>0,tid
            artwork_count+=1
        else:
            assert im.getpixel((1,1))==(0,108,182),tid
            assert 'graffiti' not in p['imageAlt'].lower()
            fallback_count+=1
    count+=1
assert count==len(json.loads((root/'tracks.json').read_text()))
print(f'Graffiti OGP: {count} opaque 1200×630 PNGs; canonical/legacy/JSON-LD social metadata match')

assert artwork_count==sum(a.get('status')=='ready' for a in art_by_id.values())
print(f'{artwork_count} unchanged transparent artworks composited on dark walls; {fallback_count} honest generic fallback')
