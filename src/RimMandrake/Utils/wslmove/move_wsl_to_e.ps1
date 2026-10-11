<#
move_wsl_to_e.ps1 -- move the Ubuntu WSL2 distro from C: to E:\WSL\Ubuntu, make it sparse,
with a full tar backup on F:\WSLBackup first. Weekly cleaning 2026-10-11, item 18.

Run DETACHED from Windows (one-shot scheduled task, see launch_move.ps1), never as a child of a
WSL session: step 3 runs `wsl --shutdown`, which would take an interop-spawned parent with it.

Order (safest first, each step checked; any failure STOPS and deletes nothing):
  0  pre-flight: WSL version, --move/--set-sparse present, distro registered, vhdx path, ext4 used
     bytes (measured live, before shutdown), free space on F: and E:, target empty
  1  disable every Windows task that can start WSL: \WSL Keepalive; and \RimFlow Pulse (its
     lantern widget runs `wsl.exe ... systemctl --user start rm-pulse` when the spine is down)
  2  stop the lantern process (it is what actually calls wsl.exe)
  3  wsl --shutdown; verify Ubuntu Stopped and no wsl/wslhost/vmmem process for the distro
  4  wsl --export Ubuntu F:\WSLBackup\Ubuntu_<stamp>.tar ; verify size is 0.80-1.30 x ext4-used
     and the archive ends in tar's zero end-of-archive blocks
  5  hard-link the C: vhdx to C:\...\wsl\pre_move_keep\ext4.vhdx (instant, same volume) so the
     old image SURVIVES the move even though --move removes its own source name
  6  wsl --manage Ubuntu --move E:\WSL\Ubuntu ; verify Lxss BasePath, file on E:, length
     (fallback only if --move is absent from this WSL build: import the tar as "Ubuntu" after
     RENAMING the old registration to Ubuntu-old-C -- never unregister)
  7  wsl --manage Ubuntu --set-sparse true ; refusal is logged, never forced (--allow-unsafe)
  8  boot + verify: echo ok as mandrake, default user is mandrake, /etc/wsl.conf [user]
  9  fstrim / as root so the now-sparse vhdx releases the ~400 GB Linux already freed
 10  re-enable + start \WSL Keepalive (its session keeps the user systemd manager up), verify
     user units, re-enable + start \RimFlow Pulse, optionally relaunch the seat fleet
 11  report: old-image paths for the owner to delete later, sizes, timings
#>
[CmdletBinding()]
param(
    [switch]$WhatIf,                       # dry run: probes + log what would run, change nothing
    [string]$Distro    = "Ubuntu",
    [string]$Target    = "E:\WSL\Ubuntu",
    [string]$BackupDir = "F:\WSLBackup",
    [string]$LogPath   = "D:\Luke\dev\_rmscratch\wslmove\move.log",
    [int]$DelaySec     = 0,                # grace period so the launching agent can finish
    [switch]$SkipBackup,                   # NOT recommended; only if a verified tar already exists
    [switch]$RelaunchFleet,                # run the logon "Start Agent Fleet" launcher at the end
    [string]$SelfTaskName = ""             # name of the trigger-less task that launched us (logged only;
                                           # unregistering a running task kills it, so it is left inert)
)

$ErrorActionPreference = "Stop"
$env:WSL_UTF8 = "1"                        # wsl.exe prints UTF-16 otherwise
$Stamp   = Get-Date -Format "yyyy-MM-dd_HHmm"
$T0      = Get-Date
$UserUnits = @("rm-artpiped.service","rm-pulse.service","hestia.service",
               "rm-memwatch.timer","rm-mirror.timer","rm-objstore.timer","rm-codebase-health.timer",
               "rm-pulse-digest.timer","rm-pulse-health.timer")
$SysUnits  = @("tailscaled.service","lodestar-sync.timer")
$WslTasks  = @("\WSL Keepalive","\RimFlow Pulse")
$FleetLnkArgs = '-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\launch_fleet.ps1"'
$script:State = @{ TasksDisabled = $false; ShutDown = $false; Moved = $false }

