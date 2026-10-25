#!/usr/bin/env bash
# Check every door into SteveDesktop from Archmagi WSL. One line per check:
#     PASS|FAIL|WARN|SKIP  <check>  <detail>
# Exit status = number of FAIL lines.
#
#   verify_from_archmagi.sh           all checks
#   verify_from_archmagi.sh --wake    send a Wake-on-LAN magic packet first (from Windows, since
#                                     WSL2 cannot broadcast on the LAN), then wait 90 s
#
# Where the facts come from: the report bootstrap.ps1 posts to Archmagi
# (D:\ClaudeWork\stevedesktop\serve\reports\latest.json). Override any with env vars:
#   STEVE_LAN (LAN IP), STEVE_USER (Windows user), STEVE_MAC, STEVE_TS (tailscale name of the
#   Windows node, default stevedesktop), STEVE_TS_WSL (default stevedesktop-wsl), STEVE_WSL_USER.
set -uo pipefail

REPORT=/mnt/d/ClaudeWork/stevedesktop/serve/reports/latest.json
jget() { [ -f "$REPORT" ] && python3 -c 'import json,sys;d=json.load(open(sys.argv[1]));v=d.get("facts",{}).get(sys.argv[2]);print("" if v is None else v)' "$REPORT" "$1" 2>/dev/null; }
LAN=${STEVE_LAN:-$(jget lan_ip)}
WUSER=${STEVE_USER:-$(jget user)}
MAC=${STEVE_MAC:-$(jget mac)}
EDITION=$(jget edition_id)
TS=${STEVE_TS:-stevedesktop}
TS_WSL=${STEVE_TS_WSL:-stevedesktop-wsl}
WSL_USER=${STEVE_WSL_USER:-mandrake}
CTL=${TMPDIR:-/tmp}/steve-ssh-%C
SSHO=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new
      -o ControlMaster=auto -o ControlPath="$CTL" -o ControlPersist=60 -o ServerAliveInterval=5)
FAILS=0

say() { printf '%-4s %-18s %s\n' "$1" "$2" "$3"; [ "$1" = FAIL ] && FAILS=$((FAILS + 1)); return 0; }
tsip() { command -v tailscale >/dev/null && tailscale ip -4 "$1" 2>/dev/null | head -1; }

if [ "${1:-}" = --wake ]; then
    if [ -z "$MAC" ]; then say FAIL wake "no MAC (report missing; set STEVE_MAC)"; else
        powershell.exe -NoProfile -Command "\$m=[byte[]](('$MAC' -split '[-:]') | % {[Convert]::ToByte(\$_,16)}); \$p=[byte[]](,0xFF*6)+(\$m*16); \$u=New-Object Net.Sockets.UdpClient; \$u.EnableBroadcast=\$true; [void]\$u.Send(\$p,\$p.Length,'192.168.86.255',9); [void]\$u.Send(\$p,\$p.Length,'255.255.255.255',9); \$u.Close()" \
            && say PASS wake "magic packet sent to $MAC; waiting 90 s" || say FAIL wake "send failed"
        sleep 90
    fi
fi

[ -f "$REPORT" ] || say WARN report "no $REPORT yet (bootstrap not run, or report not delivered); using env only"
[ -n "$WUSER" ] || { say FAIL config "Windows user unknown: set STEVE_USER"; exit "$FAILS"; }

# Door 1: LAN SSH to Windows OpenSSH.
WIN=""
if [ -n "$LAN" ]; then
    if out=$(ssh "${SSHO[@]}" "$WUSER@$LAN" 'hostname' 2>&1); then say PASS lan_ssh "$WUSER@$LAN hostname=$(echo "$out" | tr -d '\r')"; WIN="$WUSER@$LAN"
    else say FAIL lan_ssh "$WUSER@$LAN: $(echo "$out" | tr -d '\r' | tail -1)"; fi
else say SKIP lan_ssh "LAN IP unknown"; fi

# Door 2: Windows OpenSSH over Tailscale (the Windows Tailscale client is a service: no logon needed).
TSIP=$(tsip "$TS")
if [ -n "$TSIP" ]; then
    if out=$(ssh "${SSHO[@]}" "$WUSER@$TSIP" 'hostname' 2>&1); then say PASS ts_ssh "$WUSER@$TSIP ($TS)"; WIN=${WIN:-"$WUSER@$TSIP"}
    else say FAIL ts_ssh "$WUSER@$TSIP: $(echo "$out" | tr -d '\r' | tail -1)"; fi
