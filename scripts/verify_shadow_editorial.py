"""Verify bounded editorial enrichment, owner-photo provenance and static feature output."""
import hashlib,json
from approved_media_correction import historical_record
from pathlib import Path
from html.parser import HTMLParser
from PIL import Image
R=Path(__file__).resolve().parents[1]
t=json.loads((R/'tracks.json').read_text());e=json.loads((R/'scripts/shadow_editorial_expected.json').read_text())
digest=lambda x:hashlib.sha256(json.dumps(x,sort_keys=True,ensure_ascii=True).encode()).hexdigest()
fields=['id','title','artist','year','album','art','addedOrder']
ids=[x['id'] for x in t]
assert len(ids)==len(set(ids)) and len(t)>=len(e['tracks']) and set(e['tracks'])<=set(ids)
for x in t:
 x=historical_record(x)
 if x['id'] in e['tracks']:assert digest({k:x.get(k) for k in fields}|{'youtubeId':x['youtube']['id']})==e['tracks'][x['id']],x['id']
art=json.loads((R/'graffiti_artwork.json').read_text())['tracks'];art_by={x['id']:x for x in art}
assert len(art_by)==len(art) and set(e['artwork'])<=set(art_by)
for key,expected in e['artwork'].items():assert digest(art_by[key])==expected,key
for image,expected in e['imageFiles'].items():assert hashlib.sha256((R/image).read_bytes()).hexdigest()==expected,image
f=next(x for x in json.loads((R/'features.json').read_text())['features'] if x['id']=='dj-shadow');p=f['personalFeature']
assert '間違いなく' in ''.join(p['paragraphs']) and '本人にも会った' in ''.join(p['paragraphs'])
assert len(p['photos'])==4 and len({x['image'] for x in p['photos']})==4
class Parse(HTMLParser):
 def __init__(self):super().__init__();self.images=[];self.text=[]
 def handle_starttag(self,tag,attrs):
  if tag=='img':self.images.append(dict(attrs))
 def handle_data(self,data):self.text.append(data)
s=(R/'dist/producers/dj-shadow.html').read_text();h=Parse();h.feed(s)
for x in p['photos']:
 im=Image.open(R/'dist'/x['image']);assert im.size==(x['width'],x['height']);assert not im.getexif();assert 'exif' not in im.info
 matches=[a for a in h.images if a.get('src','').endswith('/'+x['image'])];assert len(matches)==1 and matches[0]['alt']==x['alt']
 assert x['caption'] in ''.join(h.text)
for text in p['paragraphs']:assert ''.join(h.text).count(text)==1
assert '写真提供：DJ Naoyaman' in s and '写真撮影：' not in s
assert '/workspace/' not in s and 'Sentinel_' not in s
fight=next(x for x in t if x['id']=='public-enemy-fight-the-power')
assert len(fight['samples'])==3 and not any(x.get('youtube') for x in fight['samples'])
assert fight['youtube']['id']=='mmo3HFa2vjg' and fight['youtube']['official'] is True
assert '掲載MVでの各断片の使用は未照合' in fight['sampleStatus']
for x in t:
 for fact in x['facts']+x['samples']:assert all(type(i) is int and 0<=i<len(x['sources']) for i in fact['sources'])
print('479 identities/audio IDs/original art preserved; four metadata-free owner photos and exact static testimony; three non-playable sourced sample entries passed')

import xml.etree.ElementTree as ET
xml=ET.parse(R/'dist/sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','i':'http://www.google.com/schemas/sitemap-image/1.1'}
node=next(x for x in xml.findall('s:url',ns) if x.findtext('s:loc',namespaces=ns).endswith('/producers/dj-shadow.html'))
assert {x['image'] for x in p['photos']}<={x.text.rsplit('/',1)[-1] for x in node.findall('i:image/i:loc',ns)}
print('All four owner-photo URLs are included on the canonical producer sitemap entry')
