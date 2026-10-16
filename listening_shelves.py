"""Load reviewed listening tags and fail builds when their editorial evidence drifts."""
import json

def load_shelves(root, tracks, deepdives):
    data = json.loads((root/'listening_shelves.json').read_text())
    shelves = data['shelves']
    shelf_ids = {s['id'] for s in shelves}
    assert len(shelves) == len(shelf_ids) == 6, 'Expected six distinct listening shelves'
    assert all(s['label'] and s['description'] for s in shelves)
    by_id = {t['id']: t for t in tracks}
    seen = set()
    counts = {sid: 0 for sid in shelf_ids}
    for t in tracks:
        t['listeningTags'] = []
    for entry in data['tracks']:
        tid = entry['id']
        assert tid in by_id and tid not in seen, f'Unknown or duplicate shelf track: {tid}'
        seen.add(tid)
        track = by_id[tid]
        assert entry['tags'], f'Empty shelf entry: {tid}'
        for tag in entry['tags']:
            sid, evidence = tag['shelf'], tag['evidence']
            assert sid in shelf_ids and sid not in track['listeningTags'], f'Invalid tag: {tid}/{sid}'
            assert evidence['file'] in ('tracks.json', 'editorial_deepdives.json')
            value = track if evidence['file'] == 'tracks.json' else deepdives
            path = evidence['field'].split('.')
            if evidence['file'] == 'editorial_deepdives.json':
                editorial = deepdives[int(path[0])]
                assert (editorial['artist'], editorial['title']) == (track['artist'], track['title']), f'Wrong editorial: {tid}'
            for key in path:
                value = value[int(key)] if isinstance(value, list) else value[key]
            assert isinstance(value, str) and evidence['quote'].strip() and evidence['quote'] in value, f'Stale listening evidence: {tid}/{sid}'
            track['listeningTags'].append(sid)
            counts[sid] += 1
    assert all(counts.values()), f'Empty listening shelf: {counts}'
    return shelves
