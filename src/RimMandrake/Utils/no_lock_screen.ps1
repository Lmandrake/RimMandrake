<#
no_lock_screen.ps1 — make this machine boot straight to the desktop.

Run ELEVATED. Applied live 2026-09-19 on ARCHMAGI at the owner's word ("Yes,
activate auto-login. No more lock screen please.") and verified by readback.

WHAT THIS SCRIPT DOES NOT DO: the autologon credential
======================================================
The password is set separately with Sysinternals Autologon, kept at
C:\Users\Mandrake\Claude\Autologon\Autologon64.exe. That tool stores it as an
LSA secret; writing DefaultPassword under Winlogon instead would leave the
account password in the registry in PLAINTEXT, readable by anything running as
the user. Verified after the fact: AutoAdminLogon = 1 with NO DefaultPassword
value present, which is Autologon's signature.

To turn auto-login back OFF, run Autologon64.exe and click Disable — not a
registry edit, or the LSA secret is orphaned.

WHY DevicePasswordLessBuildVersion MATTERS
==========================================
It was 2 here. On a Hello-passwordless build that hides the netplwiz "users
must enter a user name and password" checkbox AND blocks autologon outright, so
Autologon appears to succeed and the machine still stops at the lock screen.
Setting it to 0 is the prerequisite, not a nicety.

NOT TOUCHED ON PURPOSE
======================
DisableLockWorkstation — Win+L still locks the machine deliberately. Only the
automatic lock screen is gone.
#>
$ErrorActionPreference = 'Continue'
$log = @()

New-Item -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PasswordLess\Device' -Force | Out-Null
Set-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\PasswordLess\Device' `
    -Name DevicePasswordLessBuildVersion -Value 0 -Type DWord
$log += 'DevicePasswordLessBuildVersion = 0'

New-Item -Path 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization' -Force | Out-Null
Set-ItemProperty 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization' `
    -Name NoLockScreen -Value 1 -Type DWord
$log += 'NoLockScreen = 1'

# No sign-in on wake from sleep, on mains and on battery.
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0 2>&1 | Out-Null
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_NONE CONSOLELOCK 0 2>&1 | Out-Null
powercfg /SETACTIVE SCHEME_CURRENT 2>&1 | Out-Null
$log += 'CONSOLELOCK = 0 (AC + DC)'

Set-ItemProperty 'HKCU:\Control Panel\Desktop' -Name ScreenSaverIsSecure -Value 0 -Type String
$log += 'ScreenSaverIsSecure = 0'

$log | ForEach-Object { "OK  $_" }
