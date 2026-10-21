"""Exact EDITOR-only polite prose and rendering delta."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-editor-polite.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_editor_polite_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved EDITOR polite drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
