"""Truthful site/profile update dates from production Git changes, never build time."""
import html
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET


def latest_revision(root, paths):
    """A documentation-only commit or repeat deployment cannot advance this date."""
    if not paths:
        return None
    try:
        value = subprocess.check_output(
            ['git', '-C', str(root), 'log', '-1', '--format=%H %cI', '--', *sorted(paths)],
            stderr=subprocess.DEVNULL, text=True).strip()
        sha, date = value.split(' ', 1)
        parsed = datetime.fromisoformat(date)
        if parsed.tzinfo is None:
            return None
        return {'revision': sha, 'dateModified': parsed.isoformat()}
    except (OSError, ValueError, subprocess.CalledProcessError):
        return None


def production_path(name):
    if name.startswith(('.github/', 'audit-reports/', 'dist/', 'tests/', 'handoff/', 'notes/', 'scripts/ci/', 'scripts/fixtures/')):
        return False
    if name.endswith(('.md', '.pyc', '.log')) or name == '.gitignore':
        return False
    return not name.startswith('scripts/') or name in {'scripts/build_pipeline.py', 'scripts/profile_build.py'}


def site_paths_with_deletions(root, paths):
    # A deletion is a real production change even though it is absent from ls-files.
    result = {p for p in paths if production_path(p)}
    try:
        deleted = subprocess.check_output(['git', '-C', str(root), 'log', '--format=', '--name-only', '--diff-filter=D'], stderr=subprocess.DEVNULL, text=True)
        result.update(p for p in deleted.splitlines() if p and production_path(p))
    except (OSError, subprocess.CalledProcessError):
        pass
    return result


def json_text(value):
    return json.dumps(value, ensure_ascii=False).replace('<', '\\u003c')


def stamp(date, label, css):
    day = datetime.fromisoformat(date).astimezone(ZoneInfo('Asia/Tokyo')).date().isoformat()
    return '<p class="'+css+'">'+label+' <time datetime="'+html.escape(date, quote=True)+'">'+day+'</time> JST</p>'


def finalize_update_dates(root, dist, production_paths):
    root, dist = Path(root), Path(dist)
    # Build orchestration may classify CI/docs conservatively as full builds;
    # those alone are not a reader-facing site change.
    site_paths = site_paths_with_deletions(root, production_paths)
    site = latest_revision(root, site_paths)
    registry_file = dist/'metadata.js'
    if not site or not registry_file.is_file():
        return {'status': 'no_verified_revision_or_metadata'}
    raw = registry_file.read_text(encoding='utf-8')
    prefix = 'window.CRATE_PAGES='
    if not raw.startswith(prefix):
        raise ValueError('Unexpected metadata registry')
    registry = json.loads(raw[len(prefix):].strip().rstrip(';'))
    profile = latest_revision(root, ['editor_profile.json', 'profile_content.py', 'scripts/profile_build.py'])
    changed = {}
    for route, revision in [('#/', site), ('#/editor', profile)]:
        if not revision or route not in registry:
            continue
        item = registry[route]
        meta = dist/'metadata'/Path(item['metadataPath']).name
        if not meta.is_file():
            raise ValueError('Missing page metadata '+str(meta))
        payload = json.loads(meta.read_text(encoding='utf-8'))
        page = dist/('index.html' if route == '#/' else 'editor.html')
        text = page.read_text(encoding='utf-8')
        # The independent profile renderer has already refreshed its entity/text.
        if route == '#/editor':
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S)
            for block in blocks:
                graph = json.loads(block)
                if any(n.get('@type') == 'ProfilePage' for n in graph.get('@graph', [])):
                    payload['jsonld'] = graph
                    break
            profile_payload = dist/'editor-profile.json'
            if profile_payload.is_file():
                current = json.loads(profile_payload.read_text(encoding='utf-8'))
                for key in ('title', 'description', 'url'):
                    if key in current['page']:
                        payload[key] = current['page'][key]
        date = revision['dateModified']
        payload['jsonld']['@graph'][0]['dateModified'] = date
        payload['modified'] = date
        item.update({key: value for key, value in payload.items() if key != 'jsonld'})
        meta.write_text(json_text(payload), encoding='utf-8')
        text = re.sub(r'<script type="application/ld\+json">.*?</script>',
                      lambda _: '<script type="application/ld+json">'+json_text(payload['jsonld'])+'</script>', text, count=1, flags=re.S)
        text = re.sub(r'<script>window.INITIAL_ROUTE=.*?</script>',
                      lambda _: '<script>window.INITIAL_ROUTE='+json_text(route)+';window.CRATE_INITIAL_META='+json_text({'route': route, 'jsonld': payload['jsonld']})+';</script>', text, count=1, flags=re.S)
        if route == '#/editor' and (dist/'editor-profile.json').is_file():
            current = json.loads((dist/'editor-profile.json').read_text(encoding='utf-8'))
            current['page'].update({key: payload[key] for key in ('title', 'description', 'url', 'modified', 'jsonld')})
            current['html'] = re.sub(r'<p class="page-update">.*?</p>', '', current['html'], flags=re.S)+stamp(date, 'ページ更新', 'page-update')
            (dist/'editor-profile.json').write_text(json_text(current), encoding='utf-8')
            text = re.sub(r'<script id="editor-profile-metadata"[^>]*>.*?</script>', lambda _: '<script id="editor-profile-metadata" type="application/json">'+json_text(current['page'])+'</script>', text, flags=re.S)
            text = re.sub(r'<p class="page-update">.*?</p>', '', text, flags=re.S)
            text = text.replace('</main>', stamp(date, 'ページ更新', 'page-update')+'</main>', 1)
        page.write_text(text, encoding='utf-8')
        changed[payload['url']] = date
    registry_file.write_text(prefix+json_text(registry)+';\n', encoding='utf-8')
    footer = stamp(site['dateModified'], 'サイト最終更新', 'site-update')
    for page in dist.rglob('*.html'):
        text = page.read_text(encoding='utf-8')
        if '</footer>' not in text:
            continue  # Redirect/error shells are not rendered site pages.
        text = re.sub(r'<p class="site-update">.*?</p>', '', text, flags=re.S)
        page.write_text(text.replace('</footer>', footer+'</footer>', 1), encoding='utf-8')
    sitemap = dist/'sitemap.xml'
    if sitemap.is_file():
        ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
        ET.register_namespace('', ns)
        ET.register_namespace('image', 'http://www.google.com/schemas/sitemap-image/1.1')
        tree = ET.parse(sitemap)
        for node in tree.getroot():
            loc = node.find('{'+ns+'}loc')
            if loc is not None and loc.text in changed:
                last = node.find('{'+ns+'}lastmod')
                if last is None:
                    last = ET.SubElement(node, '{'+ns+'}lastmod')
                last.text = changed[loc.text]
        tree.write(sitemap, encoding='utf-8', xml_declaration=True)
    record = {'site': site, 'profile': profile, 'basis': 'actual production Git changes; not build/deployment time', 'timezone': 'Asia/Tokyo'}
    (dist/'site-updated.json').write_text(json_text(record), encoding='utf-8')
    return record
