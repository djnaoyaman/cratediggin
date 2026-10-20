#!/usr/bin/env python3
"""Synthetic runner contracts, with no build/browser/network execution."""
import copy
import importlib
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_checks as runner
import select_checks as selector
import test_select_checks as fixtures


class RunnerUnitTests(unittest.TestCase):
    def test_environment_distinct_dispatch_no_shell(self):
        commands = [c for c in fixtures.manifest()['commands'] if c['argv'][1] == 'scripts/verify_inline_player_browser.cjs']
        for c in commands: c['reasons'] = ['explicit environment contract']
        calls = []
        def invoke(argv, **kwargs):
            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(argv, 0)
        with mock.patch.dict('os.environ', {'PYTHONOPTIMIZE': '2', 'INLINE_PLAYER_TRACK': 'unwanted-inherited-case'}):
            results = runner.execute_commands(commands, Path('/synthetic'), invoke=invoke)
        self.assertEqual(len(results), 2)
        self.assertEqual(calls[0][0], calls[1][0])
        self.assertNotIn('INLINE_PLAYER_TRACK', calls[0][1]['env'])
        self.assertEqual(calls[1][1]['env']['INLINE_PLAYER_TRACK'], 'ini-grown-man-sport')
        self.assertNotIn('shell', calls[0][1])
        self.assertNotIn('PYTHONOPTIMIZE', calls[0][1]['env'])
        self.assertEqual(calls[0][1]['timeout'], 600)
        self.assertTrue(all(c['status'] == 'passed' for c in results))

    def test_failure_timeout_and_missing_executable_collect_and_fail(self):
        commands = [{'id': f'case-{i}', 'argv': ['node', f'scripts/case-{i}.cjs'], 'env': {}, 'reasons': ['test']} for i in range(4)]
        calls = []
        def invoke(argv, **kwargs):
            calls.append(argv)
            if len(calls) == 1: return subprocess.CompletedProcess(argv, 7)
            if len(calls) == 2: raise FileNotFoundError('synthetic missing executable')
            if len(calls) == 3: raise subprocess.TimeoutExpired(argv, kwargs['timeout'])
            return subprocess.CompletedProcess(argv, 0)
        results = runner.execute_commands(commands, '.', invoke=invoke)
        self.assertEqual([r['returncode'] for r in results], [7, 127, 124, 0])
        self.assertEqual(len(calls), 4)
        self.assertTrue(any(r['status'] == 'failed' for r in results))

    def test_empty_browser_stage_has_no_install_server_or_dispatch(self):
        p = selector.select_changes(fixtures.manifest(), [])
        commands = runner.stage_commands(p, 'browser')
        invoke = mock.Mock()
        self.assertEqual(runner.execute_commands(commands, '.', invoke=invoke), [])
        invoke.assert_not_called()
        self.assertEqual(runner.stage_commands(p, 'integrity'), [])

    def test_integrity_includes_syntax_compile_blocks_and_drift(self):
        p = selector.select_changes(fixtures.manifest(), [], event='push')
        commands = runner.stage_commands(p, 'integrity')
        self.assertEqual(commands[-1]['argv'], ['git', 'diff', '--exit-code', '--', 'src', 'templates'])
        self.assertEqual(len([c for c in commands if c['id'].startswith('syntax:')]), 5)
        self.assertIn('python-compile', {c['id'] for c in commands})
        self.assertEqual(len([c for c in commands if c['id'].startswith('integrity:')]), 4)
        with self.assertRaises(selector.SelectionError): runner.stage_commands(p, 'unregistered')


class RunnerGitTests(fixtures.SyntheticGitTests):
    # Reuse the tiny source-tree factory, not the parent's test methods.
    def test_real_valid_plan_and_omitted_command_or_guard_rejected(self):
        p = self.plan()
        self.assertEqual(runner.validate_plan(p), self.root)
        for mutation in ('command', 'integrity', 'syntax', 'compile', 'reason', 'build', 'browser', 'tree'):
            q = copy.deepcopy(p)
            if mutation == 'command': q['selected'].pop()
            if mutation == 'integrity': q['integrity_groups'].pop()
            if mutation == 'syntax': q['syntax'].pop()
            if mutation == 'compile': q['python_compile'].pop()
            if mutation == 'reason': q['selected'][0]['reasons'] = ['unproven']
            if mutation == 'build': q['build_required'] = False
            if mutation == 'browser': q['browser_required'] = False
            if mutation == 'tree': q['candidate_tree'] = '1' * 40
            with self.subTest(mutation=mutation), self.assertRaises(selector.SelectionError):
                runner.validate_plan(q)

    def test_altered_argv_env_script_bytes_and_blocked_plan_rejected(self):
        p = self.plan()
        for mutation in ('argv', 'env', 'blocker'):
            q = copy.deepcopy(p)
            if mutation == 'argv': q['selected'][0]['argv'].append('; touch /tmp/no')
            if mutation == 'env': q['selected'][0]['env']['EXTRA'] = 'not registered'
            if mutation == 'blocker': q['blockers'] = ['explicit missing coverage']
            with self.subTest(mutation=mutation), self.assertRaises(selector.SelectionError):
                runner.validate_plan(q)
        self.write('scripts/ci/run_checks.py', 'changed outside commit')
        with self.assertRaisesRegex(selector.SelectionError, 'dispatch source differs'):
            runner.validate_plan(p)

    def test_main_returns_failure_after_collecting_all_statuses(self):
        plan = self.plan()
        path = self.root / 'plan.json'
        path.write_text(json.dumps(plan))
        invoked = []
        def fake_execute(commands, repo):
            invoked.extend(commands)
            return [{'id': c['id'], 'status': 'failed' if i == 0 else 'passed', 'returncode': 1 if i == 0 else 0, 'duration_seconds': 0.1} for i, c in enumerate(commands)]
        with mock.patch.object(runner, 'execute_commands', side_effect=fake_execute):
            result = runner.main(['--plan', str(path), '--stage', 'browser'])
        self.assertEqual(result, 1)
        self.assertEqual(len(invoked), 3)
        report = json.loads((self.root / 'plan-browser-results.json').read_text())
        self.assertEqual(report['status'], 'failed')
        self.assertEqual(len(report['results']), 3)


# Avoid rerunning all inherited selector tests in the runner suite.
for _name in list(vars(fixtures.SyntheticGitTests)):
    if _name.startswith('test_'):
        setattr(RunnerGitTests, _name, None)

if __name__ == '__main__':
    unittest.main()
