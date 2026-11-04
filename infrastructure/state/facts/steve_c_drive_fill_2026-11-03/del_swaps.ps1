$before=(Get-PSDrive C).Free
$T="$env:LOCALAPPDATA\Temp"; $live='D24F4874-4EA9-4455-91D5-315E438BD1AD'
Get-ChildItem -Force $T -Directory | ? { $_.Name -ne $live -and (Test-Path "$($_.FullName)\swap.vhdx") } | % {
  $n=$_.Name; $len=(Get-Item "$($_.FullName)\swap.vhdx" -Force).Length
  try { Remove-Item -LiteralPath $_.FullName -Recurse -Force -ErrorAction Stop; "DELETED $n $len" } catch { "KEPT $n $($_.Exception.Message)" } }
"freed_GB {0:N2}  C_free_GB {1:N2}" -f (((Get-PSDrive C).Free-$before)/1GB),((Get-PSDrive C).Free/1GB)
