from pathlib import Path
import argparse,json,html,copy
from PIL import Image
from approved_lost_in_thought import F,sha,historical_lost_in_thought_file as undo
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args();t=F['track'];raw=(R/'tracks.json').read_bytes();tracks=json.loads(raw);old=json.loads(undo('tracks.json',raw))
assert len(old)==521 and len(tracks)==522 and tracks[:-1]==old and tracks[-1]==t
assert [x['id'] for x in old]==F['beforeIds'] and len({x['id'] for x in tracks})==522
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(undo(path,data))==c['beforeSHA256']
 for bad in [data+b' ',undo(path,data)]:
  try:undo(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved bytes accepted: '+path)
for mutated in [tracks+[t],tracks[:-1],copy.deepcopy(tracks)]:
 if len(mutated)==522:mutated[0]['title']+=' changed'
 try:undo('tracks.json',(json.dumps(mutated,ensure_ascii=False,indent=2)+'\n').encode())
 except AssertionError:pass
 else:raise AssertionError('Original521/duplicate/removal mutation accepted')
for path,h in F['protectedFiles'].items():assert sha((R/path).read_bytes())==h,path
adapter=(R/'scripts/approved_research_batch28.py').read_text();hook=' from approved_lost_in_thought import historical_lost_in_thought_file\n data=historical_lost_in_thought_file(path,data)\n'
assert adapter.count(hook)==1 and sha(adapter.replace(hook,'').encode())==F['beforeAdapterSHA256']
m=json.loads((R/'scripts/ci/manifest.json').read_text());new_ids=['lost-in-thought','lost-in-thought-browser'];assert m['groups'].pop('lost_in_thought')==new_ids
assert [x['id'] for x in m['commands'][-2:]]==new_ids;m['commands']=m['commands'][:-2]
for path in ['scripts/approved_lost_in_thought.py','scripts/fixtures/approved-lost-in-thought.json']:m['policy_paths'].remove(path)
for path in ['scripts/approved_lost_in_thought.py','scripts/verify_lost_in_thought.py','scripts/verify_lost_in_thought_browser.cjs']:del m['script_dependencies'][path]
assert m['script_dependencies']['scripts/approved_research_batch28.py'].pop()=='scripts/approved_lost_in_thought.py'
for path in ['tracks.json','graffiti_artwork.json','artist_entities.json']:
 assert m['scoped_content_changes'][path].pop()['groups']==['lost_in_thought']
 if not m['scoped_content_changes'][path]:del m['scoped_content_changes'][path]
del m['scoped_content_changes'][F['asset']['path']]
assert sha((json.dumps(m,ensure_ascii=False,indent=2)+'\n').encode())==F['beforeCIPolicySHA256'],'Prior CI checks/policies changed'

assert t['youtube']['id']=='e1BgXvNvq2E' and t['youtube']['channel']=='Funkdoobiest - Topic'
assert all(t['youtube'][k] is False for k in ['playbackVerified','embeddedPlaybackVerified','japanPlaybackVerified','exactMasterVerified'])
assert not any(t['youtube'].get(k) for k in ['playbackCheckedAt','japanAvailableMetadata','embeddableMetadata','playableInEmbed'])
assert t['producers']==['DJ Muggs','Ray Roll'] and t['samples']==[] and t['moods']==['ラップ']
assert len(t['essay'])==len(t['essaySources'])==3
assert all(0<=i<len(t['sources']) for refs in t['essaySources'] for i in refs)
assert all(0<=i<len(t['sources']) for f in t['facts'] for i in f['sources'])
asset=R/F['asset']['path'];assert sha(asset.read_bytes())==F['asset']['sha256']
with Image.open(asset) as im:
 im.load();assert im.mode=='RGBA' and im.size==(F['asset']['width'],F['asset']['height']);alpha=im.getchannel('A');assert alpha.getextrema()==(0,255);w,h=im.size
 assert max(alpha.crop(box).getextrema()[1] for box in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)])<=1
 bbox=alpha.point(lambda v:255 if v>1 else 0).getbbox();assert bbox[0]>0 and bbox[1]>0 and bbox[2]<w and bbox[3]<h
if not a.source_only:
 D=R/'dist';page=html.unescape((D/f'tracks/{t["id"]}.html').read_text());md=(D/f'songs/{t["id"]}.md').read_text()
 for v in [t['title'],t['artist'],t['essayTitle'],t['deck'],*t['essay'],*(f['text'] for f in t['facts']),t['editorialStatus'],t['sampleStatus']]:assert v in page,v
 for s in t['sources']:assert s['url'] in page
 for v in [t['essayTitle'],*t['essay']]:assert v in md
 assert F['asset']['path'] in page and t['title']+' — '+t['artist']+'｜CRATE DIGGIN｜DJ Naoyaman' in page
 projected=json.loads((D/'tracks.js').read_text().split('window.TRACKS = ',1)[1].strip().removesuffix(';'));assert len(projected)==522;pt=next(x for x in projected if x['id']==t['id'])
 for k,v in t.items():
  if k!='art':assert pt[k]==v,k
 assert pt['art']['image']==F['asset']['path'] and pt['art']['transparent'] is True
 assert f'/tracks/{t["id"]}.html' in (D/'sitemap.xml').read_text()
print('Exact one-song addition522; original521/assets/content preserved; official metadata not playback; alpha/decode and negative guards PASS')
