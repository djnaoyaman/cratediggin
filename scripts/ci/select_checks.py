#!/usr/bin/env python3
"""Fail-closed, two-tree selection for the existing stable Pages validate job."""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
import shlex
import subprocess
import sys

MANIFEST_PATH = 'scripts/ci/manifest.json'
BOOTSTRAP_PATH = 'scripts/ci/bootstrap-pages.yml'
BOOTSTRAP_COMMIT = 'b027a4b5b938b9f1d7f56a27bb629e683f9a749e'
BOOTSTRAP_SHA256 = '1acf04217aef8ccb551756cb1a4458a1403c9f34aa44fd22b56069c12177d124'
EVENTS = {'pull_request', 'push', 'workflow_dispatch'}


class SelectionError(ValueError):
    """The exact required comparison/coverage correction, never a fallback."""


def safe_path(value):
    if not isinstance(value, str) or not value or '\0' in value or value.startswith('/'):
        raise SelectionError(f'Invalid repository path: {value!r}')
    if any(part in ('', '.', '..') for part in value.split('/')) or '\\' in value:
        raise SelectionError(f'Unsafe repository path: {value!r}')
    return value


def parse_name_status(raw):
    if not raw:
        return []
    if not raw.endswith(b'\0'):
        raise SelectionError('Truncated NUL-delimited Git diff')
    try:
        tokens = raw[:-1].decode('utf-8', errors='strict').split('\0')
    except UnicodeDecodeError as exc:
        raise SelectionError('Non-UTF-8 Git path requires explicit mapping') from exc
    changes = []
    i = 0
    while i < len(tokens):
        status = tokens[i]
        i += 1
        if re.fullmatch(r'[RC](?:0\d\d|100)', status):
            count = 2
        elif status in {'A', 'M', 'D', 'T'}:
            count = 1
        else:
            raise SelectionError(f'Unsupported Git change status: {status!r}')
        if i + count > len(tokens):
            raise SelectionError(f'Truncated Git diff record: {status}')
        paths = [safe_path(p) for p in tokens[i:i + count]]
        i += count
        old = None if status == 'A' else paths[0]
        new = None if status == 'D' else paths[-1]
        changes.append({'status': status, 'old_path': old, 'new_path': new})
    return changes


def strict_json(raw, description):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise SelectionError(f'Duplicate JSON key {key!r} in {description}')
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except (ValueError, UnicodeError) as exc:
        raise SelectionError(f'Invalid JSON in {description}: {exc}') from exc


def command_identity(command):
    return json.dumps({'argv': command['argv'], 'env': command['env']}, sort_keys=True, separators=(',', ':'))


def workflow_invocations(raw):
    """Inventory only literal legacy script calls, preserving environment variants."""
    commands = []
    for line in raw.decode('utf-8').splitlines():
        line = line.strip()
        if not re.match(r'(?:(?:[A-Z_][A-Z_0-9]*=[^ ]+) )?(?:python|node) scripts/', line):
            continue
        parts = shlex.split(line)
        env = {}
        if '=' in parts[0]:
            name, value = parts.pop(0).split('=', 1)
            env[name] = value
        if '||' in parts:
            parts = parts[:parts.index('||')]
        commands.append({'argv': parts, 'env': env})
    return commands


