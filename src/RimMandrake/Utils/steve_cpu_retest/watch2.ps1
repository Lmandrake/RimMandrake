# watch2.ps1 - the 5-minute fault watch, now a scheduled task ("SteveDiag Fault Watch", at startup, SYSTEM),
# so a reboot no longer kills it. Every CycleS: a 4 s pinned stevecheck core per logical CPU (all of them, 18 or 20),
# summary line in C:\SteveDesktop\diag\logs\watch.log (same format as before). While retest\armed.flag exists and no
# fault.json yet, a bad CPU writes retest\fault.json (event=watch) for the controller on the PC.
param([int]$CycleS=300,[int]$CheckS=4)
$d='C:\SteveDesktop\diag'; $b="$d\bin3\stevecheck.exe"; $log="$d\logs\watch.log"; $ck="$d\logs\watch-chk.log"; $r="$d\retest"
New-Item -ItemType Directory -Force $r | Out-Null
function W($s){ Add-Content $log "$((Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss'))Z $s" }
# one watcher only
$me=$PID; $others=@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | ? { $_.CommandLine -match 'watch2\.ps1' -and $_.ProcessId -ne $me })
if($others.Count){ exit 0 }
Start-Sleep 60
$boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
$n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
W "WATCH START boot=$($boot.ToString('yyyy-MM-dd HH:mm:ss'))Z logical_cpus=$n cycle=${CycleS}s per-cpu core check ${CheckS}s each (scheduled task, survives reboot)"
while($true){
 $t0=Get-Date; $fails=@()
 foreach($cpu in 0..($n-1)){ & $b core $cpu $CheckS $ck | Out-Null; if($LASTEXITCODE -ne 0){$fails+=$cpu} }
 $up=[math]::Round(((Get-Date).ToUniversalTime()-$boot).TotalHours,2)
 W "CYCLE uptime_h=$up bad_cpus=[$($fails -join ',')] n_ok=$($n-$fails.Count)"
 if($fails.Count -and (Test-Path "$r\armed.flag") -and -not (Test-Path "$r\fault.json")){
   @{event='watch';cpu=$fails[0];bad=@('watch_core');cpus=$fails;uptime_h=$up;ts=(Get-Date).ToUniversalTime().ToString('s')+'Z'} | ConvertTo-Json | Set-Content "$r\fault.json" }
 $left=$CycleS-((Get-Date)-$t0).TotalSeconds; if($left -gt 0){Start-Sleep ([int]$left)}
}
