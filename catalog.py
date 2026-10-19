"""Shared catalog projections. Availability is never treated as verification."""
import re
from urllib.parse import urlparse,parse_qs

def review_state(t,sections):
    pending=[]
    if re.search('未確認|確認中',t.get('label','')):pending.append('レーベル')
    if re.search('継続中|照合中',t.get('yearBasis','')):pending.append('初出年・版')
    video=t.get('youtube',{})
    # Legacy verified fields refer to provenance checks, not actual playback.
    playback=video.get('playbackCheckedAt')
    return {'article':'deep-dive' if sections else 'listening-note','deepDiveSections':len(sections),
            'sampleEntries':len(t.get('samples',[])),'playableSamples':sum(bool(s.get('youtube',{}).get('id')) for s in t.get('samples',[])),
            'metadataPending':pending,'playbackCheckedAt':playback,
            'provenanceCheckedAt':video.get('verified'),'noteReviewedAt':t.get('noteReviewedAt')}

def sample_projection(t):
    return [dict(s,source=t['sources'][s['sources'][0]]['url']) for s in t.get('samples',[]) if s.get('research')]

def valid_video_url(video):
    parsed=urlparse(video.get('url',''));q=parse_qs(parsed.query)
    return parsed.hostname in {'www.youtube.com','youtube.com'} and q.get('v')==[video.get('id')]

def feature_tracks(tracks,f):
    names=f['names'];aliases=f.get('aliases',[])
    def selected(t):
        identity=t['artist'].split(' feat. ')[0] in aliases or t['artist'].split(' feat. ')[0] in names or any(a in names for a in t.get('artists',[]))
        production=any(n in f.get('productionNames',[]) for n in t.get('producers',[]))
        if f['type']=='producer':production=production or any(n in names for n in t.get('producers',[])) or t['artist'] in f.get('collaborations',[])
        return identity or production
    return sorted([t for t in tracks if (f.get('allYears') or isinstance(t['year'],int) and 1990<=t['year']<=1999) and selected(t)],key=lambda t:(year_sort(t),t['title']))


def year_label(t):
    return str(t['year']) if isinstance(t.get('year'),int) else '発表年未確認'

def year_sort(t):
    return t['year'] if isinstance(t.get('year'),int) else 9999

def work_type(t):
    return t.get('workType', 'single')

def work_label(t):
    return {'single': '楽曲', 'mix': 'DJミックス作品', 'live_video': 'ライブ映像（参考投稿）', 'album':'アルバム全体'}[work_type(t)]

def work_count(tracks):
    singles=sum(work_type(t)=='single' for t in tracks)
    mixes=sum(work_type(t)=='mix' for t in tracks)
    videos=sum(work_type(t)=='live_video' for t in tracks)
    albums=sum(work_type(t)=='album' for t in tracks)
    return str(singles)+'曲' + ('・'+str(mixes)+'ミックス作品' if mixes else '') + ('・'+str(videos)+'ライブ映像' if videos else '') + ('・'+str(albums)+'アルバム' if albums else '')

def validate_work(t):
    assert work_type(t) in {'single', 'mix', 'live_video', 'album'}, 'Unsupported work type'
    y=t.get('youtube', {});kind=y.get('sourceType','video')
    assert kind in {'video','playlist'}, 'Unsupported source type'
    if kind=='playlist':
        assert work_type(t)=='album' and not y.get('id'), 'Album playlist cannot disguise a video'
        assert isinstance(y.get('playlistId'),str) and re.fullmatch(r'[A-Za-z0-9_-]+',y['playlistId']), 'Invalid playlist identity'
        u=urlparse(y.get('url',''));q=parse_qs(u.query)
        assert u.scheme=='https' and u.hostname in {'www.youtube.com','youtube.com'} and u.path=='/playlist' and q.get('list')==[y['playlistId']] and 'v' not in q, 'Playlist URL mismatch'
        assert not any(s.get('youtube') for s in t.get('samples',[])), 'Album sample playback is not implemented'
    else:
        assert work_type(t)!='album' and not y.get('playlistId'), 'Album requires native playlist source'
        if y.get('id'):
            assert re.fullmatch(r'[A-Za-z0-9_-]{11}',y['id'])
            assert valid_video_url(y), 'Video URL does not match its identity'
