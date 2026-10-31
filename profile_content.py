"""Render the owner's supplied public biography with escaped text and supplied public links."""
import html,json,re
from pathlib import Path

def inline(text):
    result=[];start=0
    for m in re.finditer(r'\[([^\]]+)\]\((https://[^\s)]+)\)',text):
        result.append(html.escape(text[start:m.start()]))
        result.append('<a href="'+html.escape(m[2],quote=True)+'" target="_blank" rel="noopener noreferrer">'+html.escape(m[1])+'</a>');start=m.end()
    result.append(html.escape(text[start:]));return ''.join(result)

def profile_photo(base_path, kind):
    name, width, height, alt = (("editor-provided-collage.webp",1456,816,"DJ NaoyamanのDJパフォーマンス・コラージュ（ユーザー提供）") if kind=="hero" else ("editor-provided-event.jpg",2048,1365,"DJ Naoyamanのイベント写真（ユーザー提供）"))
    return '<figure class="editor-photo editor-photo--'+kind+'"><img src="'+base_path+'/'+name+'" width="'+str(width)+'" height="'+str(height)+'" alt="'+alt+'" loading="lazy"><figcaption>ユーザー提供</figcaption></figure>'

def render_profile(root,base_path):
    data=json.loads((root/'editor_profile.json').read_text(encoding='utf-8'))
    out=['<article class="editor-profile"><header class="editor-profile-heading"><h1><span class="editor-name-accessible">'+html.escape(data['name'])+'</span><img class="editor-signature" src="'+base_path+'/'+data['signature']+'" alt="" width="1881" height="628"></h1></header><div class="prose">'];in_list=False
    for block in data['blocks']:
        kind=block['type'];text=block['text']
        if kind=='h1':continue
        assert kind in ('h2','h3','p','li')
        if kind=='li' and not in_list:out.append('<ul>');in_list=True
        if kind!='li' and in_list:out.append('</ul>');in_list=False
        out.append('<'+kind+'>'+inline(text)+'</'+kind+'>')
    if in_list:out.append('</ul>')
    out.append('</div><details class="editor-photo-archive"><summary>写真</summary>'+profile_photo(base_path,'hero')+profile_photo(base_path,'event')+'</details></article>');return ''.join(out)


EDITOR_NOTE_REPLACEMENTS = json.loads(Path(__file__).with_name('editor_notes.json').read_text(encoding='utf-8'))

def polite_editor_note(content):
    """Keep the compact editor page free of a duplicate shared introduction."""
    return re.sub(r'<section class="manifesto">.*?</section>', '', content, count=1, flags=re.S)
