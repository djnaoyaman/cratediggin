#!/usr/bin/env python3
"""Focused selector contract tests; never execute the selected application checks.

Run with: python3 -m unittest discover -s scripts/ci -p test_select_checks.py -v
The temporary fixtures below are synthetic. No network or browser is involved.
"""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import select_checks as selector


def change(status: str, old: str | None, new: str | None) -> dict:
    return {"status": status, "old_path": old, "new_path": new}


class ParseNameStatusTests(unittest.TestCase):
    def test_empty_diff(self):
        self.assertEqual(selector.parse_name_status(b""), [])

    def test_add_modify_delete_and_type_change(self):
        raw = b"A\0new.js\0M\0app.js\0D\0old.js\0T\0link.js\0"
        self.assertEqual(
            selector.parse_name_status(raw),
            [
                change("A", None, "new.js"),
                change("M", "app.js", "app.js"),
                change("D", "old.js", None),
                change("T", "link.js", "link.js"),
            ],
        )

    def test_rename_and_copy_preserve_both_paths_and_original_score(self):
        raw = b"R100\0old file.js\0new file.js\0C087\0source.js\0copy.js\0"
        self.assertEqual(
            selector.parse_name_status(raw),
            [
                change("R100", "old file.js", "new file.js"),
                change("C087", "source.js", "copy.js"),
            ],
        )

    def test_utf8_and_space_paths_are_not_shell_split(self):
        raw = "M\0assets/café cover.js\0".encode()
        self.assertEqual(
            selector.parse_name_status(raw),
            [change("M", "assets/café cover.js", "assets/café cover.js")],
        )

    def test_truncated_or_non_nul_record_blocks(self):
        for raw in (
            b"M", b"M\0", b"M\0app.js", b"M\tapp.js\n", b"R100\0old.js\0",
            b"R100\0old.js\0new.js", b"C100\0source.js\0", b"\0", b"M\0\0",
            b"M\0app.js\0\0", b"M\0app.js\0R100\0old.js\0",
        ):
            with self.subTest(raw=raw), self.assertRaises(selector.SelectionError):
                selector.parse_name_status(raw)

    def test_unknown_or_unsupported_status_blocks(self):
        for status in ("Q", "U", "X", "B", "MM", "A100", "R", "C", "R-1", "C101", "R999"):
            with self.subTest(status=status), self.assertRaises(selector.SelectionError):
                selector.parse_name_status(status.encode() + b"\0a.js\0")

    def test_unsafe_paths_block(self):
        for path in ("/absolute.js", "../escape.js", "scripts/../../escape.js", ".", "a/../b.js", "a//b.js"):
            with self.subTest(path=path), self.assertRaises(selector.SelectionError):
                selector.parse_name_status(b"M\0" + path.encode() + b"\0")

    def test_invalid_utf8_blocks_instead_of_replacing_filename(self):
        with self.assertRaises(selector.SelectionError):
            selector.parse_name_status(b"M\0invalid-\xff.js\0")



# Inventory-generated contracts keep narrow examples from concealing lost cases.
from unittest import mock
import subprocess


def manifest():
    return json.loads((HERE / 'manifest.json').read_text())


def selected_ids(plan):
    return {c['id'] for c in plan['selected']}


