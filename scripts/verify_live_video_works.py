"""Unknown-year live video is not a single song, mix album, or guessed edition."""
import json,re,sys,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
from catalog import work_type,work_count
tracks=json.loads((R/'tracks.json').read_text());by={t['id']:t for t in tracks};dives=json.loads((R/'editorial_deepdives.json').read_text());dm={(d['artist'],d['title']):d['sections'] for d in dives}
expected={'dj-shadow-cut-chemist-freeze-live-video':'gu9Gz5asQe4','dj-shadow-cut-chemist-product-placement-live-video':'gdZ5cHYrcLU'}
assert expected.keys() <= by.keys()
for tid,video in expected.items():
 t=by[tid];assert work_type(t)=='live_video' and t['year'] is None and t['countsTowardDailyNewSongs'] is False
 assert t['youtube']['id']==video and t['youtube']['official'] is False
 assert 'requestProvenance' not in t and t['essay'] and len(t['essaySources'])==len(t['essay'])
 s=(R/'dist/tracks'/f'{tid}.html').read_text();md=(R/'dist/tracks'/f'{tid}.md').read_text()
 assert 'ライブ映像（参考投稿）' in s and '発表年未確認' in s and '発表年未確認' in md
 assert 'Sentinel_' not in s and '/workspace/' not in s
 graph=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)[1])['@graph'];v=next(x for x in graph if x['@type']=='VideoObject')
 assert v['embedUrl']=='https://www.youtube.com/embed/'+video and v['uploadDate']==t['youtube']['uploadDate']
 assert 'datePublished' not in v and not any(x['@type'] in ['MusicRecording','MusicAlbum'] for x in graph)
 for d in dm[(t['artist'],t['title'])]:assert html.escape(d['heading']) in s
 for inds in t['essaySources']:assert all(type(i)is int and 0<=i<len(t['sources']) for i in inds)
 feature=(R/'dist/producers/dj-shadow.html').read_text();assert '/tracks/'+tid+'.html' in feature
 timeline=(R/'dist/timeline.html').read_text();assert '発表年未確認' in timeline and tid in timeline
 assert 'timeline-year-null' not in timeline and 'None年' not in timeline
new_ids=['dj-shadow-mutual-slump','dj-shadow-napalm-brain-scatter-brain','dj-shadow-changeling','dj-shadow-monosylabik','dj-shadow-you-cant-go-home-again']
assert len({by[x]['addedOrder'] for x in new_ids+list(expected)})==7
assert not ({by[x]['addedOrder'] for x in new_ids+list(expected)} & {t['addedOrder'] for t in tracks if t['id'] not in new_ids+list(expected)})
for tid in new_ids:
 t=by[tid];assert work_type(t)=='single' and len(t['essay'])==3 and len(t['essaySources'])==3
 sections=dm[(t['artist'],t['title'])];assert len(sections)>=2
 for d in sections:assert d['sources'] and all(0<=i<len(t['sources']) for i in d['sources'])
 assert t['youtube']['official'] is True and t['youtube']['japanRegionStatus']=='included'
assert by['dj-shadow-cut-chemist-brainfreeze']['youtube']['id']=='VMw2xzb4tlQ'
assert by['dj-shadow-cut-chemist-product-placement-on-tour']['youtube']['id']=='Xhg-kVolg-Y'
print('Live video exact identities/unknown-year schema/internal feature links and five sourced songs passed; metadata is not playback')
