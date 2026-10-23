from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-continuous-scroll.json').read_bytes();assert sha(raw)=='79b8108c3bd097537fbebf4627eb71646a073e92b38798e1f332c5d0c3648348','Immutable continuous-scroll fixture drift';F=json.loads(raw)
def current_continuous_scroll_file(path,data):return data
def historical_continuous_scroll_file(path,data):
 data=current_continuous_scroll_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved continuous-scroll drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
