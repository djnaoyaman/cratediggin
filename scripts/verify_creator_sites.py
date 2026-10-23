"""Verify sites are introduced in the native author biography, never in a footer."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]
SITES = {'ppp', 'youkai', 'sakanamushi', 'kuranpo', 'chems', 'suburbia-classica',
         'sanreikotaiyoku', 'gooooooooood_expression', 'bookkeeping'}
page = (ROOT / 'dist/editor.html').read_text(encoding='utf-8')
profile = re.search(r'<article class="editor-profile">(.*?)</article>', page, re.S)
assert profile, 'Native biography missing'
works = re.search(r'<h3>制作しているWebサイト</h3><ul>(.*?)</ul>', profile[1], re.S)
assert works, 'Sites must be inside the existing profile prose'
for site in SITES:
    assert f'https://djnaoyaman.github.io/{site}/' in works[1], site
assert works[1].count('<li>') == len(SITES)
assert 'yoshida-farmer' not in works[1]
assert 'id="creator-sites-network"' not in page
assert '制作しているWebサイト' not in (ROOT / 'dist/index.html').read_text(encoding='utf-8')
print('Native Editor biography: nine described creator sites, no farm and no shared footer PASS')
