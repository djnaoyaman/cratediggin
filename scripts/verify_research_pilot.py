from pathlib import Path
import json,argparse,html,sys,copy
from approved_research_pilot import F,sha,historical_research_pilot_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
now=json.loads((R/'tracks.json').read_bytes());old=json.loads(historical_research_pilot_file('tracks.json',(R/'tracks.json').read_bytes()));assert len(now)==len(old)==521
assert [t['id'] for t in now]==[t['id'] for t in old];changed=[(x,y) for x,y in zip(old,now) if x!=y];assert len(changed)==5
by={t['id']:t for t in now}
for row in F['rows']:
 t=by[row['id']];assert t==row['after'];assert {k for k in set(t)|set(row['before']) if t.get(k)!=row['before'].get(k)}==set(row['allowedFields'])
 assert set(row['allowedFields'])<=set(['essayTitle','deck','essay','essaySources','sources','context','listening','sounds'])
 for k in ['youtube','art','samples','facts','producer','producers','year','title','artist']:assert t.get(k)==row['before'].get(k),(t['id'],k)
 assert sum(x.get('essayTitle')==t['essayTitle'] for x in now)==1
 assert len(t['essaySources'])==len(t['essay'])>=3
 for indices in t['essaySources']:assert indices and all(type(i)==int and 0<=i<len(t['sources']) for i in indices)
 assert len(set([t['deck'],t['context'],*t['essay'],*t['listening']]))==2+len(t['essay'])+len(t['listening'])
 if 'sounds' in row['allowedFields']:assert t['id']=='dj-shadow-organ-donor' and t['sounds']==[x for x in row['before']['sounds'] if x!='声の掛け合い']
for path,h in F['protected'].items():assert sha((R/path).read_bytes())==h,path
for path,c in F['files'].items():
 raw=(R/path).read_bytes();before=historical_research_pilot_file(path,raw);assert sha(before)==c['beforeSHA256']
 for bad in [raw+b' ',before]:
  try:historical_research_pilot_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted')
deep=json.load(open(R/'editorial_deepdives.json'));keys={(r['after']['artist'],r['after']['title']) for r in F['rows']};unchanged=lambda d:[x for x in d if (x['artist'],x['title']) not in keys];assert unchanged(deep)==unchanged(F['beforeDeepDives'])
sys.path.insert(0,str(R));from editorial_references import section_references
for row in F['rows']:
 t=by[row['id']];d=next(x for x in deep if x['artist']==t['artist'] and x['title']==t['title']);assert len(d['sections'])==2
 for sec in d['sections']:assert sec['text'] not in t['essay'];assert section_references(t,sec)
oldShelves=F['beforeShelves'];newShelves=F['afterShelves'];assert oldShelves['policy']==newShelves['policy'] and oldShelves['shelves']==newShelves['shelves']
shelfChanges=[]
for x,y in zip(oldShelves['tracks'],newShelves['tracks']):
 assert x['id']==y['id'] and [z['shelf'] for z in x['tags']]==[z['shelf'] for z in y['tags']]
 if x!=y:
  shelfChanges.append(y['id']);assert y['id'] in by
  for tag in y['tags']:assert tag['evidence']=={'file':'tracks.json','field':'listening.0','quote':by[y['id']]['listening'][0]}
assert set(shelfChanges)=={'a-tribe-called-quest-check-the-rhime','j-dilla-workinonit','madvillain-all-caps'}
assert by['a-tribe-called-quest-check-the-rhime']['sources'][1]['url']=='https://www.averagewhiteband.com/bio'
assert by['wu-tang-clan-c-r-e-a-m']['sources'][1]['url'].startswith('https://newsroom.spotify.com/')
assert by['j-dilla-workinonit']['sources'][1]['url']=='https://dilla.bandcamp.com/album/donuts'
if not a.source_only:
 D=R/'dist';readings=html.unescape((D/'readings/index.html').read_text())
 for row in F['rows']:
  t=by[row['id']];page=html.unescape((D/('tracks/'+t['id']+'.html')).read_text());md=(D/('songs/'+t['id']+'.md')).read_text();d=next(x for x in deep if x['artist']==t['artist'] and x['title']==t['title'])
  for value in [t['essayTitle'],t['deck'],*t['essay'],t['context'],*t['listening']]:assert value in page,value
  assert t['essayTitle'] in readings and t['essayTitle'] in md
  for sec in d['sections']:assert sec['heading'] in page and sec['text'] in page and sec['source'] in page
  for ids in t['essaySources']:
   for i in ids:assert t['sources'][i]['url'] in page
print('Fresh research pilot:5 exact editorial deltas/10 distinct DIG sections/3 shelf quotations;521 records, media/art/credits preserved; valid citations and negative mutation guards PASS'+(' source-only' if a.source_only else ', all5 static/Markdown/READINGS'))
