# daily.py (AXIS_YT) - fully portable daily generator
# - ffmpeg: auto-detect (PATH -> imageio_ffmpeg bundled fallback)
# - output: C:/AXIS_YT/out/YYYY-MM-DD/short.mp4 + meta.json
# - headless-safe: matplotlib Agg
# - JST local clock (Windows local)

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

# ----------------------------
# FFMPEG auto-detect (portable)
# ----------------------------
def resolve_ffmpeg() -> str:
    # 1) If system ffmpeg is available
    ff = shutil.which("ffmpeg")
    if ff:
        return ff

    # 2) Fallback to imageio-ffmpeg bundled binary (installed via pip: imageio-ffmpeg)
    try:
        import imageio_ffmpeg as i
        return i.get_ffmpeg_exe()
    except Exception as e:
        raise RuntimeError(
            "ffmpeg not found. Install ffmpeg (add to PATH) or install imageio-ffmpeg.\n"
            "pip install imageio-ffmpeg"
        ) from e


os.environ["IMAGEIO_FFMPEG_EXE"] = resolve_ffmpeg()

# ----------------------------
# Headless matplotlib
# ----------------------------
import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageClip, concatenate_videoclips

# ----------------------------
# Visual params
# ----------------------------
W, H = 1080, 1920
bg = (0.08, 0.09, 0.11)
c1 = (0.20, 0.70, 0.90)

HOOKS = [
    "This is 3x more expensive than you think.",
    "Most people can’t afford this city.",
    "You’re probably living in the wrong place.",
]

# ----------------------------
# Paths (portable / consistent)
# ----------------------------
ROOT = Path("C:/AXIS_YT")
OUT_ROOT = ROOT / "out"
OUT_ROOT.mkdir(parents=True, exist_ok=True)


def fig_to_rgb(fig):
    fig.canvas.draw()
    w, h = fig.canvas.get_width_height()
    buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
    img = buf.reshape(h, w, 4)[:, :, :3]
    return img


def make_frame(rank_vals, labels, title, hook_text=None, source_text=None, top3=False):
    fig = plt.figure(figsize=(W / 100, H / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    ax.set_xlim(0, 110)
    ax.set_ylim(-1, 10)
    ax.axis("off")

    ax.text(
        0.05, 0.94, title,
        transform=ax.transAxes,
        color="white", fontsize=44, fontweight="bold",
        ha="left", va="top",
    )

    y = np.arange(10)[::-1]
    for i, yi in enumerate(y):
        v = float(rank_vals[i])
        lw = 6 if (top3 and i >= 7) else 0
        ax.barh(yi, v, height=0.65, color=c1, edgecolor="white", linewidth=lw, alpha=0.95)
        ax.text(2, yi, labels[i], color="white", fontsize=26, va="center", ha="left", alpha=0.95)
        ax.text(min(v + 2, 105), yi, f"{int(round(v))}", color="white", fontsize=26, va="center", ha="left", alpha=0.95)

    if hook_text:
        ax.text(
            0.5, 0.83, hook_text,
            transform=ax.transAxes,
            color="white", fontsize=46, fontweight="bold",
            ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.6", facecolor=(0, 0, 0, 0.25), edgecolor=(1, 1, 1, 0.15)),
        )

    if source_text:
        ax.text(
            0.98, 0.03, source_text,
            transform=ax.transAxes,
            color="white", fontsize=22, ha="right", va="bottom", alpha=0.85,
        )

    img = fig_to_rgb(fig)
    plt.close(fig)
    return img


def main():
    # Local (JST on your machine)
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    hook = HOOKS[now.toordinal() % len(HOOKS)]

    outdir = OUT_ROOT / today
    outdir.mkdir(parents=True, exist_ok=True)

    labels = [f"Rank {i}" for i in range(10, 0, -1)]
    base = np.linspace(10, 100, 10)

    title = "Cost of Living Index"
    src = "Source: Numbeo | " + now.strftime("%Y-%m")

    # --- clips ---
    hook_img = make_frame(base * 0.2, labels, title, hook_text=hook)
    hook_clip = ImageClip(hook_img).set_duration(2.0)

    frames = [make_frame(base * t, labels, title) for t in np.linspace(0.2, 1.0, 28)]
    rank_clip = concatenate_videoclips([ImageClip(f).set_duration(0.5) for f in frames], method="compose")

    top3_img = make_frame(base * 1.0, labels, title, top3=True)
    top3_clip = ImageClip(top3_img).set_duration(4.0)

    src_img = make_frame(base * 1.0, labels, title, source_text=src, top3=True)
    src_clip = ImageClip(src_img).set_duration(2.0)

    out = concatenate_videoclips([hook_clip, rank_clip, top3_clip, src_clip], method="compose")

    # --- outputs ---
    mp4 = outdir / "short.mp4"
    meta_json = outdir / "meta.json"

    out.write_videofile(
        str(mp4),
        fps=30,
        codec="libx264",
        audio=False,
        ffmpeg_params=["-pix_fmt", "yuv420p"],
    )

    meta = {
        "date": today,
        "video": str(mp4),
        "title": f"Daily Rank — {today}",
        "desc": "Data source: Numbeo\nConclusion: (TBD)",
        "privacy": "private",
        "hook": hook,
        "source": src,
    }
    meta_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print("OK:", mp4)
    print("META:", meta_json)


if __name__ == "__main__":
    main()