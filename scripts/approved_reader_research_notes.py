from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-reader-research-notes.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_reader_research_notes_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved reader notice drift: '+path
 before=c['before'].encode() if c['before'] is not None else b''
 if c['beforeSHA256'] is not None:assert sha(before)==c['beforeSHA256']
 return before
