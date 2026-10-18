"""Strict scope, version, source and lossless art gate for four requested additions."""
import json, hashlib
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
expected={
 'dr-octagon-bear-witness':('Bear Witness','Dr. Octagon',1996,'35g7cZEW9Aw',1),
 'public-enemy-contract-on-the-world-love-jam':('Contract On The World Love Jam','Public Enemy',1990,'se65otxUOz0',3),
 'pete-rock-tha-game':('Tha Game','Pete Rock feat. Raekwon, Prodigy & Ghostface Killah',1998,'--VU4B9DtZM',1),
 'kanye-west-through-the-wire':('Through The Wire','Kanye West',2003,'AE8y25CcE6s',1),
}
t=json.loads((R/'tracks.json').read_text());base=json.loads((R/'scripts/fixtures/renewal-preservation.json').read_text())['records']
assert len(t)>=len(base)+4 and set(expected)<={x['id'] for x in t}-set(base)
by={x['id']:x for x in t}; art={x['id']:x for x in json.loads((R/'graffiti_artwork.json').read_text())['tracks']};d={(x['artist'],x['title']):x['sections'] for x in json.loads((R/'editorial_deepdives.json').read_text())}
f=json.loads((R/'scripts/fixtures/requested-four.json').read_text())
for id,(title,artist,year,video,count) in expected.items():
 x=by[id]; assert (x['title'],x['artist'],x['year'],x['youtube']['id'])==(title,artist,year,video)
 assert x['youtube']['official'] is True and x['youtube']['playbackVerified'] is False and x['youtube']['embeddedPlaybackVerified'] is False
 assert len(x['essay'])==len(x['essaySources']) and all(all(0<=i<len(x['sources']) for i in refs) for refs in x['essaySources'])
 assert len(d[(artist,title)])==count
 for section in d[(artist,title)]:assert section['source'].startswith('https://') and all(0<=i<len(x['sources']) for i in section['sources'])
 assert all('Hits-1998-12-11' not in s['url'] for s in x['sources'])
 a=art[id];assert a['status']=='ready' and a['transparent'] and a['palette']==x['art']['palette']
 p=R/a['image'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['art'][id]['sha256']
 with Image.open(p) as image:
  assert image.width<=2400 and image.mode=='RGBA' and image.getchannel('A').getextrema()==(0,255)
 assert x['deck'] and x['moods']
 if id!='kanye-west-through-the-wire':assert not x['samples'] and '未確認' in x['sampleStatus']
k=by['kanye-west-through-the-wire'];s=k['samples'];assert len(s)==1 and s[0]['main'] and (s[0]['artist'],s[0]['title'],s[0]['youtube']['id'])==('Chaka Khan','Through the Fire','TmtkLP_jcEI')
assert any('Jeremy Tatar' in s['label'] for s in k['sources'])
assert '2014年再発' in '\n'.join(by['public-enemy-contract-on-the-world-love-jam']['essay'])
print('Four requested exact recordings, structured sample, cited sections and alpha-art hashes passed; actual playback not certified')
