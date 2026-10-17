import copy
import json
from pathlib import Path
import sys
import unittest
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from art_motion import BOUNDS, motion_for_track


class MotionTests(unittest.TestCase):
    def test_intensity_and_timing_order(self):
        outputs = [motion_for_track({'id': 'same', 'moods': [cue]})
                   for cue in ['メロウ', '跳ねる', '重い', '爆発']]
        self.assertEqual([x['mode'] for x in outputs], list(BOUNDS))
        self.assertEqual(sorted(x['energy'] for x in outputs), [x['energy'] for x in outputs])
        self.assertEqual(sorted((x['duration'] for x in outputs), reverse=True),
                         [x['duration'] for x in outputs])

    def test_generic_groove_does_not_swamp_specific_text(self):
        self.assertEqual(motion_for_track({'moods': ['グルーヴ'], 'deck': '爆発する音'})['mode'], 'burst')
        self.assertEqual(motion_for_track({'moods': ['メロウ'], 'deck': '硬い'})['mode'], 'drift')

    def test_metadata_isolation_and_essay_scope(self):
        base = {'id': 'same', 'moods': [], 'essay': ['平常', '通常', '爆発']}
        expected = motion_for_track(base)
        other = dict(base, artist='爆発', category='heavy', region='浮遊', title='激しい',
                     album='攻撃', producers=['跳ねる'])
        self.assertEqual(motion_for_track(other), expected)
        self.assertEqual(expected['mode'], 'groove')

    def test_deterministic_without_mutating_input(self):
        track = {'id': 'abc', 'moods': ['重い'], 'art': {'seed': 234}}
        original = copy.deepcopy(track)
        self.assertEqual(motion_for_track(track), motion_for_track(copy.deepcopy(track)))
        self.assertEqual(track, original)
        configs = [motion_for_track(dict(track, id=str(i))) for i in range(50)]
        self.assertEqual({x['variant'] for x in configs}, {0, 1, 2, 3})
        self.assertGreater(len({x['duration'] for x in configs}), 10)

    def test_valid_override_and_invalid_override(self):
        track = {'moods': ['メロウ'], 'art': {'motion': {'mode': 'burst', 'duration': 1500,
                                                      'energy': .9, 'variant': 2, 'note': '編集指定'}}}
        original = copy.deepcopy(track)
        actual = motion_for_track(track)
        self.assertEqual((actual['mode'], actual['duration'], actual['variant']), ('burst', 1500, 2))
        self.assertEqual(track, original)
        for bad in [True, -1, 10000, '1500']:
            track['art']['motion']['duration'] = bad
            self.assertEqual(motion_for_track(track)['mode'], 'drift')

    def test_missing_or_malformed_info(self):
        for track in [None, {}, {'moods': None, 'essay': 4, 'art': []},
                      {'art': {'motion': {'mode': []}}}]:
            result = motion_for_track(track)
            self.assertEqual(result['mode'], 'groove')
            self.assertIn('中立', result['note'])

    def test_catalog(self):
        tracks = json.loads((ROOT / 'tracks.json').read_text())
        counts = Counter()
        for track in tracks:
            result = motion_for_track(track)
            counts[result['mode']] += 1
            lo, hi = BOUNDS[result['mode']]
            self.assertLessEqual(lo, result['duration'])
            self.assertLessEqual(result['duration'], hi)
            self.assertEqual(result['basis'], 'editorial-cues')
        print('\nCatalog motion distribution', len(tracks), dict(counts))
        self.assertEqual(len(counts), 4)
        by_id = {t['id']: t for t in tracks}
        for track_id, mode in [('mass-appeal', 'groove'), ('93-til-infinity', 'drift'),
                               ('bucktown', 'stomp'), ('dj-shadow-the-number-song', 'burst')]:
            self.assertEqual(motion_for_track(by_id[track_id])['mode'], mode)


if __name__ == '__main__':
    unittest.main()