def validate_manifest(manifest, snapshot):
    if not isinstance(manifest, dict) or manifest.get('schema') != 1:
        raise SelectionError('Unsupported dependency manifest schema')
    if manifest.get('bootstrap_commit') != BOOTSTRAP_COMMIT or manifest.get('bootstrap_workflow_sha256') != BOOTSTRAP_SHA256:
        raise SelectionError('Immutable bootstrap identity changed')
    if hashlib.sha256(snapshot).hexdigest() != BOOTSTRAP_SHA256:
        raise SelectionError('Immutable bootstrap workflow bytes changed')
    commands = manifest.get('commands')
    if not isinstance(commands, list) or not commands:
        raise SelectionError('Missing invocation registry')
    by_id = {}
    identities = set()
    for command in commands:
        if not isinstance(command, dict):
            raise SelectionError('Invalid invocation entry')
        ident = command.get('id')
        argv, env = command.get('argv'), command.get('env')
        if not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9-]+', ident) or ident in by_id:
            raise SelectionError(f'Invalid/duplicate command ID: {ident!r}')
        if not isinstance(argv, list) or len(argv) < 2 or any(not isinstance(x, str) or '\0' in x for x in argv):
            raise SelectionError(f'Invalid argument array: {ident}')
        if argv[0] not in {'python', 'python3', 'node'}:
            raise SelectionError(f'Unregistered interpreter: {ident}')
        if argv[1] == '-m':
            if argv != ['python', '-m', 'unittest', 'discover', '-s', 'scripts/ci', '-p', 'test_*.py'] or ident != 'ci-policy-units':
                raise SelectionError(f'Unregistered module command: {ident}')
        elif not safe_path(argv[1]).startswith('scripts/'):
            raise SelectionError(f'Invalid script command: {ident}')
        if not isinstance(env, dict) or any(not re.fullmatch(r'[A-Z_][A-Z_0-9]*', k) or not isinstance(v, str) or '\0' in v for k, v in env.items()):
            raise SelectionError(f'Invalid invocation environment: {ident}')
        if command.get('kind') not in {'static', 'browser'} or type(command.get('requires_build')) is not bool or type(command.get('legacy')) is not bool:
            raise SelectionError(f'Invalid invocation stage/build contract: {ident}')
        identity = command_identity(command)
        if identity in identities:
            raise SelectionError(f'Duplicate invocation: {ident}')
        identities.add(identity)
        by_id[ident] = command
    frozen = [command_identity(c) for c in workflow_invocations(snapshot)]
    legacy = [command_identity(c) for c in commands if c['legacy']]
    if len(frozen) != 130 or len(set(frozen)) != 129 or len(legacy) != 129 or set(legacy) != set(frozen) or manifest.get('legacy_count') != 129:
        raise SelectionError('Legacy registry must preserve all 129 distinct frozen invocations')
    duplicates = [x for x in set(frozen) if frozen.count(x) > 1]
    if len(duplicates) != 1 or 'scripts/verify_requested_six_browser.cjs' not in duplicates[0]:
        raise SelectionError('Unexpected bootstrap duplicate removal')
    for group, members in manifest.get('groups', {}).items():
        if not isinstance(members, list) or not members or len(members) != len(set(members)) or any(x not in by_id for x in members):
            raise SelectionError(f'Invalid invocation group: {group}')
    for path, groups in manifest.get('runtime_rules', {}).items():
        safe_path(path)
        if not groups or any(g not in manifest['groups'] for g in groups):
            raise SelectionError(f'Missing runtime behavior group for {path}')
    for path, rules in manifest.get('scoped_runtime_changes', {}).items():
        if path not in manifest['runtime_rules'] or not isinstance(rules, list) or not rules:
            raise SelectionError(f'Invalid scoped runtime path: {path}')
        for rule in rules:
            if set(rule) != {'before_sha256','after_sha256','groups'} or any(not isinstance(rule[k], str) or not re.fullmatch('[0-9a-f]{64}', rule[k]) for k in ('before_sha256','after_sha256')):
                raise SelectionError(f'Invalid scoped runtime identity: {path}')
            if not rule['groups'] or any(g not in manifest['groups'] for g in rule['groups']):
                raise SelectionError(f'Invalid scoped runtime groups: {path}')
    for path, rules in manifest.get('scoped_content_changes', {}).items():
        safe_path(path)
        if path not in manifest['data_paths'] and not any(path.startswith(prefix) for prefix in manifest['blocked_asset_prefixes']):
            raise SelectionError(f'Invalid scoped content path: {path}')
        if not isinstance(rules, list) or not rules:
            raise SelectionError(f'Empty scoped content rules: {path}')
        for rule in rules:
            if set(rule) != {'before_sha256','after_sha256','groups'} or any(rule[k] is not None and (not isinstance(rule[k], str) or not re.fullmatch('[0-9a-f]{64}',rule[k])) for k in ('before_sha256','after_sha256')) or rule['after_sha256'] is None:
                raise SelectionError(f'Invalid scoped content identity: {path}')
            if not rule['groups'] or any(g not in manifest['groups'] for g in rule['groups']):
                raise SelectionError(f'Invalid scoped content groups: {path}')
    for owner, dependencies in manifest.get('script_dependencies', {}).items():
        safe_path(owner)
        for path in dependencies:
            safe_path(path)
    for key in ('policy_paths', 'policy_files', 'data_paths', 'nonruntime_paths', 'syntax_existing'):
        for path in manifest.get(key, []):
            safe_path(path)
    from integrity_checks import BLOCKS
    if set(manifest.get('integrity_ids', [])) != set(BLOCKS):
        raise SelectionError('Original inline integrity block inventory changed')
    return by_id


