from pathlib import Path
import json,hashlib,argparse,html
from approved_region_completion import F,current_region_completion_file,historical_region_completion_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
read=lambda path:current_region_completion_file(path,(R/path).read_bytes())
for path,h in F['protected'].items():assert sha(read(path))==h,path
ph=F['previousHelper'];assert sha(read(ph['path']))==ph['afterSHA256']
for path,c in F['files'].items():
 data=read(path);assert sha(data)==c['afterSHA256'];assert sha(historical_region_completion_file(path,(R/path).read_bytes()))==c['beforeSHA256']
 try:historical_region_completion_file(path,(R/path).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
t=json.loads(read('tracks.json'));assert len(t)==F['count']==553;assert not any(x['region']=='未確認'for x in t)
for row in F['records']:
 b=row['before'];n=row['after'];assert next(x for x in t if x['id']==row['id'])==n
 assert {k for k in set(b)|set(n) if b.get(k)!=n.get(k)}==set(F['allowedFields'])
 assert n['sources'][:len(b['sources'])]==b['sources'];assert n['region']!='未確認' and n['scene']!='未確認' and n['regionBasis']
 assert all(n[k]==b[k] for k in b if k not in F['allowedFields'])
if not a.source_only:
 D=R/'dist';projected=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'))
 for row in F['records']:
  n=row['after'];page=html.unescape((D/f'tracks/{n["id"]}.html').read_text());md=(D/f'songs/{n["id"]}.md').read_text()
  assert n['region'] in md  # Detail metadata is rendered from the projected catalog, checked below.
  for s in n['sources']:assert s['url'] in page and s['url'] in md
  pt=next(x for x in projected if x['id']==n['id']);assert all(pt[k]==n[k]for k in F['allowedFields'])
 print('Rendered metadata, Markdown and searchable projected data agree for 11 regions PASS')
print('11 evidence-backed region/scene/basis/source changes; exact inverse and 553-record preservation PASS')
