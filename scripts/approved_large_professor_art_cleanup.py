"""Only the release version is normalized; approved image is checked separately."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-large-professor-art-cleanup.json').read_text())
def historical_large_professor_art_cleanup_file(path,data):
 if path!='releases.json':return data
 assert hashlib.sha256(data).hexdigest()==F['afterReleaseSHA256'],'Unapproved artwork-release drift'
 obj=json.loads(data);obj['version']=F['beforeVersion'];before=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert hashlib.sha256(before).hexdigest()==F['beforeReleaseSHA256'];return before
