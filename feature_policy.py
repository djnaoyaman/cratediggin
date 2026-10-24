"""Role-separated catalog qualification; related selections never inflate identity counts."""
from collections import defaultdict
ALIASES={'The Large Professor':'Large Professor','Jay Dee':'J Dilla','Jay Dee (remix)':'J Dilla','Quasimoto':'Madlib','CL Smooth':'C.L. Smooth'}
def role_projection(tracks):
    artists=defaultdict(set);producers=defaultdict(set)
    for t in tracks:
        if t.get('workType','single')!='single':continue
        names=set([t['artist'].split(' feat. ')[0]]+t.get('artists',[]))
        # The Red's existing association array also names its beatmaker; not a vocal credit.
        if t['id']=='jaylib-the-red':names.discard('J Dilla')
        for n in names:artists[ALIASES.get(n,n)].add(t['id'])
        for n in t.get('producers',[]):producers[ALIASES.get(n,n)].add(t['id'])
    result={}
    for name in sorted(set(artists)|set(producers)):
        a=artists[name];p=producers[name];n=max(len(a),len(p))
        result[name]={'artistIds':sorted(a),'producerIds':sorted(p),'artistCount':len(a),'producerCount':len(p),'unionCount':len(a|p),'tier':'priority' if n>=8 else 'candidate' if n>=5 else 'archive'}
    return result

def qualify_features(tracks,features):
    roles=role_projection(tracks)
    result=[dict(f,qualification=roles.get(ALIASES.get(f['names'][0],f['names'][0]),{'artistIds':[],'producerIds':[],'artistCount':0,'producerCount':0,'unionCount':0,'tier':'archive'})) for f in features if f.get('editorial')]
    for f in result:
        if f['type']=='artist' and f.get('scopeOwnNames'):
            own=sorted(t['id'] for t in tracks if t.get('workType','single')=='single' and t['artist'].split(' feat. ')[0] in f['scopeOwnNames'])
            n=len(own);f['qualification']=dict(artistIds=own,producerIds=[],artistCount=n,producerCount=0,unionCount=n,tier='priority' if n>=8 else 'candidate' if n>=5 else 'archive')
    return result

def qualification_label(f):
    q=f['qualification'];n=q['artistCount'] if f['type']=='artist' else q['producerCount']
    role='アーティスト名義' if f['type']=='artist' else '制作クレジット'
    tier={'priority':'優先特集','candidate':'特集候補','archive':'アーカイブ'}[q['tier']]
    return f'{role} {n}曲 · {tier}'
