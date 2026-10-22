from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-audio-source-labels.json').read_bytes()
assert sha(raw)=='6971d5be879c6623ed4fdabc2eec7155a5e1ac84fafbee46a3d6d33abacc6211','Immutable audio label fixture changed'
F=json.loads(raw)
def current_audio_source_labels_file(path,data):
 from approved_clout_addition import historical_clout_addition_file
 return historical_clout_addition_file(path,data)
def historical_audio_source_labels_file(path,data):
 data=current_audio_source_labels_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved audio label change: '+path
 out=c['before'].encode();assert sha(out)==c['beforeSHA256']
 return out
