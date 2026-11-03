# Creates the Claude desktop shortcuts on SteveDesktop (all-users desktop). Run on SteveDesktop.
# Each opens Windows Terminal -> WSL (mandrake) -> claude_session.sh <centre|lodestar>.
$wt  = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"
$dir = 'C:\Users\Public\Desktop'
$sh  = New-Object -ComObject WScript.Shell
function Make($name, $title, $arg, $icon) {
    $l = $sh.CreateShortcut("$dir\$name.lnk")
    $l.TargetPath = $wt
    $l.Arguments  = "new-tab --title `"$title`" wsl.exe -d Ubuntu -u mandrake --cd ~ -- bash -lc `"~/rm/runner/infrastructure/stevedesktop/claude_session.sh $arg`""
    $l.IconLocation = $icon
    $l.Description = $title
    $l.Save()
}
Make 'Claude - SteveDesktop test centre' 'Claude - test centre' 'centre'   'C:\Windows\System32\shell32.dll,15'
Make 'Claude - Lodestar'                 'Claude - Lodestar'    'lodestar' 'C:\Windows\System32\shell32.dll,21'

# Plain Terminal tiles (no Claude): profile names are from kit/wt_settings.json.
function MakeWt($name, $wtArgs, $icon) {
    $l = $sh.CreateShortcut("$dir\$name.lnk")
    $l.TargetPath = $wt
    $l.Arguments  = $wtArgs
    $l.IconLocation = $icon
    $l.Description = $name
    $l.Save()
}
MakeWt 'Terminal - Ubuntu'               '-p "Ubuntu (mandrake)"'  'C:\Windows\System32\shell32.dll,15'
MakeWt 'Terminal - SteveDesktop status'  'new-tab --title "SteveDesktop status" powershell.exe -NoExit -ExecutionPolicy Bypass -File C:\SteveDesktop\status.ps1' 'C:\Windows\System32\shell32.dll,22'
MakeWt 'Terminal - Archmagi (SSH)'       '-p "SSH Archmagi (WSL)"' 'C:\Windows\System32\shell32.dll,18'
