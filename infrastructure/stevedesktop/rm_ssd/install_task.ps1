# install_task.ps1 - register \RM SSD Attach on SteveDesktop (run elevated: the ssh door's sessions are).
# sjlewis, highest (wsl --mount needs administrator), interactive (WSL is per user; autologon keeps a session).
# Triggers: at logon, and every 2 min for ten years, as \Steve Seats Watch repeats.
$user = "$env:COMPUTERNAME\sjlewis"
$a = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument '"C:\SteveDesktop\rm_ssd_attach.vbs"'
$t1 = New-ScheduledTaskTrigger -AtLogOn -User $user
$t2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 2) -RepetitionDuration (New-TimeSpan -Days 3650)
$p = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Highest
# ExecutionTimeLimit: a hung wsl.exe would hold the task (IgnoreNew) and no later beat would attach; a beat takes ~2 s.
$s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew -ExecutionTimeLimit (New-TimeSpan -Minutes 4)
Register-ScheduledTask -TaskName 'RM SSD Attach' -TaskPath '\' -Action $a -Trigger $t1, $t2 -Principal $p -Settings $s -Force | Out-Null
$x = Get-ScheduledTask -TaskName 'RM SSD Attach'
"registered \RM SSD Attach: user=$($x.Principal.UserId) run=$($x.Principal.RunLevel) state=$($x.State)"
