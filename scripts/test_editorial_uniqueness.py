import unittest
from editorial_uniqueness import duplicates,new_violations,neighbors,sha

def row(owner,text,path='essayTitle',entities=None,role='headline'):
 return {'owner':owner,'path':path,'text':text,'entities':entities or [],'role':role}
class EditorialUniqueness(unittest.TestCase):
 def test_exact_headline_cross_work(self):self.assertTrue(duplicates([row('a','固有の発見を書く'),row('b','固有の発見を書く')]))
 def test_unicode_punctuation_invisible(self):self.assertTrue(duplicates([row('a','ＡＢＣ、の発見。'),row('b','ABC\u200b の発見!')]))
 def test_same_work_projection_is_not_duplicate(self):self.assertFalse(duplicates([row('a','固有の発見を書く'),row('a','固有の発見を書く','home')]))
 def test_entity_template(self):
  d=duplicates([row('a','Alphaの声を追えば、新しい景色が見えてくる。','essay.0',['Alpha'],'body'),row('b','Betaの声を追えば、新しい景色が見えてくる。','essay.0',['Beta'],'body')]);self.assertTrue(any(k.startswith('template:') for k in d))
 def test_shared_sentence_in_unique_paragraph(self):
  common='題名を覚えたあとにもう一度戻ると、声の置かれ方が気になってくる。'
  d=duplicates([row('a','最初の別の入口。'+common,'essay.0',role='body'),row('b','二つ目の異なる入口。'+common,'essay.0',role='body')]);self.assertTrue(d)
 def test_legacy_debt_can_shrink_not_grow(self):
  base=duplicates([row('a','同じ発見を繰り返す'),row('b','同じ発見を繰り返す')]);self.assertFalse(new_violations({},base));self.assertTrue(new_violations(duplicates([row('a','同じ発見を繰り返す'),row('b','同じ発見を繰り返す'),row('c','同じ発見を繰り返す')]),base))
 def test_semantic_counterexample_is_reviewed_despite_low_score(self):
  r=[row('electric','四拍子の上を、三小節で巡る。'),row('lyrics','四拍子の上で、三小節のループが景色をずらす。'),row('other','前座を迎える姿勢が変わる。')]
  self.assertFalse(duplicates(r),'Exact uniqueness does not imply distinct meaning')
  n=neighbors(r,{'electric'});self.assertEqual(n[0]['neighbor'],'lyrics');self.assertLess(n[0]['trigramJaccard'],.65)
 def test_changed_copy_invalidates_review_hash(self):self.assertNotEqual(sha('旧原稿'),sha('新原稿'))
if __name__=='__main__':unittest.main()
