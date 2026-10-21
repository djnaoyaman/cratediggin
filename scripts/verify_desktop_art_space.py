from pathlib import Path
import hashlib,json
from approved_desktop_art_space import F,historical_desktop_art_space_file
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
assert len(json.loads((R/'tracks.json').read_text()))==521
assert F['patch'].count('body[data-art-owner=full][data-art-mode=full]')==2
assert '@media (min-width:1024px) and (min-height:600px)' in F['patch']
assert 'top:96px;height:calc(100% - 296px)' in F['patch']
assert 'top:14px;left:200px;right:auto' in F['patch']
for p in ['src/assets/style.css','releases.json']:
 raw=(R/p).read_bytes();historical_desktop_art_space_file(p,raw)
 try:historical_desktop_art_space_file(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved mutation accepted: '+p)
assert historical_desktop_art_space_file('unrelated',b'unchanged')==b'unchanged'
print('Exact two-rule desktop ART-only CSS, version-only metadata, 521 works and all provider/runtime source preservation PASS. Rendered geometry is a separate required browser check.')
