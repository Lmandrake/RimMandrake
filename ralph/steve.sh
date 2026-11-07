#!/bin/bash
# Drive SteveDesktop's game from this clone (owner 2026-11-07: Steve as a second Artisan looper). The agent stays on
# Archmagi and no credential goes to Steve: the game, its proof scripts and their bridge calls all run on Steve, in its own
# clone ~/rm/gss, whose paths come from testcentre_env.sh. ~/rm/runner is the test lane's and is never written.
#   alive                   exit 0 if Steve's WSL answers
#   status                  uptime, last fault-canary cycle, game state, active mods
#   sync                    push ralph/gss, bring ~/rm/gss to it, lay this clone's uncommitted src/ and ralph/ changes on top
#   deploy                  sync, game down, deploy GimmeSomeSlack on Steve (a game is left down: follow with `up`)
#   tier                    game down, the small gimmesomeslack mod list on Steve
#   up | down               start the game and wait for the bridge | stop it
#   reboot                  restart the machine, wait for it to answer (about 6 min); the game stays down
#   run '<shell command>'   run it in ~/rm/gss on Steve, CR stripped; python.exe there is what reaches the bridge
#   fetch <Steve path> <local dir>   copy a file or folder back; a D:\ or C:\ path is fine
cd "$(dirname "$0")/.." || exit 1
STEVE=mandrake@stevedesktop-wsl
WIN=stevedesktop
DIR=rm/gss
OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
G=infrastructure/stevedesktop/rw_game.sh
on() { ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && $1"; }
dead() { echo "STEVE_UNREACHABLE: $1. Weather, not your bug: see Steve's section in ralph/PROMPT.md." >&2; exit 75; }

ensure_clone() {
    ssh "${OPTS[@]}" "$STEVE" "[ -d ~/$DIR/.git ] || { git clone -q --local ~/rm/runner ~/$DIR && git -C ~/$DIR remote set-url origin \"\$(git -C ~/rm/runner remote get-url origin)\"; }" \
        || dead "cannot reach it to make the clone"
}

sync_tree() {
    git push -q origin ralph/gss || { echo "push failed" >&2; exit 1; }
    ensure_clone
    on "git fetch -q origin ralph/gss && git checkout -qf -B ralph/gss FETCH_HEAD" || dead "the checkout on Steve failed"
    { git diff --name-only HEAD -- src/RimMandrake ralph; git ls-files -o --exclude-standard -- src/RimMandrake ralph; } \
        | grep -v 'northstar/proof_all_' \
        | rsync -a --ignore-missing-args --files-from=- -e "ssh ${OPTS[*]}" . "$STEVE:$DIR/" || dead "the overlay rsync failed"
    echo "steve: ~/$DIR at $(git log -1 --format=%h) plus uncommitted src/ and ralph/"
}

case "${1:-}" in
    alive) ssh "${OPTS[@]}" "$STEVE" true ;;
    status)
        ssh "${OPTS[@]}" "$STEVE" "echo windows_uptime_min \$(powershell.exe -NoProfile -Command '[int]((Get-Date)-(Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes' | tr -d '\r'); \
            grep -a CYCLE /mnt/c/SteveDesktop/diag/logs/watch.log | tail -n 1 | tr -d '\r' | cut -c1-90; \
            cd ~/$DIR 2>/dev/null && $G status; \
            python3 -c \"import os,xml.etree.ElementTree as E; print('active_mods', len(E.parse(os.environ['RM_GAME_USERDATA']+'/Config/ModsConfig.xml').find('activeMods')))\"" \
            || dead "status got no answer" ;;
    sync) sync_tree ;;
    deploy)
        sync_tree
        on "$G down; python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod GimmeSomeSlack --apply 2>&1 | tail -n 3" || dead "deploy failed" ;;
    tier) on "$G down; python3 src/RimMandrake/Utils/modset_builder.py --tier gimmesomeslack --apply --not-my-bridge 'Artisan GSS on Steve' 2>&1 | tail -n 5" || dead "tier failed" ;;
    up) on "$G init; $G up --wait" || dead "the game did not come up" ;;
    down) on "$G down" || dead "game down failed" ;;
    reboot)
        ssh "${OPTS[@]}" "$WIN" 'Restart-Computer -Force' || echo "reboot: no answer to the command, waiting anyway" >&2
        sleep 45
        for _ in $(seq 40); do
            if ssh "${OPTS[@]}" "$STEVE" true 2>/dev/null; then echo "steve: back"; exit 0; fi
            sleep 15
        done
        dead "no answer 10 minutes after the reboot" ;;
    run) shift; on "$*" 2>&1 | tr -d '\r'; rc=${PIPESTATUS[0]}; [ "$rc" = 255 ] && dead "ssh dropped"; exit "$rc" ;;
    fetch)
        src=$(echo "$2" | sed -E 's#^([A-Za-z]):[\\/]#/mnt/\L\1/#; s#\\#/#g')
        case "$src" in /*) ;; *) src="$DIR/$src" ;; esac
        rsync -a -e "ssh ${OPTS[*]}" "$STEVE:$src" "$3/" || dead "fetch failed" ;;
    *) sed -n 2,14p "$0"; exit 64 ;;
esac
