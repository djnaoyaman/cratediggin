"""Content fingerprints select profile, client, assets, or full generation.

Only verified output bytes are reused. Pages still receives a complete artifact;
copying unchanged files is not generation, image decoding, or re-encoding.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

SCHEMA = 1
HOST = 'https://djnaoyaman.github.io/cratediggin'
DOCS = {'README.md','AGENTS.md','ADDING_TRACKS.md','ARTWORK_NOTES.md','DEPLOYMENT_RULES.md','FEATURE_COMPLETENESS.md','CREATOR_SITES.md','.gitignore'}
PROFILE = {'editor_profile.json','profile_content.py','scripts/profile_build.py'}


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def source_paths(root):
    root=Path(root)
    if (root/'.git').exists():
        raw=subprocess.check_output(['git','-C',str(root),'ls-files','-z'])
        return [p.decode() for p in raw.split(b'\0') if p]
    return [p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not any(x in {'dist','.build-cache','.build-support','__pycache__','.git'} for x in p.relative_to(root).parts)]


def inputs(root):
    result={k:{} for k in ('profile','client','assets','full')}
    objects={}
    if (Path(root)/'.git').exists():
        for row in subprocess.check_output(['git','-C',str(root),'ls-files','--stage','-z']).split(b'\0'):
            if not row:continue
            header,name=row.split(b'\t',1);mode,oid,stage=header.decode().split()
            if mode not in {'100644','100755'}:raise ValueError('Unsupported production source mode')
            objects[name.decode()]='git:'+oid
    for name in sorted(source_paths(root)):
        if name in DOCS or name.startswith(('audit-reports/','dist/','tests/','handoff/','notes/','scripts/ci/','scripts/fixtures/')):continue
        if name.startswith('scripts/') and name not in {'scripts/build_pipeline.py','scripts/profile_build.py'}:continue
        if name.endswith(('.pyc','.log')):continue
        if name in PROFILE:group='profile'
        elif name.startswith('src/app/'):group='client'
        elif name.startswith('src/assets/') and name.endswith(('.js','.css')):group='assets'
        else:group='full'
        path=Path(root)/name
        if path.is_file():result[group][name]=objects.get(name) or digest(path)
    if objects:
        dirty=set(p.decode() for p in subprocess.check_output(['git','-C',str(root),'diff','--name-only','-z','HEAD']).split(b'\0') if p)
        if dirty & set().union(*(set(v) for v in result.values())):raise ValueError('Uncommitted production inputs')
    return result


def inventory(folder):
    if any(p.is_symlink() for p in Path(folder).rglob('*')):raise ValueError('Symlinks are not reusable output files')
    return {p.relative_to(folder).as_posix():digest(p) for p in sorted(Path(folder).rglob('*')) if p.is_file()}


def read_cache(cache):
    cache=Path(cache)
    try:
        state=json.loads((cache/'state.json').read_text())
        if state['schema']!=SCHEMA or state['host']!=HOST:return None
        if not (cache/'site/editor.html').is_file() or not (cache/'site/app.js').is_file() or not (cache/'support/frontend.json').is_file():return None
        if state['outputs']!=inventory(cache/'site'):return None
        if state['support']!=inventory(cache/'support'):return None
        return state
    except (OSError,ValueError,KeyError):return None


def plan(root,cache):
    current=inputs(root);previous=read_cache(cache)
    if previous is None:return {'mode':'full','stages':['full'],'reason':'No verified reusable output','inputs':current,'publish':True}
    changed=[k for k in current if current[k]!=previous['inputs'].get(k)]
    stages=['full'] if 'full' in changed else [k for k in ('client','assets','profile') if k in changed]
    retry=bool(previous.get('source_sha')) and previous.get('source_sha')==source_sha(root)
    return {'mode':'+'.join(stages) or 'none','stages':stages,'reason':'Changed content fingerprints: '+', '.join(changed) if changed else 'Production inputs unchanged','inputs':current,'publish':bool(stages) or retry}


def source_sha(root):
    if not (Path(root)/'.git').exists():return None
    return subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()


def clean_output(root):
    target=Path(root)/'dist'
    if target.resolve().parent!=Path(root).resolve() or target.is_symlink():raise ValueError('Unsafe output directory')
    if target.exists():shutil.rmtree(target)


def full_build(root):
    subprocess.run([sys.executable,'build.py'],cwd=root,env={**os.environ,'SITE_URL':HOST},check=True)


def client_build(root):
    sys.path.insert(0,str(root))
    from frontend import build_client
    args=json.loads((Path(root)/'.build-support/frontend.json').read_text())
    build_client(Path(root),Path(root)/'dist',args['features'],args['policy'],args['guides'])


def asset_build(root,old,new):
    for name in set(old)|set(new):
        if old.get(name)==new.get(name):continue
        target=Path(root)/'dist'/Path(name).name
        if name in new:shutil.copyfile(Path(root)/name,target)
        elif target.exists():target.unlink()


def bust_assets(dist,names):
    revisions={name:digest(Path(dist)/name)[:16] for name in names if (Path(dist)/name).is_file()}
    for page in Path(dist).rglob('*.html'):
        before=page.read_text(encoding='utf-8');after=before
        for name,revision in revisions.items():
            after=re.sub(r'((?:src|href)="[^"]*?'+re.escape(name)+r')(?:\?[^"#]*)?(")',lambda m:m[1]+'?v='+revision+m[2],after)
        if after!=before:page.write_text(after,encoding='utf-8')


def build(root,cache,selected,full_runner=None,client_runner=None,profile_runner=None):
    root,cache=Path(root).resolve(),Path(cache).resolve();start=time.monotonic()
    state=read_cache(cache)
    if selected['inputs']!=inputs(root):raise ValueError('Source changed after planning')
    if selected['mode']!='full' and state is None:raise ValueError('Reusable output changed after planning')
    clean_output(root)
    if state and 'full' not in selected['stages']:
        shutil.copytree(cache/'site',root/'dist')
        support=root/'.build-support';support.mkdir(exist_ok=True)
        shutil.copytree(cache/'support',support,dirs_exist_ok=True)
    if 'full' in selected['stages']:
        (full_runner or full_build)(root)
    else:
        if 'client' in selected['stages']:(client_runner or client_build)(root)
        if 'assets' in selected['stages']:asset_build(root,state['inputs']['assets'],selected['inputs']['assets'])
    if selected['stages']:
        if profile_runner is None:
            from profile_build import render
            profile_runner=lambda r:render(r,r/'dist',HOST)
        # Full builds create the shell; client/assets builds retain it without music generation.
        if 'profile' in selected['stages'] or 'full' in selected['stages']:profile_runner(root)
        if 'client' in selected['stages'] or 'full' in selected['stages']:bust_assets(root/'dist',['app.js'])
        if 'assets' in selected['stages']:bust_assets(root/'dist',[Path(n).name for n in selected['inputs']['assets']])
    # Metadata-only finalization also runs after incremental stages; no image/music work.
    sys.path.insert(0, str(root))
    from site_update_dates import finalize_update_dates
    finalize_update_dates(root, root/'dist', set().union(*(set(v) for v in selected['inputs'].values())))
    bust_assets(root/'dist', ['metadata.js'])
    report={**selected,'elapsed_seconds':round(time.monotonic()-start,3),'image_processing':'full build only' if 'full' in selected['stages'] else 'not executed','music_generation':'executed' if 'full' in selected['stages'] else 'not executed'}
    return report


def save_cache(root,cache,selected):
    root,cache=Path(root).resolve(),Path(cache).resolve()
    if cache==root or not cache.is_relative_to(root) or cache==root/'dist':raise ValueError('Unsafe cache directory')
    if selected['inputs']!=inputs(root):raise ValueError('Production source changed during validation')
    cache.mkdir(parents=True,exist_ok=True)
    for name,source in [('site',root/'dist'),('support',root/'.build-support')]:
        target=cache/name
        if target.exists():shutil.rmtree(target)
        if source.exists():shutil.copytree(source,target)
        else:target.mkdir()
    state={'schema':SCHEMA,'host':HOST,'source_sha':source_sha(root),'inputs':selected['inputs'],'outputs':inventory(cache/'site'),'support':inventory(cache/'support')}
    (cache/'state.json').write_text(json.dumps(state,sort_keys=True),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['plan','build','cache']);parser.add_argument('--root',default='.');parser.add_argument('--cache',default='.build-cache');parser.add_argument('--plan',default='/tmp/build-plan.json');parser.add_argument('--github-output');args=parser.parse_args()
    root=Path(args.root).resolve();cache=root/args.cache
    if args.command=='plan':
        selected=plan(root,cache)
        if os.environ.get('FORCE_PUBLISH')=='true':selected['publish']=True
        Path(args.plan).write_text(json.dumps(selected,indent=2))
        if args.github_output:
            with open(args.github_output,'a') as out:
                for key,value in {'mode':selected['mode'],'full':str('full' in selected['stages']).lower(),'publish':str(selected['publish']).lower()}.items():out.write(key+'='+value+'\n')
        print(json.dumps(selected,ensure_ascii=False))
    else:
        selected=json.loads(Path(args.plan).read_text())
        if args.command=='build':
            report=build(root,cache,selected);Path(args.plan+'.report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
        else:save_cache(root,cache,selected)

if __name__=='__main__':main()
