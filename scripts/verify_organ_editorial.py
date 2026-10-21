"""One cited editorial correction, without any recording, artwork or credit change."""
from pathlib import Path
import argparse,json,sys
from approved_organ_editorial import F,historical_organ_file,sha
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for name,spec in F['files'].items():
 raw=(R/name).read_bytes();old=historical_organ_file(name,raw);assert sha(old)==spec['beforeSHA256']
 for bad in [raw+b' ',old]:
  try:historical_organ_file(name,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved partial/drift accepted')
for name,h in F['protected'].items():assert sha((R/name).read_bytes())==h,name
tracks=json.loads((R/'tracks.json').read_text());old=json.loads(historical_organ_file('tracks.json',(R/'tracks.json').read_bytes()))
assert len(tracks)==len(old)==505
changed=[(x,y) for x,y in zip(old,tracks) if x!=y];assert len(changed)==1
before,t=changed[0];c=F['correction'];assert before==c['before'] and t==c['after']
assert {k for k in set(before)|set(t) if before.get(k)!=t.get(k)}==set(c['allowedFields'])=={'essayTitle','deck','essay','essaySources','sources','context','listening'}
assert t['id']=='dj-shadow-organ-donor' and t['essayTitle']=='嫌われると思っていた、あの反復。'
assert t['essayTitle'] not in {x['essayTitle'] for x in tracks if x['id']!=t['id']}
assert len(set([t['deck'],t['context'],*t['essay'],*t['listening']]))==5
assert t['sources'][:-2]==before['sources'];assert t['sources'][2]['url']=='https://www.musicradar.com/news/tech/dj-shadow-on-key-influences-over-the-years-and-the-gear-he-just-cant-do-without-643390'
assert t['essaySources']==[[2],[2]]
assert '2016年' in t['essay'][0] and '嫌われ' in t['essay'][0] and 'Extended Overhaul' in t['context']
from editorial_uniqueness import authored,duplicates,new_violations
baseline=json.loads((R/'scripts/fixtures/editorial-legacy-debt.json').read_text());assert not new_violations(duplicates(authored(R)),baseline['groups'])
if not a.source_only:
 D=R/'dist';html=(D/'tracks/dj-shadow-organ-donor.html').read_text();md=(D/'songs/dj-shadow-organ-donor.md').read_text();readings=(D/'readings/index.html').read_text()
 for value in [t['essayTitle'],t['deck'],*t['essay']]:assert value in html,value
 assert t['essayTitle'] in md and t['essayTitle'] in readings
 assert t['sources'][2]['url'] in html and 'essay-references' in html
print('Organ Donor: exactly seven editorial fields, 504 other works and all media/art/credits unchanged; sourced artist recollection, original/Extended distinction, unique copy, negative drift checks'+(' (source-only)' if a.source_only else ', generated article/Markdown/READINGS PASS'))
