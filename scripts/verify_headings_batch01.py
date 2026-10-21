from pathlib import Path
import json,argparse,html
from approved_headings_batch01 import F,sha,historical_headings_batch01_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
raw=(R/'tracks.json').read_bytes();now=json.loads(raw);old=json.loads(historical_headings_batch01_file('tracks.json',raw));assert len(now)==len(old)==521
changed=[(x,y) for x,y in zip(old,now) if x!=y];assert len(changed)==29
assert {y['id'] for x,y in changed}=={r['id'] for r in F['rows']}
for x,y in changed:
 assert {k for k in set(x)|set(y) if x.get(k)!=y.get(k)}=={'essayTitle'}
 assert sum(t.get('essayTitle')==y['essayTitle'] for t in now)==1
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 data=(R/path).read_bytes();historical_headings_batch01_file(path,data)
 for bad in [data+b' ',historical_headings_batch01_file(path,data)]:
  try:historical_headings_batch01_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted')
if not a.source_only:
 D=R/'dist';readings=html.unescape((D/'readings/index.html').read_text())
 for row in F['rows']:
  assert row['new'] in html.unescape((D/('tracks/'+row['id']+'.html')).read_text())
  assert row['new'] in (D/('songs/'+row['id']+'.md')).read_text()
  assert row['new'] in readings
print('29/226 headings individualized: exact essayTitle-only delta,521 records and all bodies/media/art preserved, global uniqueness and negative drift checks PASS'+(' source-only' if a.source_only else '; all29 static article/Markdown/READINGS projections PASS'))
