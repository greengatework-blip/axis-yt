import json, datetime, pathlib

ROOT = pathlib.Path(r"C:\AXIS_YT")
TODAY = datetime.date.today()
OUT = ROOT / "out" / TODAY.isoformat()
META = OUT / "meta.json"

rotation = {
    0:"Cost of Living",
    1:"Safety",
    2:"Internet Speed",
    3:"Walkability",
    4:"Salaries",
    5:"Cost of Living",
    6:"Safety"
}

theme = rotation[TODAY.weekday()]
year = TODAY.year

title = f"Top 10 Cities by {theme} ({year})"
desc = f"Ranking global cities by {theme}. Source: Numbeo / World Bank. Updated {year}."
tags = ["city ranking","global cities","cost of living","safety","internet","walkability","salary","top 10"]

with open(META,"r",encoding="utf-8") as f:
    meta = json.load(f)

meta["title"]=title
meta["description"]=desc
meta["tags"]=tags

with open(META,"w",encoding="utf-8") as f:
    json.dump(meta,f,ensure_ascii=False,indent=2)
