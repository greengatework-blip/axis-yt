import os, json, datetime, subprocess, argparse

def run(cmd):
    subprocess.run(cmd, check=True)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--slot", default="am", choices=["am", "pm"])
    args = ap.parse_args()

    DATE = args.date
    SLOT = args.slot
    DURATION = 18  # seconds (固定)

    outv = f"C:/AXIS_SPACE/out/{DATE}/{SLOT}"
    outh = f"C:/AXIS_SPACE_WEB/site/{DATE}"
    os.makedirs(outv, exist_ok=True)
    os.makedirs(outh, exist_ok=True)

    # --- Copy (英語前提：母数最大化)
    HOOK = f"DEEP SPACE • {DATE}"
    QUESTION = "What are you looking at?"
    ANSWER = "A real cosmic scene — explained in 15 seconds."

    title = f"Deep Space | {DATE} ({SLOT.upper()})"
    desc  = "Daily deep-space view. Educational content."
    meaning = "Short explanation for learning + discovery."

    video = f"{outv}/short.mp4"

    # 3ブロック：0-6 / 6-12 / 12-18
    # drawtextは重ねがけ。enableで時間制御。
    vf = (
        "scale=1080:1920,"
        "format=yuv420p,"
        f"drawtext=text='{HOOK}':fontcolor=white:fontsize=56:x=(w-text_w)/2:y=320:enable='between(t,0,6)',"
        f"drawtext=text='{QUESTION}':fontcolor=white:fontsize=52:x=(w-text_w)/2:y=320:enable='between(t,6,12)',"
        f"drawtext=text='{ANSWER}':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=320:enable='between(t,12,18)'"
    )

    cmd = [
        "ffmpeg","-y",
        "-f","lavfi","-i",f"color=c=black:s=1080x1920:d={DURATION}",
        "-vf",vf,
        "-r","30",
        "-c:v","libx264","-pix_fmt","yuv420p",
        video
    ]
    run(cmd)

    meta = {
        "title": title,
        "description": desc,
        "tags": ["space", "astronomy", "science"],
        "privacyStatus": "public",
        "video_path": video
    }
    with open(f"{outv}/meta.json","w",encoding="utf-8") as f:
        json.dump(meta,f,ensure_ascii=False,indent=2)

    # HTML（生成はGit外ディレクトリへ）
    tpl_path = "C:/AXIS_YT/space/template.html"
    tpl = open(tpl_path,encoding="utf-8").read()
    html = tpl.replace("{{TITLE}}",title)\
              .replace("{{DESC}}",desc)\
              .replace("{{MEANING}}",meaning)\
              .replace("{{DATE}}",DATE)
    with open(f"{outh}/deep-space-{DATE}-{SLOT}.html","w",encoding="utf-8") as f:
        f.write(html)

    print("space video + web OK", DATE, SLOT)

if __name__ == "__main__":
    main()