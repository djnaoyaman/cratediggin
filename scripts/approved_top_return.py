from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-top-return.json').read_bytes();assert sha(raw)=='e0545951e973f97d140e82ad58cea2647ef682dcf3b2548e66c2116c308eacac','Immutable TOP-return fixture drift';F=json.loads(raw)
def current_top_return_file(path,data):return data
def historical_top_return_file(path,data):
 data=current_top_return_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved TOP-return drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
