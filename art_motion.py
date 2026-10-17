"""Deterministic editorial reveal pacing; no audio/BPM analysis is performed."""
import hashlib
import math
import re


BOUNDS = {'drift': (5600, 7000), 'groove': (3200, 4600),
          'stomp': (2200, 3000), 'burst': (1200, 1800)}
ENERGY = {'drift': .22, 'groove': .48, 'stomp': .73, 'burst': .95}
CUES = {
    'drift': ('メロウ', '浮遊', '余韻', '穏やか', '柔らか', 'やわらか', '漂う',
              'ゆったり', '心地よ', '涼しい', 'mellow', 'floating', 'soft'),
    'groove': ('ファンキー', '跳ねる', '軽やか', '躍動', '踊る', 'ダンス',
               '弾む', 'funky', 'bouncy', 'dancing'),
    'stomp': ('重い', '重厚', '低い重心', '重心を下げ', '低音', '硬さ', '硬い',
              '重たい', 'ハード', '打撃', 'heavy', 'hard', 'percussive'),
    'burst': ('緊張感', '攻撃', '爆発', '切迫', '急迫', '激しい', '激しさ',
              '疾走', '怒り', '荒々', '畳みかけ', '切り刻',
              'aggressive', 'urgent', 'explosive'),
}


def _text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return ' '.join(v for v in value if isinstance(v, str))
    return ''


def _present(cue, text):
    if cue.isascii():
        return re.search(r'(?<![a-z])' + re.escape(cue) + r'(?![a-z])', text.lower()) is not None
    return cue in text


def motion_for_track(track):
    """Return a fresh, bounded motion config using only supplied editorial cues.

    Generic グルーヴ is intentionally neutral: it appears on most records and
    cannot establish a particular energy. Each keyword counts once per field.
    """
    track = track if isinstance(track, dict) else {}
    art = track.get('art') if isinstance(track.get('art'), dict) else {}
    seed = hashlib.sha256((str(art.get('seed', '')) + '\0' +
                           str(track.get('id', ''))).encode('utf-8')).digest()
    n = int.from_bytes(seed[:8], 'big')
    essay = track.get('essay', [])
    essay = essay[:2] if isinstance(essay, (list, tuple)) else []
    fields = [('moods', 6, _text(track.get('moods'))),
              ('deck', 3, _text(track.get('deck'))),
              ('listening', 2, _text(track.get('listening'))),
              ('essay', 1, _text(essay))]
    scores = {mode: 0 for mode in BOUNDS}
    evidence = {mode: [] for mode in BOUNDS}
    for field, weight, text in fields:
        for mode, cues in CUES.items():
            for cue in cues:
                if _present(cue, text):
                    scores[mode] += weight
                    evidence[mode].append((field, cue))
    # Fixed tie order is intentional, independent of identity or musical metadata.
    mode = max(BOUNDS, key=lambda m: scores[m]) if any(scores.values()) else 'groove'
    matched = evidence[mode][:3]
    note = ('編集文の手掛かり ' + ' / '.join(f'{f}「{c}」' for f, c in matched)
            if matched else '具体的な強弱の手掛かりがないため、中立のgrooveを採用。')
    low, high = BOUNDS[mode]
    result = {'mode': mode, 'duration': low + n % (high-low+1),
              'energy': ENERGY[mode], 'basis': 'editorial-cues',
              'note': note + ' 音声・BPM解析ではありません。', 'variant': n % 4}
    override = art.get('motion')
    if isinstance(override, str):
        override = {'mode': override}
    if (isinstance(override, dict) and isinstance(override.get('mode'), str)
            and override['mode'] in BOUNDS):
        chosen = override['mode']
        lo, hi = BOUNDS[chosen]
        duration = override.get('duration', lo + n % (hi-lo+1))
        energy = override.get('energy', ENERGY[chosen])
        variant = override.get('variant', n % 4)
        if (type(duration) is int and lo <= duration <= hi and
                type(energy) in (int, float) and math.isfinite(energy) and 0 <= energy <= 1 and
                type(variant) is int and 0 <= variant <= 3):
            result.update(mode=chosen, duration=duration, energy=float(energy), variant=variant,
                          note='明示された編集指定。' +
                          (_text(override.get('note')) or '演出の強弱を指定。') +
                          ' 音声・BPM解析ではありません。')
    return result
