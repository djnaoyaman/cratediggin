"""Normalize only the exact audited media correction for immutable historical guards."""
from pathlib import Path
import json, hashlib, copy
from approved_editorial_corrections import historical_editorial_record
ROOT=Path(__file__).resolve().parents[1]
FIXTURE=json.loads((ROOT/'scripts/fixtures/approved-media-correction.json').read_text())
def digest(value):
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def historical_record(record):
    record=historical_editorial_record(record)
    for correction in FIXTURE['corrections']:
        if record['id']==correction['id']:
            assert digest(correction['before'])==correction['beforeSHA256']
            assert digest(correction['after'])==correction['afterSHA256']
            changed={k for k in set(correction['before'])|set(correction['after']) if correction['before'].get(k)!=correction['after'].get(k)}
            assert changed==set(correction['allowedFields'])=={'youtube','editorialStatus'}
            assert digest(record)==correction['afterSHA256'], 'Unapproved corrected-record drift: '+record['id']
            return copy.deepcopy(correction['before'])
    return record
def historical_tracks_bytes(data):
    records=json.loads(data)
    return (json.dumps([historical_record(x) for x in records],ensure_ascii=False,indent=2)+'\n').encode()
