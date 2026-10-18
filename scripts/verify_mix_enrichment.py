"""Keep original mix essays and add precisely attributed participant stories."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1]
by={x['id']:x for x in json.loads((R/'tracks.json').read_text())}
expected=json.loads((R/'scripts/fixtures/mix-interview-enrichment.json').read_text())
dives={(d['artist'],d['title']):d['sections'] for d in json.loads((R/'editorial_deepdives.json').read_text())}
for e in expected:
 t=by[e['id']];assert t['year']==e['year'] and t['youtube']['id']==e['videoId']
 n=len(e['originalEssays']);assert t['essay'][:n]==e['originalEssays'] and t['essaySources'][:n]==e['originalEssaySources']
 assert t['essay'][n]==e['addedEssay'] and t['essaySources'][n]==e['addedEssaySources']
 assert [t['sources'][i]['url'] for i in t['essaySources'][n]]==e['addedSourceUrls']
 assert len(t['essay'])==len(t['essaySources'])==n+1
 assert t['facts']==e['facts']
 sections=dives[(t['artist'],t['title'])];assert sections==e['sections']
 s=(R/'dist/tracks'/f"{e['id']}.html").read_text();md=(R/'dist/tracks'/f"{e['id']}.md").read_text()
 for text in [*e['originalEssays'],e['addedEssay'],*[f['text'] for f in e['facts']],*[d['text'] for d in e['sections']]]:
  assert html.escape(text) in s and text in md
 for indices in t['essaySources']+[f['sources'] for f in t['facts']]:assert all(type(i)is int and 0<=i<len(t['sources']) for i in indices)
 assert 'Sentinel_' not in s and '/workspace/' not in s
print('Four participant-led stories, original essay prefixes, precise citations, chronology distinctions and static/Markdown text passed; no playback claim')
