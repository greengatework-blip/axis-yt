$ErrorActionPreference = "Stop"

# === Config ===
$RepoDir = "C:\AXIS_YT"   # VPSでは C:\AXIS_YT に clone/pull する前提
$LockDir = "C:\AXIS_YT\logs"
$Lock    = Join-Path $LockDir "pull.lock"
$Log     = Join-Path $LockDir "pull.log"

if (-not (Test-Path $LockDir)) { New-Item -ItemType Directory -Path $LockDir | Out-Null }

# === Lock (prevent concurrent pulls) ===
if (Test-Path $Lock) { throw "pull.lock exists -> another job may be running" }
New-Item -ItemType File -Path $Lock | Out-Null

try {
  Set-Location $RepoDir

  # Ensure we are on main
  git rev-parse --is-inside-work-tree | Out-Null
  git checkout main | Out-Null

  # Hard-sync to origin/main (Prodは手編集禁止)
  git fetch --all
  git reset --hard origin/main
  git clean -fd

  $head = git rev-parse HEAD
  "$(Get-Date -Format s) OK HEAD=$head" | Add-Content -Encoding utf8 $Log

} catch {
  "$(Get-Date -Format s) NG $($_.Exception.Message)" | Add-Content -Encoding utf8 $Log
  throw
} finally {
  Remove-Item $Lock -Force -ErrorAction SilentlyContinue
}