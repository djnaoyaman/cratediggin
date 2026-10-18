"""Two explicitly requested aggregate mixes are not individual-song additions."""
import json,sys,re,html as html_module
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from catalog import work_type,work_count
tracks=json.loads((ROOT/'tracks.json').read_text());by={t['id']:t for t in tracks}
expected={'dj-shadow-cut-chemist-brainfreeze':('VMw2xzb4tlQ',1999),'dj-shadow-cut-chemist-product-placement-on-tour':('Xhg-kVolg-Y',2004)}
assert len(by)==len(tracks)
for tid,(video,year) in expected.items():
 t=by[tid];assert work_type(t)=='mix' and t['workScope']=='whole_work' and t['countsTowardDailyNewSongs'] is False
 assert t['year']==year and t['youtube']['id']==video and t['youtube']['official'] is False
 assert 'オーナー指定' not in t['youtube'].get('type','')
 assert 'requestProvenance' not in t
 html=(ROOT/'dist/tracks'/f'{tid}.html').read_text()
 assert 'work-format' in html and 'DJミックス作品' in html
 assert 'MixtapeTrap' in html and '参考' in html
 assert t['title'] in html and len(t['essay'])>=3 and len(t['essaySources'])==len(t['essay'])
 memory=t['editorSelectionMemory'];assert '間違いなく' in memory['text'] and 'DJ KIYO' in memory['text']
 assert html.count('<aside class="editor-selection-memory">')==1 and html_module.escape(memory['text']) in html
 assert 'Sentinel_' not in html and 'requestProvenance' not in html
 ld=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',html,re.S).group(1))
 albums=[x for x in ld['@graph'] if x['@type']=='MusicAlbum'];assert len(albums)==1
 assert albums[0]['albumProductionType']=='https://schema.org/DJMixAlbum'
 assert not any(x['@type']=='MusicRecording' for x in ld['@graph'])
 assert 'DJミックス作品' in re.search(r'<meta property="og:description" content="([^"]*)',html).group(1)
 if year==2004:assert '60:44' in html and '61:33' in html
assert len([t for t in tracks if work_type(t)=='single'])>=479
print('Two mix identity, third-party provenance, edition caveats, distinct schema and zero-song counting passed')
