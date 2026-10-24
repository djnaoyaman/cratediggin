"""Validate current authored behavior, without historical fixed paragraph/track counts."""
from pathlib import Path
from html.parser import HTMLParser
import ast
import json
import re
import subprocess
import argparse

ROOT=Path(__file__).resolve().parents[1]


class Text(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.links=[];self.images=[]
    def handle_data(self,data):self.parts.append(data)
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='a':self.links.append(attrs)
        if tag=='img':self.images.append(attrs)


def validate_profile(root=ROOT):
    root=Path(root);dist=root/'dist'
    authored=json.loads((root/'editor_profile.json').read_text(encoding='utf-8'))
    payload=json.loads((dist/'editor-profile.json').read_text(encoding='utf-8'))
    page=(dist/'editor.html').read_text(encoding='utf-8');text=Text();text.feed(payload['html'])
    plain=''.join(text.parts)
    for block in authored['blocks']:
        if block['type']=='h1':continue
        expected=re.sub(r'\[([^\]]+)\]\(https://[^)]+\)',r'\1',block['text'])
        assert expected in plain, 'Authored profile text omitted: '+expected[:50]
    assert authored['name'] in plain and authored['realName'] in plain
    assert payload['html'].count('class="editor-profile"')==1
    assert payload['html'] in page
    assert 'id="creator-sites-network"' not in page
    expected_sites={'ppp','youkai','sakanamushi','kuranpo','chems','suburbia-classica','sanreikotaiyoku','gooooooooood_expression','bookkeeping'}
    for site in expected_sites:assert any(a.get('href','').startswith('https://djnaoyaman.github.io/'+site+'/') for a in text.links),site
    assert not any('yoshida-farmer' in a.get('href','') for a in text.links)
    assert all(a.get('href','').startswith('https://') for a in text.links)
    for image in text.images:
        src=image.get('src','')
        if src.startswith('/cratediggin/'):assert (dist/src.removeprefix('/cratediggin/')).is_file(),src
    assert '<title>'+payload['page']['title']+'</title>' in page
    script=(dist/'app.js').read_text(encoding='utf-8')
    assert '{{EDITOR_PROFILE}}' not in script
    assert "'/editor-profile.json'" in script
    assert authored['blocks'][2]['text'] not in script, 'Biography must not be embedded in shared app.js'
    print('Native author text, links, images, independent payload and SEO PASS')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--mode',default='full');args=parser.parse_args()
    validate_profile()
    if args.mode!='profile':
        for script in (ROOT/'dist').glob('*.js'):subprocess.run(['node','--check',str(script)],check=True)
    for name in ['frontend.py','profile_content.py','scripts/build_pipeline.py','scripts/profile_build.py']:
        ast.parse((ROOT/name).read_text(encoding='utf-8'),filename=name)
    if args.mode=='full':
        tracks=json.loads((ROOT/'tracks.json').read_text(encoding='utf-8'))
        identifiers=[t['id'] for t in tracks];assert len(identifiers)==len(set(identifiers))
        for identifier in identifiers:assert (ROOT/'dist/songs'/(identifier+'.html')).is_file(),identifier
        print(f'JavaScript/Python syntax and generated pages for {len(tracks)} current records PASS')

if __name__=='__main__':main()