else say FAIL ts_ssh "no tailnet node '$TS' visible from Archmagi (not logged in, expired, or offline)"; fi

# Door 3: Tailscale SSH straight into WSL (needs a Windows logon: autologon + WSL Keepalive).
TSWIP=$(tsip "$TS_WSL")
if [ -n "$TSWIP" ]; then
    if out=$(ssh "${SSHO[@]}" "$WSL_USER@$TSWIP" 'uname -r; systemctl is-system-running' 2>&1); then say PASS wsl_ts_ssh "$WSL_USER@$TSWIP $(echo "$out" | tr '\n' ' ')"
    else say FAIL wsl_ts_ssh "$WSL_USER@$TSWIP: $(echo "$out" | tail -1) (tailnet SSH rule must be accept, not check)"; fi
else say FAIL wsl_ts_ssh "no tailnet node '$TS_WSL' visible"; fi

if [ -z "$WIN" ]; then say FAIL windows "no Windows SSH door answered; remaining checks skipped"; exit "$FAILS"; fi
win() { ssh "${SSHO[@]}" "$WIN" "$1" 2>&1 | tr -d '\r'; }

# Door 4: WSL through Windows SSH (works even when WSL's own Tailscale is down).
out=$(win 'wsl.exe -d Ubuntu -- uname -r')
if echo "$out" | grep -q -i microsoft; then say PASS wsl_hop "$out"; else say FAIL wsl_hop "$(echo "$out" | tail -1)"; fi

# GUI door: Chrome Remote Desktop has no inbound port (it dials out to Google); check its service.
out=$(win "(Get-Service chromoting -ErrorAction SilentlyContinue).Status")
case "$out" in Running*) say PASS gui_crd "chromoting service Running" ;; *) say FAIL gui_crd "chromoting: ${out:-not installed}" ;; esac
if [ -n "$EDITION" ] && ! [[ "$EDITION" =~ ^Core ]]; then
    if timeout 5 bash -c "</dev/tcp/${WIN#*@}/3389" 2>/dev/null; then say PASS rdp "3389 open ($EDITION)"; else say WARN rdp "3389 closed ($EDITION)"; fi
else say SKIP rdp "Home edition (no RDP server) or edition unknown"; fi

out=$(win "\$b=(Get-CimInstance Win32_OperatingSystem).LastBootUpTime; '{0} since {1:yyyy-MM-dd HH:mm}' -f ((Get-Date)-\$b).ToString('d\.hh\:mm'), \$b")
say PASS uptime "$out"

out=$(win "(Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon').AutoAdminLogon")
[ "$out" = 1 ] && say PASS autologon "AutoAdminLogon=1" || say FAIL autologon "AutoAdminLogon=${out:-unset} (RUNBOOK step 7)"

out=$(win "if ((Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired') -or (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')) { 'pending' } else { 'none' }")
[ "$out" = none ] && say PASS reboot_pending "none" || say WARN reboot_pending "$out: reboot it at a time of our choosing (RUNBOOK survives-the-week)"

out=$(win "wsl.exe -d Ubuntu -- cat /var/lib/runner/last_selfupgrade.json")
if echo "$out" | grep -q '"utc"'; then say PASS selfupgrade_wsl "$out"; else say WARN selfupgrade_wsl "no stamp yet ($(echo "$out" | tail -1))"; fi
out=$(win "Get-Content C:\SteveDesktop\last_selfupgrade_windows.json -Raw -ErrorAction SilentlyContinue")
if echo "$out" | grep -q utc; then say PASS selfupgrade_win "$(echo "$out" | tr -d '\n ')"; else say WARN selfupgrade_win "no stamp yet (first run Sunday 04:30)"; fi

out=$(win "[math]::Round((Get-PSDrive C).Free/1GB,1)")
if [[ "$out" =~ ^[0-9.]+$ ]]; then
    if awk "BEGIN{exit !($out < 20)}"; then say FAIL disk_c "${out} GB free (<20)"; else say PASS disk_c "${out} GB free"; fi
else say FAIL disk_c "$out"; fi
out=$(win "wsl.exe -d Ubuntu -- df -P -BG / | Select-Object -Last 1")
say PASS disk_wsl "$(echo "$out" | awk '{print $4" free of "$2" on /"}')"

out=$(win "wsl.exe -d Ubuntu -- test -d /home/$WSL_USER/rm/runner/.git; if (\$LASTEXITCODE -eq 0) { 'yes' } else { 'no' }")
[ "$out" = yes ] && say PASS runner_clone "~/rm/runner present" || say WARN runner_clone "missing (RUNBOOK step A3)"

