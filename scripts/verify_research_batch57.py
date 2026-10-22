from pathlib import Path
import json,argparse,sys,html,hashlib
from approved_research_batch57 import F,sha,historical_research_batch57_file as undo
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
assert sha((R/'scripts/fixtures/approved-research-batch57.json').read_bytes())=='2d595a5fc3e1b42b49634249c323abec6f23f410183a8a146235406a2f84d971'
assert len(F['rows'])==1
row=F['rows'][0];assert row['id']=='med-where-im-from'
now=json.loads((R/'tracks.json').read_bytes());old=json.loads(undo('tracks.json',(R/'tracks.json').read_bytes()))
assert len(now)==len(old)==522 and [t['id'] for t in now]==[t['id'] for t in old]
changed=[y['id'] for x,y in zip(old,now) if x!=y];assert changed==['med-where-im-from']
from approved_lost_in_thought import F as ADDED
# Published addition remains immutable independently of this old-catalog delta.
def assert_added(rows):
 assert len(rows)==522 and rows[-1]==ADDED['track']
 assert sum(t['id']==ADDED['track']['id'] for t in rows)==1
assert_added(now);assert_added(old)
assert json.loads((R/'graffiti_artwork.json').read_bytes())['tracks'][-1]==ADDED['artwork']
assert json.loads((R/'artist_entities.json').read_bytes())['Funkdoobiest']==ADDED['newArtistEntity']['Funkdoobiest']
assert sha((R/ADDED['asset']['path']).read_bytes())==ADDED['asset']['sha256']
for invalid in [now[:-1],now+[now[-1]],json.loads(json.dumps(now))]:
 if len(invalid)==522:invalid[-1]['title']+=' changed'
 try:assert_added(invalid)
 except AssertionError:pass
 else:raise AssertionError('Unapproved added-song mutation accepted')
by={t['id']:t for t in now};assert by[row['id']]==row['after']
assert {k for k in set(row['before'])|set(row['after']) if row['before'].get(k)!=row['after'].get(k)}==set(row['allowedFields'])==set(['essayTitle'])
for k in ['essay','deck','context','listening','essaySources','youtube','art','year','title','artist','producer','producers','sounds','label','audioVerificationStatus','versionBasis','sampleStatus']:
 assert row['after'].get(k)==row['before'].get(k),(row['id'],k)
for k in ['facts','samples','sources']:
 if k not in ['essayTitle']:assert row['after'].get(k)==row['before'].get(k)
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 raw=(R/path).read_bytes();before=undo(path,raw);assert sha(before)==c['beforeSHA256']
 for bad in [raw+b' ',before]:
  try:undo(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted')
deep=json.loads((R/'editorial_deepdives.json').read_text());assert deep==F['afterDeepDives']
assert F['beforeShelves']==F['afterShelves']==json.loads((R/'listening_shelves.json').read_text())
keys=(row['after']['artist'],row['after']['title'])
assert [d for d in deep if (d['artist'],d['title'])!=keys]==[d for d in F['beforeDeepDives'] if (d['artist'],d['title'])!=keys]
assert next((d for d in deep if (d['artist'],d['title'])==keys),None)==row['deepDiveAfter']
def changed_strings(a,b,path=''):
 if a==b:return []
 if isinstance(b,dict):return sum((changed_strings(a.get(k) if isinstance(a,dict) else None,v,path+'.'+k) for k,v in b.items()),[])
 if isinstance(b,list):return sum((changed_strings(a[i] if isinstance(a,list) and i<len(a) else None,v,path+f'.{i}') for i,v in enumerate(b)),[])
 return [(path,b)] if isinstance(b,str) and not path.endswith('.kind') else []
if not a.source_only:
 D=R/'dist';t=row['after'];page=html.unescape((D/('tracks/'+t['id']+'.html')).read_text());md=(D/('songs/'+t['id']+'.md')).read_text();readings=html.unescape((D/'readings/index.html').read_text())
 for field,value in changed_strings(row['before'],row['after'])+changed_strings(row['deepDiveBefore'],row['deepDiveAfter']):assert value in page,(field,value)
 for u in {x['url'] for x in row['before'].get('sources',[])}-{x['url'] for x in row['after'].get('sources',[])}:assert u not in page,u
 for value in [t['essayTitle'],t['deck'],*t['essay']]:assert value in page,value
 assert t['essayTitle'] in readings and t['essayTitle'] in md
 for sec in (row['deepDiveAfter'] or {}).get('sections',[]):
  for k in ['heading','text','source']:assert sec[k] in page
 for indices in t.get('essaySources',[]):
  for i in indices:assert t['sources'][i]['url'] in page
print('One exact article correction:522-record preservation, immutable approved fixture, metadata/media/depth and negative guards PASS; not full research completion')
