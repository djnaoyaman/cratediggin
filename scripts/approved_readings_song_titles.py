"""Exact reversible READINGS title presentation delta; content remains immutable."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-readings-song-titles.json').read_bytes()
assert sha(raw)=='a74720e970011f2ccfbfc223eb17ca82c9172c842df24833fd1b6b40153aaf12','READINGS title fixture drift'
F=json.loads(raw)
def historical_readings_song_titles_file(path,data):
 from approved_research_batch57 import historical_research_batch57_file
 data=historical_research_batch57_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved READINGS presentation drift: '+path
 before=c['before'].encode();assert sha(before)==c['beforeSHA256']
 return before