# Tailscale key expiry, read from Archmagi's own view of the tailnet.
if command -v tailscale >/dev/null; then
    tailscale status --json 2>/dev/null | python3 -c '
import json, sys
d = json.load(sys.stdin)
for p in d.get("Peer", {}).values():
    name = (p.get("DNSName") or p.get("HostName", "")).split(".")[0].lower()
    if name in (sys.argv[1], sys.argv[2]):
        exp = p.get("KeyExpiry")
        print(("WARN" if exp else "PASS") + " %-18s %s" % ("ts_expiry_" + ("wsl" if name.endswith("wsl") else "win"),
              ("key expires " + exp + " (disable expiry: RUNBOOK step 4)") if exp else "key expiry disabled"))
' "$TS" "$TS_WSL"
fi

# Maintenance kit (RUNBOOK "Maintenance kit").
kit=$(win 'foreach($p in "$env:LOCALAPPDATA\Microsoft\WindowsApps\wt.exe","$env:LOCALAPPDATA\Programs\Microsoft VS Code\bin\code.cmd","C:\Program Files\GitHub CLI\gh.exe","C:\Program Files\Git\bin\git.exe","C:\Program Files\7-Zip\7z.exe","C:\SteveDesktop\status.ps1","C:\Users\Public\Desktop\Terminal - Ubuntu.lnk","$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"){ if(-not (Test-Path $p)){ "missing " + (Split-Path $p -Leaf) } }; if(-not (Get-Command pwsh -EA 0)){"missing pwsh.exe"}; "end"')
miss=$(echo "$kit" | grep '^missing' | sed 's/missing //' | tr '\n' ' ')
if echo "$kit" | grep -q '^end'; then
    [ -z "$miss" ] && say PASS kit_windows "wt, pwsh7, code, gh, git, 7z, status.ps1, shortcut, WT settings" || say FAIL kit_windows "missing: $miss"
else say FAIL kit_windows "no answer: $(echo "$kit" | tail -1)"; fi
out=$(win 'wsl.exe -d Ubuntu -u mandrake -- which git gh tmux htop jq rg tree python3 pipx' | grep -c '^/')
[ "$out" = 9 ] && say PASS kit_wsl "git gh tmux htop jq rg tree python3 pipx" || say FAIL kit_wsl "only $out of 9 tools found in WSL"

# Nobody at the keyboard (RUNBOOK "Full-automation audit"; fixes in kit/automation.ps1).
out=$(win '$w=(Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting" -EA 0).DontShowUI; $s=(Get-ItemProperty "HKCU:\Control Panel\Desktop" -EA 0).ScreenSaveActive; $u=(Get-ItemProperty "HKCU:\Software\Valve\Steam" -EA 0).AutoLoginUser; $r=(Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -EA 0).Steam; "wer=$w saver=$s steamuser=$(if($u){"set"}else{"none"}) steamrun=$(if($r){"yes"}else{"no"})"')
if [ "$out" = "wer=1 saver=0 steamuser=set steamrun=yes" ]; then say PASS unattended "$out"
else say FAIL unattended "$out (want wer=1 saver=0 steamuser=set steamrun=yes: run kit/automation.ps1; Steam login needs CRD)"; fi

# Claude support kit (RUNBOOK "Claude support kit"): clones, rendered CLAUDE.md, git identity.
# The script travels base64-encoded: PowerShell would expand every $ in it.
kitsh='n=0; for r in Lodestar Machinist Dispatch claude-remote-control MandrakeWorkflows MandrakeVisualize; do git -C ~/dev/$r rev-parse -q --verify HEAD >/dev/null 2>&1 && n=$((n+1)); done; c=$(grep -c SteveDesktop ~/.claude/CLAUDE.md 2>/dev/null); s=$(ls ~/.claude/skills 2>/dev/null | wc -l); e=$(git config --global user.email); echo clones=$n/6 claudemd=${c:-0} skills=$s email=${e:-none}'
out=$(win "wsl.exe -d Ubuntu -u $WSL_USER -- bash -c 'echo $(printf %s "$kitsh" | base64 -w0) | base64 -d | bash'")
if [[ "$out" =~ clones=6/6\ claudemd=[1-9].*email=[^n] ]]; then say PASS claude_kit "$out"
else say FAIL claude_kit "${out:-no answer} (RUNBOOK Claude support kit)"; fi

exit "$FAILS"
