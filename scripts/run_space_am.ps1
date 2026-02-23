$ErrorActionPreference = "Stop"

# 0) Pull latest (Prodは手編集禁止)
& "C:\AXIS_YT\scripts\axis_pull.ps1"

# 1) Generate Space (stub today)
$py = "C:\AXIS_YT\venv\Scripts\python.exe"
$date = (Get-Date).ToString("yyyy-MM-dd")
& $py "C:\AXIS_YT\space\make_space.py" --date $date --slot am

# 2) Upload (既存エンジン)
$meta = "C:\AXIS_SPACE\out\$date\am\meta.json"
& $py "C:\AXIS_YT\upload.py" --meta $meta --token "C:\AXIS_YT\secrets\token_space.json"