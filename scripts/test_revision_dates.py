"""Exercise article-date provenance against real Git revisions and invalid history."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from revision_dates import revision_dates


class RevisionDatesTest(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[2] / 'revision-date-tests'
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.root = Path(self.temp.name).resolve()
        assert self.root.is_relative_to(parent.resolve())
        self.git('init', '-q')
        self.tracks = [{'id': 'a', 'artist': 'Artist A', 'title': 'First'},
                       {'id': 'b', 'artist': 'Artist B', 'title': 'Second'}]
        self.dives = []
        self.commit('2026-10-01T10:00:00+09:00')
        self.tracks[0]['title'] = 'Revised title'
        self.commit('2026-10-02T10:00:00+09:00')
        self.dives = [{'artist': 'Artist B', 'title': 'Second', 'sections': [{'heading': 'Context', 'text': 'New research'}]}]
        self.commit('2026-10-03T10:00:00+09:00')

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args, env=None):
        return subprocess.check_output(['git', '-C', str(self.root), *args], env=env, stderr=subprocess.DEVNULL)

    def commit(self, date, invalid=False):
        for name, value in [('tracks.json', self.tracks), ('editorial_deepdives.json', self.dives),
                            ('features.json', {'features': []})]:
            (self.root / name).write_text('invalid JSON' if invalid and name == 'tracks.json' else json.dumps(value), encoding='utf-8')
        self.git('add', '.')
        env = dict(os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Article revision', env=env)

    def test_independent_article_and_deep_dive_changes(self):
        result = revision_dates(self.root, self.tracks, self.dives, [])
        self.assertTrue(result['song/a']['dateModified'].startswith('2026-10-02'))
        self.assertTrue(result['song/b']['dateModified'].startswith('2026-10-03'))

    def test_uncommitted_content_has_no_invented_date(self):
        self.tracks[0]['title'] = 'Not in Git yet'
        result = revision_dates(self.root, self.tracks, self.dives, [])
        self.assertNotIn('song/a', result)
        self.assertIn('song/b', result)

    def test_invalid_history_does_not_create_dates(self):
        self.commit('2026-10-04T10:00:00+09:00', invalid=True)
        self.commit('2026-10-05T10:00:00+09:00')
        self.assertEqual(revision_dates(self.root, self.tracks, self.dives, []), {})


if __name__ == '__main__':
    unittest.main()
