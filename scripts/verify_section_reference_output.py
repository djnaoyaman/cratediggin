import json,re,sys,hashlib
from pathlib import Path
from html.parser import HTMLParser
from markdown_it import MarkdownIt
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from editorial_references import section_references
base=Path(sys.argv[1]); authored=json.loads((base/'tracks.json').read_text()); by={(t['artist'].casefold(),t['title'].casefold()):t for t in authored}
class Sections(HTMLParser):
 def __init__(self):super().__init__();self.sections=[];self.current=None;self.link=None;self.capture=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='section' and a.get('class')=='editorial-deepdive':self.current={'heading':'','text':'','links':[]};self.sections.append(self.current)
  if self.current is not None:
   if tag=='h2':self.capture='heading'
   elif tag=='p' and not self.current['text']:self.capture='text'
   elif tag=='a':self.link=[a['href'],''];self.current['links'].append(self.link)
 def handle_data(self,data):
  if self.link is not None:self.link[1]+=data
  elif self.current is not None and self.capture:self.current[self.capture]+=data
 def handle_endtag(self,tag):
  if tag=='a':self.link=None
  if tag in ['h2','p']:self.capture=None
  if tag=='section':self.current=None
class Links(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.link=None
 def handle_starttag(self,t,a):
  if t=='a':self.link=[dict(a)['href'],''];self.links.append(self.link)
 def handle_data(self,s):
  if self.link is not None:self.link[1]+=s
 def handle_endtag(self,t):
  if t=='a':self.link=None
count=0; expected=[]
for entry in json.loads((base/'editorial_deepdives.json').read_text()):
 t=by[(entry['artist'].casefold(),entry['title'].casefold())];p=Sections();p.feed((base/'dist/tracks'/f"{t['id']}.html").read_text());assert len(p.sections)==len(entry['sections'])
 md=(base/'dist/tracks'/f"{t['id']}.md").read_text(); lines=[next(x for x in md.split('## '+s['heading']+'\n',1)[1].split('\n## ',1)[0].splitlines() if x.startswith('参考資料: ')) for s in entry['sections']]
 assert len(lines)==len(entry['sections'])
 for s,h,line in zip(entry['sections'],p.sections,lines):
  assert '\n## '+s['heading']+'\n\n'+s['text']+'\n\n参考資料: ' in md,t['id']
  refs=section_references(t,s);pairs=[[r['url'],r['label']] for r in refs]
  assert h['heading']==s['heading'] and h['text']==s['text'],t['id']
  assert h['links']==pairs,(t['id'],h['links'],pairs)
  l=Links();l.feed(MarkdownIt().render(line));assert l.links==pairs,(t['id'],l.links,pairs)
  expected.append({'track':t,'section':s,'references':refs});count+=1
print(f'{count} emitted sections: ordered HTML/Markdown URL+label parity; headings/text unchanged')
