"""Validate generated social images and non-JS legacy scraper metadata."""
import json, re, io, sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse
from PIL import Image
root=Path(__file__).resolve().parents[1]; dist=root/'dist'
sys.path.insert(0,str(root))
from brand_assets import social_image, SOCIAL_WALL, SOCIAL_WALL_LIGHT, SOCIAL_WALL_DARK, SOCIAL_PAPER
tracks={t['id']:t for t in json.loads((root/'tracks.json').read_text())}
def rgb(value):return tuple(bytes.fromhex(value[1:]))
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
    assert canonical['og:image:type']=='image/jpeg'
    assert canonical['og:image:width']=='1200' and canonical['og:image:height']=='630'
    assert canonical['og:image:alt']==canonical['twitter:image:alt']==p['imageAlt']
    assert urlparse(p['image']).scheme=='https' and urlparse(p['image']).netloc==urlparse(p['url']).netloc=='djnaoyaman.github.io' and '?v=' in p['image']
    schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',(dist/'tracks'/f'{tid}.html').read_text(),re.S)[1])
    article=next(x for x in schema['@graph'] if x.get('@type')=='Article')
    assert article['image']==[p['image']],tid
    track=json.loads(json.dumps(tracks[tid])); piece=art_by_id.get(tid,{})
    if piece.get('status')=='ready':track['art']['image']=piece['image']
    reference=social_image(track)
    encoded=io.BytesIO();reference.save(encoded,format='JPEG',quality=95,subsampling=0,optimize=True)
    target=dist/'og'/f'{tid}.jpg'
    assert target.read_bytes()==encoded.getvalue(), 'JPEG must be deterministic rendering of original artwork: '+tid
    assert not (dist/'og'/f'{tid}.png').exists(), 'Retired SNS PNG still public: '+tid
    with Image.open(target) as im:
        im.load(); assert im.format=='JPEG' and im.size==(1200,630) and im.mode=='RGB',tid
    if piece.get('status')=='ready':
        assert reference.getpixel((1,1))==rgb(SOCIAL_WALL),tid
        with Image.open(root/piece['image']) as source:
            rgba=source.convert('RGBA'); assert rgba.getchannel('A').getextrema()[0]==0,tid
            rgba.thumbnail((1080,382),Image.Resampling.LANCZOS)
            xoff=(1200-rgba.width)//2; yoff=82+(382-rgba.height)//2;checked=0
            for y in range(0,rgba.height,11):
                for x in range(0,rgba.width,11):
                    pixel=rgba.getpixel((x,y))
                    if pixel[3]>=200:
                        xx,yy=xoff+x,yoff+y
                        background=rgb(SOCIAL_WALL_DARK if xx%7==0 else SOCIAL_WALL_LIGHT if yy%4==0 else SOCIAL_WALL)
                        expected=tuple((pixel[i]*pixel[3]+background[i]*(255-pixel[3])+127)//255 for i in range(3))
                        assert reference.getpixel((xx,yy))==expected,tid
                        checked+=1
            assert checked>0,tid
        artwork_count+=1
    else:
        assert reference.getpixel((1,1))==rgb(SOCIAL_PAPER),tid
        assert 'graffiti' not in p['imageAlt'].lower()
        fallback_count+=1
    count+=1
assert count==len(json.loads((root/'tracks.json').read_text()))
print(f'Graffiti OGP: {count} opaque 1200×630 quality95 4:4:4 JPEGs; canonical/legacy/JSON-LD social metadata match')

assert artwork_count==sum(a.get('status')=='ready' for a in art_by_id.values())
print(f'{artwork_count} unchanged transparent artworks composited unchanged before deliberate JPEG encoding on subtle walls; {fallback_count} honest generic fallback')

# Every generic/profile social card also uses JPEG, while PNG application icons remain PNG.
expected_count=len(tracks)+len(json.loads((root/'features.json').read_text())['features'])+1
jpgs=list((dist/'og').glob('*.jpg'))+list((dist/'feature-og').glob('*.jpg'))+[dist/'og-image.jpg']
assert len(jpgs)==expected_count
assert not list((dist/'og').glob('*.png')) and not list((dist/'feature-og').glob('*.png')) and not (dist/'og-image.png').exists()
for path in jpgs:
    with Image.open(path) as im:im.load();assert im.format=='JPEG' and im.size==(1200,630)
for page in registry.values():
    assert urlparse(page['image']).path.endswith('.jpg')
    image_path=dist/urlparse(page['image']).path.removeprefix('/cratediggin/')
    assert image_path.is_file()
for path in dist.rglob('*'):
    if path.suffix not in ('.html','.js','.json','.xml','.txt','.md'):continue
    text=path.read_text()
    assert not re.search(r'(?:og-image|(?:feature-og|og)/[^\s\"<>?]+)\.png(?:[?\"<\s]|$)',text),path
print(f'All {expected_count} social JPEG URLs resolve; no retired SNS PNG references/files remain')

# A missing replacement must never retire a previous image. A valid one gets an exact backup first.
import tempfile, hashlib
from brand_assets import retire_legacy_social_pngs
with tempfile.TemporaryDirectory() as folder:
    test=Path(folder);old=test/'og-image.png';original=Image.new('RGB',(1200,630),'white');original.save(old)
    before=old.read_bytes()
    try:retire_legacy_social_pngs(test,[],[])
    except FileNotFoundError:pass
    else:raise AssertionError('Missing JPEG should abort retirement')
    assert old.read_bytes()==before
    original.save(test/'og-image.jpg',format='JPEG',quality=95,subsampling=0,optimize=True)
    icon=test/'icon-192.png';icon.write_bytes(before)
    retire_legacy_social_pngs(test,[],[])
    backup=Path(tempfile.gettempdir())/'cratediggin-ogp-png-backup'/hashlib.sha256(before).hexdigest()/'og-image.png'
    assert backup.read_bytes()==before and not old.exists() and icon.read_bytes()==before
print('Retirement is replacement-validated, backed up exactly, and limited to SNS derivatives')
