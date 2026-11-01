# retest.ps1 - runs ON SteveDesktop (scheduled task "SteveDiag CPU Retest", at startup, SYSTEM).
# CPU_RETEST_PROVE_MASKED_PAIR_AFTER_FLASH: after the numproc mask is removed (20 logical CPUs), test CPUs 18+19
# (quick, every QuickMin) and all CPUs (full sweep at uptime milestones) past the old onset time, while the testq
# lane runs RimWorld jobs on the same machine. Writes C:\SteveDesktop\diag\retest\readings.jsonl (one JSON per
# reading), fault.json on the first fault (then stops), done.json when clean past OnsetH.
# Runs only while retest\armed.flag exists. -SelfTest runs the instrument controls + one CPU and exits.
param([int]$QuickMin=20,[double]$OnsetH=144,[double[]]$FullAtH=@(0.2,12,24,48,72,96,120,144),[int]$P95Sec=20,[int]$ChkSec=20,[switch]$SelfTest)
$d='C:\SteveDesktop\diag'; $r="$d\retest"; $p95="$d\p95"; $b="$d\bin3\stevecheck.exe"
$py='C:\Program Files\Python313\python.exe'
New-Item -ItemType Directory -Force $r | Out-Null
$rd="$r\readings.jsonl"
function Now{(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')}
$boot=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime.ToUniversalTime()
function UpH{[math]::Round(((Get-Date).ToUniversalTime()-$boot).TotalHours,3)}
function Emit($o){ $o['ts']=Now; $o['uptime_h']=UpH; Add-Content $rd (($o|ConvertTo-Json -Compress -Depth 4)) }
function Lines($f,$n){ if(Test-Path $f){ @(Get-Content $f -Tail $n) } else { @() } }

function Test-Cpu([int]$cpu,[string]$kind){
 $hex='{0:x}' -f (1L -shl $cpu); $bad=@(); $inv=@()
 $res=[ordered]@{event='cpu';kind=$kind;cpu=$cpu}
 foreach($rg in @(@(4,8),@(128,256))){ $lo=$rg[0];$hi=$rg[1]
  "V24OptionsConverted=1`r`nStressTester=1`r`nUsePrimenet=0`r`nEnableSetAffinity=0`r`nEnableSetPriority=0`r`nMinTortureFFT=$lo`r`nMaxTortureFFT=$hi`r`nTortureMem=0`r`nTortureTime=1`r`nNumCores=1`r`nTortureHyperthreading=0`r`nNumWorkers=1`r`nCoresPerTest=1" | Set-Content "$p95\prime.txt"
  Remove-Item "$p95\results.txt" -EA 0
  Start-Process cmd.exe -ArgumentList "/c start `"`" /affinity $hex prime95.exe -t" -WorkingDirectory $p95 -WindowStyle Hidden
  Start-Sleep $P95Sec; $pr=Get-Process prime95 -EA 0|Select -First 1; $s=-1; if($pr){$s=[int]$pr.TotalProcessorTime.TotalSeconds}
  Get-Process prime95 -EA 0|Stop-Process -Force; Start-Sleep 1
  $f=0; if(Test-Path "$p95\results.txt"){ $f=@(Get-Content "$p95\results.txt"|?{$_ -match 'FATAL'}).Count }
  $res["p95_${lo}_fatal"]=$f; $res["p95_${lo}_cpusec"]=$s
  if($f -gt 0){$bad+="p95_$lo"}; if($s -lt 3){$inv+="p95_${lo}_cpusec$s"}
 }
 $cl="$r\chk.log"; & $b core $cpu $ChkSec $cl | Out-Null; $ec=$LASTEXITCODE
 $m=[regex]::Match(@(Lines $cl 1)[0],'rounds=(\d+) bad=(\d+) moved=(\d+)')
 if($m.Success){ $res.chk_rounds=[long]$m.Groups[1].Value; $res.chk_bad=[long]$m.Groups[2].Value; $res.chk_moved=[long]$m.Groups[3].Value
   if($res.chk_rounds -lt 20){$inv+='chk_rounds'} } else { $inv+='chk_noline' }
 if($ec -ne 0){$bad+='chk'}
 $hl="$r\hash.log"; Remove-Item $hl -EA 0
 Start-Process cmd.exe -ArgumentList "/c start /wait /b /affinity $hex `"$py`" $d\corestab.py $hl $cpu" -Wait -WindowStyle Hidden
 $hm=[regex]::Match(@(Lines $hl 1)[0],'distinct (\d+)')
 if($hm.Success){ $res.hash_distinct=[int]$hm.Groups[1].Value; if($res.hash_distinct -ne 1){$bad+='hash'} } else { $inv+='hash_noline' }
 $hdl="$r\hold.log"; & $b hold $cpu 3 $hdl | Out-Null; $hc=$LASTEXITCODE
 $hm2=[regex]::Match(@(Lines $hdl 1)[0],'hits=(\d+)'); if($hm2.Success){$res.hold_hits=[int]$hm2.Groups[1].Value}
 if($hc -ne 0){$bad+='hold'}
 $res.verdict= if($bad.Count){'FAULT'}elseif($inv.Count){'INVALID'}else{'OK'}
 $res.bad=$bad; $res.invalid=$inv
 $script:last=$res; Emit $res
}
function Controls{ $script:ctl=$false
 # the instrument must see a fault: stevecheck core with inject must exit 1; the clean run must exit 0
 $cl="$r\ctl.log"; & $b core 0 3 $cl inject | Out-Null; $a=$LASTEXITCODE; & $b core 0 3 $cl | Out-Null; $c=$LASTEXITCODE
 Emit ([ordered]@{event='control';inject_exit=$a;clean_exit=$c;ok=($a -eq 1 -and $c -eq 0)})
 $script:ctl=($a -eq 1 -and $c -eq 0)
}
function Stop-Fault($res){
 $res | ConvertTo-Json -Depth 4 | Set-Content "$r\fault.json"
 Emit ([ordered]@{event='FAULT_STOP';cpu=$res.cpu;bad=$res.bad}); exit 3
}

if($SelfTest){ Controls | Out-Null; $ok=$script:ctl; Test-Cpu 0 'selftest' | Out-Null; $x=$script:last; "controls_ok=$ok verdict=$($x.verdict)"; exit 0 }
if(-not (Test-Path "$r\armed.flag")){ exit 0 }
if((Test-Path "$r\fault.json") -or (Test-Path "$r\done.json")){ exit 0 }
Start-Sleep 90   # let the seats and the lane settle after boot
$n=(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors
Emit ([ordered]@{event='start';logical_cpus=$n;boot=$boot.ToString('s')+'Z';onset_h=$OnsetH})
if($n -ne 20){ Emit ([ordered]@{event='ABORT_CPU_COUNT';logical_cpus=$n}); exit 2 }
Controls | Out-Null
if(-not $script:ctl){ Emit ([ordered]@{event='ABORT_CONTROLS'}); exit 2 }
$cpus=0..($n-1); $doneFull=@{}
while($true){
 if(-not (Test-Path "$r\armed.flag")){ Emit ([ordered]@{event='DISARMED'}); exit 0 }
 $t0=Get-Date; $due=$FullAtH|?{ $_ -le (UpH) -and -not $doneFull.ContainsKey("$_") }|Select -First 1
 if($null -ne $due){
   Emit ([ordered]@{event='full_begin';milestone_h=$due}); $nf=0;$ni=0
   foreach($c in $cpus){ Test-Cpu $c 'full' | Out-Null; $x=$script:last; if($x.verdict -eq 'FAULT'){Stop-Fault $x}; if($x.verdict -eq 'INVALID'){$ni++}; $nf++ }
   $doneFull["$due"]=1; Emit ([ordered]@{event='full_end';milestone_h=$due;cpus=$nf;invalid=$ni})
   if($due -ge $OnsetH -and $ni -eq 0){
     @{verdict='CLEAN';uptime_h=(UpH);onset_h=$OnsetH;ts=(Now)} | ConvertTo-Json | Set-Content "$r\done.json"
     Emit ([ordered]@{event='DONE_CLEAN'}); exit 0 }
 } else {
   foreach($c in 18,19){ Test-Cpu $c 'quick' | Out-Null; $x=$script:last; if($x.verdict -eq 'FAULT'){Stop-Fault $x} }
 }
 $left=($QuickMin*60)-((Get-Date)-$t0).TotalSeconds; if($left -gt 0){ Start-Sleep ([int]$left) }
}
