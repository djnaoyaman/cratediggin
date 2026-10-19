"""Canonical authored-copy audit. Exact/template debt is deterministic; meaning needs review."""
import html,json,re,unicodedata,hashlib,difflib
from collections import defaultdict
from pathlib import Path
DISCLOSURES={'ここに記したのは編者の聴感です。'}
def norm(s):
 s=html.unescape(re.sub(r'<[^>]*>','',s));s=unicodedata.normalize('NFKC',s)
 return ''.join(c for c in s if not c.isspace() and unicodedata.category(c)!='Cf')
def key(s):return ''.join(c for c in norm(s) if not unicodedata.category(c).startswith('P'))
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def authored(root):
 tracks=json.loads((root/'tracks.json').read_text());out=[];by={(x['artist'],x['title']):x for x in tracks}
 def put(owner,path,text,entities,role='body'):
  if not isinstance(text,str) or not text.strip():return
  out.append({'owner':owner,'path':path,'text':text,'entities':entities,'role':role})
 for x in tracks:
  ent=[x.get(k,'') for k in ['title','artist','album']]+[str(x.get('year',''))]
  put(x['id'],'essayTitle',x.get('essayTitle',''),ent,'headline');put(x['id'],'deck',x.get('deck',''),ent,'deck')
  for field in ['essay','listening']:
   for i,s in enumerate(x.get(field,[])):put(x['id'],f'{field}.{i}',s,ent)
 for d in json.loads((root/'editorial_deepdives.json').read_text()):
  x=by.get((d['artist'],d['title']));owner=x['id'] if x else 'deep:'+d['artist']+':'+d['title'];ent=[d['artist'],d['title']]
  for i,s in enumerate(d.get('sections',[])):
   # Section headings are included; repeated functional labels remain visible legacy debt.
   put(owner,f'deep.{i}.heading',s.get('heading',''),ent,'headline');put(owner,f'deep.{i}.text',s.get('text',''),ent)
 for x in json.loads((root/'features.json').read_text())['features']:
  ent=x.get('names',[x.get('name','')]);owner='feature:'+x['id']
  for k,v in x.get('editorial',{}).items():
   if isinstance(v,str):put(owner,'editorial.'+k,v,ent,'headline' if k=='title' else 'body')
  p=x.get('personalFeature',{})
  for i,s in enumerate(p.get('paragraphs',[])):put(owner,f'personal.{i}',s,ent)
 return out

def units(rows):
 for r in rows:
  if r['text'] in DISCLOSURES:continue
  texts=[('whole',r['text'])]
  if r['role']!='headline':texts += [('sentence',s) for s in re.split(r'(?<=[。！？!?])',r['text']) if len(key(s))>=16 and s not in DISCLOSURES]
  for part,s in texts:
   if not key(s):continue
   for mode,value in [('exact',norm(s)),('punctuation',key(s))]:
    yield mode,sha(value),{'owner':r['owner'],'path':r['path'],'part':part,'textSHA256':sha(s)}
   masked=norm(s)
   for entity in sorted(set(r['entities']),key=len,reverse=True):
    if entity and len(entity)>=2:masked=masked.replace(norm(entity),'<ENTITY>')
   if '<ENTITY>' in masked and len(key(masked.replace('<ENTITY>','')))>=12:
    yield 'template',sha(key(masked)),{'owner':r['owner'],'path':r['path'],'part':part,'textSHA256':sha(s)}

def duplicates(rows):
 groups=defaultdict(list)
 for mode,k,o in units(rows):
  if o not in groups[mode+':'+k]:groups[mode+':'+k].append(o)
 return {k:sorted(v,key=lambda x:(x['owner'],x['path'],x['part'])) for k,v in groups.items() if len({x['owner'] for x in v})>1}
def new_violations(current,baseline):
 return {k:v for k,v in current.items() if k not in baseline or any(x not in baseline[k] for x in v)}
def neighbors(rows,touched):
 # Always expose nearest neighbors, even below a heuristic threshold. Scores are not meaning.
 out=[]
 for r in rows:
  if r['owner'] not in touched or r['path'].startswith('deep.'):continue
  ranked=[]
  for other in rows:
   if r['owner']==other['owner']:continue
   a,b=key(r['text']),key(other['text'])
   ag={a[i:i+3] for i in range(max(1,len(a)-2))};bg={b[i:i+3] for i in range(max(1,len(b)-2))}
   score=len(ag&bg)/len(ag|bg) if ag|bg else 0
   ranked.append((score,other))
  for score,o in sorted(ranked,key=lambda x:x[0],reverse=True)[:5]:out.append({'owner':r['owner'],'path':r['path'],'textSHA256':sha(r['text']),'neighbor':o['owner'],'neighborPath':o['path'],'neighborTextSHA256':sha(o['text']),'trigramJaccard':round(score,4)})
 return out
