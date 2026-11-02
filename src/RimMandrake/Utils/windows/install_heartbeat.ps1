# Installs the RimMandrake-Heartbeat scheduled task (every 10 min, runs whether or not WSL is up).
# Usage: powershell -File install_heartbeat.ps1 -Script <path to heartbeat.ps1> [-TokenFrom <file>]
param([Parameter(Mandatory)][string]$Script, [string]$StateDir = 'D:\ClaudeWork\heartbeat', [string]$TokenFrom)
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null
Copy-Item $Script (Join-Path $StateDir 'heartbeat.ps1') -Force   # run a copy so the task survives the repo path moving
if ($TokenFrom) { Copy-Item $TokenFrom (Join-Path $StateDir 'todoist_token') -Force }
$act = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$StateDir\heartbeat.ps1`""
$trg = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$set = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'RimMandrake-Heartbeat' -Action $act -Trigger $trg -Settings $set -Force | Out-Null
Get-ScheduledTask -TaskName 'RimMandrake-Heartbeat' | Select-Object TaskName, State | Format-Table -Auto
