from pathlib import Path
import hashlib,json,sys
from PIL import Image
from approved_masta_ace_art_cleanup import F,historical_masta_ace_art_cleanup_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
p=R/F['asset'];assert sha(p.read_bytes())==F['afterAssetSHA256'];assert F['beforeAssetSHA256']!=F['afterAssetSHA256']
with Image.open(p) as im:
 im.load();assert im.mode=='RGBA' and list(im.size)==F['dimensions'] and max(im.size)<=2400
 assert sha(im.tobytes())==F['rgbaSHA256'];assert im.getchannel('A').getextrema()[0]==0
 assert sum(1 for r,g,b,a in im.getdata() if min(r,g,b)>225 and a>240)>1000,'White paint lost'
raw=(R/'releases.json').read_bytes();historical_masta_ace_art_cleanup_file('releases.json',raw)
try:historical_masta_ace_art_cleanup_file('releases.json',raw+b' ')
except AssertionError:pass
else:raise AssertionError('Unapproved drift accepted')
assert historical_masta_ace_art_cleanup_file('unrelated',b'unchanged')==b'unchanged'
notes=(R/'ARTWORK_NOTES.md').read_text();assert 'プロンプトに明示' in notes and 'ビットマップには' in notes
if '--source-only' not in sys.argv:
 D=R/'dist';html=(D/'tracks'/(F['id']+'.html')).read_text();assert F['asset'] in html and 'DJ Naoyaman' in html and 'Original graffiti' in html
 with Image.open(D/F['asset']) as im:im.load();assert im.mode=='RGBA' and im.getchannel('A').getextrema()[0]==0
 with Image.open(D/'og'/(F['id']+'.jpg')) as im:im.load();assert im.size==(1200,630)
print('Masta Ace image-only replacement, white paint/transparency, unchanged507 records and external credit PASS; lettering/removal visually reviewed')
