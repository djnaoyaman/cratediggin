#!/usr/bin/env python3
"""Selectable, verbatim assertions extracted from the Pages workflow heredoc.

Each block is self-contained and reads only its declared inputs. The selector owns
application dependency closure; this module does not infer it or fall back to all
checks. Generated inputs must already exist from the selected build stage.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path

# Frozen from the original workflow, before extraction. Tests compare the exact
# assertion AST multiset, including error messages and every compound predicate.
LEGACY_ASSERTION_COUNT = 26
LEGACY_ASSERTIONS_SHA256 = '96313b8b1f9e8b3411bafd33b02238951b037ba361da6ea723e9afea0f4cffc4'

BLOCKS = {
    'generated-pages': {
        "description": 'Exact generated track HTML IDs, static index, and Markdown count.',
        "source_inputs": ['tracks.json'],
        "generated_inputs": ['dist/tracks/*.html', 'dist/tracks/*.md'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nroot = Path('dist')\ndata = json.loads(Path('tracks.json').read_text(encoding='utf-8'))\nassert {p.stem for p in (root/'tracks').glob('*.html') if p.name!='index.html'} == {t['id'] for t in data}, 'Generated song HTML IDs mismatch'\nassert (root/'tracks'/'index.html').exists(), 'Static song index missing'\nassert len(list((root/'tracks').glob('*.md'))) == len(data), 'Generated Markdown page count mismatch'\n",
    },
    'social-card-count': {
        "description": 'Exact generated song social-image count.',
        "source_inputs": ['tracks.json'],
        "generated_inputs": ['dist/og/*.jpg'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nroot = Path('dist')\ndata = json.loads(Path('tracks.json').read_text(encoding='utf-8'))\nassert len(list((root/'og').glob('*.jpg'))) == len(data), 'Generated social image count mismatch'\n",
    },
    'project-pages-urls': {
        "description": 'Preserve the project base path and script URLs.',
        "source_inputs": [],
        "generated_inputs": ['dist/index.html'],
        "dependencies": [],
        "source": 'from pathlib import Path\nimport json\nroot = Path(\'dist\')\nhtml = (root/\'index.html\').read_text(encoding=\'utf-8\')\nassert \'/cratediggin/tracks/\' in html, \'Project Pages links missing base path\'\nassert \'"//cratediggin/\' not in html, \'Broken protocol-relative Pages URLs\'\nassert \'src="/cratediggin/tracks.js\' in html, \'Track data script URL incorrect\'\nassert \'src="/cratediggin/app.js\' in html, \'Player script URL incorrect\'\n',
    },
    'touch-icon': {
        "description": 'Preserve the unique vinyl touch icon and generated asset.',
        "source_inputs": [],
        "generated_inputs": ['dist/index.html', 'dist/apple-touch-icon-vinyl.png'],
        "dependencies": [],
        "source": 'from pathlib import Path\nimport json\nroot = Path(\'dist\')\nhtml = (root/\'index.html\').read_text(encoding=\'utf-8\')\nassert \'href="/cratediggin/apple-touch-icon-vinyl.png?v=original-20261016"\' in html, \'Vinyl touch icon URL missing\'\nassert html.count(\'rel="apple-touch-icon"\') == 1, \'Duplicate Apple touch icon tags\'\nassert (root/\'apple-touch-icon-vinyl.png\').exists(), \'Vinyl touch icon not generated\'\n',
    },
    'artist-discovery': {
        "description": 'Preserve crawlable artist discovery, sitemap, and AI index.',
        "source_inputs": [],
        "generated_inputs": ['dist/artists/*.html', 'dist/index.html', 'dist/sitemap.xml', 'dist/tracks/*.html', 'dist/llms.txt'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nroot = Path('dist')\nhtml = (root/'index.html').read_text(encoding='utf-8')\nartist_pages = [p for p in (root/'artists').glob('*.html') if p.name!='index.html']\nassert artist_pages, 'No crawlable artist pages generated'\nsitemap = (root/'sitemap.xml').read_text(encoding='utf-8')\nassert all('/artists/'+p.name in sitemap for p in artist_pages), 'Artist page missing from sitemap'\nassert 'ARTIST INDEX' in html, 'Artist links missing from static home HTML'\nassert '/cratediggin/artists/' in html, 'Crawlable artist links missing from homepage'\nassert any('/cratediggin/artists/' in p.read_text(encoding='utf-8') for p in (root/'tracks').glob('*.html')), 'Crawlable song-to-artist links missing'\nassert '## Artists' in (root/'llms.txt').read_text(encoding='utf-8'), 'AI discovery artist index missing'\n",
    },
    'deep-dive-output': {
        "description": 'Preserve deep-dive UI and the existing source-content sentinel.',
        "source_inputs": [],
        "generated_inputs": ['dist/app.js', 'dist/tracks.js'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nroot = Path('dist')\nassert 'DIG DEEPER' in (root/'app.js').read_text(encoding='utf-8'), 'Deep-dive UI missing'\nassert '制作の背景：サンプラーの制約が音楽になった' in (root/'tracks.js').read_text(encoding='utf-8'), 'Deep-dive source content missing'\n",
    },
    'public-enemy-coverage': {
        "description": 'Preserve Public Enemy title coverage and minimum section counts.',
        "source_inputs": ['tracks.json', 'editorial_deepdives.json'],
        "generated_inputs": [],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\ntracks=json.loads((Path('tracks.json')).read_text(encoding='utf-8'))\ndeepdives=json.loads((Path('editorial_deepdives.json')).read_text(encoding='utf-8'))\npe={t['title'] for t in tracks if t['artist']=='Public Enemy'}\ncovered={d['title'] for d in deepdives if d['artist']=='Public Enemy' and len(d['sections'])>=3}\nassert pe == covered, f'Public Enemy editorial coverage mismatch: {pe ^ covered}'\n",
    },
    'gang-starr-coverage': {
        "description": 'Preserve nonempty Gang Starr title coverage and minimum section counts.',
        "source_inputs": ['tracks.json', 'editorial_deepdives.json'],
        "generated_inputs": [],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\ntracks=json.loads((Path('tracks.json')).read_text(encoding='utf-8'))\ndeepdives=json.loads((Path('editorial_deepdives.json')).read_text(encoding='utf-8'))\ngs={t['title'] for t in tracks if t['artist']=='Gang Starr'}\ngs_covered={d['title'] for d in deepdives if d['artist']=='Gang Starr' and len(d['sections'])>=3}\nassert gs and gs==gs_covered, f'Gang Starr editorial coverage mismatch: {gs ^ gs_covered}'\n",
    },
    'shadow-coverage': {
        "description": 'Preserve historic DJ Shadow IDs and minimum editorial section coverage.',
        "source_inputs": ['tracks.json', 'editorial_deepdives.json', 'scripts/shadow_existing_depth_ids.json'],
        "generated_inputs": [],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\ntracks=json.loads((Path('tracks.json')).read_text(encoding='utf-8'))\ndeepdives=json.loads((Path('editorial_deepdives.json')).read_text(encoding='utf-8'))\nshadow_ids=set(json.loads(Path('scripts/shadow_existing_depth_ids.json').read_text()))\nassert shadow_ids <= {t['id'] for t in tracks}\nshadow={t['title'] for t in tracks if t['id'] in shadow_ids}\nshadow_covered={d['title'] for d in deepdives if d['artist']=='DJ Shadow' and len(d['sections'])>=4}\nassert shadow and shadow <= shadow_covered, f'DJ Shadow coverage mismatch: {shadow ^ shadow_covered}'\n",
    },
    'shadow-research-counts': {
        "description": 'Preserve the legacy sample-research entry and sample-count assertions.',
        "source_inputs": ['dj_shadow_sample_research.json'],
        "generated_inputs": [],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nresearch=json.loads(Path('dj_shadow_sample_research.json').read_text(encoding='utf-8'))\nassert len(research)>=6 and sum(len(x['samples']) for x in research)>=13\n",
    },
    'shadow-research-output': {
        "description": 'Preserve rendered researchedSamples and per-record research linkage.',
        "source_inputs": ['tracks.json', 'dj_shadow_sample_research.json'],
        "generated_inputs": ['dist/tracks.js'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\ntracks=json.loads((Path('tracks.json')).read_text(encoding='utf-8'))\nresearch=json.loads(Path('dj_shadow_sample_research.json').read_text(encoding='utf-8'))\njs=(Path('dist')/'tracks.js').read_text(encoding='utf-8')\nassert 'researchedSamples' in js and all(any(s.get('research') for s in t['samples']) for t in tracks if t['artist']=='DJ Shadow' and t['title'] in {e['title'] for e in research})\n",
    },
    'number-song-output': {
        "description": 'Preserve the existing Number Song rendered ID assertion.',
        "source_inputs": [],
        "generated_inputs": ['dist/tracks.js'],
        "dependencies": [],
        "source": "from pathlib import Path\nimport json\nroot = Path('dist')\nassert 'dj-shadow-the-number-song' in (root/'tracks.js').read_text(encoding='utf-8')\n",
    },
}


def block_metadata() -> dict:
    """Return declarative read requirements without executable block sources."""
    return {
        name: {
            **{key: value for key, value in spec.items() if key != "source"},
            "build_required": bool(spec["generated_inputs"]),
        }
        for name, spec in BLOCKS.items()
    }


@contextmanager
def repository_directory(root: Path):
    # The CLI executes in its own process. Callers embedding this function must
    # not run it concurrently with other cwd-changing work in the same process.
    previous = Path.cwd()
    os.chdir(root)
    try:
        yield
    finally:
        os.chdir(previous)


def run_groups(root: Path, groups: list[str]) -> list[str]:
    """Run explicitly selected groups in legacy order; fail on unknown/empty scope."""
    if not __debug__:
        raise RuntimeError("Integrity assertions require Python without -O")
    unknown = sorted(set(groups) - BLOCKS.keys())
    if unknown:
        raise ValueError("Missing integrity block mapping: " + ", ".join(unknown))
    if not groups:
        raise ValueError("Select at least one integrity block; no full-suite fallback")
    selected = set(groups)
    completed = []
    with repository_directory(Path(root).resolve()):
        for name, spec in BLOCKS.items():
            if name not in selected:
                continue
            exec(compile(spec["source"], f"<integrity:{name}>", "exec"), {})
            completed.append(name)
    return completed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--group", action="append", default=[], choices=BLOCKS)
    parser.add_argument("--groups", nargs="+", default=[], choices=BLOCKS)
    parser.add_argument("--list-json", action="store_true")
    args = parser.parse_args(argv)
    if args.list_json:
        print(json.dumps(block_metadata(), ensure_ascii=False, indent=2))
        return 0
    groups = args.group + args.groups
    if not groups:
        parser.error("--group/--groups is required; no implicit full-suite execution")
    for name in run_groups(args.root, groups):
        print("PASS integrity:" + name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
