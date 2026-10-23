"""Exact scoped legacy feature card change; existing navigation verifies built output."""
from pathlib import Path
import argparse,json,re,tempfile
from approved_legacy_feature_cards import F,sha,historical_legacy_feature_cards_file as undo,current_legacy_feature_cards_file as current
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');p.parse_args()
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(undo(path,data))==c['beforeSHA256']
 try:undo(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted')
for path,h in F['unchanged'].items():assert sha(current(path,(R/path).read_bytes()))==h
old={};new={};exec(F['files']['url_migration.py']['before'],old);exec(current('url_migration.py',(R/'url_migration.py').read_bytes()),new)
features=json.loads((R/'features.json').read_text())['features'];host='https://example.test/cratediggin';base='/cratediggin'
mapping={base+'/features/':base+'/artists/'}
for f in features:mapping[base+'/features/'+f['id']+'.html']=base+('/artists/' if f['type']=='artist' else '/producers/')+f['id']+'.html'
mapping[base+'/features/tribe-production.html']=base+'/artists/tribe.html'
assert len(mapping)==19
mapping.update({base+'/songs/':base+'/tracks/',base+'/songs/control.html':base+'/tracks/control.html'})
pages={str(i):{'path':v,'title':'A & "B"','description':'説明 <x>','url':host+v[len(base):],'kind':'website','image':host+'/existing.jpg','imageAlt':'既存画像'} for i,v in enumerate(mapping.values())}
pattern=r'<meta (?:property|name)="(?:og|twitter):[^"]+" content="[^"]*">'
with tempfile.TemporaryDirectory() as tmp:
 left=Path(tmp)/'old';right=Path(tmp)/'new'
 old['write_legacy_pages'](left,host,mapping,pages);new['write_legacy_pages'](right,host,mapping,pages)
 for path in mapping:
  rel=path[len(base)+1:]+('index.html' if path.endswith('/') else '')
  a=(left/rel).read_text();b=(right/rel).read_text()
  if path.startswith(base+'/features/'):
   assert not re.findall(pattern,a) and len(re.findall(pattern,b))==16
   assert re.sub(pattern,'',b)==a,'Redirect/body changed'
   assert 'A &amp; &quot;B&quot;' in b and '説明 &lt;x&gt;' in b
  else:assert a==b,'Songs output changed'
 assert (left/'url-migrations.json').read_bytes()==(right/'url-migrations.json').read_bytes()
print('Legacy feature cards: exact19 social-only outputs, unchanged redirects/songs/catalog, escaping and negative drift guards PASS')
