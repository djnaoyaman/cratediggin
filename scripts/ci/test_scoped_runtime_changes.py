"""Exact render-only coverage cannot narrow any other source delta."""
import copy,hashlib,json
from pathlib import Path
import unittest,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
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
 def test_brand_assets_are_explicit_and_unknown_assets_block(self):
  m=json.loads((HERE/'manifest.json').read_text())
  for path in ['brand/identity/apple-180.png','brand/identity/install-512.png','brand/identity/favicon-192.png','brand/identity/social-1200.jpg']:
   for status in ('A','M','D'):
    change=dict(status=status,old_path=None if status=='A' else path,new_path=None if status=='D' else path)
    p=s.select_changes(m,[change]);self.assertFalse(p['blockers']);self.assertIn('brand-identity',{c['id'] for c in p['selected']})
  p=s.select_changes(m,[dict(status='R100',old_path='brand/identity/apple-180.png',new_path='brand/unknown.png')]);self.assertTrue(p['blockers'])
 def test_brand_source_pairs_select_only_direct_brand_group(self):
  m=json.loads((HERE/'manifest.json').read_text());root=HERE.parents[1]
  f=json.loads((root/'scripts/fixtures/approved-brand-identity.json').read_text())
  for path in ('brand_assets.py','build.py','discovery.py'):
   # Brand scope is historical after the later image-alt-only correction.
   from approved_image_alt import historical_image_alt_file
   after=historical_image_alt_file(path,(root/path).read_bytes())
   p=s.select_changes(m,[dict(status='M',old_path=path,new_path=path)],lambda _:f['files'][path]['before'].encode(),lambda _:after)
   self.assertFalse(p['blockers']);self.assertEqual({c['id'] for c in p['selected']},set(m['groups']['brand_identity']))
 def test_album_recovery_exact_pair_and_drift(self):
  m=json.loads((HERE/'manifest.json').read_text());root=HERE.parents[1];path='src/app/album-player.js'
  f=json.loads((root/'scripts/fixtures/approved-album-recovery.json').read_text())['files'][path]
  before=f['before'].encode();after=(root/path).read_bytes();change=[dict(status='M',old_path=path,new_path=path)]
  p=s.select_changes(m,change,lambda _:before,lambda _:after)
  self.assertEqual({c['id'] for c in p['selected']},set(m['groups']['album_recovery']))
  for a,b in [(before+b' ',after),(before,after+b' '),(None,after),(before,None),(after,before)]:
   q=s.select_changes(m,change,lambda _:a,lambda _:b)
   self.assertTrue(set().union(*(set(m['groups'][g]) for g in m['runtime_rules'][path]))<={c['id'] for c in q['selected']})
 def test_album_bootstrap_exact_pair_and_drift(self):
  m=json.loads((HERE/'manifest.json').read_text());root=HERE.parents[1];path='src/app/player.js'
  f=json.loads((root/'scripts/fixtures/approved-album-bootstrap.json').read_text())['files'][path]
  from approved_person_queue import historical_person_queue_file
  before=f['before'].encode();after=historical_person_queue_file(path,(root/path).read_bytes());change=[dict(status='M',old_path=path,new_path=path)]
  p=s.select_changes(m,change,lambda _:before,lambda _:after)
  self.assertEqual({c['id'] for c in p['selected']},set(m['groups']['album_bootstrap']))
  for a,b in [(before+b' ',after),(before,after+b' '),(None,after),(before,None),(after,before)]:
   q=s.select_changes(m,change,lambda _:a,lambda _:b)
   self.assertTrue(set().union(*(set(m['groups'][g]) for g in m['runtime_rules'][path]))<={c['id'] for c in q['selected']})
 def test_person_queue_exact_pair_and_drift(self):
  m=json.loads((HERE/'manifest.json').read_text());root=HERE.parents[1]
  from approved_editor_polite import historical_editor_polite_file
  f=json.loads((root/'scripts/fixtures/approved-person-queue.json').read_text())['files']
  for path in ['src/app/player.js','src/app/editorial.js']:
   before=f[path]['before'].encode();after=historical_editor_polite_file(path,(root/path).read_bytes());change=[dict(status='M',old_path=path,new_path=path)]
   p=s.select_changes(m,change,lambda _:before,lambda _:after)
   self.assertFalse(p['blockers']);self.assertEqual({c['id'] for c in p['selected']},set(m['groups']['person_queue']))
   for a,b in [(before+b' ',after),(before,after+b' '),(None,after),(before,None),(after,before)]:
    q=s.select_changes(m,change,lambda _:a,lambda _:b)
    self.assertTrue(set().union(*(set(m['groups'][g]) for g in m['runtime_rules'][path]))<={c['id'] for c in q['selected']})
if __name__=='__main__':unittest.main()
