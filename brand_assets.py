"""Reproducible brand assets using the hero's original condensed typography."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import base64, math
ROOT=Path(__file__).parent
BLUE='#006cb6';WHITE='#ffffff';INK='#101114'
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

def social_image(track=None):
    im=Image.new('RGB',(1200,630),BLUE);d=ImageDraw.Draw(im)
    text(im,(45,31),'RECORDS. RHYMES. RECOLLECTIONS.',24)
    text(im,(946,31),'VOL. 001',24)
    text(im,(45,100),'CRATE',215,width=750)
    text(im,(45,298),'DIGGIN’',215,width=750)
    text(im,(886,103),'KEEP',43,marker=True)
    text(im,(875,160),'DIGGIN’.',43,width=285,marker=True)
    vinyl(im,1004,307,72)
    text(im,(913,402),'THE PAST',22)
    text(im,(913,431),'IS STILL PLAYING.',22)
    d.line((45,503,1155,503),fill='#8dc9ed',width=2)
    if track:
        text(im,(45,526),track['title'],44,width=820)
        text(im,(45,580),track['artist'],23,width=820)
        text(im,(895,555),'DJ NAOYAMAN',25)
    else:
        text(im,(45,527),'A Guide to Sampled Mind',35)
        text(im,(45,572),'& Vintage Grooves',35)
        text(im,(889,549),'DJ NAOYAMAN',26)
    return im

def write_icons(dist):
    for size,name in [(180,'apple-touch-icon.png'),(180,'apple-touch-icon-vinyl.png'),(32,'favicon-32.png'),(192,'icon-192.png'),(512,'icon-512.png')]:icon(size).save(dist/name)
    icon(48).save(dist/'favicon.ico',sizes=[(16,16),(32,32),(48,48)])
    import io
    data=io.BytesIO();icon(48).save(data,format='PNG')
    encoded=base64.b64encode(data.getvalue()).decode()
    (dist/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192"><image width="192" height="192" href="data:image/png;base64,'+encoded+'"/></svg>', encoding='utf-8')
