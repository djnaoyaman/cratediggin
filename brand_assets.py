"""Reproducible brand assets using the hero's original condensed typography."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, math, hashlib, shutil, tempfile
ROOT=Path(__file__).parent
BLUE='#4169e1';WHITE='#ffffff';INK='#141b2d'
SOCIAL_WALL='#687180';SOCIAL_WALL_LIGHT='#6a7382';SOCIAL_WALL_DARK='#666f7e';SOCIAL_PAPER='#e8edf6'
def font(size,marker=False):
    return ImageFont.truetype(str(ROOT/'brand'/('PermanentMarker-Regular.ttf' if marker else 'BarlowCondensed-ExtraBold.ttf')),size)
def text(im,xy,value,size,width=None,marker=False,fill=WHITE):
    f=font(size,marker); d=ImageDraw.Draw(im)
    while width and d.textlength(value,font=f)>width:f=font(f.size-1,marker)
    box=d.textbbox((0,0),value,font=f)
    d.text((xy[0],xy[1]-box[1]),value,font=f,fill=fill)
def vinyl(im,cx,cy,r):
    d=ImageDraw.Draw(im)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=INK)
    for radius in range(int(r)-3,int(r*.4),-6):
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline='#303238',width=2)
    lr=r*.37;d.ellipse((cx-lr,cy-lr,cx+lr,cy+lr),fill=WHITE)
    # The same off-centre scratch cue sticker as the animated record.
    d.rectangle((cx-r*.10,cy-r*.94,cx+r*.10,cy-r*.32),fill=WHITE)
    text(im,(cx-lr*.78,cy-lr*.32),'33 1/3',int(r*.32),width=lr*1.56,fill=BLUE)
    d.ellipse((cx-2,cy-2,cx+2,cy+2),fill=INK)
def icon(size):
    """Use the supplied original record illustration, not a recreated graphic."""
    import io
    encoded=(ROOT/'brand'/'record-art.jpg.base64').read_text(encoding='utf-8').strip()
    original=Image.open(io.BytesIO(base64.b64decode(encoded))).convert('RGB')
    return original.resize((size,size),Image.Resampling.LANCZOS)

def graffiti_social_image(track):
    """Lay out an unchanged transparent artwork over a restrained cool wall; white paint remains distinct."""
    source = ROOT / track['art']['image']
    if not source.is_file():
        raise ValueError(f'Missing approved artwork for social card: {source}')
    im = Image.new('RGB', (1200, 630), SOCIAL_WALL)
    d = ImageDraw.Draw(im)
    for y in range(0, 630, 4):
        d.line((0, y, 1199, y), fill=SOCIAL_WALL_LIGHT)
    for x in range(0, 1200, 7):
        d.line((x, 0, x, 629), fill=SOCIAL_WALL_DARK)
    text(im, (48, 27), "CRATEDIGGIN'", 30)
    text(im, (890, 33), 'DJ NAOYAMAN', 24, width=262)
    artwork = Image.open(source).convert('RGBA')
    artwork.thumbnail((1080, 382), Image.Resampling.LANCZOS)
    im.paste(artwork, ((1200-artwork.width)//2, 82+(382-artwork.height)//2), artwork)
    d.line((48, 489, 1152, 489), fill='#aab2bf', width=1)
    text(im, (48, 508), track['title'], 43, width=1104)
    text(im, (48, 567), track['artist'], 28, width=1104)
    return im

def social_image(track=None):
    if track and track.get('art', {}).get('image'):
        return graffiti_social_image(track)
    im=Image.new('RGB',(1200,630),SOCIAL_PAPER);d=ImageDraw.Draw(im)
    text(im,(45,31),'RECORDS. RHYMES. RECOLLECTIONS.',24,fill=INK)
    text(im,(946,31),'VOL. 001',24,fill=INK)
    text(im,(45,100),'CRATE',215,width=750,fill=INK)
    text(im,(45,298),"DIGGIN'",215,width=750,fill=INK)
    text(im,(886,103),'KEEP',43,marker=True,fill=INK)
    text(im,(875,160),"DIGGIN'.",43,width=285,marker=True,fill=INK)
    vinyl(im,1004,307,72)
    text(im,(913,402),'THE PAST',22,fill=INK)
    text(im,(913,431),'IS STILL PLAYING.',22,fill=INK)
    d.line((45,503,1155,503),fill='#b8c1d1',width=2)
    if track:
        text(im,(45,526),track['title'],44,width=820,fill=INK)
        text(im,(45,580),track['artist'],23,width=820,fill=INK)
        text(im,(895,555),'DJ NAOYAMAN',25,fill=INK)
    else:
        text(im,(45,527),'A Guide to Sampled Mind',35,fill=INK)
        text(im,(45,572),'& Vintage Grooves',35,fill=INK)
        text(im,(889,549),'DJ NAOYAMAN',26,fill=INK)
    return im

def write_icons(dist):
    for size,name in [(180,'apple-touch-icon.png'),(180,'apple-touch-icon-vinyl.png'),(32,'favicon-32.png'),(192,'icon-192.png'),(512,'icon-512.png')]:icon(size).save(dist/name)
    icon(48).save(dist/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
    import io
    data=io.BytesIO();icon(48).save(data,format='PNG')
    encoded=base64.b64encode(data.getvalue()).decode()
    (dist/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><image width="192" height="192" href="data:image/png;base64,'+encoded+'"/></svg>', encoding='utf-8')


def save_social_image(path, track=None):
    """Public SNS derivative: opaque 1200x630 JPEG, quality95 and full chroma."""
    social_image(track).save(path, format='JPEG', quality=95, subsampling=0, optimize=True)


def retire_legacy_social_pngs(dist, track_ids, feature_ids):
    """Retire only backed-up generated SNS PNGs after every replacement decodes."""
    paths = [Path('og-image.jpg')] + [Path('og') / (x+'.jpg') for x in track_ids] + [Path('feature-og') / (x+'.jpg') for x in feature_ids]
    for rel in paths:
        with Image.open(dist/rel) as im:
            im.load()
            assert im.format=='JPEG' and im.mode=='RGB' and im.size==(1200,630), rel
    for rel in paths:
        old = dist/rel.with_suffix('.png')
        if old.exists():
            data=old.read_bytes(); digest=hashlib.sha256(data).hexdigest()
            backup=Path(tempfile.gettempdir())/'cratediggin-ogp-png-backup'/digest/rel.with_suffix('.png')
            backup.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(old,backup)
            assert backup.read_bytes()==data
            old.unlink()


def feature_social_image(source):
    """Contain the complete supplied collage; no face crop or extra painted overlay."""
    im=Image.new('RGB',(1200,630),SOCIAL_PAPER)
    with Image.open(source) as original:
        art=original.convert('RGBA');art.thumbnail((1200,630),Image.Resampling.LANCZOS)
        im.paste(art,((1200-art.width)//2,(630-art.height)//2),art)
    return im

def save_feature_social_image(path,source):
    feature_social_image(source).save(path,format='JPEG',quality=95,subsampling=0,optimize=True)
