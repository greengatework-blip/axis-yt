import os
import json
import datetime
import subprocess
import argparse


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--slot", default="am", choices=["am", "pm"])
    args = ap.parse_args()

    DATE = args.date
    SLOT = args.slot
    DURATION = 18  # seconds

    outv = f"C:/AXIS_SPACE/out/{DATE}/{SLOT}"
    outh = f"C:/AXIS_SPACE_WEB/site/{DATE}"
    os.makedirs(outv, exist_ok=True)
    os.makedirs(outh, exist_ok=True)

    # --- Copy (英語前提：母数最大化)
    HOOK = f"DEEP SPACE • {DATE}"
    QUESTION = "What are you looking at?"
    ANSWER = "A real cosmic scene — explained in 15 seconds."

    title = f"Deep Space | {DATE} ({SLOT.upper()})"
    desc = "Daily deep-space view. Educational content."
    meaning = "Short explanation for learning + discovery."

    video = f"{outv}/short.mp4"

    # ===== ffmpeg filtergraph =====
    # 目的：黒背景を捨てて、常に“動き/奥行き/変化”がある状態を作る（スワイプ耐性）
    # - noise + blur: 星っぽい粒子
    # - zoompan: 疑似パララックス（奥行き）
    # - hue: 色相がゆっくり変化（報酬予測）
    # - texts: 0-6 / 6-12 / 12-18 で切替
    vf = (
        "format=yuv420p,"
        "noise=alls=20:allf=t+u,"
        "boxblur=2:1,"
        "zoompan=z='min(zoom+0.0005,1.2)':d=1:"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920,"
        "hue='H=2*PI*t/10',"
        # Header bar
        "drawbox=x=0:y=0:w=1080:h=140:color=white@0.06:t=fill,"
        "drawtext=text='AXIS • DEEP SPACE':fontcolor=white:fontsize=34:"
        "x=(w-text_w)/2:y=50,"
        # 3 blocks
        f"drawtext=text='{HOOK}':fontcolor=white:fontsize=64:"
        "x=(w-text_w)/2:y=420:enable='between(t,0,6)',"
        f"drawtext=text='{QUESTION}':fontcolor=white:fontsize=56:"
        "x=(w-text_w)/2:y=420:enable='between(t,6,12)',"
        f"drawtext=text='{ANSWER}':fontcolor=white:fontsize=48:"
        "x=(w-text_w)/2:y=420:enable='between(t,12,18)',"
        # Bottom CTA
        "drawbox=x=0:y=1680:w=1080:h=240:color=white@0.05:t=fill,"
        "drawtext=text='Follow for daily space insights':fontcolor=white:fontsize=32:"
        "x=(w-text_w)/2:y=1760"
    )

    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:d={DURATION}",
        "-vf", vf,
        "-r", "30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
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
    with open(f"{outv}/meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # HTML（Git外ディレクトリへ）
    tpl_path = "C:/AXIS_YT/space/template.html"
    tpl = open(tpl_path, encoding="utf-8").read()
    html = (
        tpl.replace("{{TITLE}}", title)
           .replace("{{DESC}}", desc)
           .replace("{{MEANING}}", meaning)
           .replace("{{DATE}}", DATE)
    )

    with open(f"{outh}/deep-space-{DATE}-{SLOT}.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("space video + web OK", DATE, SLOT)


if __name__ == "__main__":
    main()