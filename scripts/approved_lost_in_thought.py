from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'scripts/fixtures/approved-lost-in-thought.json').read_bytes()
assert sha(raw)=='077c1f1b2e090baa02491cb83f5236924186f8a9d80d2ca772163d2aec344718','Immutable addition fixture changed'
F=json.loads(raw)
def historical_lost_in_thought_file(path,data):
 from approved_research_batch29 import historical_research_batch29_file
 data=historical_research_batch29_file(path,data)
 c=F['files'].get(path)
 if c is None:return data
 assert sha(data)==c['afterSHA256'],'Unapproved addition drift: '+path
 obj=json.loads(data)
 if path=='tracks.json':
  assert len(obj)==522 and [x['id'] for x in obj[:-1]]==F['beforeIds'] and obj[-1]==F['track'];obj.pop()
 elif path=='graffiti_artwork.json':assert obj['tracks'][-1]==F['artwork'];obj['tracks'].pop()
 elif path=='artist_entities.json':assert obj.pop('Funkdoobiest')==F['newArtistEntity']['Funkdoobiest']
 else:assert obj['version']==F['afterVersion'];obj['version']=F['beforeVersion']
 out=(json.dumps(obj,ensure_ascii=False,indent=2)+'\n').encode()
 assert sha(out)==c['beforeSHA256'],'Original521 changed: '+path
 return out
