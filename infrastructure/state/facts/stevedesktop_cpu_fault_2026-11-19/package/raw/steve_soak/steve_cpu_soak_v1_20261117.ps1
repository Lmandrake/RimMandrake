# steve_cpu_soak.ps1 - token-free repeating CPU soak, runs ON SteveDesktop (scheduled task 'SteveDiag CPU Soak', SYSTEM, detached).
# (Conductor 2026-11-17: does Steve stay fault-free under load after the BIOS +0.100 V raise; item RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING.)
# Pass = each logical CPU pinned Prime95 $CoreSecs s, then ALL CPUs at once $AllSecs s. Per step one log line: UTC ts, pass, cpu, status,
# prime95 errors, WHEA count, vcore + temps from stevetemp.exe. Stops by itself on: first error, any core > $MaxC C, RimWorldWin64 running,
# the runner worker busy (a testq job), stop file, or end time. Never touches watch2 / fault_monitor.
# By hand: New-Item C:\SteveDesktop\diag\soak\STOP -ItemType File   (it stops within one step)  or  Stop-ScheduledTask 'SteveDiag CPU Soak'; Get-Process prime95|Stop-Process
param([int]$Hours=6,[int]$CoreSecs=45,[int]$AllSecs=90,[int]$MaxC=90)
$d='C:\SteveDesktop\diag'; $p="$d\p95"; $sd="$d\soak"; $log="$sd\soak.log"; $stop="$sd\STOP"
New-Item -ItemType Directory -Force $sd | Out-Null; Remove-Item $stop -EA 0
$end=(Get-Date).AddHours($Hours)
function L($m){ ("{0:yyyy-MM-ddTHH:mm:ss}Z {1}" -f (Get-Date).ToUniversalTime(),$m) | Add-Content $log }
function Busy(){ # why we must yield, or ''
  if(Test-Path $stop){return 'STOP file'}
  if(@(Get-Process RimWorldWin64 -EA 0).Count){return 'RimWorldWin64 running'}
  $o=(wsl.exe -e bash -c "cd ~/rm/runner && python3 infrastructure/stevedesktop/worker.py status" 2>$null) -join "`n"
  if($o -match '"busy":\s*true'){return 'runner worker busy (testq job)'}
  return '' }
function Step($cpu,$secs,$mask,$w){ # -> hashtable
  $ho="$sd\heat.txt"; $hs="$sd\heat.stop"; $t0=Get-Date; $h='UNMEASURED(no_sampler)'; $f=0;$a=0;$wh=0
  try{ Remove-Item $ho,$hs,"$p\results.txt" -EA 0
    "V24OptionsConverted=1`r`nStressTester=1`r`nUsePrimenet=0`r`nEnableSetAffinity=0`r`nEnableSetPriority=0`r`nMinTortureFFT=8`r`nMaxTortureFFT=128`r`nTortureMem=0`r`nTortureTime=1`r`nNumCores=$w`r`nTortureHyperthreading=0`r`nNumWorkers=$w`r`nCoresPerTest=1" | Set-Content "$p\prime.txt"
    if(Test-Path "$d\heat\stevetemp.exe"){ $sp=Start-Process "$d\heat\stevetemp.exe" -ArgumentList @(($secs+20),'500',$hs) -RedirectStandardOutput $ho -WindowStyle Hidden -PassThru }
    Start-Process cmd.exe -ArgumentList ("/c start `"`" /affinity {0:x} prime95.exe -t" -f $mask) -WorkingDirectory $p -WindowStyle Hidden
    Start-Sleep $secs
    if(Get-Process prime95 -EA 0){$a=1}
    if(Test-Path "$p\results.txt"){ $f=@(Get-Content "$p\results.txt"|?{$_ -match 'FATAL|[Hh]ardware failure|Possible hardware'}).Count }
    if($sp){ New-Item -ItemType File -Force $hs | Out-Null; if($sp.WaitForExit(20000)){ $l=@(Get-Content $ho -EA 0|?{$_.Trim()}); if($l.Count){$h=$l[-1].Trim()}else{$h='UNMEASURED(no_output)'} }else{ try{$sp.Kill()}catch{}; $h='UNMEASURED(sampler_hung)' } }
    $wh=@(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-WHEA-Logger';StartTime=$t0} -EA 0).Count
  }finally{ Get-Process prime95 -EA 0|Stop-Process -Force; Get-Process stevetemp -EA 0|?{$_.StartTime -ge $t0}|Stop-Process -Force }
  $m=[regex]::Match($h,'core_max_c=(\d+)'); $cm=if($m.Success){[int]$m.Groups[1].Value}else{-1}
  return @{fatal=$f;alive=$a;whea=$wh;heat=$h;core_max=$cm} }
$n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
$why=Busy; if($why){ L "SOAK REFUSED: $why"; exit 0 }
if(@(Get-Process prime95 -EA 0).Count){ L "SOAK REFUSED: prime95 already running"; exit 0 }
L "SOAK START hours=$Hours end=$($end.ToUniversalTime().ToString('s'))Z cpus=$n core_secs=$CoreSecs all_secs=$AllSecs max_c=$MaxC"
$pass=0; $reason=''; $steps=0
try{
 while(-not $reason -and (Get-Date) -lt $end){
  $pass++
  $plan=New-Object System.Collections.ArrayList
  for($i=0;$i -lt $n;$i++){ [void]$plan.Add(@($i,$CoreSecs,([int64]1 -shl $i),1)) }
  [void]$plan.Add(@(-1,$AllSecs,(([int64]1 -shl $n)-1),$n))
  foreach($s in $plan){
    $why=Busy; if($why){ $reason="YIELD: $why"; break }
    if((Get-Date).AddSeconds($s[1]+40) -gt $end){ $reason='END: time'; break }
    $r=Step $s[0] $s[1] $s[2] $s[3]; $steps++
    $bad=@(); if($r.fatal){$bad+="prime95_error x$($r.fatal)"}; if($r.whea){$bad+="WHEA x$($r.whea)"}; if(-not $r.alive){$bad+='prime95_died_early'}
    if($r.core_max -gt $MaxC){$bad+="core_max_c=$($r.core_max)>$MaxC"}
    L ("pass={0} cpu={1} {2} fatal={3} whea={4} alive={5} heat={6}" -f $pass,$s[0],$(if($bad){'FAIL '+($bad -join ';')}else{'PASS'}),$r.fatal,$r.whea,$r.alive,$r.heat)
    if($bad){ $reason="STOP-ON-ERROR: pass $pass cpu $($s[0]): $($bad -join ';')"; break }
  }
  if(-not $reason){ L "PASS_COMPLETE pass=$pass" }
 }
 if(-not $reason){$reason='END: time'}
}finally{ Get-Process prime95 -EA 0|Stop-Process -Force; L "SOAK END steps=$steps passes_started=$pass reason=$reason" }
