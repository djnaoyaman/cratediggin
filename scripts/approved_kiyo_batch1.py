from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-kiyo-batch1.json').read_bytes();assert sha(raw)=='419008b8731764e294f6a5ed1b1acd77af101bef5f4d0fd883e1489caab1586f','Immutable batch fixture drift';F=json.loads(raw)
def current_kiyo_batch1_file(path,data):
 from approved_list_year_restore import historical_list_year_restore_file
 return historical_list_year_restore_file(path,data)
def historical_kiyo_batch1_file(path,data):
 data=current_kiyo_batch1_file(path,data);c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved six-song batch drift: '+path
 if 'before'in c:out=c['before'].encode()
 else:
  o=json.loads(data)
  if path=='tracks.json':assert len(o)==F['afterCount']and o[-6:]==F['tracks']and[x['id']for x in o[:-6]]==F['beforeIds'];o=o[:-6]
  elif path=='graffiti_artwork.json':assert o['tracks'][-6:]==F['artworks'];o['tracks']=o['tracks'][:-6]
  elif path=='artist_entities.json':
   for k,v in F['entities'].items():assert o.pop(k)==v
  elif path=='releases.json':assert o['version']==F['afterVersion'];o['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse')
  out=(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Prior538 changed: '+path
 return out
