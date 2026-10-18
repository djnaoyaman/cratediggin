import json
from pathlib import Path
from PIL import Image
r=Path('.');tracks=json.loads((r/'tracks.json').read_text());t=next(x for x in tracks if x['id']=='common-celebrate')
assert t['youtube']['id']=='58uykVXeGPA' and t['youtube']['channel']=='Common - Topic'
assert 'JP' in t['youtube']['regionsAllowed'].split(',') and t['youtube']['playbackVerified'] is False
assert t['year']==2011 and t['producer']=='No I.D.' and len(t['essay'])==3
assert 'explicitLyrics' not in t['youtube'] and 'officialArtistChannelId' not in t['youtube']
assert len(t['essaySources'])==3 and all(all(type(i) is int and 0<=i<len(t['sources']) for i in xs) for xs in t['essaySources'])
note='仲間の結婚式が元町の山手十番館であり、その記念に選んだCommonの「Celebrate」。'
assert t['editorSelectionMemory']=={'heading':'選曲メモ','text':note}
assert {'common-celebrate','kid-cudi-make-her-say'} <= {x['id'] for x in tracks if x.get('editorSelectionMemory')}, 'Preserve both wedding selection memories; other authorized memories may coexist'
html=(r/'dist/tracks/common-celebrate.html').read_text();md=(r/'dist/tracks/common-celebrate.md').read_text()
assert '<aside class="editor-selection-memory"><h2>選曲メモ</h2><p>'+note+'</p></aside>' in html
assert '## 選曲メモ\n\n'+note in md
assert 'Celebrate — Common｜CRATE DIGGIN｜DJ Naoyaman' in html
assert Image.open(r/'assets/graffiti/common-celebrate-alpha.webp').getchannel('A').getextrema()==(0,255)
assert len([x for x in json.loads((r/'editorial_deepdives.json').read_text()) if x['artist']=='Common' and x['title']=='Celebrate'][0]['sections'])==2
print('Celebrate original recording, source indices, owner memory, alpha, HTML/Markdown and truthful playback limits verified')

profile=(r/'dist/editor.html').read_text()
assert '株式会社サイバーエージェント：インターネット広告代理事業部でマネジメントとコンサルティングに携わり、インターネット広告のルールづくりに取り組む。' in profile
