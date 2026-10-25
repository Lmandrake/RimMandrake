# SteveDesktop status: one screen. Run from the desktop shortcut or `pwsh C:\SteveDesktop\status.ps1`.
$ErrorActionPreference='SilentlyContinue'
"== SteveDesktop status $(Get-Date -f 'yyyy-MM-dd HH:mm') =="
$b=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime; "uptime: {0}  (boot {1:yyyy-MM-dd HH:mm})" -f ((Get-Date)-$b).ToString('d\.hh\:mm'),$b
Get-PSDrive -PSProvider FileSystem | ? Used | % { "disk {0}: {1:N0} GB free of {2:N0}" -f $_.Name,($_.Free/1GB),(($_.Free+$_.Used)/1GB) }
"IPv4: " + ((Get-NetIPAddress -AddressFamily IPv4 | ? { $_.IPAddress -notmatch '^(127|169)' }).IPAddress -join ', ')
foreach($s in 'sshd','Tailscale','chromoting'){ "{0,-11} {1}" -f $s,(Get-Service $s).Status }
"steam: " + $(if(Get-Process steam){'running'}else{'NOT running'}) + "   RimWorld: " + $(if(Get-Process RimWorldWin64){'running'}else{'not running'})
"-- tailscale --"; & tailscale status 2>&1 | Select-Object -First 8
"-- WSL --"; $o=[Console]::OutputEncoding; [Console]::OutputEncoding=[Text.Encoding]::Unicode; wsl.exe -l -v; [Console]::OutputEncoding=$o
"wsl: " + (wsl.exe -d Ubuntu -u mandrake -- uptime -p) + "; systemd=" + (wsl.exe -d Ubuntu -u mandrake -- systemctl is-system-running)
"wsl free: " + (wsl.exe -d Ubuntu -u mandrake -- df -h --output=avail /)[1].Trim()
if(Test-Path 'C:\SteveDesktop\status.json'){ $j=Get-Content C:\SteveDesktop\status.json -Raw | ConvertFrom-Json; "bootstrap: see C:\SteveDesktop\status.json" }
