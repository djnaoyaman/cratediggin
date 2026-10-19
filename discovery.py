"""One metadata model for static HTML, client navigation and machine-readable views."""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, urlparse
from revision_dates import revision_dates
from catalog import work_type, work_label, work_count, year_label


def encoded(value):
    return quote(value, safe="~!*'()-_")


def finalize_discovery(root, dist, host, tracks, features, guides):
    esc = html.escape
    base_path = urlparse(host).path.rstrip('/')
    version = json.loads((root / 'releases.json').read_text(encoding='utf-8'))['version']
    deepdives = json.loads((root / 'editorial_deepdives.json').read_text(encoding='utf-8'))
    # Dates describe authored content, not image dimensions or other build projections.
    authored_tracks = json.loads((root / 'tracks.json').read_text(encoding='utf-8'))
    authored_features = json.loads((root / 'features.json').read_text(encoding='utf-8'))['features']
    revisions = revision_dates(root, authored_tracks, deepdives, authored_features)
    entities = json.loads((root / 'artist_entities.json').read_text(encoding='utf-8'))
    assert {t['artist'] for t in tracks} <= entities.keys(), 'Add new artists to artist_entities.json'
    assert all(x['type'] in ('Person', 'MusicGroup', None) for x in entities.values())
    author_url = host + '/editor.html'
    author = {'@type': 'Person', '@id': author_url + '#person', 'name': 'DJ Naoyaman', 'url': author_url}
    pages = {}
    template = (root / 'templates' / 'index.html').read_text(encoding='utf-8')
    names = sorted({t['artist'] for t in tracks}, key=str.casefold)
    slugs = {n: hashlib.sha256(n.encode()).hexdigest()[:16] for n in names}

    def entity(name):
        result = {'name': name}
        kind = entities.get(name, {}).get('type')
        if kind:
            result['@type'] = kind
        if name in slugs:
            result['@id'] = host + '/artists/' + slugs[name] + '.html#artist'
        return result

    def add(route, relative, title, description, body=None, image='og-image.jpg', graph=None, kind='website', image_alt=None):
        target = dist / (relative or 'index.html')
        if relative.endswith('/'):
            target = target / 'index.html'
        url = host + '/' + relative
        if body is not None:
            content = re.sub(r'<main id="view" tabindex="-1">.*?</main>',
                             lambda _: '<main id="view" tabindex="-1">' + body + '</main>', template, flags=re.S)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
        elif not target.exists():
            raise ValueError(f'Missing generated page: {target}')
        breadcrumb = [{'@type': 'ListItem', 'position': 1, 'name': 'CRATEDIGGIN\'', 'item': host + '/'}]
        if relative:
            breadcrumb.append({'@type': 'ListItem', 'position': 2, 'name': title.split(' — ')[0], 'item': url})
        data = {'@context': 'https://schema.org', '@graph': (graph or [
            {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': title,
             'description': description, 'inLanguage': 'ja', 'author': author}]) + [
                 {'@type': 'BreadcrumbList', 'itemListElement': breadcrumb}]}
        pages[route] = {'route': route, 'path': base_path + '/' + relative,
                        'title': title, 'description': description, 'url': url,
                        'image': host + '/' + image + '?v=' + version, 'imageAlt': image_alt or title, 'kind': kind,
                        'jsonld': data, 'target': target,
                        'published': data['@graph'][0].get('datePublished'),
                        'modified': data['@graph'][0].get('dateModified')}

    def track_links(items):
        return '<ul>' + ''.join('<li><a href="' + base_path + '/songs/' + t['id'] + '.html">' +
                               esc(t['artist'] + ' — ' + t['title']) + '</a>'+ (' <span class="work-format">'+esc(work_label(t))+'</span>' if work_type(t)!='single' else '')+'</li>' for t in items) + '</ul>'

    def article(url, title, description, image, key, published=None, about=None):
        data = {'@type': 'Article', '@id': url + '#article', 'url': url, 'mainEntityOfPage': url,
                'headline': title, 'description': description, 'inLanguage': 'ja', 'author': author,
                'image': [host + '/' + image + '?v=' + version]}
        if published:
            data['datePublished'] = published
        revision = revisions.get(key)
        if revision and (not published or revision['dateModified'][:10] >= published[:10]):
            data['dateModified'] = revision['dateModified']
        if about:
            data['about'] = about
        return data

    add('#/', '', 'CRATEDIGGIN\' — DJ NaoyamanのHip Hop・サンプリングガイド',
        '楽曲から元ネタへ。Hip Hop、サンプリング、制作背景を出典付きでたどるDJ Naoyamanの音楽ガイド。',
        graph=[{'@type': 'WebSite', '@id': host + '/#website', 'url': host + '/', 'name': 'CRATEDIGGIN\'',
                'inLanguage': 'ja', 'author': author}])
    for t in tracks:
        relative = 'songs/' + t['id'] + '.html'
        url = host + '/' + relative
        image = 'og/' + t['id'] + '.jpg'
        recording = {'@type': 'MusicRecording', '@id': url + '#recording', 'name': t['title'],
                     'byArtist': entity(t['artist']), 'inAlbum': {'@type': 'MusicAlbum', 'name': t['album']},
                     'url': url, 'subjectOf': {'@id': url + '#article'}}
        if work_type(t)=='mix':
            recording['@type']='MusicAlbum'
            recording['albumProductionType']='https://schema.org/DJMixAlbum'
            recording['description']='DJミックス作品。単独の楽曲ではなく、複数の録音をつないだ作品。'
            recording.pop('inAlbum',None)
        if work_type(t)=='album':
            recording['@type']='MusicAlbum'
            recording['albumProductionType']='https://schema.org/StudioAlbum'
            recording['albumReleaseType']='https://schema.org/AlbumRelease'
            recording['numTracks']=t['trackCount']
            recording['description']='公式プレイリストで聴くアルバム全体。'
            recording.pop('inAlbum',None)
        if work_type(t)=='live_video':
            recording={'@type':'VideoObject','@id':url+'#recording','name':t['title'],
                       'description':t['deck'],'url':url,'subjectOf':{'@id':url+'#article'},
                       'embedUrl':'https://www.youtube.com/embed/'+t['youtube']['id']}
            for key in ('uploadDate','thumbnailUrl','duration'):
                if t['youtube'].get(key): recording[key]=t['youtube'][key]
        # A reference upload is not an authoritative identity link. Omit sameAs.
        if t.get('year') is not None and not t.get('yearBasis'):
            recording['datePublished'] = str(t['year'])
        art = article(url, t['title'] + ' — ' + t['artist'], t['deck'], image,
                      'song/' + t['id'], t.get('datePublished'), {'@id': url + '#recording'})
        art['citation'] = [s['url'] for s in t['sources']]
        add('#/song/' + t['id'], relative, t['title'] + ' / ' + t['artist'] + ' — CRATEDIGGIN\'',
            (work_label(t)+'。' if work_type(t)!='single' else '')+t['deck'], image=image, graph=[art, recording], kind='article', image_alt=t['art']['alt'] if t['art'].get('image') else t['title'] + ' — ' + t['artist'] + '｜CRATE DIGGIN｜DJ Naoyaman')
        published = t.get('datePublished')
        updated = art.get('dateModified')
        byline = '<p class="byline">選曲・編集・文責 <a href="' + base_path + '/editor.html">DJ Naoyaman</a>'
        if published:
            byline += ' · 公開 <time datetime="' + esc(published) + '">' + esc(published[:10]) + '</time>'
        if updated:
            byline += ' · 更新 <time datetime="' + esc(updated) + '">' + esc(updated[:10]) + '</time>'
        byline += '</p>'
        content = (dist / relative).read_text(encoding='utf-8')
        content = re.sub(r'<!-- EDITORIAL_BYLINE -->.*?<!-- /EDITORIAL_BYLINE -->', '', content, flags=re.S)
        content = content.replace('<article>', '<article><!-- EDITORIAL_BYLINE -->' + byline + '<!-- /EDITORIAL_BYLINE -->', 1)
        (dist / relative).write_text(content, encoding='utf-8')
        md = dist / 'songs' / (t['id'] + '.md')
        source_text = re.sub(r'<!-- ARTICLE_METADATA -->.*?<!-- /ARTICLE_METADATA -->\n\n', '', md.read_text(encoding='utf-8'), flags=re.S)
        source_text = re.sub(r'\n\n<!-- SOURCE_REFERENCES -->.*?<!-- /SOURCE_REFERENCES -->', '', source_text, flags=re.S)
        for fact in t.get('facts', []):
            original = '### ' + fact['title'] + '\n\n' + fact['text']
            references = ' / '.join('[' + t['sources'][i]['label'] + '](' + t['sources'][i]['url'] + ')' for i in fact['sources'])
            if references:
                source_text = source_text.replace(original, original + '\n\n<!-- SOURCE_REFERENCES -->\n参考資料: ' + references + '\n<!-- /SOURCE_REFERENCES -->', 1)
        lines = ['正規URL: ' + url, '著者: [DJ Naoyaman](' + author_url + ')']
        if published:
            lines.append('記事公開日: ' + published)
        if updated:
            lines.append('記事更新日: ' + updated + '（記事データのGit改訂記録）')
        if t.get('noteReviewedAt'):
            lines.append('解説確認日: ' + t['noteReviewedAt'])
        pending = t.get('review', {}).get('metadataPending', [])
        if pending:
            lines.append('確認継続中: ' + ' / '.join(pending))
        source_text = source_text.replace('\n\n', '\n\n<!-- ARTICLE_METADATA -->\n' + '\n\n'.join(lines) + '\n<!-- /ARTICLE_METADATA -->\n\n', 1)
        md.write_text(source_text, encoding='utf-8')
    for name in names:
        relative = 'artists/' + slugs[name] + '.html'
        selected = [t for t in tracks if t['artist'] == name]
        url = host + '/' + relative
        add('#/artist/' + encoded(name), relative, name + ' の楽曲一覧 — CRATEDIGGIN\'',
            name + 'の掲載' + work_count(selected) + '。楽曲解説、サンプリング元ネタと制作背景を出典からたどる。',
            graph=[{'@type': 'CollectionPage', '@id': url + '#page', 'url': url, 'name': name + ' の楽曲一覧',
                    'about': entity(name), 'mainEntity': {'@type': 'ItemList', 'numberOfItems': len(selected),
                    'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': host + '/songs/' + t['id'] + '.html',
                                         'name': t['title']} for i, t in enumerate(selected)]}}])
    for f in features:
        relative = 'features/' + f['id'] + '.html'
        url = host + '/' + relative
        from brand_assets import save_social_image, save_feature_social_image
        feature_image = 'feature-og/' + f['id'] + '.jpg'
        (dist / 'feature-og').mkdir(exist_ok=True)
        if f.get('visual',{}).get('precomposed'):
            save_feature_social_image(dist/feature_image, root/'src/assets'/f['visual']['photo'])
        else:
            save_social_image(dist / feature_image, {'title': f['name'], 'artist': 'Artist & producer features / DJ Naoyaman'})
        description = f['name'] + '特集。' + f['editorial']['title'] + ' ' + f['editorial']['context']
        add('#/feature/' + f['id'], relative, f['name'] + ' — ' + f['editorial']['title'] + ' / CRATEDIGGIN\'',
            description, image=feature_image, graph=[article(url, f['editorial']['title'], description, feature_image,
                                        'feature/' + f['id'])], kind='article')
        pages['#/feature/' + f['id']]['jsonld']['@graph'][0]['citation'] = [s['url'] for s in f['editorial']['sources']]
    add('#/songs', 'songs/', '楽曲一覧 — CRATEDIGGIN\'',
        work_count(tracks) + 'のHip Hopを聴きどころ・アーティスト・年代から探す。サンプル元と制作背景を出典付きで紹介。',
        '<h1>TRACKS FROM THE GRAFFITI.</h1><p>グラフティから曲を選ぶ。</p><div class="static-graffiti-gallery">'+''.join('<a href="'+base_path+'/songs/'+t['id']+'.html"><h2>'+esc(t['title'])+'</h2><p>'+esc(t['artist'])+'</p>'+('<figure class="catalog-graffiti"><img loading="lazy" src="'+base_path+'/'+esc(t['art']['image'])+'" alt="'+esc(t['art']['alt'])+'"><figcaption>Designed by DJ Naoyaman</figcaption></figure>' if t.get('art',{}).get('image') else '')+'</a>' for t in tracks)+'</div>')
    readings_body='<h1>READ THE SOUND.</h1><p>制作の背景、サンプリング、人と音楽のつながりを読む。</p><div class="reading-grid">'+''.join('<a class="reading-card" href="'+base_path+'/songs/'+t['id']+'.html"><span class="eyebrow">'+esc(t['artist'])+'</span><h2>'+esc(t.get('essayTitle') or t['title'])+'</h2><p>'+esc(t['deck'])+'</p><span>READ ARTICLE ↗</span></a>' for t in tracks)+'</div>'
    add('#/readings','readings/',"READINGS — CRATEDIGGIN'",'Hip Hopの制作背景、サンプリング、街と人の物語。全掲載作品の記事を読む。',readings_body)
    add('#/artists', 'artists/', 'アーティスト一覧 — CRATEDIGGIN\'', '掲載アーティスト別に楽曲と特集を探す。',
        '<h1>ARTISTS</h1><ul>' + ''.join('<li><a href="' + base_path + '/artists/' + slugs[n] + '.html">' +
        esc(n) + '</a></li>' for n in names) + '</ul>')
    def feature_card(f):
        v=f.get('visual');href=base_path+'/features/'+f['id']+'.html'
        from feature_policy import qualification_label
        copy='<h3>'+esc(f['name'])+'</h3><p>'+esc(f['editorial']['title'])+'</p><span>'+esc(qualification_label(f))+'</span>'
        if not v:
            return '<a class="feature-card feature-card--text" data-feature-id="'+esc(f['id'])+'" href="'+href+'"><span class="eyebrow">PRODUCTION STORIES</span>'+copy+'<span>READ FEATURE ↗</span></a>'
        tag=('<img class="feature-name-tag" src="'+base_path+'/'+esc(v['tag'],quote=True)+'" alt="" loading="eager">') if v.get('tag') else '<span class="feature-name-tag feature-name-typography" aria-hidden="true">'+esc(v.get('typographicName',f['name']))+'</span>'
        if v.get('nameOnly'):
            return '<article class="feature-poster"><a class="feature-card feature-card--portrait" href="'+href+'"><div class="feature-portrait feature-portrait--name"><span class="feature-paper-grain" aria-hidden="true"></span><span class="feature-tape" aria-hidden="true">'+('ARTIST FILE' if f['type']=='artist' else 'PRODUCER FILE')+'</span><img class="feature-name-tag" src="'+base_path+'/'+esc(v['tag'],quote=True)+'" alt="'+esc(v['alt'],quote=True)+'" loading="lazy"></div><div class="feature-poster-copy">'+copy+'</div></a></article>'
        return ('<article class="feature-poster"><a class="feature-card feature-card--portrait '+('feature-card--provided' if v.get('precomposed') else '')+'" href="'+href+'"><div class="feature-portrait '+('feature-portrait--provided ' if v.get('precomposed') else '')+('feature-portrait--contain' if v.get('fit')=='contain' else '')+'">'
                '<img class="feature-photo" src="'+base_path+'/'+esc(v['photo'],quote=True)+'" alt="'+esc(v['alt'],quote=True)+'" loading="lazy" style="object-position:'+esc(v.get('focus','50% 35%'),quote=True)+'">'
                '<span class="feature-paper-grain" aria-hidden="true"></span><span class="feature-tape" aria-hidden="true">'+('ARTIST FILE' if f['type']=='artist' else 'PRODUCER FILE')+'</span>'
                +tag+'</div><div class="feature-poster-copy">'+copy+'</div></a>'+
                ('<details class="feature-photo-credit" data-photo-provenance="user-provided"><summary>PHOTO / SOURCE</summary><p>'+esc(v['credit'])+'<br>'+esc(v['changes'])+'</p></details>' if v.get('provenance')=='user-provided' else '<details class="feature-photo-credit"><summary>PHOTO / LICENSE</summary><p>Photo: <a href="'+esc(v['source'],quote=True)+'">'+esc(v['author'])+'</a> · <a href="'+esc(v['licenseUrl'],quote=True)+'">'+esc(v['license'])+'</a><br>'+esc(v['changes'])+('<br>写真別出典: '+ ' · '.join('<a href="'+esc(c['source'],quote=True)+'">'+esc(c['label'])+'</a> (<a href="'+esc(c['licenseUrl'],quote=True)+'">license</a>)' for c in v['components']) if v.get('components') else '')+'</p></details>')+'</article>')
    def feature_grid(kind):
        active=[f for f in features if f['type']==kind and f['qualification']['tier']!='archive']
        archive=[f for f in features if f['type']==kind and f['qualification']['tier']=='archive']
        grid=lambda fs:'<div class="feature-grid feature-swipe" role="region" aria-label="特集カード一覧" tabindex="0">'+''.join(feature_card(f) for f in fs)+'</div>'
        policy=json.loads((root/'features.json').read_text())['policy']
        return '<p class="feature-policy">'+esc(policy)+'</p><p class="feature-swipe-hint">左右にスワイプして特集を探す →</p>'+grid(active)+('<section class="feature-archive"><h2>ARCHIVE</h2><p>掲載曲数にかかわらず、公開済みの特集を残しています。</p>'+grid(archive)+'</section>' if archive else '')
    add('#/artists', 'artists/', 'ARTISTS — アーティスト特集・一覧 / CRATEDIGGIN\'',
        'アーティスト特集と全掲載アーティストの楽曲一覧。',
        '<h1>ARTISTS</h1><p><a href="'+base_path+'/producers/">PRODUCERS：プロデューサー特集へ ↗</a></p>'+feature_grid('artist')+'<h2>ALL ARTISTS</h2><ul>'+''.join('<li><a href="'+base_path+'/artists/'+slugs[n]+'.html">'+esc(n)+'</a></li>' for n in names)+'</ul>')
    add('#/producers', 'producers/', 'PRODUCERS — プロデューサー特集 / CRATEDIGGIN\'',
        'ビートと制作背景からたどるプロデューサー特集。',
        '<h1>PRODUCERS</h1><p><a href="'+base_path+'/artists/">ARTISTS：アーティスト特集へ ↗</a></p>'+feature_grid('producer')+'')
    for g in guides:
        selected = [next(t for t in tracks if t['id'] == tid) for tid in g['ids']]
        add('#/guide/' + g['id'], 'guides/' + g['id'] + '.html', g['title'] + ' — CRATEDIGGIN\'', g['description'],
            '<h1>' + esc(g['title']) + '</h1><p>' + esc(g['description']) + '</p>' + track_links(selected))
    add('#/timeline', 'timeline.html', 'Hip Hopの年表 — CRATEDIGGIN\'', '年代・作り手・地域・掲載カテゴリから収録構成を見渡し、出典のある文化の年表へ進む。',
        '<h1>THE TIMELINE</h1>' + __import__('catalog_explorer').render_summary(tracks) + ''.join('<section><h2>' + str(y) + '年</h2>' +
        track_links([t for t in tracks if t['year'] == y]) + '</section>' for y in sorted({t['year'] for t in tracks if t['year'] is not None})) + ('<section><h2>発表年未確認</h2>'+track_links([t for t in tracks if t['year'] is None])+'</section>' if any(t['year'] is None for t in tracks) else ''))
    from render_editorial import about_html
    add('#/about', 'about.html', "編集方針 — CRATEDIGGIN'", '事実と編者の私見を分け、参考資料を示す編集方針。', about_html(root,tracks))
    from brand_assets import save_feature_social_image
    save_feature_social_image(dist/'editor-og.jpg',root/'src/assets/editor-provided-collage.webp')
    add('#/editor', 'editor.html', 'DJ Naoyaman — 編者紹介 / CRATEDIGGIN\'', 'CRATEDIGGIN\'の選曲・編集を行うDJ Naoyaman。',
        __import__('profile_content').render_profile(root,base_path), image='editor-og.jpg',
        graph=[{'@type': 'ProfilePage', '@id': author_url + '#page', 'url': author_url, 'mainEntity': {**author, 'alternateName':'宮崎直哉','image':host+'/editor-og.jpg?v='+version}}])

    def real_links(content):
        def replace(match):
            route = html.unescape(match[1])
            if route=='#/features': route='#/artists'
            if route.startswith('#/?'):
                path = base_path + '/?' + route.split('?', 1)[1]
            elif route.startswith('#/songs?'):
                path = base_path + '/tracks/?' + route.split('?', 1)[1]
            else:
                item = pages.get(route)
                if not item:
                    return match[0]
                path = item['path']
            return 'href="' + esc(path, quote=True) + '"'
        return re.sub(r'href="(#/[^\"]*)"', replace, content)

    from url_migration import prepare_pages, write_legacy_pages
    migration = prepare_pages(pages, dist, host, features, tracks)
    compact = {}
    meta_dir = dist / 'metadata'
    meta_dir.mkdir(exist_ok=True)
    for route, p in pages.items():
        target = p.pop('target')
        key = hashlib.sha256(route.encode()).hexdigest()[:20]
        p['metadataPath'] = base_path + '/metadata/' + key + '.json'
        content = target.read_text(encoding='utf-8')
        if route.startswith('#/song/'):
            track = next(t for t in tracks if t['id']==route.split('/')[-1])
            art = track['art']
            if art.get('image'):
                figure = '<figure class="track-artwork"><img src="'+base_path+'/'+esc(art['image'],quote=True)+'" alt="'+esc(art['alt'],quote=True)+'" width="'+str(art['width'])+'" height="'+str(art['height'])+'" loading="lazy"><figcaption>Original graffiti · Designed by DJ Naoyaman</figcaption></figure>'
                content = re.sub(r'(<main id="view"[^>]*>.*?</h1>)', lambda m: m[0]+figure, content, count=1, flags=re.S)
        presentation = 'open' if route == '#/' else 'idle'
        content = re.sub(r'<body(?: data-player-presentation="[^"]*")?>', '<body data-player-presentation="'+presentation+'">', content, count=1)
        if p['route'] != '#/':
            content = content.replace('id="hero" aria-labelledby=', 'id="hero" hidden aria-labelledby=', 1)
        if presentation == 'idle':
            content = re.sub(r'(<button\b(?=[^>]*\bid="player-reveal")[^>]*?)\s+hidden(?=[\s>])', r'\1', content, count=1)
        content = re.sub(r'<title>.*?</title>', lambda _: '<title>' + esc(p['title']) + '</title>', content, flags=re.S)
        content = re.sub(r'<meta\b[^>]*(?:name="(?:description|author|robots|twitter:[^"]+)"|property="(?:og|article):[^"]+")[^>]*>', '', content)
        content = re.sub(r'<link\b[^>]*rel="(?:canonical|alternate)"[^>]*>', '', content)
        content = re.sub(r'<script type="application/ld\+json">.*?</script>', '', content, flags=re.S)
        content = re.sub(r'<script>window.INITIAL_ROUTE=.*?</script>', '', content, flags=re.S)
        meta = '<meta name="description" content="' + esc(p['description'], quote=True) + '">'
        meta += '<meta name="author" content="DJ Naoyaman"><meta name="robots" content="index,follow,max-image-preview:large">'
        meta += '<link rel="canonical" href="' + esc(p['url'], quote=True) + '">'
        for name, value in {'og:title': p['title'], 'og:description': p['description'], 'og:url': p['url'],
                            'og:type': p['kind'], 'og:site_name': 'CRATEDIGGIN\'', 'og:locale': 'ja_JP',
                            'og:image': p['image'], 'og:image:type': 'image/jpeg', 'og:image:width': '1200', 'og:image:height': '630',
                            'og:image:alt': p['imageAlt']}.items():
            meta += '<meta property="' + name + '" content="' + esc(value, quote=True) + '">'
        for name, value in {'twitter:card': 'summary_large_image', 'twitter:title': p['title'],
                            'twitter:description': p['description'], 'twitter:image': p['image'], 'twitter:image:alt': p['imageAlt']}.items():
            meta += '<meta name="' + name + '" content="' + esc(value, quote=True) + '">'
        if p['kind'] == 'article':
            for name, value in {'article:author': author_url, 'article:published_time': p['published'],
                                'article:modified_time': p['modified']}.items():
                if value:
                    meta += '<meta property="' + name + '" content="' + esc(value, quote=True) + '">'
        meta += '<script type="application/ld+json">' + json.dumps(p['jsonld'], ensure_ascii=False).replace('</', '<\\/') + '</script>'
        initial = {'route': route, 'jsonld': p['jsonld']}
        meta += '<script>window.INITIAL_ROUTE=' + json.dumps(route) + ';window.CRATE_INITIAL_META=' + json.dumps(initial, ensure_ascii=False).replace('</', '<\\/') + ';</script>'
        meta += '<link rel="author" href="' + author_url + '">'
        if route.startswith('#/song/'):
            tid = route.split('/')[-1]
            meta += '<link rel="alternate" type="text/markdown" href="' + host + '/tracks/' + tid + '.md">'
        if '/metadata.js' not in content:
            content = content.replace('<script src="' + base_path + '/app.js', '<script src="' + base_path + '/metadata.js?v=' + version + '" defer></script><script src="' + base_path + '/app.js')
        # Newly added static pages need the same versioned assets and analytics as existing pages.
        for asset in ('app.js', 'art.js', 'style.css', 'tracks.js', 'playlist.js', 'filters.js', 'timeline.js', 'catalog-explorer.js', 'releases.js'):
            content = re.sub(r'((?:href|src)="[^\"]*/' + re.escape(asset) + r')(?:\?v=[0-9.]+)?"',
                             lambda m: m[1] + '?v=' + version + '"', content)
        if '<!-- GOOGLE_ANALYTICS -->' not in content:
            home = (dist / 'index.html').read_text(encoding='utf-8')
            analytics = re.search(r'<!-- GOOGLE_ANALYTICS -->.*?<!-- /GOOGLE_ANALYTICS -->', home, flags=re.S)
            if analytics:
                meta += analytics[0]
        share_urls=[('X','https://x.com/intent/tweet?text='+encoded(p['title'])+'&url='+encoded(p['url'])),('Facebook','https://www.facebook.com/sharer/sharer.php?u='+encoded(p['url'])),('LINE','https://line.me/R/share?text='+encoded(p['title']+'\n'+p['url']))]
        share_html='<nav class="page-sharing" aria-label="このページをシェア"><span class="share-label">SHARE THIS PAGE</span>'+''.join('<a href="'+esc(u,quote=True)+'" target="_blank" rel="noopener noreferrer" aria-label="'+n+'でこのページをシェア（新しいタブ）">'+n+'</a>' for n,u in share_urls)+'</nav>'
        content=content.replace('</footer>',share_html+'</footer>')
        if route.startswith(('#/song/','#/feature/')):
            content=content.replace('</main>',share_html+'</main>')
        content = real_links(content.replace('</head>', meta + '</head>'))
        target.write_text(content, encoding='utf-8')
        (meta_dir / (key + '.json')).write_text(json.dumps(p, ensure_ascii=False), encoding='utf-8')
        compact[route] = {k: v for k, v in p.items() if k != 'jsonld'}
    (dist / 'metadata.js').write_text('window.CRATE_PAGES=' + json.dumps(compact, ensure_ascii=False).replace('</', '<\\/') + ';\n', encoding='utf-8')
    urls = [p['url'] for p in pages.values()]
    import xml.etree.ElementTree as ET
    ns='http://www.sitemaps.org/schemas/sitemap/0.9'
    image_ns='http://www.google.com/schemas/sitemap-image/1.1'
    ET.register_namespace('',ns);ET.register_namespace('image',image_ns)
    sitemap=ET.Element('{'+ns+'}urlset')
    for route,p in pages.items():
        node=ET.SubElement(sitemap,'{'+ns+'}url');ET.SubElement(node,'{'+ns+'}loc').text=p['url']
        modified=p['jsonld']['@graph'][0].get('dateModified')
        if modified: ET.SubElement(node,'{'+ns+'}lastmod').text=modified
        images=[]
        if route.startswith('#/song/'):
            art=next(t['art'] for t in tracks if t['id']==route.split('/')[-1])
            if art.get('image'): images.append(art['image'])
        if route.startswith('#/feature/'):
            feature=next((f for f in features if f['id']==route.split('/')[-1]),None)
            if feature:
                images.extend(photo['image'] for photo in feature.get('personalFeature',{}).get('photos',[]))
        if route=='#/editor': images.extend(['dj-naoyaman-signature-v2.webp','editor-provided-collage.webp','editor-provided-event.jpg'])
        if route in ('#/artists','#/producers'):
            kind='artist' if route=='#/artists' else 'producer'
            for f in features:
                if f['type']==kind:
                    images.extend(f.get('visual',{}).get(k) for k in ('photo','tag') if f.get('visual',{}).get(k))
        for image in dict.fromkeys(images):
            assert (dist/image).is_file(), 'Missing sitemap image: '+image
            item=ET.SubElement(node,'{'+image_ns+'}image');ET.SubElement(item,'{'+image_ns+'}loc').text=host+'/'+image
    ET.ElementTree(sitemap).write(dist/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    llms = '# CRATEDIGGIN\'\n\nDJ Naoyamanが選曲・編集する、出典付きのHip Hop・サンプリングガイド。\n\n'
    llms += '## Editorial policy\n事実と編者の私見を区別します。確認継続中の情報や参考音源を、確認済みの事実と混同しないでください。\n'
    llms += '- [著者](' + author_url + ')\n- [編集方針](' + host + '/about.html)\n- [サイトマップ](' + host + '/sitemap.xml)\n'
    llms += '- [全楽曲のMarkdown](' + host + '/llms-full.txt)\n\n'
    for label, prefix in [('Artists', '#/artist/'), ('Features', '#/feature/'), ('Guides', '#/guide/'), ('Songs', '#/song/')]:
        llms += '## ' + label + '\n'
        for route, p in pages.items():
            if route.startswith(prefix):
                llms += '- [' + p['title'] + '](' + p['url'] + ')\n'
        llms += '\n'
    (dist / 'llms.txt').write_text(llms, encoding='utf-8')
    (dist / 'llms-full.txt').write_text('\n\n---\n\n'.join((dist / 'tracks' / (t['id'] + '.md')).read_text(encoding='utf-8') for t in tracks), encoding='utf-8')
    (dist / 'article-revisions.json').write_text(json.dumps(revisions, ensure_ascii=False, indent=2), encoding='utf-8')
    write_legacy_pages(dist, host, migration, pages)
    print(f'Unified metadata, real URLs and discovery views: {len(urls)} pages')
