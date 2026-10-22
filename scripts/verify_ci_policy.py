from approved_method_man import historical_method_man_file
from pathlib import Path
import hashlib,json
from approved_ci_policy import historical_ci_policy_file
R=Path(__file__).resolve().parents[1];F=json.loads((R/'scripts/fixtures/approved-ci-policy.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
assert set(F['files'])=={'releases.json','.github/workflows/pages.yml'}
for path,c in F['files'].items():
 data=(R/path).read_bytes();assert sha(historical_ci_policy_file(path,data))==c['beforeSHA256']
 try:historical_ci_policy_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Unapproved workflow/version drift accepted')
for path,h in F['contentHashes'].items():assert sha(historical_method_man_file(path,(R/path).read_bytes()))==h,path
from approved_static_work_count import historical_static_work_count_file
release=json.loads(historical_static_work_count_file('releases.json',(R/'releases.json').read_bytes()));assert release==dict(json.loads(F['files']['releases.json']['before']),version='22.4')
old=F['files']['.github/workflows/pages.yml']['before'];new=(R/'.github/workflows/pages.yml').read_text()
assert old.split('  deploy:\n',1)[1]==new.split('  deploy:\n',1)[1], 'Deployment guards/permissions must remain byte-identical'
assert '  validate:\n' in new and '    needs: validate\n' in new
assert historical_ci_policy_file('unrelated.txt',b'unchanged')==b'unchanged'
# Exercise the original downstream contract only for the changed inputs.
from approved_queue_scope import historical_queue_scope_file
queue_fixture=json.loads((R/'scripts/fixtures/approved-queue-scope.json').read_text())
for path in ('.github/workflows/pages.yml','releases.json'):
 data=(R/path).read_bytes()
 assert sha(historical_queue_scope_file(path,data))==queue_fixture['files'][path]['beforeSHA256'],path
 try:historical_queue_scope_file(path,data+b' ')
 except AssertionError:pass
 else:raise AssertionError('Downstream queue normalization accepted drift: '+path)
assert historical_queue_scope_file('unrelated.txt',b'unchanged')==b'unchanged'
print('Exact targeted-CI delta, unchanged deployment guards/permissions,501 authored content and strict historical normalization PASS')

# Security runtime selection must precede all application Node/npm commands.
runtime_step = "          node-version: '24.22.1'"
assert new.count(runtime_step) == 1
assert new.index(runtime_step) < new.index('      - name: Select directly affected checks')
assert 'uses: actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38 # v6' in new
assert 'package-manager-cache: false' in new
assert "process.versions.node !== '24.22.1'" in new
for changed in (new.replace("node-version: '24.22.1'", "node-version: '24.22.0'"),
                new.replace("process.versions.node !== '24.22.1'", "process.versions.node !== '24.22.0'"),
                new.replace('package-manager-cache: false', 'package-manager-cache: true')):
 try: historical_ci_policy_file('.github/workflows/pages.yml', changed.encode())
 except AssertionError: pass
 else: raise AssertionError('Unapproved Node.js runtime drift accepted')
print('Patched Node.js 24.22.1 selection, runtime assertion and downgrade rejection PASS')
