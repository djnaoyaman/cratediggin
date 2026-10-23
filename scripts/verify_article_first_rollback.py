from pathlib import Path
import json,hashlib,argparse,subprocess
from approved_article_first_rollback import F,historical_article_first_rollback_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():
 if path=='audit-reports/maintenance.json':assert sha((R/path).read_bytes())==F['generatedAuditSHA256'];continue
 assert sha((R/path).read_bytes())==h,path
assert sha((R/F['previousHelper']['path']).read_bytes())==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(data)==c['afterSHA256'];assert sha(historical_article_first_rollback_file(path,data))==c['beforeSHA256']
 for mutated in [data+b' ',data[:-1]]:
  try:historical_article_first_rollback_file(path,mutated)
  except AssertionError:pass
  else:raise AssertionError('Mutation accepted '+path)
for path,h in F['approvedCatalogSHA256'].items():assert sha((R/path).read_bytes())==h,path
T=json.loads((R/'tracks.json').read_text());assert len(T)==562 and len({t['id']for t in T})==562 and not(set(F['removedIds'])&{t['id']for t in T})
core=(R/'src/app/core.js').read_text().split(' const songs=',1)[0];subprocess.run(['node','-'],input=core+'\nconst tracks='+json.dumps(T)+';if(tracks.filter(hasPlayableSource).length!==562)throw Error("Existing playable catalog changed");',text=True,check=True,capture_output=True)
if not a.source_only:
 D=R/'dist';generated=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(generated)==562
 for id in F['removedIds']:
  for path in [D/'tracks'/f'{id}.html',D/'songs'/f'{id}.md',D/'og'/f'{id}.jpg']:assert not path.exists(),path
 for path in F['removedAssets']:assert not(D/path).exists(),path
 for p in D.rglob('*'):
  if p.is_file()and p.suffix in ['.html','.xml','.md','.json','.js','.txt']:
   text=p.read_text()
   assert not any(id in text for id in F['removedIds']),str(p)
print('Rollback PASS: exact original562 data/art/entities and playable IDs; removed20 absent from public pages/assets/index/sitemap/search; runtime unchanged; historical inverse and10mutation rejection.')
