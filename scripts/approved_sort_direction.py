"""Exact sourced Sort direction additions; no catalog or playback exemption."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-sort-direction.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def historical_sort_direction_file(path,data):
 from approved_live_video_year_labels import historical_live_video_year_labels_file
 data=historical_live_video_year_labels_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved Sort direction drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256'];return before
