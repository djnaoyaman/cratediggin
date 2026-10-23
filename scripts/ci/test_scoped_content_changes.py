from pathlib import Path
import copy,hashlib,json,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import select_checks as s
HERE=Path(__file__).resolve().parent
class ScopedContentTests(unittest.TestCase):
 def setUp(self):
  self.m=json.loads((HERE/'manifest.json').read_text());self.before=b'old';self.after=b'new';self.path='tracks.json'
  self.m['scoped_content_changes']={self.path:[{'before_sha256':hashlib.sha256(self.before).hexdigest(),'after_sha256':hashlib.sha256(self.after).hexdigest(),'groups':['release']}]}
 def plan(self,a,b,path=None,status='M'):
  p=path or self.path
  return s.select_changes(self.m,[{'status':status,'old_path':p if status!='A' else None,'new_path':p if status!='D' else None}],lambda _:a,lambda _:b)
 def test_exact_existing_and_negative_drift(self):
  p=self.plan(self.before,self.after);self.assertFalse(p['blockers']);self.assertTrue(p['build_required'])
  self.assertEqual({x['id'] for x in p['selected']},set(self.m['groups']['release']))
  for a,b in [(self.before+b' ',self.after),(self.before,self.after+b' '),(None,self.after),(self.before,None),(self.after,self.before)]:self.assertTrue(self.plan(a,b)['blockers'])
 def test_exact_new_asset_and_unknown_asset(self):
  p='assets/graffiti/example.webp';self.m['scoped_content_changes'][p]=[{'before_sha256':None,'after_sha256':hashlib.sha256(self.after).hexdigest(),'groups':['release']}]
  self.assertFalse(self.plan(None,self.after,p,'A')['blockers']);self.assertTrue(self.plan(self.before,self.after,p)['blockers'])
  self.assertTrue(self.plan(None,self.after,'assets/graffiti/unmapped.webp','A')['blockers']);self.assertTrue(self.plan(self.after,None,p,'D')['blockers'])
 def test_old_new_union_and_reject_bad_schema(self):
  other=copy.deepcopy(self.m);other['scoped_content_changes']={};self.assertEqual(s.merge_manifests(self.m,other)['scoped_content_changes'],self.m['scoped_content_changes'])
  for path in ['src/app/core.js','unmapped.json']:
   bad=copy.deepcopy(self.m);bad['scoped_content_changes'][path]=bad['scoped_content_changes'].pop('tracks.json')
   with self.assertRaises(s.SelectionError):s.validate_manifest(bad,(HERE/'bootstrap-pages.yml').read_bytes())
  for change in [{'after_sha256':None},{'groups':['unknown']},{'before_sha256':'wrong'}]:
   bad=copy.deepcopy(self.m);bad['scoped_content_changes']['tracks.json'][0].update(change)
   with self.assertRaises(s.SelectionError):s.validate_manifest(bad,(HERE/'bootstrap-pages.yml').read_bytes())
 def test_reviewed_assertion_paths_remain_exact(self):
  for path in ['scripts/approved_example.py','scripts/fixtures/approved-example.json']:
   self.m['scoped_content_changes']={path:[{'before_sha256':hashlib.sha256(self.before).hexdigest(),'after_sha256':hashlib.sha256(self.after).hexdigest(),'groups':['release']}]}
   s.validate_manifest(self.m,(HERE/'bootstrap-pages.yml').read_bytes())
   self.assertFalse(self.plan(self.before,self.after,path)['blockers'])
   self.assertTrue(self.plan(self.before,self.after+b' ',path)['blockers'])
   self.assertTrue(self.plan(self.before+b' ',self.after,path)['blockers'])
  self.m['scoped_content_changes']={}
  self.assertTrue(self.plan(self.before,self.after,'scripts/approved_unmapped.py')['blockers'])
 def test_rename_requires_both_paths(self):
  p=s.select_changes(self.m,[{'status':'R100','old_path':'tracks.json','new_path':'other.json'}],lambda _:self.before,lambda _:self.after)
  self.assertTrue(p['blockers'])
if __name__=='__main__':unittest.main()
