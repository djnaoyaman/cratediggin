"""Exact contextual dates; no authentication of the embedded reference videos."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from catalog import year_label
F=json.loads((R/'scripts/fixtures/live-video-year-labels.json').read_text());tracks=json.loads((R/'tracks.json').read_text());ids={x['after']['id'] for x in F['records']}
sha=lambda b:hashlib.sha256(b).hexdigest()
assert len(tracks)==507 and len({x['id'] for x in tracks})==507
assert sha(json.dumps([x for x in tracks if x['id'] not in ids],ensure_ascii=False,sort_keys=True).encode())==F['unchangedRecordsSHA256']
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
for f in F['records']:
 old,t=f['before'],next(x for x in tracks if x['id']==f['after']['id']);assert t==f['after']
 assert t['youtube']==old['youtube'] and t['art']==old['art']
 allowed={'year','yearQualifier','yearBasis','yearDisplayNote','title','aliases','sources'}
 assert all(t.get(k)==old.get(k) for k in set(old)|set(t) if k not in allowed)
 assert year_label(t)==str(t['year'])+'年〈'+t['yearQualifier']+'〉'
 assert not t['youtube']['exactEditionVerified'] and not t['youtube']['playbackVerified']
 assert t['sources'][:len(old['sources'])]==old['sources']
d=json.loads((R/'editorial_deepdives.json').read_text());expected=F['beforeDeepdives']
for x in expected:
 if x['artist']=='DJ Shadow & Cut Chemist' and x['title']=='Product Placement (Live Video)':x['title']='Product Placement On Tour'
assert d==expected
# Normal unqualified catalog labels are unchanged.
for t in tracks:
 if t['id'] not in ids:assert year_label(t)==(str(t['year']) if isinstance(t.get('year'),int) else '発表年未確認')
if '--source-only' not in sys.argv:
 for f in F['records']:
  t=f['after'];html=(R/'dist/tracks'/ (t['id']+'.html')).read_text()
  assert year_label(t) in html and t['yearDisplayNote'] in html and t['title'] in html
  import re
  nodes=[json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>',html,re.S)]
  for node in nodes:
   for obj in node.get('@graph',[node]):
    if obj.get('@type') in ['VideoObject','MusicRecording']:assert obj.get('datePublished') not in ['2000','2004']
 timeline=(R/'dist/timeline.html').read_text()
 for f in F['records']:assert year_label(f['after']) in timeline and f['after']['yearDisplayNote'] in timeline
print('Two contextual live-video labels PASS; 505 other records/media/art unchanged')
