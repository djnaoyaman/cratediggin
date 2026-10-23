from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-kiyo-batch3.json').read_bytes();assert sha(raw)=='9b3e50a1a396dfa4a8db0a330badf9eb282afd25a1954c132644f85d937eead8','Immutable batch fixture drift';F=json.loads(raw)
def current_kiyo_batch3_file(path,data):
 return data
def historical_kiyo_batch3_file(path,data):
 data=current_kiyo_batch3_file(path,data);c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved nine-song batch drift: '+path
 if 'before'in c:out=c['before'].encode()
 else:
  o=json.loads(data)
  if path=='tracks.json':assert len(o)==F['afterCount']and o[-9:]==F['tracks']and[x['id']for x in o[:-9]]==F['beforeIds'];o=o[:-9]
  elif path=='graffiti_artwork.json':assert o['tracks'][-9:]==F['artworks'];o['tracks']=o['tracks'][:-9]
  elif path=='artist_entities.json':
   for k,v in F['entities'].items():assert o.pop(k)==v
  elif path=='releases.json':assert o['version']==F['afterVersion'];o['version']=F['beforeVersion']
  else:raise AssertionError('Unknown inverse')
  out=(json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Prior553 changed: '+path
 return out