def merge_manifests(base, candidate):
    """Union old/new coverage. Changing a command identity needs a new stable ID."""
    merged = json.loads(json.dumps(candidate))
    commands = {c['id']: c for c in candidate['commands']}
    for command in base['commands']:
        if command['id'] in commands and command != commands[command['id']]:
            raise SelectionError(f'Changed invocation contract needs a new ID: {command["id"]}')
        if command['id'] not in commands:
            merged['commands'].append(command)
    for field in ('groups', 'runtime_rules', 'script_dependencies'):
        for key, values in base[field].items():
            merged[field][key] = list(dict.fromkeys(merged[field].get(key, []) + values))
    for field in ('policy_paths', 'policy_files', 'data_paths', 'nonruntime_paths', 'syntax_existing', 'integrity_ids', 'blocked_asset_prefixes'):
        merged[field] = list(dict.fromkeys(merged[field] + base[field]))
    for path, rules in base.get('scoped_runtime_changes', {}).items():
        target = merged.setdefault('scoped_runtime_changes', {}).setdefault(path, [])
        for rule in rules:
            if rule not in target:
                target.append(rule)
    for path, rules in base.get('scoped_content_changes', {}).items():
        target = merged.setdefault('scoped_content_changes', {}).setdefault(path, [])
        for rule in rules:
            if rule not in target:
                target.append(rule)
    return merged


def scoped_runtime_groups(manifest, path, read_before, read_after):
    if read_before is None or read_after is None:
        return None
    before, after = read_before(path), read_after(path)
    if before is None or after is None:
        return None
    groups = []
    for rule in manifest.get('scoped_runtime_changes', {}).get(path, []):
        if hashlib.sha256(before).hexdigest() == rule['before_sha256'] and hashlib.sha256(after).hexdigest() == rule['after_sha256']:
            groups.extend(rule['groups'])
    return list(dict.fromkeys(groups)) or None


def scoped_content_groups(manifest, path, read_before, read_after):
    if read_before is None or read_after is None:
        return None
    before,after=read_before(path),read_after(path)
    digest=lambda data: None if data is None else hashlib.sha256(data).hexdigest()
    groups=[]
    for rule in manifest.get('scoped_content_changes',{}).get(path,[]):
        if digest(before)==rule['before_sha256'] and digest(after)==rule['after_sha256']:
            groups.extend(rule['groups'])
    return list(dict.fromkeys(groups)) or None


def reverse_consumers(paths, dependencies):
    reasons = {path: [path] for path in paths}
    pending = list(paths)
    while pending:
        changed = pending.pop(0)
        for consumer, inputs in dependencies.items():
            if changed in inputs and consumer not in reasons:
                reasons[consumer] = reasons[changed] + [consumer]
                pending.append(consumer)
    return reasons


