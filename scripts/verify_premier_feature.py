from approved_requested_two import historical_intake_tracks
"""Exact append-only feature publication; catalog roles are not a discography claim."""
from pathlib import Path
import json,hashlib,sys,copy,re
R=Path(__file__).resolve().parents[1];D=R/'dist';sys.path.insert(0,str(R))
from feature_policy import role_projection,qualify_features
from feature_editorial import render_longform
from catalog import feature_tracks
from approved_premier_feature import FIXTURE as F,historical_premier_file
sha=lambda b:hashlib.sha256(b).hexdigest()
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert historical_premier_file(path,data)==c['before'].encode()
 try:historical_premier_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unexpected mutation accepted: '+path)
from approved_home_install_direct import historical_home_install_file
for path,h in F['protected'].items():assert sha(historical_home_install_file(path,(R/path).read_bytes()))==h,path
tracks=json.loads((R/'tracks.json').read_text());historical_tracks=historical_intake_tracks();assert len(historical_tracks)==499 and len(tracks)==501
source=json.loads((R/'features.json').read_text());before=json.loads(F['files']['features.json']['before']);assert source['features'][:-1]==before['features'];assert len(source['features'])==16
f=source['features'][-1];assert f['id']=='dj-premier' and f['type']=='producer' and f['names']==['DJ Premier'] and f['allYears'];assert f['visual']['photo']=='feature-dj-premier-provided-collage.webp' and f['visual']['provenance']=='user-provided' and f['visual'].get('tag')=='feature-dj-premier-tag.webp'
roles=role_projection(historical_tracks);approved=F['qualifiedIdentities'];actual={n for n,q in roles.items() if q['tier']!='archive'};assert actual=={x['name'] for x in approved} and len(actual)==42
for row in approved:
 q=roles[row['name']];assert q['artistIds']==row['artist_ids'] and q['producerIds']==row['producer_ids'];assert q['tier']==row['tier']
assert sum(q['tier']=='priority' for q in roles.values())==22
assert roles['DJ Premier']['producerCount']==42 and roles['DJ Premier']['artistCount']==0
assert sorted(t['id'] for t in feature_tracks(tracks,f))==roles['DJ Premier']['producerIds']
assert roles['AZ']['tier']=='archive';assert roles['Main Source']['artistCount']==6 and roles['Black Sheep']['artistCount']==7
assert roles['J Dilla']['producerCount']==19 and roles['J Dilla']['artistCount']==7
assert roles['Beastie Boys']['artistCount']==10 and roles['Pete Rock']['producerCount']==19
assert roles['C.L. Smooth']['tier']=='archive'
for q in roles.values():assert len(q['artistIds'])==len(set(q['artistIds'])) and len(q['producerIds'])==len(set(q['producerIds']))
non_songs={t['id'] for t in tracks if t.get('workType','single')!='single'}
assert all(not non_songs.intersection(q['artistIds']+q['producerIds']) for q in roles.values())
# Duplicate input rows do not inflate role counts.
assert role_projection(tracks+[tracks[0]])==role_projection(tracks)
# Unknown producers remain unknown, never inferred from group membership.
fake=[dict(tracks[0],id='unknown-role',artist='New Artist',artists=[],producers=[])];assert role_projection(fake)['New Artist']['producerCount']==0
for old in source['features'][:-1]:
 selected={t['id'] for t in feature_tracks(historical_tracks,old)};previous=set(F['previousSelections'][old['id']]);assert selected==previous|({'beastie-boys-get-it-together'} if old['id']=='beastie-boys' else set())
allf=qualify_features(tracks,source['features']);assert len(allf)==16 and next(x for x in allf if x['id']=='az')['qualification']['tier']=='archive'
# Exercise the actual discovery entry point even in Git-less local snapshots.
# Stop at revision lookup, after checking raw authored inputs rather than projections.
import discovery
from unittest.mock import patch
class RevisionInputsChecked(Exception):pass
def check_revision_inputs(root, authored_tracks, authored_dives, authored_features):
 assert authored_tracks==tracks
 assert authored_dives==json.loads((R/'editorial_deepdives.json').read_text())
 assert authored_features==source['features']
 assert all('qualification' not in feature for feature in authored_features)
 raise RevisionInputsChecked
