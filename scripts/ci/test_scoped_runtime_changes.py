"""Exact render-only coverage cannot narrow any other source delta."""
import copy,hashlib,json
from pathlib import Path
import unittest
import select_checks as s
HERE=Path(__file__).resolve().parent
class ScopedRuntimeTests(unittest.TestCase):
 def setUp(self):
  self.m=json.loads((HERE/'manifest.json').read_text());self.before=b'old render';self.after=b'new render';self.path='frontend.py'
  self.m['scoped_runtime_changes']={self.path:[{'before_sha256':hashlib.sha256(self.before).hexdigest(),'after_sha256':hashlib.sha256(self.after).hexdigest(),'groups':['static_work_count']}]}
 def plan(self,before,after,extra=()):
  return s.select_changes(self.m,[dict(status='M',old_path=p,new_path=p) for p in (self.path,*extra)],before,after)
 def test_exact_pair_only_selects_count(self):
  p=self.plan(lambda _:self.before,lambda _:self.after)
  self.assertEqual([c['id'] for c in p['selected']],['static-work-count']);self.assertTrue(p['build_required']);self.assertFalse(p['browser_required'])
 def test_changed_missing_reversed_bytes_keep_broad_groups(self):
  for before,after in [(self.before+b' ',self.after),(self.before,self.after+b' '),(None,self.after),(self.before,None),(self.after,self.before)]:
   with self.subTest(before=before,after=after):
    p=self.plan(lambda _:before,lambda _:after)
    self.assertGreater(len(p['selected']),1);self.assertTrue(p['browser_required']);self.assertNotIn('static-work-count',[c['id'] for c in p['selected']])
  p=self.plan(None,None);self.assertTrue(p['browser_required'])
 def test_other_runtime_change_retains_its_dependencies(self):
  p=self.plan(lambda path:self.before if path==self.path else b'old',lambda path:self.after if path==self.path else b'new',['src/app/core.js'])
  ids={c['id'] for c in p['selected']};self.assertIn('static-work-count',ids)
  for group in self.m['runtime_rules']['src/app/core.js']:self.assertTrue(set(self.m['groups'][group])<=ids)
 def test_old_new_scope_union_and_invalid_scope(self):
  newer=copy.deepcopy(self.m);newer['scoped_runtime_changes']={}
  merged=s.merge_manifests(self.m,newer);self.assertEqual(merged['scoped_runtime_changes'],self.m['scoped_runtime_changes'])
  for path in ('tracks.json','unmapped.py'):
   bad=copy.deepcopy(self.m);bad['scoped_runtime_changes'][path]=bad['scoped_runtime_changes'].pop(self.path)
   with self.assertRaises(s.SelectionError):s.validate_manifest(bad,(HERE/'bootstrap-pages.yml').read_bytes())
if __name__=='__main__':unittest.main()
