"""Only the release version is normalized; replacement assets checked separately."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-remaining-size.json').read_text())
def historical_remaining_size_file(path,data):
 if path!='releases.json':return data
 assert hashlib.sha256(data).hexdigest()==F['afterReleaseSHA256'],'Unapproved art release drift'
 obj=json.loads(data);obj['version']=F['beforeVersion'];before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert hashlib.sha256(before).hexdigest()==F['beforeReleaseSHA256'];return before
