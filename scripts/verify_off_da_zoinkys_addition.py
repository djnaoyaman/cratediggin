from pathlib import Path
import argparse,json,html,copy,re,hashlib
from PIL import Image
from approved_off_da_zoinkys_addition import F,sha,historical_off_da_zoinkys_addition_file as undo,current_off_da_zoinkys_addition_file as current
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args()
read=lambda path:current(path,(R/path).read_bytes())
t=F['track'];raw=(R/'tracks.json').read_bytes();tracks=json.loads(current('tracks.json',raw));old=json.loads(undo('tracks.json',raw))
assert len(old)==533 and len(tracks)==534 and tracks[:-1]==old and tracks[-1]==t
assert [x['id'] for x in old]==F['beforeIds'] and len({x['id'] for x in tracks})==534
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(undo(path,data))==c['beforeSHA256']
 for bad in [data+b' ',undo(path,data)]:
  try:undo(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved bytes accepted: '+path)
for mutated in [tracks+[t],tracks[:-1],copy.deepcopy(tracks)]:
 if len(mutated)==534:
  if mutated[0]['title']==tracks[0]['title']:mutated[0]['title']+=' changed'
 try:undo('tracks.json',(json.dumps(mutated,ensure_ascii=False,indent=2)+'\n').encode())
 except AssertionError:pass
 else:raise AssertionError('Original533/duplicate/removal mutation accepted')
for target in [('title','Wrong title'),('youtube',dict(t['youtube'],playbackVerified=True))]:
 mutated=copy.deepcopy(tracks);mutated[-1][target[0]]=target[1]
 try:undo('tracks.json',(json.dumps(mutated,ensure_ascii=False,indent=2)+'\n').encode())
 except AssertionError:pass
 else:raise AssertionError('New song changed or false playback claim accepted')
for path,h in F['protectedFiles'].items():assert sha(read(path))==h,path
assert t['id']=='jid-off-da-zoinkys' and t['youtube']['id']=='6QTYQ5Mof3s' and t['youtube']['provider']=='JID'
assert all(t['youtube'][k] is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
assert not any(t['youtube'].get(k) for k in ['playbackCheckedAt','japanAvailableMetadata','embeddableMetadata','playableInEmbed'])
assert t['year']==2018 and t['album']=='DiCaprio 2' and t['producers']==['Christo'] and t['samples']==[] and t['moods']==['ラップ']
assert len(t['essay'])==len(t['essaySources'])==2
assert all(isinstance(i,int) and not isinstance(i,bool) and 0<=i<len(t['sources']) for refs in t['essaySources'] for i in refs)
assert all(0<=i<len(t['sources']) for f in t['facts'] for i in f['sources'])
entities=json.loads(read('artist_entities.json'));before_entities=json.loads(undo('artist_entities.json',(R/'artist_entities.json').read_bytes()))
assert t['artist'] not in before_entities and entities==dict(before_entities,**{t['artist']:{'type':'Person'}})
assert F['artistEntity']=={'name':'JID','record':{'type':'Person'}}
assert not any(x.get('id')==t['id'] for x in json.loads(read('editorial_deepdives.json')))
asset=R/F['asset']['path'];assert sha(read(F['asset']['path']))==F['asset']['sha256']
with Image.open(asset) as im:
 im.load();assert im.mode=='RGBA' and im.size==(F['asset']['width'],F['asset']['height']);alpha=im.getchannel('A');assert alpha.getextrema()==(0,255);w,h=im.size
 assert max(alpha.crop(box).getextrema()[1] for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])<=1
 bbox=alpha.point(lambda v:255 if v>16 else 0).getbbox();assert bbox[0]>0 and bbox[1]>0 and bbox[2]<w and bbox[3]<h
if not a.source_only:
 D=R/'dist';page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
 for v in [t['title'],t['artist'],t['essayTitle'],t['deck'],*t['essay'],*(f['text'] for f in t['facts']),t['editorialStatus'],t['sampleStatus']]:assert v in page,v
 for s in t['sources']:assert s['url'] in page
 for v in [t['essayTitle'],*t['essay']]:assert v in md
 assert F['asset']['path'] in page and t['title']+' — '+t['artist']+'｜CRATE DIGGIN｜DJ Naoyaman' in page
 projected=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(projected)==534;pt=next(x for x in projected if x['id']==t['id'])
 for k,v in t.items():
  if k!='art':assert pt[k]==v,k
 assert pt['art']['image']==F['asset']['path'] and pt['art']['transparent'] is True
 assert f'/tracks/{t["id"]}.html' in (D/'sitemap.xml').read_text()
 readings=html.unescape((D/'readings/index.html').read_text());assert t['title'] in readings and t['essayTitle'] in readings and f'/tracks/{t["id"]}.html' in readings
 assert '## 要調査' not in md
 graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',(D/f'tracks/{t["id"]}.html').read_text(),re.S).group(1))['@graph']
 recording=next(x for x in graph if x.get('@type')=='MusicRecording');assert recording['byArtist']['name']==t['artist'] and recording['byArtist']['@type']=='Person'
 artist_slug=hashlib.sha256(t['artist'].encode()).hexdigest()[:16];artist_page=(D/f'artists/{artist_slug}.html').read_text()
 artist_graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',artist_page,re.S).group(1))['@graph'];collection=next(x for x in artist_graph if x.get('@type')=='CollectionPage')
 assert collection['about']['name']==t['artist'] and collection['about']['@type']=='Person' and collection['mainEntity']['numberOfItems']==1
 assert collection['mainEntity']['itemListElement'][0]['name']==t['title'] and collection['mainEntity']['itemListElement'][0]['url'].endswith('/tracks/'+t['id']+'.html')
print('Exact one-song addition534; original533/UI/notes/security/assets preserved; metadata not playback; alpha/decode/negative guards PASS')