def version_only(before, after):
    old, new = strict_json(before, 'base releases.json'), strict_json(after, 'candidate releases.json')
    expected = {'version', 'timezone', 'policy', 'history'}
    if not isinstance(old, dict) or not isinstance(new, dict) or set(old) != expected or set(new) != expected:
        raise SelectionError('releases.json requires reviewed field/schema mapping')
    for obj in (old, new):
        if not isinstance(obj['version'], str) or not re.fullmatch(r'\d+\.\d+', obj['version']) or not isinstance(obj['history'], list) or not isinstance(obj['timezone'], str) or not isinstance(obj['policy'], str):
            raise SelectionError('Invalid releases.json version/schema')
    if {k: v for k, v in old.items() if k != 'version'} != {k: v for k, v in new.items() if k != 'version'}:
        raise SelectionError('releases.json non-version fields require explicit record/field mapping')
    return True


def select_changes(manifest, changes, read_before=None, read_after=None, event='pull_request'):
    if event not in EVENTS:
        raise SelectionError(f'Unsupported event: {event}')
    commands = {c['id']: c for c in manifest['commands']}
    selected = {}
    syntax, compile_paths, integrity = set(), set(), set()
    blockers, classified = [], []
    build = event in {'push', 'workflow_dispatch'}
    policy_paths = set(manifest['policy_paths'] + manifest['policy_files'])
    command_paths = {c['argv'][1] for c in commands.values() if c['argv'][1] != '-m'}
    changed_paths = {p for c in changes for p in (c['old_path'], c['new_path']) if p}
    policy_changed = bool(changed_paths & policy_paths)

    def add(ident, reason):
        selected.setdefault(ident, [])
        if reason not in selected[ident]:
            selected[ident].append(reason)

    def add_group(group, reason):
        for ident in manifest['groups'][group]:
            add(ident, reason + ' → ' + group + ' → ' + commands[ident]['label'])

    for path in sorted(changed_paths):
        safe_path(path)
        if path.endswith('.py') and read_after is not None and read_after(path) is not None:
            compile_paths.add(path)
        if path in policy_paths:
            add_group('policy', path + ' → CI policy/dispatch/strict preservation contract')
            classified.append({'path': path, 'scope': 'policy'})
        elif path in manifest['runtime_rules']:
            narrow = scoped_runtime_groups(manifest, path, read_before, read_after)
            if narrow is not None:
                for group in narrow:
                    add_group(group, path + ' → exact reviewed before/after rendering delta')
                build = True
                classified.append({'path': path, 'scope': 'exact runtime delta'})
                continue
            for group in manifest['runtime_rules'][path]:
                add_group(group, path + ' → explicitly declared direct runtime consumers')
            build = True
            if path.startswith('src/app/'):
                syntax.add('dist/app.js')
            elif path.startswith('src/assets/') and path.endswith('.js'):
                syntax.add('dist/' + PurePosixPath(path).name)
            else:
                syntax.update(manifest['syntax_existing'])
            if path in {'build.py', 'frontend.py', 'discovery.py', 'render_editorial.py', 'src/app/editorial.js', 'templates/index.html'}:
                integrity.add('artist-discovery')
            if path in {'build.py', 'frontend.py', 'src/app/song-ui.js'}:
                integrity.add('deep-dive-output')
            classified.append({'path': path, 'scope': 'runtime'})
        elif path == 'releases.json':
            try:
                if read_before is None or read_after is None or read_before(path) is None or read_after(path) is None:
                    raise SelectionError('releases.json requires both versions for exact version-only classification')
                version_only(read_before(path), read_after(path))
                add_group('release', 'releases.json → exact version-only metadata/About delta')
                # The existing reviewed guard rejects unapproved version bytes; no hash refresh here.
                add('ci-policy-preservation', 'releases.json → reviewed version bytes and historical normalization')
                build = True
                syntax.update(manifest['syntax_existing'])
                classified.append({'path': path, 'scope': 'version-only'})
            except SelectionError as exc:
                blockers.append(str(exc))
        elif path in manifest.get('scoped_content_changes', {}):
            narrow=scoped_content_groups(manifest,path,read_before,read_after)
            if narrow is None:
                blockers.append(f'{path}: content bytes differ from reviewed append/asset mapping')
            else:
                for group in narrow:
                    add_group(group,path+' → exact reviewed content/asset delta')
                build=True
                classified.append({'path':path,'scope':'exact content delta'})
        elif path in manifest['data_paths']:
            blockers.append(f'{path}: reviewed stable-record/field/reference coverage is required; no full-suite fallback')
        elif any(path.startswith(prefix) for prefix in manifest['blocked_asset_prefixes']):
            blockers.append(f'{path}: explicit old/new asset owner and scoped assertion mapping is required')
        elif path in command_paths or path in manifest['script_dependencies'] or any(path in ds for ds in manifest['script_dependencies'].values()):
            if PurePosixPath(path).name.startswith('approved_') or path.startswith('scripts/fixtures/'):
                blockers.append(f'{path}: scoped historical assertion equivalence and negative normalizer cases are required')
                continue
            consumers = reverse_consumers({path}, manifest['script_dependencies'])
            matches = [c for c in commands.values() if c['argv'][1] in consumers]
            if not matches:
                blockers.append(f'{path}: missing registered reverse-consumer assertion')
            for command in matches:
                add(command['id'], ' → '.join(consumers[command['argv'][1]]) + ' → ' + command['label'])
            classified.append({'path': path, 'scope': 'test/helper'})
        elif path in manifest['nonruntime_paths']:
            classified.append({'path': path, 'scope': 'explicit nonruntime file'})
        else:
            blockers.append(f'{path}: missing explicit changed-path/dependency mapping')
    # Never infer broad behavior from the shared app.js output alone.
    build = build or any(commands[c]['requires_build'] for c in selected)
    if build:
        if not syntax:
            syntax.update(manifest['syntax_existing'])
        integrity.update({'generated-pages', 'social-card-count', 'project-pages-urls', 'touch-icon'})
        compile_paths.update({'build.py', 'scripts/audit_catalog.py'})
    if policy_changed:
        compile_paths.update(p for p in manifest['policy_files'] if p.endswith('.py'))
    return {
        'schema': 1, 'event': event, 'build_required': build,
        'browser_required': any(commands[c]['kind'] == 'browser' for c in selected),
        'selected': [{**command, 'reasons': selected[command['id']]} for command in manifest['commands'] if command['id'] in selected],
        'skipped': [{'id': c['id'], 'label': c['label'], 'reason': 'No declared changed-path/direct-dependency edge; not executed, not a pass'} for c in manifest['commands'] if c['id'] not in selected],
        'syntax': sorted(syntax), 'python_compile': sorted(compile_paths),
        'integrity_groups': [x for x in manifest['integrity_ids'] if x in integrity],
        'source_drift_check': build, 'changes': changes, 'classified': classified, 'blockers': blockers,
    }


