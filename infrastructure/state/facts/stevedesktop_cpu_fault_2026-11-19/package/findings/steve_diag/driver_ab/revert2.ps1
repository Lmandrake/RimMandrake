$m = @{Auto='auto';Manual='demand';System='system';Boot='boot';Disabled='disabled'}
$a = Get-Content C:\SteveDesktop\diag\driver_ab_original.json -Raw | ConvertFrom-Json
foreach ($s in @($a)) { foreach ($x in @($s)) { sc.exe config $x.Name start= $m[[string]$x.StartMode] | Out-Null; if ([string]$x.State -eq 'Running') { sc.exe start $x.Name | Out-Null }; "{0} -> {1} {2}" -f $x.Name,$x.StartMode,$x.State } }
Start-Sleep 5
"AT " + (Get-Date).ToUniversalTime().ToString("o")
Get-CimInstance Win32_Service | ? { $_.Name -match 'Corsair|iCUE|asComSvc|LightingService' } | select Name,State,StartMode | ft -auto | Out-String
Get-CimInstance Win32_SystemDriver | ? { $_.Name -match 'cpuz|CorsairLL' } | select Name,State,StartMode | ft -auto | Out-String
