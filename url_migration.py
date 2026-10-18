"""Preserve historical URLs while moving public catalog paths. Internal route IDs stay stable."""
import html
import json
import shutil
from urllib.parse import urlparse


def prepare_pages(pages, dist, host, features, tracks):
    base = urlparse(host).path.rstrip('/')
    mapping = {base + '/songs/': base + '/tracks/', base + '/features/': base + '/artists/'}
    for t in tracks:
        for ext in ('.html', '.md'):
            mapping[base+'/songs/'+t['id']+ext] = base+'/tracks/'+t['id']+ext
    for f in features:
        mapping[base+'/features/'+f['id']+'.html'] = base+('/artists/' if f['type']=='artist' else '/producers/')+f['id']+'.html'
    mapping[base+'/features/tribe-production.html'] = base+'/artists/tribe.html'
    pairs = sorted(mapping.items(), key=lambda pair: len(pair[0]), reverse=True)

    def replace(value):
        if isinstance(value, str):
            # Only exact internal URL prefixes, never unrelated external source URLs.
            for old, new in pairs:
                value = value.replace(host+old[len(base):], host+new[len(base):])
            return value
        if isinstance(value, list): return [replace(v) for v in value]
        if isinstance(value, dict): return {k: replace(v) for k,v in value.items()}
        return value

    for route, p in pages.items():
        old_target = p['target']
        old_path = p['path']
        new_path = mapping.get(old_path, old_path)
        p.update(replace(p))
        p['path'] = new_path
        relative = new_path[len(base)+1:]
        target = dist / (relative + 'index.html' if relative.endswith('/') or not relative else relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        content = old_target.read_text(encoding='utf-8')
        for old, new in pairs:
            content = content.replace('href="'+old, 'href="'+new)
        content = replace(content)
        target.write_text(content, encoding='utf-8')
        p['target'] = target
    (dist/'tracks').mkdir(exist_ok=True)
    for t in tracks:
        old = dist/'songs'/(t['id']+'.md')
        new = dist/'tracks'/(t['id']+'.md')
        text = replace(old.read_text(encoding='utf-8'))
        new.write_text(text, encoding='utf-8')
        # Markdown has no redirect mechanism; leave a compatible copy with the new canonical.
        old.write_text(text, encoding='utf-8')
    return mapping


def write_legacy_pages(dist, host, mapping, pages=None):
    metadata = {p['path']: p for p in (pages or {}).values()}
    base = urlparse(host).path.rstrip('/')
    for old, new in mapping.items():
        if old.endswith('.md'): continue
        target = dist/(old[len(base)+1:]+'index.html' if old.endswith('/') else old[len(base)+1:])
        target.parent.mkdir(parents=True, exist_ok=True)
        url = host + new[len(base):]
        social = ''
        page = metadata.get(new) if old.startswith(base + '/songs/') and old.endswith('.html') else None
        if page:
            values = {'og:title': page['title'], 'og:description': page['description'], 'og:url': page['url'], 'og:type': page['kind'], 'og:site_name': 'CRATEDIGGIN\'', 'og:locale': 'ja_JP', 'og:image': page['image'], 'og:image:width': '1200', 'og:image:height': '630', 'og:image:type': 'image/png', 'og:image:alt': page['imageAlt']}
            social = ''.join('<meta property="'+key+'" content="'+html.escape(value, quote=True)+'">' for key,value in values.items())
            values = {'twitter:card': 'summary_large_image', 'twitter:title': page['title'], 'twitter:description': page['description'], 'twitter:image': page['image'], 'twitter:image:alt': page['imageAlt']}
            social += ''.join('<meta name="'+key+'" content="'+html.escape(value, quote=True)+'">' for key,value in values.items())
        extra = '<p><a href="'+base+'/producers/">PRODUCERS：プロデューサー特集</a></p>' if old==base+'/features/' else ''
        # Static hosting: instant HTML refresh + JS preserves query/hash. This is not an HTTP 301.
        script = 'const u=new URL('+json.dumps(url)+');u.search=location.search;u.hash=location.hash;location.replace(u.href);'
        target.write_text('<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ページの移転 — CRATEDIGGIN\'</title><link rel="canonical" href="'+html.escape(url,quote=True)+'"><meta http-equiv="refresh" content="0;url='+html.escape(url,quote=True)+'">'+social+'<script>'+script+'</script></head><body><main><h1>ページのURLが変わりました</h1><p><a href="'+html.escape(url,quote=True)+'">新しいページを開く</a></p>'+extra+'</main></body></html>', encoding='utf-8')
    (dist/'url-migrations.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2),encoding='utf-8')