class GitTree:
    def __init__(self, repo, revision):
        self.repo, self.revision = Path(repo).resolve(), revision
        self.entries = {}
        raw = git(self.repo, 'ls-tree', '-rz', '--full-tree', revision)
        for record in raw.split(b'\0'):
            if not record:
                continue
            prefix, path = record.split(b'\t', 1)
            mode, kind, oid = prefix.decode().split()
            try:
                path = safe_path(path.decode('utf-8'))
            except UnicodeDecodeError as exc:
                raise SelectionError('Non-UTF-8 tree filename requires mapping') from exc
            self.entries[path] = (mode, kind, oid)
        self.cache = {}

    def read(self, path):
        safe_path(path)
        entry = self.entries.get(path)
        if entry is None:
            return None
        if entry[0] not in {'100644', '100755'} or entry[1] != 'blob':
            raise SelectionError(f'{path}: symlink/submodule/non-file mode requires explicit mapping')
        if path not in self.cache:
            self.cache[path] = git(self.repo, 'cat-file', 'blob', entry[2])
        return self.cache[path]


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise SelectionError('Git comparison unavailable: ' + result.stderr.decode('utf-8', errors='replace').strip())
    return result.stdout


def verified_sha(repo, value, label):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{40}', value) or value == '0' * 40:
        raise SelectionError(f'{label} requires an available exact nonzero 40-character commit SHA')
    resolved = git(repo, 'rev-parse', '--verify', value + '^{commit}').decode().strip()
    if resolved != value:
        raise SelectionError(f'{label} commit identity mismatch')
    return value


