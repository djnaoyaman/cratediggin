"""Check this request's exclusions, version identity and complete audio references."""
import json
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracks = json.loads((root / 'tracks.json').read_text(encoding='utf-8'))
report = json.loads((root / 'research/kiyo-hiphop-import-2026-10-15.json').read_text(encoding='utf-8'))
by_id = {t['id']: t for t in tracks}
rows = report['requests']
assert len(rows) == 144
assert Counter(r['status'] for r in rows) == {
    'added': 100, 'skip_existing': 34, 'skip_dj_kiyo': 4,
    'skip_rnb': 4, 'hold_unverified': 2,
}
for row in rows:
    if row['status'] == 'added':
        t = by_id[row['id']]
        assert t['category'] == 'Hip Hop'
        assert t['youtube']['id'] == row['video']
        assert t['youtube']['official'] == row['official']
        assert 'kiyo' not in t['artist'].lower()
        assert (root / 'dist/songs' / (t['id'] + '.html')).is_file()
    elif row['status'] == 'skip_existing':
        assert row['existing_id'] in by_id
new = [by_id[r['id']] for r in rows if r['status'] == 'added']
assert len({t['id'] for t in new}) == 100
assert len({t['youtube']['id'] for t in new}) == 100
assert not any(t['artist'].startswith(('Heavy D', 'Prince Markie Dee', 'DJ Carbozo', 'DeeJay Rell')) for t in new)
assert any(t['title'] == 'The Lump Lump (Nubian Mix)' for t in new)
assert any(t['title'] == 'Up Against The Wall (Low Budget Mix)' for t in new)
assert any(t['title'] == 'Usual Suspect (Stretch Armstrong Remix)' for t in new)
print('Hip Hop import: 100 additions with audio; all 44 skips/holds accounted for')
