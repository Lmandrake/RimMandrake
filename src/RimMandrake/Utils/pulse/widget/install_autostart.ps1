# RimFlow Pulse widget autostart (AWAY_DASHBOARD_BUILD_1). Idempotent; current user, no admin.
# A scheduled task: at logon, then every 10 minutes. The widget is single-instance (a named
# mutex), so the repeat only matters when it crashed or was closed - the "window closed and
# never reopened" failure that killed earlier dashboards. MultipleInstances MUST be Parallel: the
# task instance stays Running for the widget's whole life, so IgnoreNew silently refused every re-run
# (LastTaskResult 0x800710E0) and the launch watchdog that replaces a hung widget never got to run.
# Run from WSL:  powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\widget\install_autostart.ps1'
# Remove:        Unregister-ScheduledTask -TaskName 'RimFlow Pulse' -Confirm:$false
$ErrorActionPreference = 'Stop'
$pyw = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\pythonw.exe'
$script = 'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\widget\lantern.pyw'
$action = New-ScheduledTaskAction -Execute $pyw -Argument ('"' + $script + '"') -WorkingDirectory 'D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\pulse\widget'
$logon = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$repeat = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 10)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances Parallel -ExecutionTimeLimit ([TimeSpan]::Zero)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName 'RimFlow Pulse' -Action $action -Trigger @($logon, $repeat) -Settings $settings -Principal $principal -Description 'RimFlow Pulse floating widget (WSL rm-pulse.service feeds it)' -Force | Out-Null
$t = Get-ScheduledTask -TaskName 'RimFlow Pulse'
"installed: $($t.TaskName) state=$($t.State) triggers=$($t.Triggers.Count)"
