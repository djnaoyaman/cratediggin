from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-list-year-restore.json').read_bytes();assert sha(raw)=='c9a21c2586fc84b07d57d5f86b24c1d01bca1d47eb91af9f85dfd11f71140e25','Immutable year-restore fixture drift';F=json.loads(raw)
def current_list_year_restore_file(path,data):
 return data
def historical_list_year_restore_file(path,data):
 data=current_list_year_restore_file(path,data);c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved year display drift: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256'];return out
