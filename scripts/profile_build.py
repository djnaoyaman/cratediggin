"""Build the independently deployable author page and SPA payload. No music/image imports."""
from pathlib import Path
import html
import importlib.util
import json
import re


def render(root, dist, host):
    root, dist = Path(root), Path(dist)
    spec = importlib.util.spec_from_file_location('independent_profile', root/'profile_content.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from urllib.parse import urlparse
    data = json.loads((root/'editor_profile.json').read_text(encoding='utf-8'))
    body = module.render_profile(root, urlparse(host).path.rstrip('/'))
    page = dist/'editor.html'
    if not page.is_file():
        raise ValueError('A validated site shell is required before an independent profile build')
    text = page.read_text(encoding='utf-8')
    text, count = re.subn(r'(<main id="view"[^>]*>).*?(</main>)', lambda m:m[1]+body+m[2], text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Missing native profile container')
    title = data['name']+' — 編者紹介 / CRATEDIGGIN’'
    description = 'CRATE DIGGIN’の選曲・編集を行う'+data['name']+'（'+data['realName']+'）のプロフィール。'
    metadata = {'title':title,'description':description,'url':host.rstrip('/')+'/editor.html'}
    def refresh_graph(match):
        graph=json.loads(match[1])
        if not any(n.get('@type')=='ProfilePage' for n in graph.get('@graph',[])):return match[0]
        for node in graph.get('@graph',[]):
            if node.get('@type')=='ProfilePage':
                node['mainEntity']['name']=data['name'];node['mainEntity']['alternateName']=data['realName']
        metadata['jsonld']=graph
        return '<script type="application/ld+json">'+json.dumps(graph,ensure_ascii=False).replace('<','\\u003c')+'</script>'
    text=re.sub(r'<script type="application/ld\+json">(.*?)</script>',refresh_graph,text,flags=re.S)
    text = re.sub(r'<title>.*?</title>',lambda _: '<title>'+html.escape(title)+'</title>',text,count=1,flags=re.S)
    for key, value in [('name="description"',description),('property="og:title"',title),('name="twitter:title"',title),('property="og:description"',description),('name="twitter:description"',description)]:
        text = re.sub(r'(<meta '+re.escape(key)+r' content=")[^"]*(")',lambda m:m[1]+html.escape(value,quote=True)+m[2],text)
    text = re.sub(r'<script id="editor-profile-metadata"[^>]*>.*?</script>','',text,flags=re.S)
    encoded = json.dumps(metadata,ensure_ascii=False).replace('<','\\u003c')
    text = text.replace('</head>','<script id="editor-profile-metadata" type="application/json">'+encoded+'</script></head>')
    page.write_text(text,encoding='utf-8')
    (dist/'editor-profile.json').write_text(json.dumps({'html':body,'page':metadata},ensure_ascii=False),encoding='utf-8')
    return ['editor.html','editor-profile.json']
