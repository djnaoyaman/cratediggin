#!/usr/bin/env python3
"""Verbatim legacy-assertion equivalence and synthetic negative-data cases."""
import ast
from collections import Counter
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import integrity_checks as integrity


def assertions(source):
    return Counter(ast.dump(node, include_attributes=False) for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assert))


class IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.tracks = [
            {'id': 'pe-song', 'artist': 'Public Enemy', 'title': 'PE Song', 'samples': []},
            {'id': 'gs-song', 'artist': 'Gang Starr', 'title': 'GS Song', 'samples': []},
            {'id': 'dj-shadow-the-number-song', 'artist': 'DJ Shadow', 'title': 'The Number Song', 'samples': [{'research': {'source': 1}}]},
        ]
        self.deepdives = [{'artist': t['artist'], 'title': t['title'], 'sections': [{}, {}, {}, {}]} for t in self.tracks]
        self.research = [{'title': 'The Number Song' if i == 0 else f'Other {i}', 'samples': [{}] * (3 if i == 0 else 2)} for i in range(6)]
        self.write_json('tracks.json', self.tracks)
        self.write_json('editorial_deepdives.json', self.deepdives)
        self.write_json('dj_shadow_sample_research.json', self.research)
        self.write_json('scripts/shadow_existing_depth_ids.json', ['dj-shadow-the-number-song'])
        self.html = '\n'.join([
            '<a href="/cratediggin/tracks/">TRACKS</a>',
            '<script src="/cratediggin/tracks.js"></script>',
            '<script src="/cratediggin/app.js"></script>',
            '<link rel="apple-touch-icon" href="/cratediggin/apple-touch-icon-vinyl.png?v=original-20261016">',
            '<a href="/cratediggin/artists/a.html">ARTIST INDEX</a>',
        ])
        self.write('dist/index.html', self.html)
        self.write('dist/apple-touch-icon-vinyl.png', 'synthetic asset')
        for t in self.tracks:
            self.write(f'dist/tracks/{t["id"]}.html', '<a href="/cratediggin/artists/a.html">Artist</a>')
            self.write(f'dist/tracks/{t["id"]}.md', 'Synthetic song')
            self.write(f'dist/og/{t["id"]}.jpg', 'synthetic social image')
        self.write('dist/tracks/index.html', 'index')
        self.write('dist/artists/a.html', 'artist')
        self.write('dist/sitemap.xml', '<loc>/cratediggin/artists/a.html</loc>')
        self.write('dist/llms.txt', '## Artists')
        self.write('dist/app.js', 'DIG DEEPER')
        self.write('dist/tracks.js', '制作の背景：サンプラーの制約が音楽になった researchedSamples dj-shadow-the-number-song')

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')

    def write_json(self, path, obj):
        self.write(path, json.dumps(obj))

    def test_every_legacy_assertion_ast_exactly_preserved(self):
        workflow = (HERE / 'bootstrap-pages.yml').read_text()
        legacy = workflow.split("          python - <<'PY'\n", 1)[1].split('\n          PY', 1)[0]
        expected = assertions(textwrap.dedent(legacy))
        actual = Counter()
        for block in integrity.BLOCKS.values():
            actual.update(assertions(block['source']))
        self.assertEqual(sum(actual.values()), 26)
        self.assertEqual(sum(actual.values()), integrity.LEGACY_ASSERTION_COUNT)
        self.assertEqual(actual, expected)

    def test_every_block_passes_individually_without_other_block_execution(self):
        for name in integrity.BLOCKS:
            with self.subTest(block=name):
                self.assertEqual(integrity.run_groups(self.root, [name]), [name])
        self.assertEqual(integrity.run_groups(self.root, list(integrity.BLOCKS)), list(integrity.BLOCKS))

    def test_each_of_26_assertions_actually_executes_and_fails(self):
        count = 0
        for name, spec in integrity.BLOCKS.items():
            parsed = ast.parse(spec['source'])
            nodes = [n for n in ast.walk(parsed) if isinstance(n, ast.Assert)]
            for index in range(len(nodes)):
                mutated = copy.deepcopy(parsed)
                mutated_nodes = [n for n in ast.walk(mutated) if isinstance(n, ast.Assert)]
                mutated_nodes[index].test = ast.Constant(False)
                ast.fix_missing_locations(mutated)
                replacement = dict(spec, source=ast.unparse(mutated))
                with self.subTest(block=name, assertion=index), mock.patch.dict(integrity.BLOCKS, {name: replacement}):
                    with self.assertRaises(AssertionError):
                        integrity.run_groups(self.root, [name])
                count += 1
        self.assertEqual(count, 26)

    def test_unknown_empty_scope_and_python_optimization_fail(self):
        for names in ([], ['unknown']):
            with self.assertRaises(ValueError): integrity.run_groups(self.root, names)
        result = subprocess.run([sys.executable, '-O', str(HERE / 'integrity_checks.py'), '--root', str(self.root), '--group', 'generated-pages'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('without -O', result.stderr)

    def test_generated_ids_negative(self):
        self.write('dist/tracks/unexpected.html', 'unexpected')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['generated-pages'])

    def test_social_image_count_negative(self):
        (self.root / 'dist/og/pe-song.jpg').unlink()
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['social-card-count'])

    def test_project_path_negative(self):
        self.write('dist/index.html', self.html.replace('/cratediggin/tracks/', '/tracks/'))
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['project-pages-urls'])

    def test_touch_icon_duplicate_negative(self):
        self.write('dist/index.html', self.html + '<link rel="apple-touch-icon">')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['touch-icon'])

    def test_artist_sitemap_negative(self):
        self.write('dist/sitemap.xml', '<loc>wrong</loc>')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['artist-discovery'])

    def test_deep_dive_negative(self):
        self.write('dist/app.js', 'missing')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['deep-dive-output'])

    def test_artist_coverage_and_section_negative(self):
        for index, group in [(0, 'public-enemy-coverage'), (1, 'gang-starr-coverage'), (2, 'shadow-coverage')]:
            bad = copy.deepcopy(self.deepdives)
            bad[index]['sections'] = []
            self.write_json('editorial_deepdives.json', bad)
            with self.subTest(group=group), self.assertRaises(AssertionError): integrity.run_groups(self.root, [group])
        self.write_json('editorial_deepdives.json', self.deepdives)

    def test_research_count_and_linkage_negative(self):
        self.write_json('dj_shadow_sample_research.json', self.research[:5])
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['shadow-research-counts'])
        self.write_json('dj_shadow_sample_research.json', self.research)
        self.tracks[2]['samples'] = []
        self.write_json('tracks.json', self.tracks)
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['shadow-research-output'])

    def test_number_song_sentinel_negative(self):
        self.write('dist/tracks.js', 'missing')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['number-song-output'])

    def test_working_directory_restored_after_assertion_failure(self):
        previous = Path.cwd()
        self.write('dist/tracks.js', 'missing')
        with self.assertRaises(AssertionError): integrity.run_groups(self.root, ['number-song-output'])
        self.assertEqual(Path.cwd(), previous)


if __name__ == '__main__':
    unittest.main()
