"""Exact image-description metadata delta, never an unrelated-source exemption."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
F=json.loads((ROOT/'scripts/fixtures/approved-image-alt.json').read_text())
def historical_image_alt_file(path,data):
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved image-alt drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
