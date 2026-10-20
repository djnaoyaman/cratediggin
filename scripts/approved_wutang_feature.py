"""Exact append of one requested artist feature; no work, media or existing feature exemption."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-wutang-feature.json').read_text())
def historical_wutang_feature_file(path,data):
 from approved_triumph import historical_triumph_file
 data=historical_triumph_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved Wu-Tang feature drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256']
 return before
