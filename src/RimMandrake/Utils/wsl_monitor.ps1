<#
  wsl_monitor.ps1 - a small always-on-top live readout of WSL fleet memory.

  WHY IT LIVES ON WINDOWS
  -----------------------
  resource_watch.sh samples from inside the VM, which is right for FORENSICS -
  the last line it writes before the log stops is the evidence. It is the wrong
  place to WATCH from. On 2026-08-14 the VM spent 6m53s thrashing before the
  kill; a process inside it is competing for the memory that just ran out. This
  reads `vmmemWSL` from Windows, which stayed fully responsive throughout (the
  host had ~32 GB free the entire time), so the readout keeps updating exactly
  when it matters most.

  DESIGN CONSTRAINTS, from the owner
  ----------------------------------
  - No modal dialogs. Nothing that steals focus or has to be dismissed. The
    window changes colour and that is the whole notification.
  - Nothing to reload. It repaints itself on a timer; you glance at it.
  - Auto-restoring: it remembers where you put it, and the scheduled task brings
    it back after a logon or a crash.
  - The game runs windowed, so a normal always-on-top window is visible. That is
    why this replaces the msg.exe popup an earlier version used.

  CALIBRATION (measured 2026-08-14 on ARCHMAGI)
  ---------------------------------------------
    idle, 5 seats     ~4.6 GB     the fatal event   ~31 GB
    VM ceiling        31.7 GB, or 36 GB once .wslconfig applies
  One seat alone reached 27.4 GB. WARN 16 GB / CRIT 22 GB leaves real runway:
  the climb is slow, and restarting one tab at WARN costs a session instead of
  the fleet.

  USAGE
    powershell -ExecutionPolicy Bypass -File wsl_monitor.ps1
    ... -File wsl_monitor.ps1 -WarnGB 12 -CritGB 20 -NoGui     (headless, logs only)

  INSTALL so it returns by itself at every logon:
    schtasks /create /tn "WSL Monitor" /sc onlogon /rl highest /f ^
      /tr "powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File D:\Luke\dev\Rimworld\src\RimMandrake\Utils\wsl_monitor.ps1"
    schtasks /delete /tn "WSL Monitor" /f      (to remove)
#>

param(
  [double]$WarnGB      = 16,
  [double]$CritGB      = 22,
  [int]   $IntervalSec = 5,
  [switch]$NoGui,
  [switch]$NoBeep,
  [string]$StateDir    = "D:\Luke\dev\Rimworld\observed\resource_watch"
)

$ErrorActionPreference = 'Continue'
if (-not (Test-Path $StateDir)) { New-Item -ItemType Directory -Path $StateDir -Force | Out-Null }
$StatusFile = Join-Path $StateDir 'WATCHDOG_STATUS.txt'
$LogFile    = Join-Path $StateDir 'WATCHDOG_LOG.txt'
$PosFile    = Join-Path $StateDir 'monitor_pos.txt'

function Write-Log($level, $msg) {
  try { Add-Content -Path $LogFile -Value ("{0} {1} {2}" -f (Get-Date -Format o), $level, $msg) } catch { }
}

# Columns are resolved BY HEADER NAME, never by fixed index. Fixed indices were
# tried first and produced confident garbage ("seats=1.17MB swapfree=1932/3MB")
# the moment resource_watch.sh gained two swap columns - and worse, two sampler
# versions were briefly appending different layouts to the same file. A monitor
# that misreports without erroring is more dangerous than one that is absent, so
# this returns nothing rather than a number it cannot justify.
function Get-VmDetail {
  $out = [ordered]@{ Seats = $null; SwapFree = $null; SwapTotal = $null; Stale = $false }
  try {
    $csv = Get-ChildItem -Path $StateDir -Filter 'watch_*.csv' -ErrorAction Stop |
           Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if (-not $csv) { return $out }
    if (((Get-Date) - $csv.LastWriteTime).TotalSeconds -gt 120) { $out.Stale = $true; return $out }
    $lines  = Get-Content $csv.FullName -ErrorAction Stop
    $header = $lines | Where-Object { $_ -like 'ts,*' } | Select-Object -First 1
    $last   = $lines | Where-Object { $_ -match '^\d{4}-\d{2}-\d{2}T' } | Select-Object -Last 1
    if (-not $header -or -not $last) { return $out }
    $cols = $header -split ','; $vals = $last -split ','
    if ($vals.Count -ne $cols.Count) { return $out }   # mixed schema; say nothing
    $idx = @{}; for ($i = 0; $i -lt $cols.Count; $i++) { $idx[$cols[$i].Trim()] = $i }
    if ($idx.ContainsKey('wsl_claude_rss_mb')) { $out.Seats     = [int]$vals[$idx['wsl_claude_rss_mb']] }
    if ($idx.ContainsKey('wsl_swapfree_mb'))   { $out.SwapFree  = [int]$vals[$idx['wsl_swapfree_mb']] }
    if ($idx.ContainsKey('wsl_swaptotal_mb'))  { $out.SwapTotal = [int]$vals[$idx['wsl_swaptotal_mb']] }
  } catch { }
  return $out
}

