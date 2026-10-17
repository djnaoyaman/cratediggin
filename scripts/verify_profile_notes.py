from pathlib import Path
import json,re,html
r=Path(__file__).resolve().parents[1];d=r/'dist';profile=(d/'editor.html').read_text()
for text in ['DJ Naoyaman','宮崎直哉','足立区','15歳','GAMMA','32年','約5万曲','50以上','青山学院大学文学部教育学科を中退','明治大学商学部商学科を卒業']:
 assert text in profile,text
assert 'GAMMAに教わ' not in profile
assert re.search(r'<a[^>]+href="https://djnaoyaman.github.io/suburbia-classica/"[^>]*>SUBURBIA CLASSICA</a>',profile)
assert 'class="editor-signature"' in profile and 'width="1881" height="628"' in profile
assert 'SUBURBIA CLASSICA</a>の公開内容をもとに' not in profile
ld=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',profile,re.S)[1]);assert ld['@graph'][0]['mainEntity']['alternateName']=='宮崎直哉'
features=json.loads((r/'features.json').read_text())['features']
for ident in ['dj-shadow','j-dilla','madlib']:
 f=next(f for f in features if f['id']==ident);n=f['noteArticle'];s=(d/'producers'/(ident+'.html')).read_text();assert html.escape(n['title']) in s and html.escape(n['introduction']) in s and n['url'] in s
tracks=json.loads((r/'tracks.json').read_text());p=next(t for t in tracks if t['id']=='slum-village-players');assert p['youtube']['id']=='AbBZKBplhGc' and '未検証' in p['youtube']['verification'];assert all('EZXXqfUBbLM' not in s['url'] for s in p['sources'])
print('Owner-supplied biography, real signature, three note links and exact Players candidate verified; playback remains unconfirmed')
