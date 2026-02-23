import os
import sys
import subprocess
import datetime
import pathlib

ROOT = pathlib.Path(r"C:\AXIS_YT")
PY = str(ROOT / "venv" / "Scripts" / "python.exe")


def axis_date() -> str:
    s = os.environ.get("AXIS_DATE", "").strip()
    return s if s else datetime.date.today().isoformat()


AXIS_DATE = axis_date()
OUT = ROOT / "out" / AXIS_DATE
OUT.mkdir(parents=True, exist_ok=True)

LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
LOG = LOGS / f"{datetime.date.today().isoformat()}.log"


def log_line(line: str) -> None:
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()


def run(cmd, extra_env=None) -> int:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    log_line(f"\n$ {' '.join(map(str, cmd))}")

    # capture stdout/stderr into the same daily log
    with open(LOG, "a", encoding="utf-8") as f:
        p = subprocess.run(
            list(map(str, cmd)),
            stdout=f,
            stderr=f,
            text=True,
            env=env,
        )
    return int(p.returncode)


def guard_exists(path: pathlib.Path, exit_code: int, msg: str) -> None:
    if not path.exists():
        print(msg)
        log_line(msg)
        sys.exit(exit_code)


# ===== pipeline =====
# ① generate (idempotent)
if not (OUT / "short.mp4").exists():
    rc = run([PY, ROOT / "daily.py"], {"AXIS_DATE": AXIS_DATE})
    if rc != 0:
        sys.exit(rc)

# ② guard: short must exist
guard_exists(
    OUT / "short.mp4",
    2,
    f"AXIS_DAILY_EXIT=2 missing short.mp4 in {OUT}",
)

# ③ guard: meta must exist BEFORE meta_patch (prevents FileNotFound)
guard_exists(
    OUT / "meta.json",
    2,
    f"AXIS_DAILY_EXIT=2 missing meta.json in {OUT}",
)

# ④ meta_patch (idempotent)
rc = run([PY, ROOT / "meta_patch.py"], {"AXIS_DATE": AXIS_DATE})
if rc != 0:
    sys.exit(rc)

# ⑤ guard again: meta still must exist
guard_exists(
    OUT / "meta.json",
    2,
    f"AXIS_DAILY_EXIT=2 missing meta.json in {OUT}",
)

# ⑥ upload (idempotent via uploaded.json); retry once if rc!=0
if not (OUT / "uploaded.json").exists():
    rc = run([PY, ROOT / "upload.py"], {"AXIS_DATE": AXIS_DATE})
    if rc != 0:
        rc = run([PY, ROOT / "upload.py"], {"AXIS_DATE": AXIS_DATE})
        if rc != 0:
            sys.exit(rc)

print("AXIS_DAILY_EXIT=0")
log_line("AXIS_DAILY_EXIT=0")

# ===== post-upload (non-fatal) =====
try:
    run([PY, ROOT / "fetch_views.py"], {"AXIS_DATE": AXIS_DATE})
except Exception as e:
    msg = f"WARN: fetch_views failed: {e}"
    print(msg)
    log_line(msg)

try:
    run([PY, ROOT / "append_metrics.py"], {"AXIS_DATE": AXIS_DATE})
except Exception as e:
    msg = f"WARN: append_metrics failed: {e}"
    print(msg)
    log_line(msg)

sys.exit(0)