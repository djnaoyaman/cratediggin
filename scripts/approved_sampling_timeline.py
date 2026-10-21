"""Exact sourced Timeline additions; no catalog or playback exemption."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-sampling-timeline.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_sampling_timeline_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Timeline drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
