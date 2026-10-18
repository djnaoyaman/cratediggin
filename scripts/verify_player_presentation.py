import json,re
from pathlib import Path
root=Path('dist');raw=(root/'metadata.js').read_text();pages=json.loads(raw.removeprefix('window.CRATE_PAGES=').removesuffix(';\n'))
count=0
for route,p in pages.items():
 path=p['path'].removeprefix('/cratediggin/');path=path+'index.html' if path.endswith('/') else path
 if not path:path='index.html'
 text=(root/path).read_text();expected='open' if route=='#/' else 'idle'
 assert f'<body data-player-presentation="{expected}">' in text,(route,path)
 assert text.count('id="listening-player"')==1 and text.count('id="player-reveal"')==1
 if expected=='idle':assert 'aria-expanded="false">プレイヤーを表示' in text
 count+=1
assert count>700
print(f'Static content-first markers and compact reveal controls checked for {count} canonical routes.')
