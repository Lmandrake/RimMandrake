#!/usr/bin/env bash
# Run one targeted modcheck on the SteveDesktop test centre, driven from Archmagi.
#
#   remote_modcheck.sh [--sync] [--deploy M1,M2] [--no-run] <Mod> [modcheck run args]
#
#   --sync         first bring the runner clone ~/rm/runner to origin/main (git pull --ff-only),
#                  then deploy <Mod> (plus every --deploy mod) with deploy_custom_mods.py. When a
#                  deploy plan shows drift the game is stopped, the mods are applied, and the
#                  game is started again; with no drift the running game is kept.
#   --deploy LIST  extra mod folders to deploy with --sync (comma-separated)
#   --no-run       stop after sync + game up (no modcheck run)
#
# Everything after the mod name goes to `modcheck run` unchanged. Steps, all on SteveDesktop's
# WSL in the runner clone:
#   0. (--sync) pull, plan, and if drift: rw_game.sh down, deploy --apply
#   1. rw_game.sh init        renew the test companion profile, check Prefs runInBackground
#   2. rw_game.sh up --wait   start Steam and the game if not up (the game stays up after the run)
#   3. modcheck run           with MODCHECK_SKIP_DEPLOY=1 (step 0 did the deploying)
#   4. the HTML sheet is copied back to $RM_SCRATCH (default
#      /mnt/d/ClaudeWork/rimmandrake/stevedesktop_testcentre) and its path printed.
# Each phase prints `PHASE <name> <seconds> s` so a run's wall-clock can be compared.
#
# The game on SteveDesktop is ours outright (owner, 2026-10-25): the runner owns its ModsConfig
# and saves, so nothing here protects any other player's state.
#
# The run records nothing in the ledger: the runner is no seat (seat UNKNOWN), so modcheck
# prints the `rimflow verify` line for the caller to record from a seat clone with --evidence.
# STEVEDESKTOP_MODCHECK_PROVE_FIRST_REMOTE_RUN (2026-10-25).
set -uo pipefail
SYNC=0; NORUN=0; EXTRA=""
while [ $# -gt 0 ]; do
    case "$1" in
        --sync) SYNC=1; shift ;;
        --deploy) EXTRA=$2; shift 2 ;;
        --no-run) NORUN=1; shift ;;
        -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
        *) break ;;
    esac
done
[ $# -ge 1 ] || { sed -n '2,13p' "$0"; exit 64; }
MOD=$1; shift
TARGET=${STEVE_WSL:-mandrake@stevedesktop-wsl}
OUT=${RM_SCRATCH:-/mnt/d/ClaudeWork/rimmandrake/stevedesktop_testcentre}
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=8 -o LogLevel=ERROR -o ServerAliveInterval=15 "$TARGET")
q() { printf '%q ' "$@"; }
now() { date +%s; }
phase() { echo "PHASE $1 $(( $(now) - $2 )) s"; }

if [ $SYNC = 1 ]; then
    t=$(now)
    MODS="$MOD${EXTRA:+,$EXTRA}"
    "${SSH[@]}" "cd ~/rm/runner && set -o pipefail && \
      git pull -q --ff-only origin main && echo \"runner at \$(git log --oneline -1)\" || exit 1
      args=''; for m in \$(echo $(q "$MODS") | tr , ' '); do args=\"\$args --mod \$m\"; done
      python3 src/RimMandrake/Utils/deploy_custom_mods.py \$args > /tmp/rmc_plan.txt 2>&1; prc=\$?
      grep -E '^ +[~+-] ' /tmp/rmc_plan.txt | head -40
      if [ \$prc = 0 ]; then echo 'deploy: no drift, game kept'; exit 0; fi
      grep -q 'Drift found' /tmp/rmc_plan.txt || { echo 'deploy plan FAILED:'; tail -n 20 /tmp/rmc_plan.txt; exit 1; }
      infrastructure/stevedesktop/rw_game.sh down || exit 1
      python3 src/RimMandrake/Utils/deploy_custom_mods.py \$args --apply > /tmp/rmc_apply.txt 2>&1 \
        || { echo 'deploy --apply FAILED:'; tail -n 20 /tmp/rmc_apply.txt; exit 1; }
      tail -n 3 /tmp/rmc_apply.txt"
    rc=$?
    phase sync "$t"
    [ $rc = 0 ] || { echo "sync FAILED (exit $rc)"; exit $rc; }
fi

t=$(now)
"${SSH[@]}" "cd ~/rm/runner && G=infrastructure/stevedesktop/rw_game.sh && \$G init && \$G up --wait"
rc=$?
phase load "$t"
[ $rc = 0 ] || { echo "game up FAILED (exit $rc)"; exit $rc; }
[ $NORUN = 1 ] && exit 0

t=$(now)
LOG=/tmp/remote_modcheck_$MOD.txt
"${SSH[@]}" "cd ~/rm/runner && export MODCHECK_SKIP_DEPLOY=1 WSLENV=\$WSLENV:MODCHECK_SKIP_DEPLOY && \
  python.exe src/RimMandrake/Utils/modcheck/cli.py run $(q "$MOD" "$@") > $LOG 2>&1; rc=\$?; cat $LOG; exit \$rc"
rc=$?
phase run "$t"
sheet=$("${SSH[@]}" "grep -a -o 'Transient\\\\modcheck\\\\[^ ]*\\.html' $LOG | tail -1 | tr '\\\\' /")
if [ -n "$sheet" ]; then
    mkdir -p "$OUT"
    scp -q -o BatchMode=yes "$TARGET:rm/runner/$sheet" "$OUT/" && echo "sheet: $OUT/$(basename "$sheet")"
fi
echo "modcheck exit $rc"
exit $rc
