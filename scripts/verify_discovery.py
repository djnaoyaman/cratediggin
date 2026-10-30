"""Validate real generated SEO/SNS metadata, editorial dates and machine-readable views."""
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
dist = root / 'dist'
registry = json.loads((dist / 'metadata.js').read_text(encoding='utf-8').split('=', 1)[1].strip().removesuffix(';'))
revision_data = json.loads((dist / 'article-revisions.json').read_text(encoding='utf-8'))
tracks = json.loads((root / 'tracks.json').read_text(encoding='utf-8'))
source_by_id = {t['id']: t for t in tracks}
# Committed source history must not be hidden by derived image metadata.
if (root / '.git').exists():
    import sys
    sys.path.insert(0,str(root))
    from revision_dates import revision_dates
    expected = revision_dates(root,tracks,json.loads((root/'editorial_deepdives.json').read_text()),json.loads((root/'features.json').read_text())['features'])
    assert revision_data == expected, 'Build projections changed authored revision provenance'
sitemap = ET.fromstring((dist / 'sitemap.xml').read_text(encoding='utf-8'))
listed = {x.text for x in sitemap.findall('.//{*}loc')}
base = urlparse(registry['#/']['url']).path.rstrip('/')
feature_titles = set()
feature_descriptions = set()
for route, meta in registry.items():
    relative = meta['path'][len(base):].lstrip('/')
    target = dist / relative
    if not relative or relative.endswith('/'):
        target /= 'index.html'
    source = target.read_text(encoding='utf-8')
    assert html.unescape(re.search(r'<title>(.*?)</title>', source, re.S)[1]) == meta['title'], route
    for tag in re.findall(r'<link\b[^>]*>', source):
        attrs=dict(re.findall(r'([\w-]+)="([^"]*)"',tag))
        if attrs.get('rel') in {'icon','alternate icon','apple-touch-icon','manifest'}:
            resolved=urlparse(urljoin(meta['url'],html.unescape(attrs['href'])))
            assert resolved.netloc==urlparse(meta['url']).netloc,(route,'Unexpected icon origin')
            assert resolved.path.startswith(base+'/'),(route,'Icon outside project',resolved.path)
            assert (dist/resolved.path[len(base)+1:]).is_file(),(route,'Broken resolved icon/manifest',resolved.path)
    for attr, key, expected in [('name', 'description', meta['description']), ('property', 'og:title', meta['title']),
                                ('property', 'og:description', meta['description']), ('property', 'og:url', meta['url']),
                                ('name', 'twitter:title', meta['title']), ('name', 'twitter:image', meta['image'])]:
        values = re.findall(r'<meta ' + attr + '="' + key + r'" content="([^"]*)">', source)
        assert len(values) == 1 and html.unescape(values[0]) == expected, (route, key)
    canonicals = re.findall(r'<link rel="canonical" href="([^"]+)">', source)
    assert canonicals == [meta['url']], route
    assert meta['url'] in listed
    assert not re.search(r'href="#/', source), route
    assert 'metadata.js?v=' in source
    image_path = urlparse(meta['image']).path[len(base):].lstrip('/')
    assert (dist / image_path).is_file()
    metadata_file = dist / meta['metadataPath'].split('/')[-2] / meta['metadataPath'].split('/')[-1]
    full = json.loads(metadata_file.read_text(encoding='utf-8'))
    ld_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', source, re.S)
    assert len(ld_blocks) == 1 and json.loads(ld_blocks[0]) == full['jsonld'], route
    graph = full['jsonld']['@graph']
    article = next((x for x in graph if x['@type'] == 'Article'), None)
    if article:
        assert article['image'] and article['author']['url'].endswith('/editor.html')
        assert article['mainEntityOfPage'] == meta['url']
        if article.get('dateModified'):
            key = route.removeprefix('#/')
            assert article['dateModified'] == revision_data[key]['dateModified']
    if route.startswith('#/song/'):
        tid = route.split('/')[-1]
        original = source_by_id[tid]
        assert article.get('datePublished') == original.get('datePublished'), 'Do not invent publication dates'
        expected_type = {'mix':'MusicAlbum','album':'MusicAlbum','live_video':'VideoObject'}.get(original.get('workType'),'MusicRecording')
        recording = next(x for x in graph if x['@type'] == expected_type)
        if original.get('workType') == 'mix':
            assert recording['albumProductionType'] == 'https://schema.org/DJMixAlbum'
            assert 'inAlbum' not in recording
            assert not any(x['@type'] == 'MusicRecording' for x in graph)
        if original.get('workType') == 'live_video':
            assert 'datePublished' not in recording and 'inAlbum' not in recording
            assert recording['embedUrl']=='https://www.youtube.com/embed/'+original['youtube']['id']
            assert recording.get('uploadDate')==original['youtube'].get('uploadDate')
        if original['artist'] in ('A Tribe Called Quest', 'Gang Starr'):
            assert recording['byArtist']['@type'] == 'MusicGroup'
        assert 'sameAs' not in recording, 'Reference uploads must not assert authoritative identity'
        markdown = (dist / 'tracks' / (tid + '.md')).read_text(encoding='utf-8')
        assert meta['url'] in markdown and '/editor.html' in markdown
    if route.startswith('#/feature/'):
        feature_titles.add(meta['title'])
        feature_descriptions.add(meta['description'])
feature_count = sum(x.startswith('#/feature/') for x in registry)
readings=(dist/'readings/index.html').read_text(encoding='utf-8')
for guide in json.loads((root/'guides.json').read_text(encoding='utf-8')):
    assert 'href="'+base+'/guides/'+guide['id']+'.html"' in readings, 'Guide missing from crawlable readings navigation'
artist_names={t['artist'] for t in tracks}
assert len({name.casefold() for name in artist_names})==len(artist_names), 'Case-only artist variants split the catalog'
normalized=next(meta for route,meta in registry.items() if route=='#/artist/Trends%20of%20Culture')
assert 'Trends%20Of%20Culture' not in json.dumps({k:v for k,v in registry.items() if k.startswith('#/artist/')})
legacy=(dist/'artists/cc191cccc5c76c55.html').read_text(encoding='utf-8')
assert '<link rel="canonical" href="'+normalized['url']+'">' in legacy
assert '/artists/cc191cccc5c76c55.html' not in listed
assert len(feature_titles) == len(feature_descriptions) == feature_count
assert '/about.html' in (dist / 'llms.txt').read_text(encoding='utf-8')
assert (dist / 'llms-full.txt').read_text(encoding='utf-8').count('正規URL: ') == len(tracks)
print(f'{len(registry)} static pages: unique metadata, canonical/OGP, schemas, real links, dates, author and Markdown verified')
