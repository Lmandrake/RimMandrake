#!/usr/bin/env bash
# Start, stop and query the test-centre RimWorld on SteveDesktop. Runs in Steve's WSL
# (from Archmagi: ssh mandrake@stevedesktop-wsl ~/rm/runner/infrastructure/stevedesktop/rw_game.sh up).
#
#   rw_game.sh status         running? pid, session, bridge port from Player.log
#   rw_game.sh up [--wait]    start the game unless running; --wait blocks until the bridge
#                             announces its port in a Player.log written after the launch (max 600 s)
#   rw_game.sh down           graceful taskkill, then /F after 90 s
#
# STEVEDESKTOP_LAUNCH_WIRE_DESKTOP_SESSION (2026-10-25). Why it looks like this:
#  - The game is started by running RimWorldWin64.exe directly (Steam must already be running,
#    which it is after Steve's autologon). steam://rungameid cannot carry arguments, and the
#    argument that matters is -savedatafolder: it keeps Config/ModsConfig.xml, Saves and DefDump
#    in D:\RimTest\userdata so Steve's own mod list and saves are never touched.
#  - powershell.exe is reached by its full /mnt/c path: a Tailscale SSH session has no Windows
#    dirs on PATH. Started from WSL interop, the process lands in session 1 (the logged-in
#    desktop), which is where a Unity game must run; from Windows OpenSSH it would land in
#    session 0 with no display.
#  - Paths come from testcentre_env.sh (RM_STEAMAPPS, RM_GAME_USERDATA, RM_GAME_LOGDIR).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
[ -n "${RM_STEAMAPPS:-}" ] || . "$HERE/testcentre_env.sh"
PS=/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe
TK=/mnt/c/Windows/System32/taskkill.exe
winpath() { echo "$1" | sed -E 's#^/mnt/([a-z])/#\U\1:/#; s#/#\\#g'; }
GAME_WSL="$RM_STEAMAPPS/common/RimWorld"
EXE_WIN=$(winpath "$GAME_WSL/RimWorldWin64.exe")
DIR_WIN=$(winpath "$GAME_WSL")
DATA_WIN=$(winpath "$RM_GAME_USERDATA")
LOG="$RM_GAME_LOGDIR/Player.log"

ps_q() { "$PS" -NoProfile -NonInteractive -Command "\$ProgressPreference='SilentlyContinue'; $1" 2>/dev/null | tr -d '\r'; }
pid_of() { ps_q "(Get-Process RimWorldWin64 -ErrorAction SilentlyContinue | Select-Object -First 1).Id"; }
port_in_log() { [ -f "$LOG" ] && grep -a -o '\[RimBridge\].*on port *[0-9]*' "$LOG" | tail -1 | grep -o '[0-9]*$'; }

status() {
    local pid; pid=$(pid_of)
    if [ -n "$pid" ]; then
        local info; info=$(ps_q "\$p=Get-Process -Id $pid; '{0} session={1} started={2:yyyy-MM-dd HH:mm:ss}' -f \$p.Id,\$p.SessionId,\$p.StartTime")
        local args; args=$(ps_q "(Get-CimInstance Win32_Process -Filter 'ProcessId=$pid').CommandLine")
        echo "running pid=$info"
        echo "  cmdline: $args"
        case "$args" in *savedatafolder*) ;; *) echo "  WARNING: not launched with -savedatafolder: this is Steve's own game, not the test centre's" ;; esac
        echo "  bridge port in Player.log: $(port_in_log || echo none)"
        return 0
    fi
    echo "stopped"
    return 3
}

up() {
    local pid; pid=$(pid_of)
    if [ -n "$pid" ]; then echo "already running (pid $pid)"; status; return 0; fi
    ps_q "Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Id" | grep -q . \
        || { echo "REFUSED: Steam is not running in Steve's session (it starts at his autologon). Without it the game exits at Steam init."; return 2; }
    mkdir -p "$RM_GAME_USERDATA"
    local t0; t0=$(date +%s)
    ps_q "Start-Process -FilePath '$EXE_WIN' -WorkingDirectory '$DIR_WIN' -ArgumentList '-savedatafolder=$DATA_WIN'"
    sleep 5
    pid=$(pid_of)
    [ -n "$pid" ] || { echo "FAILED: no RimWorldWin64 process 5 s after Start-Process"; return 1; }
    echo "started pid $pid (-savedatafolder=$DATA_WIN)"
    [ "${1:-}" = --wait ] || return 0
    while [ $(( $(date +%s) - t0 )) -lt 600 ]; do
        if [ -f "$LOG" ] && [ "$(stat -c %Y "$LOG")" -ge "$t0" ] && port_in_log >/dev/null; then
            echo "bridge up on port $(port_in_log) after $(( $(date +%s) - t0 )) s"; return 0
        fi
        [ -n "$(pid_of)" ] || { echo "FAILED: game exited during load; tail of Player.log:"; tail -n 15 "$LOG"; return 1; }
        sleep 5
    done
    echo "TIMEOUT: no bridge port in a fresh Player.log after 600 s"; return 1
}

down() {
    local pid; pid=$(pid_of)
    [ -n "$pid" ] || { echo "already stopped"; return 0; }
    "$TK" /PID "$pid" >/dev/null 2>&1
    for _ in $(seq 18); do sleep 5; [ -n "$(pid_of)" ] || { echo "stopped (graceful)"; return 0; }; done
    "$TK" /F /PID "$pid" >/dev/null 2>&1; sleep 3
    [ -n "$(pid_of)" ] && { echo "FAILED: pid $pid survives taskkill /F"; return 1; }
    echo "stopped (forced after 90 s)"
}

case "${1:-status}" in
    status) status ;;
    up) up "${2:-}" ;;
    down) down ;;
    *) echo "usage: $0 status|up [--wait]|down"; exit 64 ;;
esac
