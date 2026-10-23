from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-continuous-scroll.json').read_bytes();assert sha(raw)=='90184f9a98dde7637e8fe116dad49eb8e0b05e421eea875f5f031a1217e37b90','Immutable continuous-scroll fixture drift';F=json.loads(raw)
def current_continuous_scroll_file(path,data):
 from approved_top_return import historical_top_return_file
 return historical_top_return_file(path,data)
def historical_continuous_scroll_file(path,data):
 data=current_continuous_scroll_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved continuous-scroll drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
