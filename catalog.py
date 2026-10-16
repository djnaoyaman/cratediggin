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
        identity=t['artist'] in aliases or t['artist'] in names or any(a in names for a in t.get('artists',[]))
        production=any(n in f.get('productionNames',[]) for n in t.get('producers',[]))
        if f['type']=='producer':production=production or any(n in names for n in t.get('producers',[])) or t['artist'] in f.get('collaborations',[])
        return identity or production
    return sorted([t for t in tracks if (f.get('allYears') or 1990<=t['year']<=1999) and selected(t)],key=lambda t:(t['year'],t['title']))
