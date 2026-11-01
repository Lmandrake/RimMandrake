# install_tasks.ps1 - registers the two startup tasks (SYSTEM, highest, restart on failure, no time limit).
$ErrorActionPreference='Stop'
$d='C:\SteveDesktop\diag'
function Reg($name,$script,$desc){
 $a=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""
 $t=New-ScheduledTaskTrigger -AtStartup
 $p=New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
 $s=New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)
 Register-ScheduledTask -TaskName $name -TaskPath '\' -Action $a -Trigger $t -Principal $p -Settings $s -Description $desc -Force | Out-Null
 Get-ScheduledTask -TaskName $name | % { "$($_.TaskName) $($_.State)" }
}
Reg 'SteveDiag Fault Watch' "$d\watch2.ps1" 'CPU fault watch every 5 min, restarts at boot (STEVE_FAULT_MONITOR_ONSET_BEFORE_RESULTS)'
Reg 'SteveDiag CPU Retest' "$d\retest.ps1" 'CPU 18/19 unmasked retest schedule; runs only while retest\armed.flag exists (CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH)'
