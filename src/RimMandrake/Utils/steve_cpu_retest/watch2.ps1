# watch2.ps1 - the 5-minute fault watch, now a scheduled task ("SteveDiag Fault Watch", at startup, SYSTEM),
# so a reboot no longer kills it. Every CycleS: a 4 s pinned stevecheck core per logical CPU (all of them, 18 or 20),
# summary line in C:\SteveDesktop\diag\logs\watch.log (same format as before). While retest\armed.flag exists and no
# fault.json yet, a bad CPU writes retest\fault.json (event=watch) for the controller on the PC. Each watcher starts with a
# CONTROL line: an injected fault must exit 1, a clean run 0, or the cycles below prove nothing. The log is read on
# Archmagi by testq/fault_monitor.py (rm-steve-fault.timer): keep the WATCH START / CONTROL / CYCLE formats it parses.
# Heat (STEVE_HEAT_MEASURE_BEFORE_THE_SCREWDRIVER): heat\stevetemp.exe (fault_monitor.py deploy-heat) samples the CPU
# package and per-core temperatures every 500 ms WHILE the cycle's checks run, and its one line ends the CYCLE line;
# no sampler, a hung one or an empty answer ends it with heat=UNMEASURED(<why>) instead, never with nothing.
param([int]$CycleS=300,[int]$CheckS=4)
$d='C:\SteveDesktop\diag'; $b="$d\bin3\stevecheck.exe"; $log="$d\logs\watch.log"; $ck="$d\logs\watch-chk.log"; $r="$d\retest"
$tp="$d\heat\stevetemp.exe"; $ho="$d\logs\heat-cur.txt"; $hstop="$d\logs\heat-stop.flag"
New-Item -ItemType Directory -Force $r | Out-Null
function W($s){ Add-Content $log "$((Get-Date).ToUniversalTime().ToString('yyyy-MM-dd HH:mm:ss'))Z $s" }
# one watcher only
$me=$PID; $others=@(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | ? { $_.CommandLine -match 'watch2\.ps1' -and $_.ProcessId -ne $me })
if($others.Count){ exit 0 }
Start-Sleep 60
$boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
$n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
W "WATCH START boot=$($boot.ToString('yyyy-MM-dd HH:mm:ss'))Z logical_cpus=$n cycle=${CycleS}s per-cpu core check ${CheckS}s each (scheduled task, survives reboot)"
$cl="$d\logs\watch-ctl.log"; & $b core 0 3 $cl inject | Out-Null; $ia=$LASTEXITCODE; & $b core 0 3 $cl | Out-Null; $ic=$LASTEXITCODE
W "CONTROL inject_exit=$ia clean_exit=$ic"
while($true){
 $t0=Get-Date; $fails=@(); $rcs=@(); $hs=$null; $heat='heat=UNMEASURED(no_sampler)'
 Remove-Item $ho,$hstop -EA 0
 if(Test-Path $tp){ try{ $hs=Start-Process $tp -ArgumentList @([string]($n*$CheckS*2+60),'500',$hstop) -RedirectStandardOutput $ho -WindowStyle Hidden -PassThru }catch{ $heat='heat=UNMEASURED(sampler_start_failed)' } }
 foreach($cpu in 0..($n-1)){ & $b core $cpu $CheckS $ck | Out-Null; if($LASTEXITCODE -ne 0){$fails+=$cpu; $rcs+=$LASTEXITCODE} }
 if($hs){ New-Item -ItemType File -Force $hstop | Out-Null
   if($hs.WaitForExit(30000)){ $h=@(Get-Content $ho -EA 0 | ?{$_.Trim()}); if($h.Count){$heat=$h[-1].Trim()}else{$heat='heat=UNMEASURED(no_output)'} }
   else{ try{$hs.Kill()}catch{}; $heat='heat=UNMEASURED(sampler_hung)' } }
 $up=[math]::Round(((Get-Date).ToUniversalTime()-$boot).TotalHours,2)
 W "CYCLE uptime_h=$up bad_cpus=[$($fails -join ',')] n_ok=$($n-$fails.Count) exits=[$($rcs -join ',')] $heat"
 if($fails.Count -and (Test-Path "$r\armed.flag") -and -not (Test-Path "$r\fault.json")){
   @{event='watch';cpu=$fails[0];bad=@('watch_core');cpus=$fails;uptime_h=$up;ts=(Get-Date).ToUniversalTime().ToString('s')+'Z'} | ConvertTo-Json | Set-Content "$r\fault.json" }
 $left=$CycleS-((Get-Date)-$t0).TotalSeconds; if($left -gt 0){Start-Sleep ([int]$left)}
}
