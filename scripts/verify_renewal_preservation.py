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
def protected_bytes(path, append=None):
    data=path.read_bytes()
    if append is None:return data
    parsed=json.loads(data)
    if append.get('objectPrefix'):
        assert isinstance(parsed,dict) and len(parsed)>=append['count'], 'Protected object entries removed: '+str(path)
        return (json.dumps(dict(list(parsed.items())[:append['count']]),ensure_ascii=False,indent=2)+'\n').encode()
    key=append['arrayKey']; entries=parsed if key is None else parsed[key]
    assert len(entries)>=append['count'], 'Protected entries removed: '+str(path)
    if key is None:parsed=entries[:append['count']]
    else:parsed[key]=entries[:append['count']]
    return (json.dumps(parsed,ensure_ascii=False,indent=2)+'\n').encode()
for key,value in {**f['protectedFiles'],**f['assets']}.items():
    assert hashlib.sha256(protected_bytes(root/key,f.get('appendOnlyFiles',{}).get(key))).hexdigest()==value, 'Protected source/art changed: '+key
print(f"Preserved {len(f['records'])} published works, {len(f['assets'])} original assets and protected editorial sources")
