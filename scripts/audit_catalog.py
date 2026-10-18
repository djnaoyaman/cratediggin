"""Audit catalog metadata and optionally compare YouTube oEmbed titles.

Offline validation never treats a plausible video ID as proof of the correct recording.
Run: python scripts/audit_catalog.py
Run: python scripts/audit_catalog.py --online
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlencode, urlparse, parse_qs
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "audit-reports"
FIELDS = ["id", "artist", "title", "year", "youtube_id", "youtube_url",
          "uploader", "video_title", "video_status", "metadata_status",
          "issues", "source_count", "essay_paragraphs"]


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def check_video(track):
    video = track.get("youtube") or {}
    vid = video.get("id")
    if not vid:
        return ("PLAYLIST_METADATA_ONLY" if video.get("playlistId") else "NO_VIDEO", "", "")
    url = "https://www.youtube.com/watch?" + urlencode({"v": vid})
    endpoint = "https://www.youtube.com/oembed?" + urlencode({"url": url, "format": "json"})
    try:
        with urlopen(Request(endpoint, headers={"User-Agent": "Mozilla/5.0"}), timeout=7) as response:
            data = json.load(response)
        title = data.get("title", "")
        uploader = data.get("author_name", "")
        # oEmbed does not prove recording identity, remix/version, or playback availability.
        tokens = [w for w in normalized(track["title"]).split() if len(w) >= 3]
        match = bool(tokens) and sum(w in normalized(title) for w in tokens) >= max(1, len(tokens) // 2)
        return ("TITLE_CANDIDATE" if match else "REVIEW_TITLE_MISMATCH", title, uploader)
    except Exception as exc:
        return ("UNVERIFIED_REMOTE", "", type(exc).__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true", help="Query YouTube oEmbed; results are leads, not proof")
    args = parser.parse_args()
    tracks = json.loads((ROOT / "tracks.json").read_text(encoding="utf-8"))
    releases = json.loads((ROOT / "releases.json").read_text(encoding="utf-8"))
    ids = Counter(t.get("id") for t in tracks)
    video_ids = Counter((t.get("youtube") or {}).get("id") for t in tracks if (t.get("youtube") or {}).get("id"))
    rows = []
    fatal = []
    if not tracks:
        fatal.append("Catalog must not be empty")
    if not any(t.get("id") == "dj-shadow-the-number-song" for t in tracks):
        fatal.append("The Number Song is missing")
    for t in tracks:
        issues = []
        tid = t.get("id", "")
        video = t.get("youtube") or {}
        vid = video.get("id")
        if not re.fullmatch(r"[a-z0-9-]+", tid):
            fatal.append("Invalid ID: " + tid)
        if ids[tid] > 1:
            fatal.append("Duplicate ID: " + tid)
        if vid and not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid):
            fatal.append("Invalid YouTube ID: " + tid)
        if vid and video_ids[vid] > 1:
            issues.append("SHARED_VIDEO_ID")
        if vid and parse_qs(urlparse(video.get("url", "")).query).get("v") != [vid]:
            issues.append("VIDEO_URL_MISMATCH")
        if not vid and not video.get("playlistId"):
            issues.append("AUDIO_NOT_VERIFIED")
        if not t.get("sources"):
            fatal.append("Missing sources: " + tid)
        if not t.get("essay"):
            fatal.append("Missing listening note: " + tid)
        if "未確認" in t.get("label", "") or "確認中" in t.get("label", ""):
            issues.append("LABEL_NEEDS_RESEARCH")
        if "継続中" in t.get("yearBasis", "") or "照合中" in t.get("yearBasis", ""):
            issues.append("YEAR_NEEDS_RESEARCH")
        if any(not s.get("url", "").startswith("https://") for s in t.get("sources", [])):
            fatal.append("Invalid source URL: " + tid)
        if vid and not video.get("verification"):
            issues.append("VIDEO_PROVENANCE_MISSING")
        rows.append(dict(id=tid, artist=t.get("artist"), title=t.get("title"), year=t.get("year"),
                         youtube_id=vid or "", youtube_url=video.get("url") or "",
                         uploader="", video_title="", video_status="NOT_CHECKED" if vid else "PLAYLIST_METADATA_ONLY" if video.get("playlistId") else "NO_VIDEO",
                         metadata_status="REVIEW" if issues else "STRUCTURALLY_OK",
                         issues=";".join(issues), source_count=len(t.get("sources", [])),
                         essay_paragraphs=len(t.get("essay", []))))
    if args.online:
        with ThreadPoolExecutor(max_workers=6) as pool:
            jobs = {pool.submit(check_video, t): i for i, t in enumerate(tracks)}
            for job in as_completed(jobs):
                i = jobs[job]
                status, title, uploader = job.result()
                rows[i].update(video_status=status, video_title=title, uploader=uploader)
    REPORTS.mkdir(exist_ok=True)
    with (REPORTS / "catalog-audit.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "version": releases["version"], "total_tracks": len(tracks),
        "total_songs": sum(t.get("workType", "single")=="single" for t in tracks),
        "total_mixes": sum(t.get("workType")=="mix" for t in tracks),
        "total_albums": sum(t.get("workType")=="album" for t in tracks),
        "with_playlist_id":sum(bool(t.get("youtube",{}).get("playlistId")) for t in tracks),
        "total_live_videos": sum(t.get("workType")=="live_video" for t in tracks),
        "with_video_id": sum(bool(t["youtube_id"]) for t in rows),
        "without_video_id": sum(not t["youtube_id"] for t in rows),
        "duplicate_video_ids": sum(n - 1 for n in video_ids.values() if n > 1),
        "metadata_review_needed": sum(t["metadata_status"] == "REVIEW" for t in rows),
        "video_status": dict(Counter(t["video_status"] for t in rows)),
        "fatal_errors": sorted(set(fatal)),
        "note": "oEmbed title matches are NOT human verification of correct recording, version, or embeddability."
    }
    (REPORTS / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
