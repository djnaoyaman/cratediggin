import json
from pathlib import Path
from PIL import Image
r=Path('.');ts=json.loads((r/'tracks.json').read_text());t=next(t for t in ts if t['id']=='kid-cudi-make-her-say')
assert t['youtube']['id']=='Xt22KvnRSL4' and t['youtube']['duration']=='PT3M18S'
assert t['youtube']['playbackVerified'] is False and t['youtube']['embeddedPlaybackVerified'] is False
assert 'Clean Version' in t['youtube']['type'] and t['youtube']['japanRegionStatus']=='included'
assert len(t['essay'])==3 and len(t['essaySources'])==3
assert all(all(type(i)is int and 0<=i<len(t['sources']) for i in xs) for xs in t['essaySources'])
for x in t['facts']+t['samples']:
 assert all(type(i)is int and 0<=i<len(t['sources']) for i in x['sources'])
assert len(t['samples'])==1 and not t['samples'][0].get('youtube')
assert t['producer']=='Kanye West' and t['scratchCredits']=='A-Trak'
note='仲間の結婚式が元町の山手十番館であり、その記念にCommonの「Celebrate」とともに選んだ一曲。'
assert t['editorSelectionMemory']=={'heading':'選曲メモ','text':note}
h=(r/'dist/tracks/kid-cudi-make-her-say.html').read_text();m=(r/'dist/tracks/kid-cudi-make-her-say.md').read_text()
assert '<aside class="editor-selection-memory"><h2>選曲メモ</h2><p>'+note+'</p></aside>' in h
assert '## 選曲メモ\n\n'+note in m
assert 'Make Her Say — Kid Cudi feat. Kanye West &amp; Common｜CRATE DIGGIN｜DJ Naoyaman' in h
im=Image.open(r/'assets/graffiti/kid-cudi-make-her-say-alpha.webp');lo,hi=im.getchannel('A').getextrema();assert lo==0 and hi>=250
assert Image.open(r/'dist/og/kid-cudi-make-her-say.png').size==(1200,630)
assert len([d for d in json.loads((r/'editorial_deepdives.json').read_text()) if d['artist']==t['artist'] and d['title']==t['title']][0]['sections'])==2
print('Make Her Say approved clean MV, source mappings, wedding note, transparent art and OGP verified; actual playback not claimed')
