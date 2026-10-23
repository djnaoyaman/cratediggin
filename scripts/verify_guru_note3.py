from pathlib import Path
import json,hashlib,argparse,html
from approved_guru_note3 import F,current_guru_note3_file,historical_guru_note3_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
read=lambda path:current_guru_note3_file(path,(R/path).read_bytes())
for path,h in F['protected'].items():assert sha(read(path))==h,path
ph=F['previousHelper'];assert sha(read(ph['path']))==ph['afterSHA256']
for path,c in F['files'].items():
 data=read(path);assert sha(data)==c['afterSHA256'];assert sha(historical_guru_note3_file(path,(R/path).read_bytes()))==c['beforeSHA256']
 try:historical_guru_note3_file(path,(R/path).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
t=json.loads(read('tracks.json'));assert len(t)==F['count'];assert next(x for x in t if x['id']==F['id'])==F['after']
b=F['before'];n=F['after'];assert {k for k in set(b)|set(n) if b.get(k)!=n.get(k)}=={'facts','sources'}
assert n['facts'][:-1]==b['facts'] and n['sources'][:len(b['sources'])]==b['sources'];fact=n['facts'][-1]
assert fact['title']=='配信上のProducerクレジット' and all(isinstance(i,int) and 0<=i<len(n['sources']) for i in fact['sources'])
assert all(n[k]==b[k] for k in b if k not in F['allowedFields'])
if not a.source_only:
 D=R/'dist';page=html.unescape((D/f'tracks/{F["id"]}.html').read_text());md=(D/f'songs/{F["id"]}.md').read_text()
 assert fact['title'] in page and fact['text'] in page and fact['text'] in md
 for i in fact['sources']:assert n['sources'][i]['url'] in page and n['sources'][i]['url'] in md
 projected=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));pt=next(x for x in projected if x['id']==F['id']);assert pt['facts']==n['facts'] and pt['sources']==n['sources']
print('One article credit note: exact facts/source append, prior catalog and producers unchanged; limited correction, not research completion PASS')
