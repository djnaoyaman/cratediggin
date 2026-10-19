"""Verify delivered derivatives without weakening original artwork protection."""
import hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]; dist=root/'dist'
report=json.loads((dist/'image-delivery.json').read_text()); rows=report['images']
sha=lambda b:hashlib.sha256(b).hexdigest()
paths={p.relative_to(dist).as_posix() for p in dist.rglob('*') if p.suffix.lower() in {'.png','.jpg','.jpeg','.webp','.gif'}}
assert paths=={r['path'] for r in rows};assert len(rows)==len(paths)
resized=[]; source_count=0
for r in rows:
 p=dist/r['path'];assert sha(p.read_bytes())==r['outputSha256'];assert p.stat().st_size==r['outputBytes']
 with Image.open(p) as im:
  assert im.width<=2400 and im.size==(r['width'],r['height'])
  assert sha(im.convert('RGBA').tobytes())==r['outputPixelSha256']
 assert r['width']<=r['inputWidth']
 assert r['outputBytes']<=r['inputBytes'],r['path']
 if r['resized']:
  assert r['inputWidth']>2400 and r['width']==2400
  assert abs(r['height']-r['inputHeight']*2400/r['inputWidth'])<=.5
  resized.append(r['path'])
 else:
  assert r['losslessPixels'] and r['inputPixelSha256']==r['outputPixelSha256']
  assert r['outputBytes']<=r['inputBytes']
 source=(root/r['path']) if r['path'].startswith('assets/') else root/'src'/'assets'/r['path']
 if source.exists():
  source_count+=1
  assert sha(source.read_bytes())==r['inputSha256'],'Original source mismatch: '+str(source)
# All five formerly oversized producer/artist photos are explicitly retired.
assert not resized,resized
assert source_count>=520,source_count
assert report['outputBytes']<=report['inputBytes']
print(f"All {len(rows)} delivered images <=2400px; {len(resized)} proportional derivatives; all other decoded pixels preserved; original source bytes verified")
