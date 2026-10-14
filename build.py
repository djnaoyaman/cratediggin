"""Generate all public views from the one authoritative record crate."""
import json, html, re, os
from urllib.parse import urlparse
from pathlib import Path
ROOT=Path(__file__).parent
DIST=ROOT/'dist'
HOST=os.environ.get('SITE_URL','https://djnaoyaman.github.io/cratediggin').rstrip('/')
BASE_PATH=urlparse(HOST).path.rstrip('/')
tracks=json.loads((ROOT/'tracks.json').read_text())
ids=set()
for t in tracks:
    assert re.fullmatch(r'[a-z0-9-]+',t['id']) and t['id'] not in ids, 'Invalid or duplicate ID'
    ids.add(t['id'])
    assert isinstance(t['year'],int) and 1970<=t['year']<=2100
    assert t['youtube'].get('id') is None or re.fullmatch(r'[A-Za-z0-9_-]{11}',t['youtube']['id'])
    assert len(t['essay'])>=3 and t['sources'] and t['moods']
    main=[s for s in t['samples'] if s.get('main')]
    assert len(main)<=1, 'At most one representative sample record is allowed'
    if main and main[0].get('youtube'): assert re.fullmatch(r'[A-Za-z0-9_-]{11}',main[0]['youtube']['id'])
    for f in t['facts']+t['samples']:
        assert all(0<=i<len(t['sources']) for i in f['sources'])
    for s in t['sources']:
        assert s['url'].startswith('https://')
DIST.mkdir(exist_ok=True)
(DIST/'tracks.js').write_text('window.TRACKS = '+json.dumps(tracks,ensure_ascii=False).replace('</','<\\/')+';\n')
base=(DIST/'index.html').read_text()
base=re.sub(r'<script type="application/ld\+json">.*?</script>', '', base, flags=re.S)
base=re.sub(r'<main id="view" tabindex="-1">.*?</main>', '<main id="view" tabindex="-1"></main>', base, flags=re.S)
base=re.sub(r'<!-- SHARING_METADATA -->.*?<!-- /SHARING_METADATA -->', '', base, flags=re.S)
links=[]
for t in tracks:
    p=DIST/'songs';p.mkdir(exist_ok=True)
    e=html.escape
    body='<article><h1>'+e(t['title'])+'</h1><p>'+e(t['artist'])+'</p><p>'+e(t['deck'])+'</p><h2>'+e(t['essayTitle'])+'</h2>'+''.join('<p>'+e(x)+'</p>' for x in t['essay'])
    body+='<h2>制作背景</h2>'+''.join('<h3>'+e(f['title'])+'</h3><p>'+e(f['text'])+'</p>' for f in t['facts'])
    body+='<h2>サンプル元</h2>'+''.join('<h3>'+e(s['artist']+' — '+s['title'])+'</h3><p>'+e(s['role'])+'</p>'+('<a href="https://www.youtube.com/watch?v='+s['youtube']['id']+'">サンプル元のYouTube</a>' if s.get('youtube') else '') for s in t['samples'])
    body+='<p>'+e(t.get('editorialStatus',''))+'</p><p>'+e(t.get('sampleStatus',''))+'</p><h2>出典</h2>'+''.join('<p><a href="'+e(s['url'])+'">'+e(s['label'])+'</a></p>' for s in t['sources'])+'</article>'
    page=base.replace('<main id="view" tabindex="-1"></main>','<main id="view" tabindex="-1">'+body+'</main>')
    page=re.sub(r'<title>.*?</title>','<title>'+e(t['title']+' / '+t['artist']+' — Crate Diggin’')+'</title>',page)
    page=re.sub(r'<meta name="description" content="[^"]*">','<meta name="description" content="'+e(t['deck'],quote=True)+'">',page)
    page=page.replace('href="'+HOST+'/"','href="'+HOST+'/songs/'+t['id']+'.html"',1)
    page=page.replace('<head>','<head><script>window.INITIAL_ROUTE="#/song/'+t['id']+'";</script>')
    page=page.replace('id="hero"','id="hero" hidden')
    ld={'@context':'https://schema.org','@type':'Article','headline':t['title']+' — '+t['artist'],'author':{'@type':'Person','name':'DJ Naoyaman'},'datePublished':t.get('datePublished','2026-10-13'),'inLanguage':'ja','url':HOST+'/songs/'+t['id']+'.html'}
    page=page.replace('</head>','<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False)+'</script></head>')
    (p/(t['id']+'.html')).write_text(page)
    md='# '+t['title']+'\n\n'+t['artist']+' / '+str(t['year'])+' / '+t['region']+'\n\n## '+t['essayTitle']+'\n\n'+'\n\n'.join(t['essay'])+'\n\n## 制作背景\n\n'+'\n\n'.join('### '+f['title']+'\n\n'+f['text'] for f in t['facts'])+'\n\n## サンプル元\n\n'+'\n\n'.join(s['artist']+' — '+s['title']+'\n\n'+s['role']+('\n\nhttps://www.youtube.com/watch?v='+s['youtube']['id'] if s.get('youtube') else '') for s in t['samples'])+'\n\n## 出典\n\n'+'\n'.join('- ['+s['label']+']('+s['url']+')' for s in t['sources'])+'\n'
    (p/(t['id']+'.md')).write_text(md)
    links.append(HOST+'/songs/'+t['id']+'.html')
(DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+html.escape(u)+'</loc></url>' for u in [HOST+'/']+links)+'</urlset>')
(DIST/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+HOST+'/sitemap.xml\n')
(DIST/'llms.txt').write_text('# Crate Diggin’\n\nA Guide to Sampled Mind & Vintage Grooves\n\n選曲・編集・文責 DJ Naoyaman。事実と私見を分け、出典を示すHip Hopガイド。\n\n'+'\n'.join('- ['+t['title']+']('+HOST+'/songs/'+t['id']+'.md)' for t in tracks)+'\n')
(DIST/'llms-full.txt').write_text('\n\n'.join((DIST/'songs'/(t['id']+'.md')).read_text() for t in tracks))
(DIST/'404.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crate Diggin’</title><link rel="stylesheet" href="/style.css"><body><main style="padding:10vw"><h1 class="section-title">KEEP DIGGIN’.</h1><p>このページは見つかりませんでした。</p><a href="/">クレートへ戻る</a></main></body></html>')
print(f'Generated {len(tracks)} songs, source candidates, sitemap and Markdown. Data validation passed.')

