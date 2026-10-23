from pathlib import Path
import json,hashlib
from approved_ga_events import historical_ga_events_file,F
R=Path(__file__).resolve().parents[1]
current=(R/'releases.json').read_bytes()
assert hashlib.sha256(current).hexdigest()==F['afterSHA256']
assert historical_ga_events_file('releases.json',current)==F['beforeText'].encode('utf-8')
assert historical_ga_events_file('unrelated.txt',b'unchanged')==b'unchanged'
assert historical_ga_events_file('releases.json',current+b' ')!=F['beforeText'].encode('utf-8')
before=json.loads(F['beforeText']);after=json.loads(current);assert dict(before,version=after['version'])==after
a,b=map(int,before['version'].split('.'));assert after['version']==f'{a}.{b+1}'
print('GA release delta: exact prior bytes, version-only change, minor increment, unrelated bytes and tamper rejection pass')
