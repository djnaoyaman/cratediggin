"""Two exact requested additions; no unrelated content, media, art or UI drift."""
from pathlib import Path
import json,hashlib,copy,sys
from PIL import Image
from approved_timeline_explorer import historical_explorer_file
from approved_artifacts_credits import historical_credit_file
from approved_requested_two import FIXTURE as F,historical_intake_file,historical_intake_tracks
R=Path(__file__).resolve().parents[1];D=R/'dist';sys.path.insert(0,str(R));sha=lambda b:hashlib.sha256(b).hexdigest()
from feature_policy import role_projection
from catalog import feature_tracks
tracks=json.loads(historical_credit_file('tracks.json',(R/'tracks.json').read_bytes()));old=historical_intake_tracks();ids=[t['id'] for t in tracks]
assert len(tracks)==len(set(ids))==501 and len(old)==499
assert tracks[499:]==F['records'] and ids[499:]==F['ids'] and not set(F['held'])&set(ids)
assert [t['id'] for t in old]==F['orderedIds']
assert sum(t.get('workType','single')=='single' for t in tracks)==496
assert set(F['appendedFiles'])=={'tracks.json','editorial_deepdives.json','graffiti_artwork.json'}
for path,c in F['appendedFiles'].items():
 raw=(R/path).read_bytes();assert sha(historical_credit_file(path,raw))==c['afterSHA256'];assert sha(historical_intake_file(path,raw))==c['beforeSHA256']
 value=json.loads(raw)
 cases=[raw+b' ']
 if c['arrayKey'] is None:
  for index in [0,-1]:
   changed=copy.deepcopy(value);changed[index]['unapproved']='change';cases.append((json.dumps(changed,ensure_ascii=False,indent=2)+'\n').encode())
  for changed in [value[:-1],value+[value[-1]],list(reversed(value)),value[:499]+list(reversed(value[499:]))]:cases.append((json.dumps(changed,ensure_ascii=False,indent=2)+'\n').encode())
 else:
  changed=copy.deepcopy(value);changed['qualityReference']='unapproved';cases.append((json.dumps(changed,ensure_ascii=False,indent=2)+'\n').encode())
  changed=copy.deepcopy(value);changed[c['arrayKey']][0]['image']='unapproved.webp';cases.append((json.dumps(changed,ensure_ascii=False,indent=2)+'\n').encode())
 for bad in cases:
  if bad==raw:continue
  try:historical_intake_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Mutation accepted: '+path)
for path,h in F['protected'].items():assert sha(historical_explorer_file(path,(R/path).read_bytes()))==h,path
assert {'src/app/opening.js','src/app/opening-selection.js','features.json','artist_entities.json'}<=set(F['protected'])
assert json.loads(historical_explorer_file('releases.json',(R/'releases.json').read_bytes()))['version']==F['release']['version']=='21.14'
assert sha(historical_intake_file('releases.json',(R/'releases.json').read_bytes()))==F['release']['beforeSHA256']
for bad in [dict(F['release']['before'],version='21.99'),dict(F['release']['before'],version='21.14',history=[])]:
 try:historical_intake_file('releases.json',(json.dumps(bad,ensure_ascii=False,indent=2)+'\n').encode())
 except AssertionError:pass
 else:raise AssertionError('Release drift accepted')