New-Item -ItemType Directory -Force -Path (Split-Path $LogPath) | Out-Null
try { Start-Transcript -Path ($LogPath -replace '\.log$','.transcript.log') -Append | Out-Null } catch {}
function Log([string]$m) {
    $line = "{0}  {1}{2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), ($(if ($WhatIf) {"[WHATIF] "} else {""})), $m
    Add-Content -Path $LogPath -Value $line -Encoding UTF8
    Write-Host $line
}
function Wsl([string[]]$a) {           # run wsl.exe, log output, return @{code;out}
    $ErrorActionPreference = "Continue"   # PS 5.1 turns native stderr into a terminating error under Stop
    $out = (& wsl.exe @a 2>&1 | Out-String).Replace("`0","").Trim()
    $code = $LASTEXITCODE
    Log ("  wsl {0} -> exit {1}{2}" -f ($a -join " "), $code, $(if ($out) {"`n      " + ($out -replace "`r?`n","`n      ")} else {""}))
    return @{ code = $code; out = $out }
}
function Do-Step([string]$desc, [scriptblock]$act) {   # mutating action: skipped under -WhatIf
    if ($WhatIf) { Log "WOULD: $desc"; return $null }
    Log "DO: $desc"
    return & $act
}
function Lxss { Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss |
    ForEach-Object { Get-ItemProperty $_.PSPath } | Where-Object { $_.DistributionName -eq $Distro } }