class ManifestTests(unittest.TestCase):
    def test_exact_all_129_legacy_invocations(self):
        m = manifest()
        registry = selector.validate_manifest(m, (HERE / 'bootstrap-pages.yml').read_bytes())
        self.assertEqual(sum(c['legacy'] for c in registry.values()), 129)
        inline = [c for c in registry.values() if c['argv'][1] == 'scripts/verify_inline_player_browser.cjs']
        self.assertEqual(len(inline), 2)
        self.assertEqual({tuple(c['env'].items()) for c in inline}, {(), (('INLINE_PLAYER_TRACK', 'ini-grown-man-sport'),)})
        self.assertEqual(sum(c['argv'][1] == 'scripts/verify_requested_six_browser.cjs' for c in registry.values()), 1)

    def test_immutable_bootstrap_and_registry_removal_block(self):
        snapshot = (HERE / 'bootstrap-pages.yml').read_bytes()
        for mutation in ('snapshot', 'legacy', 'identity', 'group', 'interpreter'):
            with self.subTest(mutation=mutation):
                m, raw = manifest(), snapshot
                if mutation == 'snapshot': raw += b' '
                if mutation == 'legacy': m['commands'].pop(0)
                if mutation == 'identity': m['commands'][0]['argv'].append('--changed')
                if mutation == 'group': m['groups']['queue'].append('unknown')
                if mutation == 'interpreter': m['commands'][0]['argv'][0] = 'sh'
                with self.assertRaises(selector.SelectionError):
                    selector.validate_manifest(m, raw)

    def test_all_runtime_rules_exact_group_closure_and_build(self):
        m = manifest()
        for path, groups in m['runtime_rules'].items():
            for status in ('A', 'M', 'D'):
                with self.subTest(path=path, status=status):
                    p = selector.select_changes(m, [change(status, None if status == 'A' else path, None if status == 'D' else path)])
                    self.assertEqual(p['blockers'], [])
                    self.assertTrue(p['build_required'])
                    self.assertEqual(selected_ids(p), set().union(*(set(m['groups'][g]) for g in groups)))
                    self.assertTrue(all(c['reasons'] for c in p['selected']))
                    if path.startswith('src/app/'):
                        self.assertIn('dist/app.js', p['syntax'])

    def test_each_legacy_test_registered_for_its_own_change(self):
        m = manifest()
        for command in [c for c in m['commands'] if c['legacy']]:
            path = command['argv'][1]
            with self.subTest(path=path, env=command['env']):
                p = selector.select_changes(m, [change('M', path, path)])
                self.assertFalse(p['blockers'])
                self.assertIn(command['id'], selected_ids(p))

    def test_both_manifest_sides_retain_removed_mapping(self):
        old, new = manifest(), manifest()
        new['runtime_rules'].pop('src/app/catalog-ui.js')
        new['script_dependencies'].pop('scripts/verify_shuffle_scope.py')
        merged = selector.merge_manifests(old, new)
        self.assertEqual(merged['runtime_rules']['src/app/catalog-ui.js'], old['runtime_rules']['src/app/catalog-ui.js'])
        self.assertEqual(merged['script_dependencies']['scripts/verify_shuffle_scope.py'], old['script_dependencies']['scripts/verify_shuffle_scope.py'])
        new['commands'][0]['env']['MUTATION'] = 'yes'
        with self.assertRaises(selector.SelectionError):
            selector.merge_manifests(old, new)

    def test_each_helper_edge_transitive_closure_including_cycles(self):
        m = manifest()
        for consumer, dependencies in m['script_dependencies'].items():
            for dependency in dependencies:
                with self.subTest(consumer=consumer, dependency=dependency):
                    result = selector.reverse_consumers({dependency}, m['script_dependencies'])
                    self.assertIn(consumer, result)
                    self.assertEqual(result[consumer][0], dependency)
        result = selector.reverse_consumers({'a'}, {'b': ['a'], 'c': ['b'], 'd': ['c'], 'a': ['d'], 'e': ['b']})
        self.assertEqual(set(result), {'a', 'b', 'c', 'd', 'e'})
        self.assertEqual(result['d'], ['a', 'b', 'c', 'd'])

    def test_provider_mock_change_selects_reverse_browser_consumers(self):
        m = manifest()
        p = selector.select_changes(m, [change('M', 'scripts/verify_visible_art_browser.cjs', 'scripts/verify_visible_art_browser.cjs')])
        consumers = selector.reverse_consumers({'scripts/verify_visible_art_browser.cjs'}, m['script_dependencies'])
        self.assertEqual(selected_ids(p), {c['id'] for c in m['commands'] if c['argv'][1] in consumers})
        self.assertGreater(len(p['selected']), 5)

    def test_critical_direct_edges_and_no_bundle_overselection(self):
        m = manifest()
        p = selector.select_changes(m, [change('M', 'src/app/playlist-ui.js', 'src/app/playlist-ui.js')])
        scripts = {c['argv'][1] for c in p['selected']}
        self.assertIn('scripts/verify_feature_swipe_browser.cjs', scripts)
        self.assertIn('scripts/verify_art_crate_browser.cjs', scripts)
        self.assertIn('scripts/verify_pagination_browser.cjs', scripts)
        self.assertNotIn('scripts/verify_requested_thirteen_browser.cjs', scripts)
        p = selector.select_changes(m, [change('M', 'src/app/catalog-ui.js', 'src/app/catalog-ui.js')])
        self.assertTrue(set(m['groups']['shuffle']) <= selected_ids(p))
        p = selector.select_changes(m, [change('M', 'src/app/editorial.js', 'src/app/editorial.js')])
        self.assertIn('artist-discovery', p['integrity_groups'])
        self.assertTrue(set(m['groups']['profile']) <= selected_ids(p))

    def test_unknown_data_assets_helpers_paths_block_without_full_suite(self):
        m = manifest()
        for path in [*m['data_paths'], 'assets/new.png', 'brand/new.png', 'src/assets/new.js', 'scripts/verify_unregistered.cjs', 'new-file.txt', 'scripts/approved_queue_scope.py', 'scripts/fixtures/approved-queue-scope.json']:
            with self.subTest(path=path):
                p = selector.select_changes(m, [change('M', path, path)])
                self.assertTrue(p['blockers'])
                self.assertEqual(p['selected'], [])

    def test_two_sided_rename_union_and_unknown_endpoint_block(self):
        m = manifest()
        p = selector.select_changes(m, [change('R100', 'src/app/catalog-ui.js', 'src/app/playlist-ui.js')])
        expected = set().union(*(set(m['groups'][g]) for path in ('src/app/catalog-ui.js', 'src/app/playlist-ui.js') for g in m['runtime_rules'][path]))
        self.assertEqual(selected_ids(p), expected)
        p = selector.select_changes(m, [change('R099', 'src/app/catalog-ui.js', 'unmapped.ts')])
        self.assertTrue(p['blockers'])

    def test_empty_and_docs_main_manual_always_fresh_build(self):
        for changes in ([], [change('M', 'README.md', 'README.md')]):
            for event in ('push', 'workflow_dispatch', 'pull_request'):
                with self.subTest(event=event, changes=changes):
                    p = selector.select_changes(manifest(), changes, event=event)
                    self.assertEqual(p['build_required'], event != 'pull_request')
                    self.assertEqual(p['source_drift_check'], event != 'pull_request')
                    self.assertFalse(p['browser_required'])
                    self.assertEqual(p['selected'], [])

    def test_policy_rollout_initial_support_files_and_version_is_bounded(self):
        m = manifest()
        paths = set(m['policy_files'] + m['policy_paths'] + ['releases.json'])
        old = {'version': '22.3', 'timezone': 'Asia/Tokyo', 'policy': 'major-only', 'history': []}
        new = dict(old, version='22.4')
        p = selector.select_changes(m, [change('M', x, x) for x in paths], lambda p: json.dumps(old), lambda p: json.dumps(new))
        self.assertFalse(p['blockers'])
        self.assertEqual(selected_ids(p), set(m['groups']['policy'] + m['groups']['release']))
        browsers = [c for c in p['selected'] if c['kind'] == 'browser']
        self.assertEqual(len(browsers), 3)
        self.assertEqual({c['argv'][1] for c in browsers}, {'scripts/verify_common_celebrate_browser.cjs', 'scripts/verify_inline_player_browser.cjs'})
        self.assertIn('scripts/verify_shuffle_scope.py', {c['argv'][1] for c in p['selected']})
        self.assertTrue(p['build_required'])
        self.assertTrue(all(c['reason'].endswith('not a pass') for c in p['skipped']))

    def test_version_unknown_fields_duplicate_keys_and_changed_history_block(self):
        old = {'version': '22.3', 'timezone': 'Asia/Tokyo', 'policy': 'major-only', 'history': []}
        self.assertTrue(selector.version_only(json.dumps(old), json.dumps(dict(old, version='22.4'))))
        for new in [dict(old, extra=1), dict(old, history=[1]), dict(old, version=3), dict(old, policy='new')]:
            with self.assertRaises(selector.SelectionError):
                selector.version_only(json.dumps(old), json.dumps(new))
        with self.assertRaises(selector.SelectionError):
            selector.strict_json('{"a":1,"a":2}', 'fixture')

    def test_relative_require_helpers_select_actual_consumers(self):
        m = manifest()
        for helper, consumer in [('scripts/verify_player_readiness.cjs', 'scripts/verify_playback_browser.cjs'), ('scripts/verify_art_motion.cjs', 'scripts/verify_graffiti.cjs')]:
            with self.subTest(helper=helper):
                self.assertIn(helper, m['script_dependencies'][consumer])
                p = selector.select_changes(m, [change('M', helper, helper)])
                self.assertFalse(p['blockers'])
                self.assertIn(consumer, {c['argv'][1] for c in p['selected']})
        p = selector.select_changes(m, [change('M', 'scripts/fixtures/requested-two.json', 'scripts/fixtures/requested-two.json')])
        self.assertTrue(p['blockers'])
        self.assertIn('scripts/fixtures/requested-two.json', m['script_dependencies']['scripts/verify_essay_references.cjs'])

    def test_relative_require_resolution_rejects_escape_and_unknown(self):
        known = {'scripts/helper.cjs', 'src/module.js', 'scripts/data.json'}
        self.assertEqual(selector.relative_require_edges('scripts/test.cjs', "require('./helper.cjs'); require('../src/module'); require('./data.json'); require('fs');", known), known)
        for source in ["require('../../outside.cjs')", "require('./missing.cjs')"]:
            with self.assertRaises(selector.SelectionError):
                selector.relative_require_edges('scripts/test.cjs', source, known)


    def test_name_status_special_characters_are_data(self):
        for path in ['a b.js', 'tab\tfile.js', 'line\nfile.js', '-leading.js', 'a;echo NO.js']:
            self.assertEqual(selector.parse_name_status(('M\0' + path + '\0').encode())[0]['new_path'], path)


class SyntheticGitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        def git(*args):
            return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL).decode().strip()
        self.git = git
        git('init', '-q')
        git('config', 'user.name', 'Synthetic CI Test')
        git('config', 'user.email', 'ci-test@example.invalid')
        self.write('.github/workflows/pages.yml', (HERE / 'bootstrap-pages.yml').read_bytes())
        self.write('src/app/order.json', '["core.js"]')
        self.write('src/app/core.js', 'const value = 1;\n')
        self.write('README.md', 'before\n')
        self.write('build.py', 'pass\n')
        self.write('scripts/audit_catalog.py', 'pass\n')
        m = manifest()
        for command in m['commands']:
            if command['argv'][1] != '-m':
                self.write(command['argv'][1], 'pass\n' if command['argv'][1].endswith('.py') else '// synthetic\n')
        self.base = self.commit('base')
        self.patch = mock.patch.object(selector, 'BOOTSTRAP_COMMIT', self.base)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        m['bootstrap_commit'] = self.base
        for filename in m['policy_files']:
            self.write(filename, (HERE / Path(filename).name).read_bytes())
        self.write('scripts/ci/manifest.json', json.dumps(m))
        self.candidate = self.commit('policy')

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content.encode() if isinstance(content, str) else content)

    def commit(self, message):
        self.git('add', '.')
        self.git('commit', '-qm', message)
        return self.git('rev-parse', 'HEAD')

    def plan(self, base=None, candidate=None, event='pull_request'):
        return selector.build_plan(self.root, self.base if base is None else base, self.candidate if candidate is None else candidate, event)

    def test_real_git_bootstrap_and_exact_commit_tree_ids(self):
        p = self.plan()
        self.assertFalse(p['blockers'])
        self.assertEqual(p['base_sha'], self.base)
        self.assertEqual(p['candidate_sha'], self.candidate)
        self.assertEqual(p['candidate_tree'], self.git('rev-parse', self.candidate + '^{tree}'))
        self.assertEqual(len([x for x in p['selected'] if x['kind'] == 'browser']), 3)

    def test_missing_zero_branch_stale_dirty_bases_block(self):
        for base in ('', '0' * 40, 'main', '1' * 40):
            with self.subTest(base=base), self.assertRaises(selector.SelectionError):
                self.plan(base=base)
        with self.assertRaises(selector.SelectionError):
            self.plan(candidate=self.base)
        self.write('README.md', 'dirty')
        with self.assertRaises(selector.SelectionError):
            self.plan()

    def test_push_range_not_head_parent_and_empty_net_diff(self):
        first = self.candidate
        self.write('README.md', 'middle')
        self.commit('middle')
        self.write('README.md', 'final')
        end = self.commit('end')
        p = self.plan(base=first, candidate=end, event='push')
        self.assertEqual(p['changes'], [change('M', 'README.md', 'README.md')])
        self.assertTrue(p['build_required'])
        self.assertFalse(p['browser_required'])
        self.write('README.md', 'before\n')
        end = self.commit('restore')
        p = self.plan(base=first, candidate=end, event='workflow_dispatch')
        self.assertEqual(p['changes'], [])
        self.assertTrue(p['build_required'])

    def test_real_git_rename_unknown_new_endpoint_blocks(self):
        self.git('mv', 'src/app/core.js', 'src/app/unknown.js')
        self.write('src/app/order.json', '["unknown.js"]')
        end = self.commit('rename')
        with self.assertRaisesRegex(selector.SelectionError, 'missing app runtime mapping'):
            self.plan(base=self.candidate, candidate=end)

    def test_symlink_and_missing_or_duplicate_order_block(self):
        self.write('src/app/order.json', '["core.js", "core.js"]')
        end = self.commit('duplicate order')
        with self.assertRaisesRegex(selector.SelectionError, 'duplicate app order'):
            self.plan(base=self.candidate, candidate=end)
        self.write('src/app/order.json', '["core.js"]')
        (self.root / 'src/app/core.js').unlink()
        (self.root / 'src/app/core.js').symlink_to('/tmp/not-a-runtime-file')
        end = self.commit('symlink')
        with self.assertRaisesRegex(selector.SelectionError, 'symlink'):
            self.plan(base=self.candidate, candidate=end)

    def test_added_helper_import_without_edge_is_explicit_blocker(self):
        self.write('scripts/new_helper.py', 'pass\n')
        self.write('scripts/verify_inline_player.cjs', "require('./new_helper.py');\n")
        self.write('scripts/verify_catalog_sources.py', 'import new_helper\n')
        end = self.commit('new dependency')
        with self.assertRaisesRegex(selector.SelectionError, 'missing explicit helper dependency'):
            self.plan(base=self.candidate, candidate=end)

    def test_added_relative_require_without_edge_blocks(self):
        self.write('scripts/new_helper.cjs', '// synthetic helper')
        self.write('scripts/verify_inline_player.cjs', "require('./new_helper.cjs');\n")
        end = self.commit('new relative dependency')
        with self.assertRaisesRegex(selector.SelectionError, 'missing explicit helper dependency'):
            self.plan(base=self.candidate, candidate=end)

if __name__ == "__main__":
    unittest.main()
