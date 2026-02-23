import os, json, datetime, subprocess, random

date = datetime.date.today().isoformat()
slot = "am"

outv = f"C:/AXIS_SPACE/out/{date}/{slot}"
outh = f"C:/AXIS_SPACE_WEB/site/{date}"
os.makedirs(outv, exist_ok=True)
os.makedirs(outh, exist_ok=True)

title = f"Deep Space View | {date}"
desc  = "A daily look into the deep universe."
meaning = "Understanding cosmic structures helps reveal our origin."

# --- 動画生成（ダミー：黒背景＋テキスト）
video = f"{outv}/short.mp4"
cmd = [
"ffmpeg","-y",
"-f","lavfi","-i","color=c=black:s=1080x1920:d=8",
"-vf",f"drawtext=text='{title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
video
]
subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# --- meta.json
meta = {
"title": title,
"description": desc,
"tags": ["space","astronomy"],
"privacyStatus": "public",
"video_path": video
}
with open(f"{outv}/meta.json","w",encoding="utf-8") as f:
  json.dump(meta,f,ensure_ascii=False,indent=2)

# --- HTML生成
tpl = open("C:/AXIS_YT/space/template.html",encoding="utf-8").read()
html = tpl.replace("{{TITLE}}",title)\
          .replace("{{DESC}}",desc)\
          .replace("{{MEANING}}",meaning)\
          .replace("{{DATE}}",date)

with open(f"{outh}/deep-space-{date}.html","w",encoding="utf-8") as f:
  f.write(html)

print("space video + web OK")