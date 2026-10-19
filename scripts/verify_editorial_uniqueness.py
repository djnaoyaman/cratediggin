"""No new deterministic duplication; remaining legacy debt and human semantic review stay explicit."""
import json,hashlib,copy
from pathlib import Path
from editorial_uniqueness import authored,duplicates,new_violations,neighbors,sha
from approved_editorial_corrections import FIXTURE
R=Path(__file__).resolve().parents[1]
rows=authored(R);baseline=json.loads((R/'scripts/fixtures/editorial-legacy-debt.json').read_text())
original=copy.deepcopy(baseline['groups'])
assert baseline['removedOccurrences']
for k,removed in baseline['removedOccurrences'].items():
 assert all(x not in baseline['groups'].get(k,[]) for x in removed)
 original.setdefault(k,[]).extend(removed);original[k].sort(key=lambda x:(x['owner'],x['path'],x['part']))
assert hashlib.sha256(json.dumps(original,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()==baseline['originalGroupsSHA256']
groups=duplicates(rows);violations=new_violations(groups,baseline['groups'])
assert not violations, 'New editorial duplication: '+repr(violations)
review=json.loads((R/'scripts/fixtures/editorial-semantic-review.json').read_text())
touched={x['id'] for x in FIXTURE['corrections']}
assert set(review['works'])==touched
assert not any(o['owner'] in touched and o['path']=='essayTitle' for group in baseline['groups'].values() for o in group), 'Removed headline debt must not remain allowlisted'
for c in FIXTURE['corrections']:
 r=review['works'][c['id']];assert r['afterSHA256']==c['afterSHA256'] and r['reviewed'] is True
 assert r['proposition'] and r['contrasts'] and r['sources']
assert review['scope']=='three corrected works only; not semantic certification of the catalog'
assert review['reviewedFields']==['essayTitle','deck','essay','listening','appended sources','essaySources']
assert review['exclusions']=='Unchanged context, facts, audio and historical source claims are preserved, not newly certified.'
report={'legacyGroupsBefore':len(original),'legacyGroupsRemaining':len(groups),'newViolations':len(violations),'remainingOccurrences':sum(map(len,groups.values())),'semanticScope':review['scope'],'nearestNeighbors':neighbors(rows,touched)}
out=R/'audit-reports';out.mkdir(exist_ok=True);(out/'editorial-uniqueness.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f"No new exact/sentence/template duplication; {len(groups)} legacy groups remain; human review is limited to3 works, not all499")
