"""Resolve authored section citations without altering editorial source data."""
def section_references(track, section):
    references = []
    seen = set()
    def add(url, label):
        assert isinstance(url, str) and url.startswith('https://'), 'Section source must be HTTPS'
        assert isinstance(label, str) and label.strip(), 'Section source needs a label'
        if url not in seen:
            references.append({'url': url, 'label': label})
            seen.add(url)
    if section.get('source'):
        add(section['source'], section['sourceLabel'])
    for index in section.get('sources', []):
        assert type(index) is int and 0 <= index < len(track['sources']), 'Invalid section source index'
        source = track['sources'][index]
        add(source['url'], source['label'])
    assert references, 'Section requires at least one reference'
    return references

def enrich_sections(track, sections):
    return [dict(section, references=section_references(track, section)) for section in sections]

def markdown_reference(reference):
    from urllib.parse import quote
    from string import punctuation
    label = reference['label'].replace('\n', ' ').replace('\r', ' ')
    label = ''.join('\\' + char if char in punctuation else char for char in label)
    url = quote(reference['url'], safe=":/?#[]@!$&'()*+,;=%")
    return '[' + label + '](<' + url + '>)'
