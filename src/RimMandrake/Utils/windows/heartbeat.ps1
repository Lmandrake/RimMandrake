<#
Heartbeat: a watchdog that lives OUTSIDE WSL (HEARTBEAT_BUILD_OUTSIDE_THE_SINKING_SHIP). The 2026-11-01 disk outage
stopped every WSL-side alarm for ~6 h; this runs as a Windows Scheduled Task with no WSL dependency for its own state.
Checks, every run:
  commits  GitHub origin/main (public repo, anonymous API) has no commit for -StaleMinutes  -> alert
  wsl      a real small write inside WSL (echo > ~/.hb_probe; sync) fails or hangs past -ProbeSeconds -> alert
Alert = a Todoist Inbox task due a minute out (rings on the phone; same route as pulse/phone_push.py). One alert per
open cause; reminder every -RemindMinutes while it stays open; state clears when the cause goes green.
Token: Todoist API token in <StateDir>\todoist_token (NOT in the repo). Pause (planned stop): create <StateDir>\paused.
Test hooks: -FakeCommitAgeMinutes N, -FakeWslFail, -DryRun (log the alert, send nothing).
#>
param(
  [int]$StaleMinutes = 180,
  [int]$ProbeSeconds = 90,
  [int]$RemindMinutes = 360,
  [string]$StateDir = 'D:\ClaudeWork\heartbeat',
  [string]$Repo = 'Lmandrake/RimMandrake',
  [int]$FakeCommitAgeMinutes = -1,
  [switch]$FakeWslFail,
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
$log = Join-Path $StateDir 'heartbeat.log'
$stateFile = Join-Path $StateDir 'state.json'
function Log($m) { Add-Content -Path $log -Value ("{0} {1}" -f (Get-Date -Format 's'), $m) }

function Send-Phone($title, $body) {
  if ($DryRun) { Log "DRYRUN alert: $title | $body"; return }
  $tf = Join-Path $StateDir 'todoist_token'
  if (-not (Test-Path $tf)) { Log "NO TOKEN at $tf; alert not sent: $title"; return }
  $tok = (Get-Content $tf -Raw).Trim()
  $due = (Get-Date).ToUniversalTime().AddMinutes(1).ToString('yyyy-MM-ddTHH:mm:ssZ')
  $json = @{ content = $title; description = $body; priority = 4; due_datetime = $due } | ConvertTo-Json
  Invoke-RestMethod -Method Post -Uri 'https://api.todoist.com/api/v1/tasks' -Headers @{ Authorization = "Bearer $tok" } `
    -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($json)) | Out-Null
  Log "alert sent: $title"
}

function Get-CommitAgeMinutes {
  if ($FakeCommitAgeMinutes -ge 0) { return $FakeCommitAgeMinutes }
  $r = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repo/commits/main" -Headers @{ 'User-Agent' = 'rm-heartbeat' } -TimeoutSec 30
  $t = [DateTimeOffset]::Parse($r.commit.committer.date)
  return [int]((Get-Date).ToUniversalTime() - $t.UtcDateTime).TotalMinutes
}

function Test-WslWrite {
  if ($FakeWslFail) { return 'fake failure' }
  # CreateNoWindow + no shell: Start-Process (even -WindowStyle Hidden) lets wsl.exe take a console and Windows
  # Terminal draws a black window (HEARTBEAT_FLASH_FIX_BLACK_WINDOW_EVERY_TEN).
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = 'wsl.exe'
  $psi.Arguments = '-e sh -c "echo x > $HOME/.hb_probe && sync"'
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $p = [System.Diagnostics.Process]::Start($psi)
  if (-not $p.WaitForExit($ProbeSeconds * 1000)) {
    try { $p.Kill() } catch {}
    return "write probe hung > ${ProbeSeconds}s"
  }
  if ($p.ExitCode -ne 0) { return "write probe exit $($p.ExitCode)" }
  return $null
}

$state = @{}
if (Test-Path $stateFile) { try { (Get-Content $stateFile -Raw | ConvertFrom-Json).PSObject.Properties | ForEach-Object { $state[$_.Name] = $_.Value } } catch {} }
$paused = Test-Path (Join-Path $StateDir 'paused')

$causes = @{}   # key -> detail when red
try {
  $age = Get-CommitAgeMinutes
  if ($age -ge $StaleMinutes) { $causes['commits'] = "origin/main has had no commit for $age min (limit $StaleMinutes)" }
} catch { Log "commit check unreadable: $($_.Exception.Message)" }
try {
  $w = Test-WslWrite
  if ($w) { $causes['wsl'] = "WSL disk write: $w" }
} catch { $causes['wsl'] = "WSL probe error: $($_.Exception.Message)" }

foreach ($k in @('commits', 'wsl')) {
  if ($causes.ContainsKey($k)) {
    if ($paused) { Log "RED $k (paused, no alert): $($causes[$k])"; continue }
    $last = $state[$k]
    $due = (-not $last) -or (((Get-Date) - [datetime]$last).TotalMinutes -ge $RemindMinutes)
    if ($due) {
      Send-Phone "RimMandrake HEARTBEAT: $k is red" $causes[$k]
      $state[$k] = (Get-Date).ToString('s')
    } else { Log "RED $k (already alerted): $($causes[$k])" }
  } else {
    if ($state.ContainsKey($k)) { Log "GREEN $k (recovered)"; $state.Remove($k) }
  }
}
if ($causes.Count -eq 0) { Log "ok commits=${age}min wsl=ok" }
($state | ConvertTo-Json) | Set-Content -Path $stateFile
