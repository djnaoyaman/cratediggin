from approved_requested_two import historical_intake_tracks, historical_intake_file
from pathlib import Path
import json,hashlib,copy
from PIL import Image
from approved_media_correction import historical_tracks_bytes
from approved_editorial_corrections import historical_editorial_file
R=Path(__file__).resolve().parents[1];f=json.loads((R/'scripts/fixtures/compact-list-dilla.json').read_text())
for name,h in f['protected'].items():
 data=historical_editorial_file(name,(R/name).read_bytes())
 if name=='tracks.json':data=historical_tracks_bytes(data)
 assert hashlib.sha256(data).hexdigest()==h,name
current=json.loads(historical_editorial_file('features.json',(R/'features.json').read_bytes()));before=f['featuresBefore'];normalized=copy.deepcopy(current)
old=next(x for x in before['features'] if x['id']=='j-dilla');new=next(x for x in normalized['features'] if x['id']=='j-dilla');visual=new['visual'];new['visual']=old['visual'];assert normalized==before,'Only J Dilla visual may change'
assert visual['tag']==old['visual']['tag'] and visual['fit']=='contain' and visual['provenance']=='user-provided' and visual['credit']=='ユーザー提供'
assert not any(k in visual for k in ['author','license','licenseUrl','source'])
p=R/'src/assets'/visual['photo'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['photoSHA256']
with Image.open(p) as im:assert im.size==(512,512)
assert len(historical_intake_tracks())==499
print('499 records and all editorial sources unchanged; only authorized J Dilla visual changed; original512px JPEG hash preserved; no invented license')
