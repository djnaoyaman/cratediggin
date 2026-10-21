"""Only the release version is normalized; replacement assets checked separately."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-product-live-art.json').read_text())
def historical_product_live_art_file(path,data):
 from approved_desktop_art_space import historical_desktop_art_space_file
 data=historical_desktop_art_space_file(path,data)
 if path!='releases.json':return data
 assert hashlib.sha256(data).hexdigest()==F['afterReleaseSHA256'],'Unapproved art release drift'
 obj=json.loads(data);obj['version']=F['beforeVersion'];before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert hashlib.sha256(before).hexdigest()==F['beforeReleaseSHA256'];return before
