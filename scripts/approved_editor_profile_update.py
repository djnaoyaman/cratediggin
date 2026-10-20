"""Exact owner-supplied profile text update, preserving all other content."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-editor-profile-update.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_editor_profile_file(path,data):
 from approved_person_queue import historical_person_queue_file
 data=historical_person_queue_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved profile drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
