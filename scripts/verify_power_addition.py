from pathlib import Path
import argparse,json,hashlib,html,subprocess
from PIL import Image
from approved_power_addition import F,current_power_addition_file,historical_power_addition_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
def current(path):return current_power_addition_file(path,(R/path).read_bytes())
for path,h in F['protected'].items():
 if path=='audit-reports/maintenance.json':assert sha(current(path))==F['generatedAuditSHA256'];continue
 assert sha(current(path))==h,path
assert sha(current(F['previousHelper']['path']))==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(current_power_addition_file(path,data))==c['afterSHA256'];assert sha(historical_power_addition_file(path,data))==c['beforeSHA256']
 for changed in [data+b' ',data[:-1]]:
  try:historical_power_addition_file(path,changed)
  except AssertionError:pass
  else:raise AssertionError('Mutation accepted: '+path)
T=json.loads(current('tracks.json'));old=json.loads(F['files']['tracks.json']['before']);t=F['track'];assert len(T)==563 and len(old)==562 and T[:562]==old and T[-1]==t and len({x['id']for x in T})==563
assert not set(F['withdrawnIdsExceptPower'])&{x['id']for x in T}
assert t['id']=='rapsody-power'and t['youtube']['id']=='sVsehWDsoR0'and t['youtube']['url']=='https://www.youtube.com/watch?v=sVsehWDsoR0'and not t.get('externalAudio')
y=t['youtube'];assert all(y.get(k)is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
assert not any(y.get(k)for k in ['playbackCheckedAt','japanAvailableMetadata','embeddableMetadata','playableInEmbed']);assert not y.get('verified')
assert len(t['essaySources'])==len(t['essay'])and all(0<=i<len(t['sources'])for row in t['essaySources']for i in row)
art=json.loads(current('graffiti_artwork.json'));prior=json.loads(F['files']['graffiti_artwork.json']['before']);assert art['tracks'][:-1]==prior['tracks']and art['tracks'][-1]==F['artwork'];assert all(art[k]==v for k,v in prior.items()if k!='tracks')
for asset in F['assets']:
 assert sha((R/asset['path']).read_bytes())==asset['sha256']
 with Image.open(R/asset['path'])as im:
  im.load();assert im.mode=='RGBA';al=im.getchannel('A');assert al.getextrema()[0]==0 and al.getextrema()[1]>=250;w,h=im.size;assert w>=600 and h>=400;assert max(al.crop(z).getextrema()[1]for z in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])<=8
assert F['artwork']['noSiteBranding']is True and F['artwork']['transparent']is True
core=(R/'src/app/core.js').read_text().split(' const songs=',1)[0];subprocess.run(['node','-'],input=core+'\nconst tracks='+json.dumps(T)+';if(tracks.filter(hasPlayableSource).length!==563)throw Error("Playable IDs mismatch");',text=True,check=True,capture_output=True)
if not a.source_only:
 D=R/'dist';generated=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert [x['id']for x in generated]==[x['id']for x in json.loads((R/'tracks.json').read_text())]
 g=next(x for x in generated if x['id']==t['id']);assert g['youtube']==y
 page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
 for v in [t['title'],t['artist'],t['essayTitle'],*t['essay'],y['url']]:assert v in page and v in md,v
 for id in F['withdrawnIdsExceptPower']:
  if id not in {x['id']for x in json.loads((R/'tracks.json').read_text())}:assert not(D/'tracks'/f'{id}.html').exists()
print('Single Power PASS: prior562 unchanged, exact user-suppliedID, verification flags remain false,19withdrawn absent, art alpha/hash, historical inverse/mutations, no runtime changes.')
