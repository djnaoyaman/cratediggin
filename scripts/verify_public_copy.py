"""Prevent production instructions from leaking into reader-facing output."""
from pathlib import Path
from html.parser import HTMLParser
class Visible(HTMLParser):
 def __init__(self):super().__init__();self.hidden=0;self.parts=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.hidden+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.hidden=max(0,self.hidden-1)
 def handle_data(self,s):
  if not self.hidden:self.parts.append(s)
r=Path(__file__).resolve().parents[1];d=r/'dist'
for p in d.rglob('*.html'):
 v=Visible();v.feed(p.read_text());s=' '.join(v.parts)
 for phrase in ('アート制作ノート','ユーザー指定','では登録しない','別配信へ置き換えない','明記する。','画像ではSean Paul','制作者クレジットとサンプルの未確認事項は断定しない'):
  assert phrase not in s,(p,phrase)
app=(d/'app.js').read_text()
for phrase in ('アート制作ノート','画像の説明文には','これから追加する作品にも共通の制作ルール','この曲の個別調査記事は未公開です'):
 assert phrase not in app,phrase
assert 'Designed by DJ Naoyaman' in (d/'index.html').read_text()
print('All generated HTML and dynamic templates exclude production-only notes; genuine credits retained')
