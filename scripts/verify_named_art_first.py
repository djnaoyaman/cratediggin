from pathlib import Path
import json,hashlib,sys
from PIL import Image
from approved_named_art_first import F,historical_named_art_first_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
assert len(json.loads((R/'tracks.json').read_text()))==521
for a in F['assets']:
 p=R/a['path'];assert sha(p.read_bytes())==a['afterSHA256'] and a['afterSHA256']!=a['beforeSHA256']
 with Image.open(p) as im:
  im.load();assert im.mode=='RGBA' and list(im.size)==a['dimensions'] and max(im.size)<=2400
  assert sha(im.tobytes())==a['rgbaSHA256'];assert im.getchannel('A').getextrema()[0]==0
  assert any(min(r,g,b)>225 and alpha>240 for r,g,b,alpha in im.getdata()),'White paint lost'
 if '--source-only' not in sys.argv:
  D=R/'dist';html=(D/'tracks'/(a['id']+'.html')).read_text();assert a['path'] in html and 'Original graffiti' in html and 'DJ Naoyaman' in html
  with Image.open(D/a['path']) as im:assert im.mode=='RGBA' and im.size==tuple(a['dimensions'])
  with Image.open(D/'og'/(a['id']+'.jpg')) as im:assert im.size==(1200,630)
raw=(R/'releases.json').read_bytes();historical_named_art_first_file('releases.json',raw)
try:historical_named_art_first_file('releases.json',raw+b' ')
except AssertionError:pass
else:raise AssertionError('Unapproved release mutation accepted')
assert historical_named_art_first_file('unrelated',b'unchanged')==b'unchanged'
print('Two image-only replacements; unchanged 521 records/runtime; exact RGBA, white paint, transparency, external credit and OGP PASS. Lettering/style visually reviewed separately.')
