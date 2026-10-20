"""Only the generated static count and its direct rendering contract."""
from pathlib import Path
import json,sys
from html.parser import HTMLParser
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from frontend import render_work_count
class Count(HTMLParser):
 def __init__(self):super().__init__();self.active=False;self.values=[]
 def handle_starttag(self,tag,attrs):
  if dict(attrs).get('id')=='hero-count':self.active=True;self.values.append('')
 def handle_endtag(self,tag):
  if tag=='b':self.active=False
 def handle_data(self,data):
  if self.active:self.values[-1]+=data
source=(R/'templates/index.html').read_text();tracks=json.loads((R/'tracks.json').read_text())
for size in (0,1,9,10,501,502):
 result=render_work_count(source,[{}]*size);parser=Count();parser.feed(result)
 assert parser.values==[str(size).zfill(2)],(size,parser.values)
 assert result.replace(str(size).zfill(2)+'</b>','{{WORK_COUNT}}</b>',1)==source
for invalid in (source.replace('{{WORK_COUNT}}',''),source+'{{WORK_COUNT}}'):
 try:render_work_count(invalid,tracks)
 except ValueError:pass
 else:raise AssertionError('Invalid token cardinality accepted')
try:render_work_count(source,{})
except ValueError:pass
else:raise AssertionError('Invalid catalog shape accepted')
parser=Count();parser.feed((R/'dist/index.html').read_text());assert parser.values==[str(len(tracks)).zfill(2)],parser.values
assert "$('#hero-count').textContent=String(songs.length).padStart(2,'0')" in (R/'src/app/router.js').read_text()
print(f'Static/no-JS hero count is catalog-derived ({len(tracks)}); changing/empty catalogs and strict token contract PASS')

from approved_static_work_count import historical_static_work_count_file
import hashlib
fixture=json.loads((R/'scripts/fixtures/approved-static-work-count.json').read_text())
assert set(fixture['files'])=={'frontend.py','templates/index.html','releases.json'}
for path,c in fixture['files'].items():
 data=(R/path).read_bytes()
 assert hashlib.sha256(historical_static_work_count_file(path,data)).hexdigest()==c['beforeSHA256']
 try:historical_static_work_count_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unexpected static-count drift accepted: '+path)
assert historical_static_work_count_file('unrelated.txt',b'unchanged')==b'unchanged'
