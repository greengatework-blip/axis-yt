from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, date, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(r"C:\AXIS_YT")
TODAY = (Path.cwd() if False else None)  # noop
axis_date = ( __import__("os").environ.get("AXIS_DATE") or date.today().isoformat() )
OUT = ROOT / "out" / axis_date
META = OUT / "meta.json"
UPLOADED = OUT / "uploaded.json"
TOKEN = ROOT / "token.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None

def extract_video_id(uploaded_obj):
    # handle dict {"video_id": "..."} or list[{"video_id": "..."}] or {"items":[...]}
    if uploaded_obj is None:
        return None
    if isinstance(uploaded_obj, dict):
        if "video_id" in uploaded_obj and uploaded_obj["video_id"]:
            return uploaded_obj["video_id"]
        for k in ("items", "videos", "data"):
            v = uploaded_obj.get(k)
            if isinstance(v, list) and v:
                for it in reversed(v):
                    if isinstance(it, dict) and it.get("video_id"):
                        return it["video_id"]
    if isinstance(uploaded_obj, list):
        for it in reversed(uploaded_obj):
            if isinstance(it, dict) and it.get("video_id"):
                return it["video_id"]
    return None

if not META.exists():
    print("NO_META")
    raise SystemExit(2)

m = load_json(META) or {}
vid = m.get("video_id")

if not vid and UPLOADED.exists():
    u = load_json(UPLOADED)
    vid = extract_video_id(u)
    if vid:
        m["video_id"] = vid
        META.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

if not vid:
    print("NO_VIDEO_ID")
    raise SystemExit(3)

creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
yt = build("youtube", "v3", credentials=creds)

resp = yt.videos().list(part="statistics", id=vid).execute()
items = resp.get("items") or []
stats = (items[0].get("statistics") if items else {}) or {}
views = int(stats.get("viewCount", 0))

m["views"] = views
m["views_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z"
META.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

print("VIEWS=", views)


