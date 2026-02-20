import os
import shutil

ff = shutil.which("ffmpeg")
if not ff:
    import imageio_ffmpeg as i
    ff = i.get_ffmpeg_exe()

os.environ["IMAGEIO_FFMPEG_EXE"] = ff


import matplotlib
matplotlib.use("Agg")  # 無人運用固定

import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageClip, concatenate_videoclips
from datetime import datetime

W,H = 1080,1920
bg = (0.08,0.09,0.11)
c1 = (0.20,0.70,0.90)

def fig_to_rgb(fig):
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    img = buf.reshape(h, w, 4)[:, :, :3]
    return img

def make_frame(rank_vals, labels, title, hook_text=None, source_text=None, top3=False):
    # 1080x1920を直接作る（9:16固定）
    fig = plt.figure(figsize=(W/100, H/100), dpi=100)
    ax = fig.add_axes([0,0,1,1])
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 110)
    ax.set_ylim(-1, 10)
    ax.axis("off")

    # タイトル
    ax.text(0.05, 0.94, title, transform=ax.transAxes,
            color="white", fontsize=44, fontweight="bold", ha="left", va="top")

    # バー（10→1）
    y = np.arange(10)[::-1]  # 上がRank10
    for i, yi in enumerate(y):
        v = float(rank_vals[i])
        # Top3強調（Rank3,2,1 = 下3本）
        lw = 6 if (top3 and i>=7) else 0
        ax.barh(yi, v, height=0.65, color=c1, edgecolor="white", linewidth=lw, alpha=0.95)
        ax.text(2, yi, labels[i], color="white", fontsize=26, va="center", ha="left", alpha=0.95)
        ax.text(min(v+2,105), yi, f"{int(round(v))}", color="white", fontsize=26, va="center", ha="left", alpha=0.95)

    # Hook（中央上）
    if hook_text:
        ax.text(0.5, 0.83, hook_text, transform=ax.transAxes,
                color="white", fontsize=46, fontweight="bold",
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.6", facecolor=(0,0,0,0.25), edgecolor=(1,1,1,0.15)))

    # Source/Date（右下）
    if source_text:
        ax.text(0.98, 0.03, source_text, transform=ax.transAxes,
                color="white", fontsize=22, ha="right", va="bottom", alpha=0.85)

    img = fig_to_rgb(fig)
    plt.close(fig)
    return img

def main():
    labels = [f"Rank {i}" for i in range(10,0,-1)]
    base = np.linspace(10, 100, 10)

    # 0-2s Hook
    hook = "Most people can’t afford this city."
    src = "Source: Numbeo | " + datetime.now().strftime("%Y-%m")

    hook_img = make_frame(base*0.2, labels, "Cost of Living Index", hook_text=hook)
    hook_clip = ImageClip(hook_img).set_duration(2.0)

    # 2-16s Ranking grow（14s）
    frames = []
    for t in np.linspace(0.2, 1.0, 28):  # 28枚×0.5s=14s
        frames.append(make_frame(base*t, labels, "Cost of Living Index"))
    rank_clip = concatenate_videoclips([ImageClip(f).set_duration(0.5) for f in frames], method="compose")

    # 16-20s Top3強調（4s）
    top3_img = make_frame(base*1.0, labels, "Cost of Living Index", top3=True)
    top3_clip = ImageClip(top3_img).set_duration(4.0)

    # 20-22s Source/Date（2s）
    src_img = make_frame(base*1.0, labels, "Cost of Living Index", source_text=src, top3=True)
    src_clip = ImageClip(src_img).set_duration(2.0)

    out = concatenate_videoclips([hook_clip, rank_clip, top3_clip, src_clip], method="compose")

    out.write_videofile(
        "C:/AXIS_YT/poc_short.mp4",
        fps=30,
        codec="libx264",
        audio=False,
        ffmpeg_params=["-pix_fmt","yuv420p"]
    )

if __name__ == "__main__":
    main()
