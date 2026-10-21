from pathlib import Path
import json,argparse,html,sys,copy
from approved_research_batch09 import F,sha,historical_research_batch09_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
now=json.loads((R/'tracks.json').read_bytes());old=json.loads(historical_research_batch09_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(now)==len(old)==521
assert [t['id'] for t in now]==[t['id'] for t in old];changed=[(x,y) for x,y in zip(old,now) if x!=y];assert len(changed)==10
by={t['id']:t for t in now}
for row in F['rows']:
 t=by[row['id']];assert t==row['after'];assert {k for k in set(t)|set(row['before']) if t.get(k)!=row['before'].get(k)}==set(row['allowedFields'])
 assert set(row['allowedFields'])<=set(['essayTitle','deck','essay','essaySources','sources','context','listening','facts','sampleStatus'])
 for k in ['youtube','art','year','title','artist','audioVerificationStatus','versionBasis']:assert t.get(k)==row['before'].get(k),(t['id'],k)
 for k in ['producer','producers','sounds','samples','label']:assert t.get(k)==row['before'].get(k)
 if t['id'] not in ['jaylib-the-red','quasimoto-low-class-conspiracy']:assert t.get('facts')==row['before'].get('facts')
 else:
  assert t['facts'][0]==row['before']['facts'][0];assert len(t['facts'])==len(row['before']['facts'])==2
 if t['id']!='madlib-road-of-the-lonely-ones':assert t.get('sampleStatus')==row['before'].get('sampleStatus')
 assert sum(x.get('essayTitle')==t['essayTitle'] for x in now)==1
 assert len(t['essaySources'])==len(t['essay'])>=2
 for indices in t['essaySources']:assert all(type(i)==int and 0<=i<len(t['sources']) for i in indices)
 assert len(set([t['deck'],t['context'],*t['essay'],*t['listening']]))==2+len(t['essay'])+len(t['listening'])
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 raw=(R/path).read_bytes();before=historical_research_batch09_file(path,raw);assert sha(before)==c['beforeSHA256']
 for bad in [raw+b' ',before]:
  try:historical_research_batch09_file(path,bad)
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
 assert x['id']==y['id']
 reclassified={'madvillain-meat-grinder': 'voice'}
 expected_shelves=[reclassified[x['id']]] if x['id'] in reclassified else [z['shelf'] for z in x['tags']]
 assert [z['shelf'] for z in y['tags']]==expected_shelves

 if x!=y:
  shelfChanges.append(y['id']);assert y['id'] in by
  for tag in y['tags']:assert tag['evidence']=={'file':'tracks.json','field':'listening.0','quote':by[y['id']]['listening'][0]}
assert set(shelfChanges)<={row['id'] for row in F['rows']}
for row in F['rows']:
 prefix=row['after']['sources'][:len(row['before']['sources'])]
 for x,y in zip(prefix,row['before']['sources']):
  assert x==y
if not a.source_only:
 D=R/'dist';readings=html.unescape((D/'readings/index.html').read_text())
 for row in F['rows']:
  t=by[row['id']];page=html.unescape((D/('tracks/'+t['id']+'.html')).read_text());md=(D/('songs/'+t['id']+'.md')).read_text();d=next(x for x in deep if x['artist']==t['artist'] and x['title']==t['title'])
  for value in [t['essayTitle'],t['deck'],*t['essay']]:assert value in page,value
  assert t['essayTitle'] in readings and t['essayTitle'] in md
  for sec in d['sections']:assert sec['heading'] in page and sec['text'] in page and sec['source'] in page
  for ids in t['essaySources']:
   for i in ids:assert t['sources'][i]['url'] in page
print('Fresh research batch09:10 exact editorial deltas/source-backed distinct DIG sections/dependent shelf quotations;521 records, media/art preserved; only reviewed version facts and Road sample-status correction allowed; valid citations and negative mutation guards PASS'+(' source-only' if a.source_only else ', all10 static/Markdown/READINGS'))
