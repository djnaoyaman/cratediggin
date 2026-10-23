from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-legacy-feature-cards.json').read_bytes()
assert sha(raw)=='09605b3d687046b9b879f0e7366e81e9c8ccc663365e99a2e08a8cf4d198174f','Immutable legacy cards fixture changed'
F=json.loads(raw)
def current_legacy_feature_cards_file(path,data):
 return data
def historical_legacy_feature_cards_file(path,data):
 data=current_legacy_feature_cards_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved legacy card change: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256']
 return out
