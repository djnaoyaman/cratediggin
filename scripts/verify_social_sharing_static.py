from pathlib import Path
import json,re,html
from urllib.parse import urlparse,parse_qs
r=Path(__file__).resolve().parents[1]/'dist';s=(r/'metadata.js').read_text();j=json.loads(s.removeprefix('window.CRATE_PAGES=').strip().removesuffix(';'));n=0
for p in j.values():
 path=p['path'].removeprefix('/cratediggin/');f=r/path
 if not path or path.endswith('/'):f=f/'index.html'
 h=f.read_text();footer=h[h.index('<footer'):h.index('</footer>')];assert 'page-sharing' in footer,p['path']
 hrefs=[html.unescape(u) for u in re.findall('href="([^"]+)"',footer)];x=next(u for u in hrefs if u.startswith('https://x.com/intent/tweet?'));fb=next(u for u in hrefs if u.startswith('https://www.facebook.com/sharer/'));line=next(u for u in hrefs if u.startswith('https://line.me/R/share?'))
 assert parse_qs(urlparse(x).query)['url']==[p['url']];assert parse_qs(urlparse(x).query)['text']==[p['title']];assert parse_qs(urlparse(fb).query)['u']==[p['url']];assert parse_qs(urlparse(line).query)['text']==[p['title']+'\n'+p['url']];n+=1
print(n,'static pages have exact canonical social sharing links')
