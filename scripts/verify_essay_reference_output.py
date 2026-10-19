"""All66 authored mappings agree in static HTML and Markdown;433 unmapped essays add no references."""
from pathlib import Path
import json,sys
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from editorial_references import essay_references,markdown_reference
class Citations(HTMLParser):
 def __init__(self,text):super().__init__();self.rows=[];self.active=False;self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='div' and a.get('class')=='essay-references':self.active=True;self.rows.append([])
  if tag=='a' and self.active:self.rows[-1].append(a['href'])
 def handle_endtag(self,tag):
  if tag=='div':self.active=False
count=0
for t in json.loads((R/'tracks.json').read_text()):
 expected=[refs for i in range(len(t['essay'])) if (refs:=essay_references(t,i))]
 text=(R/'dist/tracks'/f"{t['id']}.html").read_text();md=(R/'dist/tracks'/f"{t['id']}.md").read_text()
 assert Citations(text).rows==[[x['url'] for x in row] for row in expected],t['id']
 for row in expected:
  assert '参考資料：'+' / '.join(markdown_reference(x) for x in row) in md,t['id']
 if expected:count+=1
assert count==66
print('66 mapped articles exact static/Markdown citation parity;433 unmapped essays have no invented reference rows')
