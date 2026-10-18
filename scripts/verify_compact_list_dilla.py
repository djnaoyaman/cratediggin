from pathlib import Path
import json,hashlib,copy
from PIL import Image
R=Path(__file__).resolve().parents[1];f=json.loads((R/'scripts/fixtures/compact-list-dilla.json').read_text())
for name,h in f['protected'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==h,name
current=json.loads((R/'features.json').read_text());before=f['featuresBefore'];normalized=copy.deepcopy(current)
old=next(x for x in before['features'] if x['id']=='j-dilla');new=next(x for x in normalized['features'] if x['id']=='j-dilla');visual=new['visual'];new['visual']=old['visual'];assert normalized==before,'Only J Dilla visual may change'
assert visual['tag']==old['visual']['tag'] and visual['fit']=='contain' and visual['provenance']=='user-provided' and visual['credit']=='ユーザー提供'
assert not any(k in visual for k in ['author','license','licenseUrl','source'])
p=R/'src/assets'/visual['photo'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['photoSHA256']
with Image.open(p) as im:assert im.size==(512,512)
assert len(json.loads((R/'tracks.json').read_text()))==499
print('499 records and all editorial sources unchanged; only authorized J Dilla visual changed; original512px JPEG hash preserved; no invented license')
