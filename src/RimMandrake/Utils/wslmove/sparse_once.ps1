<# sparse_once.ps1 -- force the moved Ubuntu image sparse (owner, 2026-10-11: "Force it"), then fstrim so
freed blocks go back to E:. Runs as a one-shot scheduled task (it must survive `wsl --shutdown`).
Microsoft disables sparse VHDs for "potential data corruption"; the old image on C: is the fallback.
  Launch:  powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Luke\dev\_rmscratch\wslmove\sparse_once.ps1 -Launch -DelaySec 60 #>
param([switch]$Launch, [int]$DelaySec = 60)
$name   = "WSL Sparse Once"
$distro = "Ubuntu"
$vhd    = "E:\WSL\Ubuntu\ext4.vhdx"
$log    = "D:\Luke\dev\_rmscratch\wslmove\sparse.log"
$tasks  = @("\WSL Keepalive","\RimFlow Pulse")

if ($Launch) {
    $act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$PSCommandPath`" -DelaySec $DelaySec"
    $set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2) -MultipleInstances IgnoreNew
    $pri = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
    Register-ScheduledTask -TaskName $name -Action $act -Settings $set -Principal $pri -Force | Out-Null
    Start-ScheduledTask -TaskName $name
    "STARTED task '$name' (DelaySec=$DelaySec); log: $log"
    return
}

function Log([string]$m) { Add-Content -Path $log -Value ("{0}  {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m) }
function Run([string]$exe, [string[]]$a) {
    $out = & $exe @a 2>&1 | Out-String
    $out = ($out -replace "`0", "").Trim()
    Log ("  {0} {1} -> exit {2}" -f $exe, ($a -join " "), $LASTEXITCODE)
    if ($out) { Log ("      " + ($out -replace "`r?`n", "`n      ")) }
    return $LASTEXITCODE
}
function SizeOnDisk { (& fsutil file layout $vhd 2>$null | Select-String "Allocated" | Select-Object -First 1) -as [string] }

Log "==== sparse_once start (delay $DelaySec s)"
Start-Sleep -Seconds $DelaySec
$eFree0 = (Get-Volume -DriveLetter E).SizeRemaining
foreach ($t in $tasks) { $p = Split-Path $t -Parent; $n = Split-Path $t -Leaf; Disable-ScheduledTask -TaskPath "$p\".Replace("\\","\") -TaskName $n -EA SilentlyContinue | Out-Null; Log "disabled $t" }
Run "wsl.exe" @("--shutdown") | Out-Null
Start-Sleep -Seconds 10
Run "wsl.exe" @("--manage", $distro, "--set-sparse", "true", "--allow-unsafe") | Out-Null
Run "fsutil.exe" @("sparse", "queryflag", $vhd) | Out-Null
Run "wsl.exe" @("-d", $distro, "-u", "root", "--", "fstrim", "-v", "/") | Out-Null
Start-Sleep -Seconds 5
$eFree1 = (Get-Volume -DriveLetter E).SizeRemaining
Log ("E: free: {0:N0} GB -> {1:N0} GB" -f ($eFree0/1GB), ($eFree1/1GB))
foreach ($t in $tasks) { $p = Split-Path $t -Parent; $n = Split-Path $t -Leaf; Enable-ScheduledTask -TaskPath "$p\".Replace("\\","\") -TaskName $n -EA SilentlyContinue | Out-Null; Start-ScheduledTask -TaskPath "$p\".Replace("\\","\") -TaskName $n -EA SilentlyContinue; Log "enabled+started $t" }
Start-Sleep -Seconds 20
Run "wsl.exe" @("-d", $distro, "-u", "mandrake", "--", "env", "XDG_RUNTIME_DIR=/run/user/1000", "systemctl", "--user", "is-active", "rm-artpiped.service", "rm-pulse.service", "hestia.service") | Out-Null
Log "==== DONE. Seats not relaunched -- run Start Agent Fleet."
Unregister-ScheduledTask -TaskName $name -Confirm:$false -EA SilentlyContinue