function Get-Sample {
  $vm = Get-Process -Name 'vmmemWSL' -ErrorAction SilentlyContinue
  if (-not $vm) { return @{ Level = 'DOWN'; GB = 0; Detail = (Get-VmDetail) } }
  $gb = [math]::Round($vm.WorkingSet64 / 1GB, 2)
  $lv = if ($gb -ge $CritGB) { 'CRITICAL' } elseif ($gb -ge $WarnGB) { 'WARN' } else { 'OK' }
  return @{ Level = $lv; GB = $gb; Detail = (Get-VmDetail) }
}

# ---------------------------------------------------------------- headless ---
if ($NoGui) {
  $last = 'OK'
  while ($true) {
    $s = Get-Sample
    Set-Content -Path $StatusFile -Value ("{0}  vmmemWSL={1}GB  {2}" -f $s.Level, $s.GB, (Get-Date -Format 'HH:mm:ss'))
    if ($s.Level -ne $last) { Write-Log $s.Level ("vmmemWSL={0}GB" -f $s.GB) }
    $last = $s.Level
    Start-Sleep -Seconds $IntervalSec
  }
}

# -------------------------------------------------------------------- gui ----
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()

# 🔴 NOTHING HERE USES A HARDCODED PIXEL POSITION, deliberately. The first
# version laid labels out at fixed coordinates in a fixed 330x176 window; on a
# scaled display the font rendered larger than those boxes and the bottom line
# was clipped with "free" wrapped off the right edge. Font size in points is not
# a promise about pixels — DPI decides that, and DPI is not knowable here.
# So: AutoSize labels stacked in a FlowLayoutPanel, and a form that grows to fit
# whatever it is handed. Correct at 100%, 150%, 200% or a display we never saw.
$form                 = New-Object Windows.Forms.Form
$form.Text            = 'WSL fleet'
$form.TopMost         = $true                 # visible over a windowed RimWorld
$form.FormBorderStyle = 'FixedToolWindow'
$form.ShowInTaskbar   = $false
$form.BackColor       = [Drawing.Color]::FromArgb(12, 12, 12)
$form.AutoSize        = $true
$form.AutoSizeMode    = 'GrowAndShrink'
$form.Padding         = New-Object Windows.Forms.Padding(10, 6, 10, 8)

$panel               = New-Object Windows.Forms.FlowLayoutPanel
$panel.FlowDirection = 'TopDown'
$panel.AutoSize      = $true
$panel.AutoSizeMode  = 'GrowAndShrink'
$panel.WrapContents  = $false                 # never reflow into columns
$panel.Dock          = 'Fill'
$form.Controls.Add($panel)

function NewLabel($size, $bold) {
  $l           = New-Object Windows.Forms.Label
  $l.AutoSize  = $true                        # the label decides its own width
  $l.Font      = New-Object Drawing.Font('Consolas', $size, $(if ($bold) { [Drawing.FontStyle]::Bold } else { [Drawing.FontStyle]::Regular }))
  $l.ForeColor = [Drawing.Color]::Gainsboro
  $l.BackColor = [Drawing.Color]::Transparent
  $l.Margin    = New-Object Windows.Forms.Padding(0, 1, 0, 1)
  $panel.Controls.Add($l); return $l
}

# Every line states its own meaning. An earlier version rendered
# "VM OK  warn 16  crit 22 GB", which is unreadable unless you wrote it.
$lblBig  = NewLabel 20 $true     # the number
$lblCap  = NewLabel  8 $false    # what the number IS
$lblBar  = NewLabel  7 $false    # progress toward the red line
$lblSub  = NewLabel 10 $false    # plain-English verdict
$lblSub2 = NewLabel  8 $false    # thresholds
$lblSub3 = NewLabel  8 $false    # inside-the-VM detail
$lblFoot = NewLabel  7 $false    # freshness

# Restore last position; otherwise top-right of the primary screen. Done AFTER
# layout so the width used to offset from the right edge is the real one.
$form.Add_Shown({
  $pos = $null
  if (Test-Path $PosFile) {
    try { $q = (Get-Content $PosFile -Raw) -split ','; $pos = New-Object Drawing.Point([int]$q[0], [int]$q[1]) } catch { }
  }
  if ($pos) { $form.Location = $pos }
  else {
    $wa = [Windows.Forms.Screen]::PrimaryScreen.WorkingArea
    $form.Location = New-Object Drawing.Point(($wa.Right - $form.Width - 12), ($wa.Top + 12))
  }
})
$form.StartPosition = 'Manual'

