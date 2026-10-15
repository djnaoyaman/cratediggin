# CRATE DIGGIN’ — Catalog, Playback & Repository Audit

Date: 2026-10-15. Scope: 225 source records in `tracks.json`, player code, build pipeline, publishing workflow and known repository paths.

## Measured results (source-level)

| Check | Result |
|---|---:|
| Total catalog entries | 225 |
| Entries with a YouTube video ID | 220 |
| Entries without a YouTube video ID | 5 |
| Duplicate YouTube IDs across entries | 0 |
| Entries marked with an unconfirmed label | 136 |
| Entries explicitly awaiting first-release-year verification | 137 |
| Sample references recorded | 44 |
| Entries with a unique ID | 225 |

These numbers **do not** certify that the 220 videos match their titles, artists, mixes, or actual recordings. A YouTube ID passing syntax validation is not proof of correct audio. YouTube video content has **not** been watched or listened to in this audit. The `--online` audit option retrieves oEmbed title/uploader candidates and flags title mismatches, but cannot verify actual playback, geographic rights, version, or sonic identity.

## Confirmed code issues addressed

1. The player initialized YouTube with another song's video when the current song had no ID. It also substituted the first queue entry in some playback paths. These fallbacks have been removed; unavailable audio should not silently become a different recording.
2. The generated 404 page and static fallback links contained root-absolute URLs incompatible with the `/cratediggin/` GitHub Pages project prefix. The generator now writes base-path-aware links.
3. Generated song pages and social cards were not cleaned up when a source record was removed. The generator now deletes obsolete generated files, while keeping current records.
4. The deployment pipeline previously checked only that The Number Song appeared in the generated site. It now also checks the 225-record catalog, page count, Markdown count, social card count, and project links, and produces a machine-readable metadata audit.

## Directory and filename review

Current roles:
- `tracks.json` — canonical catalog; keep at repository root to avoid breaking current tooling.
- `releases.json` — version metadata; keep at root.
- `build.py` / `brand_assets.py` / `version.py` — build and asset generation; preserve names to avoid unnecessary churn.
- `dist/` — GitHub Pages deployable directory, with `songs/<stable-track-id>.html`, `songs/<stable-track-id>.md`, and `og/<stable-track-id>.png`.
- `research/` — unpublished verification queues; never imply that a research candidate is a published song.
- `scripts/audit_catalog.py` — new reusable quality gate.
- `audit-reports/` — audit output generated during checks (not source content).

**Recommendation:** Preserve existing track IDs and published URL paths; a mass rename would break search indexing, bookmarks and external links. A later dedicated migration can move Python build modules into `scripts/` and frontend source into `src/` while retaining the exact `dist/` output and redirect policy. No destructive directory restructuring is included in this PR.

## Outstanding editorial work (not verified)

- Manually verify every video's artist, track, exact mix/clean/explicit version, uploader, embed permissions and geographic availability.
- Replace provisional release years and labels using label catalogs, original record sleeves and authoritative discographies.
- Confirm all sample credits and source-video identities; absence of a sample record does not establish no sampling.
- Replace generic repeated facts/context prose with song-specific sourced detail.
- Confirm DJ Shadow's The Number Song with the correct official recording before enabling playback; currently it intentionally has no video ID.

## Verification commands

```sh
python -m pip install Pillow
python scripts/audit_catalog.py
python scripts/audit_catalog.py --online  # optional, requires YouTube network access
python build.py
```

The PR does **not** claim that all 225 audio recordings and editorial facts have been independently verified. It provides measured findings, fixes confirmed structural/player bugs, and adds an auditable verification process for the remaining review.
