import os, subprocess, sys, shutil
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(r"C:\AXIS_YT")
OUT = ROOT / "out"
LOGDIR = ROOT / "logs"
LOGDIR.mkdir(parents=True, exist_ok=True)

os.environ["AXIS_FFMPEG"] = r"C:\AXIS_YT\bin\ffmpeg.exe"
os.environ["IMAGEIO_FFMPEG_EXE"] = os.environ["AXIS_FFMPEG"]

today = datetime.now().strftime("%Y-%m-%d")
yday  = (datetime.now()-timedelta(days=1)).strftime("%Y-%m-%d")

t_out = OUT / today
y_out = OUT / yday
t_out.mkdir(parents=True, exist_ok=True)

log = LOGDIR / f"daily_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

cmd = [r"C:\AXIS_YT\venv\Scripts\python.exe", r"C:\AXIS_YT\daily.py"]

with log.open("w", encoding="utf-8") as f:
    p = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT, timeout=600)

if p.returncode != 0:
    src = y_out / "short.mp4"
    dst = t_out / "short.mp4"
    if src.exists():
        shutil.copy(src, dst)
        with (t_out/"meta.txt").open("w",encoding="utf-8") as m:
            m.write("fallback=previous_day\n")
        sys.exit(0)

sys.exit(p.returncode)
