from pathlib import Path
import json
from approved_person_queue import F,sha,historical_person_queue_file
R=Path(__file__).resolve().parents[1]
for p,c in F['files'].items():
 raw=(R/p).read_bytes();assert sha(historical_person_queue_file(p,raw))==c['beforeSHA256']
 for bad in [raw+b' ',c['before'].encode()]:
  try:historical_person_queue_file(p,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved drift accepted: '+p)
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
assert len(json.loads((R/'tracks.json').read_text()))==505
print('Exact 2-module person queue delta; 505 records, all features/articles/profile and other transport modules unchanged; negative drift checks PASS')
