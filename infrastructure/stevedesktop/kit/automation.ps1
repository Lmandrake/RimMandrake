# SteveDesktop full-automation fixes (2026-10-25). Idempotent. Runs elevated over OpenSSH.
# Session-1 settings (the screensaver) take effect at next logon; to apply one live, run the
# SystemParametersInfo call from WSL interop, which lands in the logged-on session.
$sid=(New-Object Security.Principal.NTAccount('sjlewis')).Translate([Security.Principal.SecurityIdentifier]).Value
$hu="Registry::HKEY_USERS\$sid"
function Set-Reg($path,$name,$val,$type='DWord'){ if(-not (Test-Path $path)){ New-Item -Path $path -Force | Out-Null }; New-ItemProperty -Path $path -Name $name -Value $val -PropertyType $type -Force | Out-Null; "$path\$name=$val" }
# 1. a crashed game must not leave a modal Windows Error Reporting dialog
Set-Reg 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting' DontShowUI 1
Set-Reg "$hu\Software\Microsoft\Windows\Windows Error Reporting" DontShowUI 1
# 2. no screensaver over the game window (it was Ribbons.scr after 60 min)
Set-Reg "$hu\Control Panel\Desktop" ScreenSaveActive '0' String
# 3. no post-update "finish setting up your device" / welcome screens
Set-Reg "$hu\Software\Microsoft\Windows\CurrentVersion\UserProfileEngagement" ScoobeSystemSettingEnabled 0
Set-Reg "$hu\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" SubscribedContent-310093Enabled 0
Set-Reg "$hu\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" SubscribedContent-338389Enabled 0
# 4. Windows Update never swaps the GPU driver under a run
Set-Reg 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate' ExcludeWUDriversInQualityUpdate 1
# 5. never sleep, never hibernate on AC (already 0; enforced)
powercfg /change standby-timeout-ac 0; powercfg /change hibernate-timeout-ac 0; powercfg /hibernate off
"power: standby/hibernate AC = never"
