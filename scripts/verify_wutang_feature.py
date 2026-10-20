from pathlib import Path
import argparse,hashlib,json,re,sys
from PIL import Image
from approved_wutang_feature import F,historical_wutang_feature_file
from approved_triumph import historical_triumph_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');args=p.parse_args()
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert historical_wutang_feature_file(path,raw).decode()==c['before']
 try:historical_wutang_feature_file(path,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted')
for path,h in F['protected'].items():assert sha(historical_triumph_file(path,(R/path).read_bytes()))==h,path
old=json.loads(F['files']['features.json']['before']);current=json.loads((R/'features.json').read_text());assert current['policy']==old['policy'] and current['features'][:-1]==old['features'] and len(current['features'])==17
f=current['features'][-1];assert f==F['feature'] and f['id']=='wu-tang-clan' and f['type']=='artist'
from catalog import feature_tracks
from feature_policy import qualify_features
live_tracks=json.loads((R/'tracks.json').read_text());tracks=json.loads(historical_triumph_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(tracks)==502
live_ids=sorted(t['id'] for t in feature_tracks(live_tracks,f))
assert sorted(t['id'] for t in feature_tracks(tracks,f))==F['selectedIds'] and len(F['selectedIds'])==5
q=qualify_features(tracks,[f])[0]['qualification'];assert q['artistCount']==5 and q['tier']=='candidate'
e=f['editorial'];from feature_editorial import render_longform
body=render_longform(e,'/cratediggin');assert all(s['heading'] in body for s in e['sections'])
links=re.findall(r'\]\(#/song/([a-z0-9-]+)\)',json.dumps(e,ensure_ascii=False));assert links and set(links)<=set(F['selectedIds'])
for a in F['assets']:
 path=R/a['path'];assert sha(path.read_bytes())==a['sha256']
 with Image.open(path) as im:
  im.load();assert list(im.size)==a['dimensions'] and im.width<=2400
  if a['kind']=='tag':assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
assert sha((R/'src/assets'/f['visual']['photo']).read_bytes())==F['originalPhotoSHA256']
from editorial_uniqueness import authored,duplicates,new_violations
baseline=json.loads((R/'scripts/fixtures/editorial-legacy-debt.json').read_text());assert not new_violations(duplicates(authored(R)),baseline['groups'])
if not args.source_only:
 D=R/'dist';page=(D/'artists/wu-tang-clan.html').read_text();index=(D/'artists/index.html').read_text()
 assert body in page and ('収録作品 '+str(len(live_ids))+'曲') in page
 assert all(s['url'] in page for s in e['sources'])
 assert f['visual']['photo'] in index and f['visual']['tag'] in index
 registry=json.loads((D/'metadata.js').read_text().removeprefix('window.CRATE_PAGES=').strip().removesuffix(';'))
 image=registry['#/feature/wu-tang-clan']['image'];assert '/feature-og/wu-tang-clan.jpg?' in image
 assert 'https://djnaoyaman.github.io/cratediggin/artists/wu-tang-clan.html' in (D/'sitemap.xml').read_text()
 with Image.open(D/'feature-og/wu-tang-clan.jpg') as im:assert im.size==(1200,630)
 assert 'wu-tang-clan.html' in (D/'features/wu-tang-clan.html').read_text()
print('Wu-Tang feature: exact old16/502 preservation,5 group records, citations, photo/tag'+(' source PASS' if args.source_only else ', static routes/OGP PASS'))
