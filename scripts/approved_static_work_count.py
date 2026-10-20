"""Exact static-count projection delta, never a broad frontend exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_static_work_count_file(path,data):
 from approved_album_navigation import historical_album_navigation_file
 data=historical_album_navigation_file(path,data)
 f=json.loads((ROOT/'scripts/fixtures/approved-static-work-count.json').read_text())
 c=f['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved static-count drift: '+path
 before=c['before'].encode()
 assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
 return before
