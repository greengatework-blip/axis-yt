import os, subprocess, sys, datetime, pathlib

ROOT = pathlib.Path(r"C:\AXIS_YT")

def axis_date():
    s = os.environ.get("AXIS_DATE")
    return s if s else datetime.date.today().isoformat()

AXIS_DATE = axis_date()
OUT = ROOT / "out" / AXIS_DATE
OUT.mkdir(parents=True, exist_ok=True)

LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)
LOG = LOGS / f"{datetime.date.today().isoformat()}.log"

PY = str(ROOT/"venv/Scripts/python.exe")

def run(cmd, extra_env=None):
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"\n$ {' '.join(cmd)}\n")
        f.flush()
        p = subprocess.run(cmd, stdout=f, stderr=f, text=True, env=env)
        return p.returncode

# ① 生成（存在すればSKIP）
if not (OUT / "short.mp4").exists():
    rc = run([PY, str(ROOT/"daily.py")], {"AXIS_DATE": AXIS_DATE})
    if rc != 0: sys.exit(rc)

# ② ガード：生成物必須
if not (OUT / "short.mp4").exists():
    print(f"AXIS_DAILY_EXIT=2 missing short.mp4 in {OUT}")
    sys.exit(2)

# ③ CTR注入
rc = run([PY, str(ROOT/"meta_patch.py")], {"AXIS_DATE": AXIS_DATE})
if rc != 0: sys.exit(rc)

# ④ ガード：meta必須
if not (OUT / "meta.json").exists():
    print(f"AXIS_DAILY_EXIT=2 missing meta.json in {OUT}")
    sys.exit(2)

# ⑤ 投稿（uploaded.json が無ければ実行）
if not (OUT / "uploaded.json").exists():
    rc = run([PY, str(ROOT/"upload.py")], {"AXIS_DATE": AXIS_DATE})
    if rc != 0:
        rc = run([PY, str(ROOT/"upload.py")], {"AXIS_DATE": AXIS_DATE})
        if rc != 0: sys.exit(rc)

print("AXIS_DAILY_EXIT=0")
sys.exit(0)
