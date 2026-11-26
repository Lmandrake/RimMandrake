#!/usr/bin/env bash
# live_accept.sh <game> [<Mod> <chain>]: the live acceptance of
# RIMMANDRAKE_MAKE_MODCHECK_RESTART_GAME_ONTO_ITS_LIST_THREE_HAND_WORKAROUNDS. One command, as the item states it:
# `game_lock.py run <game> -- modcheck run <Mod>`, from a shell that names no game (game_lock aims CMD at the game it
# holds), with no stop, deploy, tier write or launch by hand: modcheck does them itself. Its modcheck JSON is copied
# here as live_<stamp>.json for accept_live.py. No time limit here: game_instance.launch --wait bounds the load.
g=${1:?usage: live_accept.sh <game> [<Mod> <chain>]}
mod=${2:-FlowWorks}
chain=${3:-toggle_bottle_loop}
cd "$(dirname "$0")/../../.." || exit 2
HERE=design/specs/2026-11-26-modcheck-restart-onto-list
S=$(python3 ~/dev/Lodestar/bin/lib/agent_storage.py)/scratch/modcheck_restart_accept
mkdir -p "$S"
log=$S/modcheck_$(date +%Y%m%dT%H%M%S).log
mark=$S/start.mark; touch "$mark"
unset RM_GAME_INSTANCE RM_GAME_USERDATA RM_GAME_LOGDIR GABP_SERVER_PORT GABP_TOKEN RIMFLOW_DRIVER_LOCK
echo "GAME=$g mod=$mod chain=$chain sha=$(git rev-parse --short=10 HEAD) at $(date +%H:%M:%S) log=$log"
python3 src/RimMandrake/rimflow/game_lock.py run "$g" --for "modcheck restart-onto-list acceptance ($mod $chain)" -- \
  python.exe -X faulthandler src/RimMandrake/Utils/modcheck/cli.py run "$mod" --chains "$chain" --reuse off \
  --purpose fix --gate off > "$log" 2>&1
rc=$?
echo "MODCHECK_RC=$rc"
grep -E "RESTART|STALE_LOAD|HARNESS|mod_not_installed|PRUNED" "$log" | tail -12
j=$(ls -t Transient/modcheck/"${mod}"_*.json 2>/dev/null | head -1)
if [ -n "$j" ] && [ "$j" -nt "$mark" ]; then
  cp "$j" "$HERE/live_$(basename "$j" .json | sed "s/^${mod}_//").json"; echo "COPIED $j"
else
  echo "NO NEW modcheck JSON (newest: ${j:-none}); log $log"
fi
python3 "$HERE/accept_live.py"
