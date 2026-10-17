"""Render the owner's supplied public biography with escaped text and supplied public links."""
import html,json,re

def inline(text):
    result=[];start=0
    for m in re.finditer(r'\[([^\]]+)\]\((https://[^\s)]+)\)',text):
        result.append(html.escape(text[start:m.start()]))
        result.append('<a href="'+html.escape(m[2],quote=True)+'" target="_blank" rel="noopener noreferrer">'+html.escape(m[1])+'</a>');start=m.end()
    result.append(html.escape(text[start:]));return ''.join(result)

def render_profile(root,base_path):
    data=json.loads((root/'editor_profile.json').read_text(encoding='utf-8'))
    out=['<article class="editor-profile"><header class="editor-profile-heading"><h1>'+html.escape(data['name'])+'</h1><p>'+html.escape(data['realName'])+'</p><img class="editor-signature" src="'+base_path+'/'+data['signature']+'" alt="DJ Naoyamanのタギング・グラフティ署名" width="1881" height="628"></header><div class="prose">'];in_list=False
    for block in data['blocks']:
        kind=block['type'];text=block['text']
        if kind=='h1':continue
        assert kind in ('h2','h3','p','li')
        if kind=='li' and not in_list:out.append('<ul>');in_list=True
        if kind!='li' and in_list:out.append('</ul>');in_list=False
        out.append('<'+kind+'>'+inline(text)+'</'+kind+'>')
    if in_list:out.append('</ul>')
    out.append('</div></article>');return ''.join(out)
