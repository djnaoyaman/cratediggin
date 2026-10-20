from pathlib import Path
import hashlib,json
from html.parser import HTMLParser
from approved_premium_notice import F,historical_premium_notice_file
R=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,c in F['files'].items():
 raw=(R/p).read_bytes();assert historical_premium_notice_file(p,raw).decode()==c['before']
 try:historical_premium_notice_file(p,raw+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved drift accepted')
for p,h in F['protected'].items():assert sha((R/p).read_bytes())==h,p
p='templates/index.html';assert (R/p).read_text().replace(F['notice'],'',1)==F['files'][p]['before']
a=json.loads(F['files']['releases.json']['before']);a['version']='22.12';assert json.loads((R/'releases.json').read_text())==a
class NoticeParser(HTMLParser):
 def __init__(self):super().__init__();self.stack=[];self.notes=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if attrs.get('id')=='youtube-premium-note':self.notes.append((tag,attrs,[v.get('id') for _,v in self.stack]))
  if any(v.get('id')=='youtube-premium-note' for _,v in self.stack):
   assert tag not in {'script','iframe','button','input'}
   if tag=='a':self.links.append(attrs)
  if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append((tag,attrs))
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,-1,-1):
   if self.stack[i][0]==tag:self.stack=self.stack[:i];break
for p in ['index.html','tracks/wu-tang-clan-method-man.html','tracks/j-dilla-donuts.html']:
 text=(R/'dist'/p).read_text();parser=NoticeParser();parser.feed(text)
 assert len(parser.notes)==1 and len(parser.links)==1,p
 tag,attrs,parents=parser.notes[0];assert tag=='p' and parents[-1]=='listening-player' and 'role' not in attrs and 'aria-live' not in attrs
 link=parser.links[0];assert link['href']=='https://support.google.com/youtube/answer/7437519?hl=ja' and 'noopener' in link['rel'].split() and link['target']=='_blank'
 assert F['notice'].strip() in text and text.index('id="youtube-link"')<text.index('id="youtube-premium-note"')<text.index('</aside>')
print('Exact static Premium notice, official help, generated placement and unchanged content/player/CSS PASS')
