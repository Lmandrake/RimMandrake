#!/bin/bash
# Drive game A on SteveDesktop from this clone, for the Claude Whittle loop CLAUDE_STEVEDESKTOP_FWLIVE. The agent stays on
# Archmagi; the game, its proof scripts and their bridge calls run on SteveDesktop, in its own clone ~/rm/claude-fwlive
# (the pattern of the FlowWorks Artisan loop's ralph/steve.sh). Game B beside it is not ours; ~/rm/runner, ~/rm/gss,
# ~/rm/gameb, ~/rm/flowworks are never written. There is no reboot verb: a machine reboot drops game B too. Restart the game.
#   alive                   exit 0 if Steve's WSL answers
#   status                  uptime, game A's state, active mods, the guard
#   sync                    bring ~/rm/claude-fwlive to origin/main, lay this clone's src/ and whittle/ differences on top
#   deploy                  sync, game A down, deploy FlowWorks on Steve (game A is left down: follow with `up`)
#   tier                    game A down, the small flowworks mod list (FlowWorks, GSS, bridge, all DLC) for game A
#   up | down | restart     start game A and wait for the bridge | stop it, by pid | both
#   run '<shell command>'   run it in ~/rm/claude-fwlive on Steve, CR stripped; python.exe there is what reaches the bridge
#   fetch <Steve path> <local dir>   copy a file or folder back; a D:\ or C:\ path is fine
# Every remote command carries RM_GUARD_SEAT=$RIMFLOW_SEAT and, when the guard is held, its generation
# (RM_HOST_GUARD_GEN), so a `rimflow bridge take --host stevedesktop` made here covers what runs there.
cd "$(dirname "$0")/../.." || exit 1
STEVE=mandrake@stevedesktop-wsl
DIR=rm/claude-fwlive
SEAT=${RIMFLOW_SEAT:-CLAUDE_STEVEDESKTOP_FWLIVE}
OPTS=(-o BatchMode=yes -o ConnectTimeout=10 -o LogLevel=ERROR -o ServerAliveInterval=15 -o ServerAliveCountMax=4)
G=infrastructure/stevedesktop/rw_game.sh
ENVS="export RM_GAME_INSTANCE=a RM_GUARD_SEAT=$SEAT RIMFLOW_SEAT=$SEAT AGENT_SEAT=$SEAT RIMFLOW_BRIDGE_SEAT=$SEAT; \
gen=\$(python3 src/RimMandrake/rimflow/host_guard.py status --json 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get(\"generation\") or \"\") if d.get(\"state\")!=\"free\" else print(\"\")' 2>/dev/null); \
[ -n \"\$gen\" ] && export RM_HOST_GUARD_GEN=\$gen WSLENV=\"\${WSLENV:+\$WSLENV:}RM_HOST_GUARD_GEN/u:RIMFLOW_SEAT/u:AGENT_SEAT/u:RIMFLOW_BRIDGE_SEAT/u\""
on() { ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR || exit 97; $ENVS; $1"; }   # a failed cd must not run the payload elsewhere
# tailed <cmd...>: run it, show the last 5 lines, return ITS status (a bare pipe into tail would report success)
TAILED='tailed() { local o r; o=$("$@" 2>&1); r=$?; printf "%s\n" "$o" | tail -n 5; return $r; }; '
SG=/home/mandrake/rm/scratch/BENCH/steve_games.py   # shared game rule; `tiered` records whose mod list is on a game
dead() { echo "STEVE_UNREACHABLE: $1. Weather, not your bug: do the offline part and end the round." >&2; exit 75; }
tier() { on "$TAILED$G down; tailed python3 src/RimMandrake/Utils/modset_builder.py --tier flowworks --apply --not-my-bridge 'Claude Whittle FWLIVE on Steve game A'" || dead "tier failed"; python3 "$SG" tiered flowworks; }

ensure_clone() {
    ssh "${OPTS[@]}" "$STEVE" "[ -d ~/$DIR/.git ] || { git clone -q --local ~/rm/runner ~/$DIR && git -C ~/$DIR remote set-url origin \"\$(git -C ~/rm/runner remote get-url origin)\"; }" \
        || dead "cannot reach it to make the clone"
}

sync_tree() {
    git fetch -q origin main || { echo "fetch failed" >&2; exit 1; }
    # Steve's own disk guard (the loop's guard probes the machine the loop runs on, Archmagi): exit 4 = under the floor
    DF=$(ssh "${OPTS[@]}" "$STEVE" python3 - diskfree < "$(dirname "$0")/wc.py" 2>&1); [ $? = 4 ] && { echo "refused: Steve disk guard: $DF" >&2; exit 4; }
    ensure_clone
    # the mod-list backups a tier writes are tracked files the checkout would overwrite: keep Steve's copies
    on "mkdir -p ~/.wc-keep && cp -p deployed/config/ModsConfig.before-tier-*.xml ~/.wc-keep/ 2>/dev/null; \
        git status --porcelain -- infrastructure/state | grep -q . && git diff HEAD -- infrastructure/state > ~/.wc-keep/state-\$(date +%s).patch; \
        git fetch -q origin main && git checkout -qf -B whittle-claude FETCH_HEAD; rc=\$?; \
        cp -p ~/.wc-keep/ModsConfig.before-tier-*.xml deployed/config/ 2>/dev/null; exit \$rc" || dead "the checkout on Steve failed"
    { git diff --name-only origin/main -- src/RimMandrake whittle infrastructure/whittle_claude
      git ls-files -o --exclude-standard -- src/RimMandrake whittle; } \
        | grep -v 'northstar/proof_all_' | sort -u \
        | rsync -a --ignore-missing-args --files-from=- -e "ssh ${OPTS[*]}" . "$STEVE:$DIR/" || dead "the overlay rsync failed"
    # files deleted here but present in origin/main: the checkout restored them on Steve, so remove them there too
    git diff --name-only --diff-filter=D origin/main -- src/RimMandrake whittle infrastructure/whittle_claude \
        | ssh "${OPTS[@]}" "$STEVE" "cd ~/$DIR && xargs -r rm -f --" || dead "removing deleted files on Steve failed"
    echo "steve: ~/$DIR at origin/main $(git rev-parse --short origin/main) plus this clone's src/ and whittle/ differences"
}

case "${1:-}" in
    alive) ssh "${OPTS[@]}" "$STEVE" true ;;
    status)
        ensure_clone
        on "echo windows_uptime_min \$(powershell.exe -NoProfile -Command '[int]((Get-Date)-(Get-CimInstance Win32_OperatingSystem).LastBootUpTime).TotalMinutes' | tr -d '\r'); \
            $G status; python3 src/RimMandrake/rimflow/host_guard.py status 2>&1 | head -n 3; \
            . infrastructure/stevedesktop/testcentre_env.sh; python3 -c \"import os,xml.etree.ElementTree as E; print('active_mods', len(E.parse(os.environ['RM_GAME_USERDATA']+'/Config/ModsConfig.xml').find('activeMods')))\"" \
            | tr -d '\r' || dead "status got no answer" ;;
    sync) sync_tree ;;
    deploy)
        sync_tree
        on "$TAILED$G down; tailed python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod FlowWorks --apply" || dead "deploy failed" ;;
    tier) ensure_clone; tier ;;
    up) ensure_clone
        if python3 "$SG" needs-tier flowworks; then echo "up: another loop's tier is on game A, applying flowworks first"; tier; fi
        on "$G init; $G up --wait" || dead "game A did not come up" ;;
    down) ensure_clone; on "$G down" || dead "game A down failed" ;;
    restart) ensure_clone; on "$G down; $G init; $G up --wait" || dead "game A did not come back up" ;;
    run) shift; ensure_clone; on "$*" 2>&1 | tr -d '\r'; rc=${PIPESTATUS[0]}; [ "$rc" = 255 ] && dead "ssh dropped"; exit "$rc" ;;
    fetch)
        src=$(echo "$2" | sed -E 's#^([A-Za-z]):[\\/]#/mnt/\L\1/#; s#\\#/#g')
        case "$src" in /*) ;; *) src="$DIR/$src" ;; esac
        rsync -a -e "ssh ${OPTS[*]}" "$STEVE:$src" "$3/" || dead "fetch failed" ;;
    *) sed -n 2,13p "$0"; exit 64 ;;
esac
