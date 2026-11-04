$t=(Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$d=Get-PSDrive C
"{0} free_bytes={1} size_bytes={2}" -f $t,$d.Free,($d.Free+$d.Used)
$tmp="C:\Users\sjlewis\AppData\Local\Temp"
Get-ChildItem $tmp -Directory -EA SilentlyContinue | ? { Test-Path (Join-Path $_.FullName 'swap.vhdx') } | % { "swapdir {0} bytes={1}" -f $_.Name,(Get-Item (Join-Path $_.FullName 'swap.vhdx')).Length }
Get-ChildItem "C:\Users\sjlewis\AppData\Local\wsl" -Recurse -Filter ext4.vhdx -EA SilentlyContinue -Depth 2 | % { "ext4vhdx {0} bytes={1}" -f $_.FullName,$_.Length }
