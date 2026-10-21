from pathlib import Path
import hashlib,json,subprocess
from approved_catalog_scope_repair import F,historical_catalog_scope_repair_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
assert len(json.loads((R/'tracks.json').read_text()))==521
before=F['files']['src/app/catalog-ui.js']['before'];after=(R/'src/app/catalog-ui.js').read_text()
assert before.replace(F['old'],F['new'])==after
for p in F['files']:
 raw=(R/p).read_bytes();historical_catalog_scope_repair_file(p,raw)
 try:historical_catalog_scope_repair_file(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unexpected mutation accepted')
assert historical_catalog_scope_repair_file('other',b'unchanged')==b'unchanged'
subprocess.run(['node','-e',r"const vm=require('vm'),fs=require('fs'),a=require('assert/strict');const s=fs.readFileSync('src/app/catalog-ui.js','utf8');const body=s.match(/function listPage\(\)\{([^]*?)const listBase/)[1];for(const [state,expected] of [[null,false],[undefined,false],[{customMode:false},false],[{customMode:true},true]]){const c={customMode:true,browseRestoring:state};vm.runInNewContext(body,c);a.equal(c.customMode,expected)}"],cwd=R,check=True)
print('One-line route-scoped My Crate reset;521 records, media, artwork, CSS and router preserved; inherited/new/restored state cases PASS')