# Search, sharing and machine-readable views use the same editorial records.
from brand_assets import icon, social_image, write_icons
write_icons(DIST)
(DIST/'site.webmanifest').write_text(json.dumps({'name':'Crate Diggin’','short_name':'Crate Diggin’','start_url':'/','display':'standalone','theme_color':'#006cb6','background_color':'#ffffff','icons':[{'src':'/icon-192.png','sizes':'192x192','type':'image/png'},{'src':'/icon-512.png','sizes':'512x512','type':'image/png'}]}))
for n in [192,512]:icon(n).save(DIST/f'icon-{n}.png')
(DIST/'og').mkdir(exist_ok=True)
social_image().save(DIST/'og-image.png')
def enhance(path,title,description,url,img,ld,article=False):
    content=path.read_text()
    content=re.sub(r'<!-- SHARING_METADATA -->.*?<!-- /SHARING_METADATA -->', '', content, flags=re.S)
    content=re.sub(r'<meta name="(?:author|robots)" content="[^"]*">|<link (?:rel="apple-touch-icon"[^>]*|rel="icon" sizes="32x32"[^>]*|rel="alternate icon"[^>]*|rel="manifest"[^>]*)>', '', content)
    content=re.sub(r'<meta (?:property="og:[^"]+"|name="twitter:[^"]+") content="[^"]*">','',content)
    version=json.loads((ROOT/'releases.json').read_text())['version']
    img+='?v='+version
    tags=[('og:title',title),('og:description',description),('og:type','article' if article else 'website'),('og:url',url),('og:site_name','Crate Diggin’'),('og:locale','ja_JP'),('og:image',img),('og:image:width','1200'),('og:image:height','630'),('og:image:alt',title+' — Crate Diggin’')]
    head=''.join('<meta property="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in tags)
    head+=''.join('<meta name="'+k+'" content="'+html.escape(v,quote=True)+'">' for k,v in [('twitter:card','summary_large_image'),('twitter:title',title),('twitter:description',description),('twitter:image',img),('twitter:image:alt',title)])
    head+='<meta name="author" content="DJ Naoyaman"><meta name="robots" content="index,follow,max-image-preview:large"><link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png"><link rel="icon" sizes="32x32" type="image/png" href="/favicon-32.png"><link rel="alternate icon" href="/favicon.ico"><link rel="manifest" href="/site.webmanifest">'
    head+='<script type="application/ld+json">'+json.dumps(ld,ensure_ascii=False).replace('</',r'<\/')+'</script>'
    content=content.replace('</head>','<!-- SHARING_METADATA -->'+head+'<!-- /SHARING_METADATA --></head>')
    content=content.replace('公式YouTubeの連続再生','YouTube音源の連続再生')
    path.write_text(content)
for t in tracks:
    social_image(t).save(DIST/'og'/(t['id']+'.png'))
    url=HOST+'/songs/'+t['id']+'.html'
    data={'@context':'https://schema.org','@graph':[{'@type':'MusicRecording','@id':url+'#recording','name':t['title'],'byArtist':{'@type':'MusicGroup' if '、' in t['members'] else 'Person','name':t['artist']},'inAlbum':{'@type':'MusicAlbum','name':t['album']},'datePublished':str(t['year']),'url':url,'sameAs':t['youtube']['url']},{'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Crate Diggin’','item':HOST+'/'},{'@type':'ListItem','position':2,'name':t['title'],'item':url}]}]}
    enhance(DIST/'songs'/(t['id']+'.html'),t['title']+' / '+t['artist'],t['deck'],url,HOST+'/og/'+t['id']+'.png',data,True)