def load_manifests(before, after):
    raw = after.read(MANIFEST_PATH)
    snapshot = after.read(BOOTSTRAP_PATH)
    if raw is None or snapshot is None:
        raise SelectionError('Candidate dependency manifest/bootstrap snapshot missing')
    candidate = strict_json(raw, MANIFEST_PATH)
    validate_manifest(candidate, snapshot)
    old = before.read(MANIFEST_PATH)
    if old is None:
        if before.revision != BOOTSTRAP_COMMIT or before.read('.github/workflows/pages.yml') != snapshot:
            raise SelectionError('Missing base manifest: bootstrap is permitted only for the exact frozen baseline commit/workflow')
        base = candidate
    else:
        base = strict_json(old, 'base ' + MANIFEST_PATH)
        old_snapshot = before.read(BOOTSTRAP_PATH)
        if old_snapshot is None:
            raise SelectionError('Base immutable workflow snapshot missing')
        validate_manifest(base, old_snapshot)
    return merge_manifests(base, candidate)


def validate_app_inventory(tree, manifest):
    raw = tree.read('src/app/order.json')
    if raw is None:
        raise SelectionError('Missing src/app/order.json runtime inventory')
    order = strict_json(raw, 'src/app/order.json')
    if not isinstance(order, list) or not order or any(not isinstance(p, str) or '/' in p or not p.endswith('.js') for p in order) or len(set(order)) != len(order):
        raise SelectionError('Invalid/duplicate app order entries')
    expected = {'src/app/' + p for p in order}
    actual = {p for p in tree.entries if p.startswith('src/app/') and p.endswith('.js')}
    if expected != actual:
        raise SelectionError('App order/module inventory mismatch: ' + repr(sorted(expected ^ actual)))
    for path in expected:
        tree.read(path)
        if path not in manifest['runtime_rules']:
            raise SelectionError(f'{path}: missing app runtime mapping')


def relative_require_edges(path, source, available):
    """Resolve literal local CommonJS reads without importing/executing the file."""
    found = set()
    for match in re.finditer(r"require\s*\(\s*(['\"])(\.[^'\"]+)\1\s*\)", source):
        literal = match.group(2)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), literal))
        safe_path(resolved)
        candidates = [resolved, resolved + '.js', resolved + '.cjs', resolved + '.json', resolved + '/index.js']
        target = next((p for p in candidates if p in available), None)
        if target is None:
            raise SelectionError(f'{path}: unresolved local require dependency: {literal!r}')
        found.add(target)
    return found


