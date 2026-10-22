"""Exact targeted-CI workflow/version delta for historical preservation checks."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def historical_ci_policy_file(path,data):
    # Accept only the exact October 2026 Node.js security runtime delta.
    # Preserve every historical workflow byte and reject any unrelated drift.
    if path == '.github/workflows/pages.yml' and hashlib.sha256(data).hexdigest() == '37d6c8233b2628102fbcbf045d5c89f852ce9f288785cc2fa81cbdc28a220d54':
        step = b'      - name: Set up patched Node.js\n        uses: actions/setup-node@249970729cb0ef3589644e2896645e5dc5ba9c38 # v6\n        with:\n          node-version: \'24.22.1\'\n          package-manager-cache: false\n      - name: Verify patched Node.js runtime\n        run: node -e "if (process.versions.node !== \'24.22.1\') throw new Error(\'Unexpected Node.js runtime\'); console.log(process.version)"\n'
        assert data.count(step) == 1
        data = data.replace(step, b'', 1)
        assert hashlib.sha256(data).hexdigest() == 'c553ee7beb67b642ee2c7ac0d0da031ab599d1748e749d5a926b4295a73dc97e'
    from approved_static_work_count import historical_static_work_count_file
    data=historical_static_work_count_file(path,data)
    f=json.loads((ROOT/'scripts/fixtures/approved-ci-policy.json').read_text())
    c=f['files'].get(path)
    if c is None:return data
    assert hashlib.sha256(data).hexdigest()==c['afterSHA256'],'Unapproved CI-policy drift: '+path
    before=c['before'].encode()
    assert hashlib.sha256(before).hexdigest()==c['beforeSHA256'],path
    return before
