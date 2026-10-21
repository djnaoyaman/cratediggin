from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-editor-bathing-link.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_editor_bathing_link_file(path,data):
 from approved_research_batch07 import historical_research_batch07_file
 data=historical_research_batch07_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved EDITOR link drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