def validate_script_edges(tree, manifest):
    """Check declared lower-level helper edges against imports/literal script reads.

    Fixture protected-path inventories are NOT promoted to whole-wrapper runs.
    Changes to those unadapted assertion contracts block in select_changes.
    """
    paths = {p for p in tree.entries if p.startswith('scripts/') and p.count('/') == 1 and p.endswith(('.py', '.cjs', '.js'))}
    modules = {PurePosixPath(p).stem: p for p in paths if p.endswith('.py')}
    for path in sorted(paths):
        source = tree.read(path).decode('utf-8')
        found = set()
        if path.endswith('.py'):
            try:
                nodes = ast.walk(ast.parse(source))
                for node in nodes:
                    if isinstance(node, ast.ImportFrom) and node.module in modules:
                        found.add(modules[node.module])
                    elif isinstance(node, ast.Import):
                        found.update(modules[a.name] for a in node.names if a.name in modules)
            except SyntaxError as exc:
                raise SelectionError(f'{path}: invalid Python helper inventory: {exc}') from exc
        for value in re.findall(r"['\"]([^'\"\n]{1,180})['\"]", source):
            value = value.lstrip('/')
            if value.startswith('scripts/') and value in tree.entries:
                found.add(value)
        if path.endswith(('.js', '.cjs')):
            found.update(relative_require_edges(path, source, tree.entries))
        missing = found - set(manifest['script_dependencies'].get(path, []))
        if missing:
            raise SelectionError(f'{path}: missing explicit helper dependency edges: {sorted(missing)!r}')


def build_plan(repo, base, candidate, event):
    if event not in EVENTS:
        raise SelectionError('Unsupported event requires explicit event mapping')
    repo = Path(repo).resolve()
    verified_sha(repo, base, 'Comparison base')
    verified_sha(repo, candidate, 'Candidate')
    if git(repo, 'rev-parse', 'HEAD').decode().strip() != candidate:
        raise SelectionError('Checked-out HEAD differs from exact candidate SHA')
    git(repo, 'diff', '--exit-code', '--quiet', candidate, '--')
    before, after = GitTree(repo, base), GitTree(repo, candidate)
    manifest = load_manifests(before, after)
    validate_app_inventory(before, manifest)
    validate_app_inventory(after, manifest)
    validate_script_edges(before, manifest)
    validate_script_edges(after, manifest)
    changes = parse_name_status(git(repo, 'diff', '--name-status', '-z', '--find-renames', base, candidate, '--'))
    for change in changes:
        if change['old_path']:
            before.read(change['old_path'])
        if change['new_path']:
            after.read(change['new_path'])
    plan = select_changes(manifest, changes, before.read, after.read, event)
    for command in plan['selected']:
        script = command['argv'][1]
        if script != '-m' and after.read(script) is None:
            plan['blockers'].append(f'{script}: selected base/candidate invocation is unavailable in candidate')
    for path in plan['python_compile']:
        if after.read(path) is None:
            plan['blockers'].append(f'{path}: required Python compilation input is unavailable')
    plan.update({'repo': str(repo), 'base_sha': base, 'candidate_sha': candidate,
                 'base_tree': git(repo, 'rev-parse', base + '^{tree}').decode().strip(),
                 'candidate_tree': git(repo, 'rev-parse', candidate + '^{tree}').decode().strip(),
                 'manifest_version': manifest['schema'],
                 'candidate_manifest_sha256': hashlib.sha256(after.read(MANIFEST_PATH)).hexdigest()})
    return plan


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--base', required=True)
    parser.add_argument('--candidate', required=True)
    parser.add_argument('--event', choices=sorted(EVENTS), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--github-output', type=Path)
    args = parser.parse_args(argv)
    try:
        plan = build_plan(args.repo, args.base, args.candidate, args.event)
    except (SelectionError, OSError, KeyError, TypeError) as exc:
        plan = {'schema': 1, 'blockers': [str(exc)], 'selected': [], 'skipped': [], 'build_required': False, 'browser_required': False}
    write_json(args.output, plan)
    if plan['blockers']:
        for blocker in plan['blockers']:
            print('MAPPING REQUIRED: ' + blocker, file=sys.stderr)
        return 2
    if args.github_output:
        with args.github_output.open('a', encoding='utf-8') as stream:
            stream.write(f'build_required={str(plan["build_required"]).lower()}\nbrowser_required={str(plan["browser_required"]).lower()}\n')
    print(json.dumps({'base': plan['base_sha'], 'candidate': plan['candidate_sha'], 'selected': len(plan['selected']), 'skipped_not_passed': len(plan['skipped']), 'build_required': plan['build_required'], 'browser_required': plan['browser_required']}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
