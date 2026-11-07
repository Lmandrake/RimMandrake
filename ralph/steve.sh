#!/bin/bash
# Drive game A on SteveDesktop from this clone, for the FlowWorks loop. The agent stays on Archmagi and no credential goes to
# Steve: the game, its proof scripts and their bridge calls all run on Steve, in its own clone ~/rm/flowworks. Game B beside it
# is the Graffiti loop's; ~/rm/runner, ~/rm/gss and ~/rm/gameb are never written. There is no reboot verb: a machine reboot
# drops game B too and nothing warns that loop (RIMMASTER_GUARD_STEVE_REBOOT_DROPS_GAME_B_UNWARNED). Restart the game instead.
#   alive                   exit 0 if Steve's WSL answers
#   status                  uptime, last fault-canary cycle, game A's state, active mods
#   sync                    push ralph/flowworks, bring ~/rm/flowworks to it, lay this clone's uncommitted src/ and ralph/ changes on top
#   deploy                  sync, game A down, deploy FlowWorks on Steve (game A is left down: follow with `up`)
#   tier                    game A down, the small flowworks mod list (FlowWorks, GSS, bridge, all DLC) for game A
#   up | down | restart     start game A and wait for the bridge | stop it, by pid | both
#   run '<shell command>'   run it in ~/rm/flowworks on Steve, CR stripped; python.exe there is what reaches the bridge
#   fetch <Steve path> <local dir>   copy a file or folder back; a D:\ or C:\ path is fine
cd "$(dirname "$0")/.." || exit 1
STEVE=mandrake@stevedesktop-wsl
DIR=rm/flowworks
BRANCH=ralph/flowworks
OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
G=infrastructure/stevedesktop/rw_game.sh
on() { ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && export RM_GAME_INSTANCE=a && $1"; }
dead() { echo "STEVE_UNREACHABLE: $1. Weather, not your bug: see Steve's section in ralph/PROMPT.md." >&2; exit 75; }

ensure_clone() {
    ssh "${OPTS[@]}" "$STEVE" "[ -d ~/$DIR/.git ] || { git clone -q --local ~/rm/runner ~/$DIR && git -C ~/$DIR remote set-url origin \"\$(git -C ~/rm/runner remote get-url origin)\"; }" \
        || dead "cannot reach it to make the clone"
}

sync_tree() {
    git push -q origin "$BRANCH" || { echo "push failed" >&2; exit 1; }
    ensure_clone
    on "git fetch -q origin $BRANCH && git checkout -qf -B $BRANCH FETCH_HEAD" || dead "the checkout on Steve failed"
    { git diff --name-only HEAD -- src/RimMandrake ralph; git ls-files -o --exclude-standard -- src/RimMandrake ralph; } \
        | grep -v 'northstar/proof_all_' \
        | rsync -a --ignore-missing-args --files-from=- -e "ssh ${OPTS[*]}" . "$STEVE:$DIR/" || dead "the overlay rsync failed"
    echo "steve: ~/$DIR at $(git log -1 --format=%h) plus uncommitted src/ and ralph/"
}

case "${1:-}" in
    alive) ssh "${OPTS[@]}" "$STEVE" true ;;
    status)
        ensure_clone
        ssh "${OPTS[@]}" "$STEVE" "echo windows_uptime_min \$(powershell.exe -NoProfile -Command '[int]((Get-Date)-(Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes' | tr -d '\r'); \
            grep -a CYCLE /mnt/c/SteveDesktop/diag/logs/watch.log | tail -n 1 | tr -d '\r' | cut -c1-90; \
            cd ~/$DIR && export RM_GAME_INSTANCE=a && $G status; \
            python3 -c \"import os,xml.etree.ElementTree as E; print('active_mods', len(E.parse(os.environ['RM_GAME_USERDATA']+'/Config/ModsConfig.xml').find('activeMods')))\" 2>/dev/null \
              || { . infrastructure/stevedesktop/testcentre_env.sh; python3 -c \"import os,xml.etree.ElementTree as E; print('active_mods', len(E.parse(os.environ['RM_GAME_USERDATA']+'/Config/ModsConfig.xml').find('activeMods')))\"; }" \
            || dead "status got no answer" ;;
    sync) sync_tree ;;
    deploy)
        sync_tree
        on "$G down; python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply 2>&1 | tail -n 3" || dead "deploy failed" ;;
    tier) ensure_clone; on "$G down; python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply --not-my-bridge 'Artisan FlowWorks on Steve game A' 2>&1 | tail -n 5" || dead "tier failed" ;;
    up) ensure_clone; on "$G init; $G up --wait" || dead "game A did not come up" ;;
    down) ensure_clone; on "$G down" || dead "game A down failed" ;;
    restart) ensure_clone; on "$G down; $G init; $G up --wait" || dead "game A did not come back up" ;;
    run) shift; ensure_clone; on "$*" 2>&1 | tr -d '\r'; rc=${PIPESTATUS[0]}; [ "$rc" = 255 ] && dead "ssh dropped"; exit "$rc" ;;
    fetch)
        src=$(echo "$2" | sed -E 's#^([A-Za-z]):[\\/]#/mnt/\L\1/#; s#\\#/#g')
        case "$src" in /*) ;; *) src="$DIR/$src" ;; esac
        rsync -a -e "ssh ${OPTS[*]}" "$STEVE:$src" "$3/" || dead "fetch failed" ;;
    *) sed -n 2,13p "$0"; exit 64 ;;
esac
