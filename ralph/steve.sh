#!/bin/bash
# Drive game B on SteveDesktop from this clone (design/RimMandrake/two_rimworld_instances_2026-11-07.md, "How a loop goes on
# game B"). The agent stays on Archmagi and no credential goes to Steve: the game, its proof scripts and their bridge calls all
# run on Steve, in its own clone ~/rm/gameb, under game B's environment. Game A beside it is the GimmeSomeSlack loop's;
# ~/rm/runner and ~/rm/gss are never written.
#   alive                   exit 0 if Steve's WSL answers
#   status                  uptime, last fault-canary cycle, game B's state, active mods
#   sync                    push ralph/graffiti, bring ~/rm/gameb to it, lay this clone's uncommitted src/ and ralph/ changes on top
#   deploy                  sync, game B down, deploy Graffiti on Steve (game B is left down: follow with `up`)
#   tier                    game B down, the small graffiti_solo mod list for game B
#   up | down               start game B and wait for the bridge | stop it
#   run '<shell command>'   run it in ~/rm/gameb on Steve with game B's environment, CR stripped; python.exe there is what reaches the bridge
#   fetch <Steve path> <local dir>   copy a file or folder back; a D:\ or C:\ path is fine
cd "$(dirname "$0")/.." || exit 1
STEVE=mandrake@stevedesktop-wsl
DIR=rm/gameb
OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
G=infrastructure/stevedesktop/rw_game.sh
on() { ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && export RM_INSTANCES_ROOT=/mnt/d/ClaudeWork/rimmandrake/instances && eval \"\$(python3 src/RimMandrake/Utils/game_instance.py env b)\" && $1"; }
dead() { echo "STEVE_UNREACHABLE: $1. Weather, not your bug: see Steve's section in ralph/PROMPT.md." >&2; exit 75; }

ensure_clone() {
    ssh "${OPTS[@]}" "$STEVE" "[ -d ~/$DIR/.git ] || { git clone -q --local ~/rm/runner ~/$DIR && git -C ~/$DIR remote set-url origin \"\$(git -C ~/rm/runner remote get-url origin)\"; }" \
        || dead "cannot reach it to make the clone"
}

sync_tree() {
    git push -q origin ralph/graffiti || { echo "push failed" >&2; exit 1; }
    ensure_clone
    # plain ssh: a clone that has not reached this branch yet has no game_instance.py for on() to read
    ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && git fetch -q origin ralph/graffiti && git checkout -qf -B ralph/graffiti FETCH_HEAD" || dead "the checkout on Steve failed"
    { git diff --name-only HEAD -- src/RimMandrake ralph; git ls-files -o --exclude-standard -- src/RimMandrake ralph; } \
        | grep -v 'northstar/proof_all_' \
        | rsync -a --ignore-missing-args --files-from=- -e "ssh ${OPTS[*]}" . "$STEVE:$DIR/" || dead "the overlay rsync failed"
    echo "steve: ~/$DIR at $(git log -1 --format=%h) plus uncommitted src/ and ralph/"
}

case "${1:-}" in
    alive) ssh "${OPTS[@]}" "$STEVE" true ;;
    status)
        ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && export RM_INSTANCES_ROOT=/mnt/d/ClaudeWork/rimmandrake/instances && eval \"\$(python3 src/RimMandrake/Utils/game_instance.py env b)\" && echo windows_uptime_min \$(powershell.exe -NoProfile -Command '[int]((Get-Date)-(Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes' | tr -d '\r'); \
            grep -a CYCLE /mnt/c/SteveDesktop/diag/logs/watch.log | tail -n 1 | tr -d '\r' | cut -c1-90; \
            $G status; \
            python3 -c \"import os,xml.etree.ElementTree as E; print('active_mods', len(E.parse(os.environ['RM_GAME_USERDATA']+'/Config/ModsConfig.xml').find('activeMods')))\"" \
            || dead "status got no answer" ;;
    sync) sync_tree ;;
    deploy)
        sync_tree
        on "$G down; python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod Graffiti --apply 2>&1 | tail -n 3" || dead "deploy failed" ;;
    tier) on "$G down; python3 src/RimMandrake/Utils/modset_builder.py --tier graffiti_solo --apply --not-my-bridge 'Artisan Graffiti on game B' 2>&1 | tail -n 5" || dead "tier failed" ;;
    up) on "$G init; $G up --wait" || dead "the game did not come up" ;;
    down) on "$G down" || dead "game down failed" ;;
    run) shift; on "$*" 2>&1 | tr -d '\r'; rc=${PIPESTATUS[0]}; [ "$rc" = 255 ] && dead "ssh dropped"; exit "$rc" ;;
    fetch)
        src=$(echo "$2" | sed -E 's#^([A-Za-z]):[\\/]#/mnt/\L\1/#; s#\\#/#g')
        case "$src" in /*) ;; *) src="$DIR/$src" ;; esac
        rsync -a -e "ssh ${OPTS[*]}" "$STEVE:$src" "$3/" || dead "fetch failed" ;;
    *) sed -n 2,14p "$0"; exit 64 ;;
esac
