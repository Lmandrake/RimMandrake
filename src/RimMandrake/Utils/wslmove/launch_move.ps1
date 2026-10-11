<# launch_move.ps1 -- start move_wsl_to_e.ps1 as a one-shot Windows scheduled task, so it is owned by the
Task Scheduler service and survives `wsl --shutdown` (a process spawned through WSL interop is not).
No elevation needed: tasks run as the current user, Limited token. The task has no trigger; it stays registered and inert (re-registered with -Force each launch).
  Dry run:  powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Luke\dev\_rmscratch\wslmove\launch_move.ps1 -WhatIf
  Real:     powershell.exe -NoProfile -ExecutionPolicy Bypass -File D:\Luke\dev\_rmscratch\wslmove\launch_move.ps1 -DelaySec 90 #>
param([switch]$WhatIf, [int]$DelaySec = 0, [switch]$RelaunchFleet)
$name   = "WSL Move Once"
$script = "D:\Luke\dev\_rmscratch\wslmove\move_wsl_to_e.ps1"
$args2  = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`" -SelfTaskName `"$name`" -DelaySec $DelaySec"
if ($WhatIf)        { $args2 += " -WhatIf" }
if ($RelaunchFleet) { $args2 += " -RelaunchFleet" }
$act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $args2
$set = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 12) -MultipleInstances IgnoreNew
$pri = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $name -Action $act -Settings $set -Principal $pri -Force | Out-Null
Start-ScheduledTask -TaskName $name
"STARTED task '$name' (WhatIf=$WhatIf, DelaySec=$DelaySec); log: D:\Luke\dev\_rmscratch\wslmove\move.log"
