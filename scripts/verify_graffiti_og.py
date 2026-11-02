"""Validate shared track previews and retained feature/profile social cards."""
from pathlib import Path
from PIL import Image
from urllib.parse import urlparse
import json, re, runpy
root=Path(__file__).resolve().parents[1];dist=root/'dist'
runpy.run_path(str(Path(__file__).with_name('verify_shared_track_social.py')), run_name='__main__')
registry=json.loads((dist/'metadata.js').read_text().split('=',1)[1].strip().removesuffix(';'))
# Every generic/profile social card also uses JPEG, while PNG application icons remain PNG.
expected_count=len(json.loads((root/'features.json').read_text())['features'])+2
jpgs=list((dist/'og').glob('*.jpg'))+list((dist/'feature-og').glob('*.jpg'))+[dist/'og-image.jpg',dist/'editor-og.jpg']
assert len(jpgs)==expected_count
assert not list((dist/'og').glob('*.png')) and not list((dist/'feature-og').glob('*.png')) and not (dist/'og-image.png').exists()
for path in jpgs:
    with Image.open(path) as im:im.load();assert im.format=='JPEG' and im.size==(1200,630)
for page in registry.values():
    assert urlparse(page['image']).path.endswith('.jpg')
    image_path=dist/urlparse(page['image']).path.removeprefix('/cratediggin/')
    assert image_path.is_file()
for path in dist.rglob('*'):
    if path.suffix not in ('.html','.js','.json','.xml','.txt','.md'):continue
    text=path.read_text()
    assert not re.search(r'(?:og-image|(?:feature-og|og)/[^\s\"<>?]+)\.png(?:[?\"<\s]|$)',text),path
print(f'All {expected_count} social JPEG URLs resolve; no retired SNS PNG references/files remain')

# A missing replacement must never retire a previous image. A valid one gets an exact backup first.
import tempfile, hashlib
from brand_assets import retire_legacy_social_pngs
with tempfile.TemporaryDirectory() as folder:
    test=Path(folder);old=test/'og-image.png';original=Image.new('RGB',(1200,630),'white');original.save(old)
    before=old.read_bytes()
    try:retire_legacy_social_pngs(test,[],[])
    except FileNotFoundError:pass
    else:raise AssertionError('Missing JPEG should abort retirement')
    assert old.read_bytes()==before
    original.save(test/'og-image.jpg',format='JPEG',quality=95,subsampling=0,optimize=True)
    icon=test/'icon-192.png';icon.write_bytes(before)
    retire_legacy_social_pngs(test,[],[])
    backup=Path(tempfile.gettempdir())/'cratediggin-ogp-png-backup'/hashlib.sha256(before).hexdigest()/'og-image.png'
    assert backup.read_bytes()==before and not old.exists() and icon.read_bytes()==before
print('Retirement is replacement-validated, backed up exactly, and limited to SNS derivatives')
