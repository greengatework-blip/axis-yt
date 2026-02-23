import csv, pathlib, datetime

p = pathlib.Path(r"C:\AXIS_YT\data\metrics.csv")
if not p.exists():
    print("NO_FILE", p); raise SystemExit(2)

bak = p.with_suffix(".csv.bak_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
bak.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")

rows=[]
with p.open("r", encoding="utf-8", newline="") as f:
    r=csv.DictReader(f)
    fields=r.fieldnames or ["date","video_id","title","views"]
    for row in r:
        if row.get("date"):
            rows.append(row)

# keep last occurrence per date
last={}
for row in rows:
    last[row["date"]] = row

# stable sort by date
out=[last[k] for k in sorted(last.keys())]

with p.open("w", encoding="utf-8", newline="") as f:
    w=csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

print("BACKUP", bak)
print("WROTE", p, "rows=", len(out))
