from pathlib import Path
import argparse,json,subprocess
from approved_audio_source_labels import F,sha,historical_audio_source_labels_file as undo,current_audio_source_labels_file as current
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(undo(path,data))==c['beforeSHA256']
 try:undo(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted')
assert sha(current('tracks.json',(R/'tracks.json').read_bytes()))==F['tracksSHA256']
expression="(s.youtube.channel||s.youtube.provider||'音源提供元未確認')"
for path in ['src/app/song-ui.js','src/app/player.js']:
 data=current(path,(R/path).read_bytes()).decode();before=F['files'][path]['before']
 assert data==before.replace('s.youtube.channel',expression) and before.count('s.youtube.channel')==1
 if not a.source_only:assert expression in (R/'dist/app.js').read_text()
js="const assert=require('node:assert/strict');const label=s=>"+expression+";assert.equal(label({youtube:{channel:'Existing',provider:'Different'}}),'Existing');assert.equal(label({youtube:{provider:'Verified provider'}}),'Verified provider');assert.equal(label({youtube:{}}),'音源提供元未確認');"
subprocess.run(['node','-e',js],check=True)
print('Audio source labels: exact two consumers, channel precedence/provider/missing branches and unchanged records PASS')
