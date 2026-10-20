"""Exact approved brand changes; unrelated content and image bytes remain protected."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
F=json.loads((ROOT/'scripts/fixtures/approved-brand-identity.json').read_text())
def historical_brand_identity_file(path,data):
 from approved_image_alt import historical_image_alt_file
 data=historical_image_alt_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved brand source drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
def historical_brand_social_digest(path,data):
 digest=hashlib.sha256(data).hexdigest();c=F['socialImages'].get(path)
 if c is None:return digest
 assert digest==c['afterSHA256'],'Unapproved brand social drift: '+path
 return c['beforeSHA256']
