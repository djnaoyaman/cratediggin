#!/usr/bin/env python3
"""Run only validated plan entries, collecting status/duration without a shell.

The workflow owns browser installation and the :8765 /cratediggin preview server.
This runner never starts either for a static or empty browser stage.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from select_checks import (GitTree, SelectionError, command_identity, git,
                           load_manifests, safe_path, strict_json, write_json,
                           verified_sha, parse_name_status, select_changes)
from integrity_checks import BLOCKS


def validate_plan(plan):
    if plan.get('schema') != 1 or plan.get('blockers') != []:
        raise SelectionError('Cannot dispatch a missing/blocked selection plan')
    repo = Path(plan['repo']).resolve()
    if git(repo, 'rev-parse', 'HEAD').decode().strip() != plan['candidate_sha']:
        raise SelectionError('Dispatch HEAD changed since selection')
    verified_sha(repo, plan['base_sha'], 'Dispatch base')
    verified_sha(repo, plan['candidate_sha'], 'Dispatch candidate')
    after = GitTree(repo, plan['candidate_sha'])
    before = GitTree(repo, plan['base_sha'])
    if hashlib.sha256(after.read('scripts/ci/manifest.json')).hexdigest() != plan['candidate_manifest_sha256']:
        raise SelectionError('Dispatch manifest identity changed')
    manifest = load_manifests(before, after)
    registry = {c['id']: c for c in manifest['commands']}
    changes = parse_name_status(git(repo, 'diff', '--name-status', '-z', '--find-renames', plan['base_sha'], plan['candidate_sha'], '--'))
    derived = select_changes(manifest, changes, before.read, after.read, plan['event'])
    for key, expected in derived.items():
        if plan.get(key) != expected:
            raise SelectionError(f'Selection plan differs from immutable two-tree derivation: {key}')
    for key, sha in [('base_tree', plan['base_sha']), ('candidate_tree', plan['candidate_sha'])]:
        if plan.get(key) != git(repo, 'rev-parse', sha + '^{tree}').decode().strip():
            raise SelectionError('Recorded source tree identity changed')
    seen = set()
    for command in plan['selected']:
        ident = command.get('id')
        if ident in seen or ident not in registry or {k: v for k, v in command.items() if k != 'reasons'} != registry[ident]:
            raise SelectionError(f'Unregistered or altered selected invocation: {ident}')
        if not command.get('reasons'):
            raise SelectionError(f'Missing reason chain for {ident}')
        seen.add(ident)
    if plan['browser_required'] != any(c['kind'] == 'browser' for c in plan['selected']):
        raise SelectionError('Browser flag disagrees with selected invocation registry')
    if (plan['event'] in {'push', 'workflow_dispatch'} or any(c['requires_build'] for c in plan['selected'])) and not plan['build_required']:
        raise SelectionError('Fresh build required by event or selected product')
    if plan['source_drift_check'] != plan['build_required']:
        raise SelectionError('Build source-drift guard missing')
    for path in plan['syntax']:
        if not safe_path(path).startswith('dist/') or not path.endswith('.js') or path.count('/') != 1:
            raise SelectionError('Invalid emitted JS syntax path')
    if not set(plan['integrity_groups']) <= set(BLOCKS):
        raise SelectionError('Unknown integrity block in plan')
    if any(BLOCKS[x]['generated_inputs'] for x in plan['integrity_groups']) and not plan['build_required']:
        raise SelectionError('Generated integrity block requires a fresh build')
    paths = {'scripts/ci/run_checks.py', 'scripts/ci/select_checks.py', 'scripts/ci/integrity_checks.py'}
    paths.update(c['argv'][1] for c in plan['selected'] if c['argv'][1] != '-m')
    paths.update(plan['python_compile'])
    for path in paths:
        safe_path(path)
        source = after.read(path)
        target = repo / path
        if source is None or target.is_symlink() or not target.is_file() or target.read_bytes() != source:
            raise SelectionError(f'{path}: dispatch source differs from recorded candidate')
    return repo


def stage_commands(plan, stage):
    if stage not in {'integrity', 'static', 'browser'}:
        raise SelectionError(f'Unknown stage: {stage}')
    if stage != 'integrity':
        return [c for c in plan['selected'] if c['kind'] == stage]
    commands = []
    for path in plan['syntax']:
        commands.append({'id': 'syntax:' + path, 'argv': ['node', '--check', path], 'env': {}, 'reasons': ['Affected emitted JavaScript syntax']})
    if plan['python_compile']:
        commands.append({'id': 'python-compile', 'argv': ['python', '-m', 'py_compile', *plan['python_compile']], 'env': {}, 'reasons': ['Affected Python source compilation']})
    for group in plan['integrity_groups']:
        commands.append({'id': 'integrity:' + group, 'argv': ['python', 'scripts/ci/integrity_checks.py', '--root', '.', '--group', group], 'env': {}, 'reasons': ['Declared generated/source integrity block']})
    if plan['source_drift_check']:
        commands.append({'id': 'source-drift', 'argv': ['git', 'diff', '--exit-code', '--', 'src', 'templates'], 'env': {}, 'reasons': ['Build must not rewrite authored src/templates']})
    return commands


def execute_commands(commands, repo, invoke=None, clock=None, timeout=600):
    invoke = invoke or subprocess.run
    clock = clock or time.monotonic
    results = []
    managed_environment = {'INLINE_PLAYER_TRACK'} | {key for command in commands for key in command['env']}
    for command in commands:
        env = os.environ.copy()
        for key in managed_environment:
            env.pop(key, None)
        # Python assertions are part of the integrity and historical contracts.
        env.pop('PYTHONOPTIMIZE', None)
        env.update(command['env'])
        start = clock()
        print('RUN ' + command['id'] + ': ' + json.dumps(command['argv']), flush=True)
        error = None
        try:
            completed = invoke(command['argv'], cwd=str(repo), env=env, check=False, timeout=timeout)
            code = completed.returncode
        except subprocess.TimeoutExpired:
            code, error = 124, f'Command exceeded the {timeout}-second limit'
        except OSError as exc:
            code, error = 127, str(exc)
        elapsed = max(0.0, clock() - start)
        result = {'id': command['id'], 'argv': command['argv'], 'env': command['env'], 'returncode': code, 'duration_seconds': round(elapsed, 4), 'status': 'passed' if code == 0 else 'failed', 'reasons': command['reasons']}
        if error:
            result['error'] = error
        results.append(result)
        print(f'{result["status"].upper()} {command["id"]} ({elapsed:.3f}s)', flush=True)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--stage', choices=['integrity', 'static', 'browser'], required=True)
    args = parser.parse_args(argv)
    report_path = args.plan.with_name(args.plan.stem + '-' + args.stage + '-results.json')
    try:
        plan = strict_json(args.plan.read_bytes(), str(args.plan))
        repo = validate_plan(plan)
        results = execute_commands(stage_commands(plan, args.stage), repo)
        failed = any(r['returncode'] != 0 for r in results)
        report = {'stage': args.stage, 'candidate_sha': plan['candidate_sha'], 'results': results, 'status': 'failed' if failed else ('passed' if results else 'not-selected'), 'skipped_not_passed': len([c for c in plan['skipped']]), 'duration_seconds': sum(r['duration_seconds'] for r in results)}
        write_json(report_path, report)
        summary = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary:
            with open(summary, 'a', encoding='utf-8') as stream:
                stream.write(f'\nTargeted {args.stage}: {report["status"]}; {len(results)} dispatched, {report["duration_seconds"]:.2f}s.\n')
                for result in results:
                    stream.write(f'- {result["id"]}: {result["status"]}, exit {result["returncode"]}, {result["duration_seconds"]:.2f}s\n')
        return 1 if failed else 0
    except (SelectionError, OSError, KeyError, TypeError) as exc:
        write_json(report_path, {'stage': args.stage, 'status': 'blocked', 'error': str(exc), 'results': []})
        print('DISPATCH BLOCKED: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