# Expose song links in HTML before JavaScript runs; the client then replaces the view.
listing='<section aria-label="収録曲"><h2>THE RECORD CRATE</h2>'+''.join('<article><h3><a href="/songs/'+t['id']+'.html">'+html.escape(t['title'])+'</a></h3><p>'+html.escape(t['artist']+' / '+str(t['year']))+'</p><p>'+html.escape(t['deck'])+'</p></article>' for t in tracks)+'</section>'
home=DIST/'index.html';content=home.read_text();content=re.sub(r'<main id="view" tabindex="-1">.*?</main>','<main id="view" tabindex="-1">'+listing+'</main>',content,flags=re.S);home.write_text(content)
enhance(home,'Crate Diggin’ — DJ NaoyamanのHip Hop・サンプリングガイド','楽曲から元ネタへ。Hip Hop、サンプリング、グラフィティを出典付きでたどる音楽ガイド。',HOST+'/',HOST+'/og-image.png',{'@context':'https://schema.org','@type':'WebSite','name':'Crate Diggin’','url':HOST+'/','inLanguage':'ja','author':{'@type':'Person','name':'DJ Naoyaman'}})
print('Generated per-song social cards, SEO metadata, structured data, touch icons and HTML links.')

# A single source of version history, also available to the browser.
release=json.loads((ROOT/'releases.json').read_text())
assert re.fullmatch(r'\d+\.\d+',release['version'])
assert all(e['kind']=='major' for e in release['history'])
(DIST/'releases.js').write_text('window.CRATE_SITE_URL = '+json.dumps(HOST)+'; window.CRATE_RELEASE = '+json.dumps(release,ensure_ascii=False).replace('</','<\\/')+';\n')
for page in DIST.rglob('*.html'):
    text=page.read_text().replace('https://crate-diggin.mossyelf3.chatgpt.site',HOST)
    if '/app.js' in text and '/releases.js' not in text:
        text=text.replace('<script src="/app.js"','<script src="/releases.js" defer></script><script src="/app.js"')
    if BASE_PATH:
        text=re.sub(r'((?:href|src)=")/(?!/|'+re.escape(BASE_PATH.lstrip('/'))+'/)',lambda m:m[1]+BASE_PATH+'/',text)
    text=re.sub(r'((?:href|src)="[^"]*?(?:style\.css|app\.js|playlist\.js|timeline\.js|filters\.js|tracks\.js|favicon\.svg|favicon-32\.png|favicon\.ico|apple-touch-icon\.png))(?:\?v=[0-9.]+)?(")',lambda m:m[1]+'?v='+release['version']+m[2],text)
    analytics='<!-- GOOGLE_ANALYTICS -->\n<script async src="https://www.googletagmanager.com/gtag/js?id=G-71ENPHWEJH"></script>\n<script>\nwindow.dataLayer = window.dataLayer || [];\nfunction gtag(){dataLayer.push(arguments);}\ngtag(\'js\', new Date());\ngtag(\'config\', \'G-71ENPHWEJH\', {send_page_view: false});\n</script>\n<!-- /GOOGLE_ANALYTICS -->'
    text=re.sub(r'<!-- GOOGLE_ANALYTICS -->.*?<!-- /GOOGLE_ANALYTICS -->', '', text, flags=re.S)
    if '/app.js' not in text:
        analytics += '<script>gtag(\"event\",\"page_view\",{page_title:document.title,page_location:location.href});</script>'
    text=text.replace('</head>',analytics+'</head>') if '</head>' in text else text.replace('<body',analytics+'<body',1)
    page.write_text(text)
manifest=json.loads((DIST/'site.webmanifest').read_text())
manifest['start_url']=BASE_PATH+'/'
manifest['scope']=BASE_PATH+'/'
for item in manifest['icons']:item['src']=BASE_PATH+'/'+item['src'].lstrip('/')
(DIST/'site.webmanifest').write_text(json.dumps(manifest))
(DIST/'.nojekyll').write_text('')
print('Version '+release['version']+' / GitHub Pages base '+BASE_PATH)