function DistroState {
    $ErrorActionPreference = "Continue"
    $r = (& wsl.exe -l -v 2>&1 | Out-String).Replace("`0","")
    foreach ($l in $r -split "`r?`n") { if ($l -match "^\s*\*?\s*$([regex]::Escape($Distro))\s+(\S+)") { return $Matches[1] } }
    return "Absent"
}
function Restore-Services([string]$why) {
    # Bring WSL + tasks back ONLY when the registered distro points at an image that exists.
    $k = Lxss
    if (-not $k) { Log "NOT restoring services: $Distro is not registered ($why)"; return }
    $img = Join-Path $k.BasePath $k.VhdFileName
    if (-not (Test-Path -LiteralPath $img)) { Log "NOT restoring services: registered image $img is missing ($why)"; return }
    foreach ($t in $WslTasks) {
        $p = Split-Path $t -Parent; $n = Split-Path $t -Leaf; if ($p -notmatch '\\$') { $p += '\' }
        Do-Step "Enable-ScheduledTask $t" { Enable-ScheduledTask -TaskPath $p -TaskName $n | Out-Null } | Out-Null
        Do-Step "Start-ScheduledTask $t"  { Start-ScheduledTask  -TaskPath $p -TaskName $n } | Out-Null
    }
}
function Stop-Run([string]$why) {
    Log "STOP: $why"
    Log "STOP: nothing was deleted. Lxss now: $((Lxss | ForEach-Object { $_.BasePath }) -join ', ')"
    if ($script:State.TasksDisabled -and -not $WhatIf) { Restore-Services $why }
    Log "STOP: total elapsed $([int]((Get-Date) - $T0).TotalMinutes) min. Read $LogPath."
    exit 1
}
function Stamp([string]$name, [datetime]$from) { Log ("TIME {0}: {1:N1} min" -f $name, ((Get-Date) - $from).TotalMinutes) }

trap { Stop-Run ("unhandled error: " + $_.Exception.Message + " at line " + $_.InvocationInfo.ScriptLineNumber) }

Log "==== move_wsl_to_e.ps1 start (task '$SelfTaskName', stamp $Stamp, WhatIf=$WhatIf, pid $PID, user $env:USERNAME, elevated=$(([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)))"
if ($DelaySec -gt 0) { Log "grace delay $DelaySec s"; Start-Sleep -Seconds $DelaySec }

# ---------------------------------------------------------------- 0 pre-flight
$s = Get-Date
$v = Wsl @("--version")
if ($v.code -ne 0) { Stop-Run "wsl --version failed" }
$ErrorActionPreference = "Continue"; $help = (& wsl.exe --help 2>&1 | Out-String).Replace("`0","")
$ErrorActionPreference = "Stop"
$HasMove   = $help -match "--move"
$HasSparse = $help -match "--set-sparse"
Log "capabilities: --move=$HasMove --set-sparse=$HasSparse"

$k = Lxss
if (-not $k) { Stop-Run "$Distro is not registered" }
$OldDir  = $k.BasePath -replace '^\\\\\?\\',''
$OldVhdx = Join-Path $OldDir $k.VhdFileName
if (-not (Test-Path -LiteralPath $OldVhdx)) { Stop-Run "vhdx not found at $OldVhdx" }
$OldLen = (Get-Item -LiteralPath $OldVhdx).Length
Log ("source: {0}  ({1:N1} GB, DefaultUid {2}, sparse: {3})" -f $OldVhdx, ($OldLen/1GB), $k.DefaultUid, ((fsutil sparse queryflag $OldVhdx) -join ' '))
if ($OldDir.TrimEnd('\') -ieq $Target.TrimEnd('\')) { Stop-Run "distro is already at $Target -- nothing to do" }

$st0 = DistroState
Log "distro state: $st0"
$UsedBytes = 0
if ($st0 -eq "Running") {
    $r = Wsl @("-d",$Distro,"-u","root","--","df","-B1","--output=used","/")
    if ($r.code -eq 0) { $UsedBytes = [int64](($r.out -split "`n")[-1].Trim()) }
}
if ($UsedBytes -le 0) { Stop-Run "could not measure ext4 used bytes (distro must be Running at start so df can read it)" }
Log ("ext4 used: {0:N1} GB" -f ($UsedBytes/1GB))

$fF = (Get-Volume -DriveLetter $BackupDir.Substring(0,1)).SizeRemaining
$fE = (Get-Volume -DriveLetter $Target.Substring(0,1)).SizeRemaining
Log ("free: {0} {1:N0} GB (need {2:N0}), {3} {4:N0} GB (need {5:N0})" -f $BackupDir.Substring(0,2), ($fF/1GB), ($UsedBytes*1.3/1GB+50), $Target.Substring(0,2), ($fE/1GB), ($OldLen/1GB+50))
if (-not $SkipBackup -and $fF -lt ($UsedBytes*1.3 + 50GB)) { Stop-Run "not enough free space for the backup tar" }
if ($fE -lt ($OldLen + 50GB)) { Stop-Run "not enough free space on the target volume for the vhdx" }
if ((Test-Path -LiteralPath $Target) -and (Get-ChildItem -LiteralPath $Target -Force | Measure-Object).Count -gt 0) { Stop-Run "$Target exists and is not empty" }
foreach ($t in $WslTasks) {
    $x = Get-ScheduledTask -TaskPath ((Split-Path $t -Parent).TrimEnd('\') + '\') -TaskName (Split-Path $t -Leaf) -ErrorAction SilentlyContinue
    Log ("task {0}: {1}" -f $t, $(if ($x) { $x.State } else { "absent" }))
}
Stamp "preflight" $s

# ---------------------------------------------------------------- 1-2 stop every WSL starter
foreach ($t in $WslTasks) {
    $p = (Split-Path $t -Parent).TrimEnd('\') + '\'; $n = Split-Path $t -Leaf
    if (Get-ScheduledTask -TaskPath $p -TaskName $n -ErrorAction SilentlyContinue) {
        Do-Step "Disable-ScheduledTask $t (and end its running instance)" {
            Stop-ScheduledTask -TaskPath $p -TaskName $n -ErrorAction SilentlyContinue
            Disable-ScheduledTask -TaskPath $p -TaskName $n | Out-Null
            if ((Get-ScheduledTask -TaskPath $p -TaskName $n).State -ne "Disabled") { Stop-Run "could not disable $t" }
        } | Out-Null
    }
}
$script:State.TasksDisabled = $true
$lant = Get-CimInstance Win32_Process | Where-Object { $_.Name -like "python*" -and $_.CommandLine -match 'lantern\.pyw' }   # real name is pythonw3.13.exe
foreach ($p in $lant) { Do-Step "stop lantern widget pid $($p.ProcessId)" { Stop-Process -Id $p.ProcessId -Force } | Out-Null }
if (-not $lant) { Log "lantern widget not running" }

# ---------------------------------------------------------------- 3 shutdown
$s = Get-Date
Do-Step "wsl --shutdown" {
    $r = Wsl @("--shutdown"); if ($r.code -ne 0) { Stop-Run "wsl --shutdown failed" }
    Start-Sleep -Seconds 10
    $st = DistroState
    if ($st -ne "Stopped") { Stop-Run "after shutdown $Distro is '$st' -- something restarted it" }
    $left = Get-Process -Name wsl,wslhost,wslrelay -ErrorAction SilentlyContinue
    if ($left) { Log ("note: Windows-side wsl processes still listed: " + (($left | ForEach-Object { "$($_.Name)/$($_.Id)" }) -join ' ')) ; Start-Sleep 15
        $left = Get-Process -Name wsl,wslhost,wslrelay -ErrorAction SilentlyContinue
        if ($left) { Stop-Run ("wsl processes survive shutdown: " + (($left | ForEach-Object { "$($_.Name)/$($_.Id)" }) -join ' ')) } }
    $script:State.ShutDown = $true
} | Out-Null
Stamp "shutdown" $s

# ---------------------------------------------------------------- 4 backup tar on F:
$Tar = Join-Path $BackupDir "$($Distro)_$Stamp.tar"
if ($SkipBackup) { Log "backup SKIPPED by -SkipBackup" } else {
    $s = Get-Date
    Do-Step "wsl --export $Distro $Tar" {
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        $r = Wsl @("--export",$Distro,$Tar)
        if ($r.code -ne 0) { Stop-Run "export failed (exit $($r.code))" }
        if (-not (Test-Path -LiteralPath $Tar)) { Stop-Run "export reported success but $Tar does not exist" }
        $tl = (Get-Item -LiteralPath $Tar).Length
        $ratio = $tl / $UsedBytes
        Log ("tar: {0:N1} GB = {1:N2} x ext4-used" -f ($tl/1GB), $ratio)
        if ($ratio -lt 0.80 -or $ratio -gt 1.30) { Stop-Run ("tar size ratio {0:N2} outside 0.80-1.30 -- not trusting it" -f $ratio) }
        $fs = [IO.File]::OpenRead($Tar); $buf = New-Object byte[] 1024
        [void]$fs.Seek(-1024, [IO.SeekOrigin]::End); [void]$fs.Read($buf,0,1024); $fs.Close()
        if (($buf | Where-Object { $_ -ne 0 }).Count -ne 0) { Stop-Run "tar does not end in zero end-of-archive blocks -- truncated?" }
        Log "tar verified: size ratio sane, end-of-archive present"
        $st = DistroState
        if ($st -ne "Stopped") { Wsl @("--shutdown") | Out-Null; Start-Sleep 10; if ((DistroState) -ne "Stopped") { Stop-Run "distro not Stopped after export" } }
    } | Out-Null
    Stamp "export" $s
}

# ---------------------------------------------------------------- 5 keep the old image
$KeepDir  = Join-Path (Split-Path $OldDir -Parent) "pre_move_keep_$Stamp"
$KeepLink = Join-Path $KeepDir $k.VhdFileName
Do-Step "hard-link $OldVhdx -> $KeepLink (old image survives the move; owner deletes later)" {
    New-Item -ItemType Directory -Force -Path $KeepDir | Out-Null
    New-Item -ItemType HardLink -Path $KeepLink -Target $OldVhdx | Out-Null
    # compare against the image NOW, not $OldLen: that was read while the distro ran, and the
    # vhdx changes length across shutdown + export (false STOP, 2026-10-11 11:33)
    $nowLen  = (Get-Item -LiteralPath $OldVhdx).Length
    $linkLen = (Get-Item -LiteralPath $KeepLink).Length
    if ($linkLen -ne $nowLen) { Stop-Run "hard link has the wrong length ($linkLen vs $nowLen)" }
    if ($nowLen -ne $OldLen) { Log ("  note: image length changed since preflight: {0} -> {1}" -f $OldLen, $nowLen) }
    $script:OldLen = $nowLen
} | Out-Null

# ---------------------------------------------------------------- 6 move
$s = Get-Date
if ($HasMove) {
    Do-Step "wsl --manage $Distro --move $Target" {
        New-Item -ItemType Directory -Force -Path (Split-Path $Target -Parent) | Out-Null
        $r = Wsl @("--manage",$Distro,"--move",$Target)
        if ($r.code -ne 0) { Stop-Run "--move failed (exit $($r.code)); old image intact at $OldVhdx and $KeepLink" }
        $script:State.Moved = $true
    } | Out-Null
} else {
    if ($SkipBackup) { Stop-Run "--move unsupported and no backup taken this run -- refusing the import path" }
    Do-Step "FALLBACK: rename registration $Distro -> $Distro-old-C (keeps its image), import $Tar as $Distro at $Target" {
        $key = (Get-ChildItem HKCU:\Software\Microsoft\Windows\CurrentVersion\Lxss | Where-Object { (Get-ItemProperty $_.PSPath).DistributionName -eq $Distro }).PSPath
        Set-ItemProperty -Path $key -Name DistributionName -Value "$Distro-old-C"
        New-Item -ItemType Directory -Force -Path $Target | Out-Null
        $r = Wsl @("--import",$Distro,$Target,$Tar,"--version","2")
        if ($r.code -ne 0) { Set-ItemProperty -Path $key -Name DistributionName -Value $Distro; Stop-Run "import failed; old registration renamed back" }
        Wsl @("--set-default",$Distro) | Out-Null
        Wsl @("--manage",$Distro,"--set-default-user","mandrake") | Out-Null
        $script:State.Moved = $true
    } | Out-Null
}
if (-not $WhatIf) {
    $k2 = Lxss; $NewDir = $k2.BasePath -replace '^\\\\\?\\',''; $NewVhdx = Join-Path $NewDir $k2.VhdFileName
    Log "Lxss BasePath now: $NewDir"
    if ($NewDir.TrimEnd('\') -ine $Target.TrimEnd('\')) { Stop-Run "BasePath is $NewDir, expected $Target" }
    if (-not (Test-Path -LiteralPath $NewVhdx)) { Stop-Run "no image at $NewVhdx" }
    Log ("new image {0:N1} GB at {1}" -f ((Get-Item -LiteralPath $NewVhdx).Length/1GB), $NewVhdx)
}
Stamp "move" $s

# ---------------------------------------------------------------- 7 sparse
if ($HasSparse) {
    Do-Step "wsl --manage $Distro --set-sparse true (never --allow-unsafe)" {
        $r = Wsl @("--manage",$Distro,"--set-sparse","true")
        if ($r.code -ne 0 -or $r.out -match "unsafe|corrupt") { Log "set-sparse REFUSED or warned -- not forced; continuing (compact on a schedule instead)" }
        Log ("sparse flag: " + ((fsutil sparse queryflag $NewVhdx) -join ' '))
    } | Out-Null
} else { Log "--set-sparse not available in this build; skipped" }

# ---------------------------------------------------------------- 8 boot + identity
Do-Step "boot $Distro and verify identity" {
    $r = Wsl @("-d",$Distro,"-u","mandrake","--","echo","ok")
    if ($r.code -ne 0 -or $r.out -notmatch "(^|\n)ok$") { Stop-Run "distro does not boot cleanly as mandrake" }
    $r = Wsl @("-d",$Distro,"--","whoami")
    if ($r.out.Trim() -ne "mandrake") {
        Log "default user is '$($r.out.Trim())' -- setting mandrake"
        Wsl @("--manage",$Distro,"--set-default-user","mandrake") | Out-Null
        $r = Wsl @("-d",$Distro,"--","whoami"); if ($r.out.Trim() -ne "mandrake") { Stop-Run "default user still not mandrake" }
    }
    $r = Wsl @("-d",$Distro,"-u","root","--","cat","/etc/wsl.conf")
    Wsl @("-d",$Distro,"--","df","-h","/") | Out-Null
    if ($r.out -notmatch "default\s*=\s*mandrake") { Log "WARN: /etc/wsl.conf has no [user] default=mandrake (DefaultUid in Lxss still governs)" }
} | Out-Null

# ---------------------------------------------------------------- 9 release freed blocks
$s = Get-Date
Do-Step "fstrim -v / (sparse image hands freed blocks back to E:)" {
    $before = (Get-Volume -DriveLetter $Target.Substring(0,1)).SizeRemaining
    Wsl @("-d",$Distro,"-u","root","--","fstrim","-v","/") | Out-Null
    Start-Sleep 5
    $after = (Get-Volume -DriveLetter $Target.Substring(0,1)).SizeRemaining
    Log ("{0} free: {1:N0} GB -> {2:N0} GB" -f $Target.Substring(0,2), ($before/1GB), ($after/1GB))
} | Out-Null
Stamp "fstrim" $s

# ---------------------------------------------------------------- 10 services back
Restore-Services "normal completion"
Do-Step "verify units (after 20 s for the keepalive session)" {
    Start-Sleep 20
    $r = Wsl (@("-d",$Distro,"-u","mandrake","--","env","XDG_RUNTIME_DIR=/run/user/1000","systemctl","--user","is-active") + $UserUnits)
    if ($r.out -match "inactive|failed|unknown") { Log "WARN: a user unit is not active (lines above are in unit order: $($UserUnits -join ' '))" }
    $r = Wsl (@("-d",$Distro,"-u","root","--","systemctl","is-active") + $SysUnits)
    if ($r.out -match "inactive|failed|unknown") { Log "WARN: a system unit is not active (order: $($SysUnits -join ' '))" }
} | Out-Null
if ($RelaunchFleet) { Do-Step "relaunch seat fleet" { Start-Process powershell.exe -ArgumentList $FleetLnkArgs -WindowStyle Hidden } | Out-Null }

# ---------------------------------------------------------------- 11 report
Log "==== DONE in $([int]((Get-Date) - $T0).TotalMinutes) min"
if ($SkipBackup) { Log "REPORT backup tar:                   NONE (-SkipBackup); the old image below is the only fallback" } else { Log "REPORT backup tar (keep):            $Tar" }
Log "REPORT distro now at:                $Target"
Log "REPORT OLD IMAGE, owner deletes later: $KeepLink  (and $OldVhdx if --move left it)"
Log "REPORT .wslconfig untouched; seats relaunch: $(if ($RelaunchFleet) {'started'} else {'not started -- log on again or run Start Agent Fleet'})"
exit 0
