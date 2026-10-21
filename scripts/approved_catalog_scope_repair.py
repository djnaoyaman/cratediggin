from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
F=json.loads((R/'scripts/fixtures/approved-catalog-scope-repair.json').read_text())
def historical_catalog_scope_repair_file(path,data):
 from approved_headings_batch01 import historical_headings_batch01_file
 data=historical_headings_batch01_file(path,data)
 if path not in F['files']:return data
 c=F['files'][path];assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved catalog route repair drift: '+path
 before=c['before'].encode();assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'];return before
