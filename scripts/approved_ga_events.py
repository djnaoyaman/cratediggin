"""Normalize only the exact reviewed GA-event release-version delta."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
raw=(R/'scripts/fixtures/approved-ga-events.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=="a1af373fa35d521a2f8f50cb4f844f3edcb4944903e099d13eae999d740f4a14", 'Immutable GA fixture drift'
F=json.loads(raw)
def historical_ga_events_file(path,data):
 if path!='releases.json' or hashlib.sha256(data).hexdigest()!=F['afterSHA256']:return data
 before=F['beforeText'].encode('utf-8')
 assert hashlib.sha256(before).hexdigest()==F['beforeSHA256']
 return before
