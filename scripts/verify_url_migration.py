"""Canonical routes, compatibility aliases, image discovery, and data preservation gates."""
from pathlib import Path
import json, re, html
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1];d=r/'dist'
pages=json.loads((d/'metadata.js').read_text().removeprefix('window.CRATE_PAGES=').strip().removesuffix(';'))
mapping=json.loads((d/'url-migrations.json').read_text());base='/cratediggin';host='https://djnaoyaman.github.io'+base
tracks=json.loads((r/'tracks.json').read_text());features=json.loads((r/'features.json').read_text())['features'];arts=json.loads((r/'graffiti_artwork.json').read_text())['tracks'];ready={a['id'] for a in arts if a['status']=='ready'}
assert len(pages)==len(tracks)+len({t['artist'] for t in tracks})+len(features)+11
assert pages['#/readings']['path']==base+'/readings/'
for old,new in mapping.items():
 p=d/old.removeprefix(base+'/');p=p/'index.html' if old.endswith('/') else p
 assert p.is_file(),old
 if old.endswith('.md'): assert host+new[len(base):].removesuffix('.md')+'.html' in p.read_text();continue
 s=p.read_text();assert '<meta http-equiv="refresh" content="0;url='+host+new[len(base):]+'">' in s
 assert '<link rel="canonical" href="'+host+new[len(base):]+'">' in s
 assert 'href="'+host+new[len(base):]+'"' in s and 'noindex' not in s
 q=d/new.removeprefix(base+'/');q=q/'index.html' if new.endswith('/') else q
 assert q.is_file() and 'http-equiv="refresh"' not in q.read_text(),(old,new)
 if old.startswith(base+'/features/'):
  social=lambda text: sorted(re.findall(r'<meta (?:property|name)="((?:og|twitter):[^"]+)" content="([^"]*)">',text))
  expected=social(q.read_text())
  assert expected and social(s)==expected,('Legacy feature social metadata differs',old,new)
assert mapping[base+'/features/tribe-production.html']==base+'/artists/tribe.html'
for route,p in pages.items():
 rel=p['path'].removeprefix(base+'/');f=d/rel;f=f/'index.html' if not rel or rel.endswith('/') else f
 s=f.read_text();assert '/songs/' not in p['url'] and '/features/' not in p['url']
 assert s.count('rel="canonical"')==1 and html.unescape(re.search('rel="canonical" href="([^"]+)"',s)[1])==p['url']
 for href in re.findall('(?:href|src)="([^"]+)"',s):
  href=html.unescape(href);path=urlparse(href).path
  if path.startswith(base+'/'):
   assert not path.startswith((base+'/songs/',base+'/features/')),(route,path)
   file=d/path.removeprefix(base+'/');file=file/'index.html' if path.endswith('/') else file
   assert file.is_file(),(route,path)
 if route.startswith('#/song/'):
  tid=route.split('/')[-1];assert ('class="track-artwork"' in s)==(tid in ready)
  if tid in ready:
   assert s.count('class="track-artwork"')==1
   main=s.split('<main id="view"',1)[1].split('</main>',1)[0]
   assert 'class="track-artwork"' in main, 'Artwork must be in the article, not the global hero'
   fig=main.split('<figure class="track-artwork">')[1].split('</figure>')[0]
   assert 'width="' in fig and 'height="' in fig and 'CRATE DIGGIN｜DJ Naoyaman' in fig
for kind,feature_type in [('artists','artist'),('producers','producer')]:
 expected=[f for f in features if f['type']==feature_type and f.get('editorial') and f.get('visual')]
 count=len(expected);photo=sum(not f['visual'].get('nameOnly') for f in expected)
 s=(d/kind/'index.html').read_text();assert s.count('class="feature-poster"')==count;assert s.count('class="feature-photo"')==photo
sitemap=ET.parse(d/'sitemap.xml');ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9','i':'http://www.google.com/schemas/sitemap-image/1.1'}
urls=[n.text for n in sitemap.findall('s:url/s:loc',ns)];assert len(urls)==len(set(urls))==len(pages)
assert set(urls)=={p['url'] for p in pages.values()}
personal_images=sum(len(f.get('personalFeature',{}).get('photos',[])) for f in json.loads((r/'features.json').read_text())['features'] if '#/feature/'+f['id'] in pages)
feature_images=sum(len({f['visual'][key] for f in features if f.get('editorial') and f['type']==kind for key in ('photo','tag') if f.get('visual',{}).get(key)}) for kind in ('artist','producer'))
images=sitemap.findall('s:url/i:image/i:loc',ns);assert len(images)==len(ready)+feature_images+(3 if (r/'editor_profile.json').exists() else 0)+personal_images
for n in images: assert (d/n.text.removeprefix(host+'/')).is_file()
artist_files={base+'/artists/'+p.name for p in (d/'artists').glob('[0-9a-f]'*16+'.html')}
legacy_artists={old for old in mapping if re.fullmatch(re.escape(base)+r'/artists/[0-9a-f]{16}\.html',old)}
canonical_artists={p['path'] for route,p in pages.items() if route.startswith('#/artist/')}
assert len(canonical_artists)==len({t['artist'] for t in tracks})
assert artist_files==canonical_artists|legacy_artists
assert not canonical_artists&legacy_artists
print(f'{len(mapping)} old URL mappings, {len(pages)} canonical pages, {len(images)} image entries, canonical and legacy artist directory verified')

