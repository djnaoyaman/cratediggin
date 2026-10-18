import json,re
from html.parser import HTMLParser
class RevealParser(HTMLParser):
 def __init__(self):super().__init__();self.buttons=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=="button" and a.get("id")=="player-reveal":self.buttons.append(a)
from pathlib import Path
root=Path('dist');raw=(root/'metadata.js').read_text();pages=json.loads(raw.removeprefix('window.CRATE_PAGES=').removesuffix(';\n'))
count=0
for route,p in pages.items():
 path=p['path'].removeprefix('/cratediggin/');path=path+'index.html' if path.endswith('/') else path
 if not path:path='index.html'
 text=(root/path).read_text();expected='open' if route=='#/' else 'idle'
 assert f'<body data-player-presentation="{expected}">' in text,(route,path)
 assert text.count('id="listening-player"')==1 and text.count('id="player-reveal"')==1
 parser=RevealParser();parser.feed(text);assert len(parser.buttons)==1
 button=parser.buttons[0];assert button['aria-expanded']=='false' and button['aria-controls']=='listening-player'
 assert ('hidden' in button)==(expected=='open')
 assert button['aria-label']=='OPEN PLAYER：操作パネルを開く'
 assert 'OPEN PLAYER</strong>' in text and '操作パネルを開く</span>' in text
 assert text.count('class="reveal-record"')==0 and text.count('class="reveal-action"')==1 and text.count('class="reveal-chevron"')==1
 count+=1
assert count>700
print(f'Static content-first markers and compact reveal controls checked for {count} canonical routes.')
