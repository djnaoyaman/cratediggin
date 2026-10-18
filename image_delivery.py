"""Optimize delivery copies only; authored originals remain immutable."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from io import BytesIO
import hashlib
import json
import tempfile
from PIL import Image

POLICY = 'v2-max2400-lossless-under-cap-photo90to94'
LOSSLESS_CACHE_POLICY = 'v1-max2400-lossless-under-cap-photo94'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def optimize_images(dist):
    cache = Path(tempfile.gettempdir()) / 'cratediggin-image-delivery-cache'
    cache.mkdir(exist_ok=True)
    paths = sorted(p for p in dist.rglob('*') if p.suffix.lower() in {'.png', '.webp', '.jpg', '.jpeg', '.gif'})

    def one(path):
        original = path.read_bytes()
        with Image.open(BytesIO(original)) as header:
            cache_policy = POLICY if header.width > 2400 else LOSSLESS_CACHE_POLICY
        key = digest(original + cache_policy.encode())
        cached, record = cache / key, cache / (key + '.json')
        if cached.exists() and record.exists():
            meta = json.loads(record.read_text())
            output = cached.read_bytes()
            assert digest(output) == meta['outputSha256']
        else:
            with Image.open(BytesIO(original)) as source:
                source.load()
                width, height = source.size
                fmt = source.format
                rgba = source.convert('RGBA')
                resized = width > 2400
                target = source.copy()
                if resized:
                    target = target.resize((2400, max(1, round(height * 2400 / width))), Image.Resampling.LANCZOS)
                output = original
                encoded = BytesIO()
                if fmt == 'PNG':
                    target.save(encoded, format='PNG', optimize=True, compress_level=9, icc_profile=source.info.get('icc_profile'))
                elif fmt == 'WEBP':
                    if resized:
                        for quality in (94, 92, 90):
                            encoded = BytesIO()
                            target.save(encoded, format='WEBP', quality=quality, method=6, exact=True, icc_profile=source.info.get('icc_profile'))
                            if len(encoded.getvalue()) <= len(original):
                                break
                    else:
                        target.save(encoded, format='WEBP', lossless=True, method=6, exact=True, icc_profile=source.info.get('icc_profile'))
                elif resized and fmt == 'JPEG':
                    target.convert('RGB').save(encoded, format='JPEG', quality=94, optimize=True, subsampling=0, icc_profile=source.info.get('icc_profile'))
                elif resized:
                    raise AssertionError('Unsupported oversized delivery image: ' + str(path))
                candidate = encoded.getvalue()
                if candidate and (resized or len(candidate) < len(original)):
                    output = candidate
                with Image.open(BytesIO(output)) as delivered:
                    delivered.load()
                    out_rgba = delivered.convert('RGBA')
                    assert delivered.width <= 2400
                    if not resized:
                        assert delivered.size == source.size
                        assert out_rgba.tobytes() == rgba.tobytes(), 'Lossless pixel preservation failed: ' + str(path)
                    assert delivered.width <= width, 'Never upscale'
                    meta = {'inputSha256': digest(original), 'outputSha256': digest(output),
                            'inputBytes': len(original), 'outputBytes': len(output),
                            'inputWidth': width, 'inputHeight': height,
                            'width': delivered.width, 'height': delivered.height,
                            'resized': resized, 'losslessPixels': not resized,
                            'inputPixelSha256': digest(rgba.tobytes()),
                            'outputPixelSha256': digest(out_rgba.tobytes())}
                cached.write_bytes(output)
                record.write_text(json.dumps(meta))
        path.write_bytes(output)
        return {'path': path.relative_to(dist).as_posix(), **meta}

    with ThreadPoolExecutor(max_workers=1) as pool:
        entries = list(pool.map(one, paths))
    report = {'policy': POLICY, 'maxWidth': 2400, 'images': entries,
              'inputBytes': sum(x['inputBytes'] for x in entries),
              'outputBytes': sum(x['outputBytes'] for x in entries)}
    (dist / 'image-delivery.json').write_text(json.dumps(report, ensure_ascii=False, separators=(',', ':')) + '\n')
    print('Image delivery:', len(entries), 'files;', report['inputBytes'], '→', report['outputBytes'], 'bytes; originals unchanged')
    return report

if __name__ == "__main__":
    import sys
    optimize_images(Path(sys.argv[1]))
