from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-top-return.json').read_bytes();assert sha(raw)=='263126fd9309a20769ac7eadfbcb30140f4f3a997f1ae009a27e63df0ab60f7d','Immutable TOP-return fixture drift';F=json.loads(raw)
def current_top_return_file(path,data):
 from approved_power_addition import historical_power_addition_file
 return historical_power_addition_file(path,data)
def historical_top_return_file(path,data):
 data=current_top_return_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved TOP-return drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'],'Prior source drift: '+path
 return out
