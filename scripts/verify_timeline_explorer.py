from approved_brand_identity import historical_brand_social_digest
from pathlib import Path
import sys,json,hashlib,subprocess,copy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R));from catalog_explorer import aggregate,summary
from approved_timeline_explorer import historical_explorer_file
from approved_artifacts_credits import historical_credit_file
F=json.loads((R/'scripts/fixtures/approved-timeline-explorer.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();tracks=json.loads((R/'tracks.json').read_text())
assert len(tracks)==501 and [t['id'] for t in tracks]==F['catalogIds']
for path,h in F['protected'].items():assert sha(historical_credit_file(path,(R/path).read_bytes()))==h,path
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_credit_file(path,data))==c['afterSHA256'];assert sha(historical_explorer_file(path,data))==c['beforeSHA256']
 try:historical_explorer_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted: '+path)
assert historical_explorer_file('unrelated-sentinel.txt',b'changed')==b'changed'
s=summary(tracks);assert s['total']==501 and s['yearsKnown']==499 and s['producerKnown']==386 and s['soundKnown']==480
js=json.loads(subprocess.check_output(['node','-e',"const E=require('./src/assets/catalog-explorer.js'),t=require('./tracks.json');console.log(JSON.stringify(Object.fromEntries(['type','decade','year','region','artist','producer','category','sound'].map(k=>[k,Object.fromEntries(E.aggregate(t,k).map(r=>[r.value,r.count]))]))))"],cwd=R))
for key,v in js.items():assert aggregate(tracks,key)==v,key
D=R/'dist'
if D.exists():
 for path,h in F['socialImages'].items():assert historical_brand_social_digest(path,(D/path).read_bytes())==h,path
 html=(D/'timeline.html').read_text();assert 'ce-static' in html and '501掲載作品' in html and '制作名義未登録' in html and 'タグ未登録' in html
 for t in tracks:assert '/tracks/'+t['id']+'.html' in html
 assert 'catalog-explorer.js?v='+json.loads((R/'releases.json').read_text())['version'] in html
 assert len(F['socialImages'])==519
 release=json.loads(historical_credit_file('releases.json',(R/'releases.json').read_bytes()));assert release['version']=='22.0' and release['history'][-1]['version']=='22.0'
print('Timeline501 exact content/art preservation;519 OGP unchanged; Python/JS bins identical; no-JS full chronology and exact correction mutation guards PASS')
