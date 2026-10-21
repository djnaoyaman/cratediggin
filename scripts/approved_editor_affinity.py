"""One owner-requested preference paragraph, with exact prior prose preservation."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-editor-affinity.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_editor_affinity_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved EDITOR preference drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
