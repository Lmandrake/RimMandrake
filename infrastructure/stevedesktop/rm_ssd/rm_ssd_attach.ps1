# rm_ssd_attach.ps1 - attach SteveDesktop's ~/rm disk (C:\WSL\rmssd\rm.vhdx, the NVMe) to the WSL VM when the VM is up
# and the disk is not attached (RIMMANDRAKE_MOVE_STEVEDESKTOP_CLONES_TO_SSD_LINUX_DRIVE_SITS_ON_HARD_DISK).
# Run by the task \RM SSD Attach (sjlewis, highest: `wsl --mount` needs administrator) at logon and every 2 min, through
# rm_ssd_attach.vbs (no console window, so no focus is taken from a game). WSL's rm-ssd-mount.service mounts it at ~/rm.
# Log C:\SteveDesktop\rm_ssd_attach.log: actions and failures only.
$vhd = 'C:\WSL\rmssd\rm.vhdx'
$log = 'C:\SteveDesktop\rm_ssd_attach.log'
$env:WSL_UTF8 = '1'
function Say($m) { Add-Content -Path $log -Value ('{0:yyyy-MM-dd HH:mm:ss} {1}' -f (Get-Date), $m) }
if ((Test-Path $log) -and (Get-Item $log).Length -gt 1MB) { Move-Item $log "$log.old" -Force }
# Stand aside while wsl.exe exports, imports, unregisters or stops the distro (as seats_watch.ps1 does).
$busy = Get-CimInstance Win32_Process -Filter "Name='wsl.exe'" |
    Where-Object { $_.CommandLine -match '--(export|import|unregister|shutdown|terminate)' }
if ($busy) { exit 0 }
# No VM, nothing to attach to: the keepalive starts WSL and the next beat attaches. Never start WSL from here.
$running = ((& wsl.exe --list --running --quiet) -join ' ') -replace "`0", ''
if ($running -notmatch 'Ubuntu') { exit 0 }
$out = ((& wsl.exe --mount --vhd $vhd --bare 2>&1 | Out-String) -replace "`0", '').Trim()
$rc = $LASTEXITCODE
if ($rc -eq 0) { Say "attached $vhd" }
elseif ($out -notmatch 'ALREADY_ATTACHED') { Say "attach FAILED rc=$rc $out" }
