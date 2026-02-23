import sys, json, os, datetime

date = datetime.date.today().isoformat()
slot = "am"
out = f"C:/AXIS_SPACE/out/{date}/{slot}"
os.makedirs(out, exist_ok=True)

meta = {
  "title": f"Deep Space | {date}",
  "description": "Auto-generated (stub)",
  "tags": ["space","nasa"],
  "privacyStatus": "public",
  "video_path": f"{out}/short.mp4"
}

with open(f"{out}/meta.json","w",encoding="utf-8") as f:
  json.dump(meta,f,ensure_ascii=False,indent=2)

print("space stub OK")