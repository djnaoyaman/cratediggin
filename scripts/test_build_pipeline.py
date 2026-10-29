import json
from pathlib import Path
import tempfile
import unittest
import shutil
import subprocess
from unittest.mock import Mock
import build_pipeline as pipeline


class PipelineTests(unittest.TestCase):
    def setUp(self):
        temporary_root=Path.cwd()/'.pipeline-test-tmp';temporary_root.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=temporary_root);self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.cache=self.root/'.build-cache'
        for name,value in {'editor_profile.json':'{"name":"Author"}','profile_content.py':'# profile','tracks.json':'[]','src/app/core.js':'// player','src/assets/site.css':'body{}','src/assets/photo.webp':'original image','scripts/build_pipeline.py':'# builder'}.items():self.write(name,value)
        self.full=Mock(side_effect=self.seed);self.profile=Mock(side_effect=lambda root:(root/'dist/editor.html').write_text('new profile'))
        self.client=Mock(side_effect=lambda root:(root/'dist/app.js').write_text('// changed client'))

    def write(self,name,value):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value);return p

    def seed(self,root):
        for name,value in {'dist/editor.html':'old profile','dist/app.js':'// app','dist/songs/song.html':'song page','dist/photo.webp':'encoded image','.build-support/frontend.json':'{}'}.items():self.write(name,value)

    def bootstrap(self):
        selected=pipeline.plan(self.root,self.cache);self.assertEqual(selected['mode'],'full')
        pipeline.build(self.root,self.cache,selected,full_runner=self.full,profile_runner=self.profile)
        pipeline.save_cache(self.root,self.cache,selected);self.full.reset_mock();self.profile.reset_mock()

    def test_profile_change_preserves_music_images_and_shared_bundle(self):
        self.bootstrap();before={p:pipeline.digest(self.root/'dist'/p) for p in ['songs/song.html','photo.webp','app.js']}
        self.write('editor_profile.json','{"name":"Updated author"}');selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['stages'],['profile'])
        report=pipeline.build(self.root,self.cache,selected,full_runner=self.full,profile_runner=self.profile)
        self.full.assert_not_called();self.profile.assert_called_once()
        self.assertEqual(report['music_generation'],'not executed');self.assertEqual(report['image_processing'],'not executed')
        self.assertEqual(before,{p:pipeline.digest(self.root/'dist'/p) for p in before})

    def test_client_change_never_calls_music_or_profile_generation(self):
        self.bootstrap();self.write('src/app/core.js','// changed player');selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['stages'],['client'])
        pipeline.build(self.root,self.cache,selected,full_runner=self.full,client_runner=self.client,profile_runner=self.profile)
        self.client.assert_called_once();self.full.assert_not_called();self.profile.assert_not_called()

    def test_css_change_copies_asset_without_image_processing(self):
        self.bootstrap();self.write('src/assets/site.css','body{color:red}');selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['stages'],['assets'])
        pipeline.build(self.root,self.cache,selected,full_runner=self.full,profile_runner=self.profile)
        self.full.assert_not_called();self.profile.assert_not_called();self.assertEqual((self.root/'dist/site.css').read_text(),'body{color:red}')

    def test_music_and_image_inputs_require_full_generation(self):
        for name,value in [('tracks.json','[{"id":"new-song"}]'),('src/assets/photo.webp','new source image')]:
            with self.subTest(path=name):
                self.bootstrap();self.write(name,value);self.assertEqual(pipeline.plan(self.root,self.cache)['mode'],'full')

    def test_corrupt_or_missing_cache_is_never_reused(self):
        self.bootstrap();(self.cache/'site/photo.webp').write_text('tampered')
        self.assertEqual(pipeline.plan(self.root,self.cache)['mode'],'full')

    def test_requested_feature_qa_change_requires_build_and_browser_validation(self):
        self.write('scripts/verify_requested_feature_editorials_browser.cjs','// initial coverage')
        self.bootstrap()
        self.write('scripts/verify_requested_feature_editorials_browser.cjs','// expanded no-JS and card coverage')
        selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['stages'],['full'])
        self.assertTrue(selected['publish'])

    def test_documentation_changes_need_no_build_or_publish(self):
        self.bootstrap();self.write('README.md','new documentation');selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['mode'],'none');self.assertFalse(selected['publish'])

    def test_source_change_after_plan_is_rejected(self):
        self.bootstrap();selected=pipeline.plan(self.root,self.cache);self.write('tracks.json','changed during build')
        with self.assertRaisesRegex(ValueError,'Source changed'):pipeline.build(self.root,self.cache,selected)

    def test_real_profile_builder_changes_only_profile_outputs(self):
        from profile_build import render
        self.write('editor_profile.json','{"name":"Author","realName":"Owner"}')
        self.write('profile_content.py',"import json\ndef render_profile(root,base):\n data=json.loads((root/'editor_profile.json').read_text())\n return '<article class=\"editor-profile\"><h1>'+data['name']+'</h1></article>'\n")
        def full(root):
            self.seed(root)
            self.write('dist/editor.html','<html><head><title>Old</title></head><body><main id="view" tabindex="-1">old</main></body></html>')
        runner=lambda root:render(root,root/'dist',pipeline.HOST)
        selected=pipeline.plan(self.root,self.cache);pipeline.build(self.root,self.cache,selected,full_runner=full,profile_runner=runner);pipeline.save_cache(self.root,self.cache,selected)
        before=pipeline.inventory(self.root/'dist')
        self.write('editor_profile.json','{"name":"Updated author","realName":"Owner"}');selected=pipeline.plan(self.root,self.cache)
        self.assertEqual(selected['mode'],'profile')
        pipeline.build(self.root,self.cache,selected,full_runner=self.full,profile_runner=runner)
        after=pipeline.inventory(self.root/'dist')
        self.assertEqual({p for p in before if before[p]!=after[p]},{'editor.html','editor-profile.json'})
        self.assertEqual(json.loads((self.root/'dist/editor-profile.json').read_text())['page']['title'],'Updated author — 編者紹介 / CRATEDIGGIN’')

    @unittest.skipUnless(shutil.which('node'),'Node executable unavailable')
    def test_about_renderer_survives_profile_bundle_separation(self):
        import importlib.util, sys, types
        from unittest.mock import patch
        repository=Path(__file__).resolve().parents[1]
        self.write('src/app/editorial.js',(repository/'src/app/editorial.js').read_text(encoding='utf-8'))
        self.write('releases.json','{"version":"test","history":[]}')
        spec=importlib.util.spec_from_file_location('about_renderer',repository/'render_editorial.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'catalog':types.SimpleNamespace(work_count=lambda tracks:str(len(tracks)))}):
            spec.loader.exec_module(module)
        rendered=module.about_html(self.root,[{}])
        self.assertIn('A Guide to Sampled Mind & Vintage Grooves',rendered)
        self.assertIn('VERSION HISTORY',rendered)
        self.assertNotIn('editor-profile.json',rendered)

    @unittest.skipUnless(shutil.which('git'),'Git executable unavailable')
    def test_git_object_fingerprints_and_worktree_guard(self):
        def git(*args):return subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True)
        git('init');git('config','user.email','test@example.invalid');git('config','user.name','Pipeline test');git('add','.');git('commit','-m','fixture')
        first=pipeline.inputs(self.root);self.assertTrue(first['profile']['editor_profile.json'].startswith('git:'))
        self.write('editor_profile.json','{"name":"changed"}')
        with self.assertRaisesRegex(ValueError,'Uncommitted'):pipeline.inputs(self.root)
        git('add','editor_profile.json');git('commit','-m','profile change')
        second=pipeline.inputs(self.root);self.assertNotEqual(first['profile'],second['profile']);self.assertEqual(first['full'],second['full'])


if __name__=='__main__':unittest.main()
