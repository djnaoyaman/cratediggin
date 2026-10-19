"""Two primary-label credit corrections, never broad catalog normalization."""
from pathlib import Path
import json,hashlib,copy,sys
from approved_artifacts_credits import historical_credit_file
from approved_queue_scope import historical_queue_scope_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from feature_policy import role_projection
from catalog import feature_tracks
from catalog_explorer import aggregate,summary
F=json.loads((R/'scripts/fixtures/approved-artifacts-credits.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();raw=(R/'tracks.json').read_bytes();tracks=json.loads(raw);old=json.loads(historical_credit_file('tracks.json',raw))
assert len(tracks)==len(old)==501 and [t['id'] for t in tracks]==F['orderedIds']
assert {r['after']['id'] for r in F['records']}=={'artifacts-wrong-side-of-da-tracks','artifacts-whassup-now-muthafucka'}
changed={i for i,(a,b) in enumerate(zip(old,tracks)) if a!=b};assert changed=={r['index'] for r in F['records']}
for r in F['records']:
 a,b=r['before'],r['after'];assert old[r['index']]==a and tracks[r['index']]==b
 fields={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)};assert fields=={'producer','producers','sources','facts'}
 assert b['producer']=='T-Ray; co-produced by Artifacts' and b['producers']==['T-Ray','Artifacts']
 assert b['sources'][:-1]==a['sources'] and b['facts'][:-1]==a['facts']
 assert b['facts'][-1]['sources']==[len(b['sources'])-1] and 'LP Version' in b['facts'][-1]['text']
 assert b['sources'][-1]['url'].startswith('https://ellarecords.jp/cdn/shop/files/20260117_09')
 assert '1994' in b['sources'][-1]['label'] and b['sources'][-1]['kind']=='原盤画像（第三者レコード店掲載）'
 for field in ['youtube','art','essay','deck','samples','sampleStatus','title','artist','album']:
  assert a[field]==b[field],(b['id'],field)
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_credit_file(path,data))==c['beforeSHA256']
 bads=[data+b' ']
 if path=='tracks.json':
  for index in [0,128,499,500]:
   v=copy.deepcopy(tracks);v[index]['unapproved']='drift';bads.append((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
  for v in [tracks[:-1],list(reversed(tracks)),tracks+[tracks[-1]]]:bads.append((json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode())
 for bad in bads:
  try:historical_credit_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Drift accepted: '+path)
assert historical_credit_file('src/app/player.js',b'changed')==b'changed'
roles0=role_projection(old);roles1=role_projection(tracks);assert {k for k in roles0.keys()|roles1.keys() if roles0.get(k)!=roles1.get(k)}=={'Artifacts','Buckwild','T-Ray'}
for name,n in [('Buckwild',8),('T-Ray',3),('Artifacts',2)]:assert roles1[name]['producerCount']==n
assert {k for k,v in roles0.items() if v['tier']!='archive'}=={k for k,v in roles1.items() if v['tier']!='archive'}
assert sum(v['tier']=='priority' for v in roles1.values())==23
features=json.loads((R/'features.json').read_text())['features'];assert len(features)==16
original_features=json.loads(historical_credit_file('features.json',(R/'features.json').read_bytes()))['features']
assert [f['id'] for f in features]==[f['id'] for f in original_features]
for a,b in zip(original_features,features):
 if a['id']=='dj-premier':
  expected=copy.deepcopy(a);expected['visual']['tag']='feature-dj-premier-tag.webp';expected['visual'].pop('typographicName');assert b==expected
 else:assert a==b
from PIL import Image
def require_complete(feature):
 v=feature.get('visual',{});assert feature.get('name') and feature.get('editorial',{}).get('title')
 assert v.get('photo') and v.get('tag') and v.get('alt') and v.get('credit') and v.get('provenance')
 assert not v.get('typographicName') and not v.get('nameOnly')
for feature in features:
 require_complete(feature)
 for key in ['photo','tag','alt','credit','provenance']:
  bad=copy.deepcopy(feature);bad['visual'].pop(key,None)
  try:require_complete(bad)
  except AssertionError:pass
  else:raise AssertionError('Incomplete feature accepted: '+feature['id']+'/'+key)
for f in features:
 v=f['visual'];assert v.get('photo') and v.get('tag') and v['precomposed'] and v['provenance']=='user-provided' and v['credit']=='ユーザー提供'
 assert v.get('alt') and v['fit']=='contain'
 for key in ['photo','tag']:assert (R/'src/assets'/v[key]).is_file(),(f['id'],key)
 with Image.open(R/'src/assets'/v['tag']) as im:assert im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
t=F['premierTag'];assert sha((R/t['path']).read_bytes())==t['sha256']
with Image.open(R/t['path']) as im:assert list(im.size)==t['dimensions'] and sha(im.convert('RGBA').tobytes())==t['rgbaSHA256']
assert (R/'FEATURE_COMPLETENESS.md').exists()

for f in features:assert [x['id'] for x in feature_tracks(old,f)]==[x['id'] for x in feature_tracks(tracks,f)]
assert summary(old)==summary(tracks)
bins=aggregate(tracks,'producer');assert bins['__missing__']==115 and len(bins)==181 and sum(n for k,n in bins.items() if k!='__missing__')==450
release=json.loads(historical_queue_scope_file('releases.json',(R/'releases.json').read_bytes()));before=json.loads(F['files']['releases.json']['before']);assert release==dict(before,version='22.1')
D=R/'dist'
if D.exists():
 assert (D/Path(t['path']).name).read_bytes()==(R/t['path']).read_bytes()
 for path,h in F['socialImages'].items():assert sha((D/path).read_bytes())==h,path
 assert len(F['socialImages'])==519
 for r in F['records']:
  t=r['after'];html=(D/'tracks'/f"{t['id']}.html").read_text();md=(D/'tracks'/f"{t['id']}.md").read_text()
  for text in [t['facts'][-1]['text'],t['sources'][-1]['label']]:assert text in html and text in md,text
 client=(D/'tracks.js').read_text();assert all(r['after']['producer'] in client for r in F['records'])
 timeline=(D/'timeline.html').read_text();assert '501掲載作品' in timeline and json.loads((R/'releases.json').read_text())['version'] in timeline
print('Two exact original-LP credit corrections; all501 media/art/prose,16 feature selections,519 OGP preserved; counts and mutation guards PASS')
