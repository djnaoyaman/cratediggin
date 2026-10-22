from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-simple-content-ci.json').read_text())
sha=lambda b:hashlib.sha256(b).hexdigest()
def current_simple_content_ci_file(path,data):
 from approved_shame_addition import historical_shame_addition_file
 return historical_shame_addition_file(path,data)
def historical_simple_content_ci_file(path,data):
 data=current_simple_content_ci_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved simple-content CI drift: '+path
 before=c['before'].encode()
 assert sha(before)==c['beforeSHA256'],path
 return before
