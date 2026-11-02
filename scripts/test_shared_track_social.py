import unittest,tempfile,sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from brand_assets import retire_track_social_images
class RetireTrackSocial(unittest.TestCase):
 def test_missing_replacement_preserves_old(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'og').mkdir();old=p/'og/x.jpg';old.write_bytes(b'old')
   with self.assertRaises(FileNotFoundError):retire_track_social_images(p)
   self.assertEqual(old.read_bytes(),b'old')
 def test_wrong_replacement_preserves_old(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'og').mkdir();old=p/'og/x.jpg';old.write_bytes(b'old');Image.new('RGB',(10,10)).save(p/'og-image.jpg')
   with self.assertRaises(AssertionError):retire_track_social_images(p)
   self.assertTrue(old.exists())
 def test_only_generated_track_cards_removed_and_idempotent(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'og').mkdir();Image.new('RGB',(1200,630)).save(p/'og-image.jpg')
   for n in ['x.jpg','x.png']:(p/'og'/n).write_bytes(b'old')
   protected=[p/'og/keep.txt',p/'assets/graffiti/x.png',p/'feature-og/x.jpg']
   for f in protected:f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b'keep')
   retire_track_social_images(p);retire_track_social_images(p)
   self.assertFalse(list((p/'og').glob('*.jpg')));self.assertFalse(list((p/'og').glob('*.png')))
   for f in protected:self.assertEqual(f.read_bytes(),b'keep')
 def test_symlink_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td);(p/'protected').mkdir();(p/'og').symlink_to(p/'protected',target_is_directory=True);Image.new('RGB',(1200,630)).save(p/'og-image.jpg')
   with self.assertRaises(ValueError):retire_track_social_images(p)
if __name__=='__main__':unittest.main()
