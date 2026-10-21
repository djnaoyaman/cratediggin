"""Exact contextual video-year labels; no media verification exemption."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-live-video-year-labels.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_live_video_year_labels_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved video-year drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
