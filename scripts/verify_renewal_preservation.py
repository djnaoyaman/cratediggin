"""Protect published content while permitting future, separately reviewed additions."""
from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parents[1]
f=json.loads((root/'scripts/fixtures/renewal-preservation.json').read_text())
def digest(v):return hashlib.sha256(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
t=json.loads((root/'tracks.json').read_text()); ids=[x['id'] for x in t]
assert len(ids)==len(set(ids))
records={x['id']:x for x in t}
assert set(f['records'])<=set(records), 'Published works removed'
for key,value in f['records'].items():assert digest(records[key])==value, 'Protected work changed: '+key
for key,value in {**f['protectedFiles'],**f['assets']}.items():assert hashlib.sha256((root/key).read_bytes()).hexdigest()==value, 'Protected source/art changed: '+key
print(f"Preserved {len(f['records'])} published works, {len(f['assets'])} original assets and protected editorial sources")
