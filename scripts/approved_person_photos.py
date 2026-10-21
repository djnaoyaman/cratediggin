"""Exact render-only portrait header delta; rejects all unreviewed drift."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-person-photos.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_person_photos_file(path,data):
 from approved_editor_affinity import historical_editor_affinity_file
 data=historical_editor_affinity_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved portrait rendering drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
