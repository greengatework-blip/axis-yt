import requests, pandas as pd, pathlib

ROOT = pathlib.Path(r"C:\AXIS_YT")
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

url = "https://raw.githubusercontent.com/datasets/cost-of-living/master/data/cost-of-living.csv"
r = requests.get(url, timeout=30)
r.raise_for_status()

csv_path = DATA / "cost_of_living.csv"
with open(csv_path,"wb") as f:
    f.write(r.content)

df = pd.read_csv(csv_path)
df = df.sort_values("Cost of Living Index", ascending=False).head(10)

top10 = DATA / "top10_cost.json"
df.to_json(top10, orient="records", force_ascii=False, indent=2)
print("OK:", top10)
