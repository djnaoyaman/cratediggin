"""Exact fourteen supplied collage replacements, never a generic asset exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-producer-photos.json').read_text())
def historical_photo_file(path,data):
 from approved_browser_tools import historical_browser_tools_file
 data=historical_browser_tools_file(path,data)
 c=FIXTURE['files'].get(path)
 if not c:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved producer-photo drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