# Drag from anywhere on the panel - a tool window's thin frame is fiddly to grab.
$script:drag = $false
$down = { $script:drag = $true; $script:dragOrigin = [Windows.Forms.Cursor]::Position; $script:formOrigin = $form.Location }
$move = {
  if ($script:drag) {
    $c = [Windows.Forms.Cursor]::Position
    $form.Location = New-Object Drawing.Point(
      ($script:formOrigin.X + $c.X - $script:dragOrigin.X),
      ($script:formOrigin.Y + $c.Y - $script:dragOrigin.Y))
  }
}
$up = { $script:drag = $false; try { Set-Content -Path $PosFile -Value ("{0},{1}" -f $form.Location.X, $form.Location.Y) } catch { } }
foreach ($c in @($form, $panel, $lblBig, $lblCap, $lblBar, $lblSub, $lblSub2, $lblSub3, $lblFoot)) {
  $c.Add_MouseDown($down); $c.Add_MouseMove($move); $c.Add_MouseUp($up)
}

$script:lastLevel = 'OK'
$timer          = New-Object Windows.Forms.Timer
$timer.Interval = $IntervalSec * 1000

$timer.Add_Tick({
  # Wrapped throughout: a transient WMI or file hiccup must never take the window
  # down, because a monitor that quietly vanished reads exactly like one saying
  # "fine". On error the footer says so and the next tick tries again.
  try {
    $s = Get-Sample; $d = $s.Detail; $lvl = $s.Level

    $col = switch ($lvl) {
      'CRITICAL' { [Drawing.Color]::FromArgb(255,  80,  80) }
      'WARN'     { [Drawing.Color]::FromArgb(255, 190,  60) }
      'DOWN'     { [Drawing.Color]::FromArgb(140, 140, 140) }
      default    { [Drawing.Color]::FromArgb(110, 220, 130) }
    }

    if ($lvl -eq 'DOWN') {
      $lblBig.Text  = 'WSL is down'
      $lblCap.Text  = 'no virtual machine running'
      $lblBar.Text  = ''
      $lblSub.Text  = 'nothing to watch'
      $lblSub2.Text = ''
    } else {
      $lblBig.Text  = ("{0:N1} GB" -f $s.GB)
      $lblCap.Text  = 'used by the whole WSL VM, all seats together'
      $pct = [math]::Min(100, [int](100 * $s.GB / $CritGB))
      $lblBar.Text  = ('|' * [int]($pct / 4)).PadRight(25, [char]0x00B7)
      $lblSub.Text  = switch ($lvl) {
        'CRITICAL' { 'CRITICAL - restart the biggest seat now' }
        'WARN'     { 'climbing - restart a seat while it is cheap' }
        default    { 'healthy' }
      }
      $lblSub2.Text = ("amber at {0} GB, red at {1} GB" -f $WarnGB, $CritGB)
    }
    $lblBig.ForeColor = $col; $lblBar.ForeColor = $col; $lblSub.ForeColor = $col

    # Two short lines rather than one long one - a single line is what ran off
    # the edge before, and short lines survive a wider font too.
    if ($d.Stale) { $lblSub3.Text = 'in-VM detail stale >2min' }
    elseif ($null -ne $d.Seats) {
      $sw = if ($d.SwapTotal) { "{0:N1}/{1:N1} GB" -f ($d.SwapFree/1024), ($d.SwapTotal/1024) } else { 'n/a' }
      $lblSub3.Text = ("seats {0:N1} GB   swap free {1}" -f ($d.Seats/1024), $sw)
    } else { $lblSub3.Text = 'per-seat detail unavailable' }

    $lblFoot.Text = ("updated {0}  -  drag to move" -f (Get-Date -Format 'HH:mm:ss'))

    Set-Content -Path $StatusFile -Value ("{0}  vmmemWSL={1}GB  {2}" -f $lvl, $s.GB, (Get-Date -Format 'HH:mm:ss'))

    if ($lvl -ne $script:lastLevel) {
      Write-Log $lvl ("vmmemWSL={0}GB seats={1}MB" -f $s.GB, $d.Seats)
      # Sound only on the way INTO trouble, and never a dialog. Colour is the
      # notification; this is in case you are looking elsewhere.
      if (-not $NoBeep -and $lvl -eq 'CRITICAL') { try { 880,1046,1318 | ForEach-Object { [console]::beep($_, 200) } } catch { } }
      elseif (-not $NoBeep -and $lvl -eq 'WARN')  { try { [console]::beep(660, 150) } catch { } }
    }
    $script:lastLevel = $lvl
  } catch {
    try { $lblFoot.Text = 'sample error - still running' } catch { }
  }
})

$form.Add_FormClosing({ try { Set-Content -Path $PosFile -Value ("{0},{1}" -f $form.Location.X, $form.Location.Y) } catch { } })
Write-Log 'START' ("monitor up: warn={0}GB crit={1}GB every {2}s" -f $WarnGB, $CritGB, $IntervalSec)
$timer.Start()
[Windows.Forms.Application]::Run($form)
