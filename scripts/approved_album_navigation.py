"""Exact album navigation correction; unrelated bytes are never exempted."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_album_navigation_file(path,data):
 f=json.loads((ROOT/'scripts/fixtures/approved-album-navigation.json').read_text())
 c=f['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved album navigation drift: '+path
 before=c['before'].encode()
 assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
 return before
