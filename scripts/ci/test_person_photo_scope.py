"""Portrait rendering scope is exact; drift cannot suppress direct dependencies."""
import hashlib,json,sys,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
import select_checks as s
class PortraitScope(unittest.TestCase):
 def test_exact_and_drift(self):
  m=json.loads((R/'scripts/ci/manifest.json').read_text());f=json.loads((R/'scripts/fixtures/approved-person-photos.json').read_text())
  for path,c in f['files'].items():
   if path=='releases.json':continue
   old=c['before'].encode();new=(R/path).read_bytes();change=[dict(status='M',old_path=path,new_path=path)]
   plan=s.select_changes(m,change,lambda _:old,lambda _:new)
   self.assertFalse(plan['blockers']);self.assertEqual({x['id'] for x in plan['selected']},set(m['groups']['person_photos']))
   plan=s.select_changes(m,change,lambda _:old,lambda _:new+b' ')
   self.assertTrue(set().union(*(set(m['groups'][g]) for g in m['runtime_rules'][path]))<={x['id'] for x in plan['selected']})
 def test_identity_helper_mapped(self):
  m=json.loads((R/'scripts/ci/manifest.json').read_text())
  p=s.select_changes(m,[dict(status='A',old_path=None,new_path='person_photos.py')]);self.assertFalse(p['blockers']);self.assertTrue(set(m['groups']['person_photos'])<={x['id'] for x in p['selected']})
