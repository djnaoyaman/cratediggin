"""Exact approved browser helpers, shuffle presentation and Editor header changes."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-browser-tools.json').read_text())
def historical_browser_tools_file(path,data):
 from approved_premier_feature import historical_premier_file
 data=historical_premier_file(path,data)
 c=FIXTURE['files'].get(path)
 if not c:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved browser-tools drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before

def historical_browser_tools_social(path,data):
 import base64
 c=FIXTURE.get('changedSocialImages',{}).get(path)
 if not c:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved social image drift: '+path
 before=base64.b64decode(c['beforeBase64']);assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
