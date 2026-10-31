# SteveDesktop bootstrap (Windows 10 Home or Pro). Run once; safe to run again.
#
# First command, typed in any PowerShell window on SteveDesktop (RUNBOOK.md step 1):
#     irm http://192.168.86.221:8767/b | iex
#
# What happens:
#   1. Stage: the script copies itself, bootstrap_wsl.sh and archmagi.pub into C:\SteveDesktop
#      (from the Archmagi server, or from the folder it sits in when run off a USB stick),
#      then relaunches itself elevated from that file (one UAC prompt).
#   2. Phase A (about 5 min): SSH door for Archmagi, then report IP/MAC to Archmagi.
#   3. Phase B (about 15 min): power, Windows Update, hostname, WSL features, winget
#      installs, Tailscale, scheduled tasks. Then asks to reboot.
#   4. Phase C (after the reboot, runs by itself at logon): Ubuntu, bootstrap_wsl.sh,
#      systemd services, final report.
#
# Log: C:\SteveDesktop\bootstrap.log    State: C:\SteveDesktop\status.json
# Every step is idempotent and records ok/fail in status.json; one failed step does not stop
# the rest. ASCII only: Windows PowerShell 5.1 reads a BOM-less .ps1 as ANSI.
# Deliberately NOT done, to avoid lockout: sshd_config is never edited (password login on the
# LAN stays as Windows ships it); no firewall rule is ever deleted; no account is changed.

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Root = 'C:\SteveDesktop'
$BaseUrl = 'http://192.168.86.221:8767'
if ($env:STEVE_BASE) { $BaseUrl = $env:STEVE_BASE }
$StageFiles = @('bootstrap.ps1', 'bootstrap_wsl.sh', 'archmagi.pub')
$WantName = 'SteveDesktop'
$TsHost = 'stevedesktop'
$ResumeTask = 'SteveDesktop Bootstrap Resume'
$LogFile = Join-Path $Root 'bootstrap.log'
$StatusFile = Join-Path $Root 'status.json'
$ScriptArgs = @($args)

function Invoke-Stage {
    # Runs when the script is NOT C:\SteveDesktop\bootstrap.ps1 (irm | iex, or a USB copy).
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    $here = $null
    if ($PSCommandPath) { $here = Split-Path -Parent $PSCommandPath }
    foreach ($f in $StageFiles) {
        $dest = Join-Path $Root $f
        $local = $null
        if ($here) { $local = Join-Path $here $f }
        if ($local -and (Test-Path -LiteralPath $local)) {
            Copy-Item -LiteralPath $local -Destination $dest -Force
        } else {
            Invoke-WebRequest -UseBasicParsing -Uri "$BaseUrl/$f" -OutFile $dest
        }
        Write-Host "staged $dest"
    }
    $argList = "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$Root\bootstrap.ps1`""
    Write-Host 'Relaunching elevated. Click YES on the User Account Control prompt.' -ForegroundColor Yellow
    Start-Process -FilePath 'powershell.exe' -Verb RunAs -ArgumentList $argList
}

function Invoke-Native([string]$exe, [string[]]$argv) {
    # Windows PowerShell 5.1 turns a native command's stderr into a terminating error when
    # $ErrorActionPreference is Stop; run natives under Continue and return their text.
    $old = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try { $o = & $exe @argv 2>&1 | Out-String } finally { $ErrorActionPreference = $old }
    return (($o -replace "`0", '').Trim())
}

# ---------------------------------------------------------------- logging and state
$script:Status = $null

