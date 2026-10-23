"""Verify the published creator directory without relying on application JavaScript."""
from html.parser import HTMLParser
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {'ppp', 'youkai', 'sakanamushi', 'kuranpo', 'chems', 'suburbia-classica',
            'cratediggin', 'sanreikotaiyoku', 'gooooooooood_expression', 'bookkeeping'}


class Directory(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sites = []
        self.descriptions = []
        self.capture = False
        self.current = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a' and 'data-creator-site' in attrs:
            site = attrs['data-creator-site']
            assert attrs['href'] == f'https://djnaoyaman.github.io/{site}/'
            assert 'noopener' in attrs.get('rel', '')
            self.sites.append(site)
        if tag == 'p':
            self.capture = True
            self.current = []

    def handle_data(self, value):
        if self.capture:
            self.current.append(value)

    def handle_endtag(self, tag):
        if tag == 'p' and self.capture:
            self.descriptions.append(''.join(self.current).strip())
            self.capture = False


def verify(text):
    assert text.count('id="creator-sites-network"') == 1
    fragment = re.search(r'<!-- CREATOR_SITES_START -->(.*?)<!-- CREATOR_SITES_END -->', text, re.S)
    assert fragment, 'Missing directory boundaries'
    assert 'yoshida-farmer' not in fragment[1]
    parsed = Directory()
    parsed.feed(fragment[1])
    assert len(parsed.sites) == len(EXPECTED) and set(parsed.sites) == EXPECTED
    assert len(parsed.descriptions) == 11 and all(parsed.descriptions)
    assert 'creator_site_visit' in fragment[1]


verify((ROOT / 'creator-sites.html').read_text(encoding='utf-8'))
pages = list((ROOT / 'dist').rglob('*.html'))
assert pages, 'No generated HTML'
for page in pages:
    text = page.read_text(encoding='utf-8')
    if '</body>' in text:
        verify(text)
print(f'Creator directory: ten described sites, farm excluded, verified in {len(pages)} generated pages')
