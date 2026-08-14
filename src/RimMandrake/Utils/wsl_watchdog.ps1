<#
  wsl_watchdog.ps1 - Windows-side early warning for the WSL memory runaway.

  WHY THIS RUNS ON WINDOWS AND NOT IN WSL
  ---------------------------------------
  resource_watch.sh already samples from inside the VM, and that is the right
  place for FORENSICS - the last line it writes before the log stops is the
  measurement. It is the wrong place for an ALARM. On 2026-08-14 the VM spent
  6m53s thrashing (32 page-allocation failures, swap 8.0 GB -> 0 in 1m55s)
  before the kill. A bash loop inside that VM is competing for the memory that
  has just run out, and it dies with the VM it was meant to warn about.

  Windows stays fully responsive throughout - the host had ~32 GB free the whole
  time. So the alarm samples `vmmemWSL`, the Windows-visible working set of the
  entire WSL2 VM. One number, no dependency on the failing side.

  WHY IT BEEPS
  ------------
  Nothing visual survives a fullscreen RimWorld - toasts, tray icons and pinned
  terminals are all covered. Audio is the only channel that reaches the desk
  while the game is up, which is exactly when the fleet is busiest and this
  fires. The beep is deliberately annoying and deliberately escalating.

  CALIBRATION (measured 2026-08-14 on ARCHMAGI)
  ---------------------------------------------
    idle, 5 seats            ~4.6 GB     vmmemWSL
    the fatal event          ~31 GB      (one seat alone held 27.4 GB)
    VM ceiling               31.7 GB now, 36 GB once .wslconfig applies
  WARN at 16 GB is ~3.5x idle and roughly half the ceiling - far enough out that
  /compact or restarting one tab still saves the session. CRITICAL at 22 GB is
  the point where the climb has never once turned around on its own.

  USAGE
    powershell -ExecutionPolicy Bypass -File wsl_watchdog.ps1
    powershell ... -File wsl_watchdog.ps1 -WarnGB 12 -CritGB 20 -IntervalSec 10

  INSTALL AS A LOGON TASK (survives reboots; runs hidden)
    schtasks /create /tn "WSL Watchdog" /sc onlogon /rl highest /f ^
      /tr "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File D:\Luke\dev\Rimworld\src\RimMandrake\Utils\wsl_watchdog.ps1"
  Remove with:  schtasks /delete /tn "WSL Watchdog" /f
#>

param(
  [double]$WarnGB      = 16,
  [double]$CritGB      = 22,
  [int]   $IntervalSec = 15,
  [string]$StatusFile  = "D:\Luke\dev\Rimworld\observed\resource_watch\WATCHDOG_STATUS.txt",
  [string]$LogFile     = "D:\Luke\dev\Rimworld\observed\resource_watch\WATCHDOG_LOG.txt",
  # The in-VM sampler's CSV. Used only to name WHICH seat is growing - the alarm
  # itself never depends on it, because the VM may be too sick to keep writing.
  [string]$WslCsvDir   = "D:\Luke\dev\Rimworld\observed\resource_watch"
)

$ErrorActionPreference = 'Continue'
foreach ($f in @($StatusFile, $LogFile)) {
  $d = Split-Path $f -Parent
  if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
}

function Write-Log($level, $msg) {
  $line = "{0} {1} {2}" -f (Get-Date -Format o), $level, $msg
  Add-Content -Path $LogFile -Value $line
  Write-Host $line
}

# Escalating, and audible over a game. Three rising tones for CRITICAL so it is
# distinguishable from any sound RimWorld itself makes.
function Alarm($level) {
  try {
    if ($level -eq 'CRITICAL') { 880,1046,1318 | ForEach-Object { [console]::beep($_, 220) } }
    else                       { [console]::beep(660, 160) }
  } catch { }   # no audio device (headless / RDP) must not kill the watchdog
}

function Toast($title, $msg) {
  # msg.exe is present on this box; BurntToast is not installed. This is crude
  # but needs no module and no install. It is the SECOND channel - the beep is
  # the one that actually reaches a player.
  try { & "$env:SystemRoot\System32\msg.exe" $env:USERNAME /TIME:60 "$title - $msg" 2>$null } catch { }
}