function Write-Log([string]$msg) {
    $line = '{0} {1}' -f (Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'), $msg
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
    Write-Host $line
}

function Get-StatusObject {
    if (Test-Path -LiteralPath $StatusFile) {
        try {
            $o = Get-Content -LiteralPath $StatusFile -Raw | ConvertFrom-Json
            $h = @{ steps = @{}; facts = @{} }
            if ($o.steps) { foreach ($p in $o.steps.PSObject.Properties) { $h.steps[$p.Name] = $p.Value } }
            if ($o.facts) { foreach ($p in $o.facts.PSObject.Properties) { $h.facts[$p.Name] = $p.Value } }
            if ($o.phase) { $h.phase = $o.phase }
            return $h
        } catch { Write-Log "status.json unreadable, starting fresh: $($_.Exception.Message)" }
    }
    return @{ steps = @{}; facts = @{}; phase = 'new' }
}

function Save-Status {
    $script:Status.updated_utc = (Get-Date).ToUniversalTime().ToString('o')
    $json = $script:Status | ConvertTo-Json -Depth 6
    [System.IO.File]::WriteAllText($StatusFile, $json, (New-Object System.Text.UTF8Encoding($false)))
}

function Invoke-Step([string]$name, [scriptblock]$body) {
    Write-Log "STEP $name ..."
    try {
        $detail = & $body
        if ($null -eq $detail) { $detail = 'ok' }
        $script:Status.steps[$name] = @{ ok = $true; detail = ([string]($detail -join '; ')); utc = (Get-Date).ToUniversalTime().ToString('o') }
        Write-Log "  OK   $name : $detail"
    } catch {
        $script:Status.steps[$name] = @{ ok = $false; detail = $_.Exception.Message; utc = (Get-Date).ToUniversalTime().ToString('o') }
        Write-Log "  FAIL $name : $($_.Exception.Message)"
    }
    Save-Status
}

function Send-Report([string]$why) {
    $script:Status.facts.report_reason = $why
    Save-Status
    try {
        # Send the file's own bytes: PS 5.1 re-encodes a string -Body as Latin-1, so any non-ASCII
        # step detail (a mangled arrow from a tool's output) reached serve_bootstrap.py as invalid
        # UTF-8 and the final report got 400 'not json' (STEVEDESKTOP_REPORT_FIX_FINAL_POST_REFUSED).
        $body = [IO.File]::ReadAllBytes($StatusFile)
        Invoke-RestMethod -UseBasicParsing -Method Post -Uri "$BaseUrl/report" -Body $body -ContentType 'application/json; charset=utf-8' -TimeoutSec 10 | Out-Null
        Write-Log "report sent to $BaseUrl ($why)"
    } catch {
        Write-Log "report NOT sent ($why): $($_.Exception.Message). Archmagi can read $StatusFile over SSH instead."
    }
}

function Test-Admin {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    return (New-Object Security.Principal.WindowsPrincipal($id)).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# ---------------------------------------------------------------- facts
function Get-PrimaryAdapter {
    $route = Get-NetRoute -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue | Sort-Object RouteMetric | Select-Object -First 1
    if ($route) { return Get-NetAdapter -InterfaceIndex $route.InterfaceIndex }
    return Get-NetAdapter -Physical | Where-Object Status -eq 'Up' | Select-Object -First 1
}

function Get-Facts {
    $f = $script:Status.facts
    $cv = Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
    $f.computer_name = $env:COMPUTERNAME
    $f.user = $env:USERNAME
    $f.user_domain = $env:USERDOMAIN
    $f.edition_id = $cv.EditionID
    $f.product_name = $cv.ProductName
    $f.display_version = $cv.DisplayVersion
    $f.build = '{0}.{1}' -f $cv.CurrentBuild, $cv.UBR
    $f.is_home = ($cv.EditionID -match '^Core')
    $ad = Get-PrimaryAdapter
    if ($ad) {
        $ip = Get-NetIPAddress -InterfaceIndex $ad.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue | Select-Object -First 1
        $f.lan_ip = $ip.IPAddress
        $f.lan_prefix = $ip.PrefixLength
        $f.mac = $ad.MacAddress
        $f.adapter = $ad.Name
        $f.adapter_desc = $ad.InterfaceDescription
        $f.adapter_media = [string]$ad.NdisPhysicalMedium
        $f.wired = -not ($ad.InterfaceDescription -match 'Wi-?Fi|Wireless|802\.11|WLAN')
        $f.link_speed = $ad.LinkSpeed
    }
    $cs = Get-CimInstance Win32_ComputerSystem
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $bios = Get-CimInstance Win32_BIOS
    $bb = Get-CimInstance Win32_BaseBoard
    $f.ram_gb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
    $f.cpu = $cpu.Name
    $f.cores = $cpu.NumberOfCores
    $f.gpu = @(Get-CimInstance Win32_VideoController | ForEach-Object { $_.Name }) -join ' | '
    $f.board = '{0} {1}' -f $bb.Manufacturer, $bb.Product
    $f.bios = '{0} {1}' -f $bios.Manufacturer, $bios.SMBIOSBIOSVersion
    $f.disks = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object {
        '{0} {1:N0}GB free of {2:N0}GB' -f $_.DeviceID, ($_.FreeSpace / 1GB), ($_.Size / 1GB) }) -join ' | '
    $f.virtualization_fw = [string]$cpu.VirtualizationFirmwareEnabled
    $f.utc = (Get-Date).ToUniversalTime().ToString('o')
    return "$($f.lan_ip) $($f.mac) $($f.edition_id) build $($f.build)"
}

function Get-SteamReport {
    $f = $script:Status.facts
    $steam = $null
    foreach ($k in @('HKCU:\Software\Valve\Steam', 'HKLM:\SOFTWARE\WOW6432Node\Valve\Steam')) {
        $p = Get-ItemProperty -Path $k -ErrorAction SilentlyContinue
        if ($p -and $p.SteamPath) { $steam = $p.SteamPath; break }
        if ($p -and $p.InstallPath) { $steam = $p.InstallPath; break }
    }
    if (-not $steam) { $f.steam = 'NOT FOUND'; return 'steam not found' }
    $steam = $steam -replace '/', '\'
    $f.steam = $steam
    $libs = @($steam)
    $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
    if (Test-Path -LiteralPath $vdf) {
        foreach ($m in [regex]::Matches((Get-Content -LiteralPath $vdf -Raw), '"path"\s+"([^"]+)"')) {
            $libs += ($m.Groups[1].Value -replace '\\\\', '\')
        }
    }
    $libs = $libs | Select-Object -Unique
    foreach ($lib in $libs) {
        $rw = Join-Path $lib 'steamapps\common\RimWorld'
        if (Test-Path -LiteralPath $rw) {
            $f.rimworld = $rw
            $data = Join-Path $rw 'Data'
            if (Test-Path -LiteralPath $data) {
                $f.rimworld_data_folders = @(Get-ChildItem -LiteralPath $data -Directory | ForEach-Object { $_.Name }) -join ','
            }
            $ver = Join-Path $rw 'Version.txt'
            if (Test-Path -LiteralPath $ver) { $f.rimworld_version = (Get-Content -LiteralPath $ver -TotalCount 1) }
            $acf = Join-Path $lib 'steamapps\appmanifest_294100.acf'
            if (Test-Path -LiteralPath $acf) {
                $txt = Get-Content -LiteralPath $acf -Raw
                $f.rimworld_installed_depots = @([regex]::Matches($txt, '"(\d{6,})"\s*\{\s*"manifest"') | ForEach-Object { $_.Groups[1].Value }) -join ','
                $m = [regex]::Match($txt, '"AutoUpdateBehavior"\s+"(\d+)"')
                if ($m.Success) { $f.rimworld_auto_update_behavior = $m.Groups[1].Value }
            }
            return "RimWorld at $rw; Data folders: $($f.rimworld_data_folders)"
        }
    }
    $f.rimworld = 'NOT FOUND in ' + ($libs -join ';')
    return $f.rimworld
}

# ---------------------------------------------------------------- phase A: SSH door
function Install-Sshd {
    $svc = Get-Service sshd -ErrorAction SilentlyContinue
    if (-not $svc) {
        $cap = Get-WindowsCapability -Online -Name 'OpenSSH.Server*' | Select-Object -First 1
        if ($cap -and $cap.State -ne 'Installed') {
            Write-Log '  adding Windows capability OpenSSH.Server (2-5 min, needs Windows Update reachable)'
            try { Add-WindowsCapability -Online -Name $cap.Name | Out-Null }
            catch { Write-Log "  capability failed: $($_.Exception.Message); trying winget Microsoft.OpenSSH.Preview" }
        }
        $svc = Get-Service sshd -ErrorAction SilentlyContinue
        if (-not $svc) {
            Install-WingetPackage 'Microsoft.OpenSSH.Preview' | Out-Null
            $svc = Get-Service sshd -ErrorAction SilentlyContinue
        }
        if (-not $svc) { throw 'sshd service still missing after capability and winget' }
    }
    Set-Service -Name sshd -StartupType Automatic
    # Recovery: restart sshd if it ever crashes.
    Invoke-Native 'sc.exe' @('failure', 'sshd', 'reset=', '86400', 'actions=', 'restart/5000/restart/5000/restart/30000') | Out-Null
    if ((Get-Service sshd).Status -ne 'Running') { Start-Service sshd }
    New-Item -Path 'HKLM:\SOFTWARE\OpenSSH' -Force | Out-Null
    New-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -PropertyType String -Force `
        -Value "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" | Out-Null
    return "sshd $((Get-Service sshd).Status), DefaultShell=powershell"
}

function Install-ArchmagiKey {
    $pubPath = Join-Path $Root 'archmagi.pub'
    $key = (Get-Content -LiteralPath $pubPath -TotalCount 1).Trim()
    if ($key -notmatch '^ssh-(ed25519|rsa) ') { throw "archmagi.pub does not look like a public key" }
    $done = @()
    # Administrators read C:\ProgramData\ssh\administrators_authorized_keys (sshd_config default).
    $adminFile = Join-Path $env:ProgramData 'ssh\administrators_authorized_keys'
    New-Item -ItemType Directory -Force -Path (Split-Path $adminFile) | Out-Null
    $existing = @()
    if (Test-Path -LiteralPath $adminFile) { $existing = @(Get-Content -LiteralPath $adminFile) }
    if ($existing -notcontains $key) { Add-Content -LiteralPath $adminFile -Value $key -Encoding ASCII; $done += 'added admin key' }
    else { $done += 'admin key present' }
    # sshd refuses the file unless only Administrators and SYSTEM can write it. SIDs, not names,
    # so a non-English Windows works too.
    $ic = Invoke-Native 'icacls.exe' @($adminFile, '/inheritance:r', '/grant', '*S-1-5-32-544:F', '/grant', '*S-1-5-18:F')
    if ($LASTEXITCODE -ne 0) { throw "icacls failed: $ic" }
    # Also the per-user file, used if this account is ever not an administrator.
    $userSsh = Join-Path $env:USERPROFILE '.ssh'
    New-Item -ItemType Directory -Force -Path $userSsh | Out-Null
    $userFile = Join-Path $userSsh 'authorized_keys'
    $ue = @()
    if (Test-Path -LiteralPath $userFile) { $ue = @(Get-Content -LiteralPath $userFile) }
    if ($ue -notcontains $key) { Add-Content -LiteralPath $userFile -Value $key -Encoding ASCII; $done += 'added user key' }
    return ($done -join ', ')
}

function Set-PrivateNetwork {
    $p = Get-NetConnectionProfile | Where-Object { $_.IPv4Connectivity -eq 'Internet' }
    $out = @()
    foreach ($x in $p) {
        if ($x.NetworkCategory -eq 'Public') { Set-NetConnectionProfile -InterfaceIndex $x.InterfaceIndex -NetworkCategory Private }
        $out += "$($x.InterfaceAlias)=Private"
    }
    return ($out -join ', ')
}

# LAN + Tailscale only. LocalSubnet covers 192.168.86.0/24; 100.64.0.0/10 and fd7a:115c:a1e0::/48
# are Tailscale's address ranges.
$TaskUserSid = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value  # SID: survives the pending hostname rename
$AllowedRemote = @('LocalSubnet', '192.168.86.0/24', '100.64.0.0/10', 'fd7a:115c:a1e0::/48')

function Set-SshFirewall {
    $rule = Get-NetFirewallRule -Name 'OpenSSH-Server-In-TCP' -ErrorAction SilentlyContinue
    if (-not $rule) {
        $rule = Get-NetFirewallRule -Name 'SteveDesktop-SSH-In' -ErrorAction SilentlyContinue
        if (-not $rule) {
            New-NetFirewallRule -Name 'SteveDesktop-SSH-In' -DisplayName 'SteveDesktop SSH (LAN+Tailscale)' `
                -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow -Profile Any -RemoteAddress $AllowedRemote | Out-Null
            return 'created SteveDesktop-SSH-In'
        }
    }
    $rule | Set-NetFirewallRule -Enabled True -Profile Any -RemoteAddress $AllowedRemote
    return "$($rule.Name): LAN+Tailscale only, all profiles"
}

