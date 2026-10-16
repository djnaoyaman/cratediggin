"""Bump x.x; only major releases receive a visible history entry."""
import argparse,json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
g.add_argument('--major',action='store_true');g.add_argument('--minor',action='store_true')
p.add_argument('--title');p.add_argument('--description');a=p.parse_args()
f=Path(__file__).parent/'releases.json';r=json.loads(f.read_text(encoding='utf-8'));major,minor=map(int,r['version'].split('.'))
if a.major:
    if not a.title or not a.description:p.error('Major changes require --title and --description')
    r['version']=f'{major+1}.0'
    r['history'].append({'version':r['version'],'datetime':datetime.now(ZoneInfo('Asia/Tokyo')).isoformat(timespec='seconds'),'title':a.title,'description':a.description,'kind':'major','dateBasis':'変更記録日時','retrospective':False})
else:r['version']=f'{major}.{minor+1}'
f.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n', encoding='utf-8');print(r['version'])
