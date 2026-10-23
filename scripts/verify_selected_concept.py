from pathlib import Path
import argparse,json,hashlib,html,subprocess
from PIL import Image
from approved_selected_concept import F,current_selected_concept_file,historical_selected_concept_file
R=Path(__file__).resolve().parents[1];sha=lambda b:hashlib.sha256(b).hexdigest();read=lambda p:current_selected_concept_file(p,(R/p).read_bytes())
p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
for path,h in F['protected'].items():
 if path=='audit-reports/maintenance.json':assert sha(read(path))==F['generatedAuditSHA256'];continue
 assert sha(read(path))==h,path
assert sha(read(F['previousHelper']['path']))==F['previousHelper']['afterSHA256']
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(current_selected_concept_file(path,raw))==c['afterSHA256'];assert sha(historical_selected_concept_file(path,raw))==c['beforeSHA256']
 for mutated in [raw+b' ',raw[:-1]]:
  try:historical_selected_concept_file(path,mutated)
  except AssertionError:pass
  else:raise AssertionError('Unapproved mutation accepted: '+path)
T=json.loads(read('tracks.json'));old=json.loads(historical_selected_concept_file('tracks.json',(R/'tracks.json').read_bytes()));N=len(F['tracks'])
assert 1<=N<=3 and len(T)==F['afterCount']==F['beforeCount']+N and len(old)==F['beforeCount']==563;assert T[:-N]==old and T[-N:]==F['tracks']and len({t['id']for t in T})==len(T)
A=json.loads(read('graffiti_artwork.json'));prior=json.loads(historical_selected_concept_file('graffiti_artwork.json',(R/'graffiti_artwork.json').read_bytes()));assert A['tracks'][:-N]==prior['tracks']and A['tracks'][-N:]==F['artworks'];assert all(A[k]==v for k,v in prior.items()if k!='tracks')
expected={'anderson-paak-the-season-carry-me':'p7GH9JJlDL8','robert-glasper-afro-blue-9th-wonder-remix':'0HbagZwKBro','2-chainz-threat-2-society':'jeVivltkmV4'}
for t,art in zip(F['tracks'],F['artworks'],strict=True):
 y=t['youtube'];assert y['id']==expected[t['id']]and y['url']=='https://www.youtube.com/watch?v='+y['id']and not t.get('externalAudio')
 assert all(y.get(k)is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified']);assert not any(y.get(k)for k in ['verified','playbackCheckedAt','japanAvailableMetadata','embeddableMetadata','playableInEmbed'])
 assert t['editorialStatus']=='再生状況・埋め込み可否は確認中。'and t['editorSelectionMemory']['text']==t['editorialStatus']
 assert t['artists']==list(dict.fromkeys(t['primaryArtists']+t['featuredArtists']));assert len(t['essaySources'])==len(t['essay'])and all(0<=i<len(t['sources'])for row in t['essaySources']for i in row)
 if t['id']=='anderson-paak-the-season-carry-me':assert t['year']==2015 and t['album']=='Malibu'and '2016'in t['yearBasis']and y['channel']=='EMPIRE'
 if t['id']=='robert-glasper-afro-blue-9th-wonder-remix':assert t['producer']=='Robert Glasper'and t['remixer']=='9th Wonder'and '9th Wonder'not in t['producers']
 assert art['id']==t['id']and art['noSiteBranding']is True and art['transparent']is True
for asset in F['assets']:
 assert sha(read(asset['path']))==asset['sha256']
 with Image.open(R/asset['path'])as im:
  im.load();assert im.mode=='RGBA';al=im.getchannel('A');assert al.getextrema()[0]==0 and al.getextrema()[1]>=250;w,h=im.size;assert w>=600 and h>=400;assert max(al.crop(z).getextrema()[1]for z in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])<=8
core=read('src/app/core.js').decode().split(' const songs=',1)[0];subprocess.run(['node','-'],input=core+'\nconst tracks='+json.dumps(T)+';if(tracks.filter(hasPlayableSource).length!=='+str(len(T))+')throw Error("Playable IDs mismatch");',text=True,check=True,capture_output=True)
if not a.source_only:
 D=R/'dist';actual=json.loads((R/'tracks.json').read_text());generated=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert [t['id']for t in generated]==[t['id']for t in actual]
 for t in F['tracks']:
  g=next(x for x in generated if x['id']==t['id']);assert g['youtube']==t['youtube'];page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
  for v in [t['title'],t['artist'],t['essayTitle'],*t['essay'],t['youtube']['url'],t['editorSelectionMemory']['text']]:assert v in page and v in md,v
print('Selected concept additions PASS: exact prior563 and selected1–3 only; compact hash-bound reversible deltas; art alpha/hash; no fabricated verification; actual generated IDs match authored catalog.')
