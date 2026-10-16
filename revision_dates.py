"""Use actual per-record Git revisions, never the build time, as editorial dates."""
import hashlib
import json
import subprocess


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def records(tracks, deepdives, features):
    dives = {(x['artist'].casefold(), x['title'].casefold()): x['sections'] for x in deepdives}
    # Projections inserted by the builder are not authored source content.
    derived = {'deepdives', 'review', 'researchedSamples', 'listeningTags'}
    result = {'song/' + t['id']: fingerprint([
        {k: v for k, v in t.items() if k not in derived},
        dives.get((t['artist'].casefold(), t['title'].casefold()), [])]) for t in tracks}
    result.update({'feature/' + f['id']: fingerprint(f) for f in features})
    return result


def revision_dates(root, tracks, deepdives, features):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.DEVNULL).decode('utf-8')
    current = records(tracks, deepdives, features)
    dates, matching = {}, {}
    try:
        history = git('log', '--format=%H %cI', '--', 'tracks.json', 'editorial_deepdives.json', 'features.json')
        cache = {}
        for line in history.splitlines():
            sha, date = line.split(' ', 1)
            values = []
            for name in ('tracks.json', 'editorial_deepdives.json', 'features.json'):
                try:
                    blob = git('rev-parse', f'{sha}:{name}').strip()
                    if blob not in cache:
                        cache[blob] = json.loads(git('show', blob))
                    value = cache[blob]
                except subprocess.CalledProcessError:
                    value = [] if name != 'features.json' else {'features': []}
                values.append(value)
            snapshot = records(values[0], values[1], values[2].get('features', []))
            for key in current.keys() - dates.keys():
                if snapshot.get(key) == current[key]:
                    matching[key] = {'dateModified': date, 'revision': sha}
                elif key in matching:
                    dates[key] = matching.pop(key)
        dates.update(matching)
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        # Archives, missing or malformed historical snapshots cannot prove a
        # revision boundary. Keep only dates already established before it.
        pass
    return dates
