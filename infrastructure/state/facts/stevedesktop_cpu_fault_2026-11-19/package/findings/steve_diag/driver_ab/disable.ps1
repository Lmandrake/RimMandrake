# driver A/B for STEVE_CRASHES_DIAGNOSE_DEFENDER_FALLS_TOO: disable MSR/IO-poking vendor callers. Revert: revert.ps1
$svcs = 'CorsairService','CorsairLLAService','iCUEDevicePluginHost','asComSvc','LightingService'
$drv  = 'CorsairLLAccessC2D033F14715AA7325305EA42FBFC65BF867CC1D','cpuz154'
$rec = @()
foreach ($n in $svcs + $drv) { $s = Get-CimInstance Win32_BaseService -Filter "Name='$n'"; if ($s) { $rec += [pscustomobject]@{Name=$n;StartMode=$s.StartMode;State=$s.State} } }
$rec | ConvertTo-Json | Set-Content C:\SteveDesktop\diag\driver_ab_original.json
foreach ($n in $svcs) { sc.exe config $n start= disabled | Out-Null; Stop-Service -Name $n -Force -EA SilentlyContinue }
Get-Process | ? { $_.Name -match '^(iCUE|Corsair\.Service.*|iCUEDevicePluginHost|LightingService|atkexComSvc)$' } | Stop-Process -Force -EA SilentlyContinue
Start-Sleep 3
foreach ($n in $drv) { sc.exe config $n start= disabled | Out-Null; sc.exe stop $n | Out-Null }
"at " + (Get-Date).ToUniversalTime().ToString('s') + "Z"
foreach ($n in $svcs + $drv) { $s = Get-CimInstance Win32_BaseService -Filter "Name='$n'"; "{0} {1} {2}" -f $n,$s.State,$s.StartMode }
Get-Process | ? { $_.Name -match 'Corsair|iCUE|Lighting|atkex' } | % { "STILL RUNNING " + $_.Name }
