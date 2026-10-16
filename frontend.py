"""Build browser assets exclusively from source, never from previous output."""
import json
import shutil


def build_frontend(root, dist, features, policy, guides):
    dist.mkdir(parents=True, exist_ok=True)
    for asset in (root / 'src' / 'assets').iterdir():
        if asset.is_file():
            shutil.copyfile(asset, dist / asset.name)
    source = root / 'src' / 'app'
    order = json.loads((source / 'order.json').read_text(encoding='utf-8'))
    tokens = {
        '{{FEATURES}}': features,
        '{{FEATURE_POLICY}}': policy,
        '{{GUIDES}}': guides,
    }
    client = '\n'.join((source / name).read_text(encoding='utf-8') for name in order)
    for token, data in tokens.items():
        if client.count(token) != 1:
            raise ValueError(f'Expected exactly one frontend token: {token}')
        client = client.replace(token, json.dumps(data, ensure_ascii=False))
    (dist / 'app.js').write_text("'use strict';\n(()=>{\n" + client + '\n})();\n', encoding='utf-8')
    template = (root / 'templates' / 'index.html').read_text(encoding='utf-8')
    (dist / 'index.html').write_text(template, encoding='utf-8')
