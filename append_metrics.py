import csv, json, pathlib, datetime

ROOT = pathlib.Path(r"C:\AXIS_YT")
OUT  = ROOT/"out"
DATA = ROOT/"data"
DATA.mkdir(parents=True, exist_ok=True)

today = datetime.date.today().isoformat()
outdir = OUT/today
meta_path = outdir/"meta.json"
if not meta_path.exists():
    print("NO_META", meta_path); raise SystemExit(2)

m = json.loads(meta_path.read_text(encoding="utf-8"))
row = {
    "date": today,
    "video_id": m.get("video_id",""),
    "title": m.get("title",""),
    "views": int(m.get("views",0) or 0),
    "theme": m.get("theme",""),
    "hook": m.get("hook",""),
    "variant": m.get("variant",""),
}

out_csv = DATA/"metrics.csv"

fields = ["date","video_id","title","views","theme","hook","variant"]

# guard: avoid duplicate date rows
if out_csv.exists():
    with out_csv.open("r", encoding="utf-8", newline="") as rf:
        r = csv.DictReader(rf)
        for old in r:
            if (old.get("date") or "").strip() == row["date"]:
                print("SKIP: already in metrics:", row["date"])
                raise SystemExit(0)

is_new = not out_csv.exists()
with out_csv.open("a", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    if is_new:
        w.writeheader()
    w.writerow(row)

print("APPENDED", row)
print("CSV", out_csv)