function Show-Banner([string]$title, [string]$color) {
    $f = $script:Status.facts
    Write-Host ''
    Write-Host ('=' * 64) -ForegroundColor $color
    Write-Host "  $title" -ForegroundColor $color
    Write-Host "  IP   : $($f.lan_ip)      MAC : $($f.mac)" -ForegroundColor $color
    Write-Host "  user : $($f.user)        edition : $($f.edition_id) ($($f.build))" -ForegroundColor $color
    Write-Host "  wired: $($f.wired)  ($($f.adapter_desc))" -ForegroundColor $color
    Write-Host ('=' * 64) -ForegroundColor $color
    Write-Host ''
}

# ---------------------------------------------------------------- phase B
function Set-PowerPolicy {
    Invoke-Native 'powercfg.exe' @('/change', 'standby-timeout-ac', '0') | Out-Null
    Invoke-Native 'powercfg.exe' @('/change', 'hibernate-timeout-ac', '0') | Out-Null
    Invoke-Native 'powercfg.exe' @('/change', 'monitor-timeout-ac', '30') | Out-Null
    # Also disables Fast Startup, which breaks Wake-on-LAN from power-off on many boards.
    Invoke-Native 'powercfg.exe' @('/hibernate', 'off') | Out-Null
    # Unattended-sleep timeout (hidden setting) to 0 as well.
    Invoke-Native 'powercfg.exe' @('/setacvalueindex', 'SCHEME_CURRENT', 'SUB_SLEEP', '7bc4a2f9-d8fc-4469-b07b-33eb785aaca0', '0') | Out-Null
    Invoke-Native 'powercfg.exe' @('/setactive', 'SCHEME_CURRENT') | Out-Null
    $q = Invoke-Native 'powercfg.exe' @('/query', 'SCHEME_CURRENT', 'SUB_SLEEP', 'STANDBYIDLE')
    if ($q -notmatch 'Current AC Power Setting Index:\s*0x00000000') { return 'set; could not confirm standby AC = 0 (non-English Windows?)' }
    return 'never sleep/hibernate on AC, fast startup off'
}

