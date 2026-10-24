"""The standard is visible ink, not a square file's CSS dimensions."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from artwork_display import measure, normalize, validate, assert_normalized, fitted_ink, sha256

class ArtworkDisplayTests(unittest.TestCase):
    def make_image(self,path,size=(1200,1200),box=(200,400,1000,800)):
        im=Image.new('RGBA',size,(0,0,0,0));im.paste((120,80,200,255),box)
        # Invisible encoding residue must not make a small tag appear full-bleed.
        im.putpixel((1,1),(255,255,255,1));im.save(path)
        return im
    def test_square_padding_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            im=self.make_image(Path(d)/'source.png')
            self.assertEqual(measure(im)['visibleBox'],[200,400,1000,800])
            with self.assertRaises(ValueError):assert_normalized(measure(im))
    def test_normalization_preserves_pixels_source_and_contain_safety(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);source=p/'source.png';old=self.make_image(source);pin=sha256(source)
            report=normalize(source,p/'normalized.webp')
            self.assertEqual(pin,sha256(source));self.assertFalse(report['pixelsRescaled'])
            with Image.open(p/'normalized.webp') as im: new=im.convert('RGBA')
            m=assert_normalized(measure(new));x,y,r,b=m['visibleBox']
            self.assertEqual(new.crop((x,y,r,b)).tobytes(),old.crop((200,400,1000,800)).tobytes())
            for bw,bh in [(580,460),(320,240),(884,464),(366,364),(240,240)]:
                ink=fitted_ink(m,bw,bh)
                ideal=min(bw/m['visibleWidth'],bh/m['visibleHeight'])
                actual=min(ink[0]/m['visibleWidth'],ink[1]/m['visibleHeight'])
                self.assertGreaterEqual(actual/ideal,.855)
                self.assertLessEqual(actual/ideal,.861)
                self.assertLess(ink[0],bw);self.assertLess(ink[1],bh)
    def test_tall_art_keeps_aspect_and_is_height_limited(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make_image(p/'tall.png',box=(500,100,700,1100))
            r=normalize(p/'tall.png',p/'out.webp')
            self.assertAlmostEqual(r['after']['visibleWidth']/r['after']['visibleHeight'],.2)
            w,h=fitted_ink(r['after'],580,460)
            self.assertLess(w,100);self.assertGreater(h,390)
    def test_source_overwrite_and_empty_art_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'source.png';self.make_image(p)
            with self.assertRaises(ValueError):normalize(p,p)
            with self.assertRaises(ValueError):measure(Image.new('RGBA',(64,64)))
    def test_legacy_is_exact_and_new_or_changed_images_require_policy(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);self.make_image(p/'source.png')
            row={'id':'old','image':'source.png','status':'ready'}
            (p/'graffiti_artwork.json').write_text(json.dumps({'tracks':[row]}))
            (p/'artwork_display_legacy.json').write_text(json.dumps({'version':1,'unchangedLegacy':{'old':{'image':'source.png','sha256':sha256(p/'source.png')}}}))
            self.assertEqual(validate(p)['unchangedLegacyCount'],1)
            with Image.open(p/'source.png') as original: changed=original.convert('RGBA')
            changed.putpixel((500,500),(50,60,70,255));changed.save(p/'source.png')
            with self.assertRaises(ValueError):validate(p)  # Same ID/path, changed bytes lose exemption.
            row['id']='new';(p/'graffiti_artwork.json').write_text(json.dumps({'tracks':[row]}))
            with self.assertRaises(ValueError):validate(p)
            report=normalize(p/'source.png',p/'out.webp');row.update(image='out.webp',displaySizing={'version':1,'visibleBox':report['after']['visibleBox'],'outputSha256':report['outputSha256']})
            (p/'graffiti_artwork.json').write_text(json.dumps({'tracks':[row]}))
            self.assertEqual(len(validate(p)['normalized']),1)
            row['displaySizing']['visibleBox']=[0,0,1,1];(p/'graffiti_artwork.json').write_text(json.dumps({'tracks':[row]}))
            with self.assertRaises(ValueError):validate(p)

if __name__=='__main__':unittest.main()
