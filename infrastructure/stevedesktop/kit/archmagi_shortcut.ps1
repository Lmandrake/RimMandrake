# Archmagi side: desktop shortcut "Claude on SteveDesktop" -> Windows Terminal -> Archmagi WSL -> ssh (Tailscale SSH)
# into SteveDesktop WSL -> tmux session 'claude-centre' (created, or re-attached if it already exists).
$wt = "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe"
$desk = [Environment]::GetFolderPath('Desktop')
$l = (New-Object -ComObject WScript.Shell).CreateShortcut("$desk\Claude on SteveDesktop.lnk")
$l.TargetPath = $wt
$l.Arguments = 'new-tab --title "Claude on SteveDesktop" wsl.exe -d Ubuntu -- ssh -t mandrake@stevedesktop-wsl "tmux new-session -A -s claude-centre ~/rm/runner/infrastructure/stevedesktop/claude_session.sh centre"'
$l.IconLocation = 'C:\Windows\System32\shell32.dll,18'
$l.Description = 'Claude session on SteveDesktop test centre (tmux, survives closing)'
$l.Save()