function Set-WakeOnLan {
    $out = @()
    foreach ($ad in @(Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' })) {
        # Every change uses -NoRestart and only when the value differs: a NIC restart would drop the
        # SSH session an agent may be repairing from. The changes take effect at the next reboot.
        try {
            $pm = Get-NetAdapterPowerManagement -Name $ad.Name -ErrorAction Stop
            if ([string]$pm.WakeOnMagicPacket -eq 'Enabled') { $out += "$($ad.Name): magic packet already on" }
            else { Set-NetAdapterPowerManagement -Name $ad.Name -WakeOnMagicPacket Enabled -NoRestart -ErrorAction Stop; $out += "$($ad.Name): magic packet on (at next reboot)" }
        } catch { $out += "$($ad.Name): WakeOnMagicPacket not settable ($($_.Exception.Message))" }
        foreach ($prop in @('Wake on Magic Packet', 'Wake on magic packet', 'Shutdown Wake-On-Lan', 'Shutdown Wake Up')) {
            $cur = Get-NetAdapterAdvancedProperty -Name $ad.Name -DisplayName $prop -ErrorAction SilentlyContinue
            if ($cur -and $cur.DisplayValue -ne 'Enabled') {
                Set-NetAdapterAdvancedProperty -Name $ad.Name -DisplayName $prop -DisplayValue 'Enabled' -NoRestart -ErrorAction SilentlyContinue
                $out += "$($ad.Name): '$prop' Enabled (at next reboot)"
            }
        }
        Invoke-Native 'powercfg.exe' @('/deviceenablewake', $ad.InterfaceDescription) | Out-Null
    }
    if (-not $script:Status.facts.wired) { $out += 'WARNING: primary adapter is Wi-Fi; Wake-on-LAN from power-off will not work' }
    return ($out -join '; ')
}

function Set-UpdatePolicy {
    # Still downloads and installs updates; only the restart is held while a user is logged on
    # (autologon keeps one logged on). Agents reboot it on purpose; RUNBOOK "survives the week".
    $au = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU'
    $wu = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate'
    New-Item -Path $au -Force | Out-Null
    # NoAutoRebootWithLoggedOnUsers is honoured only with AUOptions=4 (auto download, scheduled install).
    New-ItemProperty -Path $au -Name NoAutoUpdate -PropertyType DWord -Value 0 -Force | Out-Null
    New-ItemProperty -Path $au -Name AUOptions -PropertyType DWord -Value 4 -Force | Out-Null
    New-ItemProperty -Path $au -Name ScheduledInstallDay -PropertyType DWord -Value 0 -Force | Out-Null
    New-ItemProperty -Path $au -Name ScheduledInstallTime -PropertyType DWord -Value 3 -Force | Out-Null
    New-ItemProperty -Path $au -Name NoAutoRebootWithLoggedOnUsers -PropertyType DWord -Value 1 -Force | Out-Null
    New-ItemProperty -Path $wu -Name SetActiveHours -PropertyType DWord -Value 1 -Force | Out-Null
    New-ItemProperty -Path $wu -Name ActiveHoursStart -PropertyType DWord -Value 7 -Force | Out-Null
    New-ItemProperty -Path $wu -Name ActiveHoursEnd -PropertyType DWord -Value 1 -Force | Out-Null
    $ux = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
    New-Item -Path $ux -Force | Out-Null
    New-ItemProperty -Path $ux -Name ActiveHoursStart -PropertyType DWord -Value 7 -Force | Out-Null
    New-ItemProperty -Path $ux -Name ActiveHoursEnd -PropertyType DWord -Value 1 -Force | Out-Null
    New-ItemProperty -Path $ux -Name SmartActiveHoursState -PropertyType DWord -Value 0 -Force | Out-Null
    $note = 'AUOptions 4 (daily 03:00 install), active hours 07-01, no auto-restart while logged on'
    if ($script:Status.facts.is_home) { $note += ' (Home edition: Group Policy keys are not honoured there; autologon is the recovery path)' }
    return $note
}

function Set-Hostname {
    if ($env:COMPUTERNAME -ieq $WantName) { return "already $WantName" }
    $pending = (Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName').ComputerName
    if ($pending -ieq $WantName) { $script:Status.facts.reboot_needed = $true; return "rename to $WantName pending reboot" }
    Rename-Computer -NewName $WantName -Force
    $script:Status.facts.reboot_needed = $true
    return "renamed $($env:COMPUTERNAME) -> $WantName (takes effect at reboot)"
}

function Enable-WslFeatures {
    $build = [int]((Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion').CurrentBuild)
    if ($build -lt 19041) { throw "Windows build $build is older than 19041 (2004); WSL2 needs a Windows feature update first" }
    $out = @()
    foreach ($feat in @('Microsoft-Windows-Subsystem-Linux', 'VirtualMachinePlatform')) {
        $st = (Get-WindowsOptionalFeature -Online -FeatureName $feat).State
        if ($st -ne 'Enabled') {
            $r = Enable-WindowsOptionalFeature -Online -FeatureName $feat -All -NoRestart
            if ($r.RestartNeeded) { $script:Status.facts.reboot_needed = $true }
            $out += "$feat enabled"
        } else { $out += "$feat already" }
    }
    return ($out -join ', ')
}

function Get-WingetPath {
    $cmd = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $cand = Get-ChildItem "$env:ProgramFiles\WindowsApps\Microsoft.DesktopAppInstaller_*_x64__8wekyb3d8bbwe\winget.exe" -ErrorAction SilentlyContinue |
        Sort-Object FullName -Descending | Select-Object -First 1
    if ($cand) { return $cand.FullName }
    return $null
}

function Initialize-Winget {
    $w = Get-WingetPath
    if (-not $w) {
        try { Add-AppxPackage -RegisterByFamilyName -MainPackage Microsoft.DesktopAppInstaller_8wekyb3d8bbwe } catch { }
        $w = Get-WingetPath
    }
    if ($w) { Invoke-Native $w @('--info') | Out-Null; if ($LASTEXITCODE -ne 0) { $w = $null } }
    if (-not $w) {
        # Microsoft's documented bootstrap: it installs the bundle with its framework dependencies.
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force -Scope AllUsers | Out-Null
        Install-Module -Name Microsoft.WinGet.Client -Force -Scope AllUsers -Repository PSGallery -AllowClobber | Out-Null
        Import-Module Microsoft.WinGet.Client
        Repair-WinGetPackageManager -AllUsers -Force -Latest | Out-Null
        $w = Get-WingetPath
    }
    if ($w) { Invoke-Native $w @('--info') | Out-Null; if ($LASTEXITCODE -ne 0) { $w = $null } }
    if (-not $w) { throw 'winget unavailable (winget --info fails); agents install it over SSH later' }
    $script:Winget = $w
    Invoke-Native $w @('source', 'update') | Out-Null
    return $w
}

function Install-WingetPackage([string]$id, [string]$override) {
    if (-not $script:Winget) { Initialize-Winget | Out-Null }
    Invoke-Native $script:Winget @('list', '--id', $id, '--exact', '--accept-source-agreements') | Out-Null
    if ($LASTEXITCODE -eq 0) { return "$id already installed" }
    $a = @('install', '--id', $id, '--exact', '--source', 'winget', '--silent', '--accept-package-agreements', '--accept-source-agreements')
    if ($override) { $a += @('--override', $override) }
    $o = Invoke-Native $script:Winget $a
    $code = $LASTEXITCODE
    Add-Content -LiteralPath (Join-Path $Root 'winget.log') -Value "=== $id exit=$code`r`n$o"
    if ($code -ne 0) {
        Invoke-Native $script:Winget @('list', '--id', $id, '--exact', '--accept-source-agreements') | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "winget install $id exit $code (see winget.log)" }
    }
    return "$id installed"
}

function Install-Autologon {
    $dir = Join-Path $Root 'tools'
    $exe = Join-Path $dir 'Autologon64.exe'
    # Autologon cannot use a Microsoft account if Windows Hello-only sign-in is enforced.
    $pl = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PasswordLess\Device'
    if (Test-Path $pl) { New-ItemProperty -Path $pl -Name DevicePasswordLessBuildVersion -PropertyType DWord -Value 0 -Force | Out-Null }
    if (Test-Path -LiteralPath $exe) { return "present $exe" }
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $zip = Join-Path $dir 'AutoLogon.zip'
    Invoke-WebRequest -UseBasicParsing -Uri 'https://download.sysinternals.com/files/AutoLogon.zip' -OutFile $zip
    Expand-Archive -LiteralPath $zip -DestinationPath $dir -Force
    return "unpacked to $dir (owner runs it: RUNBOOK step 7)"
}

function Get-TailscaleExe {
    foreach ($p in @("$env:ProgramFiles\Tailscale\tailscale.exe", "${env:ProgramFiles(x86)}\Tailscale\tailscale.exe")) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    return $null
}

function Start-TailscaleLogin {
    $ts = Get-TailscaleExe
    if (-not $ts) { throw 'tailscale.exe not found' }
    $st = $null
    try { $st = Invoke-Native $ts @('status', '--json') | ConvertFrom-Json } catch { }
    if ($st -and $st.BackendState -eq 'Running') {
        Invoke-Native $ts @('set', '--unattended=true') | Out-Null
        $script:Status.facts.tailscale_ip = ((Invoke-Native $ts @('ip', '-4')) -split "`n")[0].Trim()
        return "already logged in as $($st.Self.HostName) $($script:Status.facts.tailscale_ip)"
    }
    # --unattended keeps Tailscale up when nobody is logged on (needed after a reboot).
    Invoke-Native $ts @('up', '--unattended', "--hostname=$TsHost", '--timeout=20s') | Out-Null
    try { $st = Invoke-Native $ts @('status', '--json') | ConvertFrom-Json } catch { }
    if ($st -and $st.AuthURL) {
        $script:Status.facts.tailscale_auth_url = $st.AuthURL
        Start-Process $st.AuthURL
        return "login page opened: $($st.AuthURL)"
    }
    return "state $($st.BackendState); open the Tailscale tray icon and choose Log in"
}

function Enable-RdpIfPro {
    if ($script:Status.facts.is_home) { return 'Home edition: no RDP server; Chrome Remote Desktop is the GUI door' }
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
    Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server\WinStations\RDP-Tcp' -Name UserAuthentication -Value 1
    $rules = Get-NetFirewallRule -Group '@FirewallAPI.dll,-28752' -ErrorAction SilentlyContinue
    if ($rules) { $rules | Set-NetFirewallRule -Enabled True -RemoteAddress $AllowedRemote }
    return 'RDP on (NLA), firewall LAN+Tailscale only'
}

function Register-KeepaliveTask {
    # Mirrors Archmagi's "\WSL Keepalive": logon trigger, InteractiveToken, wscript.exe running a
    # .vbs that starts "sleep infinity" in Ubuntu with no console window, IgnoreNew, no time limit,
    # runs on battery.
    $vbs = Join-Path $Root 'wsl_keepalive.vbs'
    $vbsText = @(
        "' wsl_keepalive.vbs - keeps the Ubuntu WSL distro (systemd, tailscaled, sshd) running after logon.",
        "' Window style 0: a bare wsl.exe in a scheduled task flashes a console.",
        'CreateObject("WScript.Shell").Run "wsl.exe -d Ubuntu --exec /bin/sh -c ""exec sleep infinity""", 0, False'
    )
    Set-Content -LiteralPath $vbs -Value $vbsText -Encoding ASCII
    $action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument "`"$vbs`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $TaskUserSid -LogonType Interactive
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName 'WSL Keepalive' -TaskPath '\' -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings -Description 'SteveDesktop: keeps WSL (systemd, tailscaled) alive after logon. Copy of Archmagi design.' -Force | Out-Null
    return 'registered \WSL Keepalive'
}

function Register-FleetTask {
    # STEVE_SEATS_FIX_DIE_ON_REBOOT: returns the two Claude seats after every logon. claude_fleet.ps1 comes from
    # claude-remote-control accounts/install.sh; -Logon waits for WSL and the network, and is idempotent.
    $ps = Join-Path $Root 'claude_fleet.ps1'
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' `
        -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps`" -Logon"
    $trigger = New-ScheduledTaskTrigger -AtLogOn -User $TaskUserSid
    $trigger.Delay = 'PT15S'
    $principal = New-ScheduledTaskPrincipal -UserId $TaskUserSid -LogonType Interactive
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
        -ExecutionTimeLimit (New-TimeSpan -Minutes 20) -MultipleInstances IgnoreNew
    Register-ScheduledTask -TaskName 'Claude Fleet' -TaskPath '\' -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings -Description 'SteveDesktop: returns the two Claude seats after every logon.' -Force | Out-Null
    return 'registered \Claude Fleet'
}

function Register-SelfUpgradeTask {
    $ps = Join-Path $Root 'selfupgrade_windows.ps1'
    $body = @(
        '# Weekly Windows-side self-upgrade (registered by bootstrap.ps1). Log: C:\SteveDesktop\selfupgrade.log',
        '$log = "C:\SteveDesktop\selfupgrade.log"',
        'if ((Test-Path $log) -and ((Get-Item $log).Length -gt 5MB)) { Move-Item $log "$log.old" -Force }',
        '$w = (Get-Command winget.exe -ErrorAction SilentlyContinue).Source',
        'if (-not $w) { $w = (Get-ChildItem "$env:ProgramFiles\WindowsApps\Microsoft.DesktopAppInstaller_*_x64__8wekyb3d8bbwe\winget.exe" -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -First 1).FullName }',
        '$t0 = (Get-Date).ToUniversalTime().ToString("o")',
        'Add-Content $log "=== $t0 winget upgrade --all"',
        '$o = & $w upgrade --all --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-String',
        '$rc = $LASTEXITCODE',
        'Add-Content $log $o',
        '$stamp = @{ utc = $t0; winget_exit = $rc } | ConvertTo-Json',
        '[IO.File]::WriteAllText("C:\SteveDesktop\last_selfupgrade_windows.json", $stamp)'
    )
    Set-Content -LiteralPath $ps -Value $body -Encoding ASCII
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$ps`""
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '04:30'
    $principal = New-ScheduledTaskPrincipal -UserId $TaskUserSid -LogonType Interactive -RunLevel Highest
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 2)
    Register-ScheduledTask -TaskName 'SteveDesktop SelfUpgrade' -TaskPath '\' -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings -Description 'winget upgrade --all, weekly' -Force | Out-Null
    return 'registered \SteveDesktop SelfUpgrade (Sun 04:30)'
}

function Enable-StorageSense {
    $k = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\StorageSense\Parameters\StoragePolicy'
    New-Item -Path $k -Force | Out-Null
    New-ItemProperty -Path $k -Name '01' -PropertyType DWord -Value 1 -Force | Out-Null     # on
    New-ItemProperty -Path $k -Name '2048' -PropertyType DWord -Value 7 -Force | Out-Null   # run weekly
    New-ItemProperty -Path $k -Name '04' -PropertyType DWord -Value 1 -Force | Out-Null     # temp files
    New-ItemProperty -Path $k -Name '256' -PropertyType DWord -Value 14 -Force | Out-Null   # recycle bin 14 d
    return 'Storage Sense weekly'
}

function Register-ResumeTask {
    $action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$Root\bootstrap.ps1`" -Resume"
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $TaskUserSid -LogonType Interactive -RunLevel Highest
    Register-ScheduledTask -TaskName $ResumeTask -TaskPath '\' -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
    return 'resume task registered for next logon'
}

# ---------------------------------------------------------------- phase C: WSL
function Invoke-Wsl([string[]]$wslArgs) {
    $env:WSL_UTF8 = '1'
    return (Invoke-Native 'wsl.exe' $wslArgs)
}

function Install-Ubuntu {
    $o = Invoke-Wsl @('--update')
    Write-Log "  wsl --update (exit $LASTEXITCODE): $o"
    $ver = Invoke-Wsl @('--version')
    if ($LASTEXITCODE -ne 0) {
        $o = Invoke-Wsl @('--update', '--web-download')
        Write-Log "  wsl --update --web-download (exit $LASTEXITCODE): $o"
        $ver = Invoke-Wsl @('--version')
    }
    if ($LASTEXITCODE -ne 0 -or $ver -notmatch 'WSL[^:]*:\s*(\d+)\.(\d+)\.(\d+)') {
        throw "WSL is the old inbox version (wsl --version fails). Install the latest Windows updates (Win10 22H2 with KB5020030 or newer), reboot, rerun. Output: $ver"
    }
    $wv = [version]('{0}.{1}.{2}' -f $Matches[1], $Matches[2], $Matches[3])
    $script:Status.facts.wsl_version = [string]$wv
    if ($wv -lt [version]'0.67.6') { throw "WSL $wv is older than 0.67.6 (no systemd); wsl --update did not take" }
    Invoke-Wsl @('--set-default-version', '2') | Out-Null
    $list = Invoke-Wsl @('-l', '-q')
    if ($list -match '(?m)^Ubuntu\s*$') {
        $lv = Invoke-Wsl @('-l', '-v')
        if ($lv -match '(?m)^\*?\s*Ubuntu\s+\S+\s+1\s*$') {
            Invoke-Wsl @('--set-version', 'Ubuntu', '2') | Out-Null
            if ($LASTEXITCODE -ne 0) { throw 'Ubuntu is WSL1 and wsl --set-version Ubuntu 2 failed' }
            return 'Ubuntu converted WSL1 -> WSL2'
        }
        return "Ubuntu already registered (WSL $wv)"
    }
    $o = Invoke-Wsl @('--install', '-d', 'Ubuntu', '--no-launch')
    Write-Log "  wsl --install (exit $LASTEXITCODE): $o"
    $list = Invoke-Wsl @('-l', '-q')
    if ($list -notmatch '(?m)^Ubuntu\s*$') {
        # Older Store-package Ubuntu registers only when its launcher runs; --root skips the
        # interactive user prompt (bootstrap_wsl.sh creates the user).
        $u = Get-Command ubuntu.exe -ErrorAction SilentlyContinue
        if ($u) { Invoke-Native $u.Source @('install', '--root') | Out-Null }
        $list = Invoke-Wsl @('-l', '-q')
    }
    if ($list -notmatch '(?m)^Ubuntu\s*$') { throw "Ubuntu not registered; wsl -l says: $list" }
    Invoke-Wsl @('--set-default', 'Ubuntu') | Out-Null
    return 'Ubuntu registered'
}

function Invoke-WslBootstrap([string]$pass) {
    $o = Invoke-Wsl @('-d', 'Ubuntu', '-u', 'root', '--', 'bash', '/mnt/c/SteveDesktop/bootstrap_wsl.sh', $pass)
    Add-Content -LiteralPath (Join-Path $Root 'bootstrap_wsl.out.log') -Value "=== pass $pass`r`n$o"
    $tail = ($o -split "`n" | Select-Object -Last 6) -join ' / '
    if ($o -notmatch 'BOOTSTRAP_WSL_DONE') { throw "bootstrap_wsl.sh pass $pass did not finish: $tail" }
    $m = [regex]::Match($o, 'TAILSCALE_WSL_LOGIN_URL: (\S+)')
    if ($m.Success) {
        $script:Status.facts.tailscale_wsl_auth_url = $m.Groups[1].Value
        Start-Process $m.Groups[1].Value
        Write-Host "Tailscale (WSL node) login page opened: $($m.Groups[1].Value)" -ForegroundColor Yellow
    }
    $k = [regex]::Match($o, 'WSL_PUBKEY: (ssh-ed25519 \S+ \S+)')
    if ($k.Success) { $script:Status.facts.wsl_pubkey = $k.Groups[1].Value }
    return $tail
}

function Get-WslFacts {
    $f = $script:Status.facts
    $f.wsl_ip = Invoke-Wsl @('-d', 'Ubuntu', '--', 'hostname', '-I')
    $f.wsl_pubkey = Invoke-Wsl @('-d', 'Ubuntu', '-u', 'mandrake', '--', 'cat', '/home/mandrake/.ssh/id_ed25519.pub')
    $f.wsl_tailscale = Invoke-Wsl @('-d', 'Ubuntu', '-u', 'root', '--', 'sh', '-c', 'tailscale ip -4 2>/dev/null || echo not-logged-in')
    return "wsl ip $($f.wsl_ip); ts $($f.wsl_tailscale)"
}

# ---------------------------------------------------------------- main
function Invoke-Main {
    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    if (-not (Test-Admin)) { throw 'not elevated: run it again and click Yes on the UAC prompt' }
    $script:Status = Get-StatusObject
    $resume = $ScriptArgs -contains '-Resume'
    Write-Log "==== bootstrap start (resume=$resume, phase=$($script:Status.phase))"

    # After a reboot the resume task can fire before the network is up.
    for ($i = 0; $i -lt 24; $i++) {
        try { [void][Net.Dns]::GetHostEntry('download.sysinternals.com'); break } catch { Start-Sleep -Seconds 5 }
    }
    Invoke-Step 'facts' { Get-Facts }
    # Phase A: SSH first, so Archmagi has a door within minutes.
    Invoke-Step 'network_private' { Set-PrivateNetwork }
    Invoke-Step 'sshd' { Install-Sshd }
    Invoke-Step 'ssh_key' { Install-ArchmagiKey }
    Invoke-Step 'ssh_firewall' { Set-SshFirewall }
    Invoke-Step 'steam_report' { Get-SteamReport }
    $script:Status.phase = 'A_done'
    Send-Report 'ssh_ready'
    if ($script:Status.steps['sshd'].ok -and $script:Status.steps['ssh_key'].ok -and $script:Status.steps['ssh_firewall'].ok) {
        Show-Banner 'SSH READY - Archmagi can log in now. Leave this window open.' 'Green'
    } else {
        Show-Banner 'SSH NOT READY - read the FAIL lines above (RUNBOOK step 1 fallback)' 'Red'
    }

    # Phase B. reboot_needed is recomputed on every run (hostname + WSL features set it).
    $script:Status.facts.reboot_needed = $false
    Invoke-Step 'power' { Set-PowerPolicy }
    Invoke-Step 'wake_on_lan' { Set-WakeOnLan }
    Invoke-Step 'windows_update' { Set-UpdatePolicy }
    Invoke-Step 'storage_sense' { Enable-StorageSense }
    Invoke-Step 'hostname' { Set-Hostname }
    Invoke-Step 'wsl_features' { Enable-WslFeatures }
    Invoke-Step 'winget' { Initialize-Winget }
    Invoke-Step 'pkg_git' { Install-WingetPackage 'Git.Git' }
    Invoke-Step 'pkg_python' { Install-WingetPackage 'Python.Python.3.13' '/quiet InstallAllUsers=1 PrependPath=1 Include_launcher=1' }
    # modcheck's live rows compose diptychs with Pillow in THIS python (sweep J20261026T004751Z-6e5292: 4 rows read FAIL without it)
    Invoke-Step 'pkg_python_pillow' {
        # Invoke-Native, not a bare call: under 'Stop' PS 5.1 makes any pip stderr warning a terminating error.
        $out = Invoke-Native (Join-Path $env:ProgramFiles 'Python313\python.exe') @('-m', 'pip', 'install', '--disable-pip-version-check', '-q', 'pillow')
        if ($LASTEXITCODE -ne 0) { throw "pip install pillow rc=$LASTEXITCODE $out" }
        'pillow installed'
    }
    Invoke-Step 'pkg_dotnet8' { Install-WingetPackage 'Microsoft.DotNet.SDK.8' }
    Invoke-Step 'pkg_tailscale' { Install-WingetPackage 'Tailscale.Tailscale' }
    Invoke-Step 'pkg_crd_host' { Install-WingetPackage 'Google.ChromeRemoteDesktopHost' }
    Invoke-Step 'autologon_tool' { Install-Autologon }
    Invoke-Step 'rdp' { Enable-RdpIfPro }
    Invoke-Step 'task_keepalive' { Register-KeepaliveTask }
    Invoke-Step 'task_fleet' { Register-FleetTask }
    Invoke-Step 'task_selfupgrade' { Register-SelfUpgradeTask }
    Invoke-Step 'tailscale_login' { Start-TailscaleLogin }
    $script:Status.phase = 'B_done'
    Send-Report 'phase_b_done'

    $featOk = $false
    try {
        $featOk = ((Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform).State -eq 'Enabled') -and
                  ((Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux).State -eq 'Enabled')
    } catch { }
    $needReboot = $script:Status.facts.reboot_needed -or (-not $featOk -and $script:Status.steps['wsl_features'].ok)
    if ($needReboot) {
        $n = [int]$script:Status.facts.bootstrap_reboots
        if ($n -ge 2) {
            Show-Banner 'STILL NEEDS A REBOOT after 2 reboots - stopping here; agents look at status.json over SSH' 'Red'
            Send-Report 'reboot_loop_stopped'
            return
        }
        Invoke-Step 'resume_task' { Register-ResumeTask }
        Show-Banner 'PHASE B DONE - a reboot is needed (RUNBOOK step 5: BIOS on the way back up)' 'Yellow'
        if ([Console]::IsInputRedirected) {
            # Run over SSH or from a task with no console: Read-Host would hang. Do not reboot.
            Show-Banner 'REBOOT NEEDED - not rebooting without a console; an agent reboots it on purpose' 'Yellow'
            Send-Report 'reboot_needed_noconsole'
            return
        }
        Read-Host 'Press Enter to reboot now (or close this window to reboot later)'
        $script:Status.facts.bootstrap_reboots = $n + 1
        $script:Status.phase = 'rebooting'
        Save-Status
        Restart-Computer -Force
        return
    }

    # Phase C: WSL (after the reboot, or straight away if the features were already on).
    if (-not $featOk) {
        Invoke-Step 'ubuntu' { throw 'WSL Windows features are not enabled (see step wsl_features)' }
    } else {
        Invoke-Step 'ubuntu' { Install-Ubuntu }
    }
    if ($script:Status.steps['ubuntu'].ok) {
        Invoke-Step 'wsl_pass1' { Invoke-WslBootstrap 'pass1' }
        # systemd starts only on a fresh boot of the distro after /etc/wsl.conf says so. Restart
        # Ubuntu alone, and only when systemd is not already PID 1 (a rerun must not kill the
        # WSL Tailscale door or a running job).
        Invoke-Step 'wsl_restart' {
            $pid1 = Invoke-Wsl @('-d', 'Ubuntu', '-u', 'root', '--', 'ps', '-p', '1', '-o', 'comm=')
            if ($pid1 -match 'systemd') { 'systemd already PID 1; no restart' }
            else { Invoke-Wsl @('--terminate', 'Ubuntu') | Out-Null; Start-Sleep -Seconds 8; 'Ubuntu restarted for systemd' }
        }
        Invoke-Step 'wsl_pass2' { Invoke-WslBootstrap 'pass2' }
        Invoke-Step 'wsl_facts' { Get-WslFacts }
        Invoke-Step 'keepalive_now' { Start-ScheduledTask -TaskName 'WSL Keepalive'; 'started' }
    }
    Invoke-Step 'facts_final' { Get-Facts }
    $failed = @($script:Status.steps.Keys | Where-Object { -not $script:Status.steps[$_].ok })
    $script:Status.failed_steps = $failed
    $required = @('sshd', 'ssh_key', 'ssh_firewall', 'ubuntu', 'wsl_pass1', 'wsl_pass2')
    $missing = @($required | Where-Object { -not ($script:Status.steps[$_] -and $script:Status.steps[$_].ok) })
    if ($missing.Count -eq 0) {
        $script:Status.phase = 'C_done'
    } else {
        # Keep the resume task: the next logon retries the missing steps.
        $script:Status.phase = 'C_incomplete'
        Invoke-Step 'resume_task' { Register-ResumeTask }
    }
    Send-Report ('phase_' + $script:Status.phase)
    if ($failed.Count -eq 0) { Show-Banner 'BOOTSTRAP COMPLETE - go to RUNBOOK step 7' 'Green' }
    else { Show-Banner ("BOOTSTRAP DONE WITH FAILURES: " + ($failed -join ', ') + ' - agents fix these over SSH') 'Yellow' }
    if ($script:Status.facts.tailscale_auth_url) { Write-Host "Tailscale login (if not done yet): $($script:Status.facts.tailscale_auth_url)" }
    # Last, and only now: deleting the resume task may end the very window that shows the banner.
    if ($script:Status.phase -eq 'C_done' -and (Get-ScheduledTask -TaskName $ResumeTask -ErrorAction SilentlyContinue)) {
        Unregister-ScheduledTask -TaskName $ResumeTask -Confirm:$false
    }
}

$isStaged = $false
if ($PSCommandPath) {
    try { $isStaged = ((Resolve-Path -LiteralPath $PSCommandPath).Path -ieq (Join-Path $Root 'bootstrap.ps1')) } catch { }
}
if (-not $isStaged) {
    Invoke-Stage
} else {
    try { Invoke-Main }
    catch {
        $msg = $_.Exception.Message
        try { Write-Log "FATAL: $msg" } catch { }
        Write-Host "FATAL: $msg" -ForegroundColor Red
    }
}
