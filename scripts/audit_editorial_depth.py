"""Audit the editorial depth of every catalog track without inventing facts.

Run: python scripts/audit_editorial_depth.py
Writes a ranked, human-readable CSV report for editorial follow-up.
"""
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
tracks = json.loads((root / "tracks.json").read_text(encoding="utf-8"))
deepdives = json.loads((root / "editorial_deepdives.json").read_text(encoding="utf-8"))
lookup = {(x["artist"].casefold(), x["title"].casefold()): x for x in deepdives}
ids = {(x["artist"].casefold(), x["title"].casefold()) for x in tracks}
unknown = set(lookup) - ids
if unknown:
    raise SystemExit("Deep dives have no matching catalog record: " + repr(sorted(unknown)))
rows = []
for t in tracks:
    essay = t.get("essay", [])
    facts = t.get("facts", [])
    sources = t.get("sources", [])
    samples = t.get("samples", [])
    char_count = len("".join(essay))
    sections = lookup.get((t["artist"].casefold(), t["title"].casefold()), {}).get("sections", [])
    # A triage score, NOT a fact-check or a ranking signal.
    issues = []
    # Availability dimensions are independent: paragraph and citation counts
    # do not prove research quality or factual verification.
    if not essay:
        issues.append("missing_listening_note")
    if not sources:
        issues.append("missing_sources")
    if not samples:
        issues.append("no_sample_context")
    if not sections:
        issues.append("no_deep_dive")
    if not t.get("producer"):
        issues.append("producer_unknown")
    rows.append({
        "id": t["id"], "artist": t["artist"], "title": t["title"],
        "essay_chars": char_count, "facts": len(facts),
        "sources": len(sources), "sample_entries": len(samples),
        "deep_dive_sections": len(sections), "issue_count": len(issues),
        "issues": "|".join(issues)
    })
rows.sort(key=lambda x: (-x["issue_count"], x["sources"], x["essay_chars"], x["artist"]))
dest = root / "editorial_depth_audit.csv"
with dest.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print("Audited", len(rows), "tracks")
print("Tracks with open research dimensions:", sum(bool(r["issue_count"]) for r in rows))
print("Lowest depth candidates:")
for r in rows[:20]:
    print(f'  {r["artist"]} — {r["title"]}: {r["issues"]}')
print("Report:", dest)
