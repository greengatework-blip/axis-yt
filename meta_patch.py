from pathlib import Path
from datetime import date
import json

ROOT = Path(r"C:\AXIS_YT")
today = date.today().isoformat()
META = ROOT/"out"/today/"meta.json"

# --- guard: meta.json が無ければ非致命SKIP ---
if not META.exists():
    print("SKIP: META not found:", META)
    raise SystemExit(0)

with open(META,"r",encoding="utf-8") as f:
    m=json.load(f)

# 既に video_id があるなら何もしない
if m.get("video_id"):
    print("SKIP: video_id exists")
    raise SystemExit(0)

print("NOOP: nothing to patch")
