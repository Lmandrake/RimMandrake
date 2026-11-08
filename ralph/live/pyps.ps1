Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' } | ForEach-Object { "$($_.ProcessId) $($_.CommandLine)" }
