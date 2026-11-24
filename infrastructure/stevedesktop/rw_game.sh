#!/usr/bin/env bash
# Start, stop and query the test-centre RimWorld on SteveDesktop. Runs in SteveDesktop's WSL
# (from Archmagi: ssh mandrake@stevedesktop-wsl ~/rm/runner/infrastructure/stevedesktop/rw_game.sh up).
#
#   rw_game.sh status         running? pid, session, bridge port from Player.log
#   rw_game.sh up [--wait]    start the game unless running; --wait blocks until the bridge
#                             announces its port in a Player.log written after the launch (max RW_UP_WAIT_S, 6100 s)
#   rw_game.sh down           graceful taskkill, then /F after 90 s; each stop's refusal or failure is named
#   rw_game.sh init           renew the test companion profile; seed Prefs.xml if it lacks
#                             runInBackground True (game must be stopped for that half)
#
# Every verb acts on one game: RM_GAME_INSTANCE=b rw_game.sh down stops b and only b; nothing set is
# game a, as ever (src/RimMandrake/Utils/game_instance.py finds a game by its command line and stops
# it by pid). A named game's `up` starts it directly, its `init` seeds it even with game a up.
#
# STEVEDESKTOP_LAUNCH_WIRE_DESKTOP_SESSION (2026-10-25). Why it looks like this:
#  - The game on SteveDesktop is ours outright (owner, 2026-10-25: "Steve no longer plays
#    Rimworld ... this game is ours to play with"). It runs with its normal save-data folder
#    (sjlewis's LocalLow), so ModsConfig.xml, Prefs.xml and Saves there belong to the runner.
#  - The game is started by running RimWorldWin64.exe directly; Steam must be running, and `up`
#    starts it (logged in by its remembered account) when it is not.
#  - powershell.exe is reached by its full /mnt/c path: a Tailscale SSH session has no Windows
#    dirs on PATH. Started from WSL interop, the process lands in session 1 (the logged-in
#    desktop), which is where a Unity game must run; from Windows OpenSSH it would land in
#    session 0 with no display.
#  - Paths come from testcentre_env.sh (RM_STEAMAPPS, RM_GAME_USERDATA, RM_GAME_LOGDIR).
set -uo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
[ -n "${RM_STEAMAPPS:-}" ] || . "$HERE/testcentre_env.sh"
GI="$HERE/../../src/RimMandrake/Utils/game_instance.py"
NAMED=
case "${RM_GAME_INSTANCE:-a}" in
    a|A) ;;
    *) _env=$(python3 "$GI" env) || exit 2; eval "$_env"; NAMED=$RM_GAME_INSTANCE ;;   # after testcentre_env.sh: b's folders win
esac
PS=$(command -v powershell.exe || echo /mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe)
winpath() { echo "$1" | sed -E 's#^/mnt/([a-z])/#\U\1:/#; s#/#\\#g'; }
GAME_WSL="$RM_STEAMAPPS/common/RimWorld"
EXE_WIN=$(winpath "$GAME_WSL/RimWorldWin64.exe")
DIR_WIN=$(winpath "$GAME_WSL")
DATA_WIN=$(winpath "$RM_GAME_USERDATA")
STEAM_EXE_WIN=$(winpath "$(dirname "$RM_STEAMAPPS")")\\steam.exe
LOG="$RM_GAME_LOGDIR/Player.log"

ps_q() { "$PS" -NoProfile -NonInteractive -Command "\$ProgressPreference='SilentlyContinue'; $1" 2>/dev/null | tr -d '\r'; }
pid_of() { python3 "$GI" pid; }   # this game's pid, nothing when it is down, non-zero when the list could not be read
gone() { local p; p=$(pid_of) && [ -z "$p" ]; }
port_in_log() { [ -f "$LOG" ] && grep -a -o '\[RimBridge\].*on port *[0-9]*' "$LOG" | tail -1 | grep -o '[0-9]*$'; }

status() {
    local pid; pid=$(pid_of) || return 2
    if [ -n "$pid" ]; then
        local info; info=$(ps_q "\$p=Get-Process -Id $pid; '{0} session={1} started={2:yyyy-MM-dd HH:mm:ss} age_s={3}' -f \$p.Id,\$p.SessionId,\$p.StartTime,[int]((Get-Date)-\$p.StartTime).TotalSeconds")
        local args; args=$(ps_q "(Get-CimInstance Win32_Process -Filter 'ProcessId=$pid').CommandLine")
        echo "running pid=$info"
        echo "  cmdline: $args"
        echo "  bridge port in Player.log: $(port_in_log || echo none)"
        return 0
    fi
    echo "stopped"
    return 3
}

