from pathlib import Path
import argparse
from approved_list_year_restore import F,sha,current_list_year_restore_file as current,historical_list_year_restore_file as undo
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--source-only',action='store_true');a=p.parse_args();read=lambda path:current(path,(R/path).read_bytes())
for path,h in F['protected'].items():assert sha(read(path))==h,path
ph=F['previousHelper'];assert sha(read(ph['path']))==ph['afterSHA256']
for path,c in F['files'].items():
 assert sha(undo(path,(R/path).read_bytes()))==c['beforeSHA256']
 try:undo(path,(R/path).read_bytes()+b' ')
 except AssertionError:pass
 else:raise AssertionError('Drift accepted')
css=read('src/assets/style.css').decode();before=F['files']['src/assets/style.css']['before'];assert css==before.replace(F['oldCssBlock'],F['newCssBlock'])
assert ':not(h3):not(.card-artist):not(.card-meta)'in css
assert '#results.compact-results .record-card:not(.contextual-year-card) .card-main>.card-meta>span{display:none!important}'in css
for line in before.splitlines():
 if 'contextual-year-card' in line or 'catalog-graffiti'in line:assert line in css
player=read('src/app/player.js').decode();assert "<div class=\"card-meta\"><b>'+yearLabel(s)+'</b>"in player
if not a.source_only:
 assert F['newCssBlock']in(R/'dist/style.css').read_text()
print('Compact release-year CSS restored; existing date labels/caveats, detailed/gallery modes and all544 data/art unchanged PASS')
