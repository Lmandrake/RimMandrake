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