# RIMMANDRAKE_KEEP_STEVE_LANE_GAME_SOUND_OFF_SONIC_STUDIO_AT_LAUNCH. On SteveDesktop the register fault follows the game's
# sound through the Sonic Studio virtual mixer (infrastructure/state/facts/steve_fault_diagnosis.md). Nobody plays the lane's
# game, and neither Unity 2022.3 nor RimWorld has a switch for no audio device. So `up` starts game_audio_route.ps1 BEFORE the
# game: it waits for the game's own audio session and moves that live stream to RW_GAME_AUDIO_TO with the per-app route
# (a route saved before the start is ignored by a fresh game). No system default device is touched.
# The step is OFF by default. Its one boot after a reboot (2026-11-21, boot 16:47:59Z) read FAULT: the game was ACTIVE on the mixer
# for 6.8 s before the move, and the fault watch caught one wrong result about 10-14 s after the start; the register probe then read
# clean for 48 min. To turn the step on: RW_GAME_AUDIO_TO='Realtek Digital Output' (testcentre_env.sh, or this default).
AUDIO_TO=${RW_GAME_AUDIO_TO-}
AUDIO_LOG="$RM_GAME_LOGDIR/audio_route.log"
AUDIO_PS1="$RM_GAME_LOGDIR/rimmandrake_audio_route.ps1"   # a Windows-side copy: no \\wsl.localhost path for a hidden PowerShell
# audio_arm <exe as Windows path> -> 0 armed (the watcher printed READY), 1 off by setting, 2 could not arm.
# LIMIT RW_AUDIO_READY_S 30: the watcher compiles its C# in about 3 s (measured 2026-11-21); 30 s guards a game started
# on a watcher that never came up, with no line saying so.
audio_arm() {
    [ -n "$AUDIO_TO" ] || { echo "audio route: off (RW_GAME_AUDIO_TO is empty)"; return 1; }
    cp "$HERE/game_audio_route.ps1" "$AUDIO_PS1" 2>/dev/null || { echo "audio route: NOT ARMED (could not copy the watcher to $AUDIO_PS1)"; return 2; }
    rm -f "$AUDIO_LOG"
    ps_q "Start-Process -WindowStyle Hidden -FilePath powershell.exe -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','\"$(winpath "$AUDIO_PS1")\"','-Exe','\"$1\"','-Log','\"$(winpath "$AUDIO_LOG")\"','-Endpoint','\"$AUDIO_TO\"'" >/dev/null
    local w=0 line
    while [ "$w" -lt "${RW_AUDIO_READY_S:-30}" ]; do
        line=$(grep -m1 ' RESULT ' "$AUDIO_LOG" 2>/dev/null) && { echo "audio route: NOT ARMED: ${line#* RESULT }"; return 2; }
        grep -q ' READY ' "$AUDIO_LOG" 2>/dev/null && return 0
        sleep 1; w=$(( w + 1 ))
    done
    echo "audio route: NOT ARMED (no READY in $AUDIO_LOG after ${RW_AUDIO_READY_S:-30} s)"; return 2
}
# audio_report: print the watcher's verdict line. A failure never fails `up`: the lane still runs, on the old risk.
# LIMIT RW_AUDIO_RESULT_S 330: the watcher's own longest path (300 s for a session, plus its pid wait) with margin; it
# guards an `up` blocked by a watcher that died without its RESULT line.
audio_report() {
    local w=0 line
    while [ "$w" -lt "${RW_AUDIO_RESULT_S:-330}" ]; do
        line=$(grep -m1 ' RESULT ' "$AUDIO_LOG" 2>/dev/null) && { echo "audio route: ${line#* RESULT }"; return 0; }
        sleep 1; w=$(( w + 1 ))
    done
    echo "audio route: UNMEASURED (no RESULT in $AUDIO_LOG after ${RW_AUDIO_RESULT_S:-330} s)"
}
named_exe_win() { python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import game_instance as g; print(g.win_path(g.game_dir()) + '\\\\' + g.GAME_EXE)" "$(dirname "$GI")"; }

steam_pid() { ps_q "(Get-Process steam -ErrorAction SilentlyContinue | Select-Object -First 1).Id"; }
# Steam normally runs from the autologon (Run Steam when my computer starts). If it is not
# running, start it: with a remembered login it signs in by itself. The Steam install is
# taken as the folder above RM_STEAMAPPS; if steam.exe is not there, the registry's SteamExe.
steam_up() {
    [ -n "$(steam_pid)" ] && return 0
    local exe="$STEAM_EXE_WIN"
    [ -f "$(dirname "$RM_STEAMAPPS")/steam.exe" ] || exe=$(ps_q "(Get-ItemProperty 'HKCU:\\Software\\Valve\\Steam').SteamExe")
    [ -n "$exe" ] || { echo "REFUSED: Steam is not running and steam.exe was not found"; return 2; }
    echo "Steam not running: starting $exe -silent"
    ps_q "Start-Process -FilePath '$exe' -ArgumentList '-silent'"
    for _ in $(seq 24); do sleep 5; [ -n "$(steam_pid)" ] && { sleep 20; echo "Steam up (pid $(steam_pid))"; return 0; }; done
    echo "FAILED: Steam did not start within 120 s"; return 2
}

# Poll for the game's pid after Start-Process (a slow start or a Steam relaunch can take longer than one look at 5 s).
# Prints the pid; prints nothing and returns 1 when none appeared within RW_START_WAIT_S; 2 when the list could not be read.
wait_for_pid() {
    local waited=0 step=${RW_START_POLL_S:-2} limit=${RW_START_WAIT_S:-60} p
    while :; do
        p=$(pid_of) || return 2
        [ -n "$p" ] && { echo "$p"; return 0; }
        [ "$waited" -ge "$limit" ] && return 1
        sleep "$step"; waited=$(( waited + step ))
    done
}

up() {
    local pid; pid=$(pid_of) || { echo "REFUSED: the game list could not be read; not starting a game on a guess"; return 2; }
    if [ -n "$pid" ]; then echo "already running (pid $pid)"; status; return 0; fi
    steam_up || return 2
    local armed=1
    if [ -n "$NAMED" ]; then
        audio_arm "$(named_exe_win)" && armed=0
        python3 "$GI" launch ${1:+"$1"}; local lrc=$?
        [ "$armed" -eq 0 ] && audio_report
        return $lrc
    fi
    audio_arm "$EXE_WIN" && armed=0
    local t0; t0=$(date +%s)
    ps_q "Start-Process -FilePath '$EXE_WIN' -WorkingDirectory '$DIR_WIN'"
    pid=$(wait_for_pid); local rc=$?
    [ "$rc" -ne 2 ] || { echo "FAILED: the game list could not be read after Start-Process"; return 2; }
    [ "$rc" -eq 0 ] || { echo "FAILED: no RimWorldWin64 process ${RW_START_WAIT_S:-60} s after Start-Process (polled every ${RW_START_POLL_S:-2} s)"; return 1; }
    echo "started pid $pid"
    [ "$armed" -eq 0 ] && audio_report
    [ "${1:-}" = --wait ] || return 0
    # budget: danger=a wedged load holds the lane; longest=602s (testq done records, phase load, 571 jobs, 14 days to 2026-11-24)
    # RW_UP_WAIT_S guards a load that never reaches the bridge (a wedged load, e.g. J20261121T044455Z) so the job ends
    # and the lane moves on. Measured 2026-11-21: DONE cold loads took 473-574 s; one at the old 600 s cap timed out with
    # the game still loading on a clean machine (J20261121T205538Z-b4095c). The default is over 10 times the longest.
    while [ $(( $(date +%s) - t0 )) -lt "${RW_UP_WAIT_S:-6100}" ]; do
        if [ -f "$LOG" ] && [ "$(stat -c %Y "$LOG")" -ge "$t0" ] && port_in_log >/dev/null; then
            echo "bridge up on port $(port_in_log) after $(( $(date +%s) - t0 )) s"; return 0
        fi
        [ -n "$(pid_of)" ] || { echo "FAILED: game exited during load; tail of Player.log:"; tail -n 15 "$LOG"; return 1; }
        sleep 5
    done
    echo "TIMEOUT: no bridge port in a fresh Player.log after ${RW_UP_WAIT_S:-6100} s (RW_UP_WAIT_S)"; return 1
}

# A fresh or reset save-data folder lacks two files that modcheck run refuses without
# (found on the first remote run, 2026-10-25):
#  - JawaBench/companion_profile.json: with none the companion reports profile 'campaign'
#    and ensure_test_profile raises. Every save in this folder is the runner's (the game is
#    ours, owner 2026-10-25), so 'test' is true; the expiry is renewed to 30 days ahead on
#    every init.
#  - Config/Prefs.xml with runInBackground True: game_focus.preflight refuses
#    (FocusRefused, runInBackground UNREADABLE) without it. The game writes Prefs.xml on a
#    clean exit only, and rewrites it from memory then, so it can be seeded only while the
#    game is stopped. Prefs.template.xml is Archmagi's Prefs minus the screen size.
init() {
    if [ -n "$NAMED" ]; then python3 "$GI" prepare; return $?; fi
    mkdir -p "$RM_GAME_USERDATA/JawaBench" "$RM_GAME_USERDATA/Config"
    local exp; exp=$(date -u -d '+30 days' +%Y-%m-%dT%H:%M:%SZ)
    local esc; esc=$(printf '%s' "$DATA_WIN" | sed 's/\\/\\\\/g')   # JSON-escape the backslashes
    cat > "$RM_GAME_USERDATA/JawaBench/companion_profile.json" <<EOF
{
  "profile": "test",
  "expiresUtc": "$exp",
  "campaignSaves": "",
  "why": "SteveDesktop test centre: the game and every save in $esc are the runner's (rw_game.sh init)"
}
EOF
    echo "companion profile: test until $exp"
    local prefs="$RM_GAME_USERDATA/Config/Prefs.xml"
    if grep -q '<runInBackground>True</runInBackground>' "$prefs" 2>/dev/null; then
        echo "Prefs.xml: runInBackground True"; return 0
    fi
    [ -z "$(pid_of)" ] || { echo "REFUSED: Prefs.xml lacks runInBackground True and the game is running (it would overwrite the fix on exit); run down, then init"; return 2; }
    [ -f "$prefs" ] && cp "$prefs" "$prefs.pre-init" && echo "Prefs.xml: old copy kept as Prefs.xml.pre-init"
    cp "$HERE/Prefs.template.xml" "$prefs"
    echo "Prefs.xml: seeded from Prefs.template.xml"
}

# -> 0 gone, 1 still there, 2 the list could not be read
look_gone() { local p; p=$(pid_of) || return 2; [ -z "$p" ] && return 0; return 1; }
# RIMMANDRAKE_STOP_STEVE_GAME_FORCE_KILL_LEFT_IT_RUNNING (11-16: "force stop left the game running", a hand taskkill /F
# then killed it). Each stop's own words and exit are kept: a stop game_instance REFUSED (its bridge check) sent nothing
# and is not "survives /F"; a taskkill that failed says why. After /F the process is polled RW_FORCE_WAIT_S (30) s, not
# looked at once at 3 s: Windows can take seconds to tear a large process down, and the worker's down timeout is 300 s.
down() {
    local pid; pid=$(pid_of) || { echo "REFUSED: the game list could not be read; nothing stopped"; return 2; }
    [ -n "$pid" ] || { echo "already stopped"; return 0; }
    local out rc g waited
    out=$(python3 "$GI" stop "$pid" 2>&1); rc=$?
    if [ "$rc" -ne 0 ] && printf '%s' "$out" | grep -q 'REFUSED'; then
        echo "REFUSED: graceful stop of pid $pid not sent (game_instance exit $rc): $(printf '%s' "$out" | tail -n 3 | tr '\n' ' ')"
        return 2
    fi
    for _ in $(seq $(( ${RW_DOWN_GRACE_S:-90} / 5 ))); do
        sleep 5; look_gone; g=$?
        [ "$g" -eq 0 ] && { echo "stopped (graceful)"; return 0; }
        [ "$g" -eq 2 ] && { echo "UNMEASURED: the game list could not be read after the graceful stop of pid $pid"; return 2; }
    done
    out=$(python3 "$GI" stop "$pid" --force 2>&1); rc=$?
    local said; said=$(printf '%s' "$out" | tail -n 3 | tr '\n' ' ')
    if [ "$rc" -ne 0 ]; then
        look_gone && { echo "stopped (forced after ${RW_DOWN_GRACE_S:-90} s; the stop exited $rc: $said)"; return 0; }
        echo "FAILED: taskkill /F of pid $pid not done (game_instance exit $rc): $said"; return 1
    fi
    waited=0
    while :; do
        look_gone; g=$?
        [ "$g" -eq 0 ] && { echo "stopped (forced after ${RW_DOWN_GRACE_S:-90} s, gone ${waited} s after /F)"; return 0; }
        [ "$g" -eq 2 ] && { echo "UNMEASURED: the game list could not be read ${waited} s after taskkill /F of pid $pid"; return 2; }
        [ "$waited" -ge "${RW_FORCE_WAIT_S:-30}" ] && break
        sleep 1; waited=$(( waited + 1 ))
    done
    echo "FAILED: pid $pid survives taskkill /F for ${waited} s; taskkill said: $said"; return 1
}

# One driver per game (BRIDGE_LOCK_WIDEN_ONE_PER_HOST): up/down/init take this machine's host guard for their own
# run, or inherit it from a holder (the testq worker, `rimflow bridge take --host stevedesktop`). A window or job
# already driving the game refuses them with exit 75. RW_GAME_GUARDED stops the re-exec looping.
GUARD="$HERE/../../src/RimMandrake/rimflow/host_guard.py"
case "${1:-status}" in
    up|down|init)
        if [ -z "${RW_GAME_GUARDED:-}" ]; then
            RW_GAME_GUARDED=1 exec python3 "$GUARD" run --seat "${RM_GUARD_SEAT:-RUNNER}" --for "rw_game.sh $*" -- "$0" "$@"
        fi ;;
esac

case "${1:-status}" in
    status) status ;;
    up) up "${2:-}" ;;
    down) down ;;
    init) init ;;
    *) echo "usage: $0 status|up [--wait]|down|init"; exit 64 ;;
esac
