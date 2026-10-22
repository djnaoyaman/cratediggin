from pathlib import Path
import json,argparse,html,sys,copy
from approved_research_batch37 import F,sha,historical_research_batch37_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
now=json.loads((R/'tracks.json').read_bytes());old=json.loads(historical_research_batch37_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(now)==len(old)==522
assert [t['id'] for t in now]==[t['id'] for t in old];changed=[(x,y) for x,y in zip(old,now) if x!=y];assert len(changed)==6
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
by={t['id']:t for t in now}
for row in F['rows']:
 t=by[row['id']];assert t==row['after'];assert {k for k in set(t)|set(row['before']) if t.get(k)!=row['before'].get(k)}==set(row['allowedFields'])
 assert set(row['allowedFields'])<=set(['essayTitle','deck','essay','essaySources','sources','context','listening','facts','sampleStatus'])
 for k in ['youtube','art','year','title','artist','audioVerificationStatus','versionBasis']:assert t.get(k)==row['before'].get(k),(t['id'],k)
 for k in ['producer','producers','sounds','samples','label']:assert t.get(k)==row['before'].get(k)
 assert t.get('facts')==row['before'].get('facts')
 assert t.get('sampleStatus')==row['before'].get('sampleStatus')
 assert sum(x.get('essayTitle')==t['essayTitle'] for x in now)==1
 assert len(t['essaySources'])==len(t['essay'])>=2
 for indices in t['essaySources']:assert all(type(i)==int and 0<=i<len(t['sources']) for i in indices)
 assert len(set([t['deck'],t['context'],*t['essay'],*t['listening']]))==2+len(t['essay'])+len(t['listening'])
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 raw=(R/path).read_bytes();before=historical_research_batch37_file(path,raw);assert sha(before)==c['beforeSHA256']
 for bad in [raw+b' ',before]:
  try:historical_research_batch37_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted')
deep=json.load(open(R/'editorial_deepdives.json'));keys={(r['after']['artist'],r['after']['title']) for r in F['rows']};unchanged=lambda d:[x for x in d if (x['artist'],x['title']) not in keys];assert unchanged(deep)==unchanged(F['beforeDeepDives'])
sys.path.insert(0,str(R));from editorial_references import section_references
for row in F['rows']:
 t=by[row['id']];d=next((x for x in deep if x['artist']==t['artist'] and x['title']==t['title']),None);assert d==row['deepDiveAfter']
 if d is None:continue
 for sec in d['sections']:assert sec['text'] not in t['essay'];assert section_references(t,sec)
expected=copy.deepcopy(F['beforeShelves'])
changes=[]
for change in changes:
 idx=next(i for i,e in enumerate(expected['tracks']) if e['id']==change['id']);assert expected['tracks'][idx]==change['before']
 if change['after'] is None:expected['tracks'].pop(idx)
 else:expected['tracks'][idx]=copy.deepcopy(change['after'])
assert expected==F['afterShelves']
for row in F['rows']:
 prefix=row['after']['sources'][:len(row['before']['sources'])]
 for x,y in zip(prefix,row['before']['sources']):
  assert x==y
if not a.source_only:
 D=R/'dist';readings=html.unescape((D/'readings/index.html').read_text())
 for row in F['rows']:
  t=by[row['id']];page=html.unescape((D/('tracks/'+t['id']+'.html')).read_text());md=(D/('songs/'+t['id']+'.md')).read_text();d=next((x for x in deep if x['artist']==t['artist'] and x['title']==t['title']),{'sections':[]})
  for value in [t['essayTitle'],t['deck'],*t['essay']]:assert value in page,value
  assert t['essayTitle'] in readings and t['essayTitle'] in md
  for sec in d['sections']:assert sec['heading'] in page and sec['text'] in page and sec['source'] in page
  for ids in t['essaySources']:
   for i in ids:assert t['sources'][i]['url'] in page
print('Fresh research batch37:6 exact editorial deltas/source-backed distinct DIG sections/dependent shelf quotations;522 records, media/art preserved; facts, sample metadata and media unchanged; valid citations and negative mutation guards PASS'+(' source-only' if a.source_only else ', all6 static/Markdown/READINGS'))
