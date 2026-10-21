"""One requested record and its real generated article; no changes to the published 505."""
from pathlib import Path
import argparse,copy,hashlib,json,sys
from PIL import Image
from approved_something import F,historical_something_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
args=argparse.ArgumentParser();args.add_argument('--source-only',action='store_true');args=args.parse_args()
assert set(F['files'])=={'tracks.json','editorial_deepdives.json','graffiti_artwork.json','releases.json','artist_entities.json'}
for name,c in F['files'].items():
 raw=(R/name).read_bytes();assert sha(historical_something_file(name,raw))==c['beforeSHA256']
 # Exact full-bundle binding rejects partial publication and any old/new record drift.
 for bad in [raw+b' ',historical_something_file(name,raw)]:
  try:historical_something_file(name,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved partial/drifted bundle accepted: '+name)
for name,h in F['protected'].items():assert sha((R/name).read_bytes())==h,name
tracks=json.loads((R/'tracks.json').read_text());old=json.loads(historical_something_file('tracks.json',(R/'tracks.json').read_bytes()))
assert len(tracks)==506 and len(old)==505 and tracks[:-1]==old and tracks[-1]==F['record']
assert len({t['id'] for t in tracks})==506
assert sum(t.get('workType','single')=='single' for t in tracks)==501
entities=json.loads((R/'artist_entities.json').read_text());assert {t['artist'] for t in tracks} <= entities.keys()
assert entities['Hassaan Mackey & Apollo Brown']=={'type':None}
track=tracks[-1];assert track['id']=='hassaan-mackey-apollo-brown-something' and track['artist']=='Hassaan Mackey & Apollo Brown' and track['producers']==['Apollo Brown']
assert track['artists']==['Hassaan Mackey','Apollo Brown'] and track['year']==2011
assert track['youtube']['id']=='ugRgKqQ3x4M' and track['youtube']['official'] is False
assert track['youtube']['playbackVerified'] is False and track['youtube']['embeddedPlaybackVerified'] is False
assert 'duration' not in track['youtube'] and 'japanAvailableMetadata' not in track['youtube'] and 'embeddableMetadata' not in track['youtube']
assert '一般ユーザー投稿（非公式）' in track['editorialStatus'] and '日本国内からの実再生と埋め込み再生は未確認' in track['editorialStatus']
assert len(track['essay'])==len(track['essaySources'])==5
assert track['samples']==[] and '未確認' in track['sampleStatus']
assert track['versionBasis']==track['youtube']['versionBasis']
assert 'Volume' in track['essay'][3] and 'Something' in track['essay'][3]
provenance=json.loads((R/'research/intake-something-20261021.json').read_text())
assert provenance['sourceRow']==3 and provenance['submittedMixYear']==2012 and provenance['submittedSegmentDuration']=='2:02'
assert provenance['trackId']==track['id'] and provenance['selectedVideo']==track['youtube']
for indices in track['essaySources']:
 assert indices and all(type(i)is int and 0<=i<len(track['sources']) for i in indices)
assert all(s['url'].startswith('https://') and s['label'] for s in track['sources'])
assert set(track['connections'])<={t['id'] for t in old}
assert track['essayTitle'] not in {t['essayTitle'] for t in old}
dives=json.loads((R/'editorial_deepdives.json').read_text());assert dives[-1]==F['deepdive']
assert len({(d['artist'].casefold(),d['title'].casefold()) for d in dives})==len(dives)
sys.path.insert(0,str(R))
from editorial_references import enrich_sections
assert len(enrich_sections(track,dives[-1]['sections']))==2
for section in dives[-1]['sections']:
 assert section['text'] and section['heading'] and section['sources']
 assert all(0<=i<len(track['sources']) for i in section['sources'])
 assert section['source'] in [track['sources'][i]['url'] for i in section['sources']]
art=json.loads((R/'graffiti_artwork.json').read_text())['tracks'];assert art[-1]==F['artEntry'] and len(art)==506
assert art[-1]['palette']==track['art']['palette'] and art[-1]['transparent'] and art[-1]['textReviewed'] and art[-1]['paletteReviewed']
image=R/art[-1]['image'];assert sha(image.read_bytes())==F['asset']['sha256']
with Image.open(image) as im:
 im.load();assert im.mode=='RGBA' and list(im.size)==F['asset']['dimensions'] and im.width<=2400
 assert sha(im.tobytes())==F['asset']['rgbaSHA256'] and list(im.getchannel('A').getextrema())==[0,255]
assert historical_something_file('unrelated.txt',b'changed')==b'changed'
# Run the real editorial duplication ratchet with no newly allowed debt.
sys.path.insert(0,str(R/'scripts'))
from editorial_uniqueness import authored,duplicates,new_violations
baseline=json.loads((R/'scripts/fixtures/editorial-legacy-debt.json').read_text())
assert not new_violations(duplicates(authored(R)),baseline['groups']), 'New editorial duplication'
if not args.source_only:
 D=R/'dist';assert D.is_dir(),'Generated site is required'
 id=track['id'];page=(D/'tracks'/(id+'.html')).read_text();md=(D/'songs'/(id+'.md')).read_text()
 assert track['title'] in page and track['essayTitle'] in page and track['essayTitle'] in md
 assert '一般ユーザー投稿（非公式）' in page and '未確認' in page
 assert track['essayTitle'] in (D/'readings/index.html').read_text()
 assert art[-1]['image'] in page and 'Original graffiti' in page
 assert all(p in page for p in track['essay'])
 assert all(s['heading'] in page for s in dives[-1]['sections'])
 assert 'https://djnaoyaman.github.io/cratediggin/tracks/'+id+'.html' in (D/'sitemap.xml').read_text()
 registry=json.loads((D/'metadata.js').read_text().strip().removeprefix('window.CRATE_PAGES=').removesuffix(';'))
 assert registry['#/song/'+id]['image'].endswith('/og/'+id+'.jpg?v=22.23')
 assert (D/'og'/(id+'.jpg')).is_file()
print('One Something addition; exact published505 prefix, source mappings, transparent art, honest media metadata, negative partial bundle'+(' (source-only; generated output not run)' if args.source_only else ', generated article/Markdown/metadata/sitemap PASS'))
