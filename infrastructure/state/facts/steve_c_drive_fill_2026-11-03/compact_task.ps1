# Runs as SYSTEM: compact the (already shut down) WSL Ubuntu vhdx, then bring the seat tasks back.
$log='C:\SteveDesktop\diag\disk_fill\compact.log'
$v='C:\Users\sjlewis\AppData\Local\wsl\{353db0b6-87af-4664-8d81-cf3ae8581661}\ext4.vhdx'
function L($m){ "$(Get-Date -Format o) $m" | Add-Content $log }
try {
  L "start vhdx_GB $([math]::Round((Get-Item $v).Length/1GB,2)) C_free_GB $([math]::Round((Get-PSDrive C).Free/1GB,2))"
  $ds='C:\SteveDesktop\diag\disk_fill\compact.dp'
  "select vdisk file=`"$v`"`r`nattach vdisk readonly`r`ncompact vdisk`r`ndetach vdisk`r`n" | Set-Content -Encoding ASCII $ds
  $o = & diskpart /s $ds 2>&1; L ("diskpart exit $LASTEXITCODE :: " + (($o | ? { $_ -match '\S' }) -join ' | '))
  L "end vdhx_GB $([math]::Round((Get-Item $v).Length/1GB,2)) C_free_GB $([math]::Round((Get-PSDrive C).Free/1GB,2))"
} catch { L "ERROR $($_.Exception.Message)" }
finally {
  Enable-ScheduledTask 'Steve Seats Watch' | Out-Null
  Start-ScheduledTask 'WSL Keepalive'; Start-Sleep 20; Start-ScheduledTask 'Steve Seats Watch'
  L "tasks restored; DONE"
}
