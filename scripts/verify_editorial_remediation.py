from approved_requested_two import historical_intake_tracks, historical_intake_file
"""Three exact editorial corrections; preserve all499 recordings and unrelated product bytes."""
import copy,hashlib,json,sys
from pathlib import Path
from approved_editorial_corrections import FIXTURE as f,digest,historical_editorial_record,historical_editorial_file
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from editorial_references import essay_references
tracks=historical_intake_tracks();assert len(tracks)==499 and [x['id'] for x in tracks]==f['orderedIds']
for t in tracks:assert digest(historical_editorial_record(t))==f['publishedRecords'][t['id']],t['id']
for name,h in f['protectedFiles'].items():assert hashlib.sha256(historical_editorial_file(name,(R/name).read_bytes())).hexdigest()==h,name
assert set(f['fileCorrections'])=={'listening_shelves.json','src/app/song-ui.js'}
for name,c in f['fileCorrections'].items():assert historical_editorial_file(name,(R/name).read_bytes())==c['before'].encode()
assert {x['id'] for x in f['corrections']}=={'j-live-hush-the-crowd','dj-shadow-midnight-in-a-perfect-world','a-tribe-called-quest-electric-relaxation'}
for c in f['corrections']:
 a,b=c['after'],c['before'];assert a['sources'][:len(b['sources'])]==b['sources']
 assert len(a['essay'])==3 and len(a['essaySources'])==3
 for i in range(3):assert essay_references(a,i)
 for field in ['title','artist','youtube','art','essay','context']:
  mutated=copy.deepcopy(a);mutated[field]='unapproved'
  try:historical_editorial_record(mutated)
  except AssertionError:pass
  else:raise AssertionError('Mutation accepted: '+field)
# Shelf evidence moves to an unchanged authored field, never inventing an acoustic claim.
shelf=json.loads((R/'listening_shelves.json').read_text());old=json.loads(f['fileCorrections']['listening_shelves.json']['before'])
assert shelf!=old
# All authored mappings are checked, not merely the three corrected articles.
mapped=[t for t in tracks if 'essaySources'in t];assert len(mapped)==66
for t in json.loads((R/'tracks.json').read_text()):
 for i in range(len(t['essay'])):essay_references(t,i)
base={'essay':['a'],'sources':[{'url':'https://example.org/a','label':'A'}]}
assert essay_references(base,0)==[]
assert essay_references(dict(base,essaySources=[[]]),0)==[]
assert len(essay_references(dict(base,essaySources=[[0,0]]),0))==1
for bad in [[],[None],[[True]],[[1]],[[-1]],[['0']]]:
 try:essay_references(dict(base,essaySources=bad),0)
 except AssertionError:pass
 else:raise AssertionError('Invalid citation accepted: '+repr(bad))
print('499 ordered recordings preserved; three exact six-field corrections, append-only sources and exact shelf/renderer deltas;66 valid paragraph-reference mappings, invalid-index/mutation rejection PASS')
