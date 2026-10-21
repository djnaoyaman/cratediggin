"""Exact desktop ART-only CSS append and release normalization."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-desktop-art-space.json').read_text())
def historical_desktop_art_space_file(path,data):
 if path=='src/assets/style.css':
  assert hashlib.sha256(data).hexdigest()==F['afterStyleSHA256'],'Unapproved ART layout CSS drift'
  patch=F['patch'].encode();assert data.endswith(patch)
  before=data[:-len(patch)];assert hashlib.sha256(before).hexdigest()==F['beforeStyleSHA256'];return before
 if path!='releases.json':return data
 assert hashlib.sha256(data).hexdigest()==F['afterReleaseSHA256'],'Unapproved ART release drift'
 obj=json.loads(data);obj['version']=F['beforeVersion'];before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert hashlib.sha256(before).hexdigest()==F['beforeReleaseSHA256'];return before
