"""Visible-ink sizing for authored tag art. Builds validate; only the CLI normalizes.

The source image is never overwritten. Letter pixels are neither resized nor redrawn.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
from PIL import Image

POLICY_VERSION = 1
ALPHA_THRESHOLD = 8
PADDING_FRACTION = .07


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measure(image):
    rgba = image.convert('RGBA')
    alpha = rgba.getchannel('A')
    box = alpha.point(lambda n: 255 if n >= ALPHA_THRESHOLD else 0).getbbox()
    if box is None:
        raise ValueError('No visible tag artwork')
    width, height = rgba.size
    left, top, right, bottom = box
    return {'width': width, 'height': height, 'visibleBox': list(box),
            'visibleWidth': right-left, 'visibleHeight': bottom-top,
            'margins': [left/width, top/height, (width-right)/width, (height-bottom)/height],
            'alphaThreshold': ALPHA_THRESHOLD}


def fitted_ink(metrics, box_width, box_height):
    scale = min(box_width/metrics['width'], box_height/metrics['height'])
    return [metrics['visibleWidth']*scale, metrics['visibleHeight']*scale]


def assert_normalized(metrics):
    # One pixel rounding allowance. Both axes need padding: a square canvas with
    # a small horizontal tag must not pass merely because its width looks large.
    tolerance = 1 / min(metrics['width'], metrics['height'])
    if not all(PADDING_FRACTION-tolerance <= n <= PADDING_FRACTION+tolerance for n in metrics['margins']):
        raise ValueError('Tag art needs 7% transparent padding on each visible-ink edge')
    return metrics


def normalize(source, destination):
    source, destination = Path(source), Path(destination)
    if source.resolve() == destination.resolve():
        raise ValueError('Keep the authored source; choose a new output path')
    with Image.open(source) as opened:
        opened.load()
        if 'A' not in opened.getbands():
            raise ValueError('Tag art needs a real alpha channel')
        original = opened.convert('RGBA')
    before = measure(original)
    left, top, right, bottom = before['visibleBox']
    # p/(1-2p) padding around content gives p of the final canvas on each edge.
    px = math.ceil((right-left)*PADDING_FRACTION/(1-2*PADDING_FRACTION))
    py = math.ceil((bottom-top)*PADDING_FRACTION/(1-2*PADDING_FRACTION))
    crop = [left-px, top-py, right+px, bottom+py]
    result = original.crop(crop)
    after = assert_normalized(measure(result))
    # The complete visible bbox, including paint and artist/edition text, survives.
    assert result.crop((px, py, px+right-left, py+bottom-top)).tobytes() == original.crop((left,top,right,bottom)).tobytes()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name+'.tmp')
    result.save(temp, format='WEBP', lossless=True, exact=True, method=6)
    with Image.open(temp) as checked:
        checked.load()
        assert checked.convert('RGBA').tobytes() == result.tobytes()
    temp.replace(destination)
    return {'version': POLICY_VERSION, 'sourceImage': source.as_posix(),
            'sourceSha256': sha256(source), 'outputSha256': sha256(destination),
            'cropBox': crop, 'before': before, 'after': after,
            'pixelsRescaled': False, 'visiblePixelsPreserved': True,
            'note': 'Canvas-only normalization; alpha below 8 outside the padded crop is non-visible encoding residue. Authored source retained.'}


def validate(root):
    root = Path(root)
    manifest = json.loads((root/'graffiti_artwork.json').read_text(encoding='utf-8'))
    baseline = json.loads((root/'artwork_display_legacy.json').read_text(encoding='utf-8'))
    assert baseline['version'] == POLICY_VERSION
    legacy = baseline['unchangedLegacy']
    checked, grandfathered = [], []
    for row in manifest['tracks']:
        if row.get('status') != 'ready':
            continue
        identifier, image = row['id'], row['image']
        path = root/image
        pin = {'image': image, 'sha256': sha256(path)}
        if legacy.get(identifier) == pin:
            grandfathered.append(identifier)
            continue
        # New tracks or changed images cannot silently inherit the old exemption.
        sizing = row.get('displaySizing', {})
        if sizing.get('version') != POLICY_VERSION:
            raise ValueError('New/changed tag art lacks displaySizing v1: '+identifier)
        if sizing.get('outputSha256') != pin['sha256']:
            raise ValueError('Tag art display hash changed: '+identifier)
        with Image.open(path) as im:
            im.load()
            if 'A' not in im.getbands():
                raise ValueError('Tag art is not transparent: '+identifier)
            metrics = assert_normalized(measure(im))
        if sizing.get('visibleBox') != metrics['visibleBox']:
            raise ValueError('Stale visible bounds: '+identifier)
        checked.append({'id':identifier, **metrics})
    return {'version': POLICY_VERSION, 'normalized': checked,
            'unchangedLegacyCount': len(grandfathered)}


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='command',required=True)
    norm=sub.add_parser('normalize');norm.add_argument('source');norm.add_argument('destination');norm.add_argument('--report')
    val=sub.add_parser('validate');val.add_argument('--root',default=Path(__file__).parent)
    args=parser.parse_args()
    result=normalize(args.source,args.destination) if args.command=='normalize' else validate(args.root)
    text=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if getattr(args,'report',None):Path(args.report).write_text(text,encoding='utf-8')
    print(text)

if __name__=='__main__':main()
