#!/usr/bin/env bash
# Stage and serve the SteveDesktop bootstrap from Archmagi (RUNBOOK step 0, agent side).
#   serve_bootstrap.sh            stage, then start a detached Windows python server (240 min)
#   serve_bootstrap.sh --test     stage, serve 1 min in the foreground, fetch /b through it
#   serve_bootstrap.sh --stop     stop the detached server
#   serve_bootstrap.sh --stage    stage only (for copying the folder to a USB stick)
# Folder: D:\ClaudeWork\stevedesktop\serve  (reports land in ...\serve\reports\latest.json)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
SERVE=/mnt/d/ClaudeWork/stevedesktop/serve
SERVE_WIN='D:\ClaudeWork\stevedesktop\serve'
PORT=8767
PUB=$HOME/.ssh/id_ed25519.pub

stage() {
    mkdir -p "$SERVE/reports"
    cp "$HERE/bootstrap.ps1" "$HERE/bootstrap_wsl.sh" "$HERE/serve_bootstrap.py" "$SERVE/"
    cp "$PUB" "$SERVE/archmagi.pub"
    # The .ps1 must stay ASCII (PowerShell 5.1 reads BOM-less files as ANSI); the .sh must stay LF.
    if LC_ALL=C grep -q -P '[^\x00-\x7F]' "$SERVE/bootstrap.ps1"; then echo "bootstrap.ps1 is not ASCII" >&2; exit 1; fi
    if grep -q $'\r' "$SERVE/bootstrap_wsl.sh"; then echo "bootstrap_wsl.sh has CR line ends" >&2; exit 1; fi
    echo "staged $SERVE_WIN"
}

stop() {
    if [ -f "$SERVE/serve.pid" ]; then
        powershell.exe -NoProfile -Command "Stop-Process -Id $(cat "$SERVE/serve.pid") -ErrorAction SilentlyContinue" || true
        rm -f "$SERVE/serve.pid"; echo stopped
    else echo "no serve.pid"; fi
}

case "${1:-}" in
    --stage) stage ;;
    --stop) stop ;;
    --test)
        stage
        timeout 70 python.exe "$SERVE_WIN\\serve_bootstrap.py" --dir "$SERVE_WIN" --port $PORT --minutes 1 &
        sleep 4
        { curl -s -m 5 "http://192.168.86.221:$PORT/b" || true; } | head -c 120 || true; echo
        curl -s -m 5 -o /dev/null -w 'archmagi.pub http=%{http_code}\n' "http://192.168.86.221:$PORT/archmagi.pub"
        curl -s -m 5 -o /dev/null -w 'traversal http=%{http_code}\n' "http://192.168.86.221:$PORT/../serve.log"
        curl -s -m 5 -o /dev/null -w 'report http=%{http_code}\n' -H 'Content-Type: application/json' \
            -d '{"phase":"test","facts":{"report_reason":"selftest","lan_ip":"0.0.0.0"}}' "http://192.168.86.221:$PORT/report"
        wait || true
        ;;
    "")
        stage
        stop >/dev/null 2>&1 || true
        powershell.exe -NoProfile -Command "Start-Process -WindowStyle Minimized -FilePath python.exe -ArgumentList '\"$SERVE_WIN\\serve_bootstrap.py\" --dir \"$SERVE_WIN\" --port $PORT --minutes 240'"
        sleep 3
        curl -s -m 5 -o /dev/null -w "serving: http://192.168.86.221:$PORT/b http=%{http_code}\n" "http://192.168.86.221:$PORT/b"
        echo "He types on SteveDesktop:  irm http://192.168.86.221:$PORT/b | iex"
        echo "Reports: $SERVE/reports/latest.json"
        ;;
    *) echo "usage: $0 [--test|--stop|--stage]"; exit 2 ;;
esac
