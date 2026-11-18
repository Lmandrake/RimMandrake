# steve_cpu_soak.ps1 - token-free repeating CPU soak, runs ON SteveDesktop (scheduled task 'SteveDiag CPU Soak', SYSTEM, detached,
# AtStartup trigger: a reboot resumes the same run and appends). Read it with: python3 src/RimMandrake/Utils/steve_cpu_retest/soak_read.py
# (Conductor 2026-11-17: does Steve stay fault-free under load after the BIOS +0.100 V raise; items RIMMANDRAKE_COUNT_STEVE_FAULTS_AFTER_VOLTAGE_RAISE_TO_CEILING,
#  RIMMANDRAKE_RERUN_STEVEDESKTOP_CPU_SOAK_INTERRUPTED_MID_RUN.)
# Pass = each logical CPU pinned Prime95 $CoreSecs s, then ALL CPUs at once $AllSecs s. Per step one log line: UTC ts, pass, cpu, status,
# prime95 errors, WHEA count, load % mid-step, vcore + temps from stevetemp.exe. A FAIL step is logged and the soak goes on (long data);
# it ENDS only on: a core > $MaxC C, $MaxFails FAIL steps, the STOP file, or the planned end. RimWorldWin64 running or the runner worker
# busy (a testq job) is waited out (WAIT / WAIT END lines), never an end. Each start or resume first runs CONTROL: an injected Prime95
# error and an injected early death must both be SEEN, and the sampler must answer, or the faults=0 below proves nothing.
# Run state: soak\state.json (run id, planned end UTC, last boot). -Plan writes a fresh plan (refused while one is live); the task then
# starts it; every later task start (boot) resumes it and logs SOAK REBOOT with the boot time. Never touches watch2 / fault_monitor.
# By hand: New-Item C:\SteveDesktop\diag\soak\STOP -ItemType File   (it stops within one step)  or  Stop-ScheduledTask 'SteveDiag CPU Soak'; Get-Process prime95|Stop-Process
param([switch]$Plan,[double]$Hours=72,[int]$CoreSecs=45,[int]$AllSecs=90,[int]$MaxC=90,[int]$MaxFails=50)
$d='C:\SteveDesktop\diag'; $p="$d\p95"; $sd="$d\soak"; $log="$sd\soak.log"; $stop="$sd\STOP"; $stf="$sd\state.json"
New-Item -ItemType Directory -Force $sd | Out-Null
function L($m){ ("{0:yyyy-MM-ddTHH:mm:ss}Z {1}" -f (Get-Date).ToUniversalTime(),$m) | Add-Content $log }
function Iso($t){ $t.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss')+'Z' }
function ReadState(){ if(Test-Path $stf){ try{ return (Get-Content $stf -Raw | ConvertFrom-Json) }catch{ return $null } }; return $null }
function SaveState($s){ $s | ConvertTo-Json | Set-Content $stf }
$boot=Iso (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
if($Plan){
  $s=ReadState
  if($s -and -not $s.finished -and ([datetime]$s.end_utc).ToUniversalTime() -gt (Get-Date).ToUniversalTime()){ "REFUSED: run $($s.run) is live until $($s.end_utc)"; exit 2 }
  Remove-Item $stop -EA 0
  $now=(Get-Date).ToUniversalTime(); $run='S'+$now.ToString('yyyyMMddTHHmmss')+'Z'
  SaveState ([ordered]@{run=$run;planned_utc=(Iso $now);end_utc=(Iso $now.AddHours($Hours));hours=$Hours;core_secs=$CoreSecs;all_secs=$AllSecs;max_c=$MaxC;max_fails=$MaxFails;started=$false;boot=$null;finished=$null;fails=0})
  L "SOAK PLAN run=$run hours=$Hours end=$(Iso $now.AddHours($Hours))"; "PLANNED $run"; exit 0 }
$s=ReadState
if(-not $s -or $s.finished){ exit 0 }                       # nothing planned / already ended: a boot start is a no-op
$end=([datetime]$s.end_utc).ToUniversalTime(); $run=$s.run; $CoreSecs=[int]$s.core_secs; $AllSecs=[int]$s.all_secs; $MaxC=[int]$s.max_c; $MaxFails=[int]$s.max_fails
function Finish($why){ $s.finished=$why; SaveState $s }
if((Get-Date).ToUniversalTime() -ge $end){ L "SOAK END run=$run steps=0 reason=END: time (planned end passed while down)"; Finish 'END: time'; exit 0 }
if(@(Get-Process prime95 -EA 0).Count){ L "SOAK REFUSED run=${run}: prime95 already running"; exit 0 }
function Busy(){ # why we must wait, or ''
  if(@(Get-Process RimWorldWin64 -EA 0).Count){return 'RimWorldWin64 running'}
  $o=(wsl.exe -e bash -c "cd ~/rm/runner && python3 infrastructure/stevedesktop/worker.py status" 2>$null) -join "`n"
  $script:probe=if($o -match '"busy"'){'answered'}else{'blind'}
  if($o -match '"busy":\s*true'){return 'runner worker busy (testq job)'}
  return '' }
function Load($cpu){ # % busy of that CPU (or all) over 1 s, -1 = could not read
  try{ $n=if($cpu -lt 0){'_total'}else{"$cpu"}; return [int](Get-Counter "\Processor($n)\% Processor Time" -SampleInterval 1 -MaxSamples 1 -EA Stop).CounterSamples[0].CookedValue }catch{ return -1 } }
function Step($cpu,$secs,$mask,$w,$inject=''){ # -> hashtable; $inject 'fatal' appends a Prime95 error line mid-step, 'kill' kills it mid-step
  $ho="$sd\heat.txt"; $hs="$sd\heat.stop"; $t0=Get-Date; $h='UNMEASURED(no_sampler)'; $f=0;$a=0;$wh=0;$ld=-1;$sp=$null
  try{ Remove-Item $ho,$hs,"$p\results.txt" -EA 0
    "V24OptionsConverted=1`r`nStressTester=1`r`nUsePrimenet=0`r`nEnableSetAffinity=0`r`nEnableSetPriority=0`r`nMinTortureFFT=8`r`nMaxTortureFFT=128`r`nTortureMem=0`r`nTortureTime=1`r`nNumCores=$w`r`nTortureHyperthreading=0`r`nNumWorkers=$w`r`nCoresPerTest=1" | Set-Content "$p\prime.txt"
    if(Test-Path "$d\heat\stevetemp.exe"){ $sp=Start-Process "$d\heat\stevetemp.exe" -ArgumentList @(($secs+20),'500',$hs) -RedirectStandardOutput $ho -WindowStyle Hidden -PassThru }
    Start-Process cmd.exe -ArgumentList ("/c start `"`" /affinity {0:x} prime95.exe -t" -f $mask) -WorkingDirectory $p -WindowStyle Hidden
    $half=[int]($secs/2); Start-Sleep $half; $ld=Load $cpu
    if($inject -eq 'fatal'){ Add-Content "$p\results.txt" 'FATAL ERROR: Rounding was 0.5, expected less than 0.4 (SOAK CONTROL INJECTED)' }
    if($inject -eq 'kill'){ Get-Process prime95 -EA 0|Stop-Process -Force }
    Start-Sleep ($secs-$half)
    if(Get-Process prime95 -EA 0){$a=1}
    if(Test-Path "$p\results.txt"){ $f=@(Get-Content "$p\results.txt"|?{$_ -match 'FATAL|[Hh]ardware failure|Possible hardware'}).Count }
    if($sp){ New-Item -ItemType File -Force $hs | Out-Null; if($sp.WaitForExit(20000)){ $l=@(Get-Content $ho -EA 0|?{$_.Trim()}); if($l.Count){$h=$l[-1].Trim()}else{$h='UNMEASURED(no_output)'} }else{ try{$sp.Kill()}catch{}; $h='UNMEASURED(sampler_hung)' } }
    $wh=@(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-WHEA-Logger';StartTime=$t0} -EA 0).Count
  }finally{ Get-Process prime95 -EA 0|Stop-Process -Force; Get-Process stevetemp -EA 0|?{$_.StartTime -ge $t0}|Stop-Process -Force }
  $m=[regex]::Match($h,'core_max_c=(\d+)'); $cm=if($m.Success){[int]$m.Groups[1].Value}else{-1}
  return @{fatal=$f;alive=$a;whea=$wh;heat=$h;core_max=$cm;load=$ld} }
$n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors; $probe='unasked'
# the start / resume line: a new boot under a started run is a data point
if(-not $s.started){ L "SOAK START run=$run hours=$($s.hours) end=$(Iso $end) cpus=$n core_secs=$CoreSecs all_secs=$AllSecs max_c=$MaxC max_fails=$MaxFails boot=$boot" }
elseif($s.boot -ne $boot){ L "SOAK REBOOT run=$run boot=$boot prev_boot=$($s.boot)"; L "SOAK RESUME run=$run end=$(Iso $end) cpus=$n" }
else{ L "SOAK RESTART run=$run same_boot=$boot end=$(Iso $end)" }
$s.started=$true; $s.boot=$boot; SaveState $s
$waited=$false; while(($why=Busy) -and -not (Test-Path $stop) -and (Get-Date).ToUniversalTime() -lt $end){ if(-not $waited){ L "WAIT: $why"; $waited=$true }; Start-Sleep 60 }
if($waited){ L "WAIT END" }
L "PROBES run=$run worker_probe=$probe rimworld=$(@(Get-Process RimWorldWin64 -EA 0).Count) whoami=$(whoami)"
# CONTROL: the instrument must see an injected error and an injected death, and the sampler must answer
$ci=Step 0 12 1 1 'fatal'; $ck=Step 0 12 1 1 'kill'
$okf=[int]($ci.fatal -ge 1); $okk=[int](-not $ck.alive); $okh=[int](-not ($ci.heat -like 'UNMEASURED*')); $okl=[int]($ci.load -ge 50)
L ("CONTROL run={0} inject_fatal_seen={1} inject_died_seen={2} heat_seen={3} load_seen={4} load={5} ok={6}" -f $run,$okf,$okk,$okh,$okl,$ci.load,[int]($okf -and $okk -and $okh -and $okl))
$pass=0; $reason=''; $steps=0; $fails=[int]$s.fails
try{
 while(-not $reason){
  if((Get-Date).ToUniversalTime() -ge $end){ $reason='END: time'; break }
  $pass++
  $steps_list=New-Object System.Collections.ArrayList
  for($i=0;$i -lt $n;$i++){ [void]$steps_list.Add(@($i,$CoreSecs,([int64]1 -shl $i),1)) }
  [void]$steps_list.Add(@(-1,$AllSecs,(([int64]1 -shl $n)-1),$n))
  foreach($st in $steps_list){
    if(Test-Path $stop){ $reason='STOP file'; break }
    $waited=$false; while(($why=Busy) -and -not (Test-Path $stop) -and (Get-Date).ToUniversalTime() -lt $end){ if(-not $waited){ L "WAIT: $why"; $waited=$true }; Start-Sleep 60 }
    if($waited){ L "WAIT END" }
    if(Test-Path $stop){ $reason='STOP file'; break }
    if((Get-Date).ToUniversalTime().AddSeconds($st[1]+40) -gt $end){ $reason='END: time'; break }
    $r=Step $st[0] $st[1] $st[2] $st[3]; $steps++
    $bad=@(); if($r.fatal){$bad+="prime95_error x$($r.fatal)"}; if($r.whea){$bad+="WHEA x$($r.whea)"}; if(-not $r.alive){$bad+='prime95_died_early'}
    $hot=$r.core_max -gt $MaxC; if($hot){$bad+="core_max_c=$($r.core_max)>$MaxC"}
    L ("pass={0} cpu={1} {2} fatal={3} whea={4} alive={5} load={6} heat={7}" -f $pass,$st[0],$(if($bad){'FAIL '+($bad -join ';')}else{'PASS'}),$r.fatal,$r.whea,$r.alive,$r.load,$r.heat)
    if($bad){ $fails++; $s.fails=$fails; SaveState $s }
    if($hot){ $reason="STOP-ON-HEAT: pass $pass cpu $($st[0]): core_max_c=$($r.core_max)>$MaxC"; break }
    if($fails -ge $MaxFails){ $reason="STOP-ON-FAILS: $fails FAIL steps >= $MaxFails"; break }
  }
  if(-not $reason){ L "PASS_COMPLETE pass=$pass" }
 }
}catch{ L "SOAK ERROR run=$run line=$($_.InvocationInfo.ScriptLineNumber) $($_.Exception.Message)"
}finally{ Get-Process prime95 -EA 0|Stop-Process -Force
 if($reason){ L "SOAK END run=$run steps=$steps passes_started=$pass fails=$fails reason=$reason"; Finish $reason }
 else{ L "SOAK INTERRUPTED run=$run steps=$steps passes_started=$pass (script exited without a reason; the next boot or task start resumes)" } }
