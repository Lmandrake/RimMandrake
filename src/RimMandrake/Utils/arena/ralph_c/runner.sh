#!/usr/bin/env bash
# ralph_c live runner entry (rm-runner@steve / @archmagi: the instance is the lane). Harness code.
#   $1 / RALPH_C_LANE        steve | archmagi (required)
#   RALPH_C_RUNNER_CLONE_<STEVE|ARCHMAGI>  the clone the runner checks candidate shas out in (required)
set -uo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
lane="${1:-${RALPH_C_LANE:-}}"
case "$lane" in steve|archmagi) ;; *) echo "lane must be steve or archmagi, got '$lane'"; exit 2;; esac
clonevar="RALPH_C_RUNNER_CLONE_${lane^^}"
clone="${!clonevar:-}"
[ -n "$clone" ] || { echo "set $clonevar to the $lane runner clone"; exit 2; }
cd "$here" || exit 2
unset RM_ARM
exec python3 "$here/../ralph_c_loop.py" runner --lane "$lane" --clone "$clone"
