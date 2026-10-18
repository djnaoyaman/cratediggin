import json,copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from editorial_references import section_references,enrich_sections,markdown_reference
base=Path(sys.argv[1] if len(sys.argv)>1 else str(Path(__file__).resolve().parents[1]))
tracks=json.loads((base/'tracks.json').read_text());by={(t['artist'].casefold(),t['title'].casefold()):t for t in tracks}
deepdives=json.loads((base/'editorial_deepdives.json').read_text());before=copy.deepcopy(deepdives);sections=extra=0
for entry in deepdives:
    track=by[(entry['artist'].casefold(),entry['title'].casefold())]
    for section in entry['sections']:
        references=section_references(track,section)
        assert len({r['url'] for r in references})==len(references)
        assert {r['url'] for r in references}=={section['source']}|{track['sources'][i]['url'] for i in section.get('sources',[])}
        sections+=1;extra+=len(references)-1
assert before==deepdives
track={'sources':[{'url':'https://example.com/a','label':'A'}]}
section={'source':'https://example.com/a','sourceLabel':'Legacy A','sources':[0,0]}
assert len(section_references(track,section))==1
for index in [-1,1,True,'0']:
    try:section_references(track,dict(section,sources=[index]))
    except AssertionError:pass
    else:raise AssertionError(index)
assert markdown_reference({'label':'A [B] <C> & D *E* _F_ `G`','url':'https://example.com/a(b) c<d>'})==r'[A \[B\] \<C\> \& D \*E\* \_F\_ \`G\`](<https://example.com/a(b)%20c%3Cd%3E>)'
print(f'{sections} sections and {extra} additional references; immutable data, URL dedupe, index rejection and Markdown escaping passed')
