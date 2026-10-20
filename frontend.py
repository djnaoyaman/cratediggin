"""Build browser assets exclusively from source, never from previous output."""
import json
import shutil
import os
from urllib.parse import urlparse
from profile_content import render_profile


def render_work_count(template, tracks):
    """Render the no-JavaScript total from the same authored catalog as the client."""
    if template.count('{{WORK_COUNT}}') != 1:
        raise ValueError('Expected exactly one WORK_COUNT template token')
    if not isinstance(tracks, list):
        raise ValueError('Catalog must be a list')
    return template.replace('{{WORK_COUNT}}', str(len(tracks)).zfill(2))


def build_frontend(root, dist, features, policy, guides):
    dist.mkdir(parents=True, exist_ok=True)
    retired=json.loads((root/'retired_feature_photos.json').read_text())['paths']
    assert len(retired)==13 and all('/' not in name and name.startswith('feature-') for name in retired)
    for name in retired:
        stale=dist/name
        if stale.exists():stale.unlink()
    for asset in (root / 'src' / 'assets').iterdir():
        if asset.is_file() and asset.name not in retired:
            shutil.copyfile(asset, dist / asset.name)
    source = root / 'src' / 'app'
    order = json.loads((source / 'order.json').read_text(encoding='utf-8'))
    tokens = {
        '{{FEATURES}}': features,
        '{{FEATURE_POLICY}}': policy,
        '{{GUIDES}}': guides,
        '{{EDITOR_PROFILE}}': render_profile(root,urlparse(os.environ.get('SITE_URL','https://djnaoyaman.github.io/cratediggin')).path.rstrip('/')),
    }
    client = '\n'.join((source / name).read_text(encoding='utf-8') for name in order)
    for token, data in tokens.items():
        if client.count(token) != 1:
            raise ValueError(f'Expected exactly one frontend token: {token}')
        client = client.replace(token, json.dumps(data, ensure_ascii=False))
    (dist / 'app.js').write_text("'use strict';\n(()=>{\n" + client + '\n})();\n', encoding='utf-8')
    template = (root / 'templates' / 'index.html').read_text(encoding='utf-8')
    template = render_work_count(template, json.loads((root / 'tracks.json').read_text(encoding='utf-8')))
    (dist / 'index.html').write_text(template, encoding='utf-8')