# Reads the in-VM sampler's newest CSV to name the growing seat. Best-effort:
# a stale or missing file is normal and must never stop the alarm.
#
# 🔴 Columns are resolved BY HEADER NAME, never by fixed index. Fixed indices
# were tried first and produced silent garbage ("seats=1.17MB swapfree=1932/3MB")
# the moment resource_watch.sh gained two swap columns - and worse, two sampler
# versions were briefly appending different layouts to the SAME file. A monitor
# that misreports without erroring is more dangerous than one that is simply
# absent, so this returns $null rather than a number it cannot justify.
function Get-SeatDetail {
  try {
    $csv = Get-ChildItem -Path $WslCsvDir -Filter 'watch_*.csv' -ErrorAction Stop |
           Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $csv) { return $null }
    if (((Get-Date) - $csv.LastWriteTime).TotalSeconds -gt 120) {
      return 'in-VM sampler stale (>2 min) - the VM may already be thrashing'
    }

    $lines  = Get-Content $csv.FullName
    $header = $lines | Where-Object { $_ -like 'ts,*' } | Select-Object -First 1
    $last   = $lines | Where-Object { $_ -match '^\d{4}-\d{2}-\d{2}T' } | Select-Object -Last 1
    if (-not $header -or -not $last) { return $null }

    $cols = $header -split ','
    $vals = $last   -split ','
    # A row that does not match its own header means mixed schemas in one file.
    # Say so instead of indexing into it.
    if ($vals.Count -ne $cols.Count) { return 'sampler CSV schema mismatch - ignoring detail' }

    $idx = @{}
    for ($i = 0; $i -lt $cols.Count; $i++) { $idx[$cols[$i].Trim()] = $i }
    foreach ($need in 'wsl_claude_rss_mb','wsl_swapfree_mb','wsl_swaptotal_mb') {
      if (-not $idx.ContainsKey($need)) { return $null }
    }
    return ("seats={0}MB swap={1}/{2}MB" -f `
      $vals[$idx['wsl_claude_rss_mb']], $vals[$idx['wsl_swapfree_mb']], $vals[$idx['wsl_swaptotal_mb']])
  } catch { }
  return $null
}

Write-Log 'START' ("watchdog up: warn={0}GB crit={1}GB every {2}s" -f $WarnGB, $CritGB, $IntervalSec)
$lastLevel = 'OK'
$critSince = $null

while ($true) {
  $vm = Get-Process -Name 'vmmemWSL' -ErrorAction SilentlyContinue
  if (-not $vm) {
    # No VM at all. Either WSL is not running, or it just died - both worth
    # saying out loud, because "the alarm went quiet" must never read as "fine".
    if ($lastLevel -ne 'DOWN') { Write-Log 'DOWN' 'vmmemWSL not present - WSL is stopped or has died'; $lastLevel = 'DOWN' }
    Set-Content -Path $StatusFile -Value "DOWN  WSL not running  $(Get-Date -Format 'HH:mm:ss')"
    Start-Sleep -Seconds $IntervalSec
    continue
  }

  $gb     = [math]::Round($vm.WorkingSet64 / 1GB, 2)
  $detail = Get-SeatDetail
  $level  = if ($gb -ge $CritGB) { 'CRITICAL' } elseif ($gb -ge $WarnGB) { 'WARN' } else { 'OK' }

  Set-Content -Path $StatusFile -Value ("{0}  vmmemWSL={1}GB  {2}  {3}" -f $level, $gb, $detail, (Get-Date -Format 'HH:mm:ss'))

  if ($level -eq 'CRITICAL') {
    if (-not $critSince) { $critSince = Get-Date }
    Write-Log 'CRITICAL' ("vmmemWSL={0}GB {1} - restart the largest seat NOW, or run 'wsl --shutdown' before it kills every seat" -f $gb, $detail)
    Alarm 'CRITICAL'
    # Re-alarm every cycle while critical. This is the state where the VM has
    # historically had only minutes left; a one-shot notification is useless if
    # the user stepped away.
    if ($lastLevel -ne 'CRITICAL') { Toast 'WSL CRITICAL' ("vmmemWSL at {0}GB - fleet about to OOM" -f $gb) }
  }
  elseif ($level -eq 'WARN') {
    $critSince = $null
    if ($lastLevel -ne 'WARN') {
      Write-Log 'WARN' ("vmmemWSL={0}GB {1} - a seat is climbing; /compact or restart it while that is still cheap" -f $gb, $detail)
      Alarm 'WARN'
      Toast 'WSL memory climbing' ("vmmemWSL at {0}GB" -f $gb)
    }
  }
  else {
    $critSince = $null
    if ($lastLevel -ne 'OK') { Write-Log 'RECOVERED' ("vmmemWSL back to {0}GB" -f $gb) }
  }

  $lastLevel = $level
  Start-Sleep -Seconds $IntervalSec
}