projected_tracks=copy.deepcopy(tracks);projected_tracks[0]['projectionOnlyTest']='must not enter authored dates'
with patch.object(discovery,'revision_dates',side_effect=check_revision_inputs) as lookup:
 try:discovery.finalize_discovery(R,D,'https://example.org/cratediggin',projected_tracks,allf,[])
 except RevisionInputsChecked:pass
 else:raise AssertionError('Discovery did not validate authored revision inputs')
 lookup.assert_called_once()
e=f['editorial'];assert e['format']=='source-led-v1' and len(e['sources'])==5 and len(e['sections'])==6
expected=['mass-appeal','gang-starr-alongwaytogo','nas-n-y-state-of-mind','the-notorious-b-i-g-unbelievable','jeru-the-damaja-come-clean']
links=re.findall(r'\]\(#/song/([a-z0-9-]+)\)',json.dumps(e,ensure_ascii=False));assert links==expected
assert all(i in {t['id'] for t in tracks} for i in links)
assert [s['sources'] for s in e['sections']]==[[0],[1],[2],[3],[4],[]]
review=json.loads((R/'scripts/fixtures/premier-editorial-review.json').read_text());assert sha((json.dumps(e,ensure_ascii=False,indent=2)+'\n').encode())==review['reviewedEditorialSHA256']
from editorial_uniqueness import authored,duplicates,new_violations
rows=authored(R);premier_rows=[x for x in rows if x['owner']=='feature:dj-premier'];assert len(premier_rows)==21
assert not any(any(o['owner']=='feature:dj-premier' for o in group) for group in duplicates(rows).values()),'New duplicate feature prose'
rendered=render_longform(e,'/cratediggin');assert 'DJ NAOYAMAN’S VIEW' not in rendered and '私の聴き方' not in rendered
for bad in [[5],[-1],[True],['0'],[0,0]]:
 x=copy.deepcopy(e);x['sections'][0]['sources']=bad
 try:render_longform(x)
 except (AssertionError,TypeError):pass
 else:raise AssertionError('Invalid citation accepted')
for bad in [None,{}, {'label':'x','url':'javascript:alert(1)'},{'label':'','url':'https://example.org'}]:
 x=copy.deepcopy(e);x['sources'][0]=bad
 try:render_longform(x)
 except (AssertionError,TypeError):pass
 else:raise AssertionError('Invalid source accepted')
if (D/'metadata.js').exists():
 for path,h in F['socialImages'].items():assert sha((D/path).read_bytes())==h,path
 assert len(F['socialImages'])==515
 meta=json.loads((D/'metadata.js').read_text().split('=',1)[1].rstrip(';\n'));m=meta['#/feature/dj-premier'];assert m['url'].endswith('/producers/dj-premier.html')
 assert m['image'].endswith('/feature-og/dj-premier.jpg?v='+json.loads((R/'releases.json').read_text())['version'])
 page=(D/'producers/dj-premier.html').read_text();assert rendered in page
 for tid in roles['DJ Premier']['producerIds']:assert '/tracks/'+tid+'.html' in page
 assert '収録作品 42曲' in page
 assert '/producers/dj-premier.html' in (D/'features/dj-premier.html').read_text()
 az=(D/'artists/az.html').read_text();assert before['features'][7]['editorial']['title'] in az
 index=(D/'artists/index.html').read_text();assert 'feature-archive' in index and '/artists/az.html' in index
 from PIL import Image
 with Image.open(D/'feature-og/dj-premier.jpg') as im:assert im.format=='JPEG' and im.size==(1200,630)
print('Premier42 source-led feature; exact old15/499/source/515OGP preservation; role5/8 and archive routes PASS')
