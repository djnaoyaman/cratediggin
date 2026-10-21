from pathlib import Path
import json,argparse,html,sys,copy
from approved_research_batch06 import F,sha,historical_research_batch06_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
now=json.loads((R/'tracks.json').read_bytes());old=json.loads(historical_research_batch06_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(now)==len(old)==521
assert [t['id'] for t in now]==[t['id'] for t in old];changed=[(x,y) for x,y in zip(old,now) if x!=y];assert len(changed)==10
by={t['id']:t for t in now}
for row in F['rows']:
 t=by[row['id']];assert t==row['after'];assert {k for k in set(t)|set(row['before']) if t.get(k)!=row['before'].get(k)}==set(row['allowedFields'])
 assert set(row['allowedFields'])<=set(['essayTitle','deck','essay','essaySources','sources','context','listening','sounds','facts','samples'])
 for k in ['youtube','art','year','title','artist','audioVerificationStatus','versionBasis']:assert t.get(k)==row['before'].get(k),(t['id'],k)
 for k in ['producer','producers']:assert t.get(k)==row['before'].get(k)
 if t['id']!='runnin':assert t.get('sounds')==row['before'].get('sounds')
 if t['id']!='93-til-infinity':assert t.get('facts')==row['before'].get('facts')
 if t['id'] not in ['runnin','the-pharcyde-passin-me-by']:assert t.get('samples')==row['before'].get('samples')
 if t['id'] in ['runnin','the-pharcyde-passin-me-by']:
  assert len(t['samples'])==len(row['before']['samples'])
  for x,y in zip(t['samples'],row['before']['samples']):assert {k:v for k,v in x.items() if k not in ['role','sources']}=={k:v for k,v in y.items() if k not in ['role','sources']}
 if t['id']=='93-til-infinity':assert t['facts'][:1]+t['facts'][2:]==row['before']['facts'][:1]+row['before']['facts'][2:]
 assert sum(x.get('essayTitle')==t['essayTitle'] for x in now)==1
 assert len(t['essaySources'])==len(t['essay'])>=2
 for indices in t['essaySources']:assert all(type(i)==int and 0<=i<len(t['sources']) for i in indices)
 assert len(set([t['deck'],t['context'],*t['essay'],*t['listening']]))==2+len(t['essay'])+len(t['listening'])
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 raw=(R/path).read_bytes();before=historical_research_batch06_file(path,raw);assert sha(before)==c['beforeSHA256']
 for bad in [raw+b' ',before]:
  try:historical_research_batch06_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted')
deep=json.load(open(R/'editorial_deepdives.json'));keys={(r['after']['artist'],r['after']['title']) for r in F['rows']};unchanged=lambda d:[x for x in d if (x['artist'],x['title']) not in keys];assert unchanged(deep)==unchanged(F['beforeDeepDives'])
sys.path.insert(0,str(R));from editorial_references import section_references
for row in F['rows']:
 t=by[row['id']];d=next(x for x in deep if x['artist']==t['artist'] and x['title']==t['title']);assert d==row['deepDiveAfter']
 for sec in d['sections']:assert sec['text'] not in t['essay'];assert section_references(t,sec)
oldShelves=F['beforeShelves'];newShelves=F['afterShelves'];assert oldShelves['policy']==newShelves['policy'] and oldShelves['shelves']==newShelves['shelves']
shelfChanges=[]
for x,y in zip(oldShelves['tracks'],newShelves['tracks']):
 assert x['id']==y['id'] and [z['shelf'] for z in x['tags']]==[z['shelf'] for z in y['tags']]
 if x!=y:
  shelfChanges.append(y['id']);assert y['id'] in by
  for tag in y['tags']:assert tag['evidence']=={'file':'tracks.json','field':'listening.0','quote':by[y['id']]['listening'][0]}
assert set(shelfChanges)<={row['id'] for row in F['rows']}
for row in F['rows']:
 assert row['after']['sources'][:len(row['before']['sources'])]==row['before']['sources']
if not a.source_only:
 D=R/'dist';readings=html.unescape((D/'readings/index.html').read_text())
 for row in F['rows']:
  t=by[row['id']];page=html.unescape((D/('tracks/'+t['id']+'.html')).read_text());md=(D/('songs/'+t['id']+'.md')).read_text();d=next(x for x in deep if x['artist']==t['artist'] and x['title']==t['title'])
  for value in [t['essayTitle'],t['deck'],*t['essay']]:assert value in page,value
  assert t['essayTitle'] in readings and t['essayTitle'] in md
  for sec in d['sections']:assert sec['heading'] in page and sec['text'] in page and sec['source'] in page
  for ids in t['essaySources']:
   for i in ids:assert t['sources'][i]['url'] in page
print('Fresh research batch06:10 exact editorial deltas/source-backed distinct DIG sections/dependent shelf quotations;521 records, media/art preserved; two instrument-neutral sample descriptions and one precise earlier-song clarification; valid citations and negative mutation guards PASS'+(' source-only' if a.source_only else ', all10 static/Markdown/READINGS'))
