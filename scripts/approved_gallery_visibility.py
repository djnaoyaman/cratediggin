from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-gallery-visibility.json').read_bytes();assert sha(raw)=='2960f153f51f1eb2cf8e05d5fcc98914c4e8e41489d529c9bb91ca27db8ab83d','Immutable gallery fixture drift';F=json.loads(raw)
def current_gallery_visibility_file(path,data):
 return data
def historical_gallery_visibility_file(path,data):
 data=current_gallery_visibility_file(path,data);c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved gallery visibility drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'];return out
