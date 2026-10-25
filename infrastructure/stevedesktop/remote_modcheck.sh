#!/usr/bin/env bash
# Run one targeted modcheck on the SteveDesktop test centre, driven from Archmagi.
#
#   infrastructure/stevedesktop/remote_modcheck.sh JawaIonWeapons --chains def_wiring
#
# Everything after the mod name goes to `modcheck run` unchanged. Steps, all on Steve's WSL
# in the runner clone ~/rm/runner:
#   1. rw_game.sh init        renew the test companion profile, check Prefs runInBackground
#   2. rw_game.sh up --wait   start the game if it is not up (it stays up after the run)
#   3. modcheck run           with MODCHECK_SKIP_DEPLOY=1, because modcheck's own redeploy
#                             would need a stopped game; deploy beforehand instead (below)
#   4. the HTML sheet is copied back to $RM_SCRATCH (default
#      /mnt/d/ClaudeWork/rimmandrake/stevedesktop_testcentre) and its path printed.
#
# NOT done here, on purpose: bringing the runner clone up to date and deploying our mods.
# Do that first while the game is down:
#   ssh mandrake@stevedesktop-wsl '~/rm/runner/infrastructure/stevedesktop/rw_game.sh down'
#   (update ~/rm/runner: git pull once origin has the commit, or a git bundle)
#   ssh mandrake@stevedesktop-wsl 'cd ~/rm/runner && python3 src/RimMandrake/Utils/deploy_custom_mods.py --mod <M> --apply'
#
# The run records nothing in the ledger: the runner is no seat (seat UNKNOWN), so modcheck
# prints the `rimflow verify` line for the caller to record from a seat clone with --evidence.
# STEVEDESKTOP_MODCHECK_PROVE_FIRST_REMOTE_RUN (2026-10-25).
set -uo pipefail
[ $# -ge 1 ] || { sed -n '2,8p' "$0"; exit 64; }
MOD=$1; shift
TARGET=${STEVE_WSL:-mandrake@stevedesktop-wsl}
OUT=${RM_SCRATCH:-/mnt/d/ClaudeWork/rimmandrake/stevedesktop_testcentre}
SSH=(ssh -o BatchMode=yes -o ConnectTimeout=8 -o LogLevel=ERROR "$TARGET")
q() { printf '%q ' "$@"; }

LOG=/tmp/remote_modcheck_$MOD.txt
"${SSH[@]}" "cd ~/rm/runner && G=infrastructure/stevedesktop/rw_game.sh && \$G init && \$G up --wait && \
  export MODCHECK_SKIP_DEPLOY=1 WSLENV=\$WSLENV:MODCHECK_SKIP_DEPLOY && \
  python.exe src/RimMandrake/Utils/modcheck/cli.py run $(q "$MOD" "$@") > $LOG 2>&1; rc=\$?; cat $LOG; exit \$rc"
rc=$?
sheet=$("${SSH[@]}" "grep -a -o 'Transient\\\\modcheck\\\\[^ ]*\\.html' $LOG | tail -1 | tr '\\\\' /")
if [ -n "$sheet" ]; then
    mkdir -p "$OUT"
    scp -q -o BatchMode=yes "$TARGET:rm/runner/$sheet" "$OUT/" && echo "sheet: $OUT/$(basename "$sheet")"
fi
echo "modcheck exit $rc"
exit $rc