# Unknown paths are never exempted.
assert historical_intake_file('src/app/player.js',b'changed')==b'changed'
dives=json.loads((R/'editorial_deepdives.json').read_text());assert len(dives)==161 and dives[159:]==F['deepdives']
art=json.loads((R/'graffiti_artwork.json').read_text())['tracks'];assert len(art)==501 and sum(x.get('status')=='ready' for x in art)==500
assert [x for x in art if x['id'] in F['ids']]==F['artEntries']
assert len(F['records'])==len(F['mediaEvidence'])==len(F['artEntries'])==2
assert [x['id'] for x in F['records']]==[x['id'] for x in F['artEntries']]==F['ids']
for t,e,a in zip(F['records'],F['mediaEvidence'],F['artEntries']):
 assert len(t['essay'])==len(t['essaySources'])==3 and t['samples']==[] and '未確認' in t['sampleStatus']
 y=t['youtube'];assert y['id']==e['id'] and e['japanListedMetadata'] and e['embedEligibleMetadata'] and e['playabilityStatus']=='OK'
 assert y['official'] and y['japanAvailableMetadata'] and y['embeddableMetadata'] and y['playbackVerified'] is False and y['embeddedPlaybackVerified'] is False
 assert '日本国内からの実再生と埋め込み再生は未確認' in t['editorialStatus']
 assert len(t['connections'])==2 and all(i in F['orderedIds'] for i in t['connections'])
 assert a['palette']==t['art']['palette'] and a['transparent'] and a['textReviewed'] and a['paletteReviewed']
 evidence=F['assets'][a['id']];data=(R/a['image']).read_bytes();assert sha(data)==evidence['sha256']
 with Image.open(R/a['image']) as im:
  im.load();assert im.mode=='RGBA' and im.width<=2400 and list(im.size)==evidence['dimensions'];assert sha(im.tobytes())==evidence['rgbaSHA256'];assert list(im.getchannel('A').getextrema())==evidence['alphaExtrema']==[0,254]
assert role_projection(old)==F['oldRoles']
roles=role_projection(tracks);assert roles==F['liveRoles'];assert sum(q['tier']=='priority' for q in roles.values())==23
assert {n for n,q in roles.items() if q['tier']!='archive'}=={n for n,q in F['oldRoles'].items() if q['tier']!='archive'}
assert roles['DJ Premier']==F['oldRoles']['DJ Premier'] and roles['DJ Premier']['producerCount']==42
changed={n for n in roles if roles[n]!=F['oldRoles'].get(n)};assert changed=={'Artifacts','Diamond & The Psychotic Neurotics','Diamond D','T-Ray','Jazzy Jay'}
assert roles['Diamond D']['producerCount']==8 and roles['Diamond D']['tier']=='priority'
features=json.loads((R/'features.json').read_text())['features'];assert len(features)==16
for f in features:assert [t['id'] for t in feature_tracks(tracks,f)]==F['featureSelections'][f['id']]
assert [t['id'] for t in tracks if 'essaySources' in t]==F['mappedIds'] and len(F['mappedIds'])==68
if D.exists():
 for path,h in F['socialImages'].items():assert sha((D/path).read_bytes())==h,path
 actual={str(p.relative_to(D)) for p in D.rglob('*.jpg') if p.parent.name in {'og','feature-og'} or p.name in {'og-image.jpg','editor-og.jpg'}}
 assert actual==set(F['socialImages'])|{'og/'+id+'.jpg' for id in F['ids']} and len(actual)==519
 meta=json.loads((D/'metadata.js').read_text().split('=',1)[1].rstrip(';\n'));assert len(meta)==731
 from xml.etree import ElementTree as ET
 sitemap=ET.parse(D/'sitemap.xml');assert len(sitemap.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'))==731
 for t in F['records']:
  id=t['id'];html=(D/'tracks'/f'{id}.html').read_text();md=(D/'tracks'/f'{id}.md').read_text();assert t['deck'] in html and all(paragraph in md for paragraph in t['essay'])
  assert id in (D/'llms-full.txt').read_text();assert f'/tracks/{id}.html' in (D/'songs'/f'{id}.html').read_text()
  assert meta['#/song/'+id]['image'].endswith('/og/'+id+'.jpg?v='+json.loads((R/'releases.json').read_text())['version'])
print('Two requested source-led additions:501 works,496 singles,500 art; all499/517OGP and current UI protected, exact five role deltas, mutation rejection; no actual audio certification')
