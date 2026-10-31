"""Site freshness advances only with real production changes, not CI or editorial history."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from site_update_dates import finalize_update_dates, latest_revision


class SiteDatesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='crate-dates-', dir='/tmp')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dist = self.root/'dist'
        (self.dist/'metadata').mkdir(parents=True)
        self.git('init', '-q')
        (self.root/'tracks.json').write_text('[]')
        (self.root/'editor_profile.json').write_text('{"name":"Author"}')
        self.commit('2026-10-01T23:30:00+00:00')
        self.seed()

    def git(self, *args, env=None):
        return subprocess.check_output(['git', '-C', str(self.root), *args], env=env, stderr=subprocess.DEVNULL)

    def commit(self, date):
        self.git('add', 'tracks.json', 'editor_profile.json')
        env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Real content change', env=env)

    def seed(self):
        registry = {}
        for route, filename, kind in [('#/', 'index.html', 'WebSite'), ('#/editor', 'editor.html', 'ProfilePage'), ('#/song/old', 'old.html', 'Article')]:
            key = filename.replace('.html', '')
            graph = {'@context':'https://schema.org','@graph':[{'@type':kind,'name':'Author','datePublished':'2020-01-01','dateModified':'2026-09-01T00:00:00+00:00'}]}
            data = {'route':route,'url':'https://example.test/'+('' if filename=='index.html' else filename),'metadataPath':'/metadata/'+key+'.json','title':key,'description':key,'jsonld':graph,'modified':graph['@graph'][0]['dateModified']}
            (self.dist/'metadata'/(key+'.json')).write_text(json.dumps(data))
            registry[route] = {k:v for k,v in data.items() if k!='jsonld'}
            page = '<html><head><script type="application/ld+json">'+json.dumps(graph)+'</script><script>window.INITIAL_ROUTE='+json.dumps(route)+';window.CRATE_INITIAL_META='+json.dumps({'route':route,'jsonld':graph})+';</script></head><body><main id="view">Original body</main><footer>Footer</footer></body></html>'
            if route=='#/editor':
                payload={'html':'Original profile','page':{'title':'Author updated','description':'New profile','url':data['url'],'jsonld':graph}}
                (self.dist/'editor-profile.json').write_text(json.dumps(payload))
                page=page.replace('</head>','<script id="editor-profile-metadata" type="application/json">'+json.dumps(payload['page'])+'</script></head>')
            (self.dist/filename).write_text(page)
        (self.dist/'metadata.js').write_text('window.CRATE_PAGES='+json.dumps(registry)+';\n')
        (self.dist/'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+p['url']+'</loc><lastmod>'+p['modified']+'</lastmod></url>' for p in registry.values())+'</urlset>')

    def finalize(self):
        return finalize_update_dates(self.root, self.dist, ['tracks.json','editor_profile.json'])

    def test_same_commit_repeat_is_identical_and_jst_visible(self):
        self.finalize()
        before={p.relative_to(self.dist):p.read_bytes() for p in self.dist.rglob('*') if p.is_file()}
        self.finalize()
        self.assertEqual(before,{p.relative_to(self.dist):p.read_bytes() for p in self.dist.rglob('*') if p.is_file()})
        self.assertIn('2026-10-02</time> JST', (self.dist/'index.html').read_text())
        self.assertEqual((self.dist/'old.html').read_text().count('site-update'),1)

    def test_profile_change_keeps_unrelated_article_metadata_and_published(self):
        old=(self.dist/'metadata/old.json').read_bytes()
        (self.root/'editor_profile.json').write_text('{"name":"Revised"}')
        self.commit('2026-10-03T12:00:00+09:00')
        result=self.finalize()
        self.assertEqual(old,(self.dist/'metadata/old.json').read_bytes())
        date=result['profile']['dateModified']
        payload=json.loads((self.dist/'editor-profile.json').read_text())
        meta=json.loads((self.dist/'metadata/editor.json').read_text())
        self.assertEqual(payload['page']['modified'],date)
        self.assertEqual(meta['jsonld']['@graph'][0]['dateModified'],date)
        self.assertEqual(meta['jsonld']['@graph'][0]['datePublished'],'2020-01-01')
        self.assertIn('ページ更新',payload['html'])
        nodes=ET.parse(self.dist/'sitemap.xml').getroot()
        self.assertEqual(nodes[1][-1].text,date)
        self.assertEqual(nodes[2][-1].text,'2026-09-01T00:00:00+00:00')

    def test_client_or_css_changes_only_site_date(self):
        self.finalize()
        old = (self.dist/'metadata/old.json').read_bytes()
        profile = json.loads((self.dist/'metadata/editor.json').read_text())['modified']
        source = self.root/'src/assets/style.css'
        source.parent.mkdir(parents=True)
        source.write_text('body{color:black}')
        self.git('add', 'src/assets/style.css')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Style change', env=dict(os.environ, GIT_AUTHOR_DATE='2026-10-05T00:00:00Z', GIT_COMMITTER_DATE='2026-10-05T00:00:00Z'))
        result = finalize_update_dates(self.root, self.dist, ['tracks.json', 'editor_profile.json', 'src/assets/style.css'])
        self.assertTrue(result['site']['dateModified'].startswith('2026-10-05'))
        self.assertEqual(json.loads((self.dist/'metadata/editor.json').read_text())['modified'], profile)
        self.assertEqual((self.dist/'metadata/old.json').read_bytes(), old)

    def test_documentation_commit_does_not_advance_site(self):
        before=self.finalize()
        (self.root/'README.md').write_text('Changed documentation only')
        self.git('add','README.md')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Docs',env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-10T00:00:00Z',GIT_COMMITTER_DATE='2026-10-10T00:00:00Z'))
        self.assertEqual(before,finalize_update_dates(self.root,self.dist,['tracks.json','editor_profile.json','README.md']))
        workflow=self.root/'.github/workflows/ci.yml'
        workflow.parent.mkdir(parents=True)
        workflow.write_text('name: CI')
        self.git('add','.github/workflows/ci.yml')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','CI only',env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-11T00:00:00Z',GIT_COMMITTER_DATE='2026-10-11T00:00:00Z'))
        self.assertEqual(before,finalize_update_dates(self.root,self.dist,['tracks.json','editor_profile.json','README.md','.github/workflows/ci.yml']))

    def test_deleted_production_input_still_advances_site_date(self):
        asset=self.root/'obsolete.css'
        asset.write_text('body{}')
        self.git('add','obsolete.css')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Add style',env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-11T00:00:00Z',GIT_COMMITTER_DATE='2026-10-11T00:00:00Z'))
        self.git('rm','obsolete.css')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Remove style',env=dict(os.environ,GIT_AUTHOR_DATE='2026-10-12T00:00:00Z',GIT_COMMITTER_DATE='2026-10-12T00:00:00Z'))
        self.assertTrue(self.finalize()['site']['dateModified'].startswith('2026-10-12'))

    def test_no_git_does_not_invent_build_date(self):
        self.assertIsNone(latest_revision(self.root/'missing',['tracks.json']))

if __name__=='__main__':unittest.main()
