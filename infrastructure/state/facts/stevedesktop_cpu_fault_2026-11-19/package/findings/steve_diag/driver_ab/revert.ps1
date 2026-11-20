$m = @{Auto='auto';Manual='demand';System='system';Boot='boot';Disabled='disabled'}
Get-Content C:\SteveDesktop\diag\driver_ab_original.json | ConvertFrom-Json | % { sc.exe config $_.Name start= $m[$_.StartMode] | Out-Null; if ($_.State -eq 'Running') { sc.exe start $_.Name | Out-Null }; "{0} -> {1}" -f $_.Name,$_.StartMode }
