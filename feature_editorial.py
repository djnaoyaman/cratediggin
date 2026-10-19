"""Source-led long-form features, separate from the editor's existing personal essays."""
import html,re
from urllib.parse import urlparse
LINK=re.compile(r'\[([^\]\n]+)\]\(([^\s)]+)\)')
def inline(text,base_path=''):
    out=[];position=0
    for m in LINK.finditer(text):
        out.append(html.escape(text[position:m.start()]));label,url=m.groups()
        assert re.fullmatch(r'#/song/[a-z0-9-]+',url) or (urlparse(url).scheme=='https' and bool(urlparse(url).hostname)), 'Invalid editorial link'
        href=base_path+'/tracks/'+url.split('/')[-1]+'.html' if url.startswith('#/song/') else url
        out.append('<a href="'+html.escape(href,quote=True)+'">'+html.escape(label)+'</a>');position=m.end()
    out.append(html.escape(text[position:]));return ''.join(out)
def render_longform(e,base_path=''):
    assert e['format']=='source-led-v1' and e['sections'] and e['sources']
    assert all(isinstance(s,dict) and isinstance(s.get('label'),str) and s['label'].strip() and isinstance(s.get('url'),str) and urlparse(s['url']).scheme=='https' and urlparse(s['url']).hostname for s in e['sources']), 'Invalid source metadata'
    body='<article class="prose feature-editorial feature-editorial--source-led"><p class="eyebrow">PRODUCTION STORIES</p><h2>'+html.escape(e['title'])+'</h2><p class="intro">'+html.escape(e['deck'])+'</p>'
    body+=''.join('<p>'+inline(p,base_path)+'</p>' for p in e['introduction'])
    for section in e['sections']:
        body+='<section><h3>'+html.escape(section['heading'])+'</h3>'+''.join('<p>'+inline(p,base_path)+'</p>' for p in section['paragraphs'])
        refs=section.get('sources',[]);assert len(refs)==len(set(refs)) and all(type(i)==int and 0<=i<len(e['sources']) for i in refs)
        if refs:body+='<p class="essay-references">出典：'+ ' / '.join('<a href="'+html.escape(e['sources'][i]['url'],quote=True)+'">'+html.escape(e['sources'][i]['label'])+'</a>' for i in refs)+'</p>'
        body+='</section>'
    return body+'<p class="read-only-note">'+html.escape(e['disclosure'])+'</p></article>'
