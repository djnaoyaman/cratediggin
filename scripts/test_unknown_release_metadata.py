"""Direct source contracts for explicitly unknown single-release metadata."""
import ast
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class UnknownReleaseMetadataTests(unittest.TestCase):
    def year_assertion(self):
        tree = ast.parse((ROOT / 'build.py').read_text())
        return next(n for n in ast.walk(tree) if isinstance(n, ast.Assert) and "1970" in ast.unparse(n.test) and "year" in ast.unparse(n.test))

    def allowed(self, track):
        return bool(eval(compile(ast.Expression(self.year_assertion().test), '<year-contract>', 'eval'), {'t': track, 'work_type': lambda t: t.get('workType', 'single')}))

    def test_known_year_range_unchanged(self):
        for year in (1970, 2000, 2100):
            self.assertTrue(self.allowed({'year': year}))
        for year in (1969, 2101, True, False, '2000', 2000.0):
            self.assertFalse(self.allowed({'year': year}))

    def test_existing_live_unknown_still_allowed(self):
        self.assertTrue(self.allowed({'year': None, 'workType': 'live_video'}))

    def test_explicit_unknown_single_only(self):
        valid = {'year': None, 'yearStatus': 'unconfirmed', 'yearBasis': 'Selected upload has no established release date.', 'yearDisplayNote': '収録版・発売年未確認。'}
        self.assertTrue(self.allowed(valid))
        for key in ('yearStatus', 'yearBasis', 'yearDisplayNote'):
            missing = dict(valid); missing.pop(key)
            self.assertFalse(self.allowed(missing))
        for key in ('yearBasis', 'yearDisplayNote'):
            for value in ('', '  ', None, [], 2003):
                bad = dict(valid); bad[key] = value
                self.assertFalse(self.allowed(bad))
        for kind in ('mix', 'album'):
            self.assertFalse(self.allowed(dict(valid, workType=kind)))
        self.assertFalse(self.allowed(dict(valid, yearStatus='verified')))
        self.assertFalse(self.allowed(dict(valid, year=1900)))

    def test_both_jsonld_paths_omit_unknown_album(self):
        for file in ('build.py', 'discovery.py'):
            tree = ast.parse((ROOT / file).read_text())
            branch = next(n for n in ast.walk(tree) if isinstance(n, ast.IfExp) and "inAlbum" in ast.unparse(n.body) and "isinstance" in ast.unparse(n.test))
            for value in (None, '', '  ', '未確認', '不明'):
                result = eval(compile(ast.Expression(branch), '<album-contract>', 'eval'), {'t': {'album': value}})
                self.assertEqual(result, {}, (file, value))
            result = eval(compile(ast.Expression(branch), '<album-contract>', 'eval'), {'t': {'album': 'Subject'}})
            self.assertEqual(result, {'inAlbum': {'@type': 'MusicAlbum', 'name': 'Subject'}})

    def test_legacy_jsonld_omits_absent_audio_identity(self):
        tree = ast.parse((ROOT / 'build.py').read_text())
        branch = next(n for n in ast.walk(tree) if isinstance(n, ast.IfExp) and "sameAs" in ast.unparse(n.body) and "externalAudio" in ast.unparse(n.test))
        evaluate = lambda t: eval(compile(ast.Expression(branch), '<audio-identity-contract>', 'eval'), {'t': t})
        self.assertEqual(evaluate({'youtube': {'id': None, 'type': '未設定'}}), {})
        self.assertEqual(evaluate({'youtube': {}}), {})
        self.assertEqual(evaluate({}), {})
        for t in json.loads((ROOT / 'tracks.json').read_text()):
            url = t.get('externalAudio', {}).get('url') or t.get('youtube', {}).get('url')
            self.assertEqual(evaluate(t), {'sameAs': url} if url else {})

    def test_spa_null_album_producer_and_note_display(self):
        source = (ROOT / 'src/app/song-ui.js').read_text()
        self.assertIn("(s.yearQualifier||s.yearStatus==='unconfirmed')", source)
        self.assertIn("['アルバム',s.album||'未確認']", source)
        self.assertIn("['制作',s.producer||'未確認']", source)
        script = "const s={album:null,producer:null}; const v=[['アルバム',s.album||'未確認'],['制作',s.producer||'未確認']]; process.stdout.write(JSON.stringify(v));"
        self.assertEqual(json.loads(subprocess.check_output(['node', '-e', script])), [['アルバム','未確認'],['制作','未確認']])
        static_source = (ROOT/'build.py').read_text()
        self.assertIn("'<p class=\"work-year\">'+e(year_label(t))+'</p>'", static_source)
        self.assertIn("'<p class=\"work-year-note\">'+e(t['yearDisplayNote'])+'</p>' if t.get('yearDisplayNote') else ''", static_source)

if __name__ == '__main__':
    unittest.main()
