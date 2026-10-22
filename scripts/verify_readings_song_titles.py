from pathlib import Path
import json,argparse,hashlib
from html.parser import HTMLParser
from approved_readings_song_titles import F,sha,historical_readings_song_titles_file
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');args=p.parse_args()
assert sha((R/'scripts/fixtures/approved-readings-song-titles.json').read_bytes())=='a74720e970011f2ccfbfc223eb17ca82c9172c842df24833fd1b6b40153aaf12'
for path,h in F['unchanged'].items():assert sha((R/path).read_bytes())==h,'Unchanged source/content/art drift: '+path
assert json.loads((R/'scripts/ci/manifest.json').read_text())==F['afterCI'],'CI changes outside exact reviewed delta'
assert all(c in F['afterCI']['commands']for c in F['beforeCI']['commands'])
assert all(F['afterCI']['groups'][k]==v for k,v in F['beforeCI']['groups'].items())
assert sha((R/F['priorHelper']['path']).read_bytes())==F['priorHelper']['afterSHA256']
for path,c in F['files'].items():
 raw=(R/path).read_bytes();assert sha(historical_readings_song_titles_file(path,raw))==c['beforeSHA256']
 for bad in [raw+b' ',c['before'].encode()]:
  try:historical_readings_song_titles_file(path,bad)
  except AssertionError:pass
  else:raise AssertionError('Unapproved presentation bytes accepted: '+path)
tracks=json.loads((R/'tracks.json').read_text());assert len(tracks)==len({t['id']for t in tracks})==522
assert tracks[-1]['id']=='funkdoobiest-lost-in-thought'
assert "esc(s.title)+'</p><h2>'"in(R/'src/app/renewal.js').read_text()
assert "esc(t['title'])+'</p><h2>'"in(R/'discovery.py').read_text()
class Cards(HTMLParser):
 def __init__(self):super().__init__();self.cards=[];self.card=None;self.depth=0;self.child=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if self.card is None:
   if tag=='a'and'reading-card'in a.get('class','').split():self.card={'href':a['href'],'children':[]};self.depth=1
   return
  self.depth+=1
  if self.depth==2:self.child={'tag':tag,'class':a.get('class',''),'text':''};self.card['children'].append(self.child)
 def handle_data(self,data):
  if self.card is not None and self.child is not None:self.child['text']+=data
 def handle_endtag(self,tag):
  if self.card is None:return
  self.depth-=1
  if self.depth==1:self.child=None
  if self.depth==0:self.cards.append(self.card);self.card=None
def check_static(source):
 parsed=Cards();parsed.feed(source);assert len(parsed.cards)==522
 for card,t in zip(parsed.cards,tracks):
  assert card['href']=='/cratediggin/tracks/'+t['id']+'.html'
  assert [x['tag']for x in card['children']]==['span','p','h2','p','span']
  assert [x['text']for x in card['children']]==[t['artist'],t['title'],t['essayTitle']or t['title'],t['deck'],'READ ARTICLE ↗'],t['id']
  assert card['children'][1]['class']=='reading-song-title'
if not args.source_only:
 D=R/'dist';source=(D/'readings/index.html').read_text();check_static(source)
 assert sha((D/'style.css').read_bytes())==F['files']['src/assets/style.css']['afterSHA256']
 assert 'reading-song-title'in(D/'app.js').read_text()
 # An accidentally omitted song row must fail the same whole-list contract.
 damaged=source.replace('<p class="reading-song-title">','<p class="missing-title">',1)
 try:check_static(damaged)
 except AssertionError:pass
 else:raise AssertionError('Missing title class mutation accepted')
print('READINGS exact522 artist/song/title/deck/link order; original content/art/source and strict inverse guards PASS')
