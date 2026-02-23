import os, datetime
date = datetime.date.today().isoformat()
p = f"C:/AXIS_FIN_WEB/site/fin/{date}.html"
os.makedirs(os.path.dirname(p), exist_ok=True)
open(p,"w",encoding="utf-8").write("<h1>Financial stub</h1>")
print("fin stub OK")