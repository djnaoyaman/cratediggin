from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-gallery-visibility.json').read_bytes();assert sha(raw)=='cca9cece435b20062c516510d7cb32bfa3165fc455b9cd274937536c81172887','Immutable gallery fixture drift';F=json.loads(raw)
def current_gallery_visibility_file(path,data):
 from approved_external_articles import historical_external_articles_file
 return historical_external_articles_file(path,data)
def historical_gallery_visibility_file(path,data):
 data=current_gallery_visibility_file(path,data);c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved gallery visibility drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'];return out
