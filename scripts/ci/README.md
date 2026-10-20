# Targeted Pages validation

The existing `validate` and `deploy` jobs remain the gates. `select_checks.py`
compares exact base/candidate commit IDs, records both tree IDs, and emits a JSON
plan plus `build_required` and `browser_required` GitHub outputs. The runner has
three stages: `integrity`, `static`, and `browser`. Commands are argv arrays with
separate environment values, never shell fragments. Reports record reasons,
nonselected cases (not passes), exit codes, and monotonic durations.

## Bounded coverage

Explicit source paths select declared behavior groups and direct test/helper
reverse consumers. Merely sharing bundled `app.js` does not select other cases.
All 129 distinct old workflow invocations remain registered, including both
inline-player environment variants. Only the duplicate requested-six invocation
is removed. The immutable old workflow snapshot is checked by a fixed SHA-256.
Initial bootstrap is accepted only against its exact published baseline commit;
subsequent selection unions base and candidate coverage.

Unknown paths, record/field edits, ambiguous asset owners, unreviewed normalizer
or fixture changes, and unavailable comparison bases fail with a specific mapping
requirement. They never trigger a fallback full suite. This initial release does
not claim complete semantic record/asset mapping. Add a reviewed mapping and
positive/negative tests before such changes can dispatch. Keep historical exact
normalization checks, including rejection of one-byte drift, when adapting a guard.

A policy change selects its units, exact CI/shuffle preservation, and three
representative browser invocations (normal plus both inline environments), not all
application tests. General runtime edits use explicit groups; globally shared
state/routing/styles legitimately have broader consumers. The Python tests use
synthetic Git trees and process fakes only; actual representative browser dispatch
is a separate release check, not replaced by these units.

## Build and deployment

Main pushes and manual dispatch always build a fresh artifact, including empty or
docs-only diffs. PRs build when an affected product or selected command needs it.
The workflow installs Chromium and starts the unchanged port 8765 `/cratediggin`
preview server only when a browser was selected, and owns server cleanup. Optional
screenshot uploads cannot hide command failures. Each stage collects command
results and returns nonzero if any selected command fails.

The concurrency group is stable per PR and cancellation is enabled for PRs only.
Production retains `github-pages`, cancellation false, same-run artifact upload,
`deploy.needs: validate`, permissions/environment, and the current-main SHA guard.
Manual dispatch requires an explicit available comparison base. PR artifact reuse
is not implemented.

Run focused units with:

    python -m unittest discover -s scripts/ci -p 'test_*.py' -v
