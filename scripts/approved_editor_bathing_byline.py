from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-editor-bathing-byline.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_editor_bathing_byline_file(path,data):
 from approved_research_batch08 import historical_research_batch08_file
 data=historical_research_batch08_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved EDITOR byline drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
